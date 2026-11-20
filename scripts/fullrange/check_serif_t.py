"""Measure the cap, shoulder, crossbar and returning foot on the exported Serif t."""
import itertools
import math

from fontTools.ttLib import TTFont
import numpy as np
from scipy.spatial import cKDTree

from build_text_family import OUTPUT, RELEASE
from check_axis_study import boundary_points, shape
from check_word_proof import Edges, section


def landmarks(glyphs, name, slant):
    pen = Edges(glyphs, 1)
    glyphs[name].draw(pen)
    edge = np.asarray(pen.edges)
    edge = edge - edge.imag * slant
    _, right = section(edge, 350)
    bottom = edge.imag.min()
    foot_end = edge.real[edge.imag < 190].max()
    arm_end = edge.real[(edge.imag > 445) & (edge.imag < 526)].max()
    heights = []
    for fraction in (.35, .65):
        cuts = section(edge, right + fraction * (arm_end - right), vertical=True)
        heights.append(cuts[cuts > 420])
    foot = section(edge, right + .90 * (foot_end - right), vertical=True)
    shoulder = [section(edge, y) for y in (535, 550, 580, 605, 630)]
    return edge.imag.max(), bottom, heights, min(foot) - bottom, shoulder


def check(font, italic=False):
    slant = math.tan(math.radians(9.5)) if italic else 0
    samples = itertools.product((100, 150, 250, 400, 525, 700, 825, 900),
                                (65, 77, 91, 100, 118, 137, 150), (0, 37, 73, 100))
    count = 0
    for w, d, r in samples:
        loc = dict(wght=w, wdth=d, RADI=r)
        gs = font.getGlyphSet(location=loc)
        for name in ('t', 'tbar'):
            top, bottom, arm, rise, shoulder = landmarks(gs, name, slant)
            label = (name, w, d, r)
            assert abs(top - 654) <= 1 and abs(bottom + 10) <= 1, ('height', label, top, bottom)
            assert all(len(cut) == 2 for cut in arm), ('crossbar intersections', label, arm)
            arm = np.asarray(arm)
            assert np.max(abs(arm[:, 1] - 520)) <= 1, ('crossbar height', label, arm)
            assert np.max(abs(arm[0] - arm[1])) <= 1, ('crossbar tilts', label, arm)
            assert 4 < rise < 36, ('foot sweeps out of its intended range', label, rise)
            assert all(len(cut) == 2 for cut in shoulder), ('missing shoulder', label, shoulder)
            shoulder = np.array([cut[0] for cut in shoulder])
            assert np.all(np.diff(shoulder) >= -.6) and shoulder[-1] - shoulder[0] > 9, ('shoulder reverses or disappears', label, shoulder)
            count += 1
    return count


def reference_distance(font, release):
    errors = []
    for name in ('t', 'tbar'):
        a, b = (boundary_points(shape(f.getGlyphSet(), name)) for f in (font, release))
        errors.append(max(cKDTree(a).query(b)[0].max(), cKDTree(b).query(a)[0].max()))
    return max(errors)


if __name__ == '__main__':
    for family in ('AdmiraltySerif', 'AdmiraltySerif-Italic'):
        path = OUTPUT / (family + '[wght,wdth,RADI].ttf')
        with TTFont(path) as font, TTFont(RELEASE.with_name(family + '[wght].ttf')) as release:
            distance = reference_distance(font, release)
            assert distance < 1, ('default outline differs from 0.300', family, distance)
            count = check(font, family.endswith('-Italic'))
            print(f'{family} — {count} t and tbar outlines passed, default distance {distance:.2f} units')
