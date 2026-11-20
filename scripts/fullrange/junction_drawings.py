"""Thin strokes whose two sides must continue through a crossing or a terminal."""

import pathops
import numpy as np

from fontTools.misc.bezierTools import splitCubic
from fontTools.pens.transformPen import TransformPen

from compatible import OutlinePen, Profile, compatible_points, ordered_contours
from thin_figures import Drawing, bounds
from thin_figures import register_figure, width_station_map

CURRENCIES = {
    "rupee",
    "ruble",
    "uni20A1",
    "uni20A6",
    "uni20AD",
    "uni20AE",
    "uni20B1",
    "uni20B4",
    "uni20B5",
    "uni20BA",
    "uni20AA",
    "uni20B8",
}
OTHER = {
    "Lslash",
    "lslash",
    "ampersand",
    "ordfeminine",
    "ordmasculine",
    "Germandbls",
    "germandbls",
}
NAMES = (CURRENCIES - {"uni20BA"}) | OTHER


def thin(name, reference, sx, dx, serif, mono, italic):
    box = bounds(reference)
    if name in ("ordfeminine", "ordmasculine"):
        # The underline is an independent contour. Its distance from the
        # baseline and the x-height of the miniature come from the typeface.
        body = [
            r for r in reference if r is not min(reference, key=lambda c: c.center.imag)
        ]
        l, b, r, t = bounds(body)
        l, r = l * sx + dx, r * sx + dx
        if name == "ordfeminine":
            g = Drawing((l, b, r, t), (0, 0, 400, 520), 1, 0, serif)
            g.thickness = 17
            g.stroke(
                (45, 447),
                (83, 491, 132, 506, 193, 506),
                (275, 506, 355, 455, 355, 343),
                (355, 9),
            )
            g.stroke(
                (355, 295),
                (212, 285, 31, 246, 31, 143),
                (31, 69, 94, 14, 174, 14),
                (255, 14, 355, 92, 355, 175),
            )
            result = g.pen.rings()
        else:
            g = Drawing((l, b, r, t), (0, 0, 600, 520), 1, 0, serif)
            g.thickness = 17
            oval(g, 300, 260, 270, 246)
            result = g.pen.rings()
        bar = min(reference, key=lambda c: c.center.imag)
        left, bot, right, top = bounds([bar])
        line = Drawing(
            (left * sx + dx, bot, right * sx + dx, top), (0, 0, 1, 1), 1, 0, serif
        )
        line.thickness = 16
        line.stroke((0, 0.50), (1, 0.50), aspect=1)
        return result + line.pen.rings()

    if name in ("Germandbls", "germandbls"):
        cap = name == "Germandbls"
        top = 700 if cap else 744
        g = Drawing(box, (0, -10, 600, top), sx, dx, serif)
        g.thickness = 24
        stem = 17
        if cap:
            g.stroke(
                (stem, 0),
                (stem, top - 11),
                (280, top - 11),
                (413, top - 11, 481, 625, 481, 546),
                (481, 465, 412, 384, 242, 363),
            )
        else:
            g.stroke(
                (stem, 0),
                (stem, 552),
                (stem, 666, 113, top - 11, 245, top - 11),
                (388, top - 11, 477, 645, 477, 554),
                (477, 474, 407, 400, 242, 375),
            )
        waist = 363 if cap else 375
        g.stroke(
            (242, waist),
            (403, waist, 567, 310, 567, 178),
            (567, 72, 463, 1, 327, 1),
            (246, 1, 177, 21, 132, 51),
        )
        return g.pen.rings()
    lo, hi = (0, 700)
    if name in ("uni20A1", "uni20B5"):
        lo, hi = -110, 810
    if name == "lslash":
        lo, hi = -10, 740
    g = Drawing(box, (0, lo, 600, hi), sx, dx, serif)
    g.thickness = 24
    s = g.stroke

    def bar(x, y, xx):
        s((x, y), (xx, y), width=0.78 if serif else 0.9, aspect=1)

    def upright(x, y, t):
        s((x, y), (x, t), aspect=1)

    def serif_at(x, y, top=False):
        if serif:
            px, py = g.xy(x, y)
            g.pen.serif(px, py, 12, top=top)

    if name in ("ruble", "uni20B1"):
        stem = 112
        y = 328 if name == "ruble" else 342
        upright(stem, 0, 689+g.thickness*g.aspect/(2*g.sy))
        serif_at(stem, 0)
        s(
            (stem, 689),
            (297, 689),
            (435, 689, 524, 621, 524, 520),
            (524, 406, 436, y, 306, y),
            (stem, y),
        )
        if name == "ruble":
            bar(7, y, 308)
            bar(7, 207, 373)
        else:
            bar(6, 443, 596)
            bar(6, 551, 596)
    elif name == "rupee":
        bar(8, 689, 592)
        bar(8, 529, 592)
        s(
            (108, 689),
            (146, 689),
            (311, 689, 388, 618, 388, 534),
            (388, 418, 291, 323, 99, 323),
            (548, 7),
            aspect=.78 if serif else .90,
        )
    elif name in ("uni20A1", "uni20B5"):
        s(
            (555, 574),
            (506, 651, 445, 699, 340, 699),
            (167, 699, 46, 552, 46, 350),
            (46, 148, 164, 1, 340, 1),
            (435, 1, 510, 48, 556, 122),
        )
        if name == "uni20B5":
            upright(302, -110, 810)
        else:
            for x in (226, 365):
                s((x - 65, -108), (x + 65, 808), width=0.84, aspect=1)
    elif name == "uni20A6":
        for x in (112, 491):
            upright(x, 0, 700)
            serif_at(x, 0)
            serif_at(x, 700, True)
        s((112, 694), (491, 6), aspect=1)
        for y in (252, 434):
            bar(4, y, 596)
    elif name in ("uni20AE", "Lslash", "lslash"):
        stem = 300 if name == "uni20AE" else 255 if name == "lslash" else 198
        if name == "lslash":
            if italic:
                s(
                    (stem, 731),
                    (stem, 104),
                    (stem, 41, stem + 21, 0, stem + 64, 0),
                    (stem + 99, 0, stem + 127, 25, stem + 147, 57),
                )
            else:
                upright(stem, 0, 731)
                if mono:
                    bar(62, 10, 536)
                else:
                    serif_at(stem, 0)
            if serif:
                g.pen.entry(*g.xy(stem, 740))
            elif mono:
                bar(92, 731, stem)
        elif name == "uni20AE":
            upright(stem, 0, 690)
            bar(8, 690, 592)
            serif_at(stem, 0)
        else:
            s((stem, 700), (stem, 10), (587, 10))
            serif_at(stem, 700, True)
        if name in ("Lslash", "lslash"):
            s((15, 286), (505 if name == "lslash" else 469, 451), width=0.82, aspect=1)
        else:
            for y in (231, 378):
                s((15, y - 59), (stem + 156, y + 58), width=0.82, aspect=1)
    elif name == "uni20AD":
        upright(112, 0, 700)
        serif_at(112, 0)
        serif_at(112, 700, True)
        root = 344 if not serif else 263
        s((112, root), (504, 695), width=0.85)
        branch = (344 - root) / (695 - root)
        s((112 + branch * (504 - 112), root + branch * (695 - root)), (535, 6))
        bar(6, 344, 585)
    elif name == "uni20B4":
        s(
            (111, 600),
            (154, 659, 222, 697, 305, 697),
            (416, 697, 494, 628, 494, 535),
            (494, 448, 439, 406, 305, 351),
            (175, 298, 98, 253, 98, 159),
            (98, 62, 176, 2, 290, 2),
            (378, 2, 461, 44, 512, 111),
        )
        for y in (266, 421):
            bar(6, y, 594)
    elif name == "uni20AA":
        s((34, 0), (34, 606), (401, 606), (401, 243))
        s((566, 615), (566, 12), (197, 12), (197, 363))
    elif name == "uni20B8":
        upright(300, 0, 542)
        serif_at(300, 0)
        bar(12, 542, 588)
        bar(12, 688, 588)
    elif name == "ampersand":
        # The diagonal ends with one cut perpendicular to its path. Both
        # crossings are unions of whole strokes, including the returning arm.
        s(
            (567, 6),
            (207, 438),
            (141, 514, 144, 573, 171, 623),
            (196, 672, 247, 694, 307, 694),
            (393, 694, 447, 642, 446, 572),
            (445, 472, 344, 426, 235, 362),
            (105, 286, 48, 226, 54, 145),
            (58, 53, 130, 1, 235, 1),
            (374, 1, 492, 119, 560, 316),
            aspect=1,
        )
    else:
        raise KeyError(name)
    return g.pen.rings()


def oval(g, cx, cy, rx, ry):
    k = 0.552285
    g.stroke(
        (cx, cy - ry),
        (cx + k * rx, cy - ry, cx + rx, cy - k * ry, cx + rx, cy),
        (cx + rx, cy + k * ry, cx + k * rx, cy + ry, cx, cy + ry),
        (cx - k * rx, cy + ry, cx - rx, cy + k * ry, cx - rx, cy),
        (cx - rx, cy - k * ry, cx - k * rx, cy - ry, cx, cy - ry),
        closed=True,
    )


def joined_rings(left, right, stem, hair, rising, round_left=False):
    """A shared e bowl joins either a double-storey a or a closed o."""
    span = right - left
    j = left + span * 0.50
    wall = j - stem / 2
    back = j + stem / 2
    ac = left + 0.27 * span
    ec = left + 0.753 * span
    floor = left + 0.242 * span
    xb = left + min(0.92 * stem, 0.18 * span)
    xr = right - min(0.9 * stem, 0.18 * span)
    leftbar, rightbar = (231, 281) if rising else (249, 249)
    cap = left + 0.071 * span
    p = pathops.Path()
    if round_left:
        p.moveTo(j, 422)
    else:
        p.moveTo(cap, 461)
        p.cubicTo(left + 0.122 * span, 503, left + 0.195 * span, 530, ac, 530)
        p.cubicTo(left + 0.381 * span, 530, j - 0.041 * span, 491, j, 422)
    p.cubicTo(j + 0.045 * span, 493, ec - 0.115 * span, 530, ec, 530)
    p.cubicTo(right - 0.10 * span, 530, right, 431, right, rightbar)
    p.lineTo(back, leftbar)
    p.cubicTo(back + 1, 139, ec - 0.10 * span, hair - 10, ec + 2, hair - 10)
    p.cubicTo(
        ec + 0.083 * span,
        hair - 10,
        right - 0.077 * span,
        75,
        right - 0.038 * span,
        119,
    )
    p.lineTo(right, 119 - 0.57 * hair)
    p.cubicTo(right - 0.042 * span, 35, ec + 0.087 * span, -10, ec, -10)
    p.cubicTo(ec - 0.113 * span, -10, j + 0.034 * span, 29, j, 82)
    if round_left:
        p.cubicTo(j - 0.043 * span, 24, ac + 0.079 * span, -10, ac, -10)
        p.cubicTo(left + 0.103 * span, -10, left, 91, left, 260)
        p.cubicTo(left, 419, left + 0.095 * span, 530, ac, 530)
        p.cubicTo(ac + 0.095 * span, 530, j - 0.043 * span, 494, j, 422)
        p.close()
        p.moveTo(wall, 312)
        p.cubicTo(wall, 402, ac + 0.052 * span, 530 - hair, ac, 530 - hair)
        p.cubicTo(ac - 0.084 * span, 530 - hair, xb, 377, xb, 260)
        p.cubicTo(xb, 147, ac - 0.071 * span, hair - 10, ac, hair - 10)
        p.cubicTo(ac + 0.088 * span, hair - 10, wall, 130, wall, 196)
        p.close()
    else:
        p.cubicTo(j - 0.052 * span, 23, floor + 0.085 * span, -10, floor, -10)
        p.cubicTo(left + 0.106 * span, -10, left, 49, left, 139)
        p.cubicTo(left, 249, left + 0.211 * span, 292, wall, 311)
        p.lineTo(wall, 348)
        p.cubicTo(wall, 423, ac + 0.078 * span, 530 - hair, ac, 530 - hair)
        p.cubicTo(
            ac - 0.065 * span,
            530 - hair,
            left + 0.142 * span,
            478 - 0.71 * hair,
            cap + 0.021 * span,
            461 - 0.79 * hair,
        )
        p.close()
        p.moveTo(wall, 311 - 0.86 * hair)
        p.cubicTo(left + 0.229 * span, 286 - 0.86 * hair, xb, 218, xb, 145)
        p.cubicTo(xb, 99, floor - 0.046 * span, hair - 10, floor + 1, hair - 10)
        p.cubicTo(floor + 0.096 * span, hair - 10, wall, 125, wall, 170)
        p.close()
    p.moveTo(back, leftbar + hair * 0.85)
    p.lineTo(xr, rightbar + hair * 0.85)
    p.cubicTo(xr, 416, ec + 0.069 * span, 530 - hair, ec, 530 - hair)
    p.cubicTo(ec - 0.09 * span, 530 - hair, back + 3, 404, back, leftbar + hair * 0.85)
    p.close()
    pen = OutlinePen(None)
    p.draw(pen)
    return pen.contours


def light_join(l, r, serif, rising, round_left=False):
    g = Drawing((l, -10, r, 530), (0, -10, 1000, 530), 1, 0, serif)
    g.thickness = 24
    j = 495
    b0, b1 = (236, 289) if rising else (258, 258)
    g.stroke(
        (948, 106),
        (901, 40, 840, 0, 760, 0),
        (601, 0, j, 80, j, 178),
        (j, 329),
        (j, 435, 606, 520, 753, 520),
        (898, 520, 974, 424, 974, b1),
        (j, b0),
    )
    if round_left:
        g.stroke(
            (j, 317),
            (483, 430, 393, 520, 258, 520),
            (100, 520, 26, 398, 26, 259),
            (26, 113, 105, 0, 255, 0),
            (393, 0, 482, 85, j, 180),
        )
    else:
        g.stroke(
            (73, 451),
            (114, 494, 177, 520, 259, 520),
            (383, 520, j, 443, j, 340),
            (j, 317),
        )
        g.stroke(
            (j, 302),
            (331, 295, 24, 259, 24, 143),
            (24, 57, 122, 0, 245, 0),
            (373, 0, j, 82, j, 174),
        )
    return g.pen.rings()


def ae_shape(glyphs, mono, serif, slant, weight, width, sx, dx, name="ae"):
    # Keep layout and original sidebearings; italic pen coordinates are
    # anchored in the upright frame before the final shear.
    p = OutlinePen(None)

    glyphs[name].draw(TransformPen(p, (1, 0, -slant, 1, 0, 0)))
    l, _, r, _ = bounds(p.contours)
    l, r = l * sx + dx, r * sx + dx
    if mono:
        span = np.interp(width, (65, 100, 150), (455, 511, 562))
        mid = (r + l) / 2
        l, r = mid - span / 2, mid + span / 2
    stem = {100: 24, 400: 74 if mono else 85, 900: 100 if mono else 124}[weight]
    hair = {
        100: 18 if serif else 22,
        400: 53 if serif else 65,
        900: 77 if serif else 89,
    }[weight]
    if weight == 100:
        return light_join(l, r, serif, slant and serif, round_left=name == "oe")
    return joined_rings(l, r, stem, hair, slant and serif, round_left=name == "oe")


def ae_master(design, weight, width, name="ae"):
    sx, dx = design.transform(name, weight, width)
    return ae_shape(
        design.regular.getGlyphSet(),
        design.mono,
        design.serif,
        design.slant,
        weight,
        width,
        sx,
        dx,
        name,
    )


def lira_shape(glyphs, mono, serif, slant, weight, width, sx, dx):
    """Two through-slashes and a rising quarter-bowl, on one continuous outline."""
    ref = OutlinePen(None)
    glyphs["uni20BA"].draw(TransformPen(ref, (1, 0, -slant, 1, 0, 0)))
    left, _, right, _ = bounds(ref.contours)
    left, right = left * sx + dx, right * sx + dx
    span = right - left
    stem = min({100: 24, 400: 82, 900: 116 if mono else 137}[weight], 0.235 * span)
    hair = stem * (0.76 if serif else 0.90)
    middle = left + 0.34 * span
    outer, inner = middle - stem / 2, middle + stem / 2
    end = left + 0.645 * span
    slope = 117 / (end - left)
    half = hair * 0.46 * np.hypot(1, slope)

    def bar(x, y, side):
        return x, y + slope * (x - left) + side * half

    p = pathops.Path()
    p.moveTo(outer, 0)
    # Concentric quarter-ellipses share their tangent directions. Start the
    # inside curve where it actually meets the stem's right edge.
    k = 0.55228475
    height = 292
    rx = right - outer
    p.cubicTo(outer + k * rx, 0, right, height * (1 - k), right, height)
    p.lineTo(right - stem, height)
    shoulder = splitCubic(
        (right - stem, height),
        (right - stem, height - k * (height - hair)),
        (outer + k * (rx - stem), hair),
        (outer, hair),
        inner,
        False,
    )[0]
    p.cubicTo(*shoulder[1], *shoulder[2], *shoulder[3])
    for y in (172, 319):
        for x, side in ((inner, -1), (end, -1), (end, 1), (inner, 1)):
            p.lineTo(*bar(x, y, side))
    if serif:
        bracket = 0.4 * stem
        p.lineTo(inner, 700 - 0.8 * stem)
        p.quadTo(inner, 700 - 0.27 * stem, inner + bracket, 700 - 0.27 * stem)
        p.lineTo(inner + bracket, 700)
        p.lineTo(outer - bracket, 700)
        p.lineTo(outer - bracket, 700 - 0.27 * stem)
        p.quadTo(outer, 700 - 0.27 * stem, outer, 700 - 0.8 * stem)
    else:
        p.lineTo(inner, 700)
        p.lineTo(outer, 700)
    for y in (319, 172):
        for x, side in ((outer, 1), (left, 1), (left, -1), (outer, -1)):
            p.lineTo(*bar(x, y, side))
    p.close()
    pen = OutlinePen(None)
    p.draw(pen)
    return pen.contours


def lira_tracks(design, name, cells):
    profiles = []
    for w, d in cells:
        sx, dx = design.transform(name, w, d)
        (ring,) = lira_shape(
            design.regular.getGlyphSet(),
            design.mono,
            design.serif,
            design.slant,
            w,
            d,
            sx,
            dx,
        )
        if not profiles:
            native = ring.knots
        for rad in (0, {100: 3, 400: 8, 900: 12}[w]):
            profiles.append(Profile(ring, native, ring.knots, rad))
    curves = [
        z + design.slant * z.imag
        for z in compatible_points(profiles, 0.12, compact=0.12)
    ]
    return curves, [len(curves[0]) - 1]


def revised_default(release, family, name):
    """The explicit new default design, in the same frame as the packaged glyph."""
    slant = np.tan(np.deg2rad(9.5)) if family.endswith("-Italic") else 0.0
    drawing = {"ae": ae_shape, "oe": ae_shape, "uni20BA": lira_shape}[name]
    rings = drawing(
        release.getGlyphSet(),
        "Mono" in family,
        "Serif" in family,
        slant,
        400,
        100,
        1,
        0,
        **({"name": name} if name in ("ae", "oe") else {}),
    )
    path = pathops.Path()
    for ring in rings:
        start = ring.pieces[0, 0]
        path.moveTo(start.real, start.imag)
        for _, a, b, c in ring.pieces:
            path.cubicTo(a.real, a.imag, b.real, b.imag, c.real, c.imag)
        path.close()
    return path.transform(1, 0, slant, 1, 0, 0)


def ae_tracks(design, name, cells):
    source = ae_master(design, 400, 100, name)
    profiles = [[] for c in source]
    nominal = ordered_contours(source, ae_master(design, 100, 100, name))
    anchors = [register_figure(ref, ring) for ref, ring in zip(source, nominal)]
    for w, d in cells:
        rings = ae_master(design, w, d, name)
        if w == 100:
            rings = ordered_contours(source, rings)
        for i, (group, ref, ring) in enumerate(zip(profiles, source, rings)):
            if w == 100:
                ring0, a, b = anchors[i]
                if d == 100:
                    ring = ring0
                else:
                    ring, src, dst = width_station_map(ring0, ring)
                    stations = np.unique(np.r_[b, src])
                    a, b = np.interp(stations, b, a), np.interp(stations, src, dst)
            else:
                a, b = ref.knots, ring.knots
            for radius in (0, {100: 3, 400: 8, 900: 12}[w]):
                group.append(Profile(ring, a, b, radius))
    rows = [[] for i in range(2 * len(cells))]
    ends = []
    for group in profiles:
        for row, z in zip(rows, compatible_points(group, 0.15, compact=0.16)):
            row.extend(z + design.slant * z.imag)
        ends.append(len(rows[0]) - 1)
    return list(map(np.asarray, rows)), ends
