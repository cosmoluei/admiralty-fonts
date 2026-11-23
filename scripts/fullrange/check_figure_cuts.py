"""Measure sharp numeral terminals and diagonal endpoints in compiled text fonts."""

import argparse
from itertools import product
from pathlib import Path

import numpy as np
import pathops
from fontTools.ttLib import TTFont

from check_word_proof import Edges


# Height band and outward direction selecting the corner of each terminal.
# For fractions and percent, the slash is the contour spanning the full height.
TIPS = {
    "one": (.65, 1, -1), "two": (.72, 1, -1), "five": (0, .32, -1),
    "six": (.74, 1, 1), "nine": (0, .25, -1),
    "onehalf": (.80, 1, 1+.2j), "percent": (.80, 1, 1+.2j), "uni2199": (.75, 1, 1+.2j),
}


def terminal_error(glyph, name, slant):
    path = pathops.Path()
    glyph.draw(path.getPen())
    contour = max(path.contours, key=lambda c: c.bounds[3] - c.bounds[1])
    pen = Edges(None, 1)
    contour.draw(pen)
    edges = np.asarray(pen.edges)
    edges -= slant * edges.imag
    distances = np.r_[0., np.cumsum(abs(edges[:, 1] - edges[:, 0]))]
    outline = np.interp(np.arange(0, distances[-1], .5), distances, np.r_[edges[:, 0], edges[-1, 1]])
    low, high, outward = TIPS[name]
    height = (outline.imag - outline.imag.min()) / np.ptp(outline.imag)
    in_band = np.flatnonzero((low <= height) & (height <= high))
    projection = (outline[in_band] * np.conj(outward)).real
    tip = in_band[np.argmax(projection)]

    # Fit the two rails 25–42 units from the apparent tip, beyond the bevel
    # even at Black. The sharp drawing should reach their intersection. Allow
    # 5 units for curved rails and the rounding of quadratic font coordinates.
    def rail(offsets):
        points = outline[(tip + offsets) % len(outline)]
        center = points.mean()
        direction = np.exp(.5j * np.angle(np.mean((points - center) ** 2)))
        return center, direction

    a, v = rail(np.arange(-84, -50))
    b, w = rail(np.arange(50, 84))
    cross = (v.conjugate() * w).imag
    if abs(cross) < .1:
        return float("inf")
    corner = a + v * ((b - a).conjugate() * w).imag / cross
    nearby = outline[(tip + np.arange(-100, 101)) % len(outline)]
    overhang = ((outline[tip] - corner) * np.conj(outward)).real / abs(outward)
    return max(float(min(abs(nearby - corner))), float(overhang))


def check_font(path):
    worst = 0.
    failures = []
    with TTFont(path) as font:
        slant = np.tan(np.deg2rad(-font["post"].italicAngle))
        names = list(TIPS)
        if "Serif" in font["name"].getDebugName(1):
            names.remove("two")  # The Serif two has a rounded upper terminal.
        for weight, width in product((400, 500, 700, 800, 900), (65, 82.5, 100, 125, 150)):
            glyphs = font.getGlyphSet(location={"wght": weight, "wdth": width, "RADI": 0})
            for name in names:
                error = terminal_error(glyphs[name], name, slant)
                worst = max(worst, error)
                if error > 5:
                    failures.append((name, weight, width, round(error, 1)))
    assert not failures, (path.name, "terminal misses projected corner", failures)
    return worst


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fonts", nargs="*", type=Path)
    paths = parser.parse_args().fonts or sorted(
        p for p in (Path(__file__).resolve().parents[2] / "fonts/variable/fullrange").glob("*.ttf")
        if "Symbols" not in p.name)
    assert paths, "no full-range text fonts"
    worst = max(check_font(path) for path in paths)
    print(f"{len(paths)} text fonts, largest figure terminal deviation {worst:.2f} units.")
