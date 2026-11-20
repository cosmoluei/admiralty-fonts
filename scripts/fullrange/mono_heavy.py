"""Black Mono a and eszett. Reserve their apertures inside the 600-unit cell."""

import numpy as np
import pathops

from compatible import OutlinePen, ordered_contours
from thin_figures import bounds

NAMES = {"a", "ordfeminine", "germandbls", "Germandbls"}


def double_a(l, r, stem, hair, side_ratio=0.28):
    span = r - l
    x = lambda f: l + f * span
    post = r - stem
    # The original has a rising waist, a flat right wall and a larger lower
    # bowl. Set all three before fitting the hook into its remaining space.
    crown = x(0.505)
    floor = x(0.406)
    tip = x(0.087)
    p = pathops.Path()
    p.moveTo(r, 0)
    p.lineTo(r, 342)
    p.cubicTo(r, 456, x(0.79), 530, crown, 530)
    p.cubicTo(x(0.34), 530, x(0.19), 508, tip, 473)
    p.lineTo(tip + 0.26 * stem, 473 - 0.78 * hair)
    p.cubicTo(x(0.26), 429, x(0.36), 530 - hair, crown, 530 - hair)
    p.cubicTo(crown + 0.14 * span, 530 - hair, post, 397, post, 345)
    p.lineTo(post, 310)
    p.cubicTo(x(0.46), 302, l, 261, l, 140)
    p.cubicTo(l, 46, x(0.225), -10, floor, -10)
    p.cubicTo(x(0.55), -10, post - 0.07 * span, 22, post + 4, 65)
    p.lineTo(post + 8, 0)
    p.close()
    eye = pathops.Path()
    back = l + min(stem * 0.92, span * side_ratio)
    bottom = hair - 11
    # The eye has room to turn, even when the diagonal waist is shortest.
    eye.moveTo(post, 310 - 0.81 * hair)
    eye.cubicTo(x(0.52), 306 - 0.81 * hair, back, 195, back, 141)
    eye.cubicTo(back, 102, floor - 0.06 * span, bottom, floor + 0.02 * span, bottom)
    eye.cubicTo(x(0.55), bottom, post, 109, post, 152)
    eye.lineTo(post, 310 - 0.81 * hair)
    eye.close()
    return pathops.op(p, eye, pathops.PathOp.DIFFERENCE)


def single_a(l, r, stem, hair, side_ratio=0.245):
    span = r - l
    x = lambda f: l + f * span
    wall = r - 0.12 * span - stem
    post = wall + stem
    crown = x(0.405)
    floor = x(0.395)
    p = pathops.Path()
    p.moveTo(crown, 530)
    p.cubicTo(x(0.54), 530, wall - 3, 494, wall, 459)
    p.lineTo(wall, 520)
    p.lineTo(post, 520)
    p.lineTo(post, 153)
    p.cubicTo(post, 108, post + 4, 75, post + 0.34 * (r - post), 75)
    p.cubicTo(post + 0.58 * (r - post), 75, r - 6, 84, r - 4, 91)
    p.lineTo(r, 19)
    p.cubicTo(r - 17, 1, post + 3, -8, post - 14, -8)
    p.cubicTo(wall + 0.41 * stem, -8, wall + 6, 15, wall, 64)
    p.cubicTo(x(0.54), 11, x(0.47), -10, floor, -10)
    p.cubicTo(x(0.15), -10, l, 104, l, 259)
    p.cubicTo(l, 423, x(0.16), 530, crown, 530)
    p.close()
    eye = pathops.Path()
    side = l + min(stem * 0.92, span * side_ratio)
    eye.moveTo(wall, 351)
    eye.cubicTo(wall - 7, 401, x(0.50), 530 - hair, crown, 530 - hair)
    eye.cubicTo(x(0.30), 530 - hair, side, 379, side, 259)
    eye.cubicTo(side, 146, x(0.30), hair - 10, floor + 3, hair - 10)
    eye.cubicTo(x(0.51), hair - 10, wall - 10, 114, wall, 166)
    eye.close()
    return pathops.op(p, eye, pathops.PathOp.DIFFERENCE)


def sharp_s(l, r, stem, hair, capital):
    span = r - l
    x = lambda f: l + f * span
    left = l + stem
    top = 700 if capital else 744
    upper = r - 0.125 * span
    bend = 539 if capital else 570
    crown = x(0.53 if capital else 0.45)
    waist_y = 359 if capital else 379
    back = x(0.65)
    tip = left + 0.22 * (r - left)
    end = left + max(28, 0.095 * span)
    bottom = x(0.615)
    path = pathops.Path()
    path.moveTo(l, 0)
    if capital:
        path.lineTo(l, top)
        path.lineTo(crown, top)
    else:
        path.lineTo(l, 578)
        path.cubicTo(l, 681, x(0.18), top, crown, top)
    path.cubicTo(x(0.735), top, upper, top - 67, upper, bend)
    path.cubicTo(upper, bend - 80, x(0.76), waist_y + 46, back, waist_y)
    path.cubicTo(x(0.88), waist_y - 36, r, 292, r, 178)
    path.cubicTo(r, 62, x(0.845), -10, bottom, -10)
    path.cubicTo(x(0.50), -10, end + 19, 5, end, 17)
    path.lineTo(end + 0.15 * hair, 17 + hair)
    path.cubicTo(end + 31, 24 + hair, x(0.52), hair - 10, bottom, hair - 10)
    path.cubicTo(x(0.74), hair - 10, r - stem * 0.91, 109, r - stem * 0.91, 178)
    path.cubicTo(
        r - stem * 0.91, 267, x(0.65), waist_y - 0.71 * hair, tip, waist_y - 0.48 * hair
    )
    path.lineTo(tip, waist_y + 0.45 * hair)
    path.cubicTo(
        x(0.615),
        waist_y + 0.81 * hair,
        upper - stem * 0.88,
        bend - 75,
        upper - stem * 0.88,
        bend,
    )
    path.cubicTo(upper - stem * 0.88, bend + 59, x(0.59), top - hair, crown, top - hair)
    if capital:
        path.lineTo(left, top - hair)
    else:
        path.cubicTo(x(0.33), top - hair, left, 629, left, 578)
    path.lineTo(left, 0)
    path.close()
    return path


def draw(design, name, reference, width):
    lo, _, hi, _ = bounds(reference)
    scale, shift = design.transform(name, 900, width)
    center = scale * (lo + hi) / 2 + shift
    skinny = name in ("a", "ordfeminine")
    spans = (362, 450, 516) if skinny else (393, 470, 529)
    span = np.interp(width, (65, 100, 150), spans)
    stem = np.interp(width, (65, 100, 150), (111, 124, 128))
    hair = np.interp(width, (65, 100, 150), (81, 89, 93))
    l, r = center - span / 2, center + span / 2
    if name == "a":
        shape = (single_a if design.slant else double_a)(l, r, stem, hair * 1.14)
    elif name == "ordfeminine":
        shape = double_a(-span / 2, span / 2, stem * 1.08, hair * 1.12).transform(
            0.60, 0, 0, 0.486, center, 451
        )
        bar = pathops.Path()
        bar.moveTo(center - span * 0.30, 330)
        bar.lineTo(center + span * 0.30, 330)
        bar.lineTo(center + span * 0.30, 382)
        bar.lineTo(center - span * 0.30, 382)
        bar.close()
        shape.addPath(bar)
    else:
        shape = sharp_s(l, r, stem, hair, name == "Germandbls")
    shape.simplify(clockwise=True)
    pen = OutlinePen(None)
    shape.draw(pen)
    return ordered_contours(reference, pen.contours)
