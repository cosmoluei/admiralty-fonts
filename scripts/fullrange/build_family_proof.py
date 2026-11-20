"""Embed each family's own mapped and alternate glyphs in a standalone optical proof."""
import base64
import hashlib
import io
import json
import math
from itertools import product

import uharfbuzz as hb

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable

from build_text_family import OUTPUT, REVIEW, TEXT
from glyph_peers import reference_names
from operator_masters import PAIRS


def review_bounds(binary, glyph_count):
    """Ink bounds relative to the advance midpoint, across the displayed axis samples."""
    face = hb.Face(binary)
    font = hb.Font(face)
    font.scale = (1000, 1000)
    bounds = [None] * glyph_count
    for weight, width, radius in product(range(100, 901, 100), (65, 82.5, 100, 125, 150), (0, 50, 100)):
        font.set_variations({"wght": weight, "wdth": width, "RADI": radius})
        for gid in range(glyph_count):
            ink = font.get_glyph_extents(gid)
            if not ink or not (ink.width and ink.height):
                continue
            midpoint = font.get_glyph_h_advance(gid) / 2
            left = math.floor(ink.x_bearing - midpoint)
            top = -ink.y_bearing
            right = math.ceil(ink.x_bearing + ink.width - midpoint)
            bottom = top - ink.height
            old = bounds[gid]
            bounds[gid] = ([min(left, old[0]), min(top, old[1]), max(right, old[2]), max(bottom, old[3])]
                           if old else [left, top, right, bottom])
    return bounds


def build():
    names, faces, review = {}, [], {}
    for i,family in enumerate([*TEXT, "AdmiraltySymbols"]):
        filename=family+"[wght,wdth,RADI].ttf"
        font=TTFont(OUTPUT/filename)
        order=font.getGlyphOrder()
        cmap=font.getBestCmap()
        peers = reference_names(font) if family in TEXT else {}
        operators = {}
        if 'Mono' in family:
            for sequence,pair in PAIRS.items():
                for part in pair:
                    operators.setdefault(part,sequence)
        names[family]={"operators":operators,"order":order,"cmap":cmap,"file":filename,
                       "peers": [[font.getGlyphID(p) for p in peers.get(n,())] for n in order]}
        binary = (OUTPUT / filename).read_bytes()
        review[family] = {
            "order": order, "cmap": cmap, "operators": operators, "file": filename,
            "sha256": hashlib.sha256(binary).hexdigest(),
            "inkBounds": review_bounds(binary, len(order)),
            "blank": [n for n in order if font["glyf"][n].numberOfContours == 0],
            "axes": {axis.axisTag: [axis.minValue, axis.defaultValue, axis.maxValue]
                     for axis in font["fvar"].axes},
        }
        # This cmap exists only in the embedded proof font. It makes
        # unencoded alternates viewable individually through a native browser.
        table=CmapSubtable.newSubtable(12)
        table.platformID,table.platEncID,table.language=3,10,0
        table.cmap={**cmap,**{0xf0000+j:g for j,g in enumerate(order)}}
        font["cmap"].tables=[t for t in font["cmap"].tables if (t.platformID,t.platEncID)!=(3,10)]+[table]
        font.flavor="woff2"
        data=io.BytesIO()
        font.save(data)
        blob=base64.b64encode(data.getvalue()).decode()
        faces.append(f"@font-face{{font-family:Family{i};src:url(data:font/woff2;base64,{blob});font-weight:100 900;font-stretch:65% 150%}}")
    template=(REVIEW.parent/"family_proof.html.in").read_text()
    (REVIEW/"family-proof.html").write_text(template.replace("/* FONTS */","\n".join(faces)).replace("/* DATA */",json.dumps(names,separators=(",",":"))))

    source = REVIEW.parent
    template = (source / "glyph_review.html.in").read_text()
    html = (template.replace("/* FONTS */", "\n".join(faces))
            .replace("/* STYLE */", (source / "glyph_review.css").read_text())
            .replace("/* DATA */", json.dumps(review, separators=(",", ":")))
            .replace("/* OBSERVATIONS */", (source / "review_observations.json").read_text().strip())
            .replace("/* APP */", (source / "glyph_review.js").read_text()))
    (REVIEW / "glyph-review.html").write_text(html)


if __name__=="__main__":
    build()
