"""Full-range Sans lowercase, group 1: the bowl letters b d p q g, and c e (o is in pilot.py).

Same method as the pilot: every master is drawn from measurements (stem S, bar H, bowl B,
joint J, counter and sidebearing scales), Regular reproduces today's design, and at light
weights every outside edge is worked out from its inside edge so Thin is one even line.
"""
import math
from fontTools.pens.recordingPen import RecordingPointPen
from fontTools.pens.pointPen import ReverseContourPointPen
import pilot as P0
from pilot import (B_, TOP, BOT, XH, ASC, quad_left, offset_fit, rev, mix, match_apex, draw,
                   draw_down, outer_left, light, jo, split_at, split_upper, bez_pt, u_at)

CY = 260.0
DESC = -220.0


def kc(p):
    """How much the counters grow or shrink against Regular (weight and width)."""
    return p.Cn / 260.0


def ks(p):
    """Sidebearing scale against Regular."""
    return p.sb / 76.0


def quarter(p0, p3, first, t0, t1):
    """Quarter curve. first='h': leaves p0 horizontally, arrives at p3 vertically; 'v': the other way."""
    (x0, y0), (x3, y3) = p0, p3
    if first == "h":
        return [p0, (x0 + t0 * (x3 - x0), y0), (x3, y3 - t1 * (y3 - y0)), p3]
    return [p0, (x0, y0 + t0 * (y3 - y0)), (x3 - t1 * (x3 - x0), y3), p3]


def my(c, ay=CY):
    return [(x, 2 * ay - y) for x, y in c]


def reverse_contour(pts):
    rec = RecordingPointPen()
    pen = ReverseContourPointPen(rec)
    pen.beginPath()
    for x, y, t in pts:
        pen.addPoint((x, y), segmentType=t)
    pen.endPath()
    rec2 = RecordingPointPen(); rec.replay(rec2)
    out = []
    for op, args, kw in rec.value:
        if op == "addPoint":
            pt = args[0]; t = args[1] if len(args) > 1 else kw.get("segmentType")
            out.append((pt[0], pt[1], t))
    return out


def flip(cs, adv=None, fx=False, fy=False, ay=CY):
    """Mirror contours left-right (about the advance) and/or up-down (about ay)."""
    out = []
    for c in cs:
        c2 = [((adv - x) if fx else x, (2 * ay - y) if fy else y, t) for x, y, t in c]
        if fx != fy:
            c2 = reverse_contour(c2)
        out.append(c2)
    return out


# ---------------------------------------------------------------------------------------------
# b d p q g
# ---------------------------------------------------------------------------------------------

def bowl_b(p, hook=False):
    """b: stem on the left with an ascender, bowl to the right. Top joint: the stem goes on up;
    bottom joint: a short spur on the baseline (as in n)."""
    s = p.S / 86.0; lt = light(p); k = kc(p)
    L = 74.0 * ks(p); x1 = L + p.S
    Cb = 272.0 * k
    xr_in = x1 + Cb; xr_out = xr_in + p.B
    yi = TOP - p.H
    xa_in = x1 + 0.544 * Cb; xa_out = xa_in + 16.0 * s * (1 - lt)
    # where the inside leaves the stem; the joint stays thick enough (same rule as n)
    a_in = 126.0 * Cb / 272.0
    ys = yi - a_in
    g = 0.915 * math.sqrt(2.0 * a_in * p.J)
    yj_max = yi - 10.0 * p.J / 58.0
    if ys + g > yj_max:
        ys = yj_max - g
    ys = max(ys, CY + 6.0)
    A = quad_left(x1, ys, xa_in, yi, 0.556, 0.44)
    R = quarter((xa_in, yi), (xr_in, CY), "h", p.ti - 0.015, p.ti)
    A, R = match_apex(A, R)
    OR = mix(quarter((xr_out, CY), (xa_out, TOP), "v", p.to, p.to), rev(offset_fit(R, p.B, p.H)), lt)
    OLt = outer_left(p, x1, ys, xa_out, x1, 0.556, 0.44, A)               # top: stem goes on up
    OLb = outer_left(p, x1, ys, xa_out, x1 - 6.0 * s, 0.556, 0.44, A)     # bottom: spur (mirrored)
    end_b, rest_b = my(OLb[0]), my(OLb[1])
    jb = end_b[0]
    b = B_(jb[0] - 2.0 * s, 0.0).L(*jb)
    draw(b, end_b); draw(b, rest_b)
    draw(b, rev(my(OR))); draw(b, OR)
    draw_down(b, OLt); jt = OLt[0][0]
    b.L(jt[0], ASC).L(L, ASC).L(L, 0.0)
    outer = b.contour()
    Ab, Rb = my(A), my(R)
    c = B_(*Ab[3])
    draw(c, rev(Ab)); c.L(x1, ys); draw(c, A); draw(c, R); draw(c, rev(Rb))
    inner = c.contour()
    return [outer, inner], round(xr_out + 54.0 * ks(p))


def glyph_b(p):
    return bowl_b(p)


def glyph_d(p):
    cs, adv = bowl_b(p)
    return flip(cs, adv, fx=True), adv


def glyph_p(p):
    cs, adv = bowl_b(p)
    return flip(cs, adv, fy=True, ay=(ASC + DESC) / 2.0 if False else 260.0), adv


def glyph_q(p):
    cs, adv = bowl_b(p)
    return flip(cs, adv, fx=True, fy=True), adv


def glyph_g(p):
    """g: the bowl of q with a hook instead of the straight descender."""
    cs, adv = glyph_q(p)
    outer = cs[0]
    lows = [i for i, (x, y, t) in enumerate(outer) if abs(y - DESC) < 0.5]
    assert len(lows) == 2, lows
    i0, i1 = lows
    x_in, x_out = outer[i0][0], outer[i1][0]
    if x_in > x_out:
        x_in, x_out = x_out, x_in
    s = p.S / 86.0; lt = light(p); k = kc(p) ** 0.6     # the hook grows less than the counters
    Hh = p.H if p.H <= 74 else 74.0 + 0.6 * (p.H - 74.0)   # hook bottom (lighter when heavy: room to turn)
    yb_out = -224.0; yb_in = yb_out + Hh
    y_top = -20.0                                 # the stem turns into the hook here
    xa = x_in - 158.0 * k                         # lowest point of the hook (inside)
    # inside: down the stem's inner edge, round the bottom, out to the terminal
    I1 = [(x_in, y_top), (x_in, y_top - 0.585 * (y_top - yb_in)), (xa + 0.42 * (x_in - xa), yb_in), (xa, yb_in)]
    t_in = (xa - 144.0 * k, yb_in + 32.0 * (Hh / 74.0) ** 0.3)
    I2 = [(xa, yb_in), (xa - 60.0 * k, yb_in), (xa - 108.0 * k, yb_in + 12.0), t_in]
    I1, I2 = match_apex(I1, I2)
    # outside, designed (Regular) and even-stroke (light weights)
    t_out_d = (t_in[0] - 24.0 * k, yb_out + 40.0)
    xa_o = xa + 6.0 * k
    O2d = [t_out_d, (t_out_d[0] + 50.0 * k, yb_out + 12.0), (xa_o - 66.0 * k, yb_out), (xa_o, yb_out)]
    O1d = [(xa_o, yb_out), (xa_o + 140.0 * k, yb_out), (x_out, -141.0 + 0.0 * s), (x_out, -22.0)]
    O2 = mix(O2d, rev(offset_fit(I2, p.S, Hh)), lt)
    O1 = mix(O1d, rev(offset_fit(I1, p.S, Hh)), lt)
    O1[3] = (x_out, O1[3][1])
    hook = [(x_in, y_top, "line")]
    for c in (I1, I2):
        hook += [(c[1][0], c[1][1], None), (c[2][0], c[2][1], None), (c[3][0], c[3][1], "curve")]
    hook.append((O2[0][0], O2[0][1], "line"))
    for c in (O2, O1):
        hook += [(c[1][0], c[1][1], None), (c[2][0], c[2][1], None), (c[3][0], c[3][1], "curve")]
    # in q's outline the stem runs down its inner edge first, then back up its outer edge
    if outer[i0][0] < outer[i1][0]:
        new = outer[:i0] + hook + outer[i1 + 1:]
    else:
        raise RuntimeError("unexpected g order")
    cs[0] = new
    return cs, round(adv - 4.0 * ks(p))


# ---------------------------------------------------------------------------------------------
# c e
# ---------------------------------------------------------------------------------------------

def round_open(p, top_end, bot_end):
    """The shared shape of c and e: outer and inner oval with terminals. Returns the pieces."""
    s = p.S / 86.0; lt = light(p); k = kc(p)
    xl_out = 54.0 * ks(p); xl_in = xl_out + p.B
    yi, yb = TOP - p.H, BOT + p.H
    xa_in = xl_in + 144.0 * k; xa_out = xa_in - 2.0 * s * (1 - lt)
    fy = (yi - CY) / 198.0
    # inside, left half (virtual oval quarters)
    ITL = quarter((xa_in, yi), (xl_in, CY), "h", 0.59, 0.60)        # top apex to left extreme
    IBL = my(ITL)                                                   # bottom apex to left extreme
    OTL = mix(quarter((xa_out, TOP), (xl_out, CY), "h", p.to, p.to), offset_fit(ITL, p.B, p.H, side=-1.0), lt)
    OBL = my(OTL)
    return dict(s=s, lt=lt, k=k, xl_out=xl_out, xl_in=xl_in, yi=yi, yb=yb, xa_in=xa_in, xa_out=xa_out,
                fy=fy, ITL=ITL, IBL=IBL, OTL=OTL, OBL=OBL)


def terminal(p, apex_in, apex_out, k, fy, d_end, h_in, h_out, sign, lt):
    """A terminal piece of c or e: inside from the apex to the cut, outside from the cut back to
    its apex. d_end: inside end relative to the apex; sign +1 top, -1 bottom."""
    xa, ya = apex_in
    e_in = (xa + d_end[0] * k, ya - sign * d_end[1] * fy)
    I = [apex_in, (xa + h_in[0] * k, ya), (xa + h_in[1][0] * k, ya - sign * h_in[1][1] * fy), e_in]
    e_out = (e_in[0] + 0.6 * p.B, e_in[1] + sign * 0.73 * p.H)
    Od = [e_out, (e_out[0] - h_out[0] * k, e_out[1] + sign * h_out[1] * fy), (apex_out[0] + h_out[2] * k, apex_out[1]), apex_out]
    side = 1.0 if sign > 0 else -1.0
    O = mix(Od, rev(offset_fit(I, p.B, p.H, side=side)), lt)
    return I, O


def glyph_c(p):
    r = round_open(p, None, None)
    k, fy, lt = r["k"], r["fy"], r["lt"]
    It, Ot = terminal(p, (r["xa_in"], r["yi"]), (r["xa_out"], TOP), k, fy, (122.0, 68.0),
                      (50.0, (92.0, 24.0)), (40.0, 56.0, 78.0), +1, lt)
    Ib, Ob = terminal(p, (r["xa_in"], r["yb"]), (r["xa_out"], BOT), k, fy, (126.0, 74.0),
                      (50.0, (94.0, 26.0)), (40.0, 60.0, 80.0), -1, lt)
    # outline: outer bottom apex -> bottom terminal -> inner -> top terminal -> outer top -> left
    b = B_(*rev(Ob)[0])
    draw(b, rev(Ob)); b.L(*Ib[3])
    draw(b, rev(Ib)); draw(b, r["IBL"]); draw(b, rev(r["ITL"])); draw(b, It)
    b.L(*Ot[0]); draw(b, Ot); draw(b, r["OTL"]); draw(b, rev(r["OBL"]))
    cs = [b.contour()]
    adv = max(Ob[0][0], Ot[0][0]) + 34.0 * ks(p)
    return cs, round(adv)


def glyph_e(p):
    r = round_open(p, None, None)
    k, fy, lt, s = r["k"], r["fy"], r["lt"], r["s"]
    xl_out, xl_in = r["xl_out"], r["xl_in"]
    xr_in = xl_in + 268.0 * k                      # the eye is as wide as the other counters
    xr_out = xr_in + p.S
    hb = 66.0 * (p.H / 74.0) ** (1.0 if p.H < 74 else 0.6)      # bar (a little lighter when heavy)
    yc = 269.0 - 0.4 * max(0.0, p.H - 74.0)                       # heavy: bar lower, the eye stays open
    yb_bot = yc - hb / 2.0; yb_top = yc + hb / 2.0
    yi = r["yi"]
    xe = r["xa_in"] - 8.0 * k                      # eye top (inside)
    # eye: left part follows the virtual inner oval, cut at the bar
    ITL = r["ITL"]
    Eleft = rev(split_upper(rev(ITL), u_at(rev(ITL), yb_top, 1)))   # from eye top down to the bar
    Eleft = [(xe, yi)] + Eleft[1:] if False else Eleft
    Eright = quarter((Eleft[0][0], yi), (xr_in, yb_top), "h", 0.55, 0.62)
    Eleft_up = rev(Eleft)                          # from the bar up to the eye top
    Eleft_up, Eright = match_apex(Eleft_up, Eright)
    # outer shoulder (eye's right side), designed and even-stroke
    ORd = [(xr_out, yb_top - 24.0 * (1 - lt)), (xr_out, 424.0 - (530.0 - TOP)), (xr_out - 0.43 * (xr_out - Eleft[0][0]) * 1.0, TOP), (Eleft[0][0] + 2.0 * k, TOP)]
    ORf = rev(offset_fit(Eright, p.S, p.H))
    OR = mix(ORd, ORf, lt)
    # outer top-left: from the eye top's outside to the left extreme
    OTL = list(r["OTL"]); OTL[0] = OR[3]
    # bottom: inner from the terminal to the bar (follows the virtual inner oval)
    Ib, Ob = terminal(p, (r["xa_in"] + 4.0 * k, r["yb"]), (r["xa_out"] + 2.0 * k, BOT), k, fy, (144.0, 84.0),
                      (56.0, (106.0, 30.0)), (40.0, 64.0, 88.0), -1, lt)
    IBL = r["IBL"]; IBL = [Ib[0]] + IBL[1:]
    Ibar = split_at(IBL, u_at(IBL, yb_bot, 1))[0]          # bottom apex to the bar
    b = B_(*rev(Ob)[0])
    draw(b, rev(Ob)); b.L(*Ib[3]); draw(b, rev(Ib)); draw(b, Ibar)
    b.L(xr_out, yb_bot).L(*OR[0]); draw(b, OR); draw(b, OTL); draw(b, rev(r["OBL"]))
    outer = b.contour()
    c = B_(*Eleft[3])
    draw(c, Eleft_up); draw(c, Eright)
    eye = c.contour()
    return [outer, eye], round(xr_out + 54.0 * ks(p))


GROUP1 = {"b": glyph_b, "d": glyph_d, "p": glyph_p, "q": glyph_q, "g": glyph_g, "c": glyph_c, "e": glyph_e}
P0.GLYPHS.update(GROUP1)
