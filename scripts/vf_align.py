"""
Review 2: exact master alignment for the variable fonts.

The old harmonizer re-sampled every outline that did not already match and re-fitted new
curves, which changed the shape of the masters (wobbly edges at weight 400, 500 and 700).

This module makes three contours point-compatible WITHOUT changing their shape:
  1. on-curve points of the masters are matched with a small dynamic program
     (position inside the contour box + direction of the outline at the point);
  2. where one master has a point the other lacks, the other master's segment is split
     at the matching place (de Casteljau: the outline stays exactly the same);
  3. where one master has a line and another a curve, the line is written as a curve
     with its handles on the line (again the same shape).
"""
from __future__ import annotations
import math
from typing import List, Tuple
import numpy as np

Seg = Tuple[str, np.ndarray, np.ndarray, np.ndarray, np.ndarray]

GAP = 0.0045          # cost of leaving one point unmatched (normalised units, squared)
W_DIR = 0.012         # weight of direction differences
W_CORNER = 0.006      # cost when a corner is matched with a smooth point


def _unit(v):
    n = float(np.hypot(v[0], v[1]))
    return v / n if n > 1e-9 else np.zeros(2)


def _seg_dirs(s: Seg):
    _, p0, p1, p2, p3 = s
    out = p1 - p0
    if np.hypot(*out) < 1e-6: out = p2 - p0
    if np.hypot(*out) < 1e-6: out = p3 - p0
    inn = p3 - p2
    if np.hypot(*inn) < 1e-6: inn = p3 - p1
    if np.hypot(*inn) < 1e-6: inn = p3 - p0
    return _unit(out), _unit(inn)


def _eval(s: Seg, t: float):
    _, p0, p1, p2, p3 = s
    mt = 1 - t
    return mt**3 * p0 + 3 * mt * mt * t * p1 + 3 * mt * t * t * p2 + t**3 * p3


def _seg_len_table(s: Seg, n: int = 24):
    ts = np.linspace(0, 1, n + 1)
    pts = np.array([_eval(s, t) for t in ts])
    d = np.hypot(*(np.diff(pts, axis=0).T))
    return ts, np.concatenate([[0.0], np.cumsum(d)])


def _split(s: Seg, t: float) -> Tuple[Seg, Seg]:
    kind, p0, p1, p2, p3 = s
    a = p0 + (p1 - p0) * t; b = p1 + (p2 - p1) * t; c = p2 + (p3 - p2) * t
    d = a + (b - a) * t; e = b + (c - b) * t
    m = d + (e - d) * t
    if kind == "line":
        return ("line", p0, p0 + (m - p0) / 3, p0 + 2 * (m - p0) / 3, m), ("line", m, m + (p3 - m) / 3, m + 2 * (p3 - m) / 3, p3)
    return ("curve", p0, a, d, m), ("curve", m, e, c, p3)


def _split_many(s: Seg, ts: List[float]) -> List[Seg]:
    out, rest, t_prev = [], s, 0.0
    for t in sorted(ts):
        local = (t - t_prev) / max(1 - t_prev, 1e-9)
        local = min(max(local, 0.0), 1.0)
        a, rest = _split(rest, local)
        out.append(a); t_prev = t
    out.append(rest)
    return out


class _Feat:
    def __init__(self, segs: List[Seg]):
        self.segs = segs
        n = len(segs)
        P = np.array([s[1] for s in segs])
        allp = np.array([p for s in segs for p in (s[1], s[2], s[3])])
        mn = allp.min(0); ext = np.maximum(np.ptp(allp, axis=0), 1.0)
        self.npos = (P - mn) / ext
        dirs = [_seg_dirs(s) for s in segs]
        self.out = np.array([dirs[i][0] for i in range(n)])
        self.inn = np.array([dirs[(i - 1) % n][1] for i in range(n)])
        self.corner = np.array([float(np.dot(self.out[i], self.inn[i])) < math.cos(math.radians(20)) for i in range(n)])
        self.n = n


def _cost_matrix(A: _Feat, B: _Feat) -> np.ndarray:
    d = ((A.npos[:, None, :] - B.npos[None, :, :]) ** 2).sum(-1)
    d += W_DIR * (2 - (A.out @ B.out.T) - (A.inn @ B.inn.T))
    d += W_CORNER * (A.corner[:, None] != B.corner[None, :])
    return d


def _align_linear(C: np.ndarray):
    """Global alignment of rows 1..n-1 with columns 1..m-1 (row 0 / column 0 already matched).
    Returns (total cost, list of matched (i, j))."""
    n, m = C.shape
    D = np.full((n, m), np.inf); D[0, 0] = C[0, 0]
    bt = np.zeros((n, m), dtype=np.int8)
    for i in range(n):
        for j in range(m):
            if i == 0 and j == 0: continue
            best, mv = np.inf, 0
            if i > 0 and j > 0 and D[i - 1, j - 1] + C[i, j] < best: best, mv = D[i - 1, j - 1] + C[i, j], 1
            if i > 0 and D[i - 1, j] + GAP < best: best, mv = D[i - 1, j] + GAP, 2
            if j > 0 and D[i, j - 1] + GAP < best: best, mv = D[i, j - 1] + GAP, 3
            D[i, j] = best; bt[i, j] = mv
    i, j, pairs = n - 1, m - 1, []
    while i > 0 or j > 0:
        mv = bt[i, j]
        if mv == 1: pairs.append((i, j)); i -= 1; j -= 1
        elif mv == 2: i -= 1
        else: j -= 1
    pairs.append((0, 0)); pairs.reverse()
    return float(D[n - 1, m - 1]), pairs


def _best_alignment(A: _Feat, B: _Feat):
    C = _cost_matrix(A, B)
    cand = list(np.argsort(C[0])[: min(6, B.n)])
    best = None
    for r in cand:
        idx = [(r + k) % B.n for k in range(B.n)]
        cost, pairs = _align_linear(C[:, idx])
        if best is None or cost < best[0]:
            best = (cost, int(r), pairs)
    return best


def _span_fracs(segs: List[Seg]):
    """arc-length fraction of each interior point of a span, plus per-seg tables."""
    tabs = [_seg_len_table(s) for s in segs]
    lens = np.array([t[1][-1] for t in tabs])
    tot = max(float(lens.sum()), 1e-9)
    cum = np.concatenate([[0.0], np.cumsum(lens)]) / tot
    return list(cum[1:-1]), tabs, cum


def _locate(frac: float, tabs, cum):
    """span fraction -> (segment index, local t)."""
    k = int(np.searchsorted(cum, frac, side="right") - 1)
    k = min(max(k, 0), len(tabs) - 1)
    ts, L = tabs[k]
    span = cum[k + 1] - cum[k]
    local = (frac - cum[k]) / span if span > 1e-12 else 0.5
    t = float(np.interp(local * L[-1], L, ts)) if L[-1] > 1e-9 else local
    return k, min(max(t, 0.0), 1.0)


def _plan_span(fa: List[float], fb: List[float]):
    """Pair interior points of two spans in order; return (splits for A, splits for B) as fractions."""
    ia = ib = 0; add_a, add_b = [], []
    while ia < len(fa) or ib < len(fb):
        if ia < len(fa) and ib < len(fb) and abs(fa[ia] - fb[ib]) < 0.22:
            ia += 1; ib += 1
        elif ib >= len(fb) or (ia < len(fa) and fa[ia] < fb[ib]):
            add_b.append(fa[ia]); ia += 1
        else:
            add_a.append(fb[ib]); ib += 1
    return add_a, add_b


def align_pair(A: List[Seg], B: List[Seg]):
    """Return (ops_a, B_rotated, ops_b, cost). ops = {segment index: [t, ...]} to split."""
    FA, FB = _Feat(A), _Feat(B)
    cost, r, pairs = _best_alignment(FA, FB)
    Br = B[r:] + B[:r]
    ops_a, ops_b = {}, {}
    pairs = pairs + [(len(A), len(Br))]
    for (i0, j0), (i1, j1) in zip(pairs, pairs[1:]):
        sa, sb = A[i0:i1], Br[j0:j1]
        if len(sa) == 1 and len(sb) == 1:
            continue
        fa, taba, cuma = _span_fracs(sa)
        fb, tabb, cumb = _span_fracs(sb)
        add_a, add_b = _plan_span(fa, fb)
        for f in add_a:
            k, t = _locate(f, taba, cuma); ops_a.setdefault(i0 + k, []).append(t)
        for f in add_b:
            k, t = _locate(f, tabb, cumb); ops_b.setdefault(j0 + k, []).append(t)
    return ops_a, Br, ops_b, cost


def apply_ops(segs: List[Seg], ops) -> List[Seg]:
    out = []
    for i, s in enumerate(segs):
        out.extend(_split_many(s, ops[i]) if i in ops else [s])
    return out


def align_three(S0: List[Seg], S1: List[Seg], S2: List[Seg]):
    """Make three closed contours (lists of segments) compatible. Shapes are not changed."""
    ops0, S1r, ops1, c1 = align_pair(S0, S1)
    S0a, S1a = apply_ops(S0, ops0), apply_ops(S1r, ops1)
    if len(S0a) != len(S1a):
        raise ValueError("pair alignment failed")
    ops0b, S2r, ops2, c2 = align_pair(S0a, S2)
    S0b, S1b, S2b = apply_ops(S0a, ops0b), apply_ops(S1a, ops0b), apply_ops(S2r, ops2)
    if not (len(S0b) == len(S1b) == len(S2b)):
        raise ValueError("triple alignment failed")
    out = ([], [], [])
    for a, b, c in zip(S0b, S1b, S2b):
        kind = "curve" if "curve" in (a[0], b[0], c[0]) else "line"
        for dst, s in zip(out, (a, b, c)):
            if kind == "curve" and s[0] == "line":
                p0, p3 = s[1], s[4]
                s = ("curve", p0, p0 + (p3 - p0) / 3, p0 + 2 * (p3 - p0) / 3, p3)
            dst.append(s)
    return out[0], out[1], out[2], max(c1, c2)
