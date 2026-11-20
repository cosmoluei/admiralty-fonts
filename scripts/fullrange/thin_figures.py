"""Thin figures and crossed signs, drawn around the stations of the Regular."""

import numpy as np
import pathops

from compatible import Contour, Profile, compatible_points, ordered_contours
from serif_thin import ThinPen

DIGITS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
FIGURES = {s: i for i in range(1, 10) for s in (DIGITS[i], DIGITS[i] + ".tnum")}
FIGURES.update(
    {
        n: i
        for i in range(1, 10)
        for n in ({1: "onesuperior", 2: "twosuperior", 3: "threesuperior"}.get(i, f"uni207{i}"), f"uni208{i}")
    }
)
FRACTIONS = {
    "onehalf": (1, 2),
    "onequarter": (1, 4),
    "threequarters": (3, 4),
    "uni2153": (1, 3),
    "uni2154": (2, 3),
}
SIGNS = {"numbersign", "emptyset", "Oslash", "oslash", "won", "uni20BC", "uni20BE", "sterling", "euro"}
SIGNS |= {"currency", "approxequal", "braceleft", "braceright", "braceleft.case", "braceright.case"}
NAMES = FIGURES.keys() | FRACTIONS.keys() | SIGNS
MONO_LETTERS = {"f"}
SANS_CAPS = {"J", "K", "Q", "R"}
FILLED = {
    "filledbox",
    "uni25AA",
    "triagup",
    "uni25B4",
    "uni25B6",
    "uni25B8",
    "triagdn",
    "uni25BE",
    "uni25C0",
    "uni25C2",
    "uni25C6",
    "uni25CF",
}


def bounds(rings):
    z = np.concatenate([c.pieces[:, 0] for c in rings])
    return z.real.min(), z.imag.min(), z.real.max(), z.imag.max()


class Drawing:
    """Map the skeleton into the component's own box before applying the nib."""

    def __init__(self, box, frame, width, shift, serif):
        x0, y0, x1, y1 = frame
        l, b, r, t = box
        self.sx = (r - l) / (x1 - x0) * width
        self.sy = (t - b) / (y1 - y0)
        self.x = l * width + shift - x0 * self.sx
        self.y = b - y0 * self.sy
        self.pen = ThinPen(1)
        self.aspect = 0.75 if serif else 0.91
        self.thickness = 24 * self.sy**0.65

    def xy(self, x, y):
        return self.x + x * self.sx, self.y + y * self.sy

    def stroke(self, start, *parts, width=1, aspect=None, closed=False):
        segments = [sum((self.xy(*s[i : i + 2]) for i in range(0, len(s), 2)), ()) for s in parts]
        self.pen.stroke(
            self.xy(*start),
            *segments,
            width=width * self.thickness,
            aspect=self.aspect if aspect is None else aspect,
            closed=closed,
        )

    def foot(self, x, y, reach):
        # A shallow bracket on each side and a level resting surface.
        t = self.thickness
        side = t * 0.5
        cx, cy = self.xy(x, y)
        pad = reach * self.sx
        p = pathops.Path()
        p.moveTo(cx - pad, cy)
        p.lineTo(cx + pad, cy)
        p.lineTo(cx + pad, cy + 0.39 * t)
        p.cubicTo(cx + 0.63 * t, cy + 0.39 * t, cx + side, cy + 0.58 * t, cx + side, cy + 1.2 * t)
        p.lineTo(cx - side, cy + 1.2 * t)
        p.cubicTo(cx - side, cy + 0.58 * t, cx - 0.63 * t, cy + 0.39 * t, cx - pad, cy + 0.39 * t)
        p.close()
        self.pen.add(p)


def numeral(n, box, sx, dx, serif):
    # Preserve each component's original size, alignment and italic pivot,
    # including the more tightly fitted digit boxes in the Mono fractions.
    frames = {
        1: (48, 0, 370, 690),
        2: (44, 0, 500, 700),
        3: (40, -10, 502, 700),
        4: (33, 0, 533, 690),
        5: (44, -10, 502, 695),
        6: (50, -10, 514, 700),
        7: (45, 0, 487, 690),
        8: (52, -10, 512, 700),
        9: (48, -10, 508, 700),
    }
    g = Drawing(box, frames[n], sx, dx, serif)
    s = g.stroke
    if n == 1:
        s((79, 559), (223, 678), (224, 678), (224, 0))
        if serif:
            g.foot(224, 0, 110)
        else:
            s((72, 12), (365, 12))
    elif n == 2:
        s(
            (79, 565),
            (123, 648, 187, 689, 267, 689),
            (371, 689, 438, 622, 438, 514),
            (438, 378, 280, 243, 68, 12),
            (486, 12),
        )
        if serif:
            s((486, 12), (490, 77), width=0.8)
    elif n == 3:
        waist = 370 if serif else 364
        # Both lobes leave the shared return horizontally. The small flat
        # on the left belongs to the drawing even in the smallest fraction.
        s(
            (83, 577),
            (128, 645, 190, 690, 265, 690),
            (365, 690, 436, 625, 436, 528),
            (436, 431, 367, waist, 251, waist),
            (192, waist),
        )
        s(
            (192, waist),
            (251, waist),
            (374, waist, 456, 300, 456, 191),
            (456, 83, 377, 0, 263, 0),
            (181, 0, 114, 39, 68, 112),
        )
    elif n == 4:
        bar = 201 if serif else 209
        # A single joined corner gives the diagonal a continuous edge to
        # the crossbar. The vertical rises to the flat top of the figure.
        s((394, 681), (52, bar), (532, bar), width=0.85 if serif else 1)
        s((394, 690), (394, 0))
        if serif:
            g.foot(394, 0, 61)
    elif n == 5:
        s(
            (474, 679),
            (139, 679),
            (120, 363),
            (169, 392, 214, 412, 271, 412),
            (379, 412, 456, 337, 456, 217),
            (456, 94, 376, 0, 260, 0),
            (177, 0, 116, 43, 72, 108),
        )
    elif n in (6, 9):

        def point(x, y):
            return (560 - x, 690 - y) if n == 9 else (x, y)

        def part(*values):
            return sum((point(x, y) for x, y in zip(values[::2], values[1::2])), ())

        s(
            point(480, 620),
            part(440, 662, 391, 690, 338, 690),
            part(185, 690, 99, 523, 99, 309),
            part(99, 119, 164, 0, 290, 0),
            part(402, 0, 467, 96, 467, 220),
            part(467, 329, 397, 412, 294, 412),
            part(204, 412, 137, 361, 100, 270),
        )
    elif n == 7:
        s((47, 678), (466, 678), (196, 0))
        if serif:
            s((47, 678), (44, 602), width=0.78)
    else:
        # Draw through the waist. Two ellipses tangent to the same horizontal
        # leave a flat bar at their overlap, especially at wide settings.
        s((282,356),(362,384,448,432,448,522),(448,618,381,690,282,690),
          (183,690,116,618,116,522),(116,432,202,384,282,356),
          (372,324,469,277,469,181),(469,78,394,0,282,0),
          (170,0,95,78,95,181),(95,277,192,324,282,356),closed=True)
    return g.pen.rings()


def signs(name, rings, sx, dx, serif, mono):
    box = bounds(rings)
    if name == "currency":
        g = Drawing(box, (86, 86, 494, 494), sx, dx, serif)
        radius = 128
        k = 0.552285 * radius
        g.stroke(
            (290, 290 - radius),
            (290 + k, 290 - radius, 290 + radius, 290 - k, 290 + radius, 290),
            (290 + radius, 290 + k, 290 + k, 290 + radius, 290, 290 + radius),
            (290 - k, 290 + radius, 290 - radius, 290 + k, 290 - radius, 290),
            (290 - radius, 290 - k, 290 - k, 290 - radius, 290, 290 - radius),
            closed=True,
        )
        for ix in (-1, 1):
            for iy in (-1, 1):
                g.stroke(
                    (290 + ix * 0.7071 * radius, 290 + iy * 0.7071 * radius),
                    (290 + ix * 183, 290 + iy * 183),
                    width=0.88,
                    aspect=1,
                )
    elif name == "approxequal":
        g = Drawing(box, (34, 50, 522, 400), sx, dx, serif)
        for offset in (0, 180):
            g.stroke(
                (65, 99 + offset),
                (87, 158 + offset, 114, 185 + offset, 157, 185 + offset),
                (234, 185 + offset, 301, 85 + offset, 384, 85 + offset),
                (429, 85 + offset, 466, 119 + offset, 491, 182 + offset),
                width=0.90,
                aspect=1,
            )
    elif name.startswith("brace"):
        g = Drawing(box, (0, -132, 1, 740), sx, dx, serif)
        # The tip remains a horizontal cut. Each arm runs level before
        # entering its curved shoulder and returns to a true central cusp.
        mirror = lambda x: 1 - x if name.startswith("braceright") else x

        def part(*xy):
            return tuple(v if i % 2 else mirror(v) for i, v in enumerate(xy))

        post = 0.51 if mono else 0.43
        g.stroke(
            part(0.98, -122),
            part(0.77, -122),
            part(0.61, -122, post, -70, post, 8),
            part(post, 200),
            part(post, 260, post - 0.13, 297, 0.05, 304),
            part(post - 0.13, 311, post, 348, post, 408),
            part(post, 600),
            part(post, 678, 0.61, 730, 0.77, 730),
            part(0.98, 730),
            aspect=0.90,
        )
    elif name in ("Oslash", "oslash", "emptyset"):
        outer = max(rings, key=lambda c: abs(c.area))
        z = outer.pieces[:, 0]
        cap = name != "oslash"
        h = 350 if cap else 260
        half = h + (12 if cap else 10)
        l, b, r, t = box
        cx = (l + r) / 2
        # The two flat cuts of the slash extend beyond the overshoots.
        ends = [z[z.imag < h - half - 1].mean(), z[z.imag > h + half + 1].mean()]
        g = Drawing(box, box, sx, dx, serif)
        rx = (r - l) / 2 - 12 / sx
        ry = half - g.thickness * g.aspect / 2
        k = 0.56
        g.stroke(
            (cx, h - ry),
            (cx + k * rx, h - ry, cx + rx, h - k * ry, cx + rx, h),
            (cx + rx, h + k * ry, cx + k * rx, h + ry, cx, h + ry),
            (cx - k * rx, h + ry, cx - rx, h + k * ry, cx - rx, h),
            (cx - rx, h - k * ry, cx - k * rx, h - ry, cx, h - ry),
            closed=True,
        )
        g.stroke((ends[0].real, ends[0].imag), (ends[1].real, ends[1].imag), width=0.78, aspect=1)
    elif name == "numbersign":
        g = Drawing(box, (46, 0, 534, 690), sx, dx, serif)
        for x in (153, 361):
            g.stroke((x, 0), (x + 66, 690), aspect=1)
        for y in (221, 467):
            g.stroke((46, y), (534, y), width=0.84, aspect=1)
    elif name == "won":
        frame = (28, 0, 572, 700) if mono else (6 if serif else 26, 0, 870 if serif else 858, 700)
        g = Drawing(box, frame, sx, dx, serif)
        if mono:
            stations = ((74, 700), (172, 19), (300, 425), (428, 19), (526, 700))
            heights = (256, 416)
        else:
            stations = (
                (87 if serif else 74, 700),
                (240, 17),
                (442, 659),
                (646, 17),
                (805 if serif else 810, 700),
            )
            heights = (251, 411) if serif else (254, 414)
        # Mitred joins keep the four rails straight on both sides of a bar.
        path = pathops.Path()
        path.moveTo(*g.xy(*stations[0]))
        for pt in stations[1:]:
            path.lineTo(*g.xy(*pt))
        path.stroke(24, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 12)
        path.convertConicsToQuads(0.04)
        l, b, r, t = box
        clip = pathops.Path()
        clip.moveTo(l * sx + dx - 100, 0)
        clip.lineTo(r * sx + dx + 100, 0)
        clip.lineTo(r * sx + dx + 100, 700)
        clip.lineTo(l * sx + dx - 100, 700)
        clip.close()
        g.pen.add(pathops.op(path, clip, pathops.PathOp.INTERSECTION))
        if serif:
            for x, y in (stations[0], stations[-1]):
                g.stroke((x - 37, 695), (x + 37, 695), width=0.49, aspect=1)
        for y in heights:
            g.stroke(
                (28 if mono else 26, y), (572 if mono else 858, y), width=0.75 if serif else 0.84, aspect=1
            )
    elif name == "sterling":
        g = Drawing(box, (49 if serif else 52, 0, 532 if serif else 526, 700), sx, dx, serif)
        g.stroke(
            (499, 593),
            (459, 652, 406, 689, 345, 689),
            (245, 689, 190, 608, 190, 495),
            (190, 293),
            (190, 164, 154, 64, 87, 12),
            (507, 12),
        )
        g.stroke(
            (52, 387 if serif else 349), (328 if serif else 412, 387 if serif else 349), width=0.8, aspect=1
        )
        if serif:
            g.stroke((468, 12), (489, 12, 506, 41, 510, 85), width=0.82)
    elif name == "euro":
        g = Drawing(box, (28, -10, 568 if serif else 566, 700), sx, dx, serif)
        g.stroke(
            (539, 591),
            (501, 650, 442, 689, 374, 689),
            (231, 689, 144, 539, 144, 345),
            (144, 155, 233, 0, 374, 0),
            (442, 0, 503, 41, 541, 104),
        )
        if serif:
            g.stroke((538, 592), (543, 673), width=0.76)
        for y, end in ((280, 444), (415, 464)):
            g.stroke((28, y), (end, y), width=0.75 if serif else 0.84, aspect=1)
    elif name == "uni20BE":
        g = Drawing(box, (30, 0, 640, 730), sx, dx, serif)
        g.stroke(
            (640, 11),
            (222, 11),
            (121, 11, 71, 91, 71, 240),
            (71, 460, 201, 617, 355, 617),
            (500, 617, 600, 512, 600, 330),
        )
        for x in (275, 435):
            g.stroke((x, 300), (x, 730), width=0.80, aspect=1)
    else:
        g = Drawing(box, (40, 0, 660, 680), sx, dx, serif)
        g.stroke((80, 0), (80, 270), (80, 419, 201, 540, 350, 540), (499, 540, 620, 419, 620, 270), (620, 0))
        g.stroke((350, 0), (350, 680), width=0.8, aspect=1)
    return g.pen.rings()


def thin_rings(name, reference, sx, dx, serif, mono, italic=False):
    from junction_drawings import NAMES as JUNCTIONS, thin
    if name in JUNCTIONS:
        return ordered_contours(reference, thin(name, reference, sx, dx, serif, mono, italic))
    if name in SANS_CAPS or name in MONO_LETTERS:
        box = bounds(reference)
        if name == "K":
            g = Drawing(box, (72, 0, 552, 700) if mono else (82, 0, 590, 700), sx, dx, False)
            stem = 114 if mono else 128
            arm_x, root, tip = (184, 304, 497) if mono else (128, 270, 513)
            g.stroke((stem, 0), (stem, 700), aspect=1)
            if mono:
                g.stroke((stem, root), (arm_x, root), aspect=1)

            def rail(x0, y0, x1, y1):
                g.pen.ribbon(g.xy(x0, y0), g.xy(x1, y1), 24)

            rail(arm_x, root, tip, 700)
            t = 0.27 if mono else 0.36
            rail(arm_x + t * (tip - arm_x), root + t * (700 - root), 503 if mono else 536, 0)
        elif name == "R":
            g = Drawing(box, (72, 0, 552, 700) if mono else (82, 0, 572, 700), sx, dx, False)
            stem, waist = (114, 331) if mono else (128, 365)
            g.stroke((stem, 0), (stem, 700), aspect=1)
            g.stroke(
                (stem, 689),
                (310, 689),
                (422, 689, 484, 610, 484, 505),
                (484, waist + 68, 419, waist, 310, waist),
                (stem, waist),
            )
            g.pen.ribbon(g.xy(310, waist), g.xy(500 if mono else 521, 0), 24)
        elif name == "Q":
            g = Drawing(box, (46, -98, 566, 712) if mono else (56, -112, 638, 712), sx, dx, False)
            cx, rx = (300, 254 - 12 / g.sx) if mono else (342, 286 - 12 / g.sx)
            ry = 351
            g.stroke(
                (cx, 350 - ry),
                (cx + 0.56 * rx, 350 - ry, cx + rx, 350 - 0.56 * ry, cx + rx, 350),
                (cx + rx, 350 + 0.56 * ry, cx + 0.56 * rx, 350 + ry, cx, 350 + ry),
                (cx - 0.56 * rx, 350 + ry, cx - rx, 350 + 0.56 * ry, cx - rx, 350),
                (cx - rx, 350 - 0.56 * ry, cx - 0.56 * rx, 350 - ry, cx, 350 - ry),
                closed=True,
            )
            start = (cx + 0.40 * rx, 350 - 0.9165 * ry)
            if mono:
                g.stroke(start, (446, -34, 492, -75, 549, -61), width=0.95)
            else:
                g.stroke(start, (505, -41, 562, -83, 625, -71), width=0.95)
        elif name == "J":
            if mono:
                g = Drawing(box, (72, -12, 430, 700), sx, dx, False)
                g.stroke(
                    (204, 689), (388, 689), (388, 210), (388, 86, 340, 0, 251, 0), (188, 0, 139, 39, 100, 105)
                )
            else:
                g = Drawing(box, (40, -12, 418, 700), sx, dx, False)
                g.stroke((372, 700), (372, 214), (372, 89, 313, 0, 223, 0), (161, 0, 108, 39, 71, 104))
        elif box[1] < -100:
            g = Drawing(box, (69, -184, 415, 748), sx, dx, False)
            g.stroke(
                (410, 706),
                (389, 724, 361, 736, 331, 736),
                (264, 736, 230, 678, 230, 597),
                (230, -2),
                (230, -110, 196, -172, 131, -172),
                (107, -172, 89, -168, 74, -162),
            )
            g.stroke((77, 482), (401, 482), width=0.84, aspect=1)
        else:
            g = Drawing(box, (108, 0, 494, 752), sx, dx, False)
            g.stroke((252, 10), (252, 603), (252, 682, 306, 741, 383, 741), (423, 741, 458, 733, 485, 716))
            g.stroke((108, 484), (468, 484), width=0.84, aspect=1)
            g.stroke((128, 10), (396, 10), width=0.84, aspect=1)
        rings = g.pen.rings()
    elif name in SIGNS:
        rings = signs(name, reference, sx, dx, serif, mono)
    elif name in FIGURES:
        rings = numeral(FIGURES[name], bounds(reference), sx, dx, serif)
    else:
        slash = next(c for c in reference if np.ptp(c.pieces[:, 0].imag) > 650)
        high = [c for c in reference if c is not slash and c.center.imag > 285]
        low = [c for c in reference if c is not slash and c not in high]
        a, b = FRACTIONS[name]
        rings = numeral(a, bounds(high), sx, dx, serif) + numeral(b, bounds(low), sx, dx, serif)
        nodes = slash.pieces[:, 0]
        bot = nodes[nodes.imag < nodes.imag.min() + 2].mean()
        top = nodes[nodes.imag > nodes.imag.max() - 2].mean()
        p = ThinPen(1)
        p.stroke((bot.real * sx + dx, bot.imag), (top.real * sx + dx, top.imag), width=18, aspect=1)
        rings += p.rings()
    return ordered_contours(reference, rings)


def register_figure(reference, target):
    """Match positions and tangents in ink space, allowing extra knot subdivisions.

    Joined strokes produce extra vertices on only one drawing. Match the
    boundary monotonically so an unmatched tip cannot steal a distant corner.
    """
    if target.area * reference.area < 0:
        target = Contour(target.pieces[::-1, ::-1])

    def feature(ring, u):
        z = ring.eval(u)
        span = np.ptp(ring.pieces[:, 0].real) + 1j * np.ptp(ring.pieces[:, 0].imag)

        def normalize(v):
            return v.real / max(span.real, 1) + 1j * v.imag / max(span.imag, 1)

        pos = normalize(z - ring.center)
        left = normalize(ring.eval(u - 1e-5, tangent=True))
        right = normalize(ring.eval(u + 1e-5, tangent=True))
        return pos, left / np.maximum(abs(left), 1e-9), right / np.maximum(abs(right), 1e-9)

    def distance(a, b):
        p, i, o = a
        q, j, k = b
        return abs(p[:, None] - q) ** 2 + 0.045 * (abs(i[:, None] - j) ** 2 + abs(o[:, None] - k) ** 2)

    start = distance(feature(reference, np.array([0.0])), feature(target, target.knots[:-1]))
    target = target.roll(int(start.argmin()))

    def stations(r):
        return np.unique(np.r_[0.0, 1.0, r.knots[r.corners], np.arange(1, 40) / 40])

    a, b = stations(reference), stations(target)
    cost = distance(feature(reference, a), feature(target, b))
    score = np.full(cost.shape, np.inf)
    prev = np.zeros((*cost.shape, 2), int)
    score[0, 0] = 0
    # Every accepted station advances on both outlines. A surplus source
    # corner can be skipped without crossing or collapsing a whole stroke.
    for i in range(1, len(a)):
        for j in range(1, len(b)):
            candidates = [
                (score[i - u, j - v] + 0.003 * (u + v - 2), u, v)
                for u, v in ((1, 1), (1, 2), (2, 1), (1, 3), (3, 1))
                if i >= u and j >= v
            ]
            prior, du, dv = min(candidates)
            score[i, j] = prior + cost[i, j]
            prev[i, j] = (i - du, j - dv)
    indices = [(len(a) - 1, len(b) - 1)]
    while indices[-1] != (0, 0):
        indices.append(tuple(prev[indices[-1]]))
    ii, jj = np.asarray(indices[::-1]).T
    return target, a[ii], b[jj]


class PreservedMaster:
    """A quadratic master in the existing variable font's material coordinates."""

    def __init__(self, z, knots):
        self.starts = z[::2]
        self.handles = z[1::2]
        self.ends = np.roll(self.starts, -1)
        self.stops = knots

    def eval(self, u):
        j = np.searchsorted(self.stops[1:], u, side="right").clip(0, len(self.starts) - 1)
        t = (u - self.stops[j]) / (self.stops[j + 1] - self.stops[j])
        return (1 - t) ** 2 * self.starts[j] + 2 * (1 - t) * t * self.handles[j] + t * t * self.ends[j]


def replace_masters(design, name, cells, tracks, ends, weight, drawer, radius):
    """Insert drawings at one weight while preserving the other master curves."""
    unslant = lambda z: z - design.slant * z.imag
    parts = [np.split(unslant(z), np.asarray(ends[:-1]) + 1) for z in tracks]
    reference = []
    grids = []
    for z in parts[0]:
        a, b = z[::2], z[1::2]
        c = np.roll(a, -1)
        pieces = np.array([a, (a + 2 * b) / 3, (c + 2 * b) / 3, c]).T
        live = np.maximum(abs(b - a), abs(c - a)) > 0.0001
        ring = Contour(pieces[live])
        reference.append(ring)
        # A collapsed corner in Regular may open in another weight or radius.
        # Reserve a material interval for it in every master.
        lengths = np.full(len(a), 0.04)
        lengths[live] = np.maximum(0.04, np.diff(ring.breaks))
        knots = np.r_[0, lengths.cumsum()] / lengths.sum()
        grids.append((knots, np.r_[0, np.cumsum(np.where(live, 1, 0))]))
    profiles = [[] for r in reference]
    for j, (w, d) in enumerate(cells):
        if w == weight:
            new = drawer(design, name, reference, d)
        for i, ref in enumerate(reference):
            knots, ids = grids[i]
            if w == weight:
                ring, a, b = register_figure(ref, new[i])
                # Convert the reference arc parameter to the shared segment grid.
                a = np.interp(a, ref.knots[ids], knots)
                profiles[i].extend(Profile(ring, a, b, r) for r in (0, radius))
            else:
                profiles[i].extend(PreservedMaster(parts[2 * j + k][i], knots) for k in (0, 1))
    result = [[] for z in tracks]
    last = []
    for row in profiles:
        for out, z in zip(result, compatible_points(row, 0.16, compact=0.12)):
            out.extend(z + design.slant * z.imag)
        last.append(len(result[0]) - 1)
    return list(map(np.asarray, result)), last


def width_station_map(native, other):
    """Follow the same Thin landmark across widths in width-normalized space."""

    def normalized(ring):
        z = ring.pieces
        span = np.ptp(z[:, 0].real)
        return Contour((z.real - ring.center.real) * 400 / span + 1j * z.imag)

    base, wide = normalized(native), normalized(other)
    aligned, a, b = register_figure(base, wide)
    # Roll the physical curve to the start chosen in normalized space.
    if aligned.area * wide.area < 0:
        other = Contour(other.pieces[::-1, ::-1])
        wide = normalized(other)
    start = np.argmin(abs(wide.pieces[:, 0] - aligned.pieces[0, 0]))
    other = other.roll(start)
    # Constrain extrema and spline boundaries in both spaces. In particular
    # neither side of a crown can drift sideways through width interpolation.
    material = np.unique(np.r_[a, base.knots, np.interp(aligned.knots, b, a)])
    dst = np.interp(material, a, b)
    return other, np.interp(material, base.knots, native.knots), np.interp(dst, aligned.knots, other.knots)


def replace_special_thin(design, name, cells, tracks, ends):
    def draw(face, glyph, reference, width):
        scale, shift = face.transform(glyph, 100, width)
        return thin_rings(glyph, reference, scale, shift, face.serif, face.mono, bool(face.slant))

    return replace_masters(design, name, cells, tracks, ends, 100, draw, 4 if design.serif else 8)
