"""Add italic letter–punctuation clearance after the font's existing kerning."""

import json
from pathlib import Path
import unicodedata

from fontTools import subset  # Registers GPOS.subset_lookups for index-safe removal.
from fontTools.otlLib.builder import (
    ChainContextPosBuilder, ChainContextualRule, PairPosBuilder,
    buildLookup, buildPairPosGlyphs, buildValue,
)
from fontTools.varLib.featureVars import buildFeatureRecord, sortFeatureList

from punctuation_scope import punctuation_names


DATA = Path(__file__).with_name("punctuation_clearance.json")
# This private feature is never enabled in any language system. Its only job is
# identifying our lookups when rebuilding a variable font from a delivered VF.
MARKER = "zzPC"


def clearance_pairs(kind):
    return json.loads(DATA.read_text(encoding="utf-8"))[kind]


def remove_punctuation_spacing(font):
    if "GPOS" not in font:
        return
    gpos = font["GPOS"]
    table = gpos.table
    owned = {index for record in table.FeatureList.FeatureRecord if record.FeatureTag == MARKER
             for index in record.Feature.LookupListIndex}
    if owned:
        gpos.subset_lookups([i for i in range(len(table.LookupList.Lookup)) if i not in owned])


def _protect_mono_neighbors(font, pairs, punctuation):
    """Move the mark outward when moving its italic letter would crowd another glyph."""
    gids = font.getReverseGlyphMap()
    letters = {name for cp, name in font.getBestCmap().items()
               if unicodedata.category(chr(cp))[0] in "LN"}
    neighbors = letters | punctuation
    lookups = font["GPOS"].table.LookupList.Lookup
    active = []
    for mark_first in (True, False):
        adjustment = PairPosBuilder(font, None)
        adjustment.lookupflag = 8
        for left, row in pairs.items():
            if left not in gids or (left in punctuation) != mark_first:
                continue
            for right, clearance in row.items():
                if right in gids:
                    move = buildValue({"XPlacement": -clearance if mark_first else clearance})
                    adjustment.addGlyphPair(None, left, move, right, move)
        if not adjustment.glyphPairs:
            continue
        adjustment.lookup_index = len(lookups)
        lookups.append(adjustment.build())
        context = ChainContextPosBuilder(font, None)
        context.lookupflag = 8
        if mark_first:
            prefix, glyphs, suffix = [], [punctuation], [letters, neighbors]
        else:
            prefix, glyphs, suffix = [neighbors], [letters], [punctuation]
        context.rules.append(ChainContextualRule(prefix, glyphs, suffix, [[adjustment]]))
        active.append(len(lookups))
        lookups.append(context.build())
    return active


def apply_punctuation_spacing(font):
    remove_punctuation_spacing(font)
    mono = bool(font["post"].isFixedPitch)
    if font["OS/2"].fsSelection & 1:
        kind = "mono" if mono else "proportional"
    elif not mono and "fvar" in font and any(a.axisTag == "wdth" for a in font["fvar"].axes):
        kind = "upright"
    else:
        return
    pairs = clearance_pairs(kind)
    gids = font.getReverseGlyphMap()
    punctuation = punctuation_names(font.getBestCmap(), gids)
    first, second = {}, {}
    for left, neighbors in pairs.items():
        for right, clearance in neighbors.items():
            if left not in gids or right not in gids:
                continue
            if not mono:
                first[left, right] = (buildValue({"XAdvance": clearance}), None)
            elif left in punctuation:
                second[left, right] = (None, buildValue({"XPlacement": clearance}))
            else:
                first[left, right] = (buildValue({"XPlacement": -clearance}), None)

    # With a second-glyph adjustment the shaper skips that glyph on this lookup's
    # next iteration. Separate lookups let it also match the next letter–mark pair.
    table = font["GPOS"].table
    lookups = table.LookupList.Lookup
    first_owned = len(lookups)
    indices = []
    for group in (first, second):
        if group:
            indices.append(len(lookups))
            lookups.append(buildLookup(buildPairPosGlyphs(group, gids), flags=8))
    if not indices:
        return
    if mono:
        indices.extend(_protect_mono_neighbors(font, pairs, punctuation))
    table.LookupList.LookupCount = len(lookups)

    features = table.FeatureList.FeatureRecord
    kern = [r for r in features if r.FeatureTag == "kern"]
    if not kern:
        record = buildFeatureRecord("kern", [])
        index = len(features)
        features.append(record)
        kern.append(record)
        for script in table.ScriptList.ScriptRecord:
            langsys = [r.LangSys for r in script.Script.LangSysRecord]
            if script.Script.DefaultLangSys is not None:
                langsys.append(script.Script.DefaultLangSys)
            for lang in langsys:
                lang.FeatureIndex.append(index)
                lang.FeatureCount = len(lang.FeatureIndex)
    for record in kern:
        record.Feature.LookupListIndex.extend(indices)
        record.Feature.LookupCount = len(record.Feature.LookupListIndex)
    features.append(buildFeatureRecord(MARKER, list(range(first_owned, len(lookups)))))
    table.FeatureList.FeatureCount = len(features)
    sortFeatureList(table)
