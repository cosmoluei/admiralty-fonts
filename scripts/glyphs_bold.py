"""
Milestone 6 Bold (Weight 700) Glyph Builders for:
  - Admiralty Sans Bold (1:1 duplexed advance widths with Serif Bold)
  - Admiralty Serif Bold (calligraphic contrast ~2.3:1, 146-160u stems / 58-72u hairlines)
  - Admiralty Mono Bold (strict 600u fixed pitch, 108-118u stems, 88u ss01 ligatures)

Uses a smooth cosine-blended, metric-pinned anisotropic miter offset engine paired
with explicit hand-tuned builders for acute counters, multi-bowl ligatures, Serif
calligraphic contrast letters, and dense 600u Mono glyphs.
"""

from __future__ import annotations
import math
from typing import Callable, Dict, List, Tuple

import numpy as np
import ufoLib2

from design_system import (
    ContourBuilder,
    DUPLEX_ADVANCE_WIDTHS,
    METRICS,
    TABULAR_FIG_WIDTH,
    UNICODE_MAP,
    bar_segment_contour,
    humanist_oval_contour,
    lerp_x,
    rect_contour,
    rpt,
    union_contours,
)
from glyphs_mono import (
    MONO_FEATURES_FEA,
    MONO_REGULAR,
    MONO_WIDTH,
    build_all_mono_glyphs,
)
from glyphs_sans import build_all_sans_glyphs
from glyphs_sans_latin_ext import (
    COMPOSITE_RECIPES,
    EXT_CONTOUR_BUILDERS,
    _rotate_180,
    _scale_contours,
)
from glyphs_serif_figs_ext import SERIF_REGULAR, build_all_serif_glyphs
from serif_primitives import (
    SerifWeightParams,
    diag_foot_serif,
    diag_head_serif,
    foot_pad_ccw,
    head_pad_ccw,
    vstem_serifed,
)
from spacing_kerning import BASE_ANCHORS, MARK_ANCHORS, apply_class_kerning


# ---------------------------------------------------------------------------
# Bold Parameters & Shared 1:1 Duplex Bold Width Table
# ---------------------------------------------------------------------------

SANS_BOLD_RX = 21.0
SANS_BOLD_RY = 13.0
SERIF_BOLD_RX = 21.0
SERIF_BOLD_RY = 5.5
MONO_BOLD_RX = 15.0
MONO_BOLD_RY = 9.0

SERIF_BOLD = SerifWeightParams(
    name="Bold",
    weight_value=700,
    lc_stem_v=144.0,
    lc_stem_h=58.0,
    lc_bowl_v=148.0,
    lc_join_thin=56.0,
    cap_stem_v=154.0,
    cap_stem_h=62.0,
    cap_bowl_v=160.0,
    fig_stem_v=146.0,
    fig_stem_h=60.0,
    fig_bowl_v=154.0,
    lc_serif_h=34.0,
    lc_serif_ext=48.0,
    lc_bracket=34.0,
    cap_serif_h=36.0,
    cap_serif_ext=52.0,
    cap_bracket=36.0,
)

# Widths locked to Regular so table columns, spaces & math operators never shift on bolding
_LOCKED_WIDTH_GLYPHS = {
    "space",
    "nbspace",
    "thinspace",
    "narrownbspace",
    "zero.tnum",
    "one.tnum",
    "two.tnum",
    "three.tnum",
    "four.tnum",
    "five.tnum",
    "six.tnum",
    "seven.tnum",
    "eight.tnum",
    "nine.tnum",
    "zero.tnum.slash",
    "plus",
    "minus",
    "equal",
    "less",
    "greater",
    "plusminus",
    "multiply",
    "divide",
    "notequal",
    "lessequal",
    "greaterequal",
    "approxequal",
    "dollar",
    "euro",
    "sterling",
    "yen",
    "rupee",
    "ruble",
    "currency",
    "logicalnot",
    "radical",
}

_BOLD_WIDTH_OVERRIDES: Dict[str, int] = {
    ".notdef": 600,
    "i": 274,
    "dotlessi": 274,
    "j": 284,
    "dotlessj": 284,
    "l": 284,
    "lslash": 312,
    "ldot": 424,
    "f": 376,
    "t": 384,
    "tbar": 384,
    "longs": 342,
    "r": 398,
    "m": 944,
    "w": 812,
    "I": 334,
    "M": 876,
    "W": 948,
    "AE": 968,
    "OE": 1004,
    "ae": 912,
    "oe": 932,
    "won": 948,
    "one": 456,
    "zero": 598,
    "zero.slash": 598,
    "two": 584,
    "three": 584,
    "four": 604,
    "five": 584,
    "six": 596,
    "seven": 564,
    "eight": 600,
    "nine": 596,
    "period": 272,
    "comma": 272,
    "colon": 280,
    "semicolon": 280,
    "colon.case": 280,
    "quotesingle": 252,
    "quotedbl": 416,
    "quoteleft": 268,
    "quoteright": 268,
    "quotesinglbase": 268,
    "quotedblleft": 456,
    "quotedblright": 456,
    "quotedblbase": 456,
    "bar": 306,
    "brokenbar": 306,
    "at": 904,
    "percent": 836,
    "perthousand": 1060,
    "numero": 988,
    "trademark": 764,
    "infinity": 780,
    "ordfeminine": 424,
    "ordmasculine": 424,
    "onequarter": 820,
    "onehalf": 820,
    "threequarters": 820,
}


def compute_duplex_bold_width(gname: str, reg_w: int) -> int:
    if reg_w == 0:
        return 0
    if gname in _BOLD_WIDTH_OVERRIDES:
        return _BOLD_WIDTH_OVERRIDES[gname]
    if gname in _LOCKED_WIDTH_GLYPHS:
        return reg_w
    base = gname[:-5] if gname.endswith(".case") else gname
    if base in _BOLD_WIDTH_OVERRIDES:
        return _BOLD_WIDTH_OVERRIDES[base]
    return int(round((reg_w * 1.072) / 2.0) * 2)


DUPLEX_BOLD_ADVANCE_WIDTHS: Dict[str, int] = {
    gname: compute_duplex_bold_width(gname, w)
    for gname, w in DUPLEX_ADVANCE_WIDTHS.items()
}

EXT_BOLD_ADVANCE_WIDTHS: Dict[str, int] = {
    gname: compute_duplex_bold_width(gname, w)
    for gname, (w, _, _) in EXT_CONTOUR_BUILDERS.items()
}


# ---------------------------------------------------------------------------
# Smooth Metric-Pinned Anisotropic Miter Offset Engine
# ---------------------------------------------------------------------------

# Review 2: the vertical offset is now a smooth function of height. The old version switched
# between "pinned" and "full offset" inside a 2.5u window, which left a dent on the top and
# bottom of every round letter, and switched the inner-edge compensation on and off at fixed
# heights, which left kinks on inner contours.
_TOP_ZONES = ((520.0, 530.0), (700.0, 712.0), (740.0, 752.0))      # (flat line, overshoot line)
_BOTTOM_ZONES = ((0.0, -12.0), (-220.0, -224.0))                    # (flat line, overshoot line)
_PIN_RAMP = 44.0                                                    # units over which pinning fades out
_BAND_RAMP = 26.0


def _smoothstep(x: float) -> float:
    x = 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)
    return x * x * (3.0 - 2.0 * x)


def _band(y: float, lo: float, hi: float) -> float:
    """1 inside [lo, hi], fading smoothly to 0 over _BAND_RAMP outside it."""
    if lo <= y <= hi:
        return 1.0
    d = (lo - y) if y < lo else (y - hi)
    return 1.0 - _smoothstep(d / _BAND_RAMP)


def _pin_dy(y: float, ny: float, ry: float, is_mark: bool = False) -> float:
    """
    Metric-preserving vertical normal offset (smooth in y and ny):
      - Baseline, x-height, cap height, ascender and descender stay where they are; overshoots
        grow by at most 1.5u. The pinning fades out smoothly over _PIN_RAMP units.
      - Inner edges of horizontal strokes take the weight instead (up to 1.85 * ry), also with
        smooth ramps.
    """
    if is_mark or ny == 0.0:
        return ry * ny
    best_d, best_p = 1e9, 0.0
    if ny > 0.0:
        for flat, over in _TOP_ZONES:
            if y >= over:
                d, pin = y - over, 1.5
            elif y >= flat:
                d, pin = 0.0, 1.5 * (y - flat) / (over - flat)
            else:
                d, pin = flat - y, 0.0
            if d < best_d:
                best_d, best_p = d, pin
        comp = max(_band(y, 28.0, 105.0), _band(y, -195.0, -135.0))
    else:
        for flat, over in _BOTTOM_ZONES:
            if y <= over:
                d, pin = over - y, 1.5
            elif y <= flat:
                d, pin = 0.0, 1.5 * (flat - y) / (flat - over)
            else:
                d, pin = y - flat, 0.0
            if d < best_d:
                best_d, best_p = d, pin
        comp = max(_band(y, 415.0, 495.0), _band(y, 595.0, 675.0))
    k = _smoothstep(best_d / _PIN_RAMP)
    full = ry * (1.0 + 0.85 * comp)
    return ny * (best_p + (full - best_p) * k)


def _fit_cubic_with_tangents(pts: np.ndarray, t_start, t_end):
    """Least-squares cubic through sampled points with both end tangents fixed.
    Fixing the tangents is what keeps a smooth join smooth after the offset."""
    p0, p3 = pts[0], pts[-1]
    chord = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    total = float(chord.sum())
    if total < 1e-6:
        return None
    t = np.concatenate([[0.0], np.cumsum(chord)]) / total
    mt = 1.0 - t
    b1, b2 = 3.0 * mt * mt * t, 3.0 * mt * t * t
    ts, te = np.asarray(t_start, dtype=float), np.asarray(t_end, dtype=float)
    a = np.zeros((2 * len(t), 2))
    a[: len(t), 0], a[len(t):, 0] = b1 * ts[0], b1 * ts[1]
    a[: len(t), 1], a[len(t):, 1] = -b2 * te[0], -b2 * te[1]
    resid = pts - ((mt ** 3 + b1)[:, None] * p0 + (b2 + t ** 3)[:, None] * p3)
    sol, _, _, _ = np.linalg.lstsq(a, np.concatenate([resid[:, 0], resid[:, 1]]), rcond=None)
    span = float(np.linalg.norm(p3 - p0))
    lo, hi = 0.04 * max(span, total * 0.5), 1.2 * total
    alpha = min(max(float(sol[0]), lo), hi)
    beta = min(max(float(sol[1]), lo), hi)
    return (p0 + alpha * ts, p3 - beta * te)


def bolden_contours_smooth(
    contours: List[ContourBuilder],
    orig_w: int,
    new_w: int,
    rx: float,
    ry: float,
    *,
    is_mark: bool = False,
) -> List[ContourBuilder]:
    """
    Horizontally scale Regular skeleton cleanly by new_w/orig_w, then apply a
    miter-intersected metric-pinned anisotropic contour offset & pathops cleanup.
    """
    if not contours:
        return []
    sx = (new_w / orig_w) if orig_w > 0 else 1.0
    out_cbs: List[ContourBuilder] = []

    for cb in contours:
        segs = []
        curr = (cb.start[0] * sx, cb.start[1])
        for op in cb.ops:
            if op[0] == "line":
                p1 = (op[1][0] * sx, op[1][1])
                if math.hypot(p1[0] - curr[0], p1[1] - curr[1]) > 0.5:
                    segs.append(("line", curr, p1))
                curr = p1
            elif op[0] == "curve":
                c1 = (op[1][0] * sx, op[1][1])
                c2 = (op[2][0] * sx, op[2][1])
                p3 = (op[3][0] * sx, op[3][1])
                segs.append(("curve", curr, c1, c2, p3, op[4]))
                curr = p3
        p_close = (cb.start[0] * sx, cb.start[1])
        if math.hypot(p_close[0] - curr[0], p_close[1] - curr[1]) > 0.5:
            segs.append(("line", curr, p_close))
        if not segs:
            continue

        off_segs = []
        for s in segs:
            if s[0] == "line":
                p0, p1 = s[1], s[2]
                dx, dy = p1[0] - p0[0], p1[1] - p0[1]
                length = max(math.hypot(dx, dy), 1e-6)
                tx, ty = dx / length, dy / length
                nx, ny = ty, -tx
                q0 = (p0[0] + rx * nx, p0[1] + _pin_dy(p0[1], ny, ry, is_mark))
                q1 = (p1[0] + rx * nx, p1[1] + _pin_dy(p1[1], ny, ry, is_mark))
                dqx, dqy = q1[0] - q0[0], q1[1] - q0[1]
                lq = max(math.hypot(dqx, dqy), 1e-6)
                off_segs.append(("line", q0, q1, (dqx / lq, dqy / lq), (dqx / lq, dqy / lq)))
            else:
                p0, c1, c2, p3, sm = s[1], s[2], s[3], s[4], s[5]
                ts = np.linspace(0.0, 1.0, 36)
                mt = 1.0 - ts
                pts = (
                    (mt**3)[:, None] * p0
                    + 3 * (mt**2 * ts)[:, None] * c1
                    + 3 * (mt * ts**2)[:, None] * c2
                    + (ts**3)[:, None] * p3
                )
                dpts = (
                    3 * (mt**2)[:, None] * (np.array(c1) - p0)
                    + 6 * (mt * ts)[:, None] * (np.array(c2) - c1)
                    + 3 * (ts**2)[:, None] * (np.array(p3) - c2)
                )
                norms = np.maximum(np.linalg.norm(dpts, axis=1, keepdims=True), 1e-6)
                tang = dpts / norms
                nrm = np.column_stack([tang[:, 1], -tang[:, 0]])
                dys = np.array([_pin_dy(pts[k, 1], nrm[k, 1], ry, is_mark) for k in range(len(ts))])
                shifted = np.column_stack([pts[:, 0] + rx * nrm[:, 0], pts[:, 1] + dys])
                t0 = shifted[1] - shifted[0]
                t0 /= max(np.linalg.norm(t0), 1e-6)
                t1 = shifted[-1] - shifted[-2]
                t1 /= max(np.linalg.norm(t1), 1e-6)
                off_segs.append(("curve", shifted, (float(t0[0]), float(t0[1])), (float(t1[0]), float(t1[1])), sm))

        # Review 3: drop offset segments that turned inside out. A small concave detail (radius
        # smaller than the offset) comes out reversed and leaves a spike or a zigzag in the
        # outline; without it, its two neighbours simply meet at their own join.
        if len(off_segs) > 3:
            kept = []
            for s_src, s_off in zip(segs, off_segs):
                o0, o1 = (s_src[1], s_src[2]) if s_src[0] == "line" else (s_src[1], s_src[4])
                if s_off[0] == "line":
                    q0, q1 = s_off[1], s_off[2]
                else:
                    q0, q1 = tuple(s_off[1][0]), tuple(s_off[1][-1])
                ox, oy = o1[0] - o0[0], o1[1] - o0[1]
                qx, qy = q1[0] - q0[0], q1[1] - q0[1]
                o_len = math.hypot(ox, oy)
                if o_len < 60.0 and (ox * qx + oy * qy) < 0.35 * o_len * o_len:
                    continue
                kept.append(s_off)
            if len(kept) >= 3:
                off_segs = kept
        n_s = len(off_segs)

        def _seg_end(sg):
            return (sg[2], sg[4]) if sg[0] == "line" else (tuple(sg[1][-1]), sg[3])

        def _seg_start(sg):
            return (sg[1], sg[3]) if sg[0] == "line" else (tuple(sg[1][0]), sg[2])

        # Review 2 join rules. Each join gives: the point where the previous segment ends, the
        # point where the next one starts (different only for a bevel), and a shared tangent
        # when the join is smooth.
        #   - smooth join (< ~12 deg): one shared tangent, so the join stays smooth;
        #     a straight line next to a curve keeps its own direction and end point.
        #   - corner: miter intersection as before; when the miter is too long, the straight
        #     side keeps its end point (this is what stops stems from tapering).
        joins = []
        for i in range(n_s):
            s_prev, s_curr = off_segs[(i - 1) % n_s], off_segs[i]
            p_end, t_end = _seg_end(s_prev)
            p_beg, t_beg = _seg_start(s_curr)
            cross = t_end[0] * t_beg[1] - t_end[1] * t_beg[0]
            dot = t_end[0] * t_beg[0] + t_end[1] * t_beg[1]
            mid = ((p_end[0] + p_beg[0]) * 0.5, (p_end[1] + p_beg[1]) * 0.5)
            prev_line, curr_line = s_prev[0] == "line", s_curr[0] == "line"
            if abs(cross) <= 0.21 and dot > 0.0:
                if prev_line and curr_line:
                    joins.append((mid, mid, None))
                elif prev_line:
                    joins.append((p_end, p_end, t_end))
                elif curr_line:
                    joins.append((p_beg, p_beg, t_beg))
                else:
                    tx, ty = t_end[0] + t_beg[0], t_end[1] + t_beg[1]
                    tl = max(math.hypot(tx, ty), 1e-6)
                    joins.append((mid, mid, (tx / tl, ty / tl)))
                continue
            det = t_end[0] * (-t_beg[1]) - t_end[1] * (-t_beg[0])
            dx, dy = p_beg[0] - p_end[0], p_beg[1] - p_end[1]
            u = (dx * (-t_beg[1]) - dy * (-t_beg[0])) / det if abs(det) > 1e-9 else 1e9
            lim = 2.0 * max(rx, ry)
            if abs(u) <= lim:
                pt = (p_end[0] + u * t_end[0], p_end[1] + u * t_end[1])
                joins.append((pt, pt, None))
            elif prev_line and not curr_line:
                joins.append((p_end, p_end, None))
            elif curr_line and not prev_line:
                joins.append((p_beg, p_beg, None))
            elif prev_line and curr_line and math.hypot(dx, dy) > 1.0:
                joins.append((p_end, p_beg, None))          # bevel: both lines keep their direction
            else:
                joins.append((mid, mid, None))

        nc = ContourBuilder(joins[0][1])
        for i, s in enumerate(off_segs):
            j_start, j_end = joins[i], joins[(i + 1) % n_s]
            c_start, c_end = j_start[1], j_end[0]
            if s[0] == "line":
                nc.line_to(*c_end)
            else:
                pts = s[1].copy()
                pts[0] = c_start
                pts[-1] = c_end
                fit = _fit_cubic_with_tangents(pts, j_start[2] or s[2], j_end[2] or s[3])
                if fit is None:
                    nc.line_to(*c_end)
                else:
                    nc.curve_to(tuple(fit[0]), tuple(fit[1]), c_end, smooth=s[4])
            if (i + 1) % n_s != 0 and j_end[0] != j_end[1]:
                nc.line_to(*j_end[1])
        out_cbs.append(nc)

    unioned = union_contours(out_cbs)
    # Filter degenerate sub-square-unit pinholes/slivers that pathops offset+union can emit
    from fontTools.pens.areaPen import AreaPen

    cleaned: List[ContourBuilder] = []
    for c in unioned:
        g_tmp = ufoLib2.objects.Glyph()
        c.draw_to_pen(g_tmp.getPen())
        ap = AreaPen(None)
        g_tmp.draw(ap)
        if abs(ap.value) >= 25.0:
            cleaned.append(c)
    return cleaned


# ---------------------------------------------------------------------------
# Shared Explicit Bold Symbols & Punctuation (Sans Bold + Serif Bold)
# ---------------------------------------------------------------------------

def _bold_comma_shape(cx: float, top_y: float) -> ContourBuilder:
    y_mid = top_y - 62
    return (
        ContourBuilder((cx - 32, top_y - 252))
        .curve_to((cx + 34, top_y - 224), (cx + 66, top_y - 156), (cx + 66, y_mid), smooth=True)
        .vh_to(cx, top_y, 0.60, 0.60)
        .hv_to(cx - 64, y_mid, 0.60, 0.60)
        .vh_to(cx - 8, top_y - 122, 0.58, 0.58)
        .curve_to((cx - 12, top_y - 160), (cx - 32, top_y - 190), (cx - 66, top_y - 212), smooth=False)
    )


def _bold_quoteright(mono: bool = False) -> List[ContourBuilder]:
    cx = 300.0 if mono else 134.0
    return [_bold_comma_shape(cx, 704)]


def _bold_quoteleft(mono: bool = False) -> List[ContourBuilder]:
    cx = 300.0 if mono else 134.0
    return _rotate_180(_bold_quoteright(mono), cx, 578)


def _bold_quotedblright(mono: bool = False) -> List[ContourBuilder]:
    dx = 94.0 if mono else 92.0
    q = _bold_quoteright(mono)[0]
    return [q.translated(-dx, 0), q.translated(dx, 0)]


def _bold_quotedblleft(mono: bool = False) -> List[ContourBuilder]:
    cx = 300.0 if mono else 228.0
    q = _bold_quoteright(mono)[0]
    return _rotate_180([q.translated(-92, 0), q.translated(92, 0)], cx, 578)


def _bold_quotesinglbase(mono: bool = False) -> List[ContourBuilder]:
    return [c.translated(0, -600) for c in _bold_quoteright(mono)]


def _bold_quotedblbase(mono: bool = False) -> List[ContourBuilder]:
    return [c.translated(0, -600) for c in _bold_quotedblright(mono)]


def _bold_section(dx: float = 16.0) -> List[ContourBuilder]:
    """Single-contour rotated-symmetry humanist § for Bold weight (zero pinch!)"""
    def _eval_c(p0, p1, p2, p3, t):
        mt = 1.0 - t
        return (mt**3) * p0 + 3 * (mt**2) * t * p1 + 3 * mt * (t**2) * p2 + (t**3) * p3

    def _eval_dc(p0, p1, p2, p3, t):
        mt = 1.0 - t
        return 3 * (mt**2) * (p1 - p0) + 6 * mt * t * (p2 - p1) + 3 * (t**2) * (p3 - p2)

    def _fit_c(pts):
        p0, p3 = pts[0], pts[-1]
        chord = np.linalg.norm(np.diff(pts, axis=0), axis=1)
        t = np.concatenate([[0.0], np.cumsum(chord)])
        t /= t[-1]
        mt = 1.0 - t
        mat = np.column_stack([3 * (mt**2) * t, 3 * mt * (t**2)])
        rhs = pts - ((mt**3)[:, None] * p0 + (t**3)[:, None] * p3)
        c12, _, _, _ = np.linalg.lstsq(mat, rhs, rcond=None)
        return (float(c12[0][0]), float(c12[0][1])), (float(c12[1][0]), float(c12[1][1])), (float(p3[0]), float(p3[1]))

    segs = [
        (np.array([400.0, 608.0]), np.array([370.0, 654.0]), np.array([320.0, 676.0]), np.array([262.0, 676.0])),
        (np.array([262.0, 676.0]), np.array([188.0, 676.0]), np.array([138.0, 632.0]), np.array([138.0, 568.0])),
        (np.array([138.0, 568.0]), np.array([138.0, 496.0]), np.array([204.0, 464.0]), np.array([274.0, 424.0])),
        (np.array([274.0, 424.0]), np.array([346.0, 383.0]), np.array([394.0, 342.0]), np.array([394.0, 276.0])),
        (np.array([394.0, 276.0]), np.array([394.0, 212.0]), np.array([324.0, 192.0]), np.array([248.0, 192.0])),
    ]
    left_list, right_list = [], []
    for p0, p1, p2, p3 in segs:
        ts = np.linspace(0.0, 1.0, 48)
        pts = np.array([_eval_c(p0, p1, p2, p3, tv) for tv in ts])
        dpts = np.array([_eval_dc(p0, p1, p2, p3, tv) for tv in ts])
        tang = dpts / np.linalg.norm(dpts, axis=1, keepdims=True)
        nrm = np.column_stack([-tang[:, 1], tang[:, 0]])
        hw = 45.0 - 4.0 * (np.abs(tang[:, 0]) ** 2)
        left_list.append(pts + nrm * hw[:, None])
        right_list.append(pts - nrm * hw[:, None])

    s1 = ContourBuilder((float(right_list[0][0][0]), float(right_list[0][0][1])))
    for rpts in right_list:
        c1, c2, p3 = _fit_c(rpts)
        s1.curve_to(c1, c2, p3)
    s1.line_to(float(left_list[-1][-1][0]), float(left_list[-1][-1][1]))
    for lpts in reversed(left_list):
        c1, c2, p3 = _fit_c(lpts[::-1])
        s1.curve_to(c1, c2, p3)

    s2 = _rotate_180([s1], 260, 308)
    res = union_contours([s1] + s2)
    return [c.translated(dx, 0) for c in res]


def _bold_at(w: int = 904) -> List[ContourBuilder]:
    sx = w / 840.0
    outer = (
        ContourBuilder((432 * sx, -116))
        .curve_to((524 * sx, -116), (602 * sx, -96), (666 * sx, -56), smooth=False)
        .line_to(624 * sx, 22)
        .curve_to((570 * sx, -14), (506 * sx, -30), (436 * sx, -30), smooth=True)
        .hv_to(144 * sx, 300, 0.585, 0.59)
        .vh_to(436 * sx, 616, 0.59, 0.585)
        .hv_to(704 * sx, 344, 0.585, 0.585)
        .curve_to((704 * sx, 244), (668 * sx, 186), (618 * sx, 186), smooth=True)
        .curve_to((588 * sx, 186), (576 * sx, 206), (576 * sx, 246), smooth=False)
        .line_to(576 * sx, 474)
        .line_to(480 * sx, 474)
        .line_to(478 * sx, 434)
        .curve_to((450 * sx, 468), (408 * sx, 486), (358 * sx, 486), smooth=False)
        .hv_to(210 * sx, 290, 0.585, 0.585)
        .vh_to(356 * sx, 98, 0.585, 0.585)
        .curve_to((412 * sx, 98), (456 * sx, 120), (484 * sx, 160), smooth=False)
        .curve_to((502 * sx, 108), (548 * sx, 84), (612 * sx, 84), smooth=False)
        .curve_to((722 * sx, 84), (802 * sx, 184), (802 * sx, 348), smooth=True)
        .vh_to(434 * sx, 700, 0.585, 0.585)
        .hv_to(42 * sx, 300, 0.59, 0.59)
        .vh_to(432 * sx, -116, 0.59, 0.59)
    )
    inner = (
        ContourBuilder((376 * sx, 182))
        .hv_to(314 * sx, 290, 0.59, 0.59)
        .vh_to(376 * sx, 400, 0.59, 0.59)
        .hv_to(478 * sx, 326, 0.56, 0.56)
        .line_to(478 * sx, 254)
        .vh_to(376 * sx, 182, 0.56, 0.56)
    )
    return [outer, inner]


def _bold_trademark() -> List[ContourBuilder]:
    t = (
        ContourBuilder((116, 376))
        .line_to(204, 376)
        .line_to(204, 622)
        .line_to(304, 622)
        .line_to(304, 700)
        .line_to(20, 700)
        .line_to(20, 622)
        .line_to(116, 622)
    )
    m = (
        ContourBuilder((344, 376))
        .line_to(422, 376)
        .line_to(422, 574)
        .line_to(428, 574)
        .line_to(504, 376)
        .line_to(564, 376)
        .line_to(640, 574)
        .line_to(646, 574)
        .line_to(646, 376)
        .line_to(726, 376)
        .line_to(726, 700)
        .line_to(618, 700)
        .line_to(537, 488)
        .line_to(531, 488)
        .line_to(450, 700)
        .line_to(344, 700)
    )
    return [t, m]


def _bold_infinity() -> List[ContourBuilder]:
    outer = (
        ContourBuilder((226, 98))
        .curve_to((302, 98), (354, 150), (390, 212), smooth=False)
        .curve_to((426, 150), (478, 98), (554, 98), smooth=True)
        .hv_to(734, 286, 0.58, 0.58)
        .vh_to(554, 474, 0.58, 0.58)
        .curve_to((478, 474), (426, 422), (390, 360), smooth=False)
        .curve_to((354, 422), (302, 474), (226, 474), smooth=True)
        .hv_to(46, 286, 0.58, 0.58)
        .vh_to(226, 98, 0.58, 0.58)
    )
    hole_l = humanist_oval_contour(224, 286, 80, 90, 0.59, 0.59, clockwise=True)
    hole_r = humanist_oval_contour(556, 286, 80, 90, 0.59, 0.59, clockwise=True)
    return [outer, hole_l, hole_r]


def _bold_Delta() -> List[ContourBuilder]:
    outer = ContourBuilder((28, 0)).line_to(624, 0).line_to(382, 700).line_to(270, 700)
    inner = ContourBuilder((162, 102)).line_to(322, 540).line_to(330, 540).line_to(490, 102)
    return [outer, inner]


def _bold_ordmasculine() -> List[ContourBuilder]:
    return [
        humanist_oval_contour(212, 577, 150, 134, 0.59, 0.59, clockwise=False),
        humanist_oval_contour(212, 577, 58, 62, 0.60, 0.60, clockwise=True),
        rect_contour(62, 326, 362, 396),
    ]


def _bold_ordfeminine() -> List[ContourBuilder]:
    outer = (
        ContourBuilder((174, 444))
        .curve_to((222, 444), (260, 458), (282, 484), smooth=False)
        .line_to(284, 450)
        .line_to(362, 450)
        .line_to(362, 624)
        .vh_to(216, 712, 0.58, 0.58)
        .curve_to((162, 712), (118, 698), (84, 678), smooth=False)
        .line_to(110, 616)
        .curve_to((140, 636), (174, 646), (210, 646), smooth=True)
        .hv_to(278, 608, 0.56, 0.56)
        .line_to(278, 598)
        .curve_to((198, 596), (56, 572), (56, 506), smooth=True)
        .vh_to(174, 444, 0.58, 0.58)
    )
    inner = (
        ContourBuilder((190, 496))
        .hv_to(138, 514, 0.58, 0.58)
        .curve_to((138, 536), (204, 546), (278, 546), smooth=False)
        .line_to(278, 520)
        .vh_to(190, 496, 0.56, 0.58)
    )
    bar = rect_contour(62, 326, 362, 396)
    return [outer, inner, bar]


def _bold_perthousand(w: int = 1060) -> List[ContourBuilder]:
    sx = w / 980.0
    top_o = humanist_oval_contour(200 * sx, 526, 150, 176, 0.585, 0.59, clockwise=False)
    top_i = humanist_oval_contour(200 * sx, 526, 52, 92, 0.60, 0.60, clockwise=True)
    b1_o = humanist_oval_contour(556 * sx, 164, 146, 176, 0.585, 0.59, clockwise=False)
    b1_i = humanist_oval_contour(556 * sx, 164, 48, 92, 0.60, 0.60, clockwise=True)
    b2_o = humanist_oval_contour(840 * sx, 164, 146, 176, 0.585, 0.59, clockwise=False)
    b2_i = humanist_oval_contour(840 * sx, 164, 48, 92, 0.60, 0.60, clockwise=True)
    slash = ContourBuilder((144, -12)).line_to(242, -12).line_to(568, 700).line_to(470, 700)
    return [top_o, top_i, b1_o, b1_i, b2_o, b2_i, slash]


def _bold_numero(w: int = 988) -> List[ContourBuilder]:
    n_c = (
        ContourBuilder((54, 0))
        .line_to(170, 0)
        .line_to(170, 480)
        .line_to(178, 480)
        .line_to(422, 0)
        .line_to(554, 0)
        .line_to(554, 700)
        .line_to(438, 700)
        .line_to(438, 220)
        .line_to(430, 220)
        .line_to(186, 700)
        .line_to(54, 700)
    )
    o_out = humanist_oval_contour(768, 577, 158, 134, 0.59, 0.59, clockwise=False)
    o_in = humanist_oval_contour(768, 577, 62, 62, 0.60, 0.60, clockwise=True)
    bar = rect_contour(610, 326, 926, 396)
    return [n_c, o_out, o_in, bar]


def _bold_lessequal(less_contours: List[ContourBuilder], dx: float = 0.0) -> List[ContourBuilder]:
    lt = [c.translated(0, 74) for c in less_contours]
    bar = rect_contour(68 + dx, 14, 504 + dx, 98)
    return lt + [bar]


def _bold_greaterequal(greater_contours: List[ContourBuilder], dx: float = 0.0) -> List[ContourBuilder]:
    gt = [c.translated(0, 74) for c in greater_contours]
    bar = rect_contour(76 + dx, 14, 512 + dx, 98)
    return gt + [bar]


def _bold_fraction(
    num_cs: List[ContourBuilder], den_cs: List[ContourBuilder], dx_den: float = 428.0
) -> List[ContourBuilder]:
    num = _scale_contours(num_cs, 0.54, 0.54, 16, 336)
    den = _scale_contours(den_cs, 0.54, 0.54, dx_den, 0)
    slash = ContourBuilder((176, -12)).line_to(266, -12).line_to(624, 704).line_to(534, 704)
    return num + [slash] + den


def _bold_superscript(cs: List[ContourBuilder], dx: float = 20.0, dy: float = 304.0) -> List[ContourBuilder]:
    return _scale_contours(cs, 0.62, 0.58, dx, dy)


# ---------------------------------------------------------------------------
# Sans Bold Explicit Builders (Caps, Ligatures, Figures & Symbols)
# ---------------------------------------------------------------------------

def _sans_bold_A() -> List[ContourBuilder]:
    cap = METRICS.cap_height
    yb0, yb1 = 186, 284  # 98u bold bar
    xl_b0 = lerp_x(164, 0, 337, 540, yb0)
    xr_b0 = lerp_x(518, 0, 345, 540, yb0)
    xl_b1 = lerp_x(164, 0, 337, 540, yb1)
    xr_b1 = lerp_x(518, 0, 345, 540, yb1)
    outer = (
        ContourBuilder((22, 0))
        .line_to(164, 0)
        .line_to(xl_b0, yb0)
        .line_to(xr_b0, yb0)
        .line_to(518, 0)
        .line_to(660, 0)
        .line_to(412, cap)
        .line_to(270, cap)
    )
    inner = ContourBuilder((xl_b1, yb1)).line_to(337, 540).line_to(345, 540).line_to(xr_b1, yb1)
    return [outer, inner]


def _sans_bold_four(shift_x: float = 0.0) -> List[ContourBuilder]:
    outer = (
        ContourBuilder((356 + shift_x, 0))
        .line_to(490 + shift_x, 0)
        .line_to(490 + shift_x, 166)
        .line_to(574 + shift_x, 166)
        .line_to(574 + shift_x, 268)
        .line_to(490 + shift_x, 268)
        .line_to(490 + shift_x, 690)
        .line_to(344 + shift_x, 690)
        .line_to(30 + shift_x, 250)
        .line_to(30 + shift_x, 166)
        .line_to(356 + shift_x, 166)
    )
    inner = (
        ContourBuilder((158 + shift_x, 268))
        .line_to(350 + shift_x, 526)
        .line_to(356 + shift_x, 526)
        .line_to(356 + shift_x, 268)
    )
    return [outer, inner]


def _sans_bold_eight(dx: float = 0.0) -> List[ContourBuilder]:
    cx = 300.0 + dx
    outer = (
        ContourBuilder((cx, -12))
        .hv_to(554 + dx, 188, 0.58, 0.58)
        .curve_to((554 + dx, 274), (500 + dx, 330), (420 + dx, 360), smooth=False)
        .curve_to((486 + dx, 392), (532 + dx, 446), (532 + dx, 522), smooth=False)
        .vh_to(cx, 704, 0.58, 0.58)
        .hv_to(68 + dx, 522, 0.58, 0.58)
        .curve_to((68 + dx, 446), (114 + dx, 392), (180 + dx, 360), smooth=False)
        .curve_to((100 + dx, 330), (46 + dx, 274), (46 + dx, 188), smooth=False)
        .vh_to(cx, -12, 0.58, 0.58)
    )
    in_top = humanist_oval_contour(cx, 520, 92, 92, 0.59, 0.59, clockwise=True)
    in_bot = humanist_oval_contour(cx, 186, 108, 102, 0.59, 0.59, clockwise=True)
    return [outer, in_top, in_bot]


def _sans_bold_AE() -> List[ContourBuilder]:
    cap = METRICS.cap_height
    yb0, yb1 = 186, 284
    xl_b0 = lerp_x(164, 0, 446, 540, yb0)
    xl_b1 = lerp_x(164, 0, 446, 540, yb1)
    outer = (
        ContourBuilder((22, 0))
        .line_to(164, 0)
        .line_to(xl_b0, yb0)
        .line_to(446, yb0)
        .line_to(446, 0)
        .line_to(906, 0)
        .line_to(906, 102)
        .line_to(590, 102)
        .line_to(590, 316)
        .line_to(866, 316)
        .line_to(866, 412)
        .line_to(590, 412)
        .line_to(590, cap - 102)
        .line_to(892, cap - 102)
        .line_to(892, cap)
        .line_to(388, cap)
    )
    inner = ContourBuilder((xl_b1, yb1)).line_to(440, 540).line_to(446, 540).line_to(446, yb1)
    return [outer, inner]


def _sans_bold_OE() -> List[ContourBuilder]:
    cap = METRICS.cap_height
    top, bot = cap + 12, -12
    o_out = (
        ContourBuilder((354, bot))
        .curve_to((416, bot), (464, 4), (498, 28), smooth=False)
        .line_to(500, 0)
        .line_to(944, 0)
        .line_to(944, 102)
        .line_to(624, 102)
        .line_to(624, 316)
        .line_to(902, 316)
        .line_to(902, 412)
        .line_to(624, 412)
        .line_to(624, cap - 102)
        .line_to(930, cap - 102)
        .line_to(930, cap)
        .line_to(500, cap)
        .line_to(498, cap - 28)
        .curve_to((464, cap - 4), (416, top), (354, top), smooth=False)
        .hv_to(48, 350, 0.585, 0.59)
        .vh_to(354, bot, 0.59, 0.585)
    )
    o_in = (
        ContourBuilder((356, 94))
        .hv_to(188, 350, 0.59, 0.60)
        .vh_to(356, 606, 0.60, 0.59)
        .hv_to(480, 514, 0.56, 0.56)
        .line_to(480, 186)
        .vh_to(356, 94, 0.56, 0.56)
    )
    return [o_out, o_in]


def _sans_bold_ae() -> List[ContourBuilder]:
    top, bot = 532, -12
    a_out = (
        ContourBuilder((224, bot))
        .curve_to((296, bot), (358, 12), (402, 52), smooth=False)
        .line_to(422, 52)
        .curve_to((464, 12), (528, bot), (618, bot), smooth=True)
        .curve_to((720, bot), (798, 22), (848, 86), smooth=False)
        .line_to(776, 158)
        .curve_to((734, 108), (682, 82), (624, 82), smooth=True)
        .curve_to((548, 82), (506, 124), (502, 206), smooth=False)
        .line_to(866, 206)
        .line_to(866, 278)
        .vh_to(624, top, 0.58, 0.58)
        .curve_to((544, top), (476, 502), (432, 444), smooth=False)
        .line_to(418, 444)
        .curve_to((376, 502), (314, top), (242, top), smooth=True)
        .curve_to((174, top), (118, 510), (74, 474), smooth=False)
        .line_to(118, 386)
        .curve_to((156, 414), (200, 430), (244, 430), smooth=True)
        .hv_to(356, 344, 0.56, 0.56)
        .line_to(356, 312)
        .curve_to((246, 308), (44, 266), (44, 140), smooth=True)
        .vh_to(224, bot, 0.58, 0.58)
    )
    in_a = (
        ContourBuilder((238, 80))
        .hv_to(168, 142, 0.58, 0.58)
        .curve_to((168, 198), (264, 228), (366, 232), smooth=False)
        .line_to(366, 150)
        .vh_to(238, 80, 0.56, 0.58)
    )
    in_e = (
        ContourBuilder((500, 294))
        .line_to(500, 344)
        .vh_to(620, 436, 0.56, 0.58)
        .curve_to((684, 436), (724, 382), (730, 294), smooth=False)
    )
    return [a_out, in_a, in_e]


def _sans_bold_oe() -> List[ContourBuilder]:
    top, bot = 532, -12
    outer = (
        ContourBuilder((266, bot))
        .curve_to((344, bot), (408, 14), (446, 58), smooth=False)
        .line_to(458, 58)
        .curve_to((496, 14), (558, bot), (642, bot), smooth=True)
        .curve_to((744, bot), (822, 22), (872, 86), smooth=False)
        .line_to(800, 158)
        .curve_to((758, 108), (706, 82), (648, 82), smooth=True)
        .curve_to((572, 82), (530, 124), (526, 206), smooth=False)
        .line_to(890, 206)
        .line_to(890, 278)
        .vh_to(648, top, 0.58, 0.58)
        .curve_to((568, top), (500, 502), (458, 444), smooth=False)
        .line_to(446, 444)
        .curve_to((408, 502), (344, top), (266, top), smooth=True)
        .hv_to(44, 260, 0.585, 0.59)
        .vh_to(266, bot, 0.59, 0.585)
    )
    in_o = (
        ContourBuilder((274, 86))
        .hv_to(176, 260, 0.59, 0.60)
        .vh_to(274, 434, 0.60, 0.59)
        .hv_to(388, 340, 0.56, 0.56)
        .line_to(388, 180)
        .vh_to(274, 86, 0.56, 0.56)
    )
    in_e = (
        ContourBuilder((524, 294))
        .line_to(524, 344)
        .vh_to(644, 436, 0.56, 0.58)
        .curve_to((708, 436), (748, 382), (754, 294), smooth=False)
    )
    return [outer, in_o, in_e]


def _sans_bold_Germandbls() -> List[ContourBuilder]:
    cap = METRICS.cap_height
    c = (
        ContourBuilder((74, 0))
        .line_to(214, 0)
        .line_to(214, 594)
        .line_to(370, 594)
        .hv_to(442, 530, 0.58, 0.58)
        .curve_to((442, 476), (398, 442), (308, 412), smooth=False)
        .line_to(308, 316)
        .curve_to((438, 298), (508, 250), (508, 182), smooth=False)
        .vh_to(398, 96, 0.58, 0.58)
        .curve_to((354, 96), (308, 102), (262, 114), smooth=False)
        .line_to(238, 18)
        .curve_to((296, 0), (354, -10), (418, -10), smooth=True)
        .hv_to(650, 184, 0.58, 0.58)
        .curve_to((650, 286), (586, 348), (478, 374), smooth=False)
        .curve_to((540, 412), (576, 470), (576, 540), smooth=False)
        .curve_to((576, 628), (498, cap), (388, cap), smooth=False)
        .line_to(74, cap)
    )
    return [c]


def _sans_bold_germandbls() -> List[ContourBuilder]:
    c = (
        ContourBuilder((70, 0))
        .line_to(206, 0)
        .line_to(206, 554)
        .vh_to(308, 638, 0.58, 0.58)
        .hv_to(410, 550, 0.58, 0.58)
        .curve_to((410, 488), (366, 444), (274, 414), smooth=False)
        .line_to(274, 318)
        .curve_to((408, 300), (482, 248), (482, 174), smooth=False)
        .vh_to(376, 86, 0.58, 0.58)
        .curve_to((332, 86), (290, 94), (250, 106), smooth=False)
        .line_to(228, 14)
        .curve_to((280, -2), (334, -10), (394, -10), smooth=True)
        .hv_to(622, 174, 0.58, 0.58)
        .curve_to((622, 276), (558, 342), (452, 370), smooth=False)
        .curve_to((512, 412), (546, 476), (546, 554), smooth=False)
        .vh_to(308, 742, 0.58, 0.58)
        .hv_to(70, 560, 0.58, 0.58)
    )
    return [c]


# ---------------------------------------------------------------------------
# Serif Bold Explicit Builders (Calligraphic Contrast + Bracketed Serifs)
# ---------------------------------------------------------------------------

def _isect(p1, p2, p3, p4):
    """Intersection of line p1-p2 with line p3-p4."""
    x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    a = x1 * y2 - y1 * x2
    b = x3 * y4 - y3 * x4
    return ((a * (x3 - x4) - (x1 - x2) * b) / d, (a * (y3 - y4) - (y1 - y2) * b) / d)


def _vee(xl_top, xl_bot, xr_top, xr_bot, y_top, y_bot, t_thick, t_thin):
    """Review 2: inner walls of a V shape, parallel to the outer walls, so the thick and thin
    strokes keep one width from top to crotch (the old inner walls tapered, which made the
    Bold diagonals 15-20% lighter than the upright stems). Returns (inner-left top x,
    inner-right top x, crotch point)."""
    il_top, ir_top = xl_top + t_thick, xr_top - t_thin
    crotch = _isect((il_top, y_top), (xl_bot + t_thick, y_bot), (ir_top, y_top), (xr_bot - t_thin, y_bot))
    return il_top, ir_top, crotch


def _serif_bold_A(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    yb0, yb1 = 200, 260  # 60u hairline bar
    t_thin, t_thick = 86.0, 150.0
    il, ir = 40 + t_thin, 644 - t_thick          # inner walls at the baseline
    apex = _isect((il, 0), (284 + t_thin, cap), (ir, 0), (396 - t_thick, cap))
    xl_b0, xl_b1 = lerp_x(il, 0, apex[0], apex[1], yb0), lerp_x(il, 0, apex[0], apex[1], yb1)
    xr_b0, xr_b1 = lerp_x(ir, 0, apex[0], apex[1], yb0), lerp_x(ir, 0, apex[0], apex[1], yb1)
    outer = (
        ContourBuilder((40, 0))
        .line_to(il, 0)
        .line_to(xl_b0, yb0)
        .line_to(xr_b0, yb0)
        .line_to(ir, 0)
        .line_to(644, 0)
        .line_to(396, cap)
        .line_to(284, cap)
    )
    inner = ContourBuilder((xl_b1, yb1)).line_to(apex[0] - 4, apex[1] - 8).line_to(apex[0] + 4, apex[1] - 8).line_to(xr_b1, yb1)
    f_l = diag_foot_serif(40, il, 0, lerp_x(40, 0, 284, cap, yb0), xl_b0, yb0, ext_l=24, ext_r=26, sh=36, brk=34)
    f_r = diag_foot_serif(ir, 644, 0, xr_b0, lerp_x(644, 0, 396, cap, yb0), yb0, ext_l=26, ext_r=24, sh=36, brk=34)
    return union_contours([outer, inner, f_l, f_r])


def _serif_bold_K(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    stem = vstem_serifed(80, 232, 0, cap, bl=44, br=42, tl=44, tr=42, sh=36, brk=34)
    arm_leg = (
        ContourBuilder((208, 330))
        .line_to(286, 396)
        .line_to(482, 0)
        .line_to(628, 0)
        .line_to(362, 464)
        .line_to(596, cap)
        .line_to(508, cap)
        .line_to(208, 390)
    )
    h_arm = diag_head_serif(508, 596, cap, lerp_x(508, cap, 208, 390, 464), 362, 464, ext_l=22, ext_r=24, sh=36, brk=32)
    f_leg = diag_foot_serif(482, 628, 0, 286, lerp_x(628, 0, 362, 464, 396), 396, ext_l=20, ext_r=24, sh=36, brk=32)
    return union_contours([stem, arm_leg, h_arm, f_leg])


def _serif_bold_M(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    sL = vstem_serifed(78, 152, 0, cap, bl=42, br=42, tl=42, sh=36, brk=34)  # 74u thin left stem
    sR = vstem_serifed(656, 800, 0, cap, bl=42, br=42, tr=42, sh=36, brk=34)  # 144u firm right stem
    v_mid = (
        ContourBuilder((400, 0))
        .line_to(468, 0)
        .line_to(704, cap)
        .line_to(628, cap)
        .line_to(458, 174)
        .line_to(448, 174)
        .line_to(242, cap)
        .line_to(96, cap)
    )
    return union_contours([sL, sR, v_mid])


def _serif_bold_N(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    sL = vstem_serifed(82, 156, 0, cap, bl=44, br=44, tl=44, sh=36, brk=34)
    sR = vstem_serifed(586, 660, 0, cap, tl=44, tr=44, sh=36, brk=34)
    diag = (
        ContourBuilder((544, 0))
        .line_to(660, 0)
        .line_to(660, 128)
        .line_to(220, cap)
        .line_to(96, cap)
    )
    return union_contours([sL, sR, diag])


def _serif_bold_U(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    bot = -METRICS.cap_overshoot
    body = (
        ContourBuilder((364, bot))
        .hv_to(638, 256, 0.58, 0.59)
        .line_to(638, cap)
        .line_to(564, cap)
        .line_to(564, 252)
        .vh_to(378, 48, 0.59, 0.58)
        .hv_to(228, 252, 0.58, 0.59)
        .line_to(228, cap)
        .line_to(78, cap)
        .line_to(78, 256)
        .vh_to(364, bot, 0.59, 0.58)
    )
    hL = head_pad_ccw(78, 228, cap, ext_l=42, ext_r=40, sh=36, brk=34)
    hR = head_pad_ccw(564, 638, cap, ext_l=42, ext_r=42, sh=36, brk=34)
    return union_contours([body, hL, hR])


def _serif_bold_V(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    il, ir, (cx, cy) = _vee(28, 282, 624, 374, cap, 0, 150.0, 86.0)
    v = (
        ContourBuilder((282, 0))
        .line_to(374, 0)
        .line_to(624, cap)
        .line_to(ir, cap)
        .line_to(cx + 4, cy)
        .line_to(cx - 4, cy)
        .line_to(il, cap)
        .line_to(28, cap)
    )
    hL = diag_head_serif(28, il, cap, lerp_x(28, cap, 282, 0, cy), cx - 4, cy, ext_l=22, ext_r=24, sh=36, brk=32)
    hR = diag_head_serif(ir, 624, cap, cx + 4, lerp_x(624, cap, 374, 0, cy), cy, ext_l=24, ext_r=22, sh=36, brk=32)
    return union_contours([v, hL, hR])


def _serif_bold_W(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    t1, t2, t3, t4, y_apex = 140.0, 86.0, 126.0, 86.0, 686.0
    # outer / lower walls stay; the upper walls are parallel to them
    c1 = _isect((26 + t1, cap), (204 + t1, 0), (300 - t2, 0), (462 - t2, 514))
    c2 = _isect((472 + t3, 514), (638 + t3, 0), (734 - t4, 0), (916 - t4, cap))
    ax0 = lerp_x(300 - t2, 0, 462 - t2, 514, y_apex)
    ax1 = lerp_x(472 + t3, 514, 638 + t3, 0, y_apex)
    w_body = (
        ContourBuilder((204, 0))
        .line_to(300, 0)
        .line_to(462, 514)
        .line_to(472, 514)
        .line_to(638, 0)
        .line_to(734, 0)
        .line_to(916, cap)
        .line_to(916 - t4, cap)
        .line_to(c2[0] + 4, c2[1])
        .line_to(c2[0] - 4, c2[1])
        .line_to(ax1, y_apex)
        .line_to(ax0, y_apex)
        .line_to(c1[0] + 4, c1[1])
        .line_to(c1[0] - 4, c1[1])
        .line_to(26 + t1, cap)
        .line_to(26, cap)
    )
    hL = diag_head_serif(26, 26 + t1, cap, lerp_x(26, cap, 204, 0, c1[1]), c1[0] - 4, c1[1], ext_l=20, ext_r=22, sh=36, brk=32)
    hR = diag_head_serif(916 - t4, 916, cap, c2[0] + 4, lerp_x(916, cap, 734, 0, c2[1]), c2[1], ext_l=22, ext_r=20, sh=36, brk=32)
    return union_contours([w_body, hL, hR])


def _serif_bold_X(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    d1 = ContourBuilder((450, 0)).line_to(606, 0).line_to(192, cap).line_to(36, cap)
    d2 = ContourBuilder((44, 0)).line_to(122, 0).line_to(596, cap).line_to(518, cap)
    hTL = diag_head_serif(36, 192, cap, 450, 606, 0, ext_l=20, ext_r=22, sh=36, brk=32)
    fBR = diag_foot_serif(450, 606, 0, 36, 192, cap, ext_l=22, ext_r=20, sh=36, brk=32)
    fBL = diag_foot_serif(44, 122, 0, 518, 596, cap, ext_l=22, ext_r=22, sh=36, brk=32)
    hTR = diag_head_serif(518, 596, cap, 44, 122, 0, ext_l=22, ext_r=22, sh=36, brk=32)
    return union_contours([d1, d2, hTL, hTR, fBL, fBR])


def _serif_bold_Y(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    stem = vstem_serifed(240, 386, 0, 304, bl=52, br=52, sh=36, brk=34)
    il, ir, (cx, cy) = _vee(24, 240, 598, 386, cap, 280, 152.0, 88.0)
    arms = (
        ContourBuilder((240, 280))
        .line_to(386, 280)
        .line_to(598, cap)
        .line_to(ir, cap)
        .line_to(cx + 4, cy)
        .line_to(cx - 4, cy)
        .line_to(il, cap)
        .line_to(24, cap)
    )
    hL = diag_head_serif(24, il, cap, lerp_x(24, cap, 240, 280, cy), cx - 4, cy, ext_l=20, ext_r=22, sh=36, brk=30)
    hR = diag_head_serif(ir, 598, cap, cx + 4, lerp_x(598, cap, 386, 280, cy), cy, ext_l=22, ext_r=20, sh=36, brk=30)
    return union_contours([stem, arms, hL, hR])


def _serif_bold_k(p: SerifWeightParams) -> List[ContourBuilder]:
    asc, xh = METRICS.ascender, METRICS.x_height
    sL = vstem_serifed(68, 206, 0, asc, bl=40, br=34, tl=42, tl_flag=True, sh=34, brk=32)
    arms = (
        ContourBuilder((192, 224))
        .line_to(258, 284)
        .line_to(412, 0)
        .line_to(546, 0)
        .line_to(314, 344)
        .line_to(512, xh)
        .line_to(422, xh)
        .line_to(192, 304)
    )
    h_arm = diag_head_serif(422, 512, xh, lerp_x(422, xh, 192, 304, 344), 314, 344, ext_l=20, ext_r=20, sh=34, brk=28)
    f_leg = diag_foot_serif(412, 546, 0, 258, lerp_x(546, 0, 314, 344, 284), 284, ext_l=18, ext_r=20, sh=34, brk=28)
    return union_contours([sL, arms, h_arm, f_leg])


def _serif_bold_v(p: SerifWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    il, ir, (cx, cy) = _vee(24, 220, 512, 316, xh, 0, 136.0, 82.0)
    v = (
        ContourBuilder((220, 0))
        .line_to(316, 0)
        .line_to(512, xh)
        .line_to(ir, xh)
        .line_to(cx + 4, cy)
        .line_to(cx - 4, cy)
        .line_to(il, xh)
        .line_to(24, xh)
    )
    hL = diag_head_serif(24, il, xh, lerp_x(24, xh, 220, 0, cy), cx - 4, cy, ext_l=20, ext_r=20, sh=34, brk=28)
    hR = diag_head_serif(ir, 512, xh, cx + 4, lerp_x(512, xh, 316, 0, cy), cy, ext_l=22, ext_r=20, sh=34, brk=28)
    return union_contours([v, hL, hR])


def _serif_bold_w(p: SerifWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    t1, t2, t3, t4, y_apex = 124.0, 80.0, 106.0, 80.0, 510.0
    c1 = _isect((24 + t1, xh), (176 + t1, 0), (264 - t2, 0), (396 - t2, 390))
    c2 = _isect((406 + t3, 390), (542 + t3, 0), (632 - t4, 0), (784 - t4, xh))
    ax0 = lerp_x(264 - t2, 0, 396 - t2, 390, y_apex)
    ax1 = lerp_x(406 + t3, 390, 542 + t3, 0, y_apex)
    w_body = (
        ContourBuilder((176, 0))
        .line_to(264, 0)
        .line_to(396, 390)
        .line_to(406, 390)
        .line_to(542, 0)
        .line_to(632, 0)
        .line_to(784, xh)
        .line_to(784 - t4, xh)
        .line_to(c2[0] + 4, c2[1])
        .line_to(c2[0] - 4, c2[1])
        .line_to(ax1, y_apex)
        .line_to(ax0, y_apex)
        .line_to(c1[0] + 4, c1[1])
        .line_to(c1[0] - 4, c1[1])
        .line_to(24 + t1, xh)
        .line_to(24, xh)
    )
    hL = diag_head_serif(24, 24 + t1, xh, lerp_x(24, xh, 176, 0, c1[1]), c1[0] - 4, c1[1], ext_l=18, ext_r=20, sh=34, brk=28)
    hR = diag_head_serif(784 - t4, 784, xh, c2[0] + 4, lerp_x(784, xh, 632, 0, c2[1]), c2[1], ext_l=20, ext_r=18, sh=34, brk=28)
    return union_contours([w_body, hL, hR])


def _serif_bold_x(p: SerifWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    d1 = ContourBuilder((364, 0)).line_to(506, 0).line_to(170, xh).line_to(28, xh)
    d2 = ContourBuilder((36, 0)).line_to(114, 0).line_to(496, xh).line_to(418, xh)
    hTL = diag_head_serif(28, 170, xh, 364, 506, 0, ext_l=18, ext_r=20, sh=34, brk=28)
    fBR = diag_foot_serif(364, 506, 0, 28, 170, xh, ext_l=20, ext_r=18, sh=34, brk=28)
    fBL = diag_foot_serif(36, 114, 0, 418, 496, xh, ext_l=20, ext_r=20, sh=34, brk=28)
    hTR = diag_head_serif(418, 496, xh, 36, 114, 0, ext_l=20, ext_r=20, sh=34, brk=28)
    return union_contours([d1, d2, hTL, hTR, fBL, fBR])


def _serif_bold_y(p: SerifWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    il, ir, (cx, cy) = _vee(28, 206, 492, 258, xh, -54, 136.0, 82.0)
    # the right wall runs (492, xh) -> (258, -76); _vee was given its x at y = -54
    ir = 492 - 82.0
    cx, cy = _isect((28 + 136.0, xh), (206 + 136.0, -54), (ir, xh), (258 - 82.0, -76))
    body = (
        ContourBuilder((106, -224))
        .curve_to((176, -224), (226, -162), (258, -76), smooth=True)
        .line_to(492, xh)
        .line_to(ir, xh)
        .line_to(cx + 4, cy)
        .line_to(cx - 4, cy)
        .line_to(il, xh)
        .line_to(28, xh)
        .line_to(206, -54)
        .curve_to((184, -120), (150, -172), (104, -172), smooth=False)
        .hv_to(90, -138, 0.55, 0.55)
        .vh_to(56, -104, 0.58, 0.58)
        .hv_to(18, -148, 0.58, 0.58)
        .vh_to(106, -224, 0.58, 0.58)
    )
    hL = diag_head_serif(28, il, xh, lerp_x(28, xh, 206, -54, cy), cx - 4, cy, ext_l=20, ext_r=20, sh=34, brk=28)
    hR = diag_head_serif(ir, 492, xh, cx + 4, lerp_x(492, xh, 258, -76, cy), cy, ext_l=22, ext_r=20, sh=34, brk=28)
    return union_contours([body, hL, hR])


def _serif_bold_g(p: SerifWeightParams) -> List[ContourBuilder]:
    """Double-story Serif Bold 'g' preserving all 3 contours cleanly with open lower loop."""
    bowl_out = humanist_oval_contour(284, 366, 212, 168, 0.58, 0.58, clockwise=False)
    bowl_in = humanist_oval_contour(284, 366, 86, 114, 0.60, 0.60, clockwise=True)

    loop_out = humanist_oval_contour(308, -68, 256, 158, 0.57, 0.59, clockwise=False)
    loop_in = humanist_oval_contour(310, -76, 152, 92, 0.60, 0.60, clockwise=True)

    s_link = (
        ContourBuilder((172, 46))
        # Review 3: link ends on the top of the lower loop (308, 90) with a level tangent
        .line_to(308, 46)
        .line_to(308, 90)
        .curve_to((232, 90), (170, 114), (170, 146), smooth=False)
        .curve_to((170, 172), (192, 194), (228, 214), smooth=False)
        .line_to(172, 240)
        .curve_to((116, 208), (86, 170), (86, 128), smooth=False)
        .curve_to((86, 80), (120, 50), (172, 46), smooth=False)
    )
    ear = (
        ContourBuilder((306, 490))   # Review 3: starts inside the bowl wall
        .line_to(384, 464)
        .curve_to((424, 472), (460, 478), (496, 478), smooth=False)
        .vh_to(532, 456, 0.55, 0.58)
        .hv_to(574, 494, 0.58, 0.58)
        .vh_to(530, 534, 0.58, 0.58)
        .line_to(284, 534)          # Review 3: level with the top of the bowl
    )
    return union_contours([bowl_out, bowl_in, loop_out, loop_in, s_link, ear])


def _serif_bold_four(dx: float = 0.0) -> List[ContourBuilder]:
    outer = (
        ContourBuilder((360 + dx, 0))
        .line_to(496 + dx, 0)
        .line_to(496 + dx, 172)
        .line_to(576 + dx, 172)
        .line_to(576 + dx, 232)
        .line_to(496 + dx, 232)
        .line_to(496 + dx, 690)
        .line_to(362 + dx, 690)
        .line_to(28 + dx, 224)
        .line_to(28 + dx, 172)
        .line_to(360 + dx, 172)
    )
    inner = (
        ContourBuilder((106 + dx, 232))
        .line_to(352 + dx, 574)
        .line_to(360 + dx, 574)
        .line_to(360 + dx, 232)
    )
    foot = foot_pad_ccw(360 + dx, 496 + dx, 0, ext_l=48, ext_r=48, sh=36, brk=32)
    return union_contours([outer, inner, foot])


def _serif_bold_AE(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    bh = p.cap_stem_h  # 62
    yb0, yb1 = 200, 260
    xl_b0 = lerp_x(118, 0, 444, 558, yb0)
    xl_b1 = lerp_x(118, 0, 444, 558, yb1)
    outer = (
        ContourBuilder((36, 0))
        .line_to(118, 0)
        .line_to(xl_b0, yb0)
        .line_to(444, yb0)
        .line_to(444, 0)
        .line_to(918, 0)
        .line_to(926, 174)
        .line_to(884, 174)
        .curve_to((876, 94), (850, bh), (792, bh), smooth=False)
        .line_to(592, bh)
        .line_to(592, 326)
        .line_to(776, 326)
        .curve_to((812, 326), (828, 308), (834, 264), smooth=False)
        .line_to(874, 264)
        .line_to(874, 456)
        .line_to(834, 456)
        .curve_to((828, 412), (812, 394), (776, 394), smooth=False)
        .line_to(592, 394)
        .line_to(592, cap - bh)
        .line_to(778, cap - bh)
        .curve_to((834, cap - bh), (858, cap - 94), (866, cap - 170), smooth=False)
        .line_to(908, cap - 170)
        .line_to(900, cap)
        .line_to(388, cap)
    )
    inner = ContourBuilder((xl_b1, yb1)).line_to(436, 558).line_to(444, 558).line_to(444, yb1)
    f_l = diag_foot_serif(36, 118, 0, lerp_x(36, 0, 388, cap, yb0), xl_b0, yb0, ext_l=24, ext_r=26, sh=36, brk=32)
    f_m = foot_pad_ccw(444, 592, 0, 42, 0, sh=36, brk=32)
    return union_contours([outer, inner, f_l, f_m])


def _serif_bold_OE(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    bh = p.cap_stem_h  # 62
    outer = (
        ContourBuilder((328, -12))
        .curve_to((400, -12), (452, 12), (484, 52), smooth=False)
        .line_to(486, 0)
        .line_to(956, 0)
        .line_to(964, 174)
        .line_to(922, 174)
        .curve_to((914, 94), (890, bh), (832, bh), smooth=False)
        .line_to(626, bh)
        .line_to(626, 326)
        .line_to(814, 326)
        .curve_to((850, 326), (866, 308), (872, 264), smooth=False)
        .line_to(912, 264)
        .line_to(912, 456)
        .line_to(872, 456)
        .curve_to((866, 412), (850, 394), (814, 394), smooth=False)
        .line_to(626, 394)
        .line_to(626, cap - bh)
        .line_to(818, cap - bh)
        .curve_to((874, cap - bh), (898, cap - 94), (906, cap - 170), smooth=False)
        .line_to(948, cap - 170)
        .line_to(940, cap)
        .line_to(486, cap)
        .line_to(484, 648)
        .curve_to((452, 688), (400, 712), (328, 712), smooth=True)
        .hv_to(42, 350, 0.58, 0.59)
        .vh_to(328, -12, 0.59, 0.58)
    )
    inner = (
        ContourBuilder((336, 46))
        .hv_to(196, 350, 0.59, 0.605)
        .vh_to(336, 654, 0.605, 0.59)
        .hv_to(478, 520, 0.56, 0.56)
        .line_to(478, 180)
        .vh_to(336, 46, 0.56, 0.56)
    )
    return [outer, inner]


def _serif_bold_ae(p: SerifWeightParams) -> List[ContourBuilder]:
    outer = (
        ContourBuilder((220, -10))
        .curve_to((302, -10), (378, 14), (424, 68), smooth=False)
        .line_to(446, 68)
        .curve_to((488, 14), (558, -10), (656, -10), smooth=True)
        .curve_to((746, -10), (814, 26), (858, 94), smooth=False)
        .line_to(820, 130)
        .curve_to((780, 70), (724, 46), (664, 46), smooth=True)
        .curve_to((584, 46), (528, 120), (524, 232), smooth=False)
        .line_to(872, 232)
        .line_to(872, 282)
        .vh_to(656, 530, 0.58, 0.58)
        .curve_to((576, 530), (506, 500), (464, 444), smooth=False)
        .line_to(446, 444)
        .curve_to((408, 500), (346, 530), (274, 530), smooth=True)
        .hv_to(62, 418, 0.58, 0.56)
        .vh_to(122, 372, 0.58, 0.58)
        .hv_to(176, 418, 0.58, 0.58)
        .vh_to(268, 476, 0.48, 0.58)
        .hv_to(382, 356, 0.56, 0.56)
        .line_to(382, 314)
        .curve_to((266, 308), (44, 268), (44, 134), smooth=True)
        .vh_to(220, -10, 0.58, 0.58)
    )
    in_a = (
        ContourBuilder((236, 44))
        .hv_to(174, 136, 0.58, 0.58)
        .curve_to((174, 206), (266, 248), (382, 252), smooth=False)
        .line_to(382, 138)
        .vh_to(236, 44, 0.56, 0.58)
    )
    in_e = (
        ContourBuilder((524, 290))
        .line_to(524, 344)
        .vh_to(650, 474, 0.56, 0.58)
        .curve_to((714, 474), (758, 404), (764, 290), smooth=False)
    )
    return [outer, in_a, in_e]


def _serif_bold_oe(p: SerifWeightParams) -> List[ContourBuilder]:
    outer = (
        ContourBuilder((264, -10))
        .curve_to((346, -10), (412, 14), (450, 68), smooth=False)
        .line_to(468, 68)
        .curve_to((510, 14), (580, -10), (676, -10), smooth=True)
        .curve_to((766, -10), (834, 26), (878, 94), smooth=False)
        .line_to(840, 130)
        .curve_to((800, 70), (744, 46), (684, 46), smooth=True)
        .curve_to((604, 46), (548, 120), (544, 232), smooth=False)
        .line_to(892, 232)
        .line_to(892, 282)
        .vh_to(676, 530, 0.58, 0.58)
        .curve_to((596, 530), (526, 500), (484, 444), smooth=False)
        .line_to(468, 444)
        .curve_to((428, 500), (358, 530), (264, 530), smooth=True)
        .hv_to(42, 260, 0.58, 0.585)
        .vh_to(264, -10, 0.585, 0.58)
    )
    in_o = (
        ContourBuilder((276, 44))
        .hv_to(178, 260, 0.59, 0.605)
        .vh_to(276, 476, 0.605, 0.59)
        .hv_to(390, 340, 0.56, 0.56)
        .line_to(390, 180)
        .vh_to(276, 44, 0.56, 0.56)
    )
    in_e = (
        ContourBuilder((544, 290))
        .line_to(544, 344)
        .vh_to(670, 474, 0.56, 0.58)
        .curve_to((734, 474), (778, 404), (784, 290), smooth=False)
    )
    return [outer, in_o, in_e]


def _serif_bold_Germandbls(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    bh = p.cap_stem_h  # 62
    stem = vstem_serifed(76, 224, 0, cap, bl=44, br=38, tl=44, sh=36, brk=34)
    bowls = (
        ContourBuilder((180, cap - bh))
        .line_to(370, cap - bh)
        .hv_to(448, 530, 0.58, 0.58)
        .curve_to((448, 470), (402, 434), (312, 404), smooth=False)
        .line_to(312, 318)
        .curve_to((442, 300), (512, 250), (512, 180), smooth=False)
        .vh_to(400, 48, 0.58, 0.58)
        .curve_to((346, 48), (298, 58), (254, 78), smooth=False)
        .line_to(234, 18)
        .curve_to((294, -2), (354, -10), (420, -10), smooth=True)
        .hv_to(654, 184, 0.58, 0.58)
        .curve_to((654, 286), (590, 348), (482, 374), smooth=False)
        .curve_to((544, 412), (582, 470), (582, 540), smooth=False)
        .curve_to((582, 628), (502, cap), (390, cap), smooth=False)
        .line_to(180, cap)
    )
    return union_contours([stem, bowls])


def _serif_bold_germandbls(p: SerifWeightParams) -> List[ContourBuilder]:
    foot = foot_pad_ccw(70, 206, 0, ext_l=44, ext_r=0, sh=34, brk=32)
    return union_contours(_sans_bold_germandbls() + [foot])


def _serif_bold_Eng(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    sL = vstem_serifed(82, 156, 0, cap, bl=44, br=44, tl=44, sh=36, brk=34)
    sR_t = head_pad_ccw(586, 660, cap, ext_l=44, ext_r=44, sh=36, brk=34)
    diag_hook = (
        ContourBuilder((544, 0))
        .line_to(586, 0)
        .line_to(586, -64)
        .vh_to(456, -162, 0.58, 0.58)
        .curve_to((424, -162), (394, -152), (370, -134), smooth=False)
        .line_to(342, -192)
        .curve_to((378, -216), (418, -224), (464, -224), smooth=True)
        .hv_to(660, -62, 0.58, 0.58)
        .line_to(660, cap)
        .line_to(586, cap)
        .line_to(586, 128)
        .line_to(220, cap)
        .line_to(96, cap)
    )
    return union_contours([sL, sR_t, diag_hook])


def _serif_bold_yen(serif_bold_cap_Y: List[ContourBuilder]) -> List[ContourBuilder]:
    b1 = rect_contour(84, 148, 496, 206)
    b2 = rect_contour(84, 274, 496, 332)
    return union_contours(serif_bold_cap_Y + [b1, b2])


# ---------------------------------------------------------------------------
# Mono Bold (600u Fixed Pitch) Explicit Builders
# ---------------------------------------------------------------------------

def _mono_bold_A() -> List[ContourBuilder]:
    cap = METRICS.cap_height
    yb0, yb1 = 186, 276  # 90u bar
    xl_b0 = lerp_x(148, 0, 294, 558, yb0)
    xr_b0 = lerp_x(452, 0, 306, 558, yb0)
    xl_b1 = lerp_x(148, 0, 294, 558, yb1)
    xr_b1 = lerp_x(452, 0, 306, 558, yb1)
    outer = (
        ContourBuilder((28, 0))
        .line_to(148, 0)
        .line_to(xl_b0, yb0)
        .line_to(xr_b0, yb0)
        .line_to(452, 0)
        .line_to(572, 0)
        .line_to(370, cap)
        .line_to(230, cap)
    )
    inner = ContourBuilder((xl_b1, yb1)).line_to(294, 558).line_to(306, 558).line_to(xr_b1, yb1)
    return [outer, inner]


def _mono_bold_M() -> List[ContourBuilder]:
    # 108u outer stems (36..144, 456..564) + open suspended V
    cap = METRICS.cap_height
    c = (
        ContourBuilder((36, 0))
        .line_to(144, 0)
        .line_to(144, 488)
        .line_to(152, 488)
        .line_to(262, 166)
        .line_to(338, 166)
        .line_to(448, 488)
        .line_to(456, 488)
        .line_to(456, 0)
        .line_to(564, 0)
        .line_to(564, cap)
        .line_to(436, cap)
        .line_to(304, 316)
        .line_to(296, 316)
        .line_to(164, cap)
        .line_to(36, cap)
    )
    return [c]


def _mono_bold_W() -> List[ContourBuilder]:
    cap = METRICS.cap_height
    c = (
        ContourBuilder((116, 0))
        .line_to(226, 0)
        .line_to(295, 344)
        .line_to(305, 344)
        .line_to(374, 0)
        .line_to(484, 0)
        .line_to(576, cap)
        .line_to(472, cap)
        .line_to(424, 178)
        .line_to(416, 178)
        .line_to(344, 504)
        .line_to(256, 504)
        .line_to(184, 178)
        .line_to(176, 178)
        .line_to(128, cap)
        .line_to(24, cap)
    )
    return [c]


def _mono_bold_Q(mono_bold_O: List[ContourBuilder]) -> List[ContourBuilder]:
    tail = (
        ContourBuilder((512, -96))
        .curve_to((536, -96), (554, -92), (570, -82), smooth=False)
        .line_to(550, -6)
        .curve_to((538, -10), (528, -12), (516, -12), smooth=True)
        .curve_to((484, -12), (464, 16), (434, 72), smooth=False)
        .line_to(328, 72)
        .curve_to((388, -36), (438, -96), (512, -96), smooth=True)
    )
    return union_contours([mono_bold_O[0], mono_bold_O[1], tail])


def _mono_bold_m() -> List[ContourBuilder]:
    # Three exact 106u stems inside 600u cell (28..134, 247..353, 466..572) -> two clear 113u counters!
    xh = METRICS.x_height
    top = xh + 12
    c = (
        ContourBuilder((28, 0))
        .line_to(134, 0)
        .line_to(134, 340)
        .curve_to((134, 398), (156, 434), (190, 434), smooth=True)
        .hv_to(247, 340, 0.56, 0.58)
        .line_to(247, 0)
        .line_to(353, 0)
        .line_to(353, 340)
        .curve_to((353, 398), (375, 434), (409, 434), smooth=True)
        .hv_to(466, 340, 0.56, 0.58)
        .line_to(466, 0)
        .line_to(572, 0)
        .line_to(572, 354)
        .vh_to(436, top, 0.58, 0.58)
        .curve_to((390, top), (354, 502), (334, 452), smooth=False)
        .curve_to((314, 502), (274, top), (218, top), smooth=False)
        .curve_to((168, top), (138, 502), (118, 452), smooth=False)
        .line_to(116, xh)
        .line_to(28, xh)
    )
    return [c]


def _mono_bold_w() -> List[ContourBuilder]:
    xh = METRICS.x_height
    c = (
        ContourBuilder((116, 0))
        .line_to(224, 0)
        .line_to(295, 274)
        .line_to(305, 274)
        .line_to(376, 0)
        .line_to(484, 0)
        .line_to(576, xh)
        .line_to(474, xh)
        .line_to(424, 152)
        .line_to(416, 152)
        .line_to(344, 392)
        .line_to(256, 392)
        .line_to(184, 152)
        .line_to(176, 152)
        .line_to(126, xh)
        .line_to(24, xh)
    )
    return [c]


def _mono_bold_AE() -> List[ContourBuilder]:
    cap = METRICS.cap_height
    yb0, yb1 = 186, 276
    xl_b0 = lerp_x(128, 0, 272, 540, yb0)
    xl_b1 = lerp_x(128, 0, 272, 540, yb1)
    outer = (
        ContourBuilder((24, 0))
        .line_to(128, 0)
        .line_to(xl_b0, yb0)
        .line_to(272, yb0)
        .line_to(272, 0)
        .line_to(572, 0)
        .line_to(572, 92)
        .line_to(372, 92)
        .line_to(372, 314)
        .line_to(542, 314)
        .line_to(542, 404)
        .line_to(372, 404)
        .line_to(372, cap - 92)
        .line_to(566, cap - 92)
        .line_to(566, cap)
        .line_to(240, cap)
    )
    inner = ContourBuilder((xl_b1, yb1)).line_to(266, 540).line_to(272, 540).line_to(272, yb1)
    return [outer, inner]


def _mono_bold_OE() -> List[ContourBuilder]:
    cap = METRICS.cap_height
    top, bot = cap + 12, -12
    o_out = (
        ContourBuilder((226, bot))
        .curve_to((266, bot), (288, -6), (288, 0), smooth=False)
        .line_to(572, 0)
        .line_to(572, 92)
        .line_to(384, 92)
        .line_to(384, 314)
        .line_to(544, 314)
        .line_to(544, 404)
        .line_to(384, 404)
        .line_to(384, cap - 92)
        .line_to(566, cap - 92)
        .line_to(566, cap)
        .line_to(288, cap)
        .curve_to((288, cap + 6), (266, top), (226, top), smooth=False)
        .hv_to(26, 350, 0.585, 0.59)
        .vh_to(226, bot, 0.59, 0.585)
    )
    o_in = (
        ContourBuilder((228, 78))
        .hv_to(130, 350, 0.59, 0.60)
        .vh_to(228, 622, 0.60, 0.59)
        .hv_to(280, 528, 0.56, 0.56)
        .line_to(280, 172)
        .vh_to(228, 78, 0.56, 0.56)
    )
    return [o_out, o_in]


def _mono_bold_ae() -> List[ContourBuilder]:
    top, bot = 532, -12
    outer = (
        ContourBuilder((162, bot))
        .curve_to((206, bot), (238, 4), (262, 34), smooth=False)
        .line_to(276, 34)
        .curve_to((308, 4), (356, bot), (424, bot), smooth=True)
        .curve_to((492, bot), (538, 22), (568, 76), smooth=False)
        .line_to(506, 134)
        .curve_to((484, 96), (456, 78), (426, 78), smooth=True)
        .curve_to((374, 78), (344, 120), (340, 214), smooth=False)
        .line_to(574, 214)
        .line_to(574, 276)
        .vh_to(422, top, 0.58, 0.58)
        .curve_to((364, top), (314, 502), (282, 444), smooth=False)
        .line_to(272, 444)
        .curve_to((242, 502), (198, top), (154, top), smooth=True)
        .hv_to(44, 412, 0.58, 0.58)
        .line_to(108, 372)
        .hv_to(164, 438, 0.56, 0.58)
        .hv_to(228, 348, 0.56, 0.56)
        .line_to(228, 306)
        .curve_to((158, 300), (26, 260), (26, 134), smooth=True)
        .vh_to(162, bot, 0.585, 0.585)
    )
    in_a = (
        ContourBuilder((172, 70))
        .hv_to(122, 136, 0.58, 0.58)
        .curve_to((122, 196), (186, 232), (242, 236), smooth=False)
        .line_to(242, 134)
        .vh_to(172, 70, 0.56, 0.58)
    )
    in_e = (
        ContourBuilder((342, 290))
        .line_to(342, 340)
        .vh_to(422, 442, 0.56, 0.58)
        .curve_to((458, 442), (482, 384), (486, 290), smooth=False)
    )
    return [outer, in_a, in_e]


def _mono_bold_percent() -> List[ContourBuilder]:
    top_o = humanist_oval_contour(162, 530, 128, 168, 0.59, 0.59, clockwise=False)
    top_i = humanist_oval_contour(162, 530, 44, 88, 0.60, 0.60, clockwise=True)
    bot_o = humanist_oval_contour(438, 160, 128, 168, 0.59, 0.59, clockwise=False)
    bot_i = humanist_oval_contour(438, 160, 44, 88, 0.60, 0.60, clockwise=True)
    slash = ContourBuilder((116, -8)).line_to(206, -8).line_to(484, 698).line_to(394, 698)
    return [top_o, top_i, bot_o, bot_i, slash]


def _mono_bold_IJ(bold_I: List[ContourBuilder], bold_J: List[ContourBuilder]) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    bh = 92
    i_part = (
        ContourBuilder((36, 0))
        .line_to(252, 0)
        .line_to(252, bh)
        .line_to(198, bh)
        .line_to(198, cap - bh)
        .line_to(252, cap - bh)
        .line_to(252, cap)
        .line_to(36, cap)
        .line_to(36, cap - bh)
        .line_to(90, cap - bh)
        .line_to(90, bh)
        .line_to(36, bh)
    )
    j_part = (
        ContourBuilder((384, -12))
        .hv_to(540, 186, 0.58, 0.58)
        .line_to(540, cap)
        .line_to(328, cap)
        .line_to(328, cap - bh)
        .line_to(432, cap - bh)
        .line_to(432, 186)
        .vh_to(380, 78, 0.58, 0.58)
        .curve_to((352, 78), (328, 96), (308, 128), smooth=False)
        .line_to(248, 70)
        .curve_to((280, 16), (324, -12), (384, -12), smooth=True)
    )
    return [i_part, j_part]


def _mono_bold_napostrophe(bold_n: List[ContourBuilder]) -> List[ContourBuilder]:
    q = [c.translated(-206, 0) for c in _bold_quoteright(mono=True)]
    n_c = (
        ContourBuilder((176, 0))
        .line_to(284, 0)
        .line_to(284, 316)
        .vh_to(378, 434, 0.56, 0.58)
        .hv_to(456, 336, 0.56, 0.58)
        .line_to(456, 0)
        .line_to(564, 0)
        .line_to(564, 344)
        .vh_to(390, 532, 0.58, 0.58)
        .curve_to((336, 532), (296, 502), (272, 452), smooth=False)
        .line_to(270, 520)
        .line_to(176, 520)
    )
    return q + [n_c]


def _mono_bold_ss01_ligatures() -> Dict[str, List[ContourBuilder]]:
    """600u fixed-pitch ss01 ligatures thickened cleanly to 88u bars matching Mono Bold operators."""
    # Axis y_mid = 276 -> bar y: 232..320 (88u)
    return {
        "hyphen.lig_r": [rect_contour(70, 232, 600, 320)],
        "greater.lig_arrow": union_contours([
            rect_contour(0, 232, 456, 320),
            ContourBuilder((226, 76)).line_to(288, 14).line_to(532, 266).line_to(532, 286).line_to(288, 538).line_to(226, 476).line_to(428, 276),
        ]),
        "less.lig_arrow": union_contours([
            rect_contour(144, 232, 600, 320),
            ContourBuilder((68, 266)).line_to(312, 14).line_to(374, 76).line_to(172, 276).line_to(374, 476).line_to(312, 538).line_to(68, 286),
        ]),
        "hyphen.lig_l": [rect_contour(0, 232, 530, 320)],
        "equal.lig_r": [rect_contour(70, 144, 600, 230), rect_contour(70, 322, 600, 408)],
        "equal.lig_l": [rect_contour(0, 144, 530, 230), rect_contour(0, 322, 530, 408)],
        "greater.lig_fatarrow": union_contours([
            rect_contour(0, 144, 372, 230),
            rect_contour(0, 322, 372, 408),
            ContourBuilder((220, 82)).line_to(284, 20).line_to(528, 266).line_to(528, 286).line_to(284, 532).line_to(220, 470).line_to(412, 276),
        ]),
        "exclam.lig_neq": union_contours([
            rect_contour(86, 144, 600, 230),
            rect_contour(86, 322, 600, 408),
            bar_segment_contour((352, 26), (552, 526), 88),
        ]),
        "less.lig_le": [
            ContourBuilder((86, 344)).line_to(600, 240).line_to(600, 326).line_to(272, 374).line_to(600, 422).line_to(600, 508).line_to(86, 404),
            rect_contour(86, 38, 600, 126),
        ],
        "equal.lig_le": [
            ContourBuilder((0, 240)).line_to(476, 160).line_to(496, 242).line_to(0, 326),
            ContourBuilder((0, 422)).line_to(496, 510).line_to(476, 594).line_to(0, 508),
            rect_contour(0, 38, 514, 126),
        ],
        "greater.lig_ge": [
            ContourBuilder((124, 160)).line_to(600, 240).line_to(600, 326).line_to(104, 242),
            ContourBuilder((104, 510)).line_to(600, 422).line_to(600, 508).line_to(124, 594),
            rect_contour(86, 38, 600, 126),
        ],
        "equal.lig_ge": [
            ContourBuilder((0, 240)).line_to(514, 344).line_to(514, 404).line_to(0, 508).line_to(0, 422).line_to(328, 374).line_to(0, 326),
            rect_contour(0, 38, 514, 126),
        ],
    }


# ---------------------------------------------------------------------------
# Derived / Overlay Glyph Reconstructor & Master Family Builders
# ---------------------------------------------------------------------------

def _rebuild_derived_bold(
    result: Dict[str, Tuple[int, int | None, List[ContourBuilder]]],
    reg_widths: Dict[str, int],
    *,
    is_serif: bool = False,
    is_mono: bool = False,
) -> None:
    """Reconstruct tabular digits, slashes, bars, fractions & .case variants from clean Bold bases."""
    bar_t = 60.0 if is_serif else (88.0 if is_mono else 86.0)
    thin_t = 58.0 if is_serif else 82.0

    def _set(name: str, contours: List[ContourBuilder]) -> None:
        w, uni, _ = result[name]
        result[name] = (w, uni, contours)

    # Zero slashed + tabular numerals
    slash_box = (
        bar_segment_contour((156, 86), (444, 604), thin_t)
        if is_mono
        else bar_segment_contour((138, 86), (456, 604), thin_t)
    )
    z_rings = result["zero"][2][:2]
    _set("zero.slash", union_contours(z_rings + [slash_box]))
    if is_mono:
        for d in ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"):
            _set(f"{d}.tnum", result[d][2])
        _set("zero.tnum.slash", result["zero.slash"][2])
    else:
        for d in ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"):
            w_prop = result[d][0]
            dx = (TABULAR_FIG_WIDTH - w_prop) / 2.0
            _set(f"{d}.tnum", [c.translated(dx, 0) for c in result[d][2]])
        dx0 = (TABULAR_FIG_WIDTH - result["zero.slash"][0]) / 2.0
        _set("zero.tnum.slash", [c.translated(dx0, 0) for c in result["zero.slash"][2]])

    # European overlay glyphs from Bold bases (clean union -> no bowtie artifacts!)
    wO = result["O"][0]
    _set("Oslash", union_contours(result["O"][2] + [bar_segment_contour((86, -38), (wO - 86, 738), thin_t)]))
    wo = result["o"][0]
    _set("oslash", union_contours(result["o"][2] + [bar_segment_contour((76, -32), (wo - 76, 552), thin_t)]))
    _set("Eth", union_contours(result["D"][2] + [rect_contour(16, 318, 316, 318 + bar_t)]))
    _set("Dcroat", result["Eth"][2])
    _set("dcroat", union_contours(result["d"][2] + [rect_contour(result["d"][0] - 310, 560, result["d"][0] - 20, 560 + bar_t)]))
    _set("Hbar", union_contours(result["H"][2] + [rect_contour(24, 502, result["H"][0] - 24, 502 + bar_t)]))
    _set("hbar", union_contours(result["h"][2] + [rect_contour(18, 566, 326, 566 + bar_t)]))
    _set("Tbar", union_contours(result["T"][2] + [rect_contour(result["T"][0] * 0.20, 328, result["T"][0] * 0.80, 328 + bar_t)]))
    _set("tbar", union_contours(result["t"][2] + [rect_contour(36, 236, result["t"][0] - 58, 236 + bar_t)]))
    _set("Lslash", union_contours(result["L"][2] + [bar_segment_contour((18, 250), (288, 450), bar_t)]))
    if is_mono:
        _set("lslash", union_contours(result["l"][2] + [bar_segment_contour((160, 306), (424, 472), 72.0)]))
    else:
        l_sh = [c.translated(12, 0) for c in result["l"][2]]
        _set("lslash", union_contours(l_sh + [bar_segment_contour((18, 304), (274, 474), bar_t)]))

    # Dotless i/j & IJ / ij / Ldot / ldot / napostrophe
    _set("dotlessi", result["i"][2][:1])
    _set("dotlessj", result["j"][2][:1])
    if is_mono:
        _set("ldot", [c.translated(-42, 0) for c in result["l"][2]] + [humanist_oval_contour(424, 286, 54, 54, 0.62, 0.62, clockwise=False)])
        _set("Ldot", result["L"][2] + [humanist_oval_contour(360, 368, 56, 56, 0.62, 0.62, clockwise=False)])
    else:
        _set("IJ", result["I"][2] + [c.translated(312, 0) for c in result["J"][2]])
        _set("ij", result["i"][2] + [c.translated(264, 0) for c in result["j"][2]])
        _set("Ldot", result["L"][2] + [humanist_oval_contour(376, 368, 58, 58, 0.62, 0.62, clockwise=False)])
        _set("ldot", result["l"][2] + [humanist_oval_contour(326, 286, 54, 54, 0.62, 0.62, clockwise=False)])
        _set("napostrophe", [c.translated(-24, 0) for c in result["quoteright"][2]] + [c.translated(180, 0) for c in result["n"][2]])

    # Dollar, cent, won, lessequal, greaterequal, fractions, superscripts
    if not is_mono:
        s_sh = [c.translated(6, 0) for c in result["S"][2]]
        if not is_serif:
            s_sh = _scale_contours(result["S"][2], 580.0 / result["S"][0], 1.0, 0.0, 0.0)
        _set("dollar", union_contours(s_sh + [rect_contour(250, -92, 330 if not is_serif else 320, 784)]))
    else:
        _set("dollar", union_contours(result["S"][2] + [rect_contour(264, -92, 336, 784)]))

    c_sh = _scale_contours(result["c"][2], result["cent"][0] / result["c"][0], 1.0, 0.0, 0.0)
    cx_cent = result["cent"][0] / 2.0
    cb_w = 30.0 if is_serif else 38.0
    _set("cent", union_contours(c_sh + [rect_contour(cx_cent - cb_w, -96, cx_cent + cb_w, 616)]))

    wW = result["W"][0]
    _set("won", union_contours(result["W"][2] + [rect_contour(24, 218, wW - 24, 218 + bar_t), rect_contour(24, 382, wW - 24, 382 + bar_t)]))

    if "notequal" in result:
        _set("notequal", union_contours(result["equal"][2] + [bar_segment_contour((160, 44), (420, 508), thin_t)]))
    _set("approxequal", [c.translated(0, -148) for c in result["asciitilde"][2]] + [c.translated(0, 32) for c in result["asciitilde"][2]])
    _set("lessequal", _bold_lessequal(result["less"][2], dx=10.0 if is_mono else 0.0))
    _set("greaterequal", _bold_greaterequal(result["greater"][2], dx=10.0 if is_mono else 0.0))

    # Exclamdown, Questiondown, Superscripts & Fractions
    _set("exclamdown", _rotate_180(result["exclam"][2], result["exclam"][0] / 2.0, 260))
    _set("questiondown", _rotate_180(result["question"][2], result["question"][0] / 2.0, 260))
    _set("onesuperior", _bold_superscript(result["one"][2], 24, 296))
    _set("twosuperior", _bold_superscript(result["two"][2], 20, 304))
    _set("threesuperior", _bold_superscript(result["three"][2], 20, 304))

    dx_den = 292.0 if is_mono else 428.0
    if not is_mono:
        _set("onequarter", _bold_fraction(result["one"][2], result["four"][2], dx_den))
        _set("onehalf", _bold_fraction(result["one"][2], result["two"][2], dx_den))
        _set("threequarters", _bold_fraction(result["three"][2], result["four"][2], dx_den))
    else:
        for fn, a, b in (("onequarter", "one", "four"), ("onehalf", "one", "two"), ("threequarters", "three", "four")):
            num = _scale_contours(result[a][2], 0.50, 0.50, 24, 338)
            den = _scale_contours(result[b][2], 0.50, 0.50, 286, 0)
            slash = ContourBuilder((162, -12)).line_to(242, -12).line_to(478, 704).line_to(398, 704)
            _set(fn, num + [slash] + den)

    # Spacing modifier clones & .case punctuation
    for sp_name, comb_name, dx_c in (
        ("acute", "acutecomb", 160), ("dieresis", "dieresiscomb", 180), ("macron", "macroncomb", 180),
        ("cedilla", "cedillacomb", 160), ("breve", "brevecomb", 180), ("dotaccent", "dotaccentcomb", 150),
        ("ring", "ringabovecomb", 160), ("ogonek", "ogonekcomb", 160), ("tilde", "tildecomb", 210),
        ("hungarumlaut", "hungarumlautcomb", 190), ("circumflex", "circumflexcomb", 180), ("caron", "caroncomb", 180),
    ):
        if is_mono:
            dx_c = 300
        elif sp_name in result:
            dx_c = result[sp_name][0] / 2.0
        _set(sp_name, [c.translated(dx_c, 0) for c in result[comb_name][2]])

    for name in list(result.keys()):
        if name.endswith(".case"):
            base_n = name[:-5]
            if base_n in result:
                _set(name, [c.translated(0, METRICS.case_shift_y) for c in result[base_n][2]])
    if "hyphentwo" in result:
        _set("hyphentwo", result["hyphen"][2])
    if "nonbreakinghyphen" in result:
        _set("nonbreakinghyphen", result["hyphen"][2])
    if "softhyphen" in result:
        _set("softhyphen", result["hyphen"][2])
    if "hyphentwo.case" in result:
        _set("hyphentwo.case", result["hyphen.case"][2])
    if "nonbreakinghyphen.case" in result:
        _set("nonbreakinghyphen.case", result["hyphen.case"][2])
    # Review 3: a prime is a straight tapered stroke (it was a copy of the curly quote here)
    _set("minute", [ContourBuilder((70, 446)).line_to(146, 446).line_to(208, 708).line_to(102, 708)] if not is_mono else result["minute"][2])
    _set("second", ([c.translated(-16, 0) for c in result["minute"][2]] + [c.translated(148, 0) for c in result["minute"][2]]) if not is_mono else result["second"][2])


def build_all_sans_bold_glyphs() -> Dict[str, Tuple[int, int | None, List[ContourBuilder]]]:
    reg = build_all_sans_glyphs()
    result: Dict[str, Tuple[int, int | None, List[ContourBuilder]]] = {}
    reg_widths = {k: v[0] for k, v in reg.items()}

    explicit: Dict[str, Callable[[], List[ContourBuilder]]] = {
        "A": _sans_bold_A,
        "four": lambda: _sans_bold_four(0.0),
        "eight": lambda: _sans_bold_eight(0.0),
        "quoteleft": lambda: _bold_quoteleft(False),
        "quoteright": lambda: _bold_quoteright(False),
        "quotedblleft": lambda: _bold_quotedblleft(False),
        "quotedblright": lambda: _bold_quotedblright(False),
        "quotesinglbase": lambda: _bold_quotesinglbase(False),
        "quotedblbase": lambda: _bold_quotedblbase(False),
        "AE": _sans_bold_AE,
        "OE": _sans_bold_OE,
        "ae": _sans_bold_ae,
        "oe": _sans_bold_oe,
        "Germandbls": _sans_bold_Germandbls,
        "germandbls": _sans_bold_germandbls,
        "at": lambda: _bold_at(904),
        "section": lambda: _bold_section(18.0),
        "trademark": _bold_trademark,
        "infinity": _bold_infinity,
        "Delta": _bold_Delta,
        "increment": _bold_Delta,
        "ordfeminine": _bold_ordfeminine,
        "ordmasculine": _bold_ordmasculine,
        "perthousand": lambda: _bold_perthousand(1060),
        "numero": lambda: _bold_numero(988),
    }

    for gname, (orig_w, uni, contours) in reg.items():
        nw = compute_duplex_bold_width(gname, orig_w)
        if gname in explicit:
            result[gname] = (nw, uni, explicit[gname]())
        elif gname == ".notdef":
            result[gname] = (nw, uni, [rect_contour(64, 0, 536, 700, False), rect_contour(156, 92, 444, 608, True)])
        elif gname == "euro":
            # Clean open Bold euro inside 580u (c contour untouched in ring)
            eb = bolden_contours_smooth(contours, orig_w, nw, 18.0, 12.0)
            result[gname] = (nw, uni, eb)
        elif orig_w == 0:
            eb = bolden_contours_smooth(contours, 0, 0, 13.0, 8.5, is_mark=True)
            result[gname] = (0, uni, eb)
        else:
            eb = bolden_contours_smooth(contours, orig_w, nw, SANS_BOLD_RX, SANS_BOLD_RY)
            result[gname] = (nw, uni, eb)

    _rebuild_derived_bold(result, reg_widths, is_serif=False, is_mono=False)
    return result


def build_all_serif_bold_glyphs() -> Dict[str, Tuple[int, int | None, List[ContourBuilder]]]:
    reg = build_all_serif_glyphs(SERIF_REGULAR)
    result: Dict[str, Tuple[int, int | None, List[ContourBuilder]]] = {}
    reg_widths = {k: v[0] for k, v in reg.items()}

    sb = SERIF_BOLD
    explicit: Dict[str, Callable[[], List[ContourBuilder]]] = {
        "A": lambda: _serif_bold_A(sb),
        "K": lambda: _serif_bold_K(sb),
        "M": lambda: _serif_bold_M(sb),
        "N": lambda: _serif_bold_N(sb),
        "U": lambda: _serif_bold_U(sb),
        "V": lambda: _serif_bold_V(sb),
        "W": lambda: _serif_bold_W(sb),
        "X": lambda: _serif_bold_X(sb),
        "Y": lambda: _serif_bold_Y(sb),
        "g": lambda: _serif_bold_g(sb),
        "k": lambda: _serif_bold_k(sb),
        "v": lambda: _serif_bold_v(sb),
        "w": lambda: _serif_bold_w(sb),
        "x": lambda: _serif_bold_x(sb),
        "y": lambda: _serif_bold_y(sb),
        "four": lambda: _serif_bold_four(0.0),
        "AE": lambda: _serif_bold_AE(sb),
        "OE": lambda: _serif_bold_OE(sb),
        "ae": lambda: _serif_bold_ae(sb),
        "oe": lambda: _serif_bold_oe(sb),
        "Germandbls": lambda: _serif_bold_Germandbls(sb),
        "germandbls": lambda: _serif_bold_germandbls(sb),
        "Eng": lambda: _serif_bold_Eng(sb),
        "quoteleft": lambda: _bold_quoteleft(False),
        "quoteright": lambda: _bold_quoteright(False),
        "quotedblleft": lambda: _bold_quotedblleft(False),
        "quotedblright": lambda: _bold_quotedblright(False),
        "quotesinglbase": lambda: _bold_quotesinglbase(False),
        "quotedblbase": lambda: _bold_quotedblbase(False),
        "at": lambda: _bold_at(904),
        "section": lambda: _bold_section(18.0),
        "trademark": _bold_trademark,
        "infinity": _bold_infinity,
        "Delta": _bold_Delta,
        "increment": _bold_Delta,
        "ordfeminine": _bold_ordfeminine,
        "ordmasculine": _bold_ordmasculine,
        "perthousand": lambda: _bold_perthousand(1060),
        "numero": lambda: _bold_numero(988),
    }

    for gname, (orig_w, uni, contours) in reg.items():
        nw = compute_duplex_bold_width(gname, orig_w)
        if gname in explicit:
            result[gname] = (nw, uni, explicit[gname]())
        elif gname == ".notdef":
            result[gname] = (nw, uni, [rect_contour(64, 0, 536, 700, False), rect_contour(156, 92, 444, 608, True)])
        elif gname == "euro":
            result[gname] = (nw, uni, bolden_contours_smooth(contours, orig_w, nw, 18.0, 5.5))
        elif orig_w == 0:
            result[gname] = (0, uni, bolden_contours_smooth(contours, 0, 0, 13.0, 8.5, is_mark=True))
        else:
            result[gname] = (nw, uni, bolden_contours_smooth(contours, orig_w, nw, SERIF_BOLD_RX, SERIF_BOLD_RY))

    # Build Serif Bold Q and yen cleanly on Serif Bold O & Y
    q_tail = (
        ContourBuilder((372, 26))
        .curve_to((434, -64), (522, -122), (636, -122), smooth=True)
        .curve_to((660, -122), (680, -116), (696, -108), smooth=False)
        .line_to(680, -64)
        .curve_to((598, -64), (534, -14), (476, 68), smooth=False)
    )
    result["Q"] = (result["Q"][0], result["Q"][1], union_contours(result["O"][2] + [q_tail]))
    result["yen"] = (result["yen"][0], result["yen"][1], _serif_bold_yen(result["Y"][2]))
    _rebuild_derived_bold(result, reg_widths, is_serif=True, is_mono=False)
    return result


def build_all_mono_bold_glyphs() -> Dict[str, Tuple[int, int | None, List[ContourBuilder]]]:
    reg = build_all_mono_glyphs(MONO_REGULAR)
    result: Dict[str, Tuple[int, int | None, List[ContourBuilder]]] = {}
    reg_widths = {k: v[0] for k, v in reg.items()}

    explicit: Dict[str, Callable[[], List[ContourBuilder]]] = {
        "A": _mono_bold_A,
        "M": _mono_bold_M,
        "W": _mono_bold_W,
        "m": _mono_bold_m,
        "w": _mono_bold_w,
        "four": lambda: _sans_bold_four(-4.0),
        "AE": _mono_bold_AE,
        "OE": _mono_bold_OE,
        "ae": _mono_bold_ae,
        "quoteleft": lambda: _bold_quoteleft(True),
        "quoteright": lambda: _bold_quoteright(True),
        "quotedblleft": lambda: _bold_quotedblleft(True),
        "quotedblright": lambda: _bold_quotedblright(True),
        "quotesinglbase": lambda: _bold_quotesinglbase(True),
        "quotedblbase": lambda: _bold_quotedblbase(True),
        "at": lambda: _bold_at(600),
        "percent": _mono_bold_percent,
        "section": lambda: _bold_section(40.0),
        "Delta": lambda: _scale_contours(_bold_Delta(), 0.86, 1.0, 18, 0),
        "increment": lambda: _scale_contours(_bold_Delta(), 0.86, 1.0, 18, 0),
        "perthousand": lambda: _scale_contours(_bold_perthousand(1060), 0.54, 1.0, 14, 0),
    }

    ss01_map = _mono_bold_ss01_ligatures()
    for gname, (orig_w, uni, contours) in reg.items():
        if gname in ss01_map:
            result[gname] = (MONO_WIDTH, None, ss01_map[gname])
        elif gname in explicit:
            result[gname] = (MONO_WIDTH, uni, explicit[gname]())
        elif gname == ".notdef":
            result[gname] = (MONO_WIDTH, uni, [rect_contour(64, 0, 536, 700, False), rect_contour(156, 92, 444, 608, True)])
        elif orig_w == 0:
            result[gname] = (0, uni, bolden_contours_smooth(contours, 0, 0, 13.0, 8.5, is_mark=True))
        elif gname in ("oe", "Germandbls", "germandbls", "trademark", "infinity", "ordfeminine", "ordmasculine", "numero"):
            w_prop = compute_duplex_bold_width(gname, EXT_CONTOUR_BUILDERS[gname][0] if gname in EXT_CONTOUR_BUILDERS else DUPLEX_ADVANCE_WIDTHS[gname])
            src_map = {
                "oe": _sans_bold_oe,
                "Germandbls": _sans_bold_Germandbls,
                "germandbls": _sans_bold_germandbls,
                "trademark": _bold_trademark,
                "infinity": _bold_infinity,
                "ordfeminine": _bold_ordfeminine,
                "ordmasculine": _bold_ordmasculine,
                "numero": lambda: _bold_numero(988),
            }
            raw_b = src_map[gname]()
            sx = min(1.0, 548.0 / w_prop)
            dx = 300.0 - (w_prop / 2.0) * sx
            result[gname] = (MONO_WIDTH, uni, _scale_contours(raw_b, sx, 1.0, dx, 0.0))
        else:
            result[gname] = (MONO_WIDTH, uni, bolden_contours_smooth(contours, MONO_WIDTH, MONO_WIDTH, MONO_BOLD_RX, MONO_BOLD_RY))

    # Build Q, IJ, ij, napostrophe cleanly on Mono Bold primitives
    result["Q"] = (MONO_WIDTH, UNICODE_MAP["Q"], _mono_bold_Q(result["O"][2]))
    result["IJ"] = (MONO_WIDTH, reg["IJ"][1], _mono_bold_IJ(result["I"][2], result["J"][2]))
    i_compact = [c.translated(-136, 0) for c in result["i"][2]]
    j_compact = [c.translated(96, 0) for c in result["j"][2]]
    result["ij"] = (MONO_WIDTH, reg["ij"][1], i_compact + j_compact)
    result["napostrophe"] = (MONO_WIDTH, reg["napostrophe"][1], _mono_bold_napostrophe(result["n"][2]))
    _rebuild_derived_bold(result, reg_widths, is_serif=False, is_mono=True)
    return result


# ---------------------------------------------------------------------------
# Bold Anchor Placement, Composites & Kerning
# ---------------------------------------------------------------------------

def attach_bold_anchors_and_composites(ufo: ufoLib2.Font, *, is_monospace: bool = False) -> None:
    """Attach scaled/centered anchors and depth-1 flattened composites with propagated anchors."""
    from fontTools.pens.boundsPen import BoundsPen

    # Adjusted .cap mark top anchors for Bold mark stroke thickness (stays <= 978u!)
    mark_anchors_bold = dict(MARK_ANCHORS)
    mark_anchors_bold["dieresiscomb.cap"] = {"_top": (0, 700), "top": (0, 810)}
    mark_anchors_bold["macroncomb.cap"] = {"_top": (0, 700), "top": (0, 814)}
    mark_anchors_bold["acutecomb.cap"] = {"_top": (0, 700), "top": (0, 864)}
    mark_anchors_bold["gravecomb.cap"] = {"_top": (0, 700), "top": (0, 864)}
    mark_anchors_bold["caroncomb.cap"] = {"_top": (0, 700), "top": (0, 864)}

    for mname, adict in mark_anchors_bold.items():
        if mname in ufo:
            ufo[mname].anchors = [
                ufoLib2.objects.Anchor(x=ax, y=ay, name=aname)
                for aname, (ax, ay) in adict.items()
            ]

    reg_widths_all = dict(DUPLEX_ADVANCE_WIDTHS)
    for gn, (rw, _, _) in EXT_CONTOUR_BUILDERS.items():
        reg_widths_all[gn] = rw

    special_top_x_mono = {
        "L": 124.0, "b": 129.0, "d": 471.0, "h": 127.0, "k": 155.0,
        "l": 295.0, "t": 244.0, "i": 300.0, "dotlessi": 300.0, "j": 338.0, "dotlessj": 338.0,
    }
    special_ogonek_mono = {
        "A": (516.0, 0.0), "E": (468.0, 0.0), "I": (312.0, 0.0), "U": (494.0, 4.0),
        "a": (462.0, 0.0), "e": (416.0, 12.0), "i": (343.0, 0.0), "dotlessi": (343.0, 0.0), "u": (469.0, 0.0),
    }

    for bname, orig_anchors in BASE_ANCHORS.items():
        if bname not in ufo:
            continue
        g = ufo[bname]
        if is_monospace:
            bpen = BoundsPen(ufo)
            g.draw(bpen)
            cx = round((bpen.bounds[0] + bpen.bounds[2]) / 2.0) if bpen.bounds else 300.0
            new_a = []
            for aname, (_, ay) in orig_anchors.items():
                if aname == "top":
                    new_a.append(ufoLib2.objects.Anchor(x=special_top_x_mono.get(bname, cx), y=ay, name="top"))
                elif aname == "bottom":
                    new_a.append(ufoLib2.objects.Anchor(x=295.0 if bname == "l" else cx, y=ay, name="bottom"))
                elif aname == "ogonek":
                    ox, oy = special_ogonek_mono.get(bname, (cx + 80.0, ay))
                    new_a.append(ufoLib2.objects.Anchor(x=ox, y=oy, name="ogonek"))
            g.anchors = new_a
        else:
            rw = reg_widths_all.get(bname, g.width)
            sx = g.width / rw if rw > 0 else 1.0
            g.anchors = [
                ufoLib2.objects.Anchor(x=round(ax * sx), y=ay, name=aname)
                for aname, (ax, ay) in orig_anchors.items()
            ]

    glyph_order = list(ufo.lib.get("public.glyphOrder", []))
    for comp_name, uni, base_name, mark_name, anchor_name in COMPOSITE_RECIPES:
        base_g = ufo[base_name]
        mark_g = ufo[mark_name]

        if comp_name in ("dcaron", "lcaron", "tcaron", "Lcaron"):
            if is_monospace:
                dx_map = {"dcaron": 546, "lcaron": 404, "tcaron": 374, "Lcaron": 276}
                dy_map = {"dcaron": 20, "lcaron": 18, "tcaron": 22, "Lcaron": 0}
                w_override = {}
            else:
                dx_map = {"dcaron": 608, "lcaron": 248, "tcaron": 292, "Lcaron": 284}
                dy_map = {"dcaron": 16, "lcaron": 16, "tcaron": -16, "Lcaron": 0}
                w_override = {"dcaron": 706, "lcaron": 348, "tcaron": 384, "Lcaron": 584}
            dx, dy = dx_map[comp_name], dy_map[comp_name]
        else:
            w_override = {}
            b_anc = next(a for a in base_g.anchors if a.name == anchor_name)
            m_anc = next(a for a in mark_g.anchors if a.name == f"_{anchor_name}")
            dx = round(b_anc.x - m_anc.x)
            dy = round(b_anc.y - m_anc.y)

        g = ufo.newGlyph(comp_name)
        g.width = MONO_WIDTH if is_monospace else w_override.get(comp_name, base_g.width)
        if uni is not None:
            g.unicodes = [uni]

        if base_g.components:
            for sub_c in base_g.components:
                g.components.append(
                    ufoLib2.objects.Component(baseGlyph=sub_c.baseGlyph, transformation=sub_c.transformation)
                )
        else:
            g.components.append(ufoLib2.objects.Component(baseGlyph=base_name, transformation=(1, 0, 0, 1, 0, 0)))
        g.components.append(ufoLib2.objects.Component(baseGlyph=mark_name, transformation=(1, 0, 0, 1, dx, dy)))

        mark_out = {a.name: a for a in mark_g.anchors if not a.name.startswith("_")}
        prop_anchors = []
        for a in base_g.anchors:
            if comp_name not in ("dcaron", "lcaron", "tcaron", "Lcaron") and a.name == anchor_name and anchor_name in mark_out:
                m_out = mark_out[anchor_name]
                prop_anchors.append(ufoLib2.objects.Anchor(x=round(dx + m_out.x), y=round(dy + m_out.y), name=a.name))
            else:
                prop_anchors.append(ufoLib2.objects.Anchor(x=a.x, y=a.y, name=a.name))
        g.anchors = prop_anchors
        glyph_order.append(comp_name)

    ufo.lib["public.glyphOrder"] = glyph_order


def apply_bold_class_kerning(ufo: ufoLib2.Font) -> None:
    """Apply shared class-based kerning onto Sans Bold & Serif Bold (identical pairs -> 0px reflow)."""
    apply_class_kerning(ufo)
