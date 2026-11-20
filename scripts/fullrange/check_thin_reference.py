"""Compare every text glyph at Thin and Regular with the other axes held fixed."""

import argparse
import ctypes
from concurrent.futures import ProcessPoolExecutor
from itertools import product
from pathlib import Path

import freetype as ft
import numpy as np
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from scipy.spatial import cKDTree

from build_text_family import OUTPUT, TEXT
from check_optical_inventory import unsheared
from check_word_proof import section

GRID = tuple(product((65, 82.5, 100, 125, 150), (0, 100)))


def ink(face, gid):
    face.load_glyph(gid, ft.FT_LOAD_RENDER | ft.FT_LOAD_NO_HINTING | ft.FT_LOAD_NO_BITMAP)
    b = face.glyph.bitmap
    if not b.width or not b.rows:
        return 0.0
    pixels = np.frombuffer(ctypes.string_at(b._FT_Bitmap.buffer, b.pitch * b.rows), np.uint8)
    return pixels.reshape(b.rows, b.pitch)[:, : b.width].sum() / 255.0


def check_stations(get, serif, mono):
    def vertical(z, fraction):
        x = z.real.min() + fraction * np.ptp(z.real)
        return section(z, x, vertical=True)

    def near(value, expected, tol, label):
        assert np.max(abs(np.asarray(value) - expected)) < tol, (label, value, expected)

    if not serif:
        for n, ys in (("K", (490, 555, 620)), ("R", (82, 153, 224))):
            cuts = np.array([section(get(n), y) for y in ys])
            centers = (cuts[:, 2] + cuts[:, 3]) / 2
            slope = (centers[-1] - centers[0]) / (ys[-1] - ys[0])
            near((cuts[:, 3] - cuts[:, 2]) / np.hypot(1, slope), 24, 2.1, n + " diagonal")
            near(cuts[:, 1] - cuts[:, 0], 24, 1.8, n + " stem")
        near(np.diff(section(get("J"), 350)), 24, 1.8, "J stem")
        near(np.diff(section(get("Q"), 350))[[0, 2]], 24, 2.1, "Q bowl walls")
        if mono:
            near(np.diff(section(get("f"), 320)), 24, 2.1, "Mono f stem")

    pound = get("numbersign")
    levels = np.array([section(pound, y) for y in (100, 150, 320, 540, 620)])
    centres = (levels[:, ::2] + levels[:, 1::2]) / 2
    slope = (centres[-1] - centres[0]) / 520
    near((levels[:, 1::2] - levels[:, ::2]) / np.hypot(1, slope), 24, 1.8, "# rail thickness")
    near(centres[1:] - centres[:1], np.array([50, 220, 440, 520])[:, None] * slope, 1.8, "# parallel rails")
    near(vertical(pound, 0.05), [211, 231, 457, 477], 1.9, "# bars")

    lari = get("uni20BE")
    posts = section(lari, 705)
    near(posts[1::2] - posts[::2], 19.2, 1.8, "lari posts")
    left, right = (posts[::2] + posts[1::2]) / 2
    xs = left + (right - left) * np.array([0.21, 0.5, 0.79])
    roof = np.array([section(lari, x, vertical=True)[-2:] for x in xs])
    assert min(roof[1].mean() - roof[[0, 2]].mean(axis=1)) > 2.0, ("flat lari arch", roof)
    slopes = np.array(
        [
            (
                section(lari, x + 2, vertical=True)[-2:].mean()
                - section(lari, x - 2, vertical=True)[-2:].mean()
            )
            / 4
            for x in xs
        ]
    )
    near(roof[:, 1] - roof[:, 0], np.hypot(18 if serif else 22, 24 * slopes), 2.5, "lari crown thickness")
    near(
        [np.diff(vertical(lari, x)[:2])[0] for x in (0.63, 0.73, 0.88)], 18 if serif else 22, 1.8, "lari foot"
    )

    for n in ("Oslash", "oslash"):
        mid = 350 if n == "Oslash" else 260
        cuts = section(get(n), mid)
        assert len(cuts) == 6, (n, "missing counters", cuts)
        near(np.diff(cuts)[[0, 4]], 24, 1.9, n + " bowl walls")

    for n in ("four", "four.tnum"):
        z = get(n)
        near(np.diff(section(z, 350)[-2:])[0], 24, 1.9, n + " upright")
        bar = vertical(z, 0.48)[:2]
        near(bar.mean(), 201 if serif else 209, 1.8, n + " crossbar height")
        near(np.diff(bar)[0], 16 if serif else 22, 1.8, n + " crossbar thickness")

    # Sample along the whole boundary, including long lines. A section
    # through a nearly tangent join can gain two crossings from grid rounding.
    def outline_distance(a, b):
        def dense(z):
            rows = []
            for p, q in z:
                rows.append(p + (q - p) * np.linspace(0, 1, max(2, int(np.ceil(abs(q - p))) + 1)))
            values = np.concatenate(rows)
            return np.column_stack((values.real, values.imag))

        a, b = dense(a), dense(b)
        return max(cKDTree(a).query(b)[0].max(), cKDTree(b).query(a)[0].max())

    six, tab = get("six"), get("six.tnum")
    aligned = (
        (tab.real - tab.real.min()) * np.ptp(six.real) / np.ptp(tab.real) + six.real.min() + 1j * tab.imag
    )
    near(outline_distance(six, aligned), 0, 3.0, "tabular six skeleton")
    sup, sub = (get(n) for n in ("threesuperior", "uni2083"))
    high, low = [z - (z.real.min() + z.real.max()) / 2 for z in (sup, sub)]
    near(outline_distance(high, low + 450j), 0, 3.0, "raised / lowered three")

    won = get("won")
    bars = vertical(won, 0.04)
    bars = bars[(bars > 200) & (bars < 460)]
    expected = (256, 416) if mono else (251, 411) if serif else (254, 414)
    near((bars[::2] + bars[1::2]) / 2, expected, 1.8, "won crossbar heights")
    near(bars[1::2] - bars[::2], 18 if serif else 20, 1.8, "won crossbar thickness")


def inspect(arguments):
    directory, family = arguments
    path = directory / (family + "[wght,wdth,RADI].ttf")
    faces = [ft.Face(str(path)) for _ in (100, 400)]
    for face in faces:
        face.set_pixel_sizes(0, 64)
    font = hb.Font(hb.Face(path.read_bytes()))
    with TTFont(path) as tt:
        order = tt.getGlyphOrder()
        slant = np.tan(np.deg2rad(9.5)) if "Italic" in family else 0.0
        for width, radius in GRID:
            for face, w in zip(faces, (100, 400)):
                face.set_var_design_coords((w, width, radius))
            for gid, name in enumerate(order):
                thin, regular = [ink(face, gid) for face in faces]
                assert bool(thin) == bool(regular), (family, name, width, radius, "lost or added ink")
            font.set_variations(dict(wght=100, wdth=width, RADI=radius))

            def get(n):
                return unsheared(font, tt.getGlyphID(n), slant)

            try:
                check_stations(get, "Serif" in family, "Mono" in family)
            except (AssertionError, ValueError) as exc:
                raise AssertionError((family, width, radius, str(exc))) from exc
    return family, len(order) * len(GRID)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fonts", type=Path, default=OUTPUT)
    args = parser.parse_args()
    with ProcessPoolExecutor(3) as pool:
        for family, pairs in pool.map(inspect, [(args.fonts, f) for f in TEXT]):
            print(f"{family}  {pairs} same-width Thin / Regular comparisons and stroke checks")
