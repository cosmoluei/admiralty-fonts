import pathlib
SOURCES = str(pathlib.Path(__file__).resolve().parents[2] / "sources")
"""Full-range Sans lowercase, group 1 (continued): a and s.

These two are drawn by stroking: the edges that face a counter (the white inside) are placed
from measurements, and every other edge is worked out from them at the stroke thickness of the
master. Today's Regular is then matched exactly by carrying its small design differences
(contrast, terminal angles) over to the other masters; at Thin they fade out, so Thin is one
even line.
"""
import math
import ufoLib2
import pilot as P0
from pilot import offset_fit, rev, light, split_at, u_at
from group1 import kc, ks

REG = ufoLib2.Font.open(SOURCES + "/AdmiraltySans-Regular.ufo")
BOLD = ufoLib2.Font.open(SOURCES + "/AdmiraltySans-Bold.ufo")


def pw(keys):
    """Piecewise-linear map through (old, new) pairs, extended at both ends."""
    keys = sorted(keys)
    def f(v, keys=keys):
        for (a0, b0), (a1, b1) in zip(keys, keys[1:]):
            if v <= a1 or (a1, b1) == keys[-1]:
                if v < a0 and (a0, b0) != keys[0]:
                    continue
                return b0 + (v - a0) * (b1 - b0) / (a1 - a0)
        return v
    f.keys = keys
    return f


def mapc(c, fx, fy):
    return [(fx(x), fy(y)) for x, y in c]


def rot_end(c, target, f):
    """Turn the handle at c's end point towards the direction target (radians), by f (0..1)."""
    if f <= 0:
        return c
    x3, y3 = c[3]; hx, hy = c[2][0] - x3, c[2][1] - y3
    L = math.hypot(hx, hy)
    if L < 1e-6:
        return c
    a0 = math.atan2(hy, hx)
    d = (target - a0 + math.pi) % (2 * math.pi) - math.pi
    a = a0 + d * f
    return [c[0], c[1], (x3 + L * math.cos(a), y3 + L * math.sin(a)), c[3]]


class Path:
    """Collects one closed contour as (x, y, type) points."""
    def __init__(self, start):
        self.pts = [(start[0], start[1], "line")]
    def L(self, pt):
        self.pts.append((pt[0], pt[1], "line")); return self
    def C(self, c):
        self.pts += [(c[1][0], c[1][1], None), (c[2][0], c[2][1], None), (c[3][0], c[3][1], "curve")]; return self
    def done(self):
        pts = self.pts
        if abs(pts[-1][0] - pts[0][0]) < 1e-6 and abs(pts[-1][1] - pts[0][1]) < 1e-6:
            t = pts[-1][2]; pts = pts[:-1]; pts[0] = (pts[0][0], pts[0][1], t)
        return pts


def ufo_contours(name, font=None):
    return [[(pt.x, pt.y, pt.segmentType) for pt in font_or(font)[name].contours] for c in [0]][0] if False else \
        [[(pt.x, pt.y, pt.segmentType) for pt in c] for c in (font or REG)[name].contours]


def align(mine, ref):
    """Rotate ref so its points line up with mine (same structure, any start point)."""
    n = len(ref)
    assert n == len(mine), (n, len(mine))
    best = None
    for k in range(n):
        r = ref[k:] + ref[:k]
        if any((a[2] is None) != (b[2] is None) for a, b in zip(mine, r)):
            continue
        d = sum((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 for a, b in zip(mine, r))
        if best is None or d < best[0]:
            best = (d, r)
    return best[1]


_REF = {}


def with_residual(name, build, p):
    """build(p) -> (contours, fx, fy). Light weights: the stroked drawing (outside edges worked
    out from the inside ones), with today's Regular design differences fading out towards Thin.
    Regular and heavier: today's Regular outline placed by the same measurements (fx, fy move
    every point to where its stem, bar or counter edge now is), so heavy shapes keep their design.
    Both have the same points, so they blend smoothly."""
    cs, fx, fy = build(p)
    if name not in _REF:
        reg, _, _ = build(P0.P(400, 100))
        ref = ufo_contours(name)
        al = []
        for m in reg:
            cand = [r for r in ref if len(r) == len(m)]
            r = align(m, cand[0]) if len(cand) == 1 else align(m, min(cand, key=lambda r: abs(r[0][0] - m[0][0])))
            al.append(r)
        # today's Bold has the same points in the same order: line it up the same way
        bref = ufo_contours(name, BOLD)
        bal = []
        for r in al:
            ri = ref.index(next(c for c in ref if len(c) == len(r) and set(map(tuple, c)) == set(map(tuple, r))))
            k0 = ref[ri].index(r[0])
            bc = bref[ri]
            bal.append(bc[k0:] + bc[:k0])
        _REF[name] = (reg, al, bal)
    reg, al, bal = _REF[name]
    # map for Bold: the same measurement points, read from Bold
    def bold_map(f, axis):
        new = []
        for old, tgt in f.keys:
            for c, bc in zip(al, bal):
                hit = next((b for a, b in zip(c, bc) if abs(a[axis] - old) < 0.5), None)
                if hit is not None:
                    new.append((hit[axis], tgt)); break
        return pw(new)
    bfx, bfy = bold_map(fx, 0), bold_map(fy, 1)
    tb = max(0.0, min(1.0, (p.S - 86.0) / 48.0))
    lt = light(p); k = kc(p) ** 0.5
    out = []
    for c, m, r, bb in zip(cs, reg, al, bal):
        cc = []
        for (x, y, t), (mx, my_, _), (rx, ry, _), (bx, by, _) in zip(c, m, r, bb):
            xo = x + (rx - mx) * (1 - lt) * k; yo = y + (ry - my_) * (1 - lt)   # stroked + residual
            xm, ym = fx(rx), fy(ry)                                            # placed Regular
            if tb > 0:                                                         # heavier: placed Bold
                xm += (bfx(bx) - xm) * tb; ym += (bfy(by) - ym) * tb
            cc.append((xm + (xo - xm) * lt, ym + (yo - ym) * lt, t))
        out.append(cc)
    return out


# ---------------------------------------------------------------------------------------------
# a
# ---------------------------------------------------------------------------------------------

def build_a(p):
    s = p.S / 86.0; lt = light(p); k = kc(p)
    rS, rB, rH, rJ = p.S / 86.0, p.B / 90.0, p.H / 74.0, p.J / 58.0
    xl = 54.0 * ks(p); xli = xl + 86.0 * rB
    x_sl = xli + 250.0 * k; x_sr = x_sl + 84.0 * rS
    fx = pw([(54, xl), (140, xli), (390, x_sl), (474, x_sr)])
    y_bt = 304.0 + 0.5 * max(0.0, p.H - 74.0)              # outside top of the bowl (heavy: higher, the bowl stays open)
    rJ = rJ if rJ <= 1 else rJ ** 0.8
    fy = pw([(-10, -10), (58, -10 + 68 * rH), (246, y_bt - 58 * rJ), (304, y_bt), (458, 530 - 72 * rH), (530, 530)])
    M = lambda c: mapc(c, fx, fy)
    # inside edges (Regular), mapped
    Ib1 = M([(390, 246), (264, 244), (140, 206), (140, 138)])       # bowl top, from the stem leftwards
    Ib2 = M([(140, 138), (140, 92), (177, 58), (228, 58)])          # bowl left and bottom
    Ib3 = M([(228, 58), (322, 58), (390, 96), (390, 146)])          # bowl bottom up into the stem
    Itl = M([(121, 418), (160, 443), (207, 458), (260, 458)])       # arch inside, from the terminal
    Ish = M([(260, 458), (333, 458), (390, 408), (390, 346)])       # arch inside, down to the stem
    tiny = M([(110, 410), (114, 413), (117, 415), (121, 418)])
    for c in (Ib1, Ish, Ib3):
        pass
    Ib1[0] = (x_sl, Ib1[0][1]); Ish[3] = (x_sl, Ish[3][1]); Ib3[3] = (x_sl, Ib3[3][1])
    # outside edges, worked out from the inside ones
    O1 = rev(offset_fit(rev(Ib1), 86.0 * rB, 58.0 * rJ, side=-1.0))   # stem -> bowl left (reversed back)
    O1 = offset_fit(Ib1, 86.0 * rB, 58.0 * rJ, side=-1.0)
    O2 = offset_fit(Ib2, 86.0 * rB, 68.0 * rH, side=-1.0)
    O3f = offset_fit(Ib3, 86.0 * rB, 68.0 * rH, side=-1.0)
    xcut = x_sl + 6.0 * s
    O3c = split_at(O3f, u_at(O3f, xcut, 0))[0] if O3f[3][0] > xcut else O3f
    O3, Oj = split_at(O3c, 0.92)
    Oj = rot_end(Oj, -math.pi / 2, lt)                     # light: the bowl flows into the stem
    OTR = offset_fit(rev(Ish), 84.0 * rS, 72.0 * rH, side=-1.0)    # stem -> arch top
    OTL = offset_fit(rev(Itl), 86.0 * rS, 72.0 * rH, side=-1.0)    # arch top -> terminal
    O1[0] = (x_sl, O1[0][1])
    OTR[0] = (x_sr, OTR[0][1])
    pa = Path(O2[3])
    pa.C(O3).C(Oj).L((Oj[3][0] + 2.0 * s, 0.0)).L((x_sr, 0.0)).L(OTR[0]).C(OTR).C(OTL)
    pa.L(tiny[0]).C(tiny).C(Itl).C(Ish).L(O1[0]).C(O1).C(O2)
    outer = pa.done()
    pi = Path(Ib2[3])
    pi.C(Ib3).L(Ib1[0]).C(Ib1).C(Ib2)
    inner = pi.done()
    # the inside of the bowl runs the other way (it is a counter)
    from group1 import reverse_contour
    return [outer, reverse_contour(inner)], fx, fy


def glyph_a(p):
    cs = with_residual("a", build_a, p)
    x_sr = max(x for c in cs for x, y, t in c)
    return cs, round(x_sr + 74.0 * ks(p))


# ---------------------------------------------------------------------------------------------
# s
# ---------------------------------------------------------------------------------------------

def build_s(p):
    lt = light(p); k = kc(p)
    rS, rB, rH = p.S / 86.0, p.B / 90.0, p.H / 74.0
    if rH > 1:
        rH = rH ** 0.85                                     # heavy s: lighter curves, so the counters stay open
    rSp = rS ** 0.95 if rS > 1 else rH                       # spine (heavy: as strong as a stem)
    xl = 60.0 * ks(p); xli = xl + 82.0 * rS
    xri = xli + 196.0 * k; xr = xri + 84.0 * rS
    fx = pw([(60, xl), (142, xli), (338, xri), (422, xr)])
    yc = 262.0
    fy = pw([(-10, -10), (60, -10 + 70 * rH), (219, yc - 43 * rSp), (305, yc + 43 * rSp), (460, 530 - 70 * rH), (530, 530)])
    M = lambda c: mapc(c, fx, fy)
    A3 = M([(242, 305), (168, 324), (142, 348), (142, 386)])
    A4 = M([(142, 386), (142, 429), (185, 460), (244, 460)])
    A5 = M([(244, 460), (298, 460), (344, 442), (380, 414)])
    B4 = M([(242, 219), (316, 200), (338, 176), (338, 138)])
    B5 = M([(338, 138), (338, 93), (292, 60), (228, 60)])
    B6 = M([(228, 60), (164, 60), (114, 80), (76, 112)])
    tS, tH, tSp = 84.0 * rS, 70.0 * rH, 86.0 * rSp
    B3 = rev(offset_fit(A3, tS, tSp))
    B2 = rev(offset_fit(A4, tS, tH))
    B1 = rev(offset_fit(A5, tS, tH))
    A2 = rev(offset_fit(B4, tS, tSp))
    A1 = rev(offset_fit(B5, tS, tH))
    B7 = rev(offset_fit(B6, tS, tH))
    A2[3] = A3[0]; B3[3] = B4[0]
    path = Path(A1[0])
    path.C(A1).C(A2).C(A3).C(A4).C(A5).L(B1[0]).C(B1).C(B2).C(B3).C(B4).C(B5).C(B6).L(B7[0]).C(B7)
    return [path.done()], fx, fy


def glyph_s(p):
    cs = with_residual("s", build_s, p)
    xr = max(x for c in cs for x, y, t in c)
    return cs, round(xr + 46.0 * ks(p))


P0.GLYPHS.update({"a": glyph_a, "s": glyph_s})
