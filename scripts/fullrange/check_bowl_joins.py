"""Check crossbar joins, bowl curvature and terminal cuts in compiled full-range fonts."""
import argparse
from itertools import product
from pathlib import Path
import unicodedata

import numpy as np
import pathops
from fontTools.ttLib import TTFont

from check_word_proof import Edges, section


def bowl_edges(glyphs, name):
    shape = pathops.Path()
    glyphs[name].draw(shape.getPen())
    body, eye = sorted(shape.contours, key=lambda c: abs(c.area), reverse=True)[:2]
    if name == 'ordfeminine':
        # At Black the underline can have more ink area than the small counter.
        body, eye = sorted(shape.contours, key=lambda c: c.bounds[3], reverse=True)[:2]
    elif name in ('ae', 'oe'):
        # The counter adjoining the crossbar is the right one at every width.
        eye = max((c for c in shape.contours if c.clockwise != body.clockwise), key=lambda c: c.bounds[0])
    assert body.clockwise != eye.clockwise, (name, 'missing eye')
    edges = []
    for contour in (body, eye):
        pen = Edges(None, 1)
        contour.draw(pen)
        edges.append(np.array(pen.edges))
    return edges


def crossbar_position(body, eye, fraction=.45):
    x = eye.real.min() + fraction * np.ptp(eye.real)
    top = section(eye, x, vertical=True)[0]
    crossings = section(body, x, vertical=True)
    bar = crossings[crossings < top].max()

    return x, bar, top


def crossbar_spur(body, eye):
    # Extrapolate the inside wall to one unit under the crossbar to distinguish
    # a wedge at the join from a smoothly turning bowl.
    x, bar, top = crossbar_position(body, eye)

    def wall(y):
        cuts = section(body, y)
        return cuts[cuts < x].max()

    offsets = -np.array([.14, .11, .08]) * np.ptp(body.imag)
    wall_curve = np.polyfit(offsets, [wall(bar + offset) for offset in offsets], 2)
    return wall(bar - 1) - np.polyval(wall_curve, -1), top - bar


def turn_reversal(coordinates):
    # A forward-moving arc changes direction progressively. A local flat or a
    # bulge shows up as a reversal of the secant's angle before the cut.
    curve = np.array(coordinates)
    angles = np.degrees(np.arctan((curve[12:] - curve[:-12]) / 12))
    return max(np.maximum.accumulate(angles) - angles)


def e_wall_reversal(body, eye, *, angled_bar=False):
    x, bar, _ = crossbar_position(body, eye)
    if angled_bar:
        # A ligature can have a diagonal crossbar, especially in Serif Italic.
        # Project its underside to the wall before taking vertical samples.
        x2, bar2, _ = crossbar_position(body, eye, .67)
        hits = section(body, bar - 60)
        joint_x = max(hits[hits < x])
        bar += (bar2 - bar) * (joint_x - x) / (x2 - x)
    height = np.ptp(body.imag)
    wall = []
    for y in np.arange(bar - 4, bar - .16 * height, -1):
        cuts = section(body, y)
        wall.append(max(cuts[cuts < x]))
    return turn_reversal(wall)


def e_turn_reversals(body, eye, slant, radius):
    body = body - slant * body.imag
    eye = eye - slant * eye.imag
    height = np.ptp(body.imag)
    lip = body[:, 0][body[:, 0].imag < body.imag.min() + .28 * height]
    midpoints = []
    previous_top = -np.inf
    # End at the start of the terminal cut, where the upper edge turns down.
    for x in np.arange(body.real.min() + .53 * np.ptp(body.real), lip.real.max() - .1):
        lower, upper = section(body, x, vertical=True)[:2]
        if upper < previous_top:
            break
        midpoints.append((lower + upper) / 2)
        previous_top = upper
    if radius:
        # The intentionally rounded tip turns back on itself. Measure the arm
        # before the fillet: 12 units at full radius, proportional in between.
        midpoints = midpoints[:-max(1, round(.12 * radius))]

    return e_wall_reversal(body, eye), turn_reversal(midpoints)


def check_related_e_walls(font, family, slant):
    # The italic ligatures have independently fitted right-hand bowls. The
    # estimated sign's thin wall also receives a separate fit outside upright Mono.
    names = ['ae', 'oe'] if slant else []
    if slant or 'Mono' not in family:
        names.append('uni212E')
    count = 0
    for w, d, r in ((100, 65, 0), (100, 65, 100), (104, 72, 50), (100, 100, 0), (100, 150, 0)):
        glyphs = font.getGlyphSet(location={'wght': w, 'wdth': d, 'RADI': r})
        for name in names:
            body, eye = bowl_edges(glyphs, name)
            turn = e_wall_reversal(body - slant * body.imag, eye - slant * eye.imag, angled_bar=True)
            assert turn < 3, (family, name, w, d, r, 'crossbar wall reversal', turn)
            count += 1
    return count


def ordinal_corner_distances(body):
    # The upper-left terminal is isolated above the waist. Follow its outline
    # across the cut and measure physical distance to each projected corner.
    points = body[:, 0]
    wing = ((points.real < points.real.min() + .60 * np.ptp(points.real)) &
            (points.imag > points.imag.min() + .57 * np.ptp(points.imag)))
    runs = []
    for start in np.flatnonzero(wing & ~np.roll(wing, 1)):
        end = np.flatnonzero(~np.roll(wing, -start))[0]
        runs.append(np.roll(points, -start)[:end])
    terminal = max(runs, key=lambda run: np.ptp(run.real))
    distances = np.r_[0., np.cumsum(abs(np.diff(terminal)))]
    samples = np.interp(np.arange(0, distances[-1], .25), distances, terminal)
    lower, upper = samples.imag.argmin(), samples.real.argmin()
    if upper < lower:
        samples = samples[::-1]
        lower, upper = len(samples) - 1 - lower, len(samples) - 1 - upper

    # Fitting each line away from its endpoint preserves the intended curve
    # while measuring any secondary bevel at the junction.
    def line(segment):
        center = segment.mean()
        direction = np.exp(.5j * np.angle(np.mean((segment - center) ** 2)))
        return center, direction

    span = upper - lower
    inset = max(18, min(54, round(.19 * span)))
    center, direction = line(samples[lower + round(.48 * span):lower + round(.82 * span)])
    near = samples[max(0, lower - 3 * inset):upper + 3 * inset]

    def corner_gap(neighbor):
        origin, tangent = line(neighbor)
        along = ((origin - center) * tangent.conjugate()).imag / (direction * tangent.conjugate()).imag
        return min(abs(near - (center + along * direction)))

    return (corner_gap(samples[max(0, lower - 3 * inset):lower - inset]),
            corner_gap(samples[upper + inset:upper + 3 * inset]))


def left_bowl_turns(body, eye, slant):
    # Measure angular change across a finite physical window on the free left
    # curve. An individual short, quantized TrueType tangent is not a visible kink.
    box = eye.real - slant * eye.imag
    left, bottom = box.min(), eye.imag.min()
    width, height = np.ptp(box), np.ptp(eye.imag)
    angles = []
    for contour in (body, eye):
        points = np.r_[contour[:, 0], contour[-1, 1]]
        points = points.real - slant * points.imag + 1j * points.imag
        distance = np.r_[0., np.cumsum(abs(np.diff(points)))]
        samples = np.linspace(0, distance[-1], max(6, round(distance[-1] / 2)), endpoint=False)
        curve = np.interp(samples, distance, points.real) + 1j * np.interp(samples, distance, points.imag)
        stride = max(2, round(.065 * min(width, height) / 2))
        before, after = curve - np.roll(curve, stride), np.roll(curve, -stride) - curve
        turn = abs(np.angle(before.conjugate() * after, deg=True))
        flank = ((curve.real < left + .36 * width) & (curve.imag > bottom + .08 * height)
                 & (curve.imag < bottom + .90 * height))
        angles.append(max(turn[flank]))
    return angles


def check_accent_bases(font):
    # These precomposed characters inherit the exact base outline. A frozen
    # copy of an old a or e in an accented glyph would break that guarantee.
    cmap = font.getBestCmap()
    count = 0
    for cp, name in cmap.items():
        nfd = unicodedata.normalize('NFD', chr(cp))
        if len(nfd) == 1 or nfd[0] not in 'ae':
            continue
        parts = font['glyf'][name].getComponentNames(font['glyf'])
        assert parts and parts[0] == cmap[ord(nfd[0])], (name, 'accent lost its base', parts)
        count += 1
    return count


def check_font(path):
    checks = 0
    with TTFont(path) as font:
        assert {a.axisTag for a in font['fvar'].axes} == {'wght', 'wdth', 'RADI'}, path
        family = font['name'].getDebugName(1)
        slant = np.tan(np.radians(-font['post'].italicAngle))
        accents = check_accent_bases(font)
        assert accents >= 39, (path, accents)
        checks += check_related_e_walls(font, family, slant)
        if 'Sans' in family:
            for weight, width, radius in product((104, 250), (72, 112), (0, 50, 100)):
                gs = font.getGlyphSet(location={'wght': weight, 'wdth': width, 'RADI': radius})
                spur, thickness = crossbar_spur(*bowl_edges(gs, 'e'))
                # RADI intentionally adds a small fillet at the inner corner.
                allowance = 6 + .5 * thickness * radius / 100
                assert spur <= allowance, (path, weight, width, radius, 'e crossbar spur', spur)
                checks += 1
            for w, d in ((100, 65), (104, 72), (150, 82), (100, 100), (100, 150)):
                for r in (0, 50, 100):
                    gs = font.getGlyphSet(location={'wght': w, 'wdth': d, 'RADI': r})
                    waist, lip = e_turn_reversals(*bowl_edges(gs, 'e'), slant, r)
                    assert max(waist, lip) < 3, (path, w, d, r, 'e wall / lip reversal', waist, lip)
                    checks += 2
            if not slant:
                # Website reproduction plus the two Thin width extremes. Wide
                # a has a shallower eye and consequently needs a greater turn.
                for w, d, outer_limit, inner_limit in ((122, 105, 12, 16), (100, 65, 13, 14), (100, 150, 14, 22)):
                    gs = font.getGlyphSet(location={'wght': w, 'wdth': d, 'RADI': 0})
                    outside, inside = left_bowl_turns(*bowl_edges(gs, 'a'), slant)
                    assert outside <= outer_limit and inside <= inner_limit, (path, w, d, 'a bowl', outside, inside)
                    checks += 1
        for w, d, r in product((700, 800, 900), (65, 82.5, 100, 125, 150), (0, 50, 100)):
            gs = font.getGlyphSet(location={'wght': w, 'wdth': d, 'RADI': r})
            body, eye = bowl_edges(gs, 'ordfeminine')
            _, turn = left_bowl_turns(body, eye, slant)
            assert np.ptp(eye.imag) >= 48 and turn < 45, (path, w, d, r, 'ª eye', np.ptp(eye.imag), turn)
            lower, upper = ordinal_corner_distances(body)
            # At RADI 0 both corners should meet the cut within 3 units. At
            # positive radii the larger corner must display a real fillet.
            assert .04 * r <= max(lower, upper) <= 3 + .13 * r, (
                path, w, d, r, 'ª terminal cut', lower, upper)
            checks += 3
    return checks, accents


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('fonts', nargs='*', type=Path)
    paths = parser.parse_args().fonts or sorted(
        p for p in (Path(__file__).resolve().parents[2] / 'fonts/variable/fullrange').glob('*.ttf')
        if 'Symbols' not in p.name)
    assert paths, 'no full-range fonts'
    results = [check_font(path) for path in paths]
    print(f'{len(paths)} fonts, {sum(n for n, _ in results)} bowl measurements, '
          f'{sum(n for _, n in results)} accented glyphs.')
