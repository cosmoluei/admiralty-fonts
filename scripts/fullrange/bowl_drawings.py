"""Bowl outlines with independent waist, counter and crossbar landmarks."""

import pathops


def contour(start, *segments):
    path = pathops.Path()
    pen = path.getPen()
    pen.moveTo(start)
    for segment in segments:
        if len(segment) == 2:
            pen.lineTo(segment)
        else:
            pen.curveTo(segment[:2], segment[2:4], segment[-2:])
    pen.closePath()
    return path


def ellipse(l, b, r, t):
    cx, cy = (r + l) / 2, (t + b) / 2
    a, h = (r - l) * 0.276142375, (t - b) * 0.276142375
    return contour(
        (cx, t),
        (cx + a, t, r, cy + h, r, cy),
        (r, cy - h, cx + a, b, cx, b),
        (cx - a, b, l, cy - h, l, cy),
        (l, cy + h, cx - a, t, cx, t),
    )


def black_digit(number, box):
    if number == 3:
        # A recessed right-hand joint separates the lobes even at the size
        # of a fraction denominator. The two left terminals have angled cuts.
        p = contour(
            (0.015, 0.853),
            (0.125, 0.954, 0.31, 1, 0.49, 1),
            (0.757, 1, 0.936, 0.89, 0.936, 0.742),
            (0.936, 0.64, 0.833, 0.553, 0.706, 0.523),
            (0.684, 0.518, 0.682, 0.510, 0.707, 0.503),
            (0.875, 0.458, 1, 0.384, 1, 0.257),
            (1, 0.103, 0.798, 0, 0.502, 0),
            (0.286, 0, 0.121, 0.058, 0, 0.154),
            (0.115, 0.30),
            (0.232, 0.226, 0.349, 0.181, 0.501, 0.181),
            (0.656, 0.181, 0.746, 0.22, 0.746, 0.294),
            (0.746, 0.383, 0.647, 0.431, 0.485, 0.431),
            (0.33, 0.431),
            (0.33, 0.596),
            (0.478, 0.596),
            (0.603, 0.596, 0.691, 0.636, 0.691, 0.716),
            (0.691, 0.784, 0.616, 0.826, 0.49, 0.826),
            (0.347, 0.826, 0.246, 0.79, 0.143, 0.721),
        )
    else:
        p = contour(
            (0.5, 1),
            (0.77, 1, 0.947, 0.894, 0.947, 0.745),
            (0.947, 0.636, 0.86, 0.566, 0.778, 0.515),
            (0.756, 0.50, 0.756, 0.496, 0.78, 0.48),
            (0.916, 0.405, 1, 0.34, 1, 0.245),
            (1, 0.095, 0.80, 0, 0.5, 0),
            (0.20, 0, 0, 0.095, 0, 0.245),
            (0, 0.34, 0.084, 0.405, 0.22, 0.48),
            (0.244, 0.496, 0.244, 0.50, 0.222, 0.515),
            (0.14, 0.566, 0.053, 0.636, 0.053, 0.745),
            (0.053, 0.894, 0.23, 1, 0.5, 1),
        )
        for hole in (
            ellipse(0.282, 0.61, 0.718, 0.846),
            ellipse(0.251, 0.153, 0.749, 0.397),
        ):
            p = pathops.op(p, hole, pathops.PathOp.DIFFERENCE)
    l, b, r, t = box
    return p.transform(r - l, 0, 0, t - b, l, b)


def thin_d(box):
    l, b, r, t = box
    mid = (t + b) / 2
    shoulder = l + 0.42 * (r - l)

    def bowl(left, right, low, high):
        return contour(
            (left, low),
            (left, high),
            (shoulder, high),
            (
                shoulder + 0.60 * (right - shoulder),
                high,
                right,
                mid + 0.55 * (high - mid),
                right,
                mid,
            ),
            (
                right,
                mid - 0.55 * (mid - low),
                shoulder + 0.60 * (right - shoulder),
                low,
                shoulder,
                low,
            ),
        )

    return pathops.op(
        bowl(l, r, b, t),
        bowl(l + 24, r - 24, b + 22, t - 22),
        pathops.PathOp.DIFFERENCE,
    )


def thin_bitcoin(p, box):
    l, b, r, t = box
    x = l + 12
    j = l + 0.47 * (r - l)
    g = l + 0.96 * (r - l)
    mid = b + 0.51 * (t - b)

    def lobe(y0, y1, edge):
        halfway = (y0 + y1) / 2
        p.stroke(
            (x, y0),
            (j, y0),
            (
                j + 0.64 * (edge - j),
                y0,
                edge,
                halfway - 0.56 * (halfway - y0),
                edge,
                halfway,
            ),
            (edge, halfway + 0.56 * (y1 - halfway), j + 0.64 * (edge - j), y1, j, y1),
            (x, y1),
            width=24,
            aspect=0.80,
        )

    p.stroke((x, b), (x, t), width=24, aspect=1)
    lobe(b + 9.6, mid, r - 12)
    lobe(mid, t - 9.6, g - 12)


def thin_g(p, box):
    l, b, r, t = box
    half = 12
    l, r = l + half, r - half
    b, t = b + 10.5, t - 10.5
    span = r - l
    cx = l + 0.53 * span
    mid = (b + t) / 2
    shelf = b + 0.51 * (t - b)
    # A smooth crown opens to a clean cut. The lower bowl reaches its
    # vertical tangent before changing into the right-hand upright.
    p.stroke(
        (r - 0.035 * span, t - 0.15 * (t - b)),
        (r - 0.12 * span, t - 0.047 * (t - b), cx + 0.20 * span, t, cx, t),
        (cx - 0.32 * span, t, l, mid + 0.29 * (t - b), l, mid),
        (l, mid - 0.29 * (t - b), cx - 0.31 * span, b, cx, b),
        (cx + 0.27 * span, b, r, b + 0.14 * (t - b), r, b + 0.34 * (t - b)),
        (r, shelf),
        width=24,
        aspect=0.88,
    )
    p.stroke((l + 0.55 * span, shelf), (r + half, shelf), width=21, aspect=1)


def estimated(p, box):
    l, b, r, t = box
    l, r = l + 12, r - 12
    b, t = b + 11, t - 11
    span, height = r - l, t - b
    cx = l + 0.50 * span
    bar = b + 0.52 * height
    p.stroke(
        (r - 0.035 * span, b + 0.155 * height),
        (r - 0.14 * span, b + 0.055 * height, cx + 0.23 * span, b, cx, b),
        (cx - 0.33 * span, b, l, bar - 0.29 * height, l, bar),
        (l, bar + 0.28 * height, cx - 0.28 * span, t, cx, t),
        (cx + 0.28 * span, t, r, bar + 0.25 * height, r, bar - 10.5),
        width=24,
        aspect=0.88,
    )
    p.stroke((l, bar), (r + 12, bar), width=21, aspect=1)


def capital_b(box, weight):
    l, b, r, t = box
    span = r - l
    h = t - b
    stem = 24 if weight == 100 else min(138, span * 0.285)
    bar = 20 if weight == 100 else min(105, stem * 0.85)
    mid = b + 0.51 * h
    neck = l + 0.61 * span
    top_edge = r - 0.045 * span

    def lobe(left, right, low, high, shoulder):
        center = (low + high) / 2
        return contour(
            (left, low),
            (left, high),
            (shoulder, high),
            (
                shoulder + 0.65 * (right - shoulder),
                high,
                right,
                center + 0.56 * (high - center),
                right,
                center,
            ),
            (
                right,
                center - 0.56 * (center - low),
                shoulder + 0.65 * (right - shoulder),
                low,
                shoulder,
                low,
            ),
        )

    lower = lobe(l, r, b, mid + bar / 2, neck)
    upper = lobe(l, top_edge, mid - bar / 2, t, neck - 0.035 * span)
    ink = pathops.op(lower, upper, pathops.PathOp.UNION)
    if weight == 900:

        def at(v, h):
            return (l + span * v, b + (t - b) * h)

        def bez(a, b, c, d, e, f):
            return (*at(a, b), *at(c, d), *at(e, f))

        ink = contour(
            at(0, 0),
            at(0, 1),
            at(0.55, 1),
            bez(0.79, 1, 0.955, 0.915, 0.955, 0.75),
            bez(0.955, 0.635, 0.88, 0.556, 0.735, 0.523),
            bez(0.718, 0.519, 0.718, 0.510, 0.738, 0.506),
            bez(0.902, 0.468, 1, 0.385, 1, 0.254),
            bez(1, 0.106, 0.843, 0, 0.594, 0),
        )
    for edge, lo, hi in (
        (r, b + bar, mid - bar / 2),
        (top_edge, mid + bar / 2, t - bar),
    ):
        hole = lobe(
            l + stem, edge - stem, lo, hi, min(neck - 0.055 * span, edge - stem * 0.99)
        )
        ink = pathops.op(ink, hole, pathops.PathOp.DIFFERENCE)
    return ink
