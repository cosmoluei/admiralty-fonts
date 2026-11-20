"""Check opposed diagonals and the apertures in the exported heavy Mono drawings."""

import argparse
from concurrent.futures import ProcessPoolExecutor
from itertools import product
from pathlib import Path

import numpy as np
import uharfbuzz as hb
from fontTools.ttLib import TTFont

from build_text_family import OUTPUT, TEXT
from check_optical_inventory import unsheared
from check_word_proof import section


def cross_error(z):
    lo, hi = z.imag.min(), z.imag.max()
    mid = (lo + hi) / 2
    height = hi - lo

    def arms(fractions):
        ys = lo + height * fractions
        cuts = [section(z, y) for y in ys]
        ys = ys - mid
        lines = []
        for reverse in (False, True):
            rows = [c[::-1] if reverse else c for c in cuts]
            outside = np.array([row[0] for row in rows])
            # The outside edge stays visible even after both arms have merged.
            # Find the longest straight portion outside the round caps and serifs.
            i, j = np.triu_indices(len(ys), 9)
            k = (outside[j] - outside[i]) / (ys[j] - ys[i])
            offsets = outside - k[:, None] * ys
            b = np.median(offsets, axis=1)
            residual = abs(offsets - b[:, None])
            rank = np.argmin(np.minimum(residual, 1.3).sum(axis=1))
            good = residual[rank] <= 1.3
            slope, outer = np.polyfit(ys[good], outside[good], 1)
            inner = np.array(
                [row[1] - slope * y for row, y in zip(rows, ys) if len(row) == 4]
            )
            # The uncapped parallel edge repeats the same intercept at several heights.
            if len(inner) < 4:
                raise ValueError("too little exposed inner rail to measure")
            neighborhood = abs(inner[:, None] - inner) <= 1.1
            inliers = neighborhood[neighborhood.sum(axis=1).argmax()]
            lines.append((slope, (outer + np.median(inner[inliers])) / 2))
        return np.array(lines)

    low = arms(np.linspace(0.055, 0.435, 59))
    high = arms(np.linspace(0.565, 0.945, 59))[::-1]
    return max(abs(low[:, 1] - high[:, 1]) / np.hypot(1, low[:, 0]))


def waist_landmark(outline):
    """Locate the waist and measure how far it recedes behind both lobes."""
    bottom, top = outline.imag.min(), outline.imag.max()

    def right(fraction):
        y = bottom + fraction * (top - bottom)
        return complex(section(outline, y)[-1], y)

    waist = min((right(level) for level in np.linspace(.465, .555, 15)), key=lambda z: z.real)
    recess = (min(right(.25).real, right(.75).real) - waist.real) / np.ptp(outline.real)
    return waist, recess


def bowl_recess(outline):
    return waist_landmark(outline)[1]


def heavy_apertures(get, italic):
    for name in ("germandbls", "Germandbls"):
        z = get(name)
        cuts = section(z, 42)
        assert len(cuts) >= 4 and cuts[2] - cuts[1] > 28, (
            name,
            "gap between stem and foot",
            cuts,
        )
        flank = [section(z, y)[-1] for y in (93, 178, 270)]
        assert flank[1] - max(flank[0], flank[2]) > 8, (
            name,
            "lower bowl loses its curve",
            flank,
        )
    for name, fraction in (
        ("a", 0.25 if italic else 0.36),
        ("ae", 0.15 if italic else 0.18),
    ):
        outline = get(name)
        cuts = section(outline, 140)
        minimum = np.ptp(outline.real) * fraction
        assert len(cuts) >= 4 and cuts[2] - cuts[1] > minimum, (
            name,
            "lower eye at y=140",
            cuts,
        )


def examine(args):
    directory, family = args
    path = directory / (family + "[wght,wdth,RADI].ttf")
    font = hb.Font(hb.Face(path.read_bytes()))
    italic = family.endswith("-Italic")
    slant = np.tan(np.deg2rad(9.5)) if italic else 0.0
    worst = 0
    with TTFont(path) as tt:

        def get(name):
            return unsheared(font, tt.getGlyphID(name), slant)

        for w, d, r in product(
            (100, 400, 700, 900), (65, 82.5, 100, 125, 150), (0, 100)
        ):
            font.set_variations(dict(wght=w, wdth=d, RADI=r))
            for name in ("X", "x", "multiply"):
                gap = cross_error(get(name))
                assert gap < 3.5, (
                    family,
                    name,
                    w,
                    d,
                    r,
                    "offset across intersection",
                    gap,
                )
                worst = max(worst, gap)
            if "Mono" in family and w == 100:
                cuts = section(get("W"), 396)
                # All four strokes are exposed here, below the middle crown.
                assert len(cuts) == 8 and max(np.diff(cuts)[::2]) < 28, (family, "W", d, r, cuts)
            if w >= 700 and r == 100:
                bowls = ("threesuperior", "uni2083")
                if "Serif" not in family:
                    bowls += ("B",)
                for name in bowls:
                    recess = bowl_recess(get(name))
                    assert recess > .065, (family, name, w, d, r, "indistinct waist", recess)
            if "Mono" in family and w >= 700:
                try:
                    heavy_apertures(get, italic)
                    # Broadening the eyes must still give the ligature a heavier colour.
                    a, b = get("ae").T
                    heavy = abs(np.vdot(a, b).imag)
                    font.set_variations(dict(wght=400, wdth=d, RADI=r))
                    a, b = get("ae").T
                    regular = abs(np.vdot(a, b).imag)
                    assert heavy > regular * (1.08 if w == 700 else 1.16), (
                        "ae ink gain",
                        heavy / regular,
                    )
                except AssertionError as exc:
                    raise AssertionError((family, w, d, r, str(exc))) from exc
    return family, worst


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fonts", type=Path, default=OUTPUT)
    args = parser.parse_args()
    with ProcessPoolExecutor(3) as pool:
        for family, worst in pool.map(
            examine, [(args.fonts, family) for family in TEXT]
        ):
            print(
                f"{family}  120 cross sections, maximum opposite-arm offset {worst:.2f} font units",
                flush=True,
            )
