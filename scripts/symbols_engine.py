"""
Admiralty Symbols Geometric Engine (24x24 grid -> 1000-UPM UFO + standalone SVG).

Features:
- Uniform square 24x24 optical grid mapped to ADVANCE_WIDTH = 840 (60u sidebearings,
  gx in [0..24] -> x in [60..780], gy in [0..24] -> y in [710..-10], cap-centered at y=350).
- Regular stroke width = 2.0 (60u), Bold stroke width = 2.8 (84u).
- Analytical CCW stroke ribbons + exact round caps & round joins unioned/differenced via
  skia-pathops, converted to cubic Beziers via Qu2CuPen, and split at every cubic X/Y
  extremum so all 218 Regular + Bold + RTL glyphs pass Google-Fonts outline audits cleanly.
- Dual-target emission: compiles crisp UFO contours AND standalone 24x24 clean SVGs
  (supporting automatic <mask> knockouts for -off / cutout icons and horizontal RTL mirroring).
"""

from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Any, Callable, Dict, List, Optional, Tuple
from xml.sax.saxutils import escape

from fontTools.misc.bezierTools import solveQuadratic, splitCubicAtT
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.qu2cuPen import Qu2CuPen
from fontTools.pens.recordingPen import RecordingPen
import pathops
import ufoLib2

from design_system import ContourBuilder

GRID_SIZE = 24.0
SYMBOL_ADVANCE_WIDTH = 840
# Review 2: the 24x24 grid is drawn 1.2x larger in the font (36u per grid unit instead of 30u),
# still centred on x = 420 and y = 350 (half the cap height). A typical symbol is now about as
# tall as a capital letter (median 677u against a cap height of 700u), and the strokes
# (72 / 85 / 101u) match the horizontal strokes of Admiralty Sans Regular / Medium / Bold
# (76 / 87 / 102u). The standalone SVGs stay 24x24.
GRID_SCALE = 36.0
GRID_X0 = SYMBOL_ADVANCE_WIDTH / 2.0 - 12.0 * GRID_SCALE   # -12
GRID_Y0 = 350.0 + 12.0 * GRID_SCALE                         # 782

STROKE_REGULAR = 2.0   # 60u in 1000-UPM
STROKE_MEDIUM = 2.35   # 70.5u in 1000-UPM
STROKE_BOLD = 2.8      # 84u in 1000-UPM

KAPPA = 0.5522847498307936


@dataclass(frozen=True)
class SymbolSpec:
    name: str
    category: str
    tags: Tuple[str, ...]
    draw_fn: Callable[["IconCanvas"], None]
    rtl_mirror: bool = False
    is_filled: bool = False
    codepoint: Optional[int] = None


def g2u(gx: float, gy: float) -> Tuple[float, float]:
    """Convert 24x24 top-left grid coordinate to 1000-UPM bottom-left UFO coordinate."""
    return (GRID_X0 + gx * GRID_SCALE, GRID_Y0 - gy * GRID_SCALE)


def _add_contour_pts_to_path(p: pathops.Path, ops: List[Tuple[str, Tuple]], start: Tuple[float, float]) -> None:
    p.moveTo(*start)
    for cmd, args in ops:
        if cmd == "line":
            p.lineTo(*args[0])
        elif cmd == "curve":
            p.cubicTo(*args[0], *args[1], *args[2])
    p.close()


def _ccw_ellipse_path(p: pathops.Path, cx: float, cy: float, rx: float, ry: float, cw: bool = False) -> None:
    if rx <= 1e-5 or ry <= 1e-5:
        return
    kx, ky = rx * KAPPA, ry * KAPPA
    if not cw:
        # CCW in standard mathematical / pathops (+Y up or UFO coords): bottom -> right -> top -> left -> bottom
        p.moveTo(cx, cy - ry)
        p.cubicTo(cx + kx, cy - ry, cx + rx, cy - ky, cx + rx, cy)
        p.cubicTo(cx + rx, cy + ky, cx + kx, cy + ry, cx, cy + ry)
        p.cubicTo(cx - kx, cy + ry, cx - rx, cy + ky, cx - rx, cy)
        p.cubicTo(cx - rx, cy - ky, cx - kx, cy - ry, cx, cy - ry)
        p.close()
    else:
        p.moveTo(cx, cy - ry)
        p.cubicTo(cx - kx, cy - ry, cx - rx, cy - ky, cx - rx, cy)
        p.cubicTo(cx - rx, cy + ky, cx - kx, cy + ry, cx, cy + ry)
        p.cubicTo(cx + kx, cy + ry, cx + rx, cy + ky, cx + rx, cy)
        p.cubicTo(cx + rx, cy - ky, cx + kx, cy - ry, cx, cy - ry)
        p.close()


def _ccw_round_rect_path(
    p: pathops.Path, x0: float, y0: float, x1: float, y1: float, rx: float, cw: bool = False
) -> None:
    """Rounded rect in (+Y up) coordinates where x0 < x1 and y0 < y1."""
    if x1 - x0 <= 1e-5 or y1 - y0 <= 1e-5:
        return
    r = max(0.0, min(rx, (x1 - x0) * 0.5, (y1 - y0) * 0.5))
    if r <= 1e-4:
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        if cw:
            pts.reverse()
        p.moveTo(*pts[0])
        for pt in pts[1:]:
            p.lineTo(*pt)
        p.close()
        return

    k = r * KAPPA
    if not cw:
        p.moveTo(x0 + r, y0)
        p.lineTo(x1 - r, y0)
        p.cubicTo(x1 - r + k, y0, x1, y0 + r - k, x1, y0 + r)
        p.lineTo(x1, y1 - r)
        p.cubicTo(x1, y1 - r + k, x1 - r + k, y1, x1 - r, y1)
        p.lineTo(x0 + r, y1)
        p.cubicTo(x0 + r - k, y1, x0, y1 - r + k, x0, y1 - r)
        p.lineTo(x0, y0 + r)
        p.cubicTo(x0, y0 + r - k, x0 + r - k, y0, x0 + r, y0)
        p.close()
    else:
        p.moveTo(x0 + r, y0)
        p.cubicTo(x0 + r - k, y0, x0, y0 + r - k, x0, y0 + r)
        p.lineTo(x0, y1 - r)
        p.cubicTo(x0, y1 - r + k, x0 + r - k, y1, x0 + r, y1)
        p.lineTo(x1 - r, y1)
        p.cubicTo(x1 - r + k, y1, x1, y1 - r + k, x1, y1 - r)
        p.lineTo(x1, y0 + r)
        p.cubicTo(x1, y0 + r - k, x1 - r + k, y0, x1 - r, y0)
        p.close()


def _arc_points_grid(cx: float, cy: float, r: float, a0_deg: float, a1_deg: float) -> List[Tuple[float, float]]:
    """Sample arc smoothly in grid space (0=right, 90=down in screen coords, Y down)."""
    sweep = a1_deg - a0_deg
    steps = max(8, int(math.ceil(abs(sweep) / 6.0)))
    pts: List[Tuple[float, float]] = []
    for i in range(steps + 1):
        ang = math.radians(a0_deg + sweep * (i / steps))
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


def _add_capsule_segment(path: pathops.Path, ux0: float, uy0: float, ux1: float, uy1: float, radius: float) -> None:
    """Add CCW round-capped thick segment ribbon in UFO space."""
    dx, dy = ux1 - ux0, uy1 - uy0
    length = math.hypot(dx, dy)
    if length < 1e-4:
        _ccw_ellipse_path(path, ux0, uy0, radius, radius)
        return
    tx, ty = dx / length, dy / length
    nx, ny = ty, -tx
    # True CCW quad in (+Y up) UFO coords: right-hand side p0->p1 then left-hand side p1->p0
    q0 = (ux0 + nx * radius, uy0 + ny * radius)
    q1 = (ux1 + nx * radius, uy1 + ny * radius)
    q2 = (ux1 - nx * radius, uy1 - ny * radius)
    q3 = (ux0 - nx * radius, uy0 - ny * radius)
    rect_p = pathops.Path()
    rect_p.moveTo(*q0)
    rect_p.lineTo(*q1)
    rect_p.lineTo(*q2)
    rect_p.lineTo(*q3)
    rect_p.close()
    caps_p = pathops.Path()
    _ccw_ellipse_path(caps_p, ux0, uy0, radius, radius)
    c1_p = pathops.Path()
    _ccw_ellipse_path(c1_p, ux1, uy1, radius, radius)
    united = pathops.op(rect_p, caps_p, pathops.PathOp.UNION, fix_winding=True)
    united = pathops.op(united, c1_p, pathops.PathOp.UNION, fix_winding=True)
    path.addPath(united)


def _split_cubic_at_extrema(
    p0: Tuple[float, float],
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    p3: Tuple[float, float],
) -> List[Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float], Tuple[float, float]]]:
    """Split a cubic Bezier at any interior X or Y extremum t in (0.005, 0.995)."""
    ts: List[float] = []
    for axis in (0, 1):
        c0 = p0[axis]
        c1 = p1[axis]
        c2 = p2[axis]
        c3 = p3[axis]
        # Derivative dB/dt / 3 = a*t^2 + b*t + c
        a = -c0 + 3.0 * c1 - 3.0 * c2 + c3
        b = 2.0 * (c0 - 2.0 * c1 + c2)
        c = c1 - c0
        for root in solveQuadratic(a, b, c):
            if 0.005 < root < 0.995:
                ts.append(root)
    if not ts:
        return [(p0, p1, p2, p3)]
    ts.sort()
    # Deduplicate close roots
    uniq_ts: List[float] = []
    for t in ts:
        if not uniq_ts or abs(t - uniq_ts[-1]) > 0.004:
            uniq_ts.append(t)
    if not uniq_ts:
        return [(p0, p1, p2, p3)]
    # splitCubicAtT accepts multiple t values at once!
    parts = splitCubicAtT(p0, p1, p2, p3, *uniq_ts)
    return list(parts)


def _path_to_clean_contours(sk_path: pathops.Path) -> List[ContourBuilder]:
    """
    Simplify pathops.Path -> clean winding -> convert quadratics cleanly -> cubic contours
    -> split every cubic at internal X/Y extrema -> return ContourBuilder list.
    """
    simplified = pathops.simplify(sk_path, fix_winding=True)
    # Pathops output can contain quadratics if converted via Cu2Qu/pathops internals; Qu2CuPen normalizes.
    rec_raw = RecordingPen()
    simplified.draw(rec_raw)

    # First ensure pure cubic representation via Qu2CuPen into a fresh RecordingPen
    rec_cubic = RecordingPen()
    q2c = Qu2CuPen(rec_cubic, max_err=0.5, all_cubic=True)
    for cmd, pts in rec_raw.value:
        if cmd == "moveTo":
            q2c.moveTo(*pts)
        elif cmd == "lineTo":
            q2c.lineTo(*pts)
        elif cmd == "qCurveTo":
            q2c.qCurveTo(*pts)
        elif cmd == "curveTo":
            q2c.curveTo(*pts)
        elif cmd == "closePath":
            q2c.closePath()
        elif cmd == "endPath":
            q2c.endPath()

    contours: List[ContourBuilder] = []
    cb: Optional[ContourBuilder] = None
    cur: Tuple[float, float] = (0.0, 0.0)
    start_pt: Tuple[float, float] = (0.0, 0.0)

    def _flush() -> None:
        nonlocal cb
        if cb is not None and len(cb.ops) >= 2:
            # Check non-degenerate signed area
            g_tmp = ufoLib2.objects.Glyph()
            cb.draw_to_pen(g_tmp.getPen())
            apen = AreaPen(None)
            g_tmp.draw(apen)
            if abs(apen.value) >= 20.0:
                contours.append(cb)
        cb = None

    for cmd, pts in rec_cubic.value:
        if cmd == "moveTo":
            _flush()
            start_pt = cur = (round(pts[0][0], 2), round(pts[0][1], 2))
            cb = ContourBuilder(start_pt)
        elif cmd == "lineTo" and cb is not None:
            p_end = (round(pts[0][0], 2), round(pts[0][1], 2))
            if math.hypot(p_end[0] - cur[0], p_end[1] - cur[1]) > 0.15:
                cb.line_to(*p_end)
                cur = p_end
        elif cmd == "curveTo" and cb is not None:
            p1 = (round(pts[0][0], 2), round(pts[0][1], 2))
            p2 = (round(pts[1][0], 2), round(pts[1][1], 2))
            p3 = (round(pts[2][0], 2), round(pts[2][1], 2))
            if math.hypot(p3[0] - cur[0], p3[1] - cur[1]) > 0.15:
                sub_segs = _split_cubic_at_extrema(cur, p1, p2, p3)
                for s0, s1, s2, s3 in sub_segs:
                    cb.curve_to(
                        (round(s1[0], 2), round(s1[1], 2)),
                        (round(s2[0], 2), round(s2[1], 2)),
                        (round(s3[0], 2), round(s3[1], 2)),
                        smooth=False,
                    )
                cur = p3
        elif cmd in ("closePath", "endPath"):
            _flush()
    _flush()
    return contours


class IconCanvas:
    """
    Records high-level geometric primitives on the 24x24 icon grid.
    Compiles deterministically to both 1000-UPM UFO cubic contours and 24x24 standalone SVG.
    """

    def __init__(self, sw: float = STROKE_REGULAR) -> None:
        self.sw = float(sw)
        self.commands: List[Tuple[Any, ...]] = []

    @property
    def is_bold(self) -> bool:
        return self.sw >= 2.6

    @property
    def is_medium(self) -> bool:
        return 2.2 <= self.sw < 2.6

    # ------------------------------------------------------------------
    # Stroke Primitives
    # ------------------------------------------------------------------

    def line(self, x0: float, y0: float, x1: float, y1: float, sw: Optional[float] = None) -> "IconCanvas":
        self.commands.append(("line", float(x0), float(y0), float(x1), float(y1), sw))
        return self

    def polyline(
        self, pts: List[Tuple[float, float]], closed: bool = False, sw: Optional[float] = None
    ) -> "IconCanvas":
        self.commands.append(("polyline", [(float(x), float(y)) for x, y in pts], bool(closed), sw))
        return self

    def polygon(self, pts: List[Tuple[float, float]], sw: Optional[float] = None) -> "IconCanvas":
        return self.polyline(pts, closed=True, sw=sw)

    def rect(
        self, x: float, y: float, w: float, h: float, rx: float = 0.0, sw: Optional[float] = None
    ) -> "IconCanvas":
        self.commands.append(("rect", float(x), float(y), float(w), float(h), float(rx), sw))
        return self

    def circle(self, cx: float, cy: float, r: float, sw: Optional[float] = None) -> "IconCanvas":
        self.commands.append(("circle", float(cx), float(cy), float(r), sw))
        return self

    def ellipse(self, cx: float, cy: float, rx: float, ry: float, sw: Optional[float] = None) -> "IconCanvas":
        self.commands.append(("ellipse", float(cx), float(cy), float(rx), float(ry), sw))
        return self

    def arc(
        self,
        cx: float,
        cy: float,
        r: float,
        a0_deg: float,
        a1_deg: float,
        sw: Optional[float] = None,
    ) -> "IconCanvas":
        """Arc in grid coords: 0=+X right, 90=+Y down, 180=-X left, 270=-Y up."""
        self.commands.append(("arc", float(cx), float(cy), float(r), float(a0_deg), float(a1_deg), sw))
        return self

    def cubic_stroke(
        self,
        p0: Tuple[float, float],
        c1: Tuple[float, float],
        c2: Tuple[float, float],
        p3: Tuple[float, float],
        sw: Optional[float] = None,
    ) -> "IconCanvas":
        self.commands.append(("cubic_stroke", p0, c1, c2, p3, sw))
        return self

    # ------------------------------------------------------------------
    # Filled Primitives
    # ------------------------------------------------------------------

    def fill_circle(self, cx: float, cy: float, r: float) -> "IconCanvas":
        self.commands.append(("fill_circle", float(cx), float(cy), float(r)))
        return self

    def fill_round_rect(self, x: float, y: float, w: float, h: float, rx: float = 0.0) -> "IconCanvas":
        self.commands.append(("fill_round_rect", float(x), float(y), float(w), float(h), float(rx)))
        return self

    def fill_polygon(self, pts: List[Tuple[float, float]]) -> "IconCanvas":
        self.commands.append(("fill_polygon", [(float(x), float(y)) for x, y in pts]))
        return self

    def dot(self, cx: float, cy: float, r: Optional[float] = None) -> "IconCanvas":
        """Crisp filled indicator dot scaled gently across Regular, Medium, and Bold."""
        rad = r if r is not None else (1.18 if self.is_bold else (1.06 if self.is_medium else 0.95))
        return self.fill_circle(cx, cy, rad)

    # ------------------------------------------------------------------
    # Subtractive Knockouts / Cutouts (carve from previously drawn ink!)
    # ------------------------------------------------------------------

    def cut_line(self, x0: float, y0: float, x1: float, y1: float, gap: Optional[float] = None) -> "IconCanvas":
        self.commands.append(("cut_line", float(x0), float(y0), float(x1), float(y1), gap))
        return self

    def cut_polyline(
        self, pts: List[Tuple[float, float]], closed: bool = False, gap: Optional[float] = None
    ) -> "IconCanvas":
        self.commands.append(("cut_polyline", [(float(x), float(y)) for x, y in pts], bool(closed), gap))
        return self

    def cut_circle(self, cx: float, cy: float, r: float) -> "IconCanvas":
        self.commands.append(("cut_circle", float(cx), float(cy), float(r)))
        return self

    def cut_round_rect(self, x: float, y: float, w: float, h: float, rx: float = 0.0) -> "IconCanvas":
        self.commands.append(("cut_round_rect", float(x), float(y), float(w), float(h), float(rx)))
        return self

    def cut_polygon(self, pts: List[Tuple[float, float]]) -> "IconCanvas":
        self.commands.append(("cut_polygon", [(float(x), float(y)) for x, y in pts]))
        return self

    def slash_off(
        self, x0: float = 3.0, y0: float = 3.0, x1: float = 21.0, y1: float = 21.0
    ) -> "IconCanvas":
        """Carve a crisp white halo around a diagonal -off slash, then draw the slash on top."""
        halo_w = self.sw + (2.0 if not self.is_bold else 1.8)
        self.cut_line(x0, y0, x1, y1, gap=halo_w)
        self.line(x0, y0, x1, y1)
        return self

    # ------------------------------------------------------------------
    # Horizontal RTL Reflection (gx -> 24.0 - gx)
    # ------------------------------------------------------------------

    def mirrored_horiz(self) -> "IconCanvas":
        m = IconCanvas(self.sw)
        for cmd in self.commands:
            kind = cmd[0]
            if kind == "line":
                _, x0, y0, x1, y1, sw = cmd
                m.commands.append(("line", 24.0 - x0, y0, 24.0 - x1, y1, sw))
            elif kind == "cut_line":
                _, x0, y0, x1, y1, gap = cmd
                m.commands.append(("cut_line", 24.0 - x0, y0, 24.0 - x1, y1, gap))
            elif kind == "polyline":
                _, pts, closed, sw = cmd
                m.commands.append(("polyline", [(24.0 - x, y) for x, y in pts], closed, sw))
            elif kind == "cut_polyline":
                _, pts, closed, gap = cmd
                m.commands.append(("cut_polyline", [(24.0 - x, y) for x, y in pts], closed, gap))
            elif kind == "rect":
                _, x, y, w, h, rx, sw = cmd
                m.commands.append(("rect", 24.0 - (x + w), y, w, h, rx, sw))
            elif kind == "fill_round_rect":
                _, x, y, w, h, rx = cmd
                m.commands.append(("fill_round_rect", 24.0 - (x + w), y, w, h, rx))
            elif kind == "cut_round_rect":
                _, x, y, w, h, rx = cmd
                m.commands.append(("cut_round_rect", 24.0 - (x + w), y, w, h, rx))
            elif kind == "circle":
                _, cx, cy, r, sw = cmd
                m.commands.append(("circle", 24.0 - cx, cy, r, sw))
            elif kind == "ellipse":
                _, cx, cy, rx, ry, sw = cmd
                m.commands.append(("ellipse", 24.0 - cx, cy, rx, ry, sw))
            elif kind == "fill_circle":
                _, cx, cy, r = cmd
                m.commands.append(("fill_circle", 24.0 - cx, cy, r))
            elif kind == "cut_circle":
                _, cx, cy, r = cmd
                m.commands.append(("cut_circle", 24.0 - cx, cy, r))
            elif kind == "fill_polygon":
                _, pts = cmd
                m.commands.append(("fill_polygon", [(24.0 - x, y) for x, y in pts]))
            elif kind == "cut_polygon":
                _, pts = cmd
                m.commands.append(("cut_polygon", [(24.0 - x, y) for x, y in pts]))
            elif kind == "arc":
                _, cx, cy, r, a0, a1, sw = cmd
                m.commands.append(("arc", 24.0 - cx, cy, r, 180.0 - a1, 180.0 - a0, sw))
            elif kind == "cubic_stroke":
                _, p0, c1, c2, p3, sw = cmd
                m.commands.append(
                    (
                        "cubic_stroke",
                        (24.0 - p0[0], p0[1]),
                        (24.0 - c1[0], c1[1]),
                        (24.0 - c2[0], c2[1]),
                        (24.0 - p3[0], p3[1]),
                        sw,
                    )
                )
        return m

    # ------------------------------------------------------------------
    # Compiler 1: 1000-UPM UFO Outlines
    # ------------------------------------------------------------------

    def to_ufo_contours(self) -> List[ContourBuilder]:
        acc = pathops.Path()

        def _stroke_sw(ov: Optional[float]) -> float:
            return (ov if ov is not None else self.sw) * GRID_SCALE

        def _apply_op(shape: pathops.Path, is_cut: bool) -> None:
            nonlocal acc
            shape_clean = pathops.simplify(shape, fix_winding=True)
            op = pathops.PathOp.DIFFERENCE if is_cut else pathops.PathOp.UNION
            acc = pathops.op(acc, shape_clean, op, fix_winding=True)

        for cmd in self.commands:
            kind = cmd[0]
            if kind in ("line", "cut_line"):
                is_cut = kind == "cut_line"
                _, x0, y0, x1, y1, sw_ov = cmd
                rad = 0.5 * _stroke_sw(sw_ov)
                ux0, uy0 = g2u(x0, y0)
                ux1, uy1 = g2u(x1, y1)
                sp = pathops.Path()
                _add_capsule_segment(sp, ux0, uy0, ux1, uy1, rad)
                _apply_op(sp, is_cut)

            elif kind in ("polyline", "cut_polyline"):
                is_cut = kind == "cut_polyline"
                _, pts, closed, sw_ov = cmd
                if not pts:
                    continue
                rad = 0.5 * _stroke_sw(sw_ov)
                sp = pathops.Path()
                if len(pts) == 1:
                    ux, uy = g2u(*pts[0])
                    _ccw_ellipse_path(sp, ux, uy, rad, rad)
                else:
                    n = len(pts)
                    segs = n if closed else n - 1
                    for i in range(segs):
                        p0 = g2u(*pts[i])
                        p1 = g2u(*pts[(i + 1) % n])
                        _add_capsule_segment(sp, p0[0], p0[1], p1[0], p1[1], rad)
                _apply_op(sp, is_cut)

            elif kind == "rect":
                _, x, y, w, h, rx, sw_ov = cmd
                stroke_u = _stroke_sw(sw_ov)
                half = 0.5 * stroke_u
                ux0, uy1 = g2u(x, y)            # top-left in grid -> max Y in UFO
                ux1, uy0 = g2u(x + w, y + h)    # bottom-right in grid -> min Y in UFO
                ru = rx * GRID_SCALE
                outer = pathops.Path()
                _ccw_round_rect_path(outer, ux0 - half, uy0 - half, ux1 + half, uy1 + half, ru + half)
                inner_w = (ux1 - ux0) - stroke_u
                inner_h = (uy1 - uy0) - stroke_u
                if inner_w > 1.0 and inner_h > 1.0:
                    inner = pathops.Path()
                    _ccw_round_rect_path(
                        inner,
                        ux0 + half,
                        uy0 + half,
                        ux1 - half,
                        uy1 - half,
                        max(0.0, ru - half),
                        cw=True,
                    )
                    outer.addPath(inner)
                _apply_op(outer, False)

            elif kind == "circle":
                _, cx, cy, r, sw_ov = cmd
                stroke_u = _stroke_sw(sw_ov)
                half = 0.5 * stroke_u
                ucx, ucy = g2u(cx, cy)
                ru = r * GRID_SCALE
                p = pathops.Path()
                _ccw_ellipse_path(p, ucx, ucy, ru + half, ru + half)
                if ru - half > 1.0:
                    _ccw_ellipse_path(p, ucx, ucy, ru - half, ru - half, cw=True)
                _apply_op(p, False)

            elif kind == "ellipse":
                _, cx, cy, rx, ry, sw_ov = cmd
                stroke_u = _stroke_sw(sw_ov)
                half = 0.5 * stroke_u
                ucx, ucy = g2u(cx, cy)
                rxu, ryu = rx * GRID_SCALE, ry * GRID_SCALE
                p = pathops.Path()
                _ccw_ellipse_path(p, ucx, ucy, rxu + half, ryu + half)
                if rxu - half > 1.0 and ryu - half > 1.0:
                    _ccw_ellipse_path(p, ucx, ucy, rxu - half, ryu - half, cw=True)
                _apply_op(p, False)

            elif kind == "arc":
                _, cx, cy, r, a0, a1, sw_ov = cmd
                rad = 0.5 * _stroke_sw(sw_ov)
                pts = _arc_points_grid(cx, cy, r, a0, a1)
                sp = pathops.Path()
                for i in range(len(pts) - 1):
                    p0 = g2u(*pts[i])
                    p1 = g2u(*pts[i + 1])
                    _add_capsule_segment(sp, p0[0], p0[1], p1[0], p1[1], rad)
                _apply_op(sp, False)

            elif kind == "cubic_stroke":
                _, p0, c1, c2, p3, sw_ov = cmd
                rad = 0.5 * _stroke_sw(sw_ov)
                steps = 22
                sp = pathops.Path()
                u_pts = []
                for i in range(steps + 1):
                    t = i / steps
                    mt = 1.0 - t
                    gx = mt**3 * p0[0] + 3 * mt**2 * t * c1[0] + 3 * mt * t**2 * c2[0] + t**3 * p3[0]
                    gy = mt**3 * p0[1] + 3 * mt**2 * t * c1[1] + 3 * mt * t**2 * c2[1] + t**3 * p3[1]
                    u_pts.append(g2u(gx, gy))
                for i in range(steps):
                    _add_capsule_segment(sp, u_pts[i][0], u_pts[i][1], u_pts[i + 1][0], u_pts[i + 1][1], rad)
                _apply_op(sp, False)

            elif kind in ("fill_circle", "cut_circle"):
                is_cut = kind == "cut_circle"
                _, cx, cy, r = cmd
                ucx, ucy = g2u(cx, cy)
                ru = r * GRID_SCALE
                p = pathops.Path()
                _ccw_ellipse_path(p, ucx, ucy, ru, ru)
                _apply_op(p, is_cut)

            elif kind in ("fill_round_rect", "cut_round_rect"):
                is_cut = kind == "cut_round_rect"
                _, x, y, w, h, rx = cmd
                ux0, uy1 = g2u(x, y)
                ux1, uy0 = g2u(x + w, y + h)
                p = pathops.Path()
                _ccw_round_rect_path(p, ux0, uy0, ux1, uy1, rx * GRID_SCALE)
                _apply_op(p, is_cut)

            elif kind in ("fill_polygon", "cut_polygon"):
                is_cut = kind == "cut_polygon"
                _, pts = cmd
                if len(pts) >= 3:
                    upts = [g2u(gx, gy) for gx, gy in pts]
                    p = pathops.Path()
                    p.moveTo(*upts[0])
                    for pt in upts[1:]:
                        p.lineTo(*pt)
                    p.close()
                    _apply_op(p, is_cut)

        return _path_to_clean_contours(acc)

    # ------------------------------------------------------------------
    # Compiler 2: Clean 24x24 Standalone SVG
    # ------------------------------------------------------------------

    def to_svg(self, title: Optional[str] = None) -> str:
        """Emit clean standalone 24x24 SVG with sequential <mask> support for cut_* knockouts."""
        def _fmt(v: float) -> str:
            r = round(v, 3)
            if abs(r - round(r)) < 1e-3:
                return str(int(round(r)))
            return f"{r:.3f}".rstrip("0").rstrip(".")

        def _render_element(cmd: Tuple[Any, ...], stroke_col: str, fill_col: str, force_sw: Optional[float] = None) -> str:
            kind = cmd[0]
            if kind in ("line", "cut_line"):
                _, x0, y0, x1, y1, sw_ov = cmd
                sw_v = force_sw if force_sw is not None else (sw_ov if sw_ov is not None else self.sw)
                return (
                    f'<line x1="{_fmt(x0)}" y1="{_fmt(y0)}" x2="{_fmt(x1)}" y2="{_fmt(y1)}" '
                    f'stroke="{stroke_col}" stroke-width="{_fmt(sw_v)}" stroke-linecap="round"/>'
                )
            if kind in ("polyline", "cut_polyline"):
                _, pts, closed, sw_ov = cmd
                sw_v = force_sw if force_sw is not None else (sw_ov if sw_ov is not None else self.sw)
                tag = "polygon" if closed else "polyline"
                pstr = " ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in pts)
                return (
                    f'<{tag} points="{pstr}" fill="none" stroke="{stroke_col}" '
                    f'stroke-width="{_fmt(sw_v)}" stroke-linecap="round" stroke-linejoin="round"/>'
                )
            if kind == "rect":
                _, x, y, w, h, rx, sw_ov = cmd
                sw_v = sw_ov if sw_ov is not None else self.sw
                rx_attr = f' rx="{_fmt(rx)}"' if rx > 0 else ""
                return (
                    f'<rect x="{_fmt(x)}" y="{_fmt(y)}" width="{_fmt(w)}" height="{_fmt(h)}"{rx_attr} '
                    f'fill="none" stroke="{stroke_col}" stroke-width="{_fmt(sw_v)}" stroke-linejoin="round"/>'
                )
            if kind == "circle":
                _, cx, cy, r, sw_ov = cmd
                sw_v = sw_ov if sw_ov is not None else self.sw
                return (
                    f'<circle cx="{_fmt(cx)}" cy="{_fmt(cy)}" r="{_fmt(r)}" '
                    f'fill="none" stroke="{stroke_col}" stroke-width="{_fmt(sw_v)}"/>'
                )
            if kind == "ellipse":
                _, cx, cy, rx, ry, sw_ov = cmd
                sw_v = sw_ov if sw_ov is not None else self.sw
                return (
                    f'<ellipse cx="{_fmt(cx)}" cy="{_fmt(cy)}" rx="{_fmt(rx)}" ry="{_fmt(ry)}" '
                    f'fill="none" stroke="{stroke_col}" stroke-width="{_fmt(sw_v)}"/>'
                )
            if kind == "arc":
                _, cx, cy, r, a0, a1, sw_ov = cmd
                sw_v = sw_ov if sw_ov is not None else self.sw
                r0 = math.radians(a0)
                r1 = math.radians(a1)
                sx, sy = cx + r * math.cos(r0), cy + r * math.sin(r0)
                ex, ey = cx + r * math.cos(r1), cy + r * math.sin(r1)
                sweep_diff = a1 - a0
                large_arc = 1 if abs(sweep_diff) > 180.0 else 0
                sweep_flag = 1 if sweep_diff >= 0 else 0
                return (
                    f'<path d="M {_fmt(sx)} {_fmt(sy)} A {_fmt(r)} {_fmt(r)} 0 {large_arc} {sweep_flag} '
                    f'{_fmt(ex)} {_fmt(ey)}" fill="none" stroke="{stroke_col}" '
                    f'stroke-width="{_fmt(sw_v)}" stroke-linecap="round"/>'
                )
            if kind == "cubic_stroke":
                _, p0, c1, c2, p3, sw_ov = cmd
                sw_v = sw_ov if sw_ov is not None else self.sw
                return (
                    f'<path d="M {_fmt(p0[0])} {_fmt(p0[1])} C {_fmt(c1[0])} {_fmt(c1[1])}, '
                    f'{_fmt(c2[0])} {_fmt(c2[1])}, {_fmt(p3[0])} {_fmt(p3[1])}" '
                    f'fill="none" stroke="{stroke_col}" stroke-width="{_fmt(sw_v)}" stroke-linecap="round"/>'
                )
            if kind in ("fill_circle", "cut_circle"):
                _, cx, cy, r = cmd
                return f'<circle cx="{_fmt(cx)}" cy="{_fmt(cy)}" r="{_fmt(r)}" fill="{fill_col}"/>'
            if kind in ("fill_round_rect", "cut_round_rect"):
                _, x, y, w, h, rx = cmd
                rx_attr = f' rx="{_fmt(rx)}"' if rx > 0 else ""
                return f'<rect x="{_fmt(x)}" y="{_fmt(y)}" width="{_fmt(w)}" height="{_fmt(h)}"{rx_attr} fill="{fill_col}"/>'
            if kind in ("fill_polygon", "cut_polygon"):
                _, pts = cmd
                pstr = " ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in pts)
                return f'<polygon points="{pstr}" fill="{fill_col}"/>'
            return ""

        # Split commands into layers separated by cuts so SVG mask ordering matches UFO pathops order!
        layers: List[Tuple[str, List[Tuple[Any, ...]]]] = []
        cur_draws: List[Tuple[Any, ...]] = []
        cut_batches: List[Tuple[int, List[Tuple[Any, ...]]]] = []

        # Build sequential tree cleanly: every cut applies to all currently accumulated DOM
        dom_nodes: List[str] = []
        mask_idx = 0
        for cmd in self.commands:
            is_cut = cmd[0].startswith("cut_")
            if not is_cut:
                el = _render_element(cmd, "currentColor", "currentColor")
                if el:
                    dom_nodes.append(el)
            else:
                mask_idx += 1
                mid = f"cut-{mask_idx}"
                if cmd[0] in ("cut_line", "cut_polyline"):
                    gap_w = cmd[-1] if cmd[-1] is not None else (self.sw + 1.8)
                    cut_el = _render_element(cmd, "black", "black", force_sw=gap_w)
                else:
                    cut_el = _render_element(cmd, "black", "black")
                prev_body = "".join(dom_nodes)
                mask_def = f'<defs><mask id="{mid}"><rect width="24" height="24" fill="white"/>{cut_el}</mask></defs>'
                dom_nodes = [f"{mask_def}<g mask=\"url(#{mid})\">{prev_body}</g>"]

        title_el = f"<title>{escape(title)}</title>" if title else ""
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
            'width="24" height="24" fill="none">'
            f"{title_el}{''.join(dom_nodes)}</svg>\n"
        )
