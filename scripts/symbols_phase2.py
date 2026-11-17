"""
Admiralty Symbols — Phase 2 (62 new symbols, added for version 0.300).

New code points follow the 218 Phase 1 symbols (U+E0DA onwards), in the order of SYMBOLS_PHASE2.
All drawings are original and use the IconCanvas primitives on the 24 x 24 grid
(angles: 0 = right, 90 = down, angles grow clockwise on screen, arcs always a0 < a1).
Symbols that already existed under another name were not drawn again:
gift (whats-new), light bulb (tips), clock (recent), alarm (reminder), globe (language),
external link (new-window), waveform (voice-message), table (spreadsheet), database (data-controls).
"""

from __future__ import annotations
import math
from typing import List, Tuple

from symbols_engine import IconCanvas, SymbolSpec
from symbols_refine_r2 import _arc_arrow, _head, _pt, _spark

Pt = Tuple[float, float]


# ---------------------------------------------------------------------------
# Shared parts
# ---------------------------------------------------------------------------

def _union_outline(c: IconCanvas, circles: List[Tuple[float, float, float]], step: float = 1.0,
                   hidden: List[Tuple[float, float, float]] = ()) -> None:
    """Outline of a union of circles: each circle is drawn only where it is not inside another.
    `hidden` circles are part of the shape (they hide outlines) but are not drawn."""
    masks = list(circles) + list(hidden)
    for i, (cx, cy, r) in enumerate(circles):
        vis = []
        n = int(round(360.0 / step))
        for k in range(n):
            a = k * step
            x, y = cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
            inside = any(
                j != i and math.hypot(x - ox, y - oy) < orr - 0.05 for j, (ox, oy, orr) in enumerate(masks)
            )
            vis.append(not inside)
        if all(vis):
            c.circle(cx, cy, r)
            continue
        # rotate so that the list starts on a hidden sample, then collect visible runs
        k0 = vis.index(False)
        runs, start = [], None
        for k in range(n + 1):
            idx = (k0 + k) % n
            if vis[idx] and start is None:
                start = k0 + k
            if (not vis[idx] or k == n) and start is not None:
                runs.append((start * step, (k0 + k) * step))
                start = None
        for a0, a1 in runs:
            if a1 - a0 >= step * 1.5:
                c.arc(cx, cy, r, a0, a1)


def _monitor(c: IconCanvas, x: float = 2.5, y: float = 3.5, w: float = 19.0, h: float = 12.5) -> None:
    c.rect(x, y, w, h, rx=2.0)
    cx = x + w / 2.0
    c.line(cx, y + h, cx, y + h + 3.6)
    c.line(cx - 4.2, y + h + 3.8, cx + 4.2, y + h + 3.8)


def _bubble(c: IconCanvas, x: float = 3.0, y: float = 3.5, w: float = 18.0, h: float = 13.5, tail_x: float = 7.4) -> None:
    """Speech bubble with a tail on the lower left."""
    c.rect(x, y, w, h, rx=3.4)
    yb = y + h
    c.cut_line(tail_x + 0.6, yb, tail_x + 4.2, yb, gap=c.sw + 0.3)
    c.polyline([(tail_x, yb - 0.4), (tail_x, yb + 3.8), (tail_x + 4.6, yb)])


def _speaker(c: IconCanvas, dx: float = 0.0) -> None:
    c.polygon([(3.0 + dx, 9.0), (7.0 + dx, 9.0), (12.0 + dx, 4.6), (12.0 + dx, 19.4), (7.0 + dx, 15.0), (3.0 + dx, 15.0)])


def _corners(c: IconCanvas, lo: float = 3.0, hi: float = 21.0, arm: float = 5.0) -> None:
    for (x, y, sx, sy) in ((lo, lo, 1, 1), (hi, lo, -1, 1), (lo, hi, 1, -1), (hi, hi, -1, -1)):
        c.polyline([(x, y + sy * arm), (x, y), (x + sx * arm, y)])


def _clock_badge(c: IconCanvas, cx: float, cy: float, r: float = 4.4) -> None:
    c.cut_circle(cx, cy, r + c.sw * 0.5 + 1.0)
    c.circle(cx, cy, r)
    c.polyline([(cx, cy - r * 0.55), (cx, cy), (cx + r * 0.45, cy + r * 0.3)])


# ---------------------------------------------------------------------------
# Devices
# ---------------------------------------------------------------------------

def _draw_computer(c: IconCanvas) -> None:
    _monitor(c)


def _draw_laptop(c: IconCanvas) -> None:
    c.rect(4.5, 4.5, 15.0, 10.5, rx=1.8)
    c.line(2.2, 18.8, 21.8, 18.8)


def _draw_phone(c: IconCanvas) -> None:
    c.rect(6.5, 2.5, 11.0, 19.0, rx=2.6)
    c.line(10.6, 18.2, 13.4, 18.2)


def _draw_tablet(c: IconCanvas) -> None:
    c.rect(4.0, 3.0, 16.0, 18.0, rx=2.6)
    c.dot(12.0, 17.6)


def _draw_watch(c: IconCanvas) -> None:
    c.rect(6.8, 6.8, 10.4, 10.4, rx=2.8)
    c.polyline([(8.8, 6.8), (9.6, 2.8), (14.4, 2.8), (15.2, 6.8)])
    c.polyline([(8.8, 17.2), (9.6, 21.2), (14.4, 21.2), (15.2, 17.2)])


def _draw_devices(c: IconCanvas) -> None:
    c.rect(2.0, 4.0, 14.5, 10.5, rx=1.8)
    c.line(9.25, 14.5, 9.25, 18.2)
    c.line(5.6, 18.6, 12.0, 18.6)
    c.cut_round_rect(13.2, 7.6, 10.2, 15.0, rx=2.6)
    c.rect(15.0, 9.4, 6.6, 11.4, rx=1.8)
    c.line(17.6, 18.0, 19.0, 18.0)


def _draw_browser(c: IconCanvas) -> None:
    # a web page: window with a toolbar (three dots) and lines of content
    c.rect(2.5, 3.5, 19.0, 17.0, rx=2.2)
    c.line(2.5, 8.4, 21.5, 8.4)
    d = 1.05 if c.is_bold else 0.95
    for x in (5.4, 8.0, 10.6):
        c.dot(x, 5.95, r=d)
    c.line(6.2, 12.6, 17.8, 12.6)
    c.line(6.2, 16.4, 13.4, 16.4)


# ---------------------------------------------------------------------------
# Agent and tools
# ---------------------------------------------------------------------------

def _draw_brain(c: IconCanvas) -> None:
    # two hemispheres with a softly scalloped edge, split by a centre line
    circles = []
    for side in (-1.0, 1.0):
        for a in (-80.0, -40.0, 0.0, 40.0, 80.0):
            rad = math.radians(a)
            circles.append((12.0 + side * (4.6 * math.cos(rad) + 1.6), 12.0 + 6.0 * math.sin(rad), 3.3))
    _union_outline(c, circles, hidden=[(9.0, 12.0, 5.4), (15.0, 12.0, 5.4), (12.0, 8.0, 4.4), (12.0, 16.0, 4.4)])
    c.line(12.0, 4.6, 12.0, 19.4)
    c.cubic_stroke((6.4, 10.4), (8.2, 9.4), (9.8, 10.4), (9.6, 12.8))
    c.cubic_stroke((17.6, 13.6), (15.8, 14.6), (14.2, 13.6), (14.4, 11.2))


def _draw_web_search(c: IconCanvas) -> None:
    c.circle(10.0, 10.0, 7.2)
    c.ellipse(10.0, 10.0, 3.0, 7.2)
    c.line(2.8, 10.0, 17.2, 10.0)
    c.cut_circle(17.0, 17.0, 5.6)
    c.circle(16.6, 16.6, 3.0)
    c.line(18.8, 18.8, 21.2, 21.2)


def _draw_deep_research(c: IconCanvas) -> None:
    c.circle(10.5, 10.5, 7.0)
    c.line(15.6, 15.6, 20.8, 20.8)
    _spark(c, 10.5, 10.5, 3.8, 1.2)


def _draw_project(c: IconCanvas) -> None:
    c.rect(2.8, 7.0, 18.4, 13.0, rx=2.2)
    c.polyline([(8.8, 7.0), (8.8, 4.2), (15.2, 4.2), (15.2, 7.0)])
    c.line(2.8, 12.6, 21.2, 12.6)
    c.line(12.0, 11.4, 12.0, 14.0)


def _draw_artifact(c: IconCanvas) -> None:
    c.rect(2.8, 2.8, 18.4, 18.4, rx=2.4)
    c.circle(8.8, 8.8, 2.4)
    c.polygon([(12.2, 17.6), (15.4, 11.6), (18.6, 17.6)])


def _draw_summarize(c: IconCanvas) -> None:
    c.line(3.5, 5.5, 20.5, 5.5)
    c.line(3.5, 10.0, 20.5, 10.0)
    c.line(3.5, 14.5, 11.5, 14.5)
    _spark(c, 17.6, 17.4, 4.0, 1.3)


def _draw_translate(c: IconCanvas) -> None:
    # Latin capital A (upper left) and a simplified CJK character (lower right)
    c.polyline([(2.8, 13.0), (6.6, 3.2), (10.4, 13.0)])
    c.line(4.2, 9.6, 9.0, 9.6)
    c.line(12.6, 13.4, 21.4, 13.4)
    c.line(17.0, 10.6, 17.0, 13.4)
    c.cubic_stroke((14.2, 13.8), (15.2, 17.6), (17.4, 19.6), (21.0, 20.8))
    c.cubic_stroke((19.8, 13.8), (18.8, 17.6), (16.6, 19.6), (13.0, 20.8))


def _draw_computer_use(c: IconCanvas) -> None:
    _monitor(c)
    ptr = [(9.6, 6.2), (9.6, 14.0), (11.4, 12.4), (12.7, 15.2), (14.2, 14.5), (12.9, 11.8), (15.3, 11.6)]
    c.cut_polygon([(8.4, 4.8), (8.4, 16.4), (11.0, 14.4), (12.2, 16.8), (15.8, 15.2), (14.8, 13.0), (17.6, 12.6)])
    c.fill_polygon(ptr)


def _draw_screen_share(c: IconCanvas) -> None:
    _monitor(c)
    c.line(12.0, 13.0, 12.0, 6.8)
    _head(c, (12.0, 6.6), 270.0, 3.4)


def _draw_extension(c: IconCanvas) -> None:
    dx, dy = -1.0, 0.6
    r = 2.4
    c.polyline([(4.0 + dx, 21.0 + dy), (4.0 + dx, 6.8 + dy), (9.16 + dx, 6.8 + dy)])
    c.arc(11.0 + dx, 5.25 + dy, r, 140.0, 400.0)
    c.polyline([(12.84 + dx, 6.8 + dy), (18.0 + dx, 6.8 + dy), (18.0 + dx, 12.16 + dy)])
    c.arc(19.6 + dx, 14.0 + dy, r, 230.0, 490.0)
    c.polyline([(18.0 + dx, 15.84 + dy), (18.0 + dx, 21.0 + dy), (4.0 + dx, 21.0 + dy)])


def _brace(c: IconCanvas, x: float, s: float) -> None:
    """Curly brace; s = +1 opens to the right ({), -1 opens to the left (})."""
    xo, xm, xt = x, x - 2.4 * s, x - 4.6 * s
    c.cubic_stroke((xo, 3.5), (xo - 2.0 * s, 3.5), (xm, 4.4), (xm, 6.6))
    c.line(xm, 6.6, xm, 9.6)
    c.cubic_stroke((xm, 9.6), (xm, 11.2), (xt + 1.0 * s, 12.0), (xt, 12.0))
    c.cubic_stroke((xt, 12.0), (xt + 1.0 * s, 12.0), (xm, 12.8), (xm, 14.4))
    c.line(xm, 14.4, xm, 17.4)
    c.cubic_stroke((xm, 17.4), (xm, 19.6), (xo - 2.0 * s, 20.5), (xo, 20.5))


def _draw_api(c: IconCanvas) -> None:
    _brace(c, 9.0, 1.0)
    _brace(c, 15.0, -1.0)
    c.dot(12.0, 12.0, r=(1.5 if c.is_bold else 1.3))


def _draw_server(c: IconCanvas) -> None:
    c.rect(3.0, 3.5, 18.0, 7.4, rx=1.8)
    c.rect(3.0, 13.1, 18.0, 7.4, rx=1.8)
    c.dot(7.0, 7.2)
    c.dot(7.0, 16.8)
    c.line(11.0, 7.2, 17.0, 7.2)
    c.line(11.0, 16.8, 17.0, 16.8)


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

def _draw_chat(c: IconCanvas) -> None:
    _bubble(c)


def _draw_new_chat(c: IconCanvas) -> None:
    _bubble(c)
    c.line(12.0, 7.0, 12.0, 13.4)
    c.line(8.8, 10.2, 15.2, 10.2)


def _draw_conversations(c: IconCanvas) -> None:
    c.rect(9.0, 2.6, 12.6, 9.6, rx=2.8)
    c.cut_round_rect(1.2, 6.6, 15.8, 13.0, rx=3.6)
    _bubble(c, x=2.4, y=8.0, w=13.0, h=9.4, tail_x=5.8)


def _draw_edit_message(c: IconCanvas) -> None:
    _bubble(c)
    c.polygon([(8.4, 13.4), (8.8, 11.4), (13.6, 6.6), (15.2, 8.2), (10.4, 13.0)])


def _draw_read_receipt(c: IconCanvas) -> None:
    c.polyline([(2.4, 12.6), (6.4, 16.6), (14.0, 8.0)])
    c.polyline([(11.0, 15.4), (12.2, 16.6), (19.8, 8.0)])


def _draw_schedule_send(c: IconCanvas) -> None:
    c.polygon([(2.8, 4.0), (20.4, 12.0), (2.8, 20.0), (5.8, 12.0)])
    c.line(5.8, 12.0, 11.0, 12.0)
    _clock_badge(c, 17.8, 17.8, 3.6)


def _draw_hashtag(c: IconCanvas) -> None:
    c.line(9.8, 3.5, 7.8, 20.5)
    c.line(16.2, 3.5, 14.2, 20.5)
    c.line(4.0, 8.6, 20.2, 8.6)
    c.line(3.8, 15.4, 20.0, 15.4)


def _draw_keyboard(c: IconCanvas) -> None:
    c.rect(2.0, 5.5, 20.0, 13.0, rx=2.2)
    for y in (9.4, 12.4):
        for x in (6.0, 9.4, 12.8, 16.2):
            c.dot(x + (1.0 if y > 10 else 0.0), y, r=(1.2 if c.is_bold else 1.05))
    c.line(8.2, 15.4, 15.8, 15.4)


def _draw_command(c: IconCanvas) -> None:
    lo, hi, r = 9.4, 14.6, 2.8
    c.line(lo, lo - 0.2, lo, hi + 0.2)
    c.line(hi, lo - 0.2, hi, hi + 0.2)
    c.line(lo - 0.2, lo, hi + 0.2, lo)
    c.line(lo - 0.2, hi, hi + 0.2, hi)
    c.arc(lo - r, lo - r, r, 90.0, 360.0)
    c.arc(hi + r, lo - r, r, 180.0, 450.0)
    c.arc(lo - r, hi + r, r, 0.0, 270.0)
    c.arc(hi + r, hi + r, r, 270.0, 540.0)


# ---------------------------------------------------------------------------
# Account, billing and security
# ---------------------------------------------------------------------------

def _draw_usage(c: IconCanvas) -> None:
    c.arc(12.0, 13.6, 8.6, 150.0, 390.0)
    c.line(12.0, 13.6, 16.4, 9.2)
    c.dot(12.0, 13.6, r=(1.8 if c.is_bold else 1.6))
    c.line(6.4, 19.4, 17.6, 19.4)


def _draw_appearance(c: IconCanvas) -> None:
    r = 9.0
    a_end, a_start = 350.0, 62.0
    c.arc(12.0, 12.0, r, a_start, a_end)
    p_end, p_start = _pt(12.0, 12.0, r, a_end), _pt(12.0, 12.0, r, a_start)
    c.cubic_stroke(p_end, (20.8, 13.6), (18.6, 14.6), (16.4, 14.6))
    c.cubic_stroke((16.4, 14.6), (14.2, 14.6), (14.0, 17.4), p_start)
    d = 1.5 if c.is_bold else 1.35
    for (x, y) in ((7.2, 12.4), (8.6, 7.8), (13.2, 6.4), (17.0, 9.0)):
        c.dot(x, y, r=d)


def _draw_billing(c: IconCanvas) -> None:
    c.rect(2.5, 5.0, 19.0, 14.0, rx=2.2)
    c.line(2.5, 9.6, 21.5, 9.6)
    c.line(5.6, 15.4, 9.8, 15.4)


def _draw_receipt(c: IconCanvas) -> None:
    xs = [19.0, 16.67, 14.33, 12.0, 9.67, 7.33, 5.0]
    zig = [(x, 21.0 if k % 2 == 0 else 19.4) for k, x in enumerate(xs)]
    c.polygon([(5.0, 3.0), (19.0, 3.0)] + zig)
    c.line(8.4, 7.6, 15.6, 7.6)
    c.line(8.4, 11.4, 15.6, 11.4)
    c.line(8.4, 15.2, 12.6, 15.2)


def _draw_wallet(c: IconCanvas) -> None:
    c.rect(2.5, 6.0, 19.0, 14.0, rx=2.4)
    c.rect(14.8, 10.4, 6.7, 5.2, rx=1.6)
    c.dot(17.6, 13.0)
    c.polyline([(5.2, 6.0), (15.6, 3.0), (17.0, 6.0)])


def _draw_subscription(c: IconCanvas) -> None:
    c.rect(2.5, 4.0, 19.0, 16.0, rx=2.4)
    _arc_arrow(c, 12.0, 12.2, 4.2, -20.0, 285.0, length=3.0)


def _draw_face_id(c: IconCanvas) -> None:
    _corners(c)
    c.line(9.0, 8.6, 9.0, 10.6)
    c.line(15.0, 8.6, 15.0, 10.6)
    c.arc(12.0, 11.6, 4.4, 35.0, 145.0)


def _draw_fingerprint(c: IconCanvas) -> None:
    c.arc(12.0, 12.4, 9.6, 205.0, 335.0)
    c.arc(12.0, 13.6, 6.2, 180.0, 360.0)
    c.line(5.8, 13.6, 5.8, 17.0)
    c.line(18.2, 13.6, 18.2, 19.2)
    c.arc(12.0, 14.2, 2.6, 180.0, 360.0)
    c.line(9.4, 14.2, 9.4, 20.8)
    c.line(14.6, 14.2, 14.6, 19.0)


def _draw_qr_code(c: IconCanvas) -> None:
    for (x, y) in ((3.0, 3.0), (14.0, 3.0), (3.0, 14.0)):
        c.rect(x, y, 7.0, 7.0, rx=1.2)
        c.fill_round_rect(x + 2.3, y + 2.3, 2.4, 2.4, rx=0.4)
    for (x, y) in ((14.0, 14.0), (18.6, 14.0), (14.0, 18.6), (18.6, 18.6)):
        c.fill_round_rect(x, y, 2.4, 2.4, rx=0.4)


def _draw_scan(c: IconCanvas) -> None:
    _corners(c)
    c.line(3.0, 12.0, 21.0, 12.0)


# ---------------------------------------------------------------------------
# Time and places
# ---------------------------------------------------------------------------

def _calendar(c: IconCanvas) -> None:
    c.rect(3.0, 4.6, 18.0, 16.4, rx=2.4)
    c.line(3.0, 9.6, 21.0, 9.6)
    c.line(8.0, 2.6, 8.0, 6.6)
    c.line(16.0, 2.6, 16.0, 6.6)


def _draw_calendar(c: IconCanvas) -> None:
    _calendar(c)
    c.dot(8.0, 14.0)
    c.dot(12.0, 14.0)
    c.dot(16.0, 14.0)
    c.dot(8.0, 17.6)
    c.dot(12.0, 17.6)


def _draw_scheduled_task(c: IconCanvas) -> None:
    _calendar(c)
    _clock_badge(c, 16.8, 16.8, 4.4)


def _draw_timer(c: IconCanvas) -> None:
    c.circle(12.0, 13.6, 7.6)
    c.line(12.0, 13.6, 12.0, 9.4)
    c.line(9.6, 2.8, 14.4, 2.8)
    c.line(12.0, 3.0, 12.0, 6.0)
    c.line(18.0, 6.6, 19.6, 5.0)


def _draw_location(c: IconCanvas) -> None:
    cx, cy, r = 12.0, 9.6, 6.6
    c.arc(cx, cy, r, 150.0, 390.0)
    a, b = _pt(cx, cy, r, 150.0), _pt(cx, cy, r, 390.0)
    c.cubic_stroke(b, (16.4, 15.6), (13.6, 18.8), (12.0, 21.2))
    c.cubic_stroke((12.0, 21.2), (10.4, 18.8), (7.6, 15.6), a)
    c.circle(cx, cy, 2.4)


def _draw_map(c: IconCanvas) -> None:
    c.polygon([(3.0, 5.6), (9.0, 3.4), (15.0, 5.6), (21.0, 3.4), (21.0, 18.4), (15.0, 20.6), (9.0, 18.4), (3.0, 20.6)])
    c.line(9.0, 3.4, 9.0, 18.4)
    c.line(15.0, 5.6, 15.0, 20.6)


# ---------------------------------------------------------------------------
# Media and voice
# ---------------------------------------------------------------------------

def _draw_play(c: IconCanvas) -> None:
    c.polygon([(7.0, 4.4), (19.4, 12.0), (7.0, 19.6)])


def _draw_pause(c: IconCanvas) -> None:
    w = c.sw * 1.35
    c.line(8.6, 5.0, 8.6, 19.0, sw=w)
    c.line(15.4, 5.0, 15.4, 19.0, sw=w)


def _draw_volume(c: IconCanvas) -> None:
    _speaker(c)
    c.arc(12.6, 12.0, 4.0, -48.0, 48.0)
    c.arc(12.6, 12.0, 7.8, -50.0, 50.0)


def _draw_mute(c: IconCanvas) -> None:
    _speaker(c)
    c.line(15.6, 9.4, 20.8, 14.6)
    c.line(20.8, 9.4, 15.6, 14.6)


def _draw_headphones(c: IconCanvas) -> None:
    c.arc(12.0, 13.0, 8.4, 180.0, 360.0)
    c.rect(3.6, 13.0, 4.6, 7.4, rx=1.6)
    c.rect(15.8, 13.0, 4.6, 7.4, rx=1.6)


def _draw_read_aloud(c: IconCanvas) -> None:
    c.line(3.0, 6.0, 12.6, 6.0)
    c.line(3.0, 10.2, 10.2, 10.2)
    c.line(3.0, 14.4, 7.8, 14.4)
    c.arc(12.6, 14.6, 3.6, -55.0, 55.0)
    c.arc(12.6, 14.6, 7.4, -52.0, 52.0)


def _draw_subtitles(c: IconCanvas) -> None:
    c.rect(2.5, 4.6, 19.0, 14.8, rx=2.4)
    c.line(6.0, 11.4, 10.6, 11.4)
    c.line(13.4, 11.4, 18.0, 11.4)
    c.line(6.0, 15.4, 14.6, 15.4)


def _draw_record(c: IconCanvas) -> None:
    c.circle(12.0, 12.0, 8.6)
    c.fill_circle(12.0, 12.0, 4.2)


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

def _draw_bar_chart(c: IconCanvas) -> None:
    w = c.sw * 1.35
    c.line(6.0, 19.6, 6.0, 12.4, sw=w)
    c.line(12.0, 19.6, 12.0, 4.6, sw=w)
    c.line(18.0, 19.6, 18.0, 9.0, sw=w)


def _draw_line_chart(c: IconCanvas) -> None:
    c.polyline([(3.0, 3.0), (3.0, 21.0), (21.0, 21.0)])
    c.polyline([(6.6, 16.0), (10.6, 10.8), (14.2, 14.2), (19.6, 6.6)])


def _draw_pie_chart(c: IconCanvas) -> None:
    cx, cy, r = 10.6, 13.4, 7.6
    c.arc(cx, cy, r, 0.0, 270.0)
    c.line(cx, cy, cx, cy - r)
    c.line(cx, cy, cx + r, cy)
    ex, ey = cx + 2.8, cy - 2.8
    c.arc(ex, ey, r, 270.0, 360.0)
    c.line(ex, ey, ex, ey - r)
    c.line(ex, ey, ex + r, ey)


def _draw_trending_up(c: IconCanvas) -> None:
    c.polyline([(2.8, 17.4), (9.0, 11.2), (13.0, 15.2), (20.6, 7.6)])
    c.polyline([(15.4, 7.6), (20.6, 7.6), (20.6, 12.8)])


# ---------------------------------------------------------------------------
# Communication
# ---------------------------------------------------------------------------

def _draw_mail(c: IconCanvas) -> None:
    c.rect(2.5, 5.0, 19.0, 14.0, rx=2.2)
    c.polyline([(3.2, 6.4), (12.0, 13.0), (20.8, 6.4)])


def _draw_inbox(c: IconCanvas) -> None:
    c.rect(3.0, 4.0, 18.0, 16.0, rx=2.4)
    c.polyline([(3.0, 13.4), (8.0, 13.4), (9.6, 16.4), (14.4, 16.4), (16.0, 13.4), (21.0, 13.4)])


def _draw_phone_call(c: IconCanvas) -> None:
    c.polyline([(5.4, 3.4), (9.0, 3.4), (10.8, 8.0), (8.4, 9.6)])
    c.cubic_stroke((8.4, 9.6), (9.6, 12.2), (11.8, 14.4), (14.4, 15.6))
    c.polyline([(14.4, 15.6), (16.0, 13.2), (20.6, 15.0), (20.6, 18.6)])
    c.cubic_stroke((20.6, 18.6), (20.6, 19.8), (19.7, 20.6), (18.5, 20.6))
    c.cubic_stroke((18.5, 20.6), (10.2, 20.0), (4.0, 13.8), (3.4, 5.5))
    c.cubic_stroke((3.4, 5.5), (3.4, 4.3), (4.2, 3.4), (5.4, 3.4))


def _draw_contacts(c: IconCanvas) -> None:
    c.rect(5.2, 2.8, 15.4, 18.4, rx=2.2)
    c.circle(12.9, 9.6, 2.8)
    c.arc(12.9, 18.6, 4.8, 200.0, 340.0)
    for y in (7.0, 12.0, 17.0):
        c.line(3.2, y, 6.6, y)


# ---------------------------------------------------------------------------
# Common
# ---------------------------------------------------------------------------

def _draw_drag_handle(c: IconCanvas) -> None:
    d = 1.6 if c.is_bold else 1.45
    for x in (9.0, 15.0):
        for y in (6.0, 12.0, 18.0):
            c.dot(x, y, r=d)


def _draw_heart(c: IconCanvas) -> None:
    r = 4.6
    c.arc(8.0, 9.0, r, 140.0, 330.4)
    c.arc(16.0, 9.0, r, 209.6, 400.0)
    c.line(*_pt(8.0, 9.0, r, 140.0), 12.0, 20.0)
    c.line(*_pt(16.0, 9.0, r, 400.0), 12.0, 20.0)


def _draw_bug(c: IconCanvas) -> None:
    c.ellipse(12.0, 14.4, 4.6, 6.0)
    c.line(12.0, 10.4, 12.0, 20.2)
    c.arc(12.0, 8.6, 2.8, 180.0, 360.0)
    c.line(10.2, 6.4, 8.8, 3.6)
    c.line(13.8, 6.4, 15.2, 3.6)
    for (y0, y1) in ((10.6, 11.8), (14.6, 14.6), (18.6, 17.4)):
        c.line(3.6, y0, 7.4, y1)
        c.line(20.4, y0, 16.6, y1)


SYMBOLS_PHASE2: List[SymbolSpec] = [
    # Devices
    SymbolSpec("computer", "Devices", ("desktop", "monitor", "pc"), _draw_computer),
    SymbolSpec("laptop", "Devices", ("notebook", "macbook", "computer"), _draw_laptop),
    SymbolSpec("phone", "Devices", ("mobile", "smartphone", "device"), _draw_phone),
    SymbolSpec("tablet", "Devices", ("ipad", "device", "screen"), _draw_tablet),
    SymbolSpec("watch", "Devices", ("wearable", "smartwatch", "device"), _draw_watch),
    SymbolSpec("devices", "Devices", ("computer-phone", "sync", "cross-device"), _draw_devices),
    SymbolSpec("browser", "Devices", ("web", "website", "internet"), _draw_browser),
    # Agent and tools
    SymbolSpec("brain", "Agent and tools", ("thinking", "reasoning", "mind"), _draw_brain),
    SymbolSpec("web-search", "Agent and tools", ("internet", "globe", "lookup"), _draw_web_search),
    SymbolSpec("deep-research", "Agent and tools", ("investigate", "report", "analysis"), _draw_deep_research),
    SymbolSpec("project", "Agent and tools", ("workspace", "briefcase", "work"), _draw_project),
    SymbolSpec("artifact", "Agent and tools", ("canvas", "output", "creation"), _draw_artifact),
    SymbolSpec("summarize", "Agent and tools", ("tldr", "digest", "condense"), _draw_summarize),
    SymbolSpec("translate", "Agent and tools", ("language", "localize", "convert"), _draw_translate),
    SymbolSpec("computer-use", "Agent and tools", ("cursor", "control", "automation"), _draw_computer_use),
    SymbolSpec("screen-share", "Agent and tools", ("present", "cast", "display"), _draw_screen_share),
    SymbolSpec("extension", "Agent and tools", ("plugin", "integration", "puzzle"), _draw_extension),
    SymbolSpec("api", "Agent and tools", ("developer", "endpoint", "json"), _draw_api),
    SymbolSpec("server", "Agent and tools", ("host", "backend", "infrastructure"), _draw_server),
    # Chat
    SymbolSpec("chat", "Chat", ("message", "bubble", "conversation"), _draw_chat),
    SymbolSpec("new-chat", "Chat", ("compose", "start", "conversation"), _draw_new_chat),
    SymbolSpec("conversations", "Chat", ("threads", "history", "messages"), _draw_conversations),
    SymbolSpec("edit-message", "Chat", ("revise", "change", "message"), _draw_edit_message),
    SymbolSpec("read-receipt", "Chat", ("seen", "double-check", "delivered"), _draw_read_receipt),
    SymbolSpec("schedule-send", "Chat", ("later", "delay", "queue"), _draw_schedule_send, rtl_mirror=True),
    SymbolSpec("hashtag", "Chat", ("channel", "topic", "tag"), _draw_hashtag),
    SymbolSpec("keyboard", "Chat", ("type", "input", "keys"), _draw_keyboard),
    SymbolSpec("command", "Chat", ("shortcut", "cmd", "hotkey"), _draw_command),
    # Account, billing and security
    SymbolSpec("usage", "Account and billing", ("quota", "gauge", "limit"), _draw_usage),
    SymbolSpec("appearance", "Account and billing", ("palette", "colors", "style"), _draw_appearance),
    SymbolSpec("billing", "Account and billing", ("credit-card", "payment", "card"), _draw_billing),
    SymbolSpec("receipt", "Account and billing", ("invoice", "bill", "purchase"), _draw_receipt),
    SymbolSpec("wallet", "Account and billing", ("balance", "credits", "money"), _draw_wallet),
    SymbolSpec("subscription", "Account and billing", ("plan", "renew", "recurring"), _draw_subscription),
    SymbolSpec("face-id", "Account and billing", ("face", "biometric", "unlock"), _draw_face_id),
    SymbolSpec("fingerprint", "Account and billing", ("touch-id", "biometric", "unlock"), _draw_fingerprint),
    SymbolSpec("qr-code", "Account and billing", ("code", "link", "pair"), _draw_qr_code),
    SymbolSpec("scan", "Account and billing", ("capture", "camera", "document"), _draw_scan),
    # Time and places
    SymbolSpec("calendar", "Time and places", ("date", "event", "schedule"), _draw_calendar),
    SymbolSpec("scheduled-task", "Time and places", ("routine", "cron", "later"), _draw_scheduled_task),
    SymbolSpec("timer", "Time and places", ("stopwatch", "duration", "countdown"), _draw_timer),
    SymbolSpec("location", "Time and places", ("place", "map-pin", "address"), _draw_location),
    SymbolSpec("map", "Time and places", ("directions", "route", "area"), _draw_map),
    # Media and voice
    SymbolSpec("play", "Media and voice", ("start", "resume", "media"), _draw_play, rtl_mirror=True),
    SymbolSpec("pause", "Media and voice", ("hold", "media", "break"), _draw_pause),
    SymbolSpec("volume", "Media and voice", ("sound", "speaker", "audio"), _draw_volume, rtl_mirror=True),
    SymbolSpec("mute", "Media and voice", ("silent", "sound-off", "speaker"), _draw_mute, rtl_mirror=True),
    SymbolSpec("headphones", "Media and voice", ("listen", "audio", "earphones"), _draw_headphones),
    SymbolSpec("read-aloud", "Media and voice", ("speak", "text-to-speech", "voice"), _draw_read_aloud, rtl_mirror=True),
    SymbolSpec("subtitles", "Media and voice", ("captions", "transcript", "cc"), _draw_subtitles),
    SymbolSpec("record", "Media and voice", ("capture", "rec", "dictate"), _draw_record),
    # Data
    SymbolSpec("bar-chart", "Data", ("statistics", "analytics", "columns"), _draw_bar_chart),
    SymbolSpec("line-chart", "Data", ("trend", "graph", "analytics"), _draw_line_chart),
    SymbolSpec("pie-chart", "Data", ("share", "breakdown", "segments"), _draw_pie_chart),
    SymbolSpec("trending-up", "Data", ("growth", "increase", "rise"), _draw_trending_up, rtl_mirror=True),
    # Communication
    SymbolSpec("mail", "Communication", ("email", "envelope", "message"), _draw_mail),
    SymbolSpec("inbox", "Communication", ("tray", "messages", "received"), _draw_inbox),
    SymbolSpec("phone-call", "Communication", ("call", "telephone", "voice"), _draw_phone_call),
    SymbolSpec("contacts", "Communication", ("address-book", "people", "directory"), _draw_contacts),
    # Common
    SymbolSpec("drag-handle", "Common", ("grip", "reorder", "move"), _draw_drag_handle),
    SymbolSpec("heart", "Common", ("like", "favorite", "love"), _draw_heart),
    SymbolSpec("bug", "Common", ("debug", "issue", "error"), _draw_bug),
]

assert len(SYMBOLS_PHASE2) == 62, len(SYMBOLS_PHASE2)
