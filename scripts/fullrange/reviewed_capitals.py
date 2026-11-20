"""Match each corner of the crossing and zigzag capitals across all axes."""

import numpy as np


def rounded(z, radius):
    prev, nxt = np.roll(z, 1) - z, np.roll(z, -1) - z
    a, b = np.maximum(abs(prev), 1.0e-7), np.maximum(abs(nxt), 1.0e-7)
    theta = np.arccos(np.clip((prev.conj() * nxt).real / (a * b), -1, 1))
    trim = np.minimum(
        radius / np.maximum(np.tan(theta / 2), 0.001), 0.42 * np.minimum(a, b)
    )
    entry, exit = z + trim * prev / a, z + trim * nxt / b
    return np.column_stack((entry, z, exit, (exit + np.roll(entry, -1)) / 2)).ravel()


def thin_or_black(name, left, right, height, weight):
    span = right - left
    stem = 24 if weight == 100 else min(133, span * (0.22 if name == "W" else 0.34))
    x = lambda f: left + span * f
    point = lambda x, y: complex(x, y)
    if name == "K":
        h = height
        mid = stem / 2 + left
        edge = mid + stem / 2
        join = 290
        # One uninterrupted rising rail passes through the junction.
        upper = right - 0.58 * stem
        m = (upper - mid) / (h - join)
        half = stem * 0.5 * np.hypot(1, m)
        knee = join + 0.25 * (h - join)
        k = mid + m * (knee - join)
        lower = right - 0.58 * stem
        n = (k - lower) / knee
        leg = stem * 0.5 * np.hypot(1, n)
        outer_y = knee + (leg - half) / (m - n)
        outer = (k + m * (outer_y - knee) + half, outer_y)
        inner_y = knee + (-leg - half) / (m - n)
        inner = (k + m * (inner_y - knee) + half, inner_y)
        # Two positions on straight rails correspond to the two small flats
        # in the prototype; at Thin they coincide with the adjoining rail.
        spur = (outer[0] + 0.015 * (lower + leg - outer[0]), outer[1] * 0.985)
        foot_y = join + (edge - mid - half) / m
        foot = (edge + 0.025 * (inner[0] - edge), foot_y + 0.025 * (inner[1] - foot_y))
        pts = [
            (left, 0),
            (left, h),
            (edge, h),
            (edge, join + (edge - mid + half) / m),
            (upper - half, h),
            (upper + half, h),
            outer,
            spur,
            (lower + leg, 0),
            (lower - leg, 0),
            inner,
            foot,
            (edge, foot_y),
            (edge, 0),
        ]
    else:
        h = height
        crown = h * 0.75
        a, b, c = left + stem / 2, x(0.26), x(0.5)
        # Reserve enough white at the center of the narrowest Black master.
        half = min(stem / 2, 0.40 * (b - a))
        m = (b - a) / h
        n = (c - b) / crown
        u = half * np.hypot(1, m)
        v = half * np.hypot(1, n)
        gap = 1 if weight == 100 else 3
        eye = (u + v + 2 * gap) / (m + n)
        tip = b + u - m * eye
        valley = crown - (2 * v + 2 * gap) / (2 * n)
        rev = lambda value: 2 * c - value
        pts = [
            (b + v, 0),
            (b - u, 0),
            (a - u, h),
            (a + u, h),
            (tip, eye),
            (tip + 2 * gap, eye),
            (c - v, crown),
            (c + v, crown),
            (rev(tip + 2 * gap), eye),
            (rev(tip), eye),
            (rev(a + u), h),
            (rev(a - u), h),
            (rev(b - u), 0),
            (rev(b + v), 0),
            (c + gap, valley),
            (c - gap, valley),
        ]
    return np.array([point(a, b) for a, b in pts])


def tracks(design, name, cells):
    glyph = design.regular["glyf"][name]
    xy = np.asarray(glyph.coordinates)
    native = xy[:, 0] - design.slant * xy[:, 1] + 1j * xy[:, 1]
    result = []
    for w, d in cells:
        sx, dx = design.transform(name, w, d)
        if w == 400:
            z = native.real * sx + dx + 1j * native.imag
        elif name == "X":
            # Set both centerlines from the Regular terminals at this width.
            # Holding their angle through weight changes also keeps the two
            # halves collinear between the three drawn weights.
            sx, dx = design.transform(name, 400, d)
            top = (
                native[[5, 6]].real.mean() * sx + dx,
                native[[8, 9]].real.mean() * sx + dx,
            )
            bot = (
                native[[2, 3]].real.mean() * sx + dx,
                native[[0, 11]].real.mean() * sx + dx,
            )
            a, b = (top[0] + bot[0]) / 2, (top[1] + bot[1]) / 2
            slope = (b - a) / 700
            t = 24 if w == 100 else min(128, (b - a) * 0.40)
            half = t * 0.5 * np.hypot(1, slope)
            mid = (a + b) / 2
            z = np.array(
                [
                    b - half,
                    mid + 1j * (350 - half / slope),
                    a + half,
                    a - half,
                    mid - half + 350j,
                    a - half + 700j,
                    a + half + 700j,
                    mid + 1j * (350 + half / slope),
                    b - half + 700j,
                    b + half + 700j,
                    mid + half + 350j,
                    b + half,
                ]
            )
        elif name == "W" and w == 900:
            # Carry the release's bold W forward in its native cell. Its four
            # narrow stems need more space than the width fit of a single stem.
            bold = np.asarray(design.bold["glyf"][name].coordinates)
            bold = bold[:, 0] - design.slant * bold[:, 1] + 1j * bold[:, 1]
            z = native + 1.55 * (bold - native)
            sx, dx = design.transform(name, 400, d)
            z = z.real * sx + dx + 1j * z.imag
        else:
            z = thin_or_black(
                name, native.real.min() * sx + dx, native.real.max() * sx + dx, 700, w
            )
        if len(z) != len(native):
            raise ValueError((name, len(z), len(native)))
        for radius in (0, {100: 8, 400: 27, 900: 39}[w]):
            if name == "X":
                # The acute internal junctions must retain exposed straight
                # edges even on a condensed, rounded Black cross.
                radius = np.full(len(z), radius, dtype=float)
                radius[[1, 4, 7, 10]] *= 0.20
            pts = rounded(z, radius)
            result.append(pts + design.slant * pts.imag)
    return result, [len(result[0]) - 1]


def kip_tracks(design, name, cells):
    """Follow the two rail edges through each branch, including at Light."""
    glyph = design.regular["glyf"][name]
    raw = np.asarray(glyph.coordinates)
    native = raw[:, 0] - design.slant * raw[:, 1] + 1j * raw[:, 1]
    tracks = []
    for w, d in cells:
        sx, dx = design.transform(name, 400 if design.mono else w, d)
        proto = native.real * sx + dx + 1j * native.imag
        if w == 400:
            z = proto
        else:
            span = np.ptp(proto.real)
            pen = 24 if w == 100 else min(126, 0.27 * span)
            rail = 20 if w == 100 else min(95, 0.75 * pen)
            lo, hi = 350 - rail / 2, 350 + rail / 2
            center = (
                proto[5 if design.mono else 6].real
                + proto[6 if design.mono else 7].real
            ) / 2
            L, R = center - pen / 2, center + pen / 2
            start = proto.real.min()
            end = proto.real.max()
            joint = R + 0.095 * span
            tip = end - 0.54 * pen
            slope = (tip - joint) / 350
            half = 0.5 * pen * np.hypot(1, slope)
            ul = joint + slope * (hi - 350) - half
            ur = ul + 2 * half
            # A horizontal stroke connects both branches, with flat caps and
            # clean intersections on both sides of the vertical.
            lower = joint + slope * (350 - lo)
            ll, lr = lower - half, lower + half
            left_cap = tip - half
            right_cap = tip + half
            if design.mono:
                pts = [
                    (L, 0),
                    (L, lo),
                    (start, lo),
                    (start, hi),
                    (L, hi),
                    (L, 700),
                    (R, 700),
                    (R, hi),
                    (max(R + 1, ul), hi),
                    (left_cap, 700),
                    (right_cap, 700),
                    (ur, hi),
                    (end, hi),
                    (end, lo),
                    (lr, lo),
                    (right_cap, 0),
                    (left_cap, 0),
                    (ll, lo),
                    (R + 1, lo),
                    (R + 0.5, lo - 0.5),
                    (R, lo - 0.5),
                    (R, 0),
                ]
            else:
                pts = [
                    (R, 0),
                    (L, 0),
                    (L, lo),
                    (start, lo),
                    (start, hi),
                    (L, hi),
                    (L, 700),
                    (R, 700),
                    (R, hi),
                    (max(R + 1, ul), hi),
                    (left_cap, 700),
                    (right_cap, 700),
                    (ur + slope, hi + 1),
                    (ur, hi),
                    (end, hi),
                    (end, lo),
                    (lr, lo),
                    (right_cap, 0),
                    (left_cap, 0),
                    (ll, lo),
                    (R + 1, lo),
                    (R, lo - 1),
                ]
            z = np.array([complex(x, y) for x, y in pts])
        for radius in (0, {100: 6, 400: 16, 900: 22}[w]):
            q = rounded(z, radius)
            tracks.append(q + design.slant * q.imag)
    return tracks, [len(tracks[0]) - 1]
