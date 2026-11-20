"""Check the released Serif drawings and thin strokes in the compiled alphabet."""
import math

import numpy as np
from fontTools.ttLib import TTFont
from scipy.spatial import cKDTree

from build_text_family import OUTPUT, RELEASE, SERIF_LETTERS
from check_axis_study import boundary_points, shape
from junction_drawings import revised_default
from check_word_proof import Edges, section


def compare_regular(font, release, family):
    distances = {}
    for name in sorted(SERIF_LETTERS):
        a = boundary_points(shape(font.getGlyphSet(), name))
        reference = revised_default(release, family, name) if name in ("ae", "oe") else shape(release.getGlyphSet(), name)
        b = boundary_points(reference)
        distances[name] = max(cKDTree(a).query(b)[0].max(), cKDTree(b).query(a)[0].max())
    return max(distances.items(), key=lambda item: item[1])


def segments(glyphs, name, slant):
    pen = Edges(glyphs, 1)
    glyphs[name].draw(pen)
    edges = np.asarray(pen.edges)
    return edges - slant * edges.imag


def diagonal_widths(edges, name):
    # Take three sections away from the serifs. Project onto the local
    # normal so that widening a diagonal never makes the test overweight it.
    sections = []
    for height in (192, 280, 370):
        cuts = section(edges, height)
        index = 2 if name == 'N' else 0
        left, right = cuts[index:index + 2]
        sections.append(((left + right) / 2, right - left))
    slope = (sections[2][0] - sections[0][0]) / (370 - 192)
    return np.asarray(sections)[:, 1] / math.hypot(1, slope)


def check_thin_stations(glyphs, slant):
    # Project horizontal slices onto each stroke normal. In the old x the
    # fine diagonal measured anywhere from 12 to 21 units as wdth changed.
    cases = (
        ('A', (300, 346, 395), (18, 24)), ('X', (114, 164, 214), (18, 24)),
        ('x', (75, 110, 145), (18, 24)), ('K', (112, 165, 218), (24, 24)),
        ('k', (133, 158, 182), (24, 24)), ('Y', (445, 495, 545), (24, 18)),
        ('y', (250, 304, 358), (24, 18)),
    )
    for name, heights, targets in cases:
        edges = segments(glyphs, name, slant)
        cuts = np.array([section(edges, y) for y in heights])
        centers = (cuts[:, 1::2] + cuts[:, ::2]) / 2
        slope = (centers[-1] - centers[0]) / (heights[-1] - heights[0])
        width = (cuts[:, 1::2] - cuts[:, ::2]) / np.hypot(1, slope)
        assert np.max(abs(width - targets)) < 2, (name, 'Thin diagonal sections', width)
    for name in 'CGQacdm':
        edges = segments(glyphs, name, slant)
        top = 712 if name.isupper() else 530
        near_crown = edges.real[abs(edges.imag - top) < .7]
        # Ascenders and the two arches of m have separate high points.
        x = np.min(near_crown)
        cuts = section(edges, x, vertical=True)
        crown = cuts[np.abs(cuts - top) < 32]
        assert len(crown) == 2 and abs(np.diff(crown)[0] - 18) < 2.5, (name, 'Thin crown', crown)
    for name, y in (('J', 380), ('R', 123), ('f', 300), ('u', 300)):
        cuts = section(segments(glyphs, name, slant), y)
        assert abs(cuts[1] - cuts[0] - 24) < 1.8, (name, 'Thin shaft', cuts)
    f = segments(glyphs, 'f', slant)
    left, right = section(f, 511)
    cuts = section(f, left + .18 * (right - left), vertical=True)
    crossbar = cuts[(cuts > 485) & (cuts < 535)]
    assert len(crossbar) == 2 and max(abs(crossbar - [502, 520])) < 1.8, ('f crossbar', crossbar)


def check_thin(font, italic):
    slant = math.tan(math.radians(9.5)) if italic else 0
    for width in (65, 75, 90, 100, 115, 137, 150):
        for radius in (0, 50, 100):
            gs = font.getGlyphSet(location=dict(wght=100, wdth=width, RADI=radius))
            check_thin_stations(gs, slant)
            for name in ('N', 'z', 'Z'):
                values = diagonal_widths(segments(gs, name, slant), name)
                assert max(abs(values - 24)) < 2.5, ('Thin diagonal', name, width, radius, values)
            for name in ('o', 'O'):
                curve = segments(gs, name, slant)
                cuts = section(curve, 350 if name == 'O' else 260)
                walls = cuts[1::2] - cuts[::2]
                assert max(abs(walls - 24)) < 2, ('Thin oval wall', name, width, radius, walls)
                center = (cuts[0] + cuts[-1]) / 2
                vertical = section(curve, center, vertical=True)
                caps = vertical[1::2] - vertical[::2]
                assert max(abs(caps - 18)) < 2, ('Thin oval crown', name, width, radius, caps)
            for name, fractions in (('m', (.53, .56, .59)), ('q', (.58, .65, .70)),
                                    ('ae', (.37, .42, .60)), ('oe', (.37, .42, .60))):
                curve = segments(gs, name, slant)
                for fraction in fractions:
                    x = curve.real.min() + fraction * np.ptp(curve.real)
                    cuts = section(curve, x, vertical=True)
                    assert len(cuts) >= 2 and cuts[-1] - cuts[-2] > 14, ('vanishing arch', name, width, radius, fraction, cuts)
            curve = segments(gs, 's', slant)
            xs = curve.real.min() + np.linspace(.33, .67, 13) * np.ptp(curve.real)
            cuts = [section(curve, x, vertical=True) for x in xs]
            assert all(len(row) == 6 for row in cuts), ('s spine crossings', width, radius)
            spine = np.array([(row[2] + row[3]) / 2 for row in cuts])
            slopes = np.diff(spine) / np.diff(xs)
            widths = np.array([row[3] - row[2] for row in cuts]) / np.hypot(1, np.gradient(spine, xs))
            assert max(slopes) < 0 and max(abs(np.diff(slopes))) < .12, ('s spine tangent', width, radius, slopes)
            assert min(widths) > 21 and max(widths) < 29, ('s spine thickness', width, radius, widths)
            if not italic:
                link = segments(gs, 'g', slant)
                for y in (119, 140, 163):
                    cuts = section(link, y)
                    assert len(cuts) == 2 and 15 <= cuts[1] - cuts[0] <= 31, ('g link', width, radius, y, cuts)
                e = segments(gs, 'e', slant)
                for fraction in (.35, .60, .78):
                    lo, hi = e.real.min(), e.real.max()
                    cuts = section(e, lo + fraction * (hi - lo), vertical=True)
                    crossbar = cuts[(cuts > 230) & (cuts < 300)]
                    assert len(crossbar) == 2 and max(abs(crossbar - [255, 273])) < 2, ('e crossbar', width, radius, crossbar)


if __name__ == '__main__':
    for family in ('AdmiraltySerif', 'AdmiraltySerif-Italic'):
        with TTFont(OUTPUT / (family + '[wght,wdth,RADI].ttf')) as font, TTFont(RELEASE.with_name(family + '[wght].ttf')) as release:
            worst, distance = compare_regular(font, release, family)
            assert distance < 1.15, ('default outline distance', family, worst, distance)
            check_thin(font, family.endswith('-Italic'))
            print(f'{family}: {len(SERIF_LETTERS)} default drawings, max distance {distance:.2f} ({worst}); Thin stroke checks passed')
