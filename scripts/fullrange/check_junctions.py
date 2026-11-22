"""Measure through-strokes, joined vowels and operator seams in the exported fonts."""

import argparse
from itertools import product
from pathlib import Path

import numpy as np
import uharfbuzz as hb
from fontTools.ttLib import TTFont

from build_text_family import OUTPUT, TEXT
from check_optical_inventory import unsheared
from check_text_layout import shape
from check_word_proof import section
from operator_masters import PAIRS

# Sample exposed portions of each rail on opposite sides of a vertical stroke.
# Coordinates are relative to the glyph width after removing the italic shear.
RAILS = {
    "uni20A6": [(252, (0.055, 0.315, 0.945)), (434, (0.055, 0.315, 0.945))],
    "uni20B1": [(443, (0.055, 0.48, 0.945)), (551, (0.055, 0.48, 0.945))],
    "uni20B4": [(263, (0.055, 0.48, 0.945)), (424, (0.055, 0.315, 0.945))],
    "uni20B8": [(542, (0.055, 0.315, 0.945)), (688, (0.055, 0.315, 0.945))],
    "rupee": [(529, (0.055, 0.315, 0.945)), (689, (0.055, 0.76, 0.945))],
    "ruble": [(207, (0.055, 0.315, 0.48)), (328, (0.055, 0.315, 0.48))],
}


def check_rails(get):
    worst = 0.0
    for name, rows in RAILS.items():
        edges = get(name)
        for y, positions in rows:
            exposed = []
            for u in positions:
                x = edges.real.min() + u * np.ptp(edges.real)
                bands = section(edges, x, vertical=True).reshape(-1, 2)
                band = min(bands, key=lambda pair: abs(pair.mean() - y))
                assert abs(band.mean() - y) < 14 and 16 <= np.ptp(band) <= 25, (
                    name,
                    y,
                    u,
                    band,
                )
                exposed.append(band)
            drift = np.ptp(exposed, axis=0).max()
            assert drift < 2.25, (name, y, exposed)
            worst = max(worst, drift)
    return worst


def check_diagonal_rules(get):
    for name in ("Lslash", "lslash", "uni20BA"):
        z = get(name)
        if name == "uni20BA":
            xs = z.real.min() + np.ptp(z.real) * np.array((.08,.14,.46,.50))
        else:
            # L's foot may extend much further right than its diagonal.
            # Find the exposed ink on each side of the upright independently.
            stem = section(z, 181)[:2]
            xs = []
            grid = np.linspace(z.real.min(), z.real.max(), 131)
            for side in (grid[grid<stem[0]-4],grid[grid>stem[1]+4]):
                exposed = []
                for x in side:
                    bands = section(z,x,vertical=True).reshape(-1,2)
                    if any(140 < band.mean() < 548 and 11 < np.ptp(band) < 55 for band in bands):
                        exposed.append(x)
                assert len(exposed)>=3 and np.ptp(exposed)>9, (name, 'short exposed slash', exposed)
                xs.extend(np.quantile(exposed,(.32,.65)))
        strokes = []
        for x in xs:
            cuts = section(z, x, vertical=True).reshape(-1, 2)
            parts = [
                band for band in cuts if 100 < band.mean() < 548 and np.ptp(band) < 55
            ]
            assert len(parts) == (2 if name == "uni20BA" else 1), (name, x, parts)
            strokes.append(parts)
        # Compare both edges with one continuous straight line through the stem.
        for edge in np.array(strokes).reshape(4, -1).T:
            line = np.polyfit(xs, edge, 1)
            assert line[0] > .12, (name, 'slash slope', line[0])
            residual = edge - np.polyval(line, xs)
            assert np.ptp(residual) < 2.5, (name, "interrupted slash", residual)


def check_lira_pressure(get):
    z = get("uni20BA")
    # At this height the rightmost pair always belongs to the returning arc.
    ys = np.arange(58, 226, 4)
    walls = np.array([section(z, y)[-2:] for y in ys])
    slope = np.gradient(walls.mean(axis=1), ys)
    thickness = np.diff(walls, axis=1).ravel() / np.hypot(1, slope)
    assert min(thickness) > 15 and max(thickness) < 26, (
        "lira bowl weight",
        min(thickness),
        max(thickness),
    )


def check_figures(get):
    for name in ("eight", "eight.tnum"):
        ring = get(name)
        for start in (132, 480):
            heights = np.arange(start, start + 63, 7)
            cuts = np.array([section(ring, y) for y in heights]).reshape(-1, 2, 2)
            inclinations = np.gradient(cuts.mean(axis=2), heights, axis=0)
            thickness = np.diff(cuts, axis=2)[:, :, 0] / np.hypot(1, inclinations)
            assert np.max(abs(thickness - 24)) < 2.5, (
                name,
                "uneven bowl sides",
                thickness,
            )
    for name in ("five", "five.tnum"):
        ring = get(name)
        top = ring.imag.max()
        xs = ring.real.min() + np.ptp(ring.real) * np.array((0.54, 0.67, 0.80, 0.92))
        caps = [section(ring, x, vertical=True)[-2:] for x in xs]
        assert all(
            len(pair) == 2 and top - pair[1] < 1.5 and 15 < np.ptp(pair) < 26
            for pair in caps
        ), (name, "top rule", caps)
        assert np.ptp(caps, axis=0).max() < 2, (name, "wedge-shaped terminal", caps)


def check_joined_vowels(get, heavy_mono):
    for name in ("ae", "oe"):
        z = get(name)
        left = z.real.min()
        span = np.ptp(z.real)
        low = section(z, 143)
        upper = section(z, 363)
        # At the upper eye of e, œ has an outside left wall and æ has open air.
        # At the lower eye both have a left wall and a counter.
        u = (upper[0] - left) / span
        assert u > 0.27 if name == "ae" else u < 0.21, (name, "upper left opening", u)
        assert (
            len(low) >= 4
            and (low[0] - left) / span < 0.19
            and low[2] - low[1] > 0.07 * span
        ), (name, "lower eye", low)
        if heavy_mono:
            cuts = section(z, 390)
            gaps = zip(cuts[1:-1:2], cuts[2::2])
            eye = max(
                (b - a for a, b in gaps if (a + b) / 2 > left + 0.6 * span), default=0
            )
            assert eye > 0.12 * span, (name, "compressed upper e eye", eye, span)


def check_lira_foot(get):
    z = get("uni20BA")
    lo = z.real.min()
    span = np.ptp(z.real)
    top = section(z, 235)[-1]
    bottom = section(z, 73)[-1]
    assert top > lo + 0.90 * span and top - bottom > 0.045 * span, (
        "lira rising foot",
        top,
        bottom,
        span,
    )


def check_operator(font, tt, get):
    worst = 0.0
    for op, pair in PAIRS.items():
        glyphs = shape(font, op, {"ss01": True})
        assert tuple(tt.getGlyphName(row[0]) for row in glyphs) == pair and all(
            row[1] == 600 for row in glyphs
        ), (op, glyphs)
        seam = 600
        a = section(get(pair[0]), seam - 2, vertical=True)
        b = section(get(pair[1]), seam + 2 - 600, vertical=True)
        count = 6 if op in ("<=", ">=") else 2 if op in ("<-", "->") else 4
        assert len(a) == len(b) == count, (op, "strokes at cell seam", a, b)
        offset = max(abs(a - b))
        assert offset < 2.5, (op, "seam displacement", offset)
        worst = max(worst, offset)
    return worst


def examine(directory, family):
    path = directory / (family + "[wght,wdth,RADI].ttf")
    font = hb.Font(hb.Face(path.read_bytes()))
    slope = np.tan(np.deg2rad(9.5)) if family.endswith("-Italic") else 0.0
    worst_rail = worst_seam = 0.0
    with TTFont(path) as tt:

        def get(name):
            return unsheared(font, tt.getGlyphID(name), 0 if ".lig_" in name else slope)

        for weight, width, radius in product(
            (100, 175, 300, 400, 550, 700, 900), (65, 82.5, 100, 125, 150), (0, 100)
        ):
            font.set_variations(dict(wght=weight, wdth=width, RADI=radius))
            try:
                if weight == 100:
                    worst_rail = max(worst_rail, check_rails(get))
                    check_diagonal_rules(get)
                    check_figures(get)
                    check_lira_pressure(get)
                check_lira_foot(get)
                check_joined_vowels(get, "Mono" in family and weight >= 700)
                if "Mono" in family:
                    worst_seam = max(worst_seam, check_operator(font, tt, get))
            except AssertionError as e:
                raise AssertionError((family, weight, width, radius, *e.args)) from e
    print(
        f"{family} — maximum Thin rule drift {worst_rail:.2f} units"
        + (
            f", maximum operator seam deviation {worst_seam:.2f} units"
            if "Mono" in family
            else ""
        ),
        flush=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fonts", type=Path, default=OUTPUT)
    args = parser.parse_args()
    for family in TEXT:
        examine(args.fonts, family)
