"""Check the visible contour of U+002E in the delivered text fonts, including interpolation."""
import argparse
from itertools import product
from pathlib import Path

import numpy as np
from fontTools.ttLib import TTFont

from check_word_proof import Edges

ROOT = Path(__file__).resolve().parents[2]


def locations(font):
    if "fvar" not in font:
        yield {}
        return
    tags = {axis.axisTag for axis in font["fvar"].axes}
    if tags == {"wght"}:
        for weight in (400, 450, 500, 600, 700):
            yield {"wght": weight}
        return
    assert tags == {"wght", "wdth", "RADI"}, tags
    grid = product(range(100, 901, 100), (65, 82.5, 100, 125, 150), (0, 50, 100))
    for weight, width, radius in (*grid, (175, 73, 27), (350, 113, 73), (525, 142, 27), (775, 83, 73)):
        yield {"wght": weight, "wdth": width, "RADI": radius}


def circle_errors(draw, glyphs=None):
    pen = Edges(glyphs, 1)
    draw(pen)
    assert pen.contours == 1 and pen.edges, "full stop must have one closed contour"
    edges = np.asarray(pen.edges)
    # Include chord midpoints so an inscribed polygon fails even when its
    # vertices lie on a circle. Measure in displayed (including italic) space.
    points = np.concatenate((edges.ravel(), edges.mean(axis=1)))
    x, y = points.real, points.imag
    center = (x.min() + x.max()) / 2 + 1j * (y.min() + y.max()) / 2
    w, h = np.ptp(x), np.ptp(y)
    assert min(w, h) > 0
    radial_error = np.abs(np.abs(points - center) - (w + h) / 4).max()
    return abs(w - h), radial_error


def release_files():
    patterns = ("fonts/ttf/*.ttf", "fonts/otf/*.otf", "fonts/woff2/*.woff2",
                "fonts/variable/**/*.ttf", "fonts/variable/**/*.woff2",
                "site/fonts/admiralty/*.woff2", "packages/web/fonts/subsets/*-latin.woff2")
    return sorted(p for pattern in patterns for p in ROOT.glob(pattern) if "Symbols" not in p.name)


def check(files):
    assert files, "no text fonts to check"
    cases = 0
    worst_extent = worst_radial = 0
    for path in files:
        with TTFont(path) as font:
            for location in locations(font):
                glyphs = font.getGlyphSet(location=location)
                extent, radial = circle_errors(glyphs[font.getBestCmap()[0x2E]].draw, glyphs)
                # One coordinate unit allows the rounding of quadratic control
                # points and implied on-curve positions in the 1000-unit em.
                assert max(extent, radial) <= 1, (str(path), location, extent, radial)
                worst_extent, worst_radial = max(worst_extent, extent), max(worst_radial, radial)
                cases += 1
    print(f"{len(files)} files, {cases} full stops. Maximum width/height difference "
          f"{worst_extent:.3f} u; maximum radial error {worst_radial:.3f} u.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fonts", nargs="*", type=Path, help="font files (default: delivered editions)")
    check(parser.parse_args().fonts or release_files())
