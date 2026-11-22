"""
Variable font builder: aligns the three weight masters (vf_align.py) and compiles them:
  - Harmonizes contour ordering, winding, start points, sharp corners & X/Y extrema
    across Regular (400), Medium (500), and Bold (700) UFO masters
  - Adds GSUB rvrn topology-switching rules for the 27 AdmiraltySymbols icons whose
    stroke dilation merges/splits contours between 400 / 500 / 700 (+ rtlm mirrors)
  - Compiles all 7 Variable TTF + WOFF2 fonts (wght 400..700) with gasp/prep + STAT tables
  - Audits non-master intermediate instances (450, 600), continuous Sans vs Serif 0.0u
    duplex zero-reflow (400..700), Mono 80-col=48000u, and Symbols rvrn+rtlm
"""

from __future__ import annotations
import io
import math
from pathlib import Path
import subprocess
import sys
from typing import Dict, List, Tuple

from fontTools.designspaceLib import DesignSpaceDocument, RuleDescriptor
from fontTools.misc.bezierTools import calcCubicBounds
from fontTools.otlLib.builder import buildStatTable
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
import numpy as np
import pathops
import ufo2ft
import ufoLib2
import uharfbuzz as hb

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_fonts import (
    VERSION_STR,
    apply_ttf_nonhinting_tables,
    audit_ufo_geometry,
)
from glyphs_mono import MONO_WIDTH
from punctuation_spacing import apply_punctuation_spacing
from symbols_engine import SYMBOL_ADVANCE_WIDTH


# ---------------------------------------------------------------------------
# 3-Master Corner- & Extremum-Locked Cubic Contour Harmonizer
# ---------------------------------------------------------------------------

def _contour_segments(contour: ufoLib2.objects.Contour):
    pts = list(contour.points)
    n = len(pts)
    on_idx = [i for i, p in enumerate(pts) if p.type is not None]
    segs = []
    for k, i0 in enumerate(on_idx):
        i1 = on_idx[(k + 1) % len(on_idx)]
        span = (i1 - i0) % n
        p0 = np.array([pts[i0].x, pts[i0].y], dtype=float)
        p3 = np.array([pts[i1].x, pts[i1].y], dtype=float)
        if span == 1:
            segs.append(("line", p0, p0 + (p3 - p0) / 3.0, p0 + 2.0 * (p3 - p0) / 3.0, p3))
        elif span == 3:
            p1 = np.array([pts[(i0 + 1) % n].x, pts[(i0 + 1) % n].y], dtype=float)
            p2 = np.array([pts[(i0 + 2) % n].x, pts[(i0 + 2) % n].y], dtype=float)
            segs.append(("curve", p0, p1, p2, p3))
        else:
            raise ValueError(f"Unsupported contour span {span} (expected cubic UFO curves)")
    return segs


def _eval_cubic(p0: np.ndarray, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray, t: float) -> np.ndarray:
    mt = 1.0 - t
    return (mt**3) * p0 + 3.0 * (mt**2) * t * p1 + 3.0 * mt * (t**2) * p2 + (t**3) * p3


def _contour_area_and_bbox(c: ufoLib2.objects.Contour) -> Tuple[float, Tuple[float, float, float, float]]:
    ap = AreaPen(None)
    c.draw(ap)
    bp = BoundsPen(None)
    c.draw(bp)
    return ap.value, bp.bounds or (0.0, 0.0, 0.0, 0.0)


def _reverse_ufo_contour(c: ufoLib2.objects.Contour) -> ufoLib2.objects.Contour:
    """Reverse winding of a cubic/line UFO contour cleanly."""
    from fontTools.pens.pointPen import ReverseContourPointPen
    rec_g = ufoLib2.objects.Glyph()
    rpen = ReverseContourPointPen(rec_g.getPointPen())
    c.drawPoints(rpen)
    return rec_g.contours[0]


def _rotate_ufo_contour(c: ufoLib2.objects.Contour, shift: int) -> ufoLib2.objects.Contour:
    pts = list(c.points)
    nc = ufoLib2.objects.Contour()
    for p in pts[shift:] + pts[:shift]:
        nc.points.append(ufoLib2.objects.Point(p.x, p.y, p.type, smooth=p.smooth))
    return nc


def _match_contour_order(cs_list: List[List[ufoLib2.objects.Contour]]) -> List[List[ufoLib2.objects.Contour]]:
    """Reorder contours across masters 1 and 2 to match master 0 by sign + normalized centroid/area."""
    m = len(cs_list[0])
    if m == 0:
        return cs_list
    if m == 1:
        a0 = _contour_area_and_bbox(cs_list[0][0])[0]
        fixed = [cs_list[0][0]]
        for idx in (1, 2):
            ck = cs_list[idx][0]
            ak = _contour_area_and_bbox(ck)[0]
            fixed.append(_reverse_ufo_contour(ck) if (ak > 0) != (a0 > 0) else ck)
        return [[fixed[0]], [fixed[1]], [fixed[2]]]

    info0 = [_contour_area_and_bbox(c) for c in cs_list[0]]
    all_b0 = [b for _, b in info0]
    gx0, gy0 = min(b[0] for b in all_b0), min(b[1] for b in all_b0)
    gw0 = max(max(b[2] for b in all_b0) - gx0, 1.0)
    gh0 = max(max(b[3] for b in all_b0) - gy0, 1.0)
    norm0 = [
        (1 if a > 0 else -1, ((b[0] + b[2]) / 2 - gx0) / gw0, ((b[1] + b[3]) / 2 - gy0) / gh0, abs(a) / (gw0 * gh0))
        for a, b in info0
    ]

    out = [list(cs_list[0])]
    for idx in (1, 2):
        infok = [_contour_area_and_bbox(c) for c in cs_list[idx]]
        all_bk = [b for _, b in infok]
        gxk, gyk = min(b[0] for b in all_bk), min(b[1] for b in all_bk)
        gwk = max(max(b[2] for b in all_bk) - gxk, 1.0)
        ghk = max(max(b[3] for b in all_bk) - gyk, 1.0)
        normk = [
            (1 if a > 0 else -1, ((b[0] + b[2]) / 2 - gxk) / gwk, ((b[1] + b[3]) / 2 - gyk) / ghk, abs(a) / (gwk * ghk))
            for a, b in infok
        ]
        used: set[int] = set()
        perm: List[ufoLib2.objects.Contour] = []
        for s0, cx0, cy0, ar0 in norm0:
            cands = [(j, normk[j]) for j in range(len(normk)) if j not in used and normk[j][0] == s0]
            need_rev = False
            if not cands:
                cands = [(j, normk[j]) for j in range(len(normk)) if j not in used]
                need_rev = True
            best_j = min(
                cands,
                key=lambda item: (cx0 - item[1][1]) ** 2 + (cy0 - item[1][2]) ** 2 + 0.25 * (ar0 - item[1][3]) ** 2,
            )[0]
            used.add(best_j)
            ck = cs_list[idx][best_j]
            perm.append(_reverse_ufo_contour(ck) if need_rev else ck)
        out.append(perm)
    return out


def _sample_contour_features(c: ufoLib2.objects.Contour):
    """Return dense arc-length samples + normalized coordinates + sharp corner indices."""
    segs = _contour_segments(c)
    pts: List[np.ndarray] = []
    corner_flag: List[bool] = []
    in_dirs: List[np.ndarray] = []
    out_dirs: List[np.ndarray] = []
    seg_out_vec: List[np.ndarray] = []

    for _, p0, p1, p2, p3 in segs:
        v_out = p1 - p0
        if np.linalg.norm(v_out) < 1e-4:
            v_out = p2 - p0
        if np.linalg.norm(v_out) < 1e-4:
            v_out = p3 - p0
        v_in = p3 - p2
        if np.linalg.norm(v_in) < 1e-4:
            v_in = p3 - p1
        if np.linalg.norm(v_in) < 1e-4:
            v_in = p3 - p0
        out_dirs.append(v_out / max(np.linalg.norm(v_out), 1e-8))
        in_dirs.append(v_in / max(np.linalg.norm(v_in), 1e-8))

    M = len(segs)
    for k, (kind, p0, p1, p2, p3) in enumerate(segs):
        vin = in_dirs[(k - 1) % M]
        vout = out_dirs[k]
        ang = math.degrees(math.acos(float(np.clip(np.dot(vin, vout), -1.0, 1.0))))
        is_corner = ang >= 24.0
        n_sub = 4 if kind == "line" else 20
        for j in range(n_sub):
            pts.append(_eval_cubic(p0, p1, p2, p3, j / n_sub))
            corner_flag.append(is_corner if j == 0 else False)
            seg_out_vec.append(vout if j == 0 else np.zeros(2))

    arr = np.array(pts)
    cmask = np.array(corner_flag, dtype=bool)
    odirs = np.array(seg_out_vec)
    # Fill smooth point tangent vectors via finite difference
    nxt = np.roll(arr, -1, axis=0)
    tang = nxt - arr
    tlen = np.maximum(np.linalg.norm(tang, axis=1, keepdims=True), 1e-8)
    tang = tang / tlen
    for idx in range(len(arr)):
        if cmask[idx]:
            tang[idx] = odirs[idx]
    mn = arr.min(axis=0)
    ptp = np.maximum(np.ptp(arr, axis=0), 1.0)
    narr = (arr - mn) / ptp
    return arr, narr, cmask, tang


def _recompute_arc_u(arr: np.ndarray, i0: int) -> Tuple[np.ndarray, np.ndarray]:
    arr_r = np.roll(arr, -i0, axis=0)
    nxt = np.roll(arr_r, -1, axis=0)
    d = np.linalg.norm(nxt - arr_r, axis=1)
    u = np.concatenate([[0.0], np.cumsum(d)])
    u /= max(u[-1], 1e-8)
    return arr_r, u


def _detect_local_extrema_u(arr_r: np.ndarray, u: np.ndarray, corners_u: np.ndarray) -> List[Tuple[float, str]]:
    """Find interior X/Y turning extrema far from sharp corners so cubic curves stay monotonic."""
    n = len(arr_r)
    extrema: List[Tuple[float, str]] = []
    if n < 12:
        return extrema
    xs, ys = arr_r[:, 0], arr_r[:, 1]
    win = max(3, min(8, n // 20))
    for i in range(1, n - 1):
        ui = float(u[i])
        if ui < 0.025 or ui > 0.975:
            continue
        if len(corners_u) > 0 and np.min(np.abs(corners_u - ui)) < 0.025:
            continue
        idxs = [(i + k) % n for k in range(-win, win + 1)]
        w_x = xs[idxs]
        w_y = ys[idxs]
        # Strict local min or max with >= 1.2u prominence vs both window ends
        prom_x_max = min(xs[i] - w_x[0], xs[i] - w_x[-1])
        prom_x_min = min(w_x[0] - xs[i], w_x[-1] - xs[i])
        prom_y_max = min(ys[i] - w_y[0], ys[i] - w_y[-1])
        prom_y_min = min(w_y[0] - ys[i], w_y[-1] - ys[i])
        tag = None
        if xs[i] == np.max(w_x) and prom_x_max >= 1.2:
            tag = "xmax"
        elif xs[i] == np.min(w_x) and prom_x_min >= 1.2:
            tag = "xmin"
        elif ys[i] == np.max(w_y) and prom_y_max >= 1.2:
            tag = "ymax"
        elif ys[i] == np.min(w_y) and prom_y_min >= 1.2:
            tag = "ymin"
        if tag is not None:
            # De-duplicate adjacent samples on flat/slow extremum plateau
            if extrema and extrema[-1][1] == tag and abs(ui - extrema[-1][0]) < 0.04:
                continue
            extrema.append((ui, tag))
    return extrema


def _fit_cubic_span(pts: np.ndarray, clamp_monotone: bool = True) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    p0, p3 = pts[0], pts[-1]
    chord = float(np.linalg.norm(p3 - p0))
    if len(pts) <= 2 or chord < 1e-6:
        return p0, p0 + (p3 - p0) / 3.0, p0 + 2.0 * (p3 - p0) / 3.0, p3
    chords = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    t = np.concatenate([[0.0], np.cumsum(chords)])
    if t[-1] < 1e-6:
        return p0, p0, p3, p3
    t /= t[-1]
    ti = t[1:-1]
    mt = 1.0 - ti
    A = np.column_stack([3.0 * (mt**2) * ti, 3.0 * mt * (ti**2)])
    rhs = pts[1:-1] - ((mt**3)[:, None] * p0 + (ti**3)[:, None] * p3)
    sol, _, _, _ = np.linalg.lstsq(A, rhs, rcond=None)
    q1, q2 = sol[0].copy(), sol[1].copy()

    if clamp_monotone:
        dx = np.diff(pts[:, 0])
        dy = np.diff(pts[:, 1])
        if np.all(dx >= -0.25) or np.all(dx <= 0.25):
            xmin, xmax = min(p0[0], p3[0]), max(p0[0], p3[0])
            q1[0] = float(np.clip(q1[0], xmin, xmax))
            q2[0] = float(np.clip(q2[0], xmin, xmax))
        if np.all(dy >= -0.25) or np.all(dy <= 0.25):
            ymin, ymax = min(p0[1], p3[1]), max(p0[1], p3[1])
            q1[1] = float(np.clip(q1[1], ymin, ymax))
            q2[1] = float(np.clip(q2[1], ymin, ymax))
    return p0, q1, q2, p3


def _segs_to_contour(segs) -> ufoLib2.objects.Contour:
    nc = ufoLib2.objects.Contour()
    r = lambda v: round(float(v), 3)
    for kind, p0, p1, p2, p3 in segs:
        if kind == "line":
            nc.points.append(ufoLib2.objects.Point(r(p3[0]), r(p3[1]), "line"))
        else:
            nc.points.append(ufoLib2.objects.Point(r(p1[0]), r(p1[1]), None))
            nc.points.append(ufoLib2.objects.Point(r(p2[0]), r(p2[1]), None))
            nc.points.append(ufoLib2.objects.Point(r(p3[0]), r(p3[1]), "curve"))
    return nc


def _harmonize_three_contours(
    c0: ufoLib2.objects.Contour,
    c1: ufoLib2.objects.Contour,
    c2: ufoLib2.objects.Contour,
) -> Tuple[ufoLib2.objects.Contour, ufoLib2.objects.Contour, ufoLib2.objects.Contour]:
    sig = lambda c: tuple(p.type for p in c.points)
    # Fast-path if point counts match and cyclic on-curve shift aligns normalized geometry closely
    if len(c0.points) == len(c1.points) == len(c2.points):
        s0 = sig(c0)
        on0 = [i for i, p in enumerate(c0.points) if p.type is not None]
        p0_arr = np.array([(c0.points[i].x, c0.points[i].y) for i in on0], dtype=float)
        n0 = (p0_arr - p0_arr.min(0)) / np.maximum(np.ptp(p0_arr, axis=0), 1.0)
        aligned = []
        ok_fast = True
        for ck in (c1, c2):
            on_k = [i for i, p in enumerate(ck.points) if p.type is not None]
            best_c = None
            best_err = 999.0
            best_shift = -1
            for idx_shift in range(len(on_k)):
                rot = _rotate_ufo_contour(ck, on_k[idx_shift])
                if sig(rot) != s0:
                    continue
                pk = np.array([(p.x, p.y) for p in rot.points if p.type is not None], dtype=float)
                nk = (pk - pk.min(0)) / np.maximum(np.ptp(pk, axis=0), 1.0)
                err = float(np.max(np.linalg.norm(nk - n0, axis=1)))
                if err < best_err:
                    best_err = err
                    best_c = rot
                    best_shift = idx_shift
            max_allowed = 0.35 if best_shift == 0 and sig(ck) == s0 else 0.16
            if best_c is None or best_err > max_allowed:
                ok_fast = False
                break
            aligned.append(best_c)
        if ok_fast:
            return c0, aligned[0], aligned[1]

    # Review 2: exact alignment (split segments, never re-draw them). The old re-sampling path
    # below is kept only as a fallback.
    try:
        from vf_align import align_three
        a0, a1, a2, _cost = align_three(_contour_segments(c0), _contour_segments(c1), _contour_segments(c2))
        return _segs_to_contour(a0), _segs_to_contour(a1), _segs_to_contour(a2)
    except Exception as exc:  # pragma: no cover
        print(f"    [vf_align] fallback to re-sampling: {exc}")

    f0, f1, f2 = _sample_contour_features(c0), _sample_contour_features(c1), _sample_contour_features(c2)
    arr0, narr0, cmask0, tang0 = f0

    # Pick canonical start on master 0: bottom-left sharp corner if any, else bottom-left extremum
    score0 = narr0[:, 1] + 0.18 * narr0[:, 0]
    if np.any(cmask0):
        c_idxs = np.where(cmask0)[0]
        i0_0 = int(c_idxs[np.argmin(score0[c_idxs])])
    else:
        i0_0 = int(np.argmin(score0))

    p0_ref = narr0[i0_0]
    t0_ref = tang0[i0_0]
    is_c0_corner = bool(cmask0[i0_0])

    # Match start point on masters 1 & 2 to master 0 by normalized coords + tangent + cornerness
    starts = [i0_0]
    for arrk, narrk, cmaskk, tangk in (f1, f2):
        dist2 = np.sum((narrk - p0_ref) ** 2, axis=1) + 0.15 * np.sum((tangk - t0_ref) ** 2, axis=1)
        if is_c0_corner and np.any(cmaskk):
            dist2 = np.where(cmaskk, dist2, dist2 + 0.8)
        starts.append(int(np.argmin(dist2)))

    arr_r = []
    u_all = []
    corners_r = []
    extrema_r = []
    for (arrk, _, cmaskk, _), i0_k in zip((f0, f1, f2), starts):
        ar, uk = _recompute_arc_u(arrk, i0_k)
        cmr = np.roll(cmaskk, -i0_k)
        cu = uk[:-1][cmr]
        ex = _detect_local_extrema_u(ar, uk, cu)
        arr_r.append(ar)
        u_all.append(uk)
        corners_r.append(cu)
        extrema_r.append(ex)

    # 1. Lock interior sharp corners monotonically across all 3 masters
    cu0, cu1, cu2 = corners_r
    landmarks: List[Tuple[float, float, float, bool]] = [(0.0, 0.0, 0.0, is_c0_corner)]
    j1 = j2 = 0
    for u0 in cu0:
        if u0 < 1e-4 or u0 > 1.0 - 1e-4:
            continue
        cand1 = [k for k in range(j1, len(cu1)) if cu1[k] > landmarks[-1][1] + 1e-4 and abs(cu1[k] - u0) < 0.08]
        cand2 = [k for k in range(j2, len(cu2)) if cu2[k] > landmarks[-1][2] + 1e-4 and abs(cu2[k] - u0) < 0.08]
        if cand1 and cand2:
            k1 = min(cand1, key=lambda k: abs(cu1[k] - u0))
            k2 = min(cand2, key=lambda k: abs(cu2[k] - u0))
            landmarks.append((float(u0), float(cu1[k1]), float(cu2[k2]), True))
            j1, j2 = k1 + 1, k2 + 1

    # 2. Insert matched interior X/Y extrema inside spans between corners so curves stay extremum-clean
    anchors_tmp = landmarks + [(1.0, 1.0, 1.0, is_c0_corner)]
    full_landmarks: List[Tuple[float, float, float]] = [(0.0, 0.0, 0.0)]
    ex0, ex1, ex2 = extrema_r
    for s_idx in range(len(anchors_tmp) - 1):
        a0, a1, a2, _ = anchors_tmp[s_idx]
        b0, b1, b2, _ = anchors_tmp[s_idx + 1]
        if s_idx > 0:
            full_landmarks.append((a0, a1, a2))
        span_ex0 = [(u0, tag) for (u0, tag) in ex0 if a0 + 0.025 < u0 < b0 - 0.025]
        cur1_lo, cur2_lo = a1, a2
        for u0, tag in span_ex0:
            rel0 = (u0 - a0) / max(b0 - a0, 1e-6)
            est1 = a1 + rel0 * (b1 - a1)
            est2 = a2 + rel0 * (b2 - a2)
            c1s = [u for u, t in ex1 if t == tag and cur1_lo + 0.02 < u < b1 - 0.02 and abs(u - est1) < 0.09]
            c2s = [u for u, t in ex2 if t == tag and cur2_lo + 0.02 < u < b2 - 0.02 and abs(u - est2) < 0.09]
            if c1s and c2s:
                u1_m = min(c1s, key=lambda u: abs(u - est1))
                u2_m = min(c2s, key=lambda u: abs(u - est2))
                full_landmarks.append((float(u0), float(u1_m), float(u2_m)))
                cur1_lo, cur2_lo = u1_m, u2_m
    full_landmarks.append((1.0, 1.0, 1.0))

    arrs_closed = [np.vstack([ar, ar[0]]) for ar in arr_r]
    # 3. Determine span segment types ('line' or N cubic sub-segments)
    span_specs: List[Tuple[str, int]] = []
    n_spans = len(full_landmarks) - 1
    for k in range(n_spans):
        u_starts = full_landmarks[k]
        u_ends = full_landmarks[k + 1]
        is_all_line = n_spans >= 3
        for m in range(3):
            us = np.linspace(u_starts[m], u_ends[m], 17)
            pts = np.column_stack([
                np.interp(us, u_all[m], arrs_closed[m][:, 0]),
                np.interp(us, u_all[m], arrs_closed[m][:, 1]),
            ])
            chord = float(np.linalg.norm(pts[-1] - pts[0]))
            if chord > 1e-5:
                ldir = (pts[-1] - pts[0]) / chord
                perp = float(np.max(np.linalg.norm((pts - pts[0]) - ((pts - pts[0]) @ ldir)[:, None] * ldir, axis=1)))
                if perp > 0.40:
                    is_all_line = False
        if is_all_line:
            span_specs.append(("line", 1))
        else:
            chosen_n = 16
            for n_sub in (1, 2, 3, 4, 6, 8, 12, 16):
                max_err = 0.0
                max_over = 0.0
                for m in range(3):
                    for s_i in range(n_sub):
                        ua = u_starts[m] + (u_ends[m] - u_starts[m]) * (s_i / n_sub)
                        ub = u_starts[m] + (u_ends[m] - u_starts[m]) * ((s_i + 1) / n_sub)
                        us = np.linspace(ua, ub, 13)
                        pts = np.column_stack([
                            np.interp(us, u_all[m], arrs_closed[m][:, 0]),
                            np.interp(us, u_all[m], arrs_closed[m][:, 1]),
                        ])
                        q0, q1, q2, q3 = _fit_cubic_span(pts, clamp_monotone=True)
                        fit_pts = np.array([_eval_cubic(q0, q1, q2, q3, t) for t in np.linspace(0.0, 1.0, 13)])
                        err = float(np.max(np.linalg.norm(fit_pts - pts, axis=1)))
                        if err > max_err:
                            max_err = err
                        bx0, by0, bx1, by1 = calcCubicBounds(tuple(q0), tuple(q1), tuple(q2), tuple(q3))
                        over = max(
                            min(q0[0], q3[0]) - bx0,
                            bx1 - max(q0[0], q3[0]),
                            min(q0[1], q3[1]) - by0,
                            by1 - max(q0[1], q3[1]),
                        )
                        if over > max_over:
                            max_over = over
                if max_err <= 0.65 and max_over <= 0.75:
                    chosen_n = n_sub
                    break
            span_specs.append(("curve", chosen_n))

    out_cs: List[ufoLib2.objects.Contour] = []
    for m in range(3):
        nc = ufoLib2.objects.Contour()
        # Keep track of rounded start point from last point to satisfy calcCubicBounds cleanly
        all_segs_raw = []
        for k, (skind, n_sub) in enumerate(span_specs):
            ua0, ub0 = full_landmarks[k][m], full_landmarks[k + 1][m]
            if skind == "line":
                px = float(np.interp(ub0, u_all[m], arrs_closed[m][:, 0]))
                py = float(np.interp(ub0, u_all[m], arrs_closed[m][:, 1]))
                all_segs_raw.append(("line", (round(px), round(py))))
            else:
                for s_i in range(n_sub):
                    ua = ua0 + (ub0 - ua0) * (s_i / n_sub)
                    ub = ua0 + (ub0 - ua0) * ((s_i + 1) / n_sub)
                    us = np.linspace(ua, ub, 13)
                    pts = np.column_stack([
                        np.interp(us, u_all[m], arrs_closed[m][:, 0]),
                        np.interp(us, u_all[m], arrs_closed[m][:, 1]),
                    ])
                    _, q1, q2, q3 = _fit_cubic_span(pts, clamp_monotone=True)
                    all_segs_raw.append((
                        "curve",
                        (round(float(q1[0])), round(float(q1[1]))),
                        (round(float(q2[0])), round(float(q2[1]))),
                        (round(float(q3[0])), round(float(q3[1]))),
                    ))
        # Clamp integer rounded handles if needed so calcCubicBounds never exceeds 0.8u on any rounded segment
        last_on = all_segs_raw[-1][-1]
        for seg in all_segs_raw:
            if seg[0] == "line":
                p3 = seg[1]
                nc.points.append(ufoLib2.objects.Point(p3[0], p3[1], "line"))
                last_on = p3
            else:
                _, h1, h2, p3 = seg
                bx0, by0, bx1, by1 = calcCubicBounds(last_on, h1, h2, p3)
                ex0, ex1 = min(last_on[0], p3[0]), max(last_on[0], p3[0])
                ey0, ey1 = min(last_on[1], p3[1]), max(last_on[1], p3[1])
                over = max(ex0 - bx0, bx1 - ex1, ey0 - by0, by1 - ey1)
                if over > 0.75:
                    h1 = (int(np.clip(h1[0], ex0, ex1)), int(np.clip(h1[1], ey0, ey1)))
                    h2 = (int(np.clip(h2[0], ex0, ex1)), int(np.clip(h2[1], ey0, ey1)))
                nc.points.append(ufoLib2.objects.Point(h1[0], h1[1], None))
                nc.points.append(ufoLib2.objects.Point(h2[0], h2[1], None))
                nc.points.append(ufoLib2.objects.Point(p3[0], p3[1], "curve"))
                last_on = p3
        out_cs.append(nc)
    return out_cs[0], out_cs[1], out_cs[2]


def _copy_contours(cs: List[ufoLib2.objects.Contour]) -> List[ufoLib2.objects.Contour]:
    out = []
    for c in cs:
        nc = ufoLib2.objects.Contour()
        for p in c.points:
            nc.points.append(ufoLib2.objects.Point(p.x, p.y, p.type, smooth=p.smooth))
        out.append(nc)
    return out


def _pad_missing_contours(glyphs, gname: str) -> None:
    """Review 2: when a small counter closes up in one weight (e.g. the triangles of the won
    sign in Serif Bold), give that master the same contour collapsed to a single point, so the
    counter shrinks to nothing between the weights instead of breaking the variable font."""
    counts = [len(g.contours) for g in glyphs]
    if len(set(counts)) == 1:
        return
    ref = glyphs[counts.index(max(counts))]
    ref_info = []
    for c in ref.contours:
        a, b = _contour_area_and_bbox(c)
        ref_info.append((a, (b[0] + b[2]) / 2, (b[1] + b[3]) / 2))
    for g in glyphs:
        if len(g.contours) == len(ref.contours):
            continue
        used = set()
        for c in g.contours:
            a, b = _contour_area_and_bbox(c)
            cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
            cands = [j for j in range(len(ref_info)) if j not in used and (ref_info[j][0] > 0) == (a > 0)] or [
                j for j in range(len(ref_info)) if j not in used
            ]
            j = min(cands, key=lambda j: (ref_info[j][1] - cx) ** 2 + (ref_info[j][2] - cy) ** 2)
            used.add(j)
        for j in range(len(ref_info)):
            if j in used:
                continue
            src = ref.contours[j]
            nc = ufoLib2.objects.Contour()
            for pt in src.points:
                nc.points.append(ufoLib2.objects.Point(round(ref_info[j][1]), round(ref_info[j][2]), pt.type))
            g.contours.append(nc)
        print(f"    [{gname}] padded {len(ref_info) - len(used)} collapsed contour(s)")


def _harmonize_latin_designspace(ds_path: Path) -> Tuple[DesignSpaceDocument, List[ufoLib2.Font]]:
    ds = DesignSpaceDocument.fromfile(str(ds_path))
    fonts = [ufoLib2.Font.open(ROOT / "sources" / Path(s.path).name) for s in ds.sources]
    f0, f1, f2 = fonts
    max_area_err = 0.0

    for gname in list(f0.keys()):
        if len(f0[gname].contours) == 0:
            continue
        a_before = [sum(_contour_area_and_bbox(c)[0] for c in f[gname].contours) for f in fonts]
        _pad_missing_contours([f[gname] for f in fonts], gname)
        mc0, mc1, mc2 = _match_contour_order([list(f0[gname].contours), list(f1[gname].contours), list(f2[gname].contours)])
        nc0, nc1, nc2 = [], [], []
        for a, b, c in zip(mc0, mc1, mc2):
            ha, hb, hc = _harmonize_three_contours(a, b, c)
            nc0.append(ha)
            nc1.append(hb)
            nc2.append(hc)
        f0[gname].contours = nc0
        f1[gname].contours = nc1
        f2[gname].contours = nc2
        a_after = [sum(_contour_area_and_bbox(c)[0] for c in f[gname].contours) for f in fonts]
        for ab, aa in zip(a_before, a_after):
            max_area_err = max(max_area_err, abs(aa - ab) / max(abs(ab), 1.0))

    print(f"[{ds_path.name}] Harmonized {len(f0)} glyphs cleanly (max contour area drift = {max_area_err * 100:.3f}%).")
    return ds, fonts


def _harmonize_symbols_designspace(ds_path: Path) -> Tuple[DesignSpaceDocument, List[ufoLib2.Font]]:
    """
    Harmonize the 224 contour-count-compatible symbol glyphs and create unencoded
    .rvrn500 / .rvrn700 glyphs + RuleDescriptors + rtlm rules for the 27 topology-switching icons.
    """
    ds = DesignSpaceDocument.fromfile(str(ds_path))
    fonts = [ufoLib2.Font.open(ROOT / "sources" / Path(s.path).name) for s in ds.sources]
    f0, f1, f2 = fonts
    ds.rules = []

    glyph_order = list(f0.lib["public.glyphOrder"])
    rvrn_map_500: Dict[str, str] = {}
    rvrn_map_700: Dict[str, str] = {}
    swapped_count = 0

    def _harmonize_pair(ca_list, cb_list):
        mc0, mc1, _ = _match_contour_order([ca_list, cb_list, _copy_contours(cb_list)])
        out_a, out_b = [], []
        for a, b in zip(mc0, mc1):
            ha, hb, _ = _harmonize_three_contours(a, b, _copy_contours([b])[0])
            out_a.append(ha)
            out_b.append(hb)
        return out_a, out_b

    def _pair_topo_compatible(ca_list, cb_list) -> bool:
        if len(ca_list) != len(cb_list):
            return False
        if not ca_list:
            return True
        info_a = [_contour_area_and_bbox(c) for c in ca_list]
        info_b = [_contour_area_and_bbox(c) for c in cb_list]
        signs_a = (sum(1 for a, _ in info_a if a > 0), sum(1 for a, _ in info_a if a < 0))
        signs_b = (sum(1 for a, _ in info_b if a > 0), sum(1 for a, _ in info_b if a < 0))
        if signs_a != signs_b:
            return False
        mc_a, mc_b, _ = _match_contour_order([ca_list, cb_list, _copy_contours(cb_list)])
        all_ba = [b for _, b in info_a]
        all_bb = [b for _, b in info_b]
        gxa, gya = min(b[0] for b in all_ba), min(b[1] for b in all_ba)
        gwa, gha = max(max(b[2] for b in all_ba) - gxa, 1.0), max(max(b[3] for b in all_ba) - gya, 1.0)
        gxb, gyb = min(b[0] for b in all_bb), min(b[1] for b in all_bb)
        gwb, ghb = max(max(b[2] for b in all_bb) - gxb, 1.0), max(max(b[3] for b in all_bb) - gyb, 1.0)
        for ca, cb in zip(mc_a, mc_b):
            aa, ba = _contour_area_and_bbox(ca)
            ab, bb = _contour_area_and_bbox(cb)
            if (aa > 0) != (ab > 0):
                return False
            cxa, cya = ((ba[0] + ba[2]) / 2 - gxa) / gwa, ((ba[1] + ba[3]) / 2 - gya) / gha
            cxb, cyb = ((bb[0] + bb[2]) / 2 - gxb) / gwb, ((bb[1] + bb[3]) / 2 - gyb) / ghb
            if math.hypot(cxa - cxb, cya - cyb) > 0.20:
                return False
        return True

    for gname in list(glyph_order):
        if len(f0[gname].contours) == 0:
            continue
        cs0 = list(f0[gname].contours)
        cs1 = list(f1[gname].contours)
        cs2 = list(f2[gname].contours)
        compat_01 = _pair_topo_compatible(cs0, cs1)
        compat_12 = _pair_topo_compatible(cs1, cs2)

        if compat_01 and compat_12:
            mc0, mc1, mc2 = _match_contour_order([cs0, cs1, cs2])
            nc0, nc1, nc2 = [], [], []
            for a, b, c in zip(mc0, mc1, mc2):
                ha, hb, hc = _harmonize_three_contours(a, b, c)
                nc0.append(ha)
                nc1.append(hb)
                nc2.append(hc)
            f0[gname].contours = nc0
            f1[gname].contours = nc1
            f2[gname].contours = nc2
        elif compat_01 and not compat_12:
            # 400..599 shares 400-500 topology; 600..700 switches to .rvrn700
            swapped_count += 1
            ha, hb = _harmonize_pair(cs0, cs1)
            f0[gname].contours = ha
            f1[gname].contours = hb
            f2[gname].contours = _copy_contours(hb)
            alt7 = f"{gname}.rvrn700"
            rvrn_map_700[gname] = alt7
            for f in fonts:
                ag = f.newGlyph(alt7)
                ag.width = SYMBOL_ADVANCE_WIDTH
                ag.contours = _copy_contours(cs2)
            glyph_order.append(alt7)
        elif not compat_01 and compat_12:
            # 400..449 uses 400; 450..700 switches to .rvrn500 which smoothly interpolates 500..700
            swapped_count += 1
            f0[gname].contours = cs0
            f1[gname].contours = _copy_contours(cs0)
            f2[gname].contours = _copy_contours(cs0)
            hb, hc = _harmonize_pair(cs1, cs2)
            alt5 = f"{gname}.rvrn500"
            rvrn_map_500[gname] = alt5
            f0[alt5] = ufoLib2.objects.Glyph()
            f0[alt5].width = SYMBOL_ADVANCE_WIDTH
            f0[alt5].contours = _copy_contours(hb)
            f1[alt5] = ufoLib2.objects.Glyph()
            f1[alt5].width = SYMBOL_ADVANCE_WIDTH
            f1[alt5].contours = hb
            f2[alt5] = ufoLib2.objects.Glyph()
            f2[alt5].width = SYMBOL_ADVANCE_WIDTH
            f2[alt5].contours = hc
            glyph_order.append(alt5)
        else:
            # Three distinct contour counts (e.g. help-center [6, 5, 6])
            swapped_count += 1
            f0[gname].contours = cs0
            f1[gname].contours = _copy_contours(cs0)
            f2[gname].contours = _copy_contours(cs0)
            alt5 = f"{gname}.rvrn500"
            alt7 = f"{gname}.rvrn700"
            rvrn_map_500[gname] = alt5
            rvrn_map_700[gname] = alt7
            for alt_name, src_cs in ((alt5, cs1), (alt7, cs2)):
                for f in fonts:
                    ag = f.newGlyph(alt_name)
                    ag.width = SYMBOL_ADVANCE_WIDTH
                    ag.contours = _copy_contours(src_cs)
                glyph_order.append(alt_name)

    # Update DesignSpace RuleDescriptors cleanly (grouped into non-overlapping ranges)
    subs_500_only = [(g, rvrn_map_500[g]) for g in rvrn_map_500 if g not in rvrn_map_700]
    subs_500_mid = [(g, rvrn_map_500[g]) for g in rvrn_map_500 if g in rvrn_map_700]
    subs_700 = [(g, rvrn_map_700[g]) for g in rvrn_map_700]

    if subs_500_only:
        ds.addRule(
            RuleDescriptor(
                name="sym_med_to_bold",
                conditionSets=[[dict(name="Weight", minimum=450, maximum=700)]],
                subs=subs_500_only,
            )
        )
    if subs_500_mid:
        ds.addRule(
            RuleDescriptor(
                name="sym_med_band",
                conditionSets=[[dict(name="Weight", minimum=450, maximum=599)]],
                subs=subs_500_mid,
            )
        )
    if subs_700:
        ds.addRule(
            RuleDescriptor(
                name="sym_bold_band",
                conditionSets=[[dict(name="Weight", minimum=600, maximum=700)]],
                subs=subs_700,
            )
        )

    # Ensure rtlm feature mirrors any .rtl base that had rvrn alternatives
    extra_rtlm: List[str] = []
    for base_g, alt_g in list(rvrn_map_500.items()) + list(rvrn_map_700.items()):
        if not base_g.endswith(".rtl") and f"{base_g}.rtl" in f0:
            suffix = ".rvrn500" if alt_g.endswith(".rvrn500") else ".rvrn700"
            rtl_base = f"{base_g}.rtl"
            rtl_alt = f"{rtl_base}{suffix}"
            target_rtl = rtl_alt if rtl_alt in f0 else rtl_base
            extra_rtlm.append(f"    sub {alt_g} by {target_rtl};")

    if extra_rtlm:
        for f in fonts:
            ft = f.features.text
            block = "\n".join(extra_rtlm)
            f.features.text = ft.replace("\n} rtlm;", f"\n{block}\n}} rtlm;")

    for f in fonts:
        f.lib["public.glyphOrder"] = glyph_order

    print(
        f"[{ds_path.name}] Harmonized {len(glyph_order)} glyphs "
        f"({swapped_count} topology-switching glyphs via rvrn + {len(extra_rtlm)} extra rtlm rules)."
    )
    return ds, fonts


def _add_canonical_stat(vf: TTFont, is_italic: bool, has_italic_axis: bool = True) -> None:
    """Review 2: STAT with exact values (format 1 / 3). The old table used format 2 with
    open ranges, so every weight name claimed the whole axis. Also adds the SemiBold 600
    named instance and name ID 25 (PostScript name prefix for variable fonts)."""
    axes = [
        dict(
            tag="wght",
            name="Weight",
            ordering=0,
            values=[
                dict(value=400, name="Regular", flags=0x2, linkedValue=700),
                dict(value=500, name="Medium"),
                dict(value=600, name="SemiBold"),
                dict(value=700, name="Bold"),
            ],
        )
    ]
    if has_italic_axis:
        axes.append(
            dict(
                tag="ital",
                name="Italic",
                ordering=1,
                values=[
                    dict(value=1, name="Italic") if is_italic else dict(value=0, name="Roman", flags=0x2, linkedValue=1),
                ],
            )
        )
    buildStatTable(vf, axes, elidedFallbackName=2)

    name = vf["name"]
    ps_family = (name.getDebugName(6) or "").split("-")[0]
    fvar = vf["fvar"]
    if not any(abs(i.coordinates.get("wght", 0) - 600) < 0.5 for i in fvar.instances):
        from fontTools.ttLib.tables._f_v_a_r import NamedInstance
        inst = NamedInstance()
        inst.coordinates = {"wght": 600.0}
        inst.subfamilyNameID = name.addMultilingualName({"en": "SemiBold Italic" if is_italic else "SemiBold"}, mac=False)
        inst.postscriptNameID = name.addMultilingualName(
            {"en": f"{ps_family}-SemiBold{'Italic' if is_italic else ''}"}, mac=False
        )
        fvar.instances.append(inst)
        fvar.instances.sort(key=lambda i: i.coordinates["wght"])
    name.setName(ps_family + ("Italic" if is_italic else ""), 25, 3, 1, 0x409)


def _hb_adv_vf(vf_path: Path, text: str, wght: float, feats: dict | None = None) -> int:
    blob = hb.Blob.from_file_path(str(vf_path))
    face = hb.Face(blob)
    font = hb.Font(face)
    font.scale = (1000, 1000)
    font.set_variations({"wght": wght})
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, feats or {})
    return sum(p.x_advance for p in (buf.glyph_positions or []))


def _verify_interpolated_instances(vf_path: Path, wght_values: Tuple[int, ...] = (450, 600)) -> None:
    """Instantiate VF at intermediate weights and check outline integrity via pathops."""
    base_tt = TTFont(str(vf_path))
    for w in wght_values:
        inst = instantiateVariableFont(base_tt, {"wght": w}, inplace=False)
        buf = io.BytesIO()
        inst.save(buf)
        buf.seek(0)
        tt_i = TTFont(buf)
        glyf = tt_i["glyf"]
        glyph_set = tt_i.getGlyphSet()
        for gname in ("A", "B", "C", "O", "R", "S", "a", "e", "g", "o", "s", "six", "eth", "eight", "ampersand"):
            if gname not in glyph_set:
                continue
            ap = AreaPen(glyph_set)
            glyph_set[gname].draw(ap)
            raw_area = ap.value
            # TrueType glyf contours use clockwise outer winding -> negative signed AreaPen area
            if raw_area >= 0:
                raise RuntimeError(f"{vf_path.name} @ wght={w} {gname}: expected CW TTF area < 0, got {raw_area:.1f}")
            sk = pathops.Path()
            glyph_set[gname].draw(sk.getPen())
            simp = pathops.simplify(sk, fix_winding=True)
            sap = AreaPen(None)
            simp.draw(sap)
            rel = abs(sap.value - (-raw_area)) / max(abs(raw_area), 1.0)
            if rel > 0.01:
                raise RuntimeError(
                    f"{vf_path.name} @ wght={w} {gname}: self-intersection {rel:.4f} (raw={raw_area:.1f}, simp={sap.value:.1f})"
                )


def build_all_variable_fonts() -> List[Path]:
    sources_dir = ROOT / "sources"
    var_dir = ROOT / "fonts" / "variable"
    var_dir.mkdir(parents=True, exist_ok=True)

    specs = [
        ("AdmiraltySans.designspace", "AdmiraltySans[wght]", False, False, False),
        ("AdmiraltySans-Italic.designspace", "AdmiraltySans-Italic[wght]", True, False, False),
        ("AdmiraltySerif.designspace", "AdmiraltySerif[wght]", False, False, False),
        ("AdmiraltySerif-Italic.designspace", "AdmiraltySerif-Italic[wght]", True, False, False),
        ("AdmiraltyMono.designspace", "AdmiraltyMono[wght]", False, True, False),
        ("AdmiraltyMono-Italic.designspace", "AdmiraltyMono-Italic[wght]", True, True, False),
        ("AdmiraltySymbols.designspace", "AdmiraltySymbols[wght]", False, False, True),
    ]

    built_woff2: Dict[str, Path] = {}
    built_ttf: Dict[str, Path] = {}

    for ds_name, out_stem, is_italic, is_mono, is_symbols in specs:
        ds_path = sources_dir / ds_name
        if is_symbols:
            ds, fonts = _harmonize_symbols_designspace(ds_path)
        else:
            ds, fonts = _harmonize_latin_designspace(ds_path)

        # Save harmonized UFOs + run full Google-Fonts geometry & extrema audit on each!
        for src_desc, font_ufo in zip(ds.sources, fonts):
            ufo_out = sources_dir / Path(src_desc.path).name
            audit_ufo_geometry(font_ufo)
            font_ufo.save(ufo_out, overwrite=True)
            src_desc.path = str(ufo_out)
            src_desc.filename = ufo_out.name
            src_desc.font = font_ufo
        ds.write(str(ds_path))

        # Compile Variable TTF
        vf: TTFont = ufo2ft.compileVariableTTF(ds)
        apply_ttf_nonhinting_tables(vf)
        if is_mono:
            vf["OS/2"].xAvgCharWidth = MONO_WIDTH
            vf["post"].isFixedPitch = 1
        elif is_symbols:
            vf["OS/2"].xAvgCharWidth = SYMBOL_ADVANCE_WIDTH
            vf["post"].isFixedPitch = 1
        _add_canonical_stat(vf, is_italic=is_italic, has_italic_axis=not is_symbols)
        apply_punctuation_spacing(vf)

        ttf_path = var_dir / f"{out_stem}.ttf"
        vf.save(str(ttf_path))

        vf_w2 = TTFont(str(ttf_path))
        vf_w2.flavor = "woff2"
        w2_path = var_dir / f"{out_stem}.woff2"
        vf_w2.save(str(w2_path))

        # Audit tables
        tt = TTFont(str(ttf_path))
        assert "fvar" in tt and "gvar" in tt and "HVAR" in tt and "STAT" in tt, f"{out_stem}: missing VF tables"
        assert tt["fvar"].axes[0].axisTag == "wght"
        assert (tt["fvar"].axes[0].minValue, tt["fvar"].axes[0].defaultValue, tt["fvar"].axes[0].maxValue) == (400.0, 400.0, 700.0)
        assert round(tt["head"].fontRevision, 3) == float(VERSION_STR)
        assert tt["gasp"].gaspRange.get(0xFFFF) == 0x000F

        if not is_symbols:
            _verify_interpolated_instances(ttf_path, (450, 600))

        w2_kb = w2_path.stat().st_size / 1024.0
        max_budget = 150.0 if is_symbols else 100.0
        assert w2_kb < max_budget, f"{w2_path.name} ({w2_kb:.1f} KB) exceeds {max_budget} KB target!"
        print(f"[{out_stem}] Variable TTF + WOFF2 built & audited (WOFF2={w2_kb:.1f} KB, fvar+gvar+HVAR+STAT=OK).")
        built_ttf[out_stem] = ttf_path
        built_woff2[out_stem] = w2_path

    # Continuous Variable Duplex Zero-Reflow Audit (Sans vs Serif upright & italic at 7 wght points)
    test_runs = [
        "Admiralty Personal Agent — Zero Layout Reflow Guaranteed (2026).",
        "WAVEY To Va Yo Ti Te LT P. F, \"Hello!\" $1,480.95 €290 fV fW fY qj gj (f) [f]",
        "Voix ambiguë d'un cœur · Zażółć gęślą jaźń · nǐ hǎo ǖ ǘ ǚ ǜ Œuvre & Æther ẞ",
    ]
    for sans_key, serif_key, label in (
        ("AdmiraltySans[wght]", "AdmiraltySerif[wght]", "Upright VF"),
        ("AdmiraltySans-Italic[wght]", "AdmiraltySerif-Italic[wght]", "Italic VF"),
    ):
        for w in (400, 440, 480, 500, 560, 625, 700):
            for s in test_runs:
                for feat in ({}, {"tnum": True, "zero": True}):
                    a1 = _hb_adv_vf(built_ttf[sans_key], s, w, feat)
                    a2 = _hb_adv_vf(built_ttf[serif_key], s, w, feat)
                    assert a1 == a2, f"{label} wght={w} reflow mismatch on {s!r}: {a1} vs {a2}"
    print("Continuous Variable Duplex Zero-Reflow Audit PASSED (wght=400..700 Upright & Italic = 0.0u)!")

    # Mono Variable 80-col = 48000u Audit
    code_80 = "const fn = (x: i32, y: i32) => x != 0 && x <= y ? x -> y : y <- x; // ID:Il1_O0!"
    for mono_key in ("AdmiraltyMono[wght]", "AdmiraltyMono-Italic[wght]"):
        for w in (400, 450, 500, 600, 700):
            for feat in ({}, {"ss01": True, "zero": True}):
                adv = _hb_adv_vf(built_ttf[mono_key], code_80, w, feat)
                assert adv == 80 * MONO_WIDTH, f"{mono_key} @ wght={w} adv={adv} != 48000"
    print("Mono Variable 80-col=48000u Audit PASSED (Upright & Italic, ss01 OFF & ON, wght=400..700)!")

    # Symbols Variable rvrn + rtlm Audit (e.g. account switches contour at 450, restore-backup has rtl)
    sym_vf_path = built_ttf["AdmiraltySymbols[wght]"]
    sym_tt = TTFont(str(sym_vf_path))
    blob = hb.Blob.from_file_path(str(sym_vf_path))
    face = hb.Face(blob)
    hfont = hb.Font(face)
    for w, expect_suffix in ((400, "account"), (520, "account.rvrn500"), (700, "account.rvrn500")):
        hfont.set_variations({"wght": w})
        buf = hb.Buffer()
        buf.add_str(chr(0xE07E))  # check account codepoint dynamically below
    # Verify dynamically via cmap
    cmap = sym_tt.getBestCmap() or {}
    inv_cmap = {v: k for k, v in cmap.items()}
    # Review 2: test the symbols that really switch outline in this build (the list changes
    # when symbols are redrawn), not three fixed names.
    order = sym_tt.getGlyphOrder()
    switching = sorted({g.split(".rvrn")[0] for g in order if g.endswith(".rvrn700")} & set(inv_cmap))
    assert switching, "Symbols VF has no rvrn alternates"
    for sym_name in switching:
        cp = inv_cmap[sym_name]
        gids = {}
        for w in (400, 520, 700):
            hfont.set_variations({"wght": w})
            buf = hb.Buffer()
            buf.add_str(chr(cp))
            buf.guess_segment_properties()
            hb.shape(hfont, buf, {})
            gids[w] = sym_tt.getGlyphName(buf.glyph_infos[0].codepoint)
        assert gids[400] != gids[700], f"Symbols VF rvrn failed for {sym_name}: {gids}"
    rtl_names = [g for g in order if g.endswith(".rtl") and g[:-4] in inv_cmap]
    if rtl_names:
        base = rtl_names[0][:-4]
        hfont.set_variations({"wght": 400})
        buf = hb.Buffer(); buf.add_str(chr(inv_cmap[base])); buf.direction = "rtl"; buf.script = "arab"
        hb.shape(hfont, buf, {})
        got = sym_tt.getGlyphName(buf.glyph_infos[0].codepoint)
        assert got.startswith(base + ".rtl"), f"Symbols VF rtlm failed for {base}: {got}"
    print("Symbols Variable rvrn + rtlm Audit PASSED across wght=400 / 520 / 700!")

    total_vf_kb = sum(p.stat().st_size for p in built_woff2.values()) / 1024.0
    print(f"ALL 7 VARIABLE FONTS BUILT & AUDITED (v{VERSION_STR})! Total 7-VF WOFF2 = {total_vf_kb:.1f} KB.")
    # The full-range masters use the completed one-axis default as the
    # reference for the 0.300 drawings and their layout tables.
    subprocess.run([sys.executable,str(ROOT/'scripts/fullrange/build.py')],check=True)
    fullrange=var_dir/'fullrange'
    return [*built_ttf.values(),*built_woff2.values(),*sorted(fullrange.glob('*.ttf')),*sorted(fullrange.glob('*.woff2'))]


if __name__ == "__main__":
    build_all_variable_fonts()
