"""Compare the public symbol reached by shaping against its independent drawing recipe."""
import argparse
import collections
import hashlib
import json
from concurrent.futures import ProcessPoolExecutor
from itertools import product
from pathlib import Path

import numpy as np
import uharfbuzz as hb
from fontTools.pens.freetypePen import FreeTypePen
from fontTools.ttLib import TTFont

from audit_text_family import LOCATIONS, pen_shape
from build_text_family import OUTPUT, REVIEW
from build_symbol_family import VALUES
from symbol_masters import CATALOG, glyph_path

FONT = OUTPUT / "AdmiraltySymbols[wght,wdth,RADI].ttf"
BY_NAME = {s.name: s for s in CATALOG}
# Test designs inside cells as well as at the explicitly drawn masters.
OFF_GRID = list(product((150,350,550,750,850),(73.75,91.25,112.5,137.5),(25,75)))
SAMPLES=LOCATIONS+OFF_GRID


def bitmap(outline):
    pen = FreeTypePen(None)
    outline.draw(pen)
    data, _ = pen.buffer(128, 128, (.105, 0, 0, .105, 17, 25))
    return np.frombuffer(data, dtype=np.uint8).astype(np.int16)


def shape(font, cp, direction):
    buf = hb.Buffer()
    buf.add_codepoints([cp])
    buf.guess_segment_properties()
    buf.direction = direction
    hb.shape(font, buf)
    assert len(buf.glyph_infos) == 1
    return buf.glyph_infos[0].codepoint, buf.glyph_positions[0].x_advance


def inspect_batch(names):
    tt = TTFont(FONT)
    face = hb.Font(hb.Face(FONT.read_bytes()))
    cmap = tt.getBestCmap()
    problems = collections.defaultdict(list)
    max_master, max_middle = (0., '', ''), (0., '', '')
    for name in names:
        spec = BY_NAME[name]
        stem = name.replace('-', '_')
        assert cmap[spec.codepoint] == stem
        for w, d, r in SAMPLES:
            loc = f"{w}/{d}/{r}"
            face.set_variations(dict(wght=w, wdth=d, RADI=r))
            left, advance = shape(face, spec.codepoint, "ltr")
            right, rtl_advance = shape(face, spec.codepoint, "rtl")
            left_name, right_name = tt.getGlyphName(left), tt.getGlyphName(right)
            if (left_name != stem and not left_name.startswith(stem+'.design')) or right_name != left_name+('.rtl' if spec.rtl_mirror else ''):
                problems[name].append([loc, "substitution", left_name, right_name])
            if (advance, rtl_advance) != (840, 840):
                problems[name].append([loc, "advance", advance, rtl_advance])
            ref = glyph_path(name, w, d, r)
            source = bitmap(ref)
            native = bitmap(pen_shape(face, left))
            denom = int(source.sum())
            assert denom and native.any(), (name, loc, 'empty artwork')
            error = float(abs(source-native).sum()/denom)
            on_master = all(x in choices for x,choices in zip((w,d,r),VALUES))
            if on_master:
                max_master = max(max_master, (error, name, loc))
            else:
                max_middle = max(max_middle, (error, name, loc))
            if error > (.035 if on_master else .12):
                problems[name].append([loc, "master" if on_master else "interpolation", round(error,4)])
            if spec.rtl_mirror:
                # Mirror the native LTR geometry before rasterization, so an
                # asymmetric icon or half-pixel canvas origin cannot mask a flip.
                mirror = bitmap(pen_shape(face, left).transform(-1,0,0,1,840,0))
                mirrored = bitmap(pen_shape(face, right))
                if abs(mirror-mirrored).sum()/max(mirror.sum(),1) > .012:
                    problems[name].append([loc, "mirror"])
    return problems, max_master, max_middle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=REVIEW/'audits'/'AdmiraltySymbols.json')
    parser.add_argument('--workers', type=int, default=3)
    parser.add_argument('--only', nargs='+', choices=BY_NAME)
    parser.add_argument('--strict', action='store_true')
    args = parser.parse_args()
    names = args.only or list(BY_NAME)
    groups = [names[i:i+8] for i in range(0,len(names),8)]
    exceptions = {}
    worst_master, worst_middle = (0., '', ''), (0., '', '')
    with ProcessPoolExecutor(args.workers) as pool:
        for items, master, middle in pool.map(inspect_batch, groups):
            exceptions.update(items)
            worst_master, worst_middle = max(worst_master,master), max(worst_middle,middle)
    report = dict(family="AdmiraltySymbols", names=names, sample_grid=SAMPLES,
                  sha256=hashlib.sha256(FONT.read_bytes()).hexdigest(), exceptions=exceptions,
                  max_master_error=worst_master, max_interpolation_error=worst_middle,
                  public_symbol_instances=len(names)*len(SAMPLES))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, separators=(',',':')))
    print(report['public_symbol_instances'], 'public icon instances in both directions;',
          len(exceptions), 'symbols flagged; worst pixel differences', worst_master, worst_middle)
    if args.strict and exceptions:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
