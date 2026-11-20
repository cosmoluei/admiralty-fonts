"""Physical pen drawings for signs with continuous rails, mirrored arms or counters."""

import numpy as np
import pathops

import serif_brackets

from accent_masters import as_path
from compatible import Contour, OutlinePen, Profile, compatible_points, ordered_contours
from optical_curves import round_default
from serif_thin import ThinPen
from thin_figures import FIGURES, FRACTIONS, register_figure, thin_rings, width_station_map

ANGLES = {
    s + side + case
    for s in ("guilsingl", "guillemot")
    for side in ("left", "right")
    for case in ("", ".case")
}
ARROWS = {
    "arrowleft",
    "arrowright",
    "arrowup",
    "arrowdown",
    "arrowboth",
    "uni2195",
    "arrowupright",
    "arrowdownright",
    "uni2196",
    "uni2199",
    "arrowdblright",
    "arrowhookleft",
}
SIGNS = (
    ANGLES
    | ARROWS
    | {
        "plusminus",
        "summation",
        "product",
        "Omega",
        "ohm",
        "infinity",
        "notequal",
        "asciitilde",
        "ballotx",
        "registered",
        "copyright",
        "uni24B9",
        "AE",
        "OE",
        "perthousand",
        "percent",
        "Oslash",
        "oslash",
        "emptyset",
        "zero",
        "zero.tnum",
    }
)
NUMERALS = FIGURES.keys() | FRACTIONS.keys()


def outlined(path):
    pen = OutlinePen(None)
    path.draw(pen)
    return pen.contours


def to_path(rings):
    p = pathops.Path()
    for ring in rings:
        z = ring.pieces[0, 0]
        p.moveTo(z.real, z.imag)
        for _, a, b, c in ring.pieces:
            p.cubicTo(a.real, a.imag, b.real, b.imag, c.real, c.imag)
        p.close()
    return p


def fit_box(path, box):
    x0, y0, x1, y1 = path.bounds
    l, b, r, t = box
    sx, sy = (r - l) / (x1 - x0), (t - b) / (y1 - y0)
    return path.transform(sx, 0, 0, sy, l - sx * x0, b - sy * y0)


def figure_black(rings, sx, dx):
    # Add ink normal to the two sides of the released drawing. A single
    # offset around each complete curve keeps its extents and smooth joins.
    # Separately fitted fraction digits keep their baseline and clearance.
    native = to_path(rings).transform(sx, 0, 0, 1, dx, 0)
    l, b, r, t = native.bounds
    size = (t - b) / 710
    rx = max(4, 20 + 32 * (1 - sx)) * size
    ry = 16 * size
    for _ in range(8):
        nib = native.transform(1 / rx, 0, 0, 1 / ry, 0, 0)
        nib.stroke(2, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 2)
        nib.convertConicsToQuads(0.002)
        expanded = pathops.op(native, nib.transform(rx, 0, 0, ry, 0, 0), pathops.PathOp.UNION)
        result = outlined(fit_box(expanded, (l, b, r, t)))
        if len(result) == len(rings):
            return result
        rx *= 0.8
        ry *= 0.8
    raise ValueError("counter closed while fitting a numeral")


def black_numeral(name, reference, sx, dx):
    from bowl_drawings import black_digit

    def digit(rings, number):
        if number not in (3, 8):
            return figure_black(rings, sx, dx)
        l,b,r,t = to_path(rings).bounds
        return outlined(black_digit(number, (l*sx+dx,b,r*sx+dx,t)))
    if name not in FRACTIONS:
        return digit(reference, FIGURES.get(name))
    slash = max(reference, key=lambda ring: np.ptp(ring.pieces[:, 0].imag))
    high = [r for r in reference if r is not slash and r.center.imag > 285]
    low = [r for r in reference if r is not slash and r not in high]
    a,b = FRACTIONS[name]
    return digit(high,a) + digit(low,b) + figure_black([slash], sx, dx)


def aligned_rings(name, reference, rings):
    if name in ("registered", "copyright", "uni24B9"):
        # The enclosing circle, its counter and the nested letter have
        # nearly coincident centers. Each has a distinct nesting level.
        ranked = sorted(rings, key=lambda c: abs(c.area), reverse=True)
        indices = sorted(range(len(reference)), key=lambda i: abs(reference[i].area), reverse=True)
        assert len(ranked) == len(indices), name
        result = list(reference)
        for i, c in zip(indices, ranked):
            result[i] = c
        return result
    return ordered_contours(reference, rings)


class Nib:
    def __init__(self, box, t):
        l, b, r, top = box
        self.span = r - l
        self.height = top - b
        self.x = l
        self.y = b
        self.t = t
        self.pen = ThinPen(1)

    def point(self, x, y):
        return self.x + x * self.span, self.y + y * self.height

    def stroke(self, start, *pieces, ratio=1, aspect=1, closed=False):
        parts = [sum((self.point(x, y) for x, y in zip(part[::2], part[1::2])), ()) for part in pieces]
        self.pen.stroke(self.point(*start), *parts, width=self.t * ratio, aspect=aspect, closed=closed)

    def loop(self, cx, cy, rx, ry, ratio=1):
        k = 0.55228475
        self.stroke(
            (cx + rx, cy),
            (cx + rx, cy + k * ry, cx + k * rx, cy + ry, cx, cy + ry),
            (cx - k * rx, cy + ry, cx - rx, cy + k * ry, cx - rx, cy),
            (cx - rx, cy - k * ry, cx - k * rx, cy - ry, cx, cy - ry),
            (cx + k * rx, cy - ry, cx + rx, cy - k * ry, cx + rx, cy),
            ratio=ratio,
            closed=True,
        )


def arrow(g, name):
    left = name in ("arrowleft", "arrowboth", "arrowhookleft")
    other = name in ("arrowboth", "uni2195")
    if name in ("arrowupright", "arrowdownright", "uni2196", "uni2199"):
        flip_x = name in ("uni2196", "uni2199")
        flip_y = name in ("arrowdownright", "uni2199")

        def xy(x, y):
            return (1 - x if flip_x else x, 1 - y if flip_y else y)

        g.stroke(xy(0, 0), xy(1, 1))
        g.stroke(xy(0.35, 1), xy(1, 1), xy(1, 0.35))
    elif name == "arrowhookleft":
        g.stroke(
            (0.49, 1), (0.70, 1), (0.90, 1, 1, 0.87, 1, 0.69), (1, 0.51, 0.89, 0.35, 0.70, 0.35), (0.02, 0.35)
        )
        g.stroke((0.32, 0.70), (0.02, 0.35), (0.32, 0))
    else:
        vertical = name in ("arrowup", "arrowdown", "uni2195")

        def xy(x, y):
            if vertical:
                return y, 1 - x if name == "arrowdown" else x
            return 1 - x if left else x, y

        width = 0.40 if not other else 0.33
        levels = (0.32, 0.68) if name == "arrowdblright" else (0.5,)
        for y in levels:
            end = 1 - 2 * width * abs(y - 0.5)
            g.stroke(xy(0, y), xy(end, y))
        g.stroke(xy(1 - width, 0), xy(1, 0.5), xy(1 - width, 1))
        if other:
            g.stroke(xy(width, 0), xy(0, 0.5), xy(width, 1))


def sign(name, native, box, w, serif, mono):
    l, b, r, t = box
    weight = 23 if w == 100 else 110
    if name in ANGLES:
        # Each chevron has its own tip, even at the narrow end of the axis.
        double = name.startswith("guillemot")
        g = Nib(box, min(weight, (r - l) * (0.13 if double else 0.29)))
        for offset in [0, 0.48] if double else [0]:
            reach = 0.52 if double else 1
            start, end = offset + reach, offset
            if "right" in name:
                start, end = 1 - start, 1 - end
            g.stroke((start, 0), (end, 0.50), (start, 1))
    elif name in ARROWS:
        g = Nib(box, 121 if w == 900 and mono else weight * 0.86)
        arrow(g, name)
    elif name in ("registered", "copyright", "uni24B9"):
        # Work in the ring's own coordinate frame. In a circled D the outer
        # contour is a real circle, even in a wide font or an italic face.
        if name == "uni24B9":
            diameter = min(r - l, t - b)
            cx, cy = (r + l) / 2, (t + b) / 2
            box = (cx - diameter / 2, cy - diameter / 2, cx + diameter / 2, cy + diameter / 2)
        g = Nib(box, (19 if w == 100 else 68) * min(1, (box[2] - box[0]) / 470))
        g.loop(0.5, 0.5, 0.47, 0.47)
        if name == "copyright":
            g.stroke(
                (0.68, 0.654),
                (0.63, 0.735, 0.56, 0.765, 0.49, 0.765),
                (0.347, 0.765, 0.284, 0.648, 0.284, 0.505),
                (0.284, 0.352, 0.359, 0.238, 0.50, 0.238),
                (0.574, 0.238, 0.632, 0.268, 0.691, 0.352),
            )
        else:
            foot = 0.31 if name == "registered" else 0.32
            g.stroke(
                (foot, 0.255),
                (foot, 0.745),
                (0.50, 0.745),
                *(
                    (
                        [
                            (0.65, 0.745, 0.72, 0.65, 0.72, 0.503),
                            (0.72, 0.354, 0.635, 0.255, 0.49, 0.255),
                            (foot, 0.255),
                        ]
                    )
                    if name == "uni24B9"
                    else [
                        (0.626, 0.745, 0.673, 0.691, 0.673, 0.609),
                        (0.673, 0.526, 0.614, 0.467, 0.506, 0.467),
                        (foot, 0.467),
                    ]
                ),
                closed=name == "uni24B9",
            )
            if name == "registered":
                g.stroke((0.495, 0.467), (0.685, 0.255))
    elif name in ("percent", "perthousand"):
        # Reserve separate optical counters in the Mono cell. The slash
        # descends between groups, clear of all three rings in Black.
        three = name == "perthousand"
        unit = min((r - l) * (0.117 if three else 0.17), (t - b) * 0.18)
        g = Nib(box, min(weight * 0.70, unit * 0.71))
        rx, ry = unit / (r - l), 0.20
        for x, y in [(0.15, 0.77), (0.55, 0.24), (0.875, 0.24)] if three else [(0.21, 0.77), (0.79, 0.24)]:
            g.loop(x, y, rx, ry)
        g.stroke((0.12 if three else 0.16, 0.015), (0.59 if three else 0.84, 0.985), ratio=1.08)
    else:
        g = Nib(box, weight)
        s = g.stroke
        if name in ("Oslash", "oslash", "emptyset", "zero", "zero.tnum"):
            slashed = name in ("Oslash", "oslash", "emptyset")
            if not slashed and w == 900:
                g.t = 143
            g.loop(0.5, 0.5, 0.465, 0.418 if slashed else 0.48)
            if slashed:
                s((0.035, 0), (0.965, 1), ratio=0.79)
            else:
                radius = 18 if w == 100 else 42
                x, y = g.point(0.5, 0.5)
                p = pathops.Path()
                p.moveTo(x + radius, y)
                for vx, vy in ((0, 1), (-1, 0), (0, -1), (1, 0)):
                    px, py = vy, -vx
                    k = 0.55228475 * radius
                    p.cubicTo(
                        x + radius * px + k * vx,
                        y + radius * py + k * vy,
                        x + radius * vx + k * px,
                        y + radius * vy + k * py,
                        x + radius * vx,
                        y + radius * vy,
                    )
                p.close()
                g.pen.add(p)
        elif name in ("Omega", "ohm"):
            # The full foot length is part of Ω's skeleton in Thin.
            s(
                (0.015, 0.02),
                (0.32, 0.02),
                (0.24, 0.115, 0.063, 0.220, 0.063, 0.513),
                (0.063, 0.790, 0.236, 0.985, 0.5, 0.985),
                (0.764, 0.985, 0.937, 0.79, 0.937, 0.513),
                (0.937, 0.22, 0.76, 0.115, 0.68, 0.02),
                (0.985, 0.02),
                aspect=0.83,
            )
        elif name == "plusminus":
            s((0, 0.62), (1, 0.62))
            s((0.5, 0.255), (0.5, 0.99))
            s((0, 0.02), (1, 0.02))
        elif name == "summation":
            s((1, 0.985), (0.035, 0.985), (0.57, 0.51), (0.035, 0.015), (1, 0.015))
        elif name == "product":
            s((0, 0.985), (1, 0.985))
            for x in (0.17, 0.83):
                s((x, 0.985), (x, 0.015))
                if serif:
                    s((x - 0.13, 0.015), (x + 0.13, 0.015), ratio=0.76)
        elif name == "ballotx":
            s((0.02, 0.015), (0.98, 0.985))
            s((0.02, 0.985), (0.98, 0.015))
        elif name == "notequal":
            for y in (0.32, 0.68):
                s((0, y), (1, y))
            s((0.27, 0), (0.73, 1))
        elif name == "asciitilde":
            if w == 900:
                g.t = 126
            s(
                (0.015, 0.26),
                (0.095, 0.64, 0.20, 0.84, 0.316, 0.84),
                (0.46, 0.84, 0.55, 0.18, 0.70, 0.18),
                (0.817, 0.18, 0.912, 0.354, 0.984, 0.77),
            )
        elif name == "infinity":
            # The crossover is a single pen movement with symmetric entry
            # and exit tangents, keeping both counters open.
            g.t = min(weight, 0.17 * (r - l), 0.25 * (t - b))
            s(
                (0.50, 0.50),
                (0.40, 0.72, 0.36, 0.90, 0.24, 0.90),
                (0.103, 0.90, 0.027, 0.745, 0.027, 0.50),
                (0.027, 0.255, 0.103, 0.10, 0.24, 0.10),
                (0.36, 0.10, 0.40, 0.28, 0.50, 0.50),
                (0.60, 0.72, 0.64, 0.90, 0.76, 0.90),
                (0.897, 0.90, 0.973, 0.745, 0.973, 0.50),
                (0.973, 0.255, 0.897, 0.10, 0.76, 0.10),
                (0.64, 0.10, 0.60, 0.28, 0.50, 0.50),
                closed=True,
            )
        elif name in ("AE", "OE"):
            j = 0.54
            # Set the outer edges of the three rails on the spine edges.
            # Stopping each independent butt at its centre leaves a stair.
            stem = g.t / g.span
            rail = g.t * .84 / g.height
            jleft = j - stem / 2
            s((j, 0), (j, 1))
            s((jleft, 1-rail/2), (1, 1-rail/2), ratio=.84)
            s((j, .51), (.89, .51), ratio=.80)
            s((jleft, rail/2), (1, rail/2), ratio=.84)
            if name == "AE":
                g.pen.ribbon(g.point(.02,0),g.point(j-stem*.04,1),g.t)
                s((0.20, 0.37), (j, 0.37), ratio=0.80)
                if serif:
                    s((0, 0), (0.11, 0), ratio=0.60)
            else:
                s(
                    (j, 0.75),
                    (j, 0.864, 0.443, 0.994, 0.314, 0.994),
                    (0.112, 0.994, 0.024, 0.806, 0.024, 0.50),
                    (0.024, 0.194, 0.112, 0.006, 0.314, 0.006),
                    (0.443, 0.006, j, 0.136, j, 0.25),
                    aspect=0.76 if serif else 0.90,
                )
            if serif:
                for x, y, direction in [(1, 1, -1), (1, 0, 1), (0.89, 0.51, 1)]:
                    end = x - .30 * stem
                    start = y if y in (0,1) else y - direction * .40 * g.t/g.height
                    s((end, start), (end, y + .066 * direction), ratio=.60)
        else:
            raise KeyError(name)
    return outlined(fit_box(g.pen.shape, box))


def mono_perthousand_tracks(slant, cells):
    from reviewed_capitals import rounded

    # Eight quadratic arcs per ellipse. Odd points are intersections of the
    # neighboring tangents, so every master shares the extrema and tangents.
    angles = np.arange(16) * np.pi / 8
    circle = np.exp(1j * angles)
    circle[1::2] /= np.cos(np.pi / 8)
    rows = []
    for weight, width in cells:
        growth, wall, height = {100: (0, 18, 250), 400: (7, 43, 252), 900: (15, 60, 252)}[weight]
        span = np.interp(width, (65, 100, 150), (548, 564, 578)) + growth
        diameter = np.interp(width, (65, 100, 150), (180, 191, 199)) + .42 * growth
        left = (600 - span) / 2
        right = left + span
        gap = {100: 24, 400: 22, 900: 18}[weight]
        radius = diameter / 2
        centers = [(left + radius, 700 - height / 2),
                   (right - 3 * radius - gap, -10 + height / 2),
                   (right - radius, -10 + height / 2)]
        rings = []
        for x, y in centers:
            center = x + 1j * y
            rings.append(center + radius * circle.real - 1j * height / 2 * circle.imag)
            rings.append(center + (radius - wall) * circle.real
                         + 1j * (height / 2 - .90 * wall) * circle.imag)

        # Keep the diagonal between the two groups. Its caps share the ring
        # overshoots, while its measured thickness is normal to its slope.
        foot = left + max(.58 * wall, .042 * span)
        tip = left + .605 * span
        half = .5 * wall * np.hypot(1, (tip - foot) / 710)
        slash = np.array([foot - half - 10j, tip - half + 700j,
                          tip + half + 700j, foot + half - 10j])
        for fillet in (0, .32 * wall):
            outlines = [*rings, rounded(slash, fillet)]
            points = np.concatenate(outlines)
            rows.append(points + slant * (points.imag - 260))
    return rows, (np.cumsum([len(c) for c in outlines]) - 1).tolist()


def master_tracks(design, name, cells):
    import member_masters

    if design.mono and name == "perthousand":
        return mono_perthousand_tracks(design.slant, cells)

    native = as_path(design.regular.getGlyphSet(), name, (1, 0, -design.slant, 1, 0, 0))
    reference = outlined(native)
    box = native.bounds
    drawings = {}
    for w, d in cells:
        sx, dx = design.transform(name, w, d)
        if name == "infinity" and d == 65:
            # Preserve two horizontal loops inside the available advance.
            # In a condensed Mono cell, compressing only the horizontal
            # coordinates turns the crossing into two upright oval counters.
            l, b, r, t = box
            span = (r - l) * sx
            if design.mono:
                span = max(span, 490)
            center = (r + l) * sx / 2 + dx
            height = min(t - b, span / 1.77)
            mid = (t + b) / 2
            if w == 400:
                rings = [
                    Contour(
                        (c.pieces.real - (r + l) / 2) * span / (r - l)
                        + center
                        + 1j * ((c.pieces.imag - mid) * height / (t - b) + mid)
                    )
                    for c in reference
                ]
            else:
                rings = sign(
                    name,
                    native,
                    (center - span / 2, mid - height / 2, center + span / 2, mid + height / 2),
                    w,
                    design.serif,
                    design.mono,
                )
        elif name == "uni24B9" and w == 400:
            cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
            size = min(1.0, sx)
            rings = [
                Contour((c.pieces - complex(cx, cy)) * size + complex(cx * sx + dx, cy)) for c in reference
            ]
        elif w == 400:
            rings = [Contour(c.pieces.real * sx + dx + 1j * c.pieces.imag) for c in reference]
            if design.mono and name == "IJ" and d != 100:
                left, right = sorted(range(len(rings)), key=lambda i: rings[i].center.real)
                separation = max(0, 25 + rings[left].pieces.real.max() - rings[right].pieces.real.min())
                rings[left] = Contour(rings[left].pieces - separation / 2)
                rings[right] = Contour(rings[right].pieces + separation / 2)
        elif member_masters.handles(design, name):
            rings = outlined(member_masters.draw(design, name, native, w, d))
        elif name == "AE" and design.mono and w == 900:
            # Reserve width for the A before thickening the E. The triangle's
            # left edge continues the inner diagonal below the crossbar.
            l, b, r, t = box
            l, r = l*sx+dx, r*sx+dx
            width = r-l
            def x(u):
                return l+width*u
            foot, slope, spine = .19, .48/700, .53
            low, high = 175, 262
            apex = (spine-.008-foot)/slope
            outlines = [
                [(0,0),(.48,700),(1,700),(1,607),(.75,607),(.75,409),
                 (.945,409),(.945,317),(.75,317),(.75,93),(1,93),(1,0),
                 (spine,0),(spine,low),(foot+slope*low,low),(foot,0)],
                [(foot+slope*high,high),(spine,high),(spine,apex),(spine-.008,apex)]]
            shape = pathops.Path()
            for contour in outlines:
                shape.moveTo(x(contour[0][0]),contour[0][1])
                for u,y in contour[1:]:
                    shape.lineTo(x(u),y)
                shape.close()
            rings = outlined(shape)
        elif w == 900 and (
            name in ANGLES | {"AE", "OE", "percent"} or name in {"uni2196", "uni2199"} and not design.mono
        ):
            rings = figure_black(reference, sx, dx)
        elif name in NUMERALS:
            rings = (
                thin_rings(name, reference, sx, dx, design.serif, design.mono, bool(design.slant))
                if w == 100
                else black_numeral(name, reference, sx, dx)
            )
        else:
            l, b, r, t = box
            if (name == "asciitilde" or name in ARROWS) and w == 900 and design.mono:
                sx, dx = design.transform(name, 400, d)
            rings = sign(name, native, (l * sx + dx, b, r * sx + dx, t), w, design.serif, design.mono)
        drawings[w, d] = aligned_rings(name, reference, rings)
    rows = [[] for _ in range(2 * len(cells))]
    ends = []
    for i, ref in enumerate(reference):
        profiles = []
        nominal = {w: register_figure(ref, drawings[w, 100][i]) for w in (100, 900)}
        for w, d in cells:
            ring = drawings[w, d][i]
            if w == 100 and name == "F" and design.serif and design.slant:
                ring, a, b = serif_brackets.italic_f(ref, *design.transform(name, w, d))
            elif w == 100 and name == "uni20AD" and design.serif and not design.slant:
                ring, a, b = serif_brackets.kip(ref, ring)
            elif w == 400:
                a, b = ref.knots, ring.knots
            else:
                source, a, b = nominal[w]
                if d == 100:
                    ring = source
                else:
                    ring, c, e = width_station_map(source, ring)
                    stations = np.unique(np.r_[b, c])
                    a, b = np.interp(stations, b, a), np.interp(stations, c, e)
            radius = {100: 8, 400: 28, 900: 43}[w]
            if w==900 and name in NUMERALS and (FIGURES.get(name) in (3,8) or
                    any(n in (3,8) for n in FRACTIONS.get(name,()))):
                # A fraction's joins have a much smaller optical radius than
                # a capital's. Retain the waist between the two bowls.
                radius=min(radius, .041*np.ptp(ring.pieces.imag))
            for fillet in (0, radius):
                profiles.append(Profile(ring, a, b, fillet))
        for irow, (row, z) in enumerate(zip(rows, compatible_points(profiles, 0.17, compact=0.16))):
            z = z + design.slant * z.imag
            row.extend(round_default(z, ref.area) if irow == 0 else z)
        ends.append(len(rows[0]) - 1)
    return list(map(np.asarray, rows)), ends
