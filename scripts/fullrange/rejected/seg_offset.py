"""Stroke-weight change by moving each outline segment along its own normal.

Each segment (a line or a curve between two on-curve points) is moved by an amount that is
proportional to the thickness of the stroke it belongs to, measured across the stroke from the
segment's middle. Corners are rebuilt where the moved neighbouring segments meet (a true mitre),
so diagonals keep an even thickness and serifs stay whole. Segments that end a stroke (their
"thickness" is really the stroke's length) do not move, and edges that lie on an alignment
height (baseline, x-height, cap height, ...) stay on it while the other side of the stroke
moves twice as far. The point structure never changes, so results stay interpolatable.
"""
import math


def _bez(p0, h, p1, u):
    if len(h) == 2:
        m = 1 - u
        return (m**3 * p0[0] + 3*m*m*u*h[0][0] + 3*m*u*u*h[1][0] + u**3 * p1[0],
                m**3 * p0[1] + 3*m*m*u*h[0][1] + 3*m*u*u*h[1][1] + u**3 * p1[1])
    if len(h) == 1:
        m = 1 - u
        return (m*m*p0[0] + 2*m*u*h[0][0] + u*u*p1[0], m*m*p0[1] + 2*m*u*h[0][1] + u*u*p1[1])
    return (p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u)


def _segments(c):
    """[(i_start, [handle indices], i_end)] for one closed contour."""
    n = len(c)
    on = [k for k in range(n) if c[k][2] is not None]
    segs = []
    for a, b in zip(on, on[1:] + on[:1]):
        hs, j = [], (a + 1) % n
        while j != b:
            hs.append(j); j = (j + 1) % n
        segs.append((a, hs, b))
    return segs


def _flat(cs, steps=10):
    out = []
    for c in cs:
        for a, hs, b in _segments(c):
            p0, p1, h = c[a], c[b], [c[k] for k in hs]
            prev = (p0[0], p0[1])
            for t in range(1, (steps if h else 1) + 1):
                q = _bez(p0, h, p1, t / (steps if h else 1))
                out.append((prev[0], prev[1], q[0], q[1])); prev = q
    return out


def _ray(px, py, dx, dy, segs, skip=4.0):
    best, hit = None, None
    for x0, y0, x1, y1 in segs:
        ex, ey = x1 - x0, y1 - y0
        den = dx * ey - dy * ex
        if abs(den) < 1e-9:
            continue
        t = ((x0 - px) * ey - (y0 - py) * ex) / den
        u = ((x0 - px) * dy - (y0 - py) * dx) / den
        if t > skip and -1e-6 <= u <= 1 + 1e-6 and (best is None or t < best):
            best, hit = t, (x0 + u * ex, y0 + u * ey, ex, ey)
    return best, hit


def _unit(x, y):
    L = math.hypot(x, y)
    return (x / L, y / L) if L > 1e-9 else (0.0, 0.0)


def _in_zone(y, zones, tol=16):
    return any(abs(y - z) <= tol for z in zones)


def offset(cs, fx, fy, stem, zones):
    """Make strokes fx times as thick across vertical stems and fy times across horizontal bars."""
    flat = _flat(cs)
    cap = 1.45 * stem
    # outline direction: PostScript outlines run counter-clockwise outside; some glyphs (made by
    # path operations) run the other way, so flip the normals for them
    def area(c):
        return sum(c[i][0] * c[(i + 1) % len(c)][1] - c[(i + 1) % len(c)][0] * c[i][1] for i in range(len(c))) / 2
    if cs:
        big = max(cs, key=lambda c: abs(area(c)))
        sgn = 1.0 if area(big) >= 0 else -1.0
    else:
        sgn = 1.0
    out = []
    for c in cs:
        segs = _segments(c)
        if len(segs) < 2:
            out.append([p[:] for p in c]); continue
        info = []
        for a, hs, b in segs:
            p0, p1, h = c[a], c[b], [c[k] for k in hs]
            # tangents at both ends (skip zero-length handles)
            pts = [p0] + h + [p1]
            t0 = (0.0, 0.0)
            for q in pts[1:]:
                t0 = _unit(q[0] - p0[0], q[1] - p0[1])
                if t0 != (0.0, 0.0):
                    break
            t1 = (0.0, 0.0)
            for q in reversed(pts[:-1]):
                t1 = _unit(p1[0] - q[0], p1[1] - q[1])
                if t1 != (0.0, 0.0):
                    break
            # thickness: measured across the stroke at several places; the smallest is the stroke
            # itself (larger values come from where another stroke joins)
            T, hit, m, tm = None, None, None, None
            for u in (0.2, 0.35, 0.5, 0.65, 0.8):
                q = _bez(p0, h, p1, u)
                q2 = _bez(p0, h, p1, min(u + 0.02, 1.0))
                tq = _unit(q2[0] - q[0], q2[1] - q[1]) if h else _unit(p1[0] - p0[0], p1[1] - p0[1])
                nq = (sgn * tq[1], -sgn * tq[0])
                Tq, hq = _ray(q[0], q[1], -nq[0], -nq[1], flat)
                if u == 0.5:
                    m, tm = q, tq
                if Tq is not None and (T is None or Tq < T):
                    T, hit = Tq, hq
            nm = (sgn * tm[1], -sgn * tm[0])              # outward normal
            f = fx * nm[0] ** 2 + fy * nm[1] ** 2          # mix of the two factors by direction
            if T is None or T > cap:
                o = 0.0                                    # end of a stroke: keep its length
            elif abs(tm[1]) < 0.35 and _in_zone(m[1], zones):
                o = 0.0                                    # edge on an alignment height
            elif hit is not None and abs(hit[3]) < 0.35 * math.hypot(hit[2], hit[3]) and _in_zone(hit[1], zones) \
                    and abs(tm[1]) < 0.35:
                o = (f - 1) * T                            # other side of a bar on an alignment height
            else:
                o = (f - 1) / 2 * T
            short = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) < 0.4 * stem
            info.append([t0, t1, o, short])
        # tiny connecting edges (in a crotch or a joint) follow their neighbours
        for k in range(len(info)):
            if info[k][3]:
                nb = [info[(k - 1) % len(info)], info[(k + 1) % len(info)]]
                vals = [x[2] for x in nb if not x[3]]
                if vals:
                    info[k][2] = sum(vals) / len(vals)
        disp = {}
        ns = len(segs)
        for k in range(ns):
            a_in = info[k - 1]; a_out = info[k]
            i = segs[k][0]
            ta, tb = a_in[1], a_out[0]
            na, nb = (sgn * ta[1], -sgn * ta[0]), (sgn * tb[1], -sgn * tb[0])
            oa, ob = a_in[2], a_out[2]
            cross = ta[0] * tb[1] - ta[1] * tb[0]
            if abs(cross) < 0.2:                           # smooth: thickness measured at this point
                nx, ny = _unit(na[0] + nb[0], na[1] + nb[1])
                P = c[i]
                Tp, hp = _ray(P[0], P[1], -nx, -ny, flat)
                f = fx * nx ** 2 + fy * ny ** 2
                horiz = abs(ny) > 0.94                       # a top or bottom extreme
                if Tp is None or Tp > cap:
                    o = (oa + ob) / 2
                elif horiz and _in_zone(P[1], zones):
                    o = 0.0                                  # stays on the alignment height (overshoot)
                elif horiz and hp is not None and _in_zone(hp[1], zones) and abs(hp[3]) < 0.5 * math.hypot(hp[2], hp[3]) + 1e-9:
                    o = (f - 1) * Tp                         # the other side moves twice as far
                else:
                    o = (f - 1) / 2 * Tp
                d = (nx * o, ny * o)
            else:                                          # corner: where the two moved edges meet
                det = na[0] * nb[1] - na[1] * nb[0]
                d = ((oa * nb[1] - ob * na[1]) / det, (na[0] * ob - nb[0] * oa) / det)
                lim = 3.0 * max(abs(oa), abs(ob), 1e-6)
                L = math.hypot(*d)
                if L > lim:
                    d = (d[0] * lim / L, d[1] * lim / L)
            disp[i] = d
        new = [p[:] for p in c]
        for i, d in disp.items():
            new[i][0] += d[0]; new[i][1] += d[1]
        # handles: move with their own end of the segment
        for a, hs, b in segs:
            if not hs:
                continue
            half = len(hs) / 2
            for idx, k in enumerate(hs):
                d = disp[a] if idx < half else disp[b]
                if len(hs) == 1:
                    d = ((disp[a][0] + disp[b][0]) / 2, (disp[a][1] + disp[b][1]) / 2)
                new[k][0] += d[0]; new[k][1] += d[1]
        out.append(new)
    return out
