"""Audit the saved font, including off-master instances and correspondence of flat stems."""
import itertools
from collections import defaultdict

import numpy as np
import pathops
import uharfbuzz as hb
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from scipy.spatial import cKDTree

from build_axis_study import AXES, CELLS, FILENAME, LETTERS, REVIEW, SCALE, master_glyph_sets, master_outline
from check_word_proof import Edges, section


def shape(gs, name, scale=1):
    path = pathops.Path()
    gs[name].draw(TransformPen(path.getPen(), (1/scale, 0, 0, 1/scale, 0, 0)))
    return path


def boundary_points(path):
    # Both point clouds include every endpoint of short chords. Long straight
    # spans need the same physical sampling interval as curved pieces.
    pen = Edges(None, 1)
    path.draw(pen)
    edges = np.array(pen.edges)
    ds = edges[:,1]-edges[:,0]
    count = np.maximum(1, np.ceil(abs(ds)/.4).astype(int))
    start = np.cumsum(count)-count
    t = (np.arange(count.sum())-np.repeat(start,count))/np.repeat(count,count)
    z = np.repeat(edges[:,0],count) + t*np.repeat(ds,count)
    return np.column_stack([z.real,z.imag])


def main():
    file = REVIEW / "fonts" / (FILENAME + ".ttf")
    font = TTFont(file)
    web = TTFont(file.with_suffix(".woff2"))
    for table in ("cmap", "fvar", "gvar", "glyf", "hmtx"):
        assert font.getTableData(table) == web.getTableData(table), table
    assert {a.axisTag: (a.minValue, a.defaultValue, a.maxValue) for a in font["fvar"].axes} == AXES
    hb_font = hb.Font(hb.Face(file.read_bytes()))
    widths = (65, 82.5, 100, 125, 150)
    radii = (0, 50, 100)
    weights = range(100, 901, 100)
    cover = defaultdict(int)
    previous_area = {}
    for w, d, r in itertools.product(weights, widths, radii):
        loc = dict(wght=w, wdth=d, RADI=r)
        gs = font.getGlyphSet(location=loc)
        hb_font.set_variations(loc)
        for name in LETTERS:
            path = shape(gs, name, SCALE)
            initial = len(list(path.contours))
            path.simplify()
            assert len(list(path.contours)) == initial, ("winding or closure changed", loc, name)
            area = abs(path.area)
            assert area > previous_area.get((name, d, r), 0), ("weight reversal", loc, name)
            previous_area[name, d, r] = area
            advance = hb_font.get_glyph_h_advance(font.getGlyphID(name))/SCALE
            assert abs(advance-gs[name].width/SCALE) <= .26
            if name in "hminubdpq":
                horizontal = 110
                if name in "bdh":
                    horizontal = 605
                elif name in "pq":
                    horizontal = -130
                elif name == "u":
                    horizontal = 390
                p = Edges(gs, SCALE)
                gs[name].draw(p)
                a = section(np.array(p.edges), horizontal)
                b = section(np.array(p.edges), horizontal+30)
                # Crossing a flat-sided stem away from a join must not produce a slant.
                assert len(a) == len(b) and max(abs(a-b)) < 1, ("stem shifted", name, loc, a, b)
            cover[name] += 1
    sources = master_glyph_sets()
    errors = []
    for (w,d), source in zip(CELLS, sources):
        gs = font.getGlyphSet(location=dict(wght=w, wdth=d))
        for name in LETTERS:
            candidate = shape(gs, name, SCALE)
            design, advance = master_outline(name, (w,d), source, sources[0])
            original = pathops.Path()
            design.draw(original.getPen())
            assert abs(gs[name].width/SCALE-advance) < .26
            a, b = boundary_points(original), boundary_points(candidate)
            err = max(cKDTree(a).query(b)[0].max(), cKDTree(b).query(a)[0].max())
            assert abs(original.area-candidate.area) / max(abs(original.area),1) < .005
            errors.append((err, name, w, d))
    worst = max(errors)
    assert worst[0] < .6, ("outline deviation", worst)
    print(f"{len(LETTERS)} glyphs × {len(weights)*len(widths)*len(radii)} locations = {sum(cover.values())} outlines")
    print(f"{len(errors)} unrounded master outlines compared. Largest sampled boundary distance: {worst[0]:.3f} units ({worst[1:]})")
    print("TTF/WOFF2 axis tables, winding, increasing ink area, advances and straight stems checked.")


if __name__ == "__main__":
    main()
