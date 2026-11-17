"""
Admiralty Symbols — Review 2 refinements.

Redrawn symbols that replace the Phase 1 drawings of the same name (see SYMBOL_OVERRIDES_R2,
applied in build_symbols.get_phase1_catalog). Everything is drawn from scratch on the 24x24 grid
with the IconCanvas primitives. Grid angles: 0 = right, 90 = down, 180 = left, 270 = up, and
angles increase clockwise on screen. Arcs are always given with a0 < a1.

What changed and why:
  1. One arrowhead construction (_head) for every arrow, and circular arrows whose head sits on
     the end of the arc and follows its tangent (_arc_arrow): retry, regenerate, sync, restore,
     history, reply, forward-message.
  2. Badly made symbols redrawn: dark-mode, theme, tool, data-controls, tabs, timeout,
     advanced-search, help-center, and the whole cloud family (one cloud shape, one badge system).
  3. Symbols that closed up when small or bold: legal, toggle-on/off, plan, mention, attach, pdf,
     cloud-download, share-app, new.
  4. Pairs made consistent: online/offline share one drawing; every filled variant is the
     outline drawing of its partner with the inside filled, so the silhouettes match.
"""

from __future__ import annotations
import math
from typing import Callable, Dict, List, Optional, Tuple

from symbols_engine import IconCanvas

Pt = Tuple[float, float]


# ---------------------------------------------------------------------------
# Shared geometry helpers
# ---------------------------------------------------------------------------

def _pt(cx: float, cy: float, r: float, ang_deg: float) -> Pt:
    a = math.radians(ang_deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def _head(c: IconCanvas, tip: Pt, ang_deg: float, length: float = 4.2, spread: float = 43.0) -> None:
    """Open chevron arrowhead whose tip is `tip` and which points in direction `ang_deg`."""
    a1 = math.radians(ang_deg + 180.0 - spread)
    a2 = math.radians(ang_deg + 180.0 + spread)
    c.polyline([
        (tip[0] + length * math.cos(a1), tip[1] + length * math.sin(a1)),
        tip,
        (tip[0] + length * math.cos(a2), tip[1] + length * math.sin(a2)),
    ])


def _arc_arrow(
    c: IconCanvas, cx: float, cy: float, r: float, a0: float, a1: float,
    head_at: str = "end", length: float = 4.0, spread: float = 43.0,
) -> None:
    """Arc a0 -> a1 (a0 < a1, clockwise) with an arrowhead on one end that follows the curve."""
    c.arc(cx, cy, r, a0, a1)
    lead = math.degrees(length / (2.0 * r))
    if head_at == "end":
        _head(c, _pt(cx, cy, r, a1), a1 + 90.0 - lead, length, spread)
    else:
        _head(c, _pt(cx, cy, r, a0), a0 - 90.0 + lead, length, spread)


def _circle_isect(c1: Pt, r1: float, c2: Pt, r2: float) -> Tuple[Pt, Pt]:
    dx, dy = c2[0] - c1[0], c2[1] - c1[1]
    d = math.hypot(dx, dy)
    a = (r1 * r1 - r2 * r2 + d * d) / (2.0 * d)
    h = math.sqrt(max(r1 * r1 - a * a, 0.0))
    mx, my = c1[0] + a * dx / d, c1[1] + a * dy / d
    return ((mx + h * dy / d, my - h * dx / d), (mx - h * dy / d, my + h * dx / d))


def _ang(center: Pt, p: Pt) -> float:
    return math.degrees(math.atan2(p[1] - center[1], p[0] - center[0]))


def _spark(c: IconCanvas, cx: float, cy: float, big: float, small: float) -> None:
    """Small solid four-point star."""
    pts: List[Pt] = []
    for k in range(8):
        rad = big if k % 2 == 0 else small
        pts.append(_pt(cx, cy, rad, -90.0 + k * 45.0))
    c.fill_polygon(pts)


# ---------------------------------------------------------------------------
# 1. Arrows
# ---------------------------------------------------------------------------

def _draw_retry(c: IconCanvas) -> None:
    _arc_arrow(c, 12.0, 12.8, 7.4, -25.0, 280.0)


def _draw_regenerate(c: IconCanvas) -> None:
    _arc_arrow(c, 12.0, 12.8, 7.4, -25.0, 280.0)
    _spark(c, 12.0, 12.8, 3.5, 1.25)


def _draw_sync(c: IconCanvas) -> None:
    _arc_arrow(c, 12.0, 12.0, 7.6, 195.0, 335.0, length=3.9)
    _arc_arrow(c, 12.0, 12.0, 7.6, 15.0, 155.0, length=3.9)


def _draw_restore(c: IconCanvas) -> None:
    _arc_arrow(c, 12.4, 12.6, 7.6, 232.0, 532.0, head_at="start")
    c.line(12.4, 16.8, 12.4, 9.6)
    _head(c, (12.4, 9.2), 270.0, length=3.3)


def _draw_history(c: IconCanvas) -> None:
    _arc_arrow(c, 12.4, 12.6, 7.6, 232.0, 532.0, head_at="start")
    c.line(12.4, 8.4, 12.4, 12.8)
    c.line(12.4, 12.8, 15.3, 14.6)


def _draw_reply(c: IconCanvas) -> None:
    c.line(3.8, 10.0, 14.0, 10.0)
    c.arc(14.0, 16.0, 6.0, 270.0, 360.0)
    c.line(20.0, 16.0, 20.0, 19.6)
    _head(c, (3.6, 10.0), 180.0, length=5.4, spread=45.0)


def _draw_forward_message(c: IconCanvas) -> None:
    c.line(20.2, 10.0, 10.0, 10.0)
    c.arc(10.0, 16.0, 6.0, 180.0, 270.0)
    c.line(4.0, 16.0, 4.0, 19.6)
    _head(c, (20.4, 10.0), 0.0, length=5.4, spread=45.0)


# ---------------------------------------------------------------------------
# 2. Cloud family: one cloud, one badge system
# ---------------------------------------------------------------------------

def _cloud(c: IconCanvas, dx: float = 0.0, dy: float = 0.0, gap: Optional[Tuple[float, float]] = None) -> None:
    """Three-lobe cloud with a flat bottom. Lobes meet exactly, so there are no inner strokes.
    `gap` = (x0, x1) leaves the bottom edge open between those x positions."""
    left, rl = (7.6 + dx, 13.6 + dy), 4.4
    top, rt = (12.2 + dx, 10.2 + dy), 5.2
    right, rr = (16.6 + dx, 14.0 + dy), 4.0
    bottom_y = 18.0 + dy
    p_lt = min(_circle_isect(left, rl, top, rt), key=lambda p: p[1])     # upper crossing, left/top
    p_tr = min(_circle_isect(top, rt, right, rr), key=lambda p: p[1])    # upper crossing, top/right
    a_l = _ang(left, p_lt) % 360.0                                       # ~250..290
    c.arc(left[0], left[1], rl, 90.0, a_l)
    a_t0 = _ang(top, p_lt) % 360.0
    a_t1 = _ang(top, p_tr) % 360.0
    if a_t1 < a_t0:
        a_t1 += 360.0
    c.arc(top[0], top[1], rt, a_t0, a_t1)
    a_r = _ang(right, p_tr) % 360.0
    c.arc(right[0], right[1], rr, a_r, 450.0)
    if gap is None:
        c.line(left[0], bottom_y, right[0], bottom_y)
    else:
        if gap[0] > left[0] + 0.2:
            c.line(left[0], bottom_y, gap[0], bottom_y)
        if gap[1] < right[0] - 0.2:
            c.line(gap[1], bottom_y, right[0], bottom_y)


def _draw_cloud(c: IconCanvas) -> None:
    _cloud(c, dy=0.5)


def _draw_cloud_off(c: IconCanvas) -> None:
    _cloud(c, dy=0.5)
    c.slash_off(3.2, 3.2, 20.8, 20.8)


def _draw_cloud_upload(c: IconCanvas) -> None:
    _cloud(c, dy=-1.6, gap=(7.6, 16.6))
    c.line(12.0, 21.2, 12.0, 11.6)
    _head(c, (12.0, 11.2), 270.0, length=3.7, spread=45.0)


def _draw_cloud_download(c: IconCanvas) -> None:
    _cloud(c, dy=-1.6, gap=(7.6, 16.6))
    c.line(12.0, 10.8, 12.0, 21.0)
    _head(c, (12.0, 21.4), 90.0, length=3.7, spread=45.0)


_BADGE = (17.6, 17.4)


def _cloud_with_badge(c: IconCanvas, radius: float = 5.7) -> None:
    """Cloud moved up and left, with the lower right corner cleared for a badge."""
    _cloud(c, dx=-1.0, dy=-1.6)
    c.cut_circle(_BADGE[0], _BADGE[1], radius)


def _draw_backup(c: IconCanvas) -> None:
    # cloud + check: "safely stored"
    _cloud_with_badge(c)
    c.polyline([(14.2, 17.6), (16.7, 20.0), (21.2, 14.9)])


def _draw_restore_backup(c: IconCanvas) -> None:
    # cloud + arrow pointing back: "bring it back"
    _cloud_with_badge(c, radius=5.6)
    c.line(14.4, 17.6, 21.2, 17.6)
    _head(c, (14.2, 17.6), 180.0, length=3.4, spread=45.0)


def _draw_sync_now(c: IconCanvas) -> None:
    # cloud + solid bolt: "do it now"
    _cloud_with_badge(c, radius=5.6)
    c.fill_polygon([(18.9, 12.2), (14.3, 18.3), (17.3, 18.3), (16.3, 22.4), (21.0, 16.2), (18.0, 16.2)])


def _draw_auto_sync(c: IconCanvas) -> None:
    # cloud + A, the same A as in auto-mode
    _cloud_with_badge(c)
    c.polyline([(14.6, 21.0), (17.6, 13.6), (20.6, 21.0)])
    c.line(15.9, 18.4, 19.3, 18.4)


def _draw_sync_paused(c: IconCanvas) -> None:
    _cloud_with_badge(c)
    c.line(15.8, 14.2, 15.8, 20.8)
    c.line(19.6, 14.2, 19.6, 20.8)


def _draw_sync_error(c: IconCanvas) -> None:
    _cloud_with_badge(c, radius=5.2)
    c.line(17.6, 13.4, 17.6, 17.8)
    c.dot(17.6, 20.9, r=(1.45 if c.is_bold else 1.25))


# ---------------------------------------------------------------------------
# 3. Redrawn symbols
# ---------------------------------------------------------------------------

def _draw_dark_mode(c: IconCanvas) -> None:
    # Crescent: the part of circle O that lies outside circle I. The two arcs meet at the tips.
    o, ro = (11.0, 13.0), 8.2
    i, ri = (16.2, 8.2), 7.0
    p, q = _circle_isect(o, ro, i, ri)
    a_p, a_q = _ang(o, p) % 360.0, _ang(o, q) % 360.0
    lo, hi = sorted((a_p, a_q))
    mid = _pt(o[0], o[1], ro, (lo + hi) / 2.0)
    if math.hypot(mid[0] - i[0], mid[1] - i[1]) > ri:      # lo..hi is the outside part
        c.arc(o[0], o[1], ro, lo, hi)
    else:
        c.arc(o[0], o[1], ro, hi, lo + 360.0)
    b_p, b_q = _ang(i, p) % 360.0, _ang(i, q) % 360.0
    lo, hi = sorted((b_p, b_q))
    mid = _pt(i[0], i[1], ri, (lo + hi) / 2.0)
    if math.hypot(mid[0] - o[0], mid[1] - o[1]) < ro:      # lo..hi is inside O
        c.arc(i[0], i[1], ri, lo, hi)
    else:
        c.arc(i[0], i[1], ri, hi, lo + 360.0)


def _draw_theme(c: IconCanvas) -> None:
    # Half-filled disc: solid right half, outlined left half, one clean edge down the middle.
    c.fill_circle(12.0, 12.0, 8.8)
    c.cut_polygon([(1.0, 1.0), (12.0, 1.0), (12.0, 23.0), (1.0, 23.0)])
    c.circle(12.0, 12.0, 8.8)


def _draw_tool(c: IconCanvas) -> None:
    # Wrench: open ring jaw facing up-right, straight handle to the lower left.
    cx, cy, r = 15.4, 8.6, 4.2
    c.arc(cx, cy, r, 15.0, 255.0)
    for a in (15.0, 255.0):
        p = _pt(cx, cy, r, a)
        c.line(p[0], p[1], p[0] + 1.9 * math.cos(math.radians(-45.0)), p[1] + 1.9 * math.sin(math.radians(-45.0)))
    h = _pt(cx, cy, r, 135.0)
    c.line(h[0], h[1], 4.6, 19.4)


def _draw_data_controls(c: IconCanvas) -> None:
    # Database cylinder with two bands, fully inside the grid.
    c.ellipse(12.0, 6.6, 7.2, 2.9)
    c.line(4.8, 6.6, 4.8, 17.4)
    c.line(19.2, 6.6, 19.2, 17.4)
    k = 2.9 * 4.0 / 3.0
    c.cubic_stroke((4.8, 12.0), (4.8, 12.0 + k), (19.2, 12.0 + k), (19.2, 12.0))
    c.cubic_stroke((4.8, 17.4), (4.8, 17.4 + k), (19.2, 17.4 + k), (19.2, 17.4))


def _draw_tabs(c: IconCanvas) -> None:
    # Two tabs standing on a panel.
    c.rect(3.0, 9.0, 18.0, 11.0, rx=2.0)
    c.polyline([(4.6, 9.0), (4.6, 4.6), (11.0, 4.6), (11.0, 9.0)])
    c.polyline([(13.2, 9.0), (13.2, 6.2), (18.6, 6.2), (18.6, 9.0)])


def _draw_timeout(c: IconCanvas) -> None:
    # Clock with a separate alert mark; the clock is cleared around the mark so they never merge.
    c.circle(10.8, 11.0, 7.8)
    c.line(10.8, 6.8, 10.8, 11.2)
    c.line(10.8, 11.2, 13.7, 13.0)
    c.cut_circle(18.8, 17.8, 4.7)
    c.line(18.8, 13.6, 18.8, 17.8)
    c.dot(18.8, 20.9, r=(1.45 if c.is_bold else 1.25))


def _draw_advanced_search(c: IconCanvas) -> None:
    # Magnifier above a slider.
    c.circle(10.2, 8.8, 5.4)
    c.line(14.1, 12.7, 17.4, 16.0)
    c.line(3.4, 20.4, 20.6, 20.4)
    c.cut_circle(8.4, 20.4, 3.0)
    c.circle(8.4, 20.4, 1.7)


def _draw_help_center(c: IconCanvas) -> None:
    # Lifebuoy: two rings and four equal spokes.
    c.circle(12.0, 12.0, 8.8)
    c.circle(12.0, 12.0, 3.5)
    for a in (45.0, 135.0, 225.0, 315.0):
        p0, p1 = _pt(12.0, 12.0, 3.5, a), _pt(12.0, 12.0, 8.8, a)
        c.line(p0[0], p0[1], p1[0], p1[1])


def _draw_legal(c: IconCanvas) -> None:
    # Balance: post, beam, and two open bowls on single cords. No closed triangles to fill in.
    c.line(12.0, 3.8, 12.0, 20.4)
    c.line(8.0, 20.4, 16.0, 20.4)
    c.line(4.6, 7.2, 19.4, 7.2)
    for x in (5.4, 18.6):
        c.line(x, 7.2, x, 13.2)
        c.arc(x, 8.4, 4.8, 48.0, 132.0)


def _draw_toggle_on(c: IconCanvas) -> None:
    # On = solid track, knob on the right.
    c.fill_round_rect(2.5, 6.2, 19.0, 11.6, rx=5.8)
    c.cut_circle(15.7, 12.0, 3.3)


def _draw_toggle_off(c: IconCanvas) -> None:
    # Off = outlined track, solid knob on the left.
    c.rect(2.5, 6.2, 19.0, 11.6, rx=5.8)
    c.fill_circle(8.3, 12.0, (2.7 if c.is_bold else 3.0))


def _draw_plan(c: IconCanvas) -> None:
    # A route between two points.
    c.circle(6.2, 6.4, 2.4)
    c.line(8.6, 6.4, 14.4, 6.4)
    c.arc(14.4, 9.4, 3.0, 270.0, 450.0)
    c.line(14.4, 12.4, 9.6, 12.4)
    c.arc(9.6, 15.0, 2.6, 90.0, 270.0)
    c.line(9.6, 17.6, 15.4, 17.6)
    c.circle(17.8, 17.6, 2.4)


def _draw_mention(c: IconCanvas) -> None:
    # @ with more room between the inner bowl and the outer ring.
    ex, ey = _pt(12.0, 12.0, 9.0, 8.0)
    c.circle(12.0, 12.0, 3.2)
    c.line(15.6, 8.6, 15.6, ey)
    r = (ex - 15.6) / 2.0
    c.arc(15.6 + r, ey, r, 0.0, 180.0)
    c.arc(12.0, 12.0, 9.0, 52.0, 368.0)


def _draw_attach(c: IconCanvas) -> None:
    # Paperclip with three tracks at least 4.5 apart, so it stays open in Bold.
    c.line(7.0, 9.6, 7.0, 15.6)
    c.arc(11.75, 15.6, 4.75, 0.0, 180.0)
    c.line(16.5, 15.6, 16.5, 6.6)
    c.arc(14.0, 6.6, 2.5, 180.0, 360.0)
    c.line(11.5, 6.6, 11.5, 15.0)


def _file(c: IconCanvas) -> None:
    c.polygon([(5.0, 3.0), (13.8, 3.0), (19.0, 8.2), (19.0, 21.0), (5.0, 21.0)])
    c.polyline([(13.8, 3.0), (13.8, 8.2), (19.0, 8.2)])


def _draw_pdf(c: IconCanvas) -> None:
    # Document with a solid label tab that sticks out to the left.
    _file(c)
    c.cut_round_rect(1.2, 11.4, 14.4, 7.4, rx=1.8)
    c.fill_round_rect(2.4, 12.6, 12.0, 5.0, rx=1.2)


def _draw_share_app(c: IconCanvas) -> None:
    # Phone with an arrow leaving it; the phone outline is cleared around the arrow.
    c.rect(4.0, 5.0, 10.6, 16.4, rx=2.2)
    c.line(8.2, 18.2, 10.4, 18.2)
    c.cut_line(11.6, 12.4, 20.4, 3.6, gap=c.sw + 2.4)
    c.cut_polyline([(15.0, 3.6), (20.4, 3.6), (20.4, 9.0)], gap=c.sw + 2.4)
    c.line(11.6, 12.4, 20.4, 3.6)
    c.polyline([(15.0, 3.6), (20.4, 3.6), (20.4, 9.0)])


def _draw_new(c: IconCanvas) -> None:
    # Twelve-point seal with a solid four-point star inside.
    pts: List[Pt] = []
    for k in range(24):
        rad = 9.5 if k % 2 == 0 else 7.9
        pts.append(_pt(12.0, 12.0, rad, -90.0 + k * 15.0))
    c.polygon(pts)
    _spark(c, 12.0, 12.0, (3.9 if c.is_bold else 4.3), 1.45)


def _draw_settings(c: IconCanvas) -> None:
    # Gear: eight flat teeth around a hub.
    pts: List[Pt] = []
    for k in range(8):
        t = k * 45.0
        pts += [_pt(12.0, 12.0, 6.9, t - 14.0), _pt(12.0, 12.0, 9.3, t - 8.5), _pt(12.0, 12.0, 9.3, t + 8.5), _pt(12.0, 12.0, 6.9, t + 14.0)]
    c.polygon(pts)
    c.circle(12.0, 12.0, (2.6 if c.is_bold else 3.0))


def _doc_right(c: IconCanvas) -> None:
    c.polygon([(9.0, 3.0), (16.0, 3.0), (21.0, 8.0), (21.0, 21.0), (9.0, 21.0)])
    c.polyline([(16.0, 3.0), (16.0, 8.0), (21.0, 8.0)])


def _draw_import(c: IconCanvas) -> None:
    # Arrow going into a document (sign-in keeps the arrow-into-door drawing).
    _doc_right(c)
    c.cut_line(2.6, 14.0, 15.6, 14.0, gap=c.sw + 2.4)
    c.line(2.8, 14.0, 14.2, 14.0)
    _head(c, (14.6, 14.0), 0.0, length=3.9, spread=45.0)


def _draw_export(c: IconCanvas) -> None:
    # Arrow leaving a document (sign-out keeps the arrow-out-of-door drawing).
    _doc_right(c)
    c.cut_line(2.6, 14.0, 15.6, 14.0, gap=c.sw + 2.4)
    c.line(3.2, 14.0, 14.8, 14.0)
    _head(c, (2.8, 14.0), 180.0, length=3.9, spread=45.0)


def _draw_new_file(c: IconCanvas) -> None:
    # Document with a plus; the outline is cleared around the plus.
    _file(c)
    c.cut_circle(17.8, 18.0, 5.3)
    c.line(17.8, 14.4, 17.8, 21.6)
    c.line(14.2, 18.0, 21.4, 18.0)


# ---------------------------------------------------------------------------
# 4. Consistent pairs
# ---------------------------------------------------------------------------

def _wifi(c: IconCanvas) -> None:
    c.arc(12.0, 18.4, 11.2, 224.0, 316.0)
    c.arc(12.0, 18.4, 6.4, 224.0, 316.0)
    c.dot(12.0, 18.4, r=1.4)


def _draw_online(c: IconCanvas) -> None:
    _wifi(c)


def _draw_offline(c: IconCanvas) -> None:
    _wifi(c)
    c.slash_off(3.4, 3.4, 20.6, 20.6)


def _star_pts() -> List[Pt]:
    return [_pt(12.0, 12.6, (9.5 if k % 2 == 0 else 4.3), -90.0 + k * 36.0) for k in range(10)]


def _draw_star_filled(c: IconCanvas) -> None:
    c.polygon(_star_pts())
    c.fill_polygon(_star_pts())


_BOOKMARK = [(5.5, 3.2), (18.5, 3.2), (18.5, 20.8), (12.0, 16.2), (5.5, 20.8)]


def _draw_bookmark_filled(c: IconCanvas) -> None:
    c.polygon(_BOOKMARK)
    c.fill_polygon(_BOOKMARK)


_PIN = [(8.5, 4.0), (15.5, 4.0), (14.5, 10.5), (18.5, 14.0), (5.5, 14.0), (9.5, 10.5)]


def _draw_pin_filled(c: IconCanvas) -> None:
    c.polygon(_PIN)
    c.fill_polygon(_PIN)
    c.line(12.0, 14.0, 12.0, 21.5)


_THUMB_UP = [(7.2, 11.2), (11.2, 3.8), (13.6, 4.2), (12.8, 9.5), (19.5, 9.5), (21.0, 12.0), (19.2, 20.0), (7.2, 20.0)]


def _draw_thumbs_up_filled(c: IconCanvas) -> None:
    c.rect(3.0, 10.5, 4.2, 9.5, rx=1.2)
    c.fill_round_rect(3.0, 10.5, 4.2, 9.5, rx=1.2)
    c.polygon(_THUMB_UP)
    c.fill_polygon(_THUMB_UP)
    c.cut_line(7.2, 9.0, 7.2, 22.0, gap=1.0)


def _draw_thumbs_down_filled(c: IconCanvas) -> None:
    pts = [(x, 24.0 - y) for x, y in _THUMB_UP]
    c.rect(3.0, 4.0, 4.2, 9.5, rx=1.2)
    c.fill_round_rect(3.0, 4.0, 4.2, 9.5, rx=1.2)
    c.polygon(pts)
    c.fill_polygon(pts)
    c.cut_line(7.2, 2.0, 7.2, 15.0, gap=1.0)


def _draw_bell_filled(c: IconCanvas) -> None:
    c.polyline([(6.2, 11.5), (6.2, 15.5), (4.0, 17.5), (20.0, 17.5), (17.8, 15.5), (17.8, 11.5)])
    c.arc(12.0, 10.5, 5.8, 180.0, 360.0)
    c.fill_circle(12.0, 10.5, 5.8)
    c.fill_polygon([(6.2, 10.5), (6.2, 15.5), (4.0, 17.5), (20.0, 17.5), (17.8, 15.5), (17.8, 10.5)])
    c.arc(12.0, 18.8, 2.2, 0.0, 180.0)


def _draw_mic_filled(c: IconCanvas) -> None:
    c.rect(9.0, 2.5, 6.0, 10.5, rx=3.0)
    c.fill_round_rect(9.0, 2.5, 6.0, 10.5, rx=3.0)
    c.arc(12.0, 10.2, 6.8, 12.0, 168.0)
    c.line(12.0, 17.0, 12.0, 21.2)
    c.line(8.2, 21.2, 15.8, 21.2)


def _draw_stop_filled(c: IconCanvas) -> None:
    c.rect(5.0, 5.0, 14.0, 14.0, rx=2.5)
    c.fill_round_rect(5.0, 5.0, 14.0, 14.0, rx=2.5)


# ---------------------------------------------------------------------------
# Round 3 (owner feedback, 2026-11-16): help, timeout, history, restore, cloud-off,
# link, unlink, automation, background-task, tabs
# ---------------------------------------------------------------------------

def _ccw_arrow(c: IconCanvas) -> None:
    """Counter-clockwise circular arrow: the exact mirror image of `retry`."""
    _arc_arrow(c, 12.0, 12.8, 7.4, 260.0, 565.0, head_at="start")


def _draw_history_r3(c: IconCanvas) -> None:
    # smaller head and shorter hands than `restore`, so the head never touches the minute hand
    _arc_arrow(c, 12.0, 12.8, 7.6, 262.0, 565.0, head_at="start", length=3.3)
    c.polyline([(12.0, 10.6), (12.0, 13.6), (14.5, 15.1)])


def _draw_restore_r3(c: IconCanvas) -> None:
    # "put it back": the same arrow as history, with a solid centre instead of clock hands
    _ccw_arrow(c)
    c.dot(12.0, 12.8, r=(2.1 if c.is_bold else 1.9))


def _draw_help_r3(c: IconCanvas) -> None:
    c.circle(12.0, 12.0, 9.0)
    # one connected stroke: hook, then down into the stem
    c.arc(12.0, 9.7, 2.75, 182.0, 400.0)
    end = _pt(12.0, 9.7, 2.75, 400.0)
    c.polyline([end, (12.0, 13.1), (12.0, 14.0)])
    c.dot(12.0, 17.1, r=(1.35 if c.is_bold else 1.2))


def _draw_timeout_r3(c: IconCanvas) -> None:
    # Clock that is open on the lower right, where the alert mark stands on its own.
    c.arc(10.6, 11.6, 7.8, 78.0, 322.0)
    c.polyline([(10.6, 7.4), (10.6, 11.8), (13.4, 13.5)])
    c.line(19.4, 11.6, 19.4, 16.4)
    c.dot(19.4, 20.0, r=(1.4 if c.is_bold else 1.25))


def _draw_cloud_off_r3(c: IconCanvas) -> None:
    # The slash stays inside the cloud's box and the cut is wide enough that the two halves
    # of the cloud never join the slash in any weight (one outline topology for 400-700).
    _cloud(c, dy=0.5)
    c.cut_line(4.0, 4.6, 20.0, 20.6, gap=c.sw + 2.6)
    c.line(4.0, 4.6, 20.0, 20.6)


_U = (0.70711, -0.70711)   # along the link, towards upper right
_V = (0.70711, 0.70711)    # across the link, towards lower right


def _uv(u: float, v: float) -> Pt:
    return (12.0 + u * _U[0] + v * _V[0], 12.0 + u * _U[1] + v * _V[1])


def _chain(c: IconCanvas, cu: float, off: float, r: float, near_outer: float, near_inner: float) -> None:
    """Two interlocking U-shaped chain links on the 45 degree diagonal.
    cu = distance of each round end from the centre, off = sideways shift of each link,
    near_outer / near_inner = where the two sides of a link stop (u position)."""
    # upper-right link (round end at +u, shifted to -v)
    c.arc(*_uv(cu, -off), r, 225.0, 405.0)
    c.line(*_uv(cu, -off - r), *_uv(near_outer, -off - r))
    c.line(*_uv(cu, -off + r), *_uv(near_inner, -off + r))
    # lower-left link: the same, turned half a circle
    c.arc(*_uv(-cu, off), r, 45.0, 225.0)
    c.line(*_uv(-cu, off + r), *_uv(-near_outer, off + r))
    c.line(*_uv(-cu, off - r), *_uv(-near_inner, off - r))


def _draw_link_r3(c: IconCanvas) -> None:
    _chain(c, 5.5, 1.45, 3.5, -0.2, 2.6)


def _draw_unlink_r3(c: IconCanvas) -> None:
    # the same two links pulled apart, with two small "break" ticks
    _chain(c, 6.6, 0.0, 3.3, 3.6, 3.6)
    c.line(7.0, 4.0, 8.4, 6.6)
    c.line(4.0, 7.0, 6.6, 8.4)
    c.line(17.0, 20.0, 15.6, 17.4)
    c.line(20.0, 17.0, 17.4, 15.6)


def _draw_automation_r3(c: IconCanvas) -> None:
    # the `retry` arrow (runs again by itself) around a solid bolt
    _arc_arrow(c, 12.0, 12.8, 7.8, -25.0, 280.0)
    c.fill_polygon([(13.3, 7.6), (8.6, 13.7), (11.5, 13.7), (10.7, 18.0), (15.4, 11.9), (12.5, 11.9)])


def _draw_background_task_r3(c: IconCanvas) -> None:
    c.arc(12.0, 12.0, 8.6, 48.0, 272.0)
    d = _pt(12.0, 12.0, 8.6, 340.0)
    c.dot(d[0], d[1], r=(1.7 if c.is_bold else 1.5))
    c.polyline([(12.0, 7.8), (12.0, 12.3), (15.0, 14.1)])


def _draw_tabs_r3(c: IconCanvas) -> None:
    # A window whose top strip is divided into tabs; the left tab is open into the page.
    c.rect(3.0, 4.5, 18.0, 15.0, rx=2.2)
    c.polyline([(10.2, 4.5), (10.2, 9.6), (21.0, 9.6)])
    c.line(15.6, 4.5, 15.6, 9.6)


def _draw_legal_r3(c: IconCanvas) -> None:
    # A gavel: one big shape instead of the scales, whose thin pans closed up at 16 px.
    c.polygon([(13.9, 6.5), (10.5, 3.1), (4.1, 9.5), (7.5, 12.9)])
    c.line(10.9, 9.9, 19.7, 18.7)
    c.line(3.6, 20.4, 12.4, 20.4)


SYMBOL_OVERRIDES_R2: Dict[str, Callable[[IconCanvas], None]] = {
    "help": _draw_help_r3,
    "link": _draw_link_r3,
    "unlink": _draw_unlink_r3,
    "automation": _draw_automation_r3,
    "background-task": _draw_background_task_r3,
    "retry": _draw_retry,
    "regenerate": _draw_regenerate,
    "sync": _draw_sync,
    "restore": _draw_restore_r3,
    "history": _draw_history_r3,
    "reply": _draw_reply,
    "forward-message": _draw_forward_message,
    "cloud": _draw_cloud,
    "cloud-off": _draw_cloud_off_r3,
    "cloud-upload": _draw_cloud_upload,
    "cloud-download": _draw_cloud_download,
    "backup": _draw_backup,
    "restore-backup": _draw_restore_backup,
    "sync-now": _draw_sync_now,
    "auto-sync": _draw_auto_sync,
    "sync-paused": _draw_sync_paused,
    "sync-error": _draw_sync_error,
    "dark-mode": _draw_dark_mode,
    "theme": _draw_theme,
    "tool": _draw_tool,
    "data-controls": _draw_data_controls,
    "tabs": _draw_tabs_r3,
    "timeout": _draw_timeout_r3,
    "advanced-search": _draw_advanced_search,
    "help-center": _draw_help_center,
    "legal": _draw_legal_r3,
    "toggle-on": _draw_toggle_on,
    "toggle-off": _draw_toggle_off,
    "plan": _draw_plan,
    "mention": _draw_mention,
    "attach": _draw_attach,
    "pdf": _draw_pdf,
    "share-app": _draw_share_app,
    "new": _draw_new,
    "new-file": _draw_new_file,
    "settings": _draw_settings,
    "import": _draw_import,
    "export": _draw_export,
    "online": _draw_online,
    "offline": _draw_offline,
    "star-filled": _draw_star_filled,
    "bookmark-filled": _draw_bookmark_filled,
    "pin-filled": _draw_pin_filled,
    "thumbs-up-filled": _draw_thumbs_up_filled,
    "thumbs-down-filled": _draw_thumbs_down_filled,
    "bell-filled": _draw_bell_filled,
    "mic-filled": _draw_mic_filled,
    "stop-filled": _draw_stop_filled,
}
