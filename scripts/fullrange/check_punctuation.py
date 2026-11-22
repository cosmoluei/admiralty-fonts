"""Verify punctuation in delivered faces against the same-weight upright at normal width."""
import argparse
from io import BytesIO
from pathlib import Path
import sys
import unicodedata

import numpy as np
import pathops
import uharfbuzz as hb
from fontTools.ttLib import TTFont

from check_period import circle_errors, locations

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from punctuation_scope import punctuation_names

CODE_PAIRS = ('->', '<-', '=>', '==', '!=', '<=', '>=')
RUNS = ('——', '––', '__', '……', '‰‰', '%%', '@@', '?!', '()', '[]', '{}', '/\\')
RELEASE_DIRS = ('fonts/ttf', 'fonts/otf', 'fonts/woff2', 'fonts/variable',
                'fonts/variable/fullrange', 'site/fonts/admiralty', 'packages/web/fonts/subsets')


def shaped(font, text, features=None):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.direction, buf.script = 'ltr', 'Latn'
    hb.shape(font, buf, features or {})
    return [(g.codepoint, p) for g, p in zip(buf.glyph_infos, buf.glyph_positions)]


def open_face(path, tt):
    data = path.read_bytes()
    if tt.flavor == 'woff2':  # HarfBuzz needs a decompressed sfnt, including for web subsets.
        out = BytesIO()
        tt.flavor = None
        tt.save(out)
        data = out.getvalue()
    return hb.Font(hb.Face(data))


def punctuation_ids(tt, font, mono):
    cmap = tt.getBestCmap()
    gids = {tt.getGlyphID(n) for cp, n in cmap.items() if unicodedata.category(chr(cp)).startswith('P')}
    for cp in cmap:
        if unicodedata.category(chr(cp)).startswith('P'):
            gids.update(g for g, _ in shaped(font, chr(cp), {'case': True}))
    # The line breaker reveals SOFT HYPHEN at a discretionary break. Ordinary
    # shaping hides it, so verify the actual glyph directly through its cmap.
    if 0x00AD in cmap:
        gids.add(tt.getGlyphID(cmap[0x00AD]))
    if mono and all(ord(c) in cmap for c in '-<>=!'):
        for pair in CODE_PAIRS:
            base = [g for g, _ in shaped(font, pair)]
            alt = [g for g, _ in shaped(font, pair, {'ss01': True})]
            assert len(alt) == 2 and all(a != b for a, b in zip(alt, base)), pair
            gids.update(alt)
    # Subsets drop post names; shaping above still finds the unencoded glyph IDs.
    if tt['post'].formatType != 3:
        declared = punctuation_names(cmap, tt.getGlyphOrder())
        assert declared == {tt.getGlyphName(g) for g in gids}, declared ^ {tt.getGlyphName(g) for g in gids}
    return sorted(gids)


def outline(font, gid):
    path = pathops.Path()
    font.draw_glyph_with_pen(gid, path.getPen())
    return path


def check_dots(font, path, weight):
    for char in '.:;…!?¡¿·•':
        if font.get_nominal_glyph(ord(char)) is None:
            continue
        variants = {g for feat in ({}, {'case': True}) for g, _ in shaped(font, char, feat)}
        for gid in variants:
            contours = list(outline(font, gid).contours)
            if char in ';!?¡¿':
                # Separate the small dot from the tall stem, hook, or comma.
                assert len(contours) == 2, (path, weight, char, 'missing detached dot')
                contours = [min(contours, key=lambda c: c.bounds[3] - c.bounds[1])]
            else:
                assert len(contours) == {':': 2, '…': 3}.get(char, 1), (path, weight, char)
            for contour in contours:
                extent, radial = circle_errors(contour.draw)
                assert max(extent, radial) <= 1, (path, weight, char, gid, 'round dot', extent, radial)


def profile(font, gid):
    path = outline(font, gid)
    points = np.asarray(path.points)
    anchor = points[0] if len(points) else np.zeros(2)
    if len(points):
        # Remove placement only. Off-curve points and contour commands must agree too.
        points = points - anchor
    return path.verbs, points, anchor, font.get_glyph_h_advance(gid)


def check_run_spacing(font, reference, path, location, texts, features=None, mono=False):
    for text in texts:
        if any(font.get_nominal_glyph(ord(char)) is None for char in text):
            # Separate unicode-range subsets may have just the decomposed
            # fallback of a different file's letter, e.g. d + caron for ď.
            continue
        run = shaped(font, text, features)
        assert all(g for g, _ in run), (path, text, 'missing glyph')
        assert len(run) == len(text), text
        placed = []
        x = 0
        for gid, pos in run:
            if mono:
                assert pos.x_advance == 600, (path, location, text, 'fixed cell')
            placed.append(outline(font, gid).transform(1, 0, 0, 1, x + pos.x_offset, pos.y_offset))
            x += pos.x_advance
        if text == '__':
            # Underscores may make one continuous line. Keep the same join as
            # the upright rather than requiring whitespace between the cells.
            joined = [(p.x_advance, p.x_offset, p.y_offset) for _, p in run]
            expected = [(p.x_advance, p.x_offset, p.y_offset) for _, p in shaped(reference, text)]
            assert joined == expected, (path, location, text, 'underscore join')
            continue
        for a, b in zip(placed, placed[1:]):
            if a.bounds[2] > b.bounds[0]:  # overhanging bounds alone do not imply touching ink
                overlap = pathops.op(a, b, pathops.PathOp.INTERSECTION)
                assert abs(overlap.area) <= .01, (str(path), location, text, 'overlapping ink', overlap.area)


def check_axis_deltas(tt, gids):
    if 'fvar' not in tt or len(tt['fvar'].axes) == 1:
        return
    # Also inspect encoded variation supports. A narrow intermediate region
    # for width/radius could fall entirely between the rendered test cases.
    axes = [a.axisTag for a in tt['fvar'].axes]
    hvar = tt['HVAR'].table
    regions = hvar.VarStore.VarRegionList.Region
    non_weight_regions = {i for i, r in enumerate(regions)
                          if any(axis != 'wght' and region.PeakCoord != 0
                                 for axis, region in zip(axes, r.VarRegionAxis))}
    for gid in gids:
        name = tt.getGlyphName(gid)
        for t in tt['gvar'].variations[name]:
            if t.axes.keys() - {'wght'}:
                assert not any(p and any(p) for p in t.coordinates), (name, t.axes, 'outline variation')
        index = hvar.AdvWidthMap.mapping[name] if hvar.AdvWidthMap else gid
        data = hvar.VarStore.VarData[index >> 16]
        for region, delta in zip(data.VarRegionIndex, data.Item[index & 0xFFFF]):
            assert not (region in non_weight_regions and delta), (name, region, delta, 'advance variation')


def check_pair(roman, italic):
    mono = 'Mono' in roman.name
    count = 0
    with TTFont(roman) as rt, TTFont(italic) as it:
        normal, slanted = open_face(roman, rt), open_face(italic, it)
        reference = hb.Font(normal.face)
        rgids, igids = punctuation_ids(rt, normal, mono), punctuation_ids(it, slanted, mono)
        assert [rt.getGlyphName(g) for g in rgids] == [it.getGlyphName(g) for g in igids]
        check_axis_deltas(rt, rgids)
        check_axis_deltas(it, igids)
        refs = {}
        areas = {}
        for loc in locations(rt):
            weight = loc.get('wght')
            reference.set_variations({'wght': weight} if weight is not None else {})
            if weight not in refs:
                check_dots(reference, roman, weight)
                refs[weight] = [profile(reference, g) for g in rgids]
                if weight is not None:
                    areas[weight] = [abs(outline(reference, g).area) for g in rgids]
            for path, font, gids in ((roman, normal, rgids), (italic, slanted, igids)):
                font.set_variations(loc)
                for gid, (verbs, points, anchor, adv) in zip(gids, refs[weight]):
                    ops, actual, position, width = profile(font, gid)
                    key = (str(path), loc, rt.getGlyphName(gid))
                    assert width == adv and (not mono or width == 600), (*key, 'advance', width, adv)
                    assert ops == verbs and actual.shape == points.shape, (*key, 'contour commands')
                    assert np.allclose(points, actual, rtol=0, atol=.01), (*key, 'displayed contour')
                    assert np.allclose(anchor, position, rtol=0, atol=.01), (*key, 'ink placement')
                    count += 1
                if loc.get('wdth', 65) == 65:
                    check_run_spacing(font, reference, path, loc, RUNS, mono=mono)
                    check_run_spacing(font, reference, path, loc, ('——', '––'), {'case': True})
                if path == italic and loc.get('wght', 400) in (400, 700, 900) and loc.get('wdth', 100) in (65, 100, 150):
                    # A letter that clears either neighbor alone must still fit between both.
                    mixed = ('‰ď‰', '¶ď⟩') if mono else ('[f', 'f?', '{j')
                    check_run_spacing(font, reference, path, loc, mixed, mono=mono)
        for lighter, heavier in zip(sorted(areas), sorted(areas)[1:]):
            for g, a, b in zip(rgids, areas[lighter], areas[heavier]):
                assert b > a, (roman, rt.getGlyphName(g), lighter, heavier, 'weight must increase ink area')
    return count


def pairs(directory):
    for path in sorted(directory.iterdir()):
        if not path.is_file() or path.suffix not in {'.ttf', '.otf', '.woff2'}:
            continue
        if 'Symbols' in path.name or 'Italic' not in path.name:
            continue
        upright_name = path.name.replace('-Italic.', '-Regular.').replace('-Italic', '').replace('Italic', '')
        yield path.with_name(upright_name), path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directories', nargs='*', type=Path, help='directories containing upright and italic pairs')
    dirs = parser.parse_args().directories or [ROOT / d for d in RELEASE_DIRS]
    total = files = 0
    for directory in dirs:
        face_pairs = list(pairs(directory))
        assert face_pairs, f'No text pairs in {directory}'
        for roman, italic in face_pairs:
            total += check_pair(roman, italic)
            files += 2
    print(f'{files} font files, {total:,} punctuation outlines and advances matched. Shaped spacing passed.')
