"""Pilot: Admiralty Sans lowercase n h m u r o i l drawn from measurements, for any weight and width.

At weight 400 / width 100 every letter reproduces today's Regular point for point. Other masters
are drawn, not stretched: stems, bars, bowls and joints have their own thickness per weight; the
counters (the white inside) take most of the width change; curves get squarer when narrow and
rounder when wide; arch joints keep a real thickness at every weight. Every master uses the same
drawing steps, so all masters are compatible for the variable font.
"""
import sys, math
from pathlib import Path
import ufoLib2
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor
import ufo2ft

XH, ASC, OV = 520, 740, 10
TOP, BOT = XH + OV, -OV

# measurements per weight (Regular values are today's design)
TAB = {
    #        stem  bar  bowl  joint  sb   n-advance
    100: dict(S=24, H=24, B=24, J=24, sb=70, adv=560),   # Thin: one even line everywhere
    400: dict(S=86, H=74, B=90, J=58, sb=76, adv=584),
    700: dict(S=134, H=104, B=140, J=84, sb=70, adv=626),
    900: dict(S=186, H=140, B=194, J=112, sb=62, adv=664),
}
WEIGHTS = [100, 400, 700, 900]
WIDTHS = [65, 100, 150]


class P:
    """All measurements for one master."""
    def __init__(self, w, d):
        t = TAB[w]; wf = d / 100.0
        self.wf = wf
        hv = max(0.0, (t["S"] - 86) / 100.0)          # 0 at Regular, 1 at Black
        es = 0.22 + 0.30 * hv * (wf < 1)              # heavy narrow stems thin more, to keep counters open
        self.S = t["S"] * wf ** es
        self.H = t["H"] * wf ** 0.08                 # bars barely change with width
        self.B = t["B"] * wf ** es
        self.J = t["J"] * wf ** es
        self.sb = t["sb"] * wf ** 0.7                # sidebearings change less than counters
        c0 = t["adv"] - 2 * t["sb"] - 2 * t["S"]     # n counter at normal width
        self.Cn = c0 * wf ** (1.12 - 0.30 * hv * (wf < 1))                   # counters take most of the width change
        # curve tension: squarer when narrow, rounder when wide (0.58 = today's arches)
        self.t = min(0.70, max(0.52, 0.58 + 0.26 * (1 - wf)))
        self.to = min(0.70, max(0.53, 0.585 + 0.24 * (1 - wf)))   # ovals (0.585 today)
        self.ti = min(0.72, max(0.55, 0.605 + 0.24 * (1 - wf)))


class B_:
    """Tiny outline builder without automatic splitting (keeps every master compatible)."""
    def __init__(self, x, y):
        self.pts = [(x, y, "line")]
    def L(self, x, y):
        self.pts.append((x, y, "line")); return self
    def C(self, c1, c2, e):
        self.pts += [(c1[0], c1[1], None), (c2[0], c2[1], None), (e[0], e[1], "curve")]; return self
    def last(self):
        return self.pts[-1][:2]
    def hv(self, x, y, t0, t1):
        x0, y0 = self.last(); return self.C((x0 + t0 * (x - x0), y0), (x, y - t1 * (y - y0)), (x, y))
    def vh(self, x, y, t0, t1):
        x0, y0 = self.last(); return self.C((x0, y0 + t0 * (y - y0)), (x - t1 * (x - x0), y), (x, y))
    def contour(self):
        pts = smooth_joins(list(self.pts))
        # close: the first point is a line start; if the last segment ends on it, drop the copy
        if abs(pts[-1][0] - pts[0][0]) < 1e-6 and abs(pts[-1][1] - pts[0][1]) < 1e-6:
            first_type = pts[-1][2]
            pts = pts[:-1]
            pts[0] = (pts[0][0], pts[0][1], first_type)
        return pts


def smooth_joins(pts):
    """Where two curves meet smoothly (top of an arch, say), give them the same curvature, so
    the join cannot be seen as a flat spot or a kink, even in Thin."""
    n = len(pts)
    closed_dup = abs(pts[-1][0] - pts[0][0]) < 1e-6 and abs(pts[-1][1] - pts[0][1]) < 1e-6
    out = [list(p) for p in pts]
    for i in range(n):
        if out[i][2] != "curve":
            continue
        a, b = i - 1, i + 1
        if b >= n:
            if not closed_dup:
                continue
            b = 1
        if out[a][2] is not None or out[b][2] is not None or a - 1 < 0 or b + 1 >= n:
            continue
        P = out[i]; A1 = out[a]; A2 = out[a - 1]; B1 = out[b]; B2 = out[b + 1]
        ta = (P[0] - A1[0], P[1] - A1[1]); tb = (B1[0] - P[0], B1[1] - P[1])
        la, lb = math.hypot(*ta), math.hypot(*tb)
        if la < 1 or lb < 1 or abs(ta[0] * tb[1] - ta[1] * tb[0]) > 1e-3 * la * lb:
            continue                               # not a smooth join
        u = (ta[0] / la, ta[1] / la)
        da = abs((A2[0] - A1[0]) * u[1] - (A2[1] - A1[1]) * u[0])   # far handle's distance from the tangent
        db = abs((B2[0] - B1[0]) * u[1] - (B2[1] - B1[1]) * u[0])
        if da < 1 or db < 1:
            continue
        ka, kb = da / la ** 2, db / lb ** 2
        k = math.sqrt(ka * kb)
        la2, lb2 = math.sqrt(da / k), math.sqrt(db / k)
        out[a][0], out[a][1] = P[0] - u[0] * la2, P[1] - u[1] * la2
        out[b][0], out[b][1] = P[0] + u[0] * lb2, P[1] + u[1] * lb2
    if closed_dup:
        out[-1][:2] = out[0][:2]
    return [tuple(p) for p in out]


def oval(cx, cy, rx, ry, t, cw=False):
    b = B_(cx, cy - ry)
    if not cw:
        b.hv(cx + rx, cy, t, t).vh(cx, cy + ry, t, t).hv(cx - rx, cy, t, t).vh(cx, cy - ry, t, t)
    else:
        b.hv(cx - rx, cy, t, t).vh(cx, cy + ry, t, t).hv(cx + rx, cy, t, t).vh(cx, cy - ry, t, t)
    return b.contour()


# ---------------------------------------------------------------------------------------------
# arches (n, h, m, r) and the bowl of u
# ---------------------------------------------------------------------------------------------

def arch_geometry(p, x1, C):
    """Heights for one arch that starts at a stem's right edge x1 and spans counter C."""
    k = C / 260.0
    yi = TOP - p.H                                   # inside top of the arch
    a_in = 116.0 * k                                 # how far the inner curve drops to the stem
    ys = yi - a_in                                   # inner curve leaves the stem here
    # the outer curve meets the stem a gap g above that: the inner curve has moved about
    # g*g/(2r) away from the stem there, which is the joint's thickness
    g = 0.915 * math.sqrt(2.0 * a_in * p.J)
    yj_max = TOP - p.H - 10.0 * p.J / 58.0
    if ys + g > yj_max:
        ys = yj_max - g
    return dict(yi=yi, ys=ys, yj=ys + g, k=k, s=p.S / 86.0)


def outer_to_junction(b, xa_out, xj, yj):
    """From the outer top of an arch down to where it meets the stem."""
    drop = TOP - yj
    b.C((xa_out - 0.476 * (xa_out - xj), TOP), (xj + 30.0 * drop / 86.0, yj + 54.0 * drop / 86.0), (xj, yj))


def light(p):
    """0 at Regular and heavier, 1 at Thin."""
    return max(0.0, min(1.0, (86.0 - p.S) / 62.0))


def te(p):
    """Handle length where an arch's side meets a straight stem: longer at light weights, so the
    curve eases into the straight line instead of ending with a visible change."""
    return min(0.85, p.t + 0.22 * light(p))


def arch_inner(p, g, x1, C, Rx, ia=0.546, sh=0.57, h1=None):
    """The inside of one arch: left quarter (stem up to the top) and right quarter (top down to
    the next stem), with the same curvature where they meet."""
    xa_in = x1 + ia * C
    yr = g["yi"] - 0.492 * C
    h1 = (1 - p.t) if h1 is None else h1
    yi = g["yi"]
    A = quad_left(x1, g["ys"], xa_in, yi, sh, h1)
    B = [(xa_in, yi), (xa_in + (p.t - 0.02) * (Rx - xa_in), yi), (Rx, yr + te(p) * (yi - yr)), (Rx, yr)]
    A, B = match_apex(A, B)
    return A, B, xa_in, yr


def outer_right(p, Bin, R2, yro, xa_out):
    """Outside of an arch's right quarter, drawn upwards from the stem to the top."""
    D = [(R2, yro), (R2, yro + te(p) * (TOP - yro)), (xa_out - p.t * (xa_out - R2), TOP), (xa_out, TOP)]
    return mix(D, rev(offset_fit(Bin, p.S, p.H)), light(p))


def glyph_n(p, asc=None):
    L = p.sb; x1 = L + p.S; C = p.Cn; R1 = x1 + C; R2 = R1 + p.S
    g = arch_geometry(p, x1, C); s = g["s"]; lt = light(p)
    A, Bc, xa_in, yr = arch_inner(p, g, x1, C, R1)
    b = B_(L, 0).L(x1, 0).L(x1, g["ys"])
    draw(b, A); draw(b, Bc); b.L(R1, 0).L(R2, 0)
    xa_out = xa_in + 20.0 * s * (1 - lt)
    O = outer_right(p, Bc, R2, yr + 12.0 * s, xa_out)
    b.L(*O[0]); draw(b, O)
    xj = x1 - 6.0 * s if asc is None else x1
    q = outer_left(p, x1, g["ys"], xa_out, xj, 0.57, 1 - p.t, A)
    draw_down(b, q); xj = q[0][0][0]
    if asc is None:
        b.L(xj - 2.0 * s, XH).L(L, XH)
    else:
        b.L(xj, asc).L(L, asc)
    return [b.contour()], round(R2 + p.sb)


def glyph_h(p):
    return glyph_n(p, asc=ASC)


def bez_pt(c, u):
    m = 1 - u
    return tuple(m**3 * c[0][i] + 3*m*m*u * c[1][i] + 3*m*u*u * c[2][i] + u**3 * c[3][i] for i in (0, 1))


def split_upper(c, u):
    """The part of cubic c after parameter u (same shape, fewer points never change)."""
    lerp = lambda a, b: (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
    a, b_, d = lerp(c[0], c[1]), lerp(c[1], c[2]), lerp(c[2], c[3])
    e, f = lerp(a, b_), lerp(b_, d)
    return [lerp(e, f), f, d, c[3]]


def offset_fit(c, S, H, side=1.0, n=24):
    """The curve that runs parallel to cubic c at stroke thickness S across vertical parts and H
    across horizontal parts (side=+1: to the left of c's direction). Fitted as one cubic with the
    same end directions, so the two edges of a stroke stay evenly apart all along."""
    def tan(u):
        m = 1 - u
        d = [3 * (m * m * (c[1][i] - c[0][i]) + 2 * m * u * (c[2][i] - c[1][i]) + u * u * (c[3][i] - c[2][i])) for i in (0, 1)]
        L = math.hypot(*d)
        if L < 1e-9:
            d = [c[3][i] - c[0][i] for i in (0, 1)]; L = math.hypot(*d)
        return d[0] / L, d[1] / L
    def off(u):
        q = bez_pt(c, u); tx, ty = tan(u)
        nx, ny = -ty * side, tx * side
        T = math.sqrt((S * nx) ** 2 + (H * ny) ** 2)
        return q[0] + T * nx, q[1] + T * ny
    P0, P3 = off(0.0), off(1.0)
    t0 = tan(1e-4); t3 = tan(1 - 1e-4)
    # least squares for the two handle lengths a, b:  B(u) = A(u) + a*3m^2u*t0 - b*3mu^2*t3
    saa = sab = sbb = sar = sbr = 0.0
    for k in range(1, n):
        u = k / n; m = 1 - u
        Q = off(u)
        base = [m**3 * P0[i] + 3*m*m*u * P0[i] + 3*m*u*u * P3[i] + u**3 * P3[i] for i in (0, 1)]
        va = [3*m*m*u * t0[i] for i in (0, 1)]; vb = [-3*m*u*u * t3[i] for i in (0, 1)]
        r = [Q[i] - base[i] for i in (0, 1)]
        saa += va[0]**2 + va[1]**2; sbb += vb[0]**2 + vb[1]**2; sab += va[0]*vb[0] + va[1]*vb[1]
        sar += va[0]*r[0] + va[1]*r[1]; sbr += vb[0]*r[0] + vb[1]*r[1]
    det = saa * sbb - sab * sab
    a = (sar * sbb - sbr * sab) / det; b = (saa * sbr - sab * sar) / det
    return [P0, (P0[0] + a * t0[0], P0[1] + a * t0[1]), (P3[0] - b * t3[0], P3[1] - b * t3[1]), P3]


def rev(c):
    return [c[3], c[2], c[1], c[0]]


def mix(D, F, t):
    """Point by point between the designed curve D (t=0) and the even-stroke curve F (t=1)."""
    return [(d[0] + (f[0] - d[0]) * t, d[1] + (f[1] - d[1]) * t) for d, f in zip(D, F)]


def match_apex(A, B):
    """A ends where B starts, smoothly: give both the same curvature there (changes A[2], B[1])."""
    P = A[3]
    ta = (P[0] - A[2][0], P[1] - A[2][1]); la = math.hypot(*ta)
    tb = (B[1][0] - P[0], B[1][1] - P[1]); lb = math.hypot(*tb)
    if la < 1 or lb < 1:
        return A, B
    u = (ta[0] / la, ta[1] / la)
    da = abs((A[1][0] - A[2][0]) * u[1] - (A[1][1] - A[2][1]) * u[0])
    db = abs((B[2][0] - B[1][0]) * u[1] - (B[2][1] - B[1][1]) * u[0])
    if da < 1 or db < 1:
        return A, B
    k = math.sqrt((da / la ** 2) * (db / lb ** 2))
    la2, lb2 = math.sqrt(da / k), math.sqrt(db / k)
    A = [A[0], A[1], (P[0] - u[0] * la2, P[1] - u[1] * la2), P]
    B = [P, (P[0] + u[0] * lb2, P[1] + u[1] * lb2), B[2], B[3]]
    return A, B


def draw(b, c):
    b.C(c[1], c[2], c[3])


MU = 0.18  # how much of the curve eases into the middle stem of m (light weights)
JO = 0.6   # how far the outside of an arch's left curve sits from the inside, in joints (J)


def jo(p):
    """Offset of an arch's outside left curve. Light weights: almost none, so a hairline arch
    leaves its stem tangentially with no visible corner; heavy weights: more, for a firm joint."""
    return JO * p.J * (1 + 0.7 * max(0.0, (p.S - 86.0) / 100.0))


def split_at(c, u):
    lerp = lambda a, b: (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
    a, b_, d = lerp(c[0], c[1]), lerp(c[1], c[2]), lerp(c[2], c[3])
    e, f = lerp(a, b_), lerp(b_, d)
    m = lerp(e, f)
    return [c[0], a, e, m], [m, f, d, c[3]]


def ease_joint(p, seg, u0=0.4):
    """Split off the short piece of a curve next to the joint where it meets a stem (seg[0]).
    Light weights: that piece turns to run along the stem, so the curve flows into the stem
    instead of hitting it at an angle. Regular and heavier keep Admiralty's crisp notch.
    Returns (piece at the joint, rest), both starting at the joint end."""
    end, rest = split_at(seg, u0)
    f = max(0.0, min(1.0, (86.0 - p.S) / 62.0))
    if f > 0:
        x0, y0 = end[0]; hx, hy = end[1][0] - x0, end[1][1] - y0
        L = math.hypot(hx, hy)
        if L > 1e-6:
            a0 = math.atan2(hy, hx); a = a0 + (math.pi / 2 - a0) * f
            end = [end[0], (x0 + L * math.cos(a), y0 + L * math.sin(a)), end[2], end[3]]
    return end, rest


def quad_left(xs, ys, xa, ya, sh, h1):
    """Quarter curve from a stem edge (vertical start) up to an arch top (horizontal end)."""
    return [(xs, ys), (xs, ys + sh * (ya - ys)), (xs + h1 * (xa - xs), ya), (xa, ya)]


def u_at(c, val, axis):
    """Parameter where a monotonic cubic reaches val on the given axis (0 = x, 1 = y)."""
    lo, hi = 0.0, 1.0
    inc = c[3][axis] >= c[0][axis]
    for _ in range(60):
        mid = (lo + hi) / 2
        v = bez_pt(c, mid)[axis]
        if (v < val) == inc: lo = mid
        else: hi = mid
    return (lo + hi) / 2


def draw_down(b, pieces):
    """Draw (piece at the joint, rest) backwards: from the arch top down to the joint."""
    end, rest = pieces
    b.C(rest[2], rest[1], rest[0]); b.C(end[2], end[1], end[0])


def outer_left(p, x1, ys, xa_out, xcut, sh, h1, inner):
    """The outside of an arch's left curve: the inside curve moved out by about a joint's
    thickness; light weights: exactly parallel to the inside at the stroke thickness.
    Cut where it reaches the stem (x = xcut)."""
    q = mix(quad_left(x1 - jo(p), ys, xa_out, TOP, sh, h1), offset_fit(inner, p.S, p.H), light(p))
    if xcut > q[0][0]:
        q = split_upper(q, u_at(q, xcut, 0))
    return ease_joint(p, q)


def glyph_m(p):
    L = p.sb; x1 = L + p.S; C = p.Cn * (236.0 / 260.0)
    Sm = p.S * (84.0 / 86.0)
    M1 = x1 + C; M2 = M1 + Sm; R1 = M2 + C; R2 = R1 + p.S
    g = arch_geometry(p, x1, C); s = g["s"]; lt = light(p)
    A1, B1, xi1, yr = arch_inner(p, g, x1, C, M1, ia=0.551, sh=0.55, h1=0.415)
    A2, B2, xi2, yr = arch_inner(p, g, M2, C, R1, ia=0.551, sh=0.55, h1=0.415)
    b = B_(L, 0).L(x1, 0).L(x1, g["ys"])
    draw(b, A1); draw(b, B1); b.L(M1, 0).L(M2, 0).L(M2, g["ys"])
    draw(b, A2); draw(b, B2); b.L(R1, 0).L(R2, 0)
    xo1 = xi1 + 20.0 * s * (1 - lt); xo2 = xi2 + 20.0 * s * (1 - lt)
    O = outer_right(p, B2, R2, yr + 12.0 * s, xo2)
    b.L(*O[0]); draw(b, O)
    # the first arch's right shoulder (outside parallel to inside), cut where the second arch's
    # outer curve meets the middle stem
    q0 = (M2, yr + 12.0 * s); q3 = (xo1, TOP)
    tq = min(p.t + 0.16 * max(0.0, min(1.0, (s - 0.28) / 0.72)), 0.80)
    seg = mix([q0, (M2, q0[1] + tq * (TOP - q0[1])), (xo1 + tq * (M2 - xo1), TOP), q3], rev(offset_fit(B1, p.S, p.H)), lt)
    # second arch's outside left curve; the joint is where it crosses the first arch's shoulder
    q2 = mix(quad_left(M2 - jo(p), g["ys"], xo2, TOP, 0.55, 0.415), offset_fit(A2, p.S, p.H), lt)
    lo, hi = max(seg[0][1], q2[0][1]) + 0.5, TOP - 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if bez_pt(q2, u_at(q2, mid, 1))[0] < bez_pt(seg, u_at(seg, mid, 1))[0]: lo = mid
        else: hi = mid
    yjm = (lo + hi) / 2
    q2 = ease_joint(p, split_upper(q2, u_at(q2, yjm, 1)), MU); seg = ease_joint(p, split_upper(seg, u_at(seg, yjm, 1)), MU)
    draw_down(b, q2)
    b.C(seg[0][1], seg[0][2], seg[0][3]); b.C(seg[1][1], seg[1][2], seg[1][3])
    q1 = outer_left(p, x1, g["ys"], xo1, x1 - 6.0 * s, 0.55, 0.415, A1)
    draw_down(b, q1); xj = q1[0][0][0]
    b.L(xj - 2.0 * s, XH).L(L, XH)
    return [b.contour()], round(R2 + p.sb)


def glyph_u(p):
    # u is the n turned upside down: bowl at the bottom, joint on the right stem
    import copy
    q = copy.copy(p); q.Cn = p.Cn * (252.0 / 260.0)
    cs, adv = glyph_n(q)
    return [[(adv - x, (XH) - y, t) for x, y, t in c] for c in cs], adv


def glyph_r(p):
    L = p.sb; x1 = L + p.S
    arm = 170.0 * p.wf ** 1.12 * (1 + 0.15 * (p.S - 86) / 86)      # arm reaches a little further when heavy
    k = arm / 170.0
    yi = TOP - p.H
    g = arch_geometry(p, x1, 260.0 * k)
    ys = g["ys"]
    xe = x1 + arm                                    # end of the arm
    xa_in = x1 + 126.0 * k; xa_out = x1 + 122.0 * k + (4.0 * k) * light(p)
    b = B_(L, 0).L(x1, 0).L(x1, ys)
    A = quad_left(x1, ys, xa_in, yi, 0.62, 0.43)
    draw(b, A)
    b.C((xa_in + 0.41 * (xe - xa_in), yi), (xe - 0.27 * (xe - xa_in), yi - 4.0), (xe, yi - 10.0))
    b.L(xe + 16.0 * k, TOP - 14.0)
    b.C((xe - 2.0 * k, TOP - 4.0), (xa_out + 0.37 * (xe - xa_out), TOP), (xa_out, TOP))
    q = outer_left(p, x1, ys, xa_out, x1 - 6.0 * p.S / 86.0, 0.62, 0.43, A)
    draw_down(b, q); xj = q[0][0][0]
    b.L(xj - 2.0 * p.S / 86.0, XH).L(L, XH)
    return [b.contour()], round(xe + 20.0 * k + p.sb * 0.21)


def glyph_o(p):
    sb = 54.0 * p.wf ** 0.7 * (p.sb / 76.0)
    rxi = 146.0 * p.Cn / 260.0                  # inside: as wide as the other counters
    rx = rxi + p.B
    ry = 260.0 + OV
    cx = sb + rx
    outer = oval(cx, 260, rx, ry, p.to)
    inner = oval(cx, 260, rx - p.B, ry - p.H, p.ti, cw=True)
    lt = light(p)
    if lt > 0:
        # outer runs counter-clockwise; its inside parallel is to its left... ink is between, so
        # the inner edge is the outer moved inwards (to the left of a counter-clockwise outline)
        segs = [[outer[i][:2] for i in range(k, k + 4)] for k in (0, 3, 6)] + [[outer[9][:2], outer[10][:2], outer[11][:2], outer[0][:2]]]
        fit = [rev(offset_fit(c, p.B, p.H)) for c in segs][::-1]
        pts = [fit[0][0]]
        for c in fit:
            pts += [c[1], c[2], c[3]]
        pts = pts[:-1]
        inner = [(x + (fx - x) * lt, y + (fy - y) * lt, t) for (x, y, t), (fx, fy) in zip(inner, pts)]
    return [outer, inner], round(2 * cx)


def glyph_i(p):
    x0 = 80.0 * p.wf ** 0.7 * (p.sb / 76.0); x1 = x0 + p.S
    stem = B_(x0, 0).L(x1, 0).L(x1, XH).L(x0, XH).contour()
    r = 50.0 * (p.S / 86.0) ** 0.55
    cy = 656.0 + (r - 50.0) * 0.3
    dot = oval((x0 + x1) / 2, cy, r, r, 0.62)
    return [stem, dot], round(x1 + x0)


def glyph_l(p):
    """Stem that turns into a short tail on the baseline; the inside and outside of the turn
    stay a stroke apart at every weight."""
    s = p.S / 86.0
    x0 = 74.0 * p.wf ** 0.7 * (p.sb / 76.0); x1 = x0 + p.S
    tail = 60.0 * p.wf ** 0.9 * (1 + 0.3 * max(0.0, (p.S - 86) / 86)) * (1 + 0.25 * light(p))
    xt = x1 + tail
    th = p.H - 8.0                                     # tail top: the bar (from the -8 overshoot) is as thick as other bars
    ri = 56.0 * p.wf ** 0.5 * (1 + 0.3 * light(p))                           # inside turn: height
    yi_top = th + ri                                   # inside turn leaves the stem here
    # light weights: the outside of the turn runs parallel to the inside (an even hairline);
    # from Regular up it is Admiralty's tighter outside turn that makes the foot taper
    lt = max(0.0, min(1.0, (86.0 - p.S) / 62.0))
    yo_top = yi_top - 20.0 * s * (1 - lt)              # outside turn leaves the stem here
    xb = (1 - lt) * (x1 + 2.0 * s) + lt * (x0 + 0.85 * (xt - x0))      # outside turn reaches the bottom here
    I = [(xt, th), (xt - 0.6 * tail, th), (x1, th + (0.29 + 0.3 * lt) * ri), (x1, yi_top)]
    # designed outside: the turn (stem down to the bottom), then the bottom rising to the tip
    Dturn = [(x0, yo_top), (x0, -8.0 + (0.4 + 0.2 * lt) * (yo_top + 8.0)), (x0 + (0.4 + 0.15 * lt) * (xb - x0), -8.0), (xb, -8.0)]
    Dtail = [(xb, -8.0), (xb + 0.34 * (xt - xb), -8.0), (xb + 0.69 * (xt - xb), -5.0), (xt, 0.0)]
    # even-stroke outside: the inside turn moved out by the stroke, split in the same two parts
    F = rev(offset_fit(I, p.S, p.H))
    Fturn, Ftail = split_at(F, 0.85)
    turn, tl = mix(Dturn, Fturn, lt), mix(Dtail, Ftail, lt)
    b = B_(*tl[0]); draw(b, tl); b.L(xt, th)
    draw(b, I)
    b.L(x1, ASC).L(x0, ASC).L(*turn[0]); draw(b, turn)
    return [b.contour()], round(xt + 36.0 * p.wf ** 0.7)


GLYPHS = {"n": glyph_n, "h": glyph_h, "m": glyph_m, "u": glyph_u, "r": glyph_r, "o": glyph_o, "i": glyph_i, "l": glyph_l}


def build(OUT):
    OUT = Path(OUT); OUT.mkdir(parents=True, exist_ok=True)
    ds = DesignSpaceDocument()
    for tag, nm, lo, de, hi in (("wght", "Weight", 100, 400, 900), ("wdth", "Width", 65, 100, 150)):
        a = AxisDescriptor(); a.tag, a.name, a.minimum, a.default, a.maximum = tag, nm, lo, de, hi
        ds.addAxis(a)
    for w in WEIGHTS:
        for d in WIDTHS:
            p = P(w, d)
            u = ufoLib2.Font()
            u.info.familyName = "Admiralty Pilot"; u.info.styleName = f"w{w} d{d}"
            u.info.unitsPerEm = 1000; u.info.ascender = 740; u.info.descender = -220
            u.info.xHeight = 520; u.info.capHeight = 700
            g = u.newGlyph(".notdef"); g.width = 500
            sp = u.newGlyph("space"); sp.width = round(240 * d / 100); sp.unicodes = [32]
            for name, fn in GLYPHS.items():
                cs, adv = fn(p)
                gl = u.newGlyph(name); gl.width = adv; gl.unicodes = [ord(name)] if len(name) == 1 else []
                pen = gl.getPointPen()
                for c in cs:
                    pen.beginPath()
                    for x, y, seg in c:
                        pen.addPoint((round(x, 1), round(y, 1)), segmentType=seg)
                    pen.endPath()
            path = OUT / f"pilot-w{w}-d{d}.ufo"
            u.save(path, overwrite=True)
            s = SourceDescriptor(); s.path = str(path); s.font = u; s.location = {"Weight": w, "Width": d}
            ds.addSource(s)
    vf = ufo2ft.compileVariableTTF(ds, optimizeGvar=True)
    vf.save(OUT / "AdmiraltyPilot.ttf")
    print("pilot VF ->", OUT / "AdmiraltyPilot.ttf")


if __name__ == "__main__":
    build(sys.argv[1])
