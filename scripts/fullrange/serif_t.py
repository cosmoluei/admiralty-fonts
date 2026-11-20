"""The Serif t and stroked t share a shoulder, crossbar and returning foot."""
import numpy as np

from compatible import Contour, OutlinePen, Profile, compatible_points


def draw_t(advance, weight, width, barred):
    # Use the 0.300 landmarks verbatim in the reference recipe. The feet of
    # the wide and narrow masters take up different space, with the same cut.
    stem = {100: 24, 400: {65: 83, 100: 92, 150: 98}[width], 900: 132}[weight]
    bar = {100: 18, 400: 48, 900: 66}[weight]
    cap = {100: 13, 400: 36, 900: 52}[weight]
    toe = {100: 15, 400: 36, 900: 52}[weight]
    center = advance * (148 / 354)
    left, right = center - stem / 2, center + stem / 2
    lead = advance * (36 / 354)
    end = advance - max(12, advance * (16 / 354))
    arm = end - (end - right) / 6
    bar_floor = 520 - bar
    bottom = -10
    outer = center + (end - center) * (88 / 190)
    inner = outer + (18 / 92) * stem
    turn = bottom + 48 + (outer - left) * (102 / 134)
    floor = bottom + bar
    rise = min(34, max(19, 28 * ((end - outer) / 102) ** .38))
    tip = bottom + rise
    inner_end = end - toe / 6
    shoulder = right - cap

    pen = OutlinePen(None)
    pen.moveTo((outer, bottom))
    pen.curveTo((outer - .58 * (outer - left), bottom),
                (left, turn - .58 * (turn - bottom)), (left, turn))
    if barred:
        second_left = lead + (left - lead) / 11
        second_right = right + (arm - right) * (92 / 120)
        low, high = 268 - bar / 2, 268 + bar / 2
        for p in ((left, low), (second_left, low), (second_left, high), (left, high)):
            pen.lineTo(p)
    pen.lineTo((left, bar_floor))
    pen.lineTo((lead, bar_floor))
    pen.lineTo((lead, 520 - bar / 4))
    # The flag rises concavely from the left tip at every weight. The shaft
    # and its flat cap meet the very same points throughout interpolation.
    reach = shoulder - lead
    if weight == 100:
        # Let a wide hairline spend its extra length close to the crossbar.
        # Raising the whole span would make a dark triangular flag.
        first, second, lift = {65: (.70, .94, 570), 100: (.79, .96, 553),
                               150: (.86, .98, 542)}[width]
        controls = (lead + first * reach, 520), (lead + second * reach, lift)
    else:
        controls = (lead + .56 * reach, 530), (shoulder - .148 * reach, 574)
    pen.curveTo(*controls, (shoulder, 654))
    for p in ((right, 654), (right, 520), (arm, 520), (arm, bar_floor), (right, bar_floor)):
        pen.lineTo(p)
    if barred:
        for p in ((right, high), (second_right, high), (second_right, low), (right, low)):
            pen.lineTo(p)
    inner_turn = turn + 2
    pen.lineTo((right, inner_turn))
    pen.curveTo((right, inner_turn - .58 * (inner_turn - floor)),
                (inner - .55 * (inner - right), floor), (inner, floor))
    pen.curveTo((inner + .36 * (inner_end - inner), floor),
                (inner_end - .31 * (inner_end - inner), floor + .23 * (tip + toe - floor)),
                (inner_end, tip + toe))
    pen.lineTo((end, tip))
    pen.curveTo((end - .24 * (end - outer), bottom + .36 * rise),
                (outer + .45 * (end - outer), bottom), (outer, bottom))
    pen.closePath()
    return pen.contours[0]


def serif_t_tracks(design, name, cells):
    barred = name == 'tbar'
    glyphs = design.regular.getGlyphSet()
    regular = OutlinePen(glyphs)
    glyphs[name].draw(regular)
    native = regular.contours[0]
    landmarks = draw_t(354, 400, 100, barred).pieces[:, 0]
    # The italic release has additional quadratic extrema from its slant.
    # Match the anatomical landmarks and retain all its original curves.
    skew = design.slant
    landmarks = landmarks + skew * (landmarks.imag - 250)
    ids = np.argmin(abs(native.pieces[:, 0, None] - landmarks), axis=0)
    ids[0] = 0
    if not np.all(np.diff(ids) > 0):
        raise ValueError(f'{design.family} {name}: reference landmarks out of order')
    reference = np.r_[native.knots[ids], 1.]
    profiles = []
    for w, d in cells:
        if (w, d) == (400, 100):
            ring, knots = native, reference
        else:
            ring = draw_t(design.advance('t', w, d), w, d, barred)
            if skew:
                ring = Contour(ring.pieces + skew * (ring.pieces.imag - 250))
            knots = ring.knots
        for radius in (0, {100: 4, 400: 12, 900: 18}[w]):
            profiles.append(Profile(ring, reference, knots, radius))
    tracks = compatible_points(profiles, tolerance=.15)
    return tracks, [len(tracks[0]) - 1]
