"""
Admiralty Mono — box drawing (U+2500–U+257F) and block elements (U+2580–U+259F).

All 160 characters are built from rules, not drawn one by one:
  * lines run to the edges of the 600-unit cell and over the full line box (-320 to 980),
    so they join with the next cell and the next line when line-height is 'normal' (1.3);
  * the arms of each box character are read from its Unicode name
    (e.g. "BOX DRAWINGS DOWN LIGHT AND RIGHT HEAVY"), so every combination is consistent;
  * double lines are cut out of a wide band (band minus gap), which gives correct corners,
    tees and crosses without overlapping strokes.
The italics use the same upright shapes, as terminals expect.
"""

from __future__ import annotations
import math
import unicodedata
from typing import Dict, List, Optional, Tuple

import pathops

from design_system import ContourBuilder, rect_contour, union_contours

CELL_W = 600.0
Y_BOT, Y_TOP = -320.0, 980.0
CX, CY = CELL_W / 2.0, (Y_BOT + Y_TOP) / 2.0   # 300, 330

# light line, heavy line and double-line stroke per weight
WEIGHTS = {
    400: dict(t=80.0, T=160.0, d=64.0),
    500: dict(t=92.0, T=184.0, d=74.0),
    700: dict(t=110.0, T=216.0, d=86.0),
}

DIRS = ("UP", "DOWN", "LEFT", "RIGHT")


# ---------------------------------------------------------------------------
# path helpers
# ---------------------------------------------------------------------------

def _rect_path(x0: float, y0: float, x1: float, y1: float) -> pathops.Path:
    p = pathops.Path()
    xa, xb = sorted((x0, x1))
    ya, yb = sorted((y0, y1))
    p.moveTo(xa, ya); p.lineTo(xb, ya); p.lineTo(xb, yb); p.lineTo(xa, yb); p.close()
    return p


def _poly_path(pts: List[Tuple[float, float]]) -> pathops.Path:
    p = pathops.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    p.close()
    return p


def _union(paths: List[pathops.Path]) -> pathops.Path:
    out = pathops.Path()
    if not paths:
        return out
    return pathops.op(paths[0], paths[0], pathops.PathOp.UNION) if len(paths) == 1 else _fold(paths, pathops.PathOp.UNION)


def _fold(paths: List[pathops.Path], op) -> pathops.Path:
    acc = paths[0]
    for p in paths[1:]:
        acc = pathops.op(acc, p, op)
    return acc


def _to_contours(path: pathops.Path) -> List[ContourBuilder]:
    """pathops path (lines and cubics) -> ContourBuilders, coordinates rounded to whole units."""
    out: List[ContourBuilder] = []
    cur: Optional[ContourBuilder] = None
    r = lambda pt: (round(pt[0]), round(pt[1]))
    start = None
    for verb, pts in path:
        if verb == pathops.PathVerb.MOVE:
            start = r(pts[0])
            cur = ContourBuilder(start)
        elif verb == pathops.PathVerb.LINE:
            q = r(pts[0])
            if cur is not None and q != cur_last(cur):
                cur.line_to(*q)
        elif verb == pathops.PathVerb.CUBIC:
            cur.curve_to(r(pts[0]), r(pts[1]), r(pts[2]), smooth=False)
        elif verb == pathops.PathVerb.QUAD:
            p0 = cur_last(cur); c = pts[0]; p3 = pts[1]
            c1 = (p0[0] + 2.0 / 3.0 * (c[0] - p0[0]), p0[1] + 2.0 / 3.0 * (c[1] - p0[1]))
            c2 = (p3[0] + 2.0 / 3.0 * (c[0] - p3[0]), p3[1] + 2.0 / 3.0 * (c[1] - p3[1]))
            cur.curve_to(r(c1), r(c2), r(p3), smooth=False)
        elif verb == pathops.PathVerb.CLOSE:
            if cur is not None:
                if cur.ops and cur.ops[-1][0] == "line" and cur.ops[-1][1] == cur.start:
                    cur.ops.pop()
                if len(cur.ops) >= 2:
                    out.append(cur)
            cur = None
    return out


def cur_last(cb: ContourBuilder) -> Tuple[float, float]:
    if not cb.ops:
        return cb.start
    return cb.ops[-1][-1] if cb.ops[-1][0] == "line" else cb.ops[-1][3]


# ---------------------------------------------------------------------------
# name parser: "BOX DRAWINGS DOWN LIGHT AND RIGHT HEAVY" -> {"DOWN": "L", "RIGHT": "H"}
# ---------------------------------------------------------------------------

_W = {"LIGHT": "L", "HEAVY": "H", "DOUBLE": "D", "SINGLE": "L"}


def parse_arms(name: str) -> Dict[str, str]:
    body = name.replace("BOX DRAWINGS ", "")
    parts = body.split(" AND ")
    parsed = []
    for part in parts:
        words = part.split()
        w = next((_W[x] for x in words if x in _W), None)
        dirs: List[str] = []
        for x in words:
            if x in DIRS:
                dirs.append(x)
            elif x == "VERTICAL":
                dirs += ["UP", "DOWN"]
            elif x == "HORIZONTAL":
                dirs += ["LEFT", "RIGHT"]
        parsed.append([dirs, w])
    # a part without a weight takes the weight of the part before it (or after it)
    for i, p in enumerate(parsed):
        if p[1] is None:
            prev = next((parsed[j][1] for j in range(i - 1, -1, -1) if parsed[j][1]), None)
            nxt = next((parsed[j][1] for j in range(i + 1, len(parsed)) if parsed[j][1]), None)
            p[1] = prev or nxt
    arms: Dict[str, str] = {}
    for dirs, w in parsed:
        for dname in dirs:
            arms[dname] = w
    return arms


# ---------------------------------------------------------------------------
# box characters made of arms
# ---------------------------------------------------------------------------

def _arms_path(arms: Dict[str, str], wt: Dict[str, float]) -> pathops.Path:
    t, T, d = wt["t"], wt["T"], wt["d"]
    o = d * 1.25                      # centre of each double stroke from the cell centre
    half = {"L": t / 2.0, "H": T / 2.0}

    def perp(dname: str) -> Tuple[str, str]:
        return ("LEFT", "RIGHT") if dname in ("UP", "DOWN") else ("UP", "DOWN")

    def opposite(dname: str) -> str:
        return {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}[dname]

    def band(dname: str, w0: float, w1: float, ext: float, overshoot: float = 0.0) -> pathops.Path:
        """Rectangle for one arm: across = [w0, w1] around the axis, along = centre - ext .. edge."""
        if dname == "RIGHT":
            return _rect_path(CX - ext, CY + w0, CELL_W + overshoot, CY + w1)
        if dname == "LEFT":
            return _rect_path(-overshoot, CY + w0, CX + ext, CY + w1)
        if dname == "UP":
            return _rect_path(CX + w0, CY - ext, CX + w1, Y_TOP + overshoot)
        return _rect_path(CX + w0, Y_BOT - overshoot, CX + w1, CY + ext)

    thick, gaps, singles = [], [], []
    for dname, w in arms.items():
        p1, p2 = perp(dname)
        pw = [arms.get(p1), arms.get(p2)]
        perp_double = [x for x in pw if x == "D"]
        perp_single = [half[x] for x in pw if x in half]
        if w == "D":
            if perp_double:
                e_thick, e_gap = o + d / 2.0, o - d / 2.0
            elif perp_single:
                e_thick = e_gap = max(perp_single)
            else:
                e_thick = e_gap = 0.0
            thick.append(band(dname, -o - d / 2.0, o + d / 2.0, e_thick))
            gaps.append(band(dname, -o + d / 2.0, o - d / 2.0, e_gap, overshoot=2.0))
        else:
            hw = half[w]
            if perp_double:
                through = len(perp_double) == 2
                has_opp = opposite(dname) in arms
                if has_opp:
                    ext = 0.0
                elif through:
                    ext = -(o - d / 2.0)         # stop on the near double stroke
                else:
                    ext = o + d / 2.0            # reach the far double stroke (a corner)
            elif perp_single:
                ext = max(perp_single)
            else:
                ext = 0.0
            if opposite(dname) in arms and arms[opposite(dname)] != "D":
                ext = max(ext, 0.0)
            singles.append(band(dname, -hw, hw, ext))
    ink = _fold(thick, pathops.PathOp.UNION) if thick else pathops.Path()
    if gaps:
        ink = pathops.op(ink, _fold(gaps, pathops.PathOp.UNION), pathops.PathOp.DIFFERENCE)
    if singles:
        ink = pathops.op(ink, _fold(singles, pathops.PathOp.UNION), pathops.PathOp.UNION) if thick else _fold(singles + [singles[0]], pathops.PathOp.UNION)
    return ink


def _dashes(horizontal: bool, n: int, w: float) -> pathops.Path:
    paths = []
    length = CELL_W if horizontal else (Y_TOP - Y_BOT)
    period = length / n
    seg = period * 0.62
    for k in range(n):
        a = k * period + (period - seg) / 2.0
        if horizontal:
            paths.append(_rect_path(a, CY - w / 2.0, a + seg, CY + w / 2.0))
        else:
            paths.append(_rect_path(CX - w / 2.0, Y_BOT + a, CX + w / 2.0, Y_BOT + a + seg))
    return _fold(paths, pathops.PathOp.UNION)


def _arc_path(corner: str, t: float) -> pathops.Path:
    """Rounded corner (light arc). corner = the two arms, e.g. ('DOWN', 'RIGHT')."""
    r = 220.0
    k = 0.5523
    sx = 1.0 if "RIGHT" in corner else -1.0
    sy = -1.0 if "DOWN" in corner else 1.0
    # centre of the arc
    ax, ay = CX + sx * r, CY + sy * r
    paths = []
    # straight runs to the edges
    paths.append(_rect_path(ax, CY - t / 2.0, CELL_W if sx > 0 else 0.0, CY + t / 2.0))
    paths.append(_rect_path(CX - t / 2.0, ay, CX + t / 2.0, Y_BOT if sy < 0 else Y_TOP))
    # quarter ring from (CX, ay) to (ax, CY)
    ring = pathops.Path()
    ro, ri = r + t / 2.0, r - t / 2.0

    def q(rad: float, rev: bool = False):
        # points on the quarter circle around (ax, ay), from the vertical run to the horizontal run
        p0 = (ax - sx * rad, ay)
        p3 = (ax, ay - sy * rad)
        c1 = (ax - sx * rad, ay - sy * rad * k)
        c2 = (ax - sx * rad * k, ay - sy * rad)
        return (p3, c2, c1, p0) if rev else (p0, c1, c2, p3)

    o0, o1, o2, o3 = q(ro)
    i0, i1, i2, i3 = q(ri, rev=True)
    ring.moveTo(*o0); ring.cubicTo(*o1, *o2, *o3); ring.lineTo(*i0); ring.cubicTo(*i1, *i2, *i3); ring.close()
    paths.append(ring)
    return _fold(paths, pathops.PathOp.UNION)


def _diag_path(kind: str, t: float) -> pathops.Path:
    def stroke(x0, y0, x1, y1):
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        nx, ny = -dy / L * t / 2.0, dx / L * t / 2.0
        ex, ey = dx / L * t, dy / L * t      # run past the cell, then clip
        return _poly_path([(x0 - ex + nx, y0 - ey + ny), (x1 + ex + nx, y1 + ey + ny),
                           (x1 + ex - nx, y1 + ey - ny), (x0 - ex - nx, y0 - ey - ny)])
    paths = []
    if kind in ("/", "X"):
        paths.append(stroke(0.0, Y_BOT, CELL_W, Y_TOP))
    if kind in ("\\", "X"):
        paths.append(stroke(0.0, Y_TOP, CELL_W, Y_BOT))
    ink = _fold(paths, pathops.PathOp.UNION) if len(paths) > 1 else pathops.op(paths[0], paths[0], pathops.PathOp.UNION)
    return pathops.op(ink, _rect_path(0.0, Y_BOT, CELL_W, Y_TOP), pathops.PathOp.INTERSECTION)


# ---------------------------------------------------------------------------
# block elements
# ---------------------------------------------------------------------------

def _shade(level: int) -> pathops.Path:
    """level 1 = light (25%), 2 = medium (50%), 3 = dark (75%); 100-unit tiles that repeat."""
    paths = []
    s = 50.0
    for i in range(6):
        for j in range(13):
            x, y = i * 100.0, Y_BOT + j * 100.0
            if level == 1:
                paths.append(_rect_path(x, y, x + s, y + s))
            elif level == 2:
                paths.append(_rect_path(x, y, x + s, y + s))
                paths.append(_rect_path(x + s, y + s, x + 100.0, y + 100.0))
            else:
                paths.append(_rect_path(x, y, x + 100.0, y + 100.0))
    ink = _fold(paths, pathops.PathOp.UNION)
    if level == 3:
        holes = _fold([_rect_path(i * 100.0 + s, Y_BOT + j * 100.0 + s, i * 100.0 + 100.0, Y_BOT + j * 100.0 + 100.0)
                       for i in range(6) for j in range(13)], pathops.PathOp.UNION)
        ink = pathops.op(ink, holes, pathops.PathOp.DIFFERENCE)
    return ink


def _block_path(cp: int) -> pathops.Path:
    H = Y_TOP - Y_BOT
    if cp == 0x2580:
        return _rect_path(0, CY, CELL_W, Y_TOP)
    if 0x2581 <= cp <= 0x2588:                        # lower n/8
        n = cp - 0x2580
        return _rect_path(0, Y_BOT, CELL_W, Y_BOT + H * n / 8.0)
    if 0x2589 <= cp <= 0x258F:                        # left 7/8 .. 1/8
        n = 0x2590 - cp
        return _rect_path(0, Y_BOT, CELL_W * n / 8.0, Y_TOP)
    if cp == 0x2590:
        return _rect_path(CX, Y_BOT, CELL_W, Y_TOP)
    if cp in (0x2591, 0x2592, 0x2593):
        return _shade(cp - 0x2590)
    if cp == 0x2594:
        return _rect_path(0, Y_TOP - H / 8.0, CELL_W, Y_TOP)
    if cp == 0x2595:
        return _rect_path(CELL_W * 7 / 8.0, Y_BOT, CELL_W, Y_TOP)
    # quadrants 2596-259F: UL, UR, LL, LR
    quads = {
        0x2596: "LL", 0x2597: "LR", 0x2598: "UL", 0x2599: "UL LL LR", 0x259A: "UL LR",
        0x259B: "UL UR LL", 0x259C: "UL UR LR", 0x259D: "UR", 0x259E: "UR LL", 0x259F: "UR LL LR",
    }
    boxes = {"UL": (0, CY, CX, Y_TOP), "UR": (CX, CY, CELL_W, Y_TOP), "LL": (0, Y_BOT, CX, CY), "LR": (CX, Y_BOT, CELL_W, CY)}
    return _fold([_rect_path(*boxes[q]) for q in quads[cp].split()] + [_rect_path(*boxes[quads[cp].split()[0]])],
                 pathops.PathOp.UNION)


# ---------------------------------------------------------------------------
# public builder
# ---------------------------------------------------------------------------

def glyph_name(cp: int) -> str:
    return f"uni{cp:04X}"


def box_path(cp: int, weight_class: int) -> pathops.Path:
    wt = WEIGHTS[weight_class]
    if cp >= 0x2580:
        return _block_path(cp)
    name = unicodedata.name(chr(cp))
    t, T = wt["t"], wt["T"]
    w = T if "HEAVY" in name else t
    if "DASH" in name:
        n = 2 if "DOUBLE DASH" in name else (3 if "TRIPLE" in name else 4)
        return _dashes("HORIZONTAL" in name, n, w)
    if "ARC" in name:
        return _arc_path(tuple(x for x in DIRS if x in name.split("ARC ")[1]), t)
    if "DIAGONAL" in name:
        return _diag_path("X" if "CROSS" in name else ("/" if "UPPER RIGHT TO LOWER LEFT" in name else "\\"), t)
    return _arms_path(parse_arms(name), wt)


def build_box_glyphs(weight_class: int) -> Dict[str, Tuple[int, int, List[ContourBuilder]]]:
    out: Dict[str, Tuple[int, int, List[ContourBuilder]]] = {}
    for cp in range(0x2500, 0x25A0):
        out[glyph_name(cp)] = (int(CELL_W), cp, _to_contours(box_path(cp, weight_class)))
    return out
