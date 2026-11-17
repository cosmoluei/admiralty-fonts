"""
Admiralty Symbols Phase 1 — Part A (99 icons):
  1. Chat (24)
  2. Agent and AI (24)
  3. Navigation and layout (32)
  4. Status and feedback (19)
"""

from __future__ import annotations
import math
from typing import List

from symbols_engine import IconCanvas, SymbolSpec


def _draw_send(c: IconCanvas) -> None:
    c.polygon([(3.0, 11.2), (21.0, 3.0), (12.8, 21.0), (10.2, 13.8)])
    c.line(10.2, 13.8, 20.5, 3.5)


def _draw_stop(c: IconCanvas) -> None:
    c.rect(5.0, 5.0, 14.0, 14.0, rx=2.5)


def _draw_mic(c: IconCanvas) -> None:
    c.rect(9.0, 2.5, 6.0, 10.5, rx=3.0)
    c.arc(12.0, 10.2, 6.8, 12.0, 168.0)
    c.line(12.0, 17.0, 12.0, 21.2)
    c.line(8.2, 21.2, 15.8, 21.2)


def _draw_mic_off(c: IconCanvas) -> None:
    _draw_mic(c)
    c.slash_off(3.0, 3.0, 21.0, 21.0)


def _draw_attach(c: IconCanvas) -> None:
    # Paperclip with generous >= 4u parallel track separation for Bold legibility
    c.line(7.5, 8.0, 7.5, 15.5)
    c.arc(12.0, 15.5, 4.5, 0.0, 180.0)
    c.line(16.5, 15.5, 16.5, 6.2)
    c.arc(13.25, 6.2, 3.25, 180.0, 360.0)
    c.line(10.0, 6.2, 10.0, 14.2)


def _draw_image(c: IconCanvas) -> None:
    c.rect(3.0, 4.0, 18.0, 16.0, rx=2.2)
    c.dot(8.2, 9.0, r=1.25)
    c.polyline([(3.8, 17.8), (9.8, 12.2), (13.8, 15.8), (16.5, 13.0), (20.2, 16.8)])


def _draw_camera(c: IconCanvas) -> None:
    c.polygon([
        (3.0, 8.5), (7.2, 8.5), (9.0, 5.0), (15.0, 5.0),
        (16.8, 8.5), (21.0, 8.5), (21.0, 19.5), (3.0, 19.5),
    ])
    c.circle(12.0, 13.5, 3.6)


def _draw_copy(c: IconCanvas) -> None:
    c.rect(8.5, 8.5, 12.0, 12.0, rx=2.0)
    c.polyline([(15.5, 5.5), (15.5, 4.0), (4.0, 4.0), (4.0, 15.5), (5.5, 15.5)])


def _draw_paste(c: IconCanvas) -> None:
    c.rect(4.0, 5.5, 11.5, 14.5, rx=1.8)
    c.rect(7.8, 3.0, 4.0, 3.0, rx=1.0)
    c.cut_round_rect(9.0, 8.5, 12.5, 13.0, rx=2.4)
    c.rect(10.5, 9.8, 9.5, 11.2, rx=1.8)


def _draw_cut(c: IconCanvas) -> None:
    c.circle(6.5, 17.5, 2.8)
    c.circle(17.5, 17.5, 2.8)
    c.line(8.5, 15.3, 18.2, 4.2)
    c.line(15.5, 15.3, 5.8, 4.2)


def _draw_retry(c: IconCanvas) -> None:
    c.arc(12.0, 12.0, 7.6, -50.0, 235.0)
    c.polyline([(15.8, 3.8), (18.8, 6.2), (14.8, 8.5)])


def _draw_regenerate(c: IconCanvas) -> None:
    c.arc(12.0, 12.0, 8.0, 25.0, 150.0)
    c.arc(12.0, 12.0, 8.0, 205.0, 330.0)
    c.polyline([(17.0, 4.5), (20.2, 7.2), (16.5, 9.5)])
    c.polyline([(7.0, 19.5), (3.8, 16.8), (7.5, 14.5)])
    c.dot(12.0, 12.0, r=1.5)


def _draw_edit(c: IconCanvas) -> None:
    c.polygon([(16.0, 3.2), (20.8, 8.0), (8.8, 20.0), (3.5, 20.5), (4.0, 15.2)])
    c.line(13.2, 6.0, 18.0, 10.8)


def _draw_delete(c: IconCanvas) -> None:
    c.polygon([(8.8, 5.0), (21.0, 5.0), (21.0, 19.0), (8.8, 19.0), (3.0, 12.0)])
    c.line(12.5, 9.5, 17.2, 14.5)
    c.line(17.2, 9.5, 12.5, 14.5)


def _draw_reply(c: IconCanvas) -> None:
    c.polyline([(8.8, 4.5), (3.5, 9.5), (8.8, 14.5)])
    c.line(4.0, 9.5, 14.5, 9.5)
    c.arc(14.5, 14.5, 5.0, -90.0, 45.0)
    c.line(19.5, 14.5, 19.5, 19.5)


def _draw_forward_message(c: IconCanvas) -> None:
    c.polyline([(15.2, 4.5), (20.5, 9.5), (15.2, 14.5)])
    c.line(20.0, 9.5, 9.5, 9.5)
    c.arc(9.5, 14.5, 5.0, 135.0, 270.0)
    c.line(4.5, 14.5, 4.5, 19.5)


def _draw_quote(c: IconCanvas) -> None:
    for ox in (5.0, 14.0):
        c.rect(ox, 6.0, 5.0, 6.5, rx=1.4)
        c.cubic_stroke((ox + 4.8, 11.5), (ox + 4.8, 15.5), (ox + 3.0, 17.8), (ox + 0.5, 18.5))


def _draw_pin(c: IconCanvas) -> None:
    c.polygon([
        (8.5, 4.0), (15.5, 4.0), (14.5, 10.5),
        (18.5, 14.0), (5.5, 14.0), (9.5, 10.5),
    ])
    c.line(12.0, 14.0, 12.0, 21.5)


def _draw_unpin(c: IconCanvas) -> None:
    _draw_pin(c)
    c.slash_off(3.0, 3.0, 21.0, 21.0)


def _draw_mention(c: IconCanvas) -> None:
    c.circle(12.0, 12.0, 3.6)
    c.line(15.6, 8.6, 15.6, 13.8)
    c.arc(17.9, 13.8, 2.3, 0.0, 175.0)
    c.line(20.2, 12.0, 20.2, 13.8)
    c.arc(12.0, 12.0, 8.2, 42.0, 360.0)


def _draw_emoji(c: IconCanvas) -> None:
    c.circle(12.0, 12.0, 9.0)
    c.dot(8.8, 9.8, r=1.15)
    c.dot(15.2, 9.8, r=1.15)
    c.arc(12.0, 12.0, 4.8, 28.0, 152.0)


def _draw_thumbs_up(c: IconCanvas) -> None:
    c.rect(3.0, 10.5, 4.2, 9.5, rx=1.2)
    c.polygon([
        (7.2, 11.2), (11.2, 3.8), (13.6, 4.2), (12.8, 9.5),
        (19.5, 9.5), (21.0, 12.0), (19.2, 20.0), (7.2, 20.0),
    ])


def _draw_thumbs_down(c: IconCanvas) -> None:
    c.rect(3.0, 4.0, 4.2, 9.5, rx=1.2)
    c.polygon([
        (7.2, 12.8), (11.2, 20.2), (13.6, 19.8), (12.8, 14.5),
        (19.5, 14.5), (21.0, 12.0), (19.2, 4.0), (7.2, 4.0),
    ])


def _draw_voice_message(c: IconCanvas) -> None:
    bars = [(3.8, 9.5, 14.5), (7.9, 6.0, 18.0), (12.0, 3.5, 20.5), (16.1, 7.2, 16.8), (20.2, 10.0, 14.0)]
    for bx, y0, y1 in bars:
        c.line(bx, y0, bx, y1)


# --- 2. Agent and AI (24) ---

def _draw_agent(c: IconCanvas) -> None:
    c.line(12.0, 3.2, 12.0, 6.8)
    c.dot(12.0, 2.8, r=1.05)
    c.rect(4.0, 6.8, 16.0, 13.5, rx=3.6)
    c.dot(9.0, 12.8, r=1.2)
    c.dot(15.0, 12.8, r=1.2)
    c.line(9.5, 16.8, 14.5, 16.8)


def _draw_user(c: IconCanvas) -> None:
    c.circle(12.0, 7.5, 3.8)
    c.arc(12.0, 21.5, 8.2, 198.0, 342.0)


def _draw_team(c: IconCanvas) -> None:
    c.circle(9.2, 7.8, 3.2)
    c.arc(9.2, 20.2, 6.4, 198.0, 342.0)
    c.circle(16.8, 8.6, 2.5)
    c.arc(16.8, 20.2, 4.8, 240.0, 342.0)


def _draw_tool(c: IconCanvas) -> None:
    # Diagonal wrench with hexagonal open jaw
    c.line(4.5, 19.5, 13.5, 10.5)
    c.polyline([(13.2, 10.8), (12.5, 6.2), (16.5, 3.5), (18.8, 5.8), (16.5, 8.2), (18.2, 9.8), (20.5, 7.5), (21.5, 10.0), (17.5, 12.5), (13.2, 10.8)])


def _draw_plug(c: IconCanvas) -> None:
    c.line(9.2, 3.5, 9.2, 8.5)
    c.line(14.8, 3.5, 14.8, 8.5)
    c.line(6.5, 8.5, 17.5, 8.5)
    c.line(6.5, 8.5, 6.5, 12.0)
    c.line(17.5, 8.5, 17.5, 12.0)
    c.arc(12.0, 12.0, 5.5, 0.0, 180.0)
    c.line(12.0, 17.5, 12.0, 21.5)


def _draw_memory(c: IconCanvas) -> None:
    c.rect(5.5, 5.5, 13.0, 13.0, rx=2.0)
    c.rect(9.8, 9.8, 4.4, 4.4, rx=0.6)
    for d in (9.0, 15.0):
        c.line(d, 2.5, d, 5.5)
        c.line(d, 18.5, d, 21.5)
        c.line(2.5, d, 5.5, d)
        c.line(18.5, d, 21.5, d)


def _draw_task_list(c: IconCanvas) -> None:
    c.polyline([(3.5, 6.5), (5.2, 8.2), (8.2, 4.8)])
    c.line(11.2, 6.5, 20.5, 6.5)
    c.line(4.0, 12.2, 7.8, 12.2)
    c.line(11.2, 12.2, 20.5, 12.2)
    c.line(4.0, 17.8, 7.8, 17.8)
    c.line(11.2, 17.8, 20.5, 17.8)


def _draw_reminder(c: IconCanvas) -> None:
    c.circle(12.0, 13.0, 7.5)
    c.line(12.0, 9.2, 12.0, 13.2)
    c.line(12.0, 13.2, 15.0, 15.2)
    c.line(4.2, 6.2, 6.8, 3.6)
    c.line(19.8, 6.2, 17.2, 3.6)


def _draw_sparkle(c: IconCanvas) -> None:
    # 4-point convex astroid + crisp secondary corner spark
    c.cubic_stroke((12.0, 2.5), (12.4, 8.8), (15.2, 11.6), (21.5, 12.0))
    c.cubic_stroke((21.5, 12.0), (15.2, 12.4), (12.4, 15.2), (12.0, 21.5))
    c.cubic_stroke((12.0, 21.5), (11.6, 15.2), (8.8, 12.4), (2.5, 12.0))
    c.cubic_stroke((2.5, 12.0), (8.8, 11.6), (11.6, 8.8), (12.0, 2.5))
    c.dot(18.5, 5.2, r=1.15)


def _draw_plan(c: IconCanvas) -> None:
    c.rect(4.0, 3.5, 16.0, 17.0, rx=2.2)
    c.circle(8.2, 8.5, 1.8)
    c.line(12.5, 8.5, 17.0, 8.5)
    c.polyline([(8.2, 10.5), (8.2, 15.5), (14.5, 15.5)])
    c.circle(16.0, 15.5, 1.8)


def _draw_workflow(c: IconCanvas) -> None:
    c.circle(5.5, 6.0, 2.4)
    c.circle(5.5, 18.0, 2.4)
    c.circle(18.5, 12.0, 2.4)
    c.polyline([(7.9, 6.0), (12.0, 6.0), (12.0, 18.0), (7.9, 18.0)])
    c.line(12.0, 12.0, 16.1, 12.0)


def _draw_automation(c: IconCanvas) -> None:
    c.arc(12.0, 12.0, 8.8, 35.0, 325.0)
    c.polyline([(18.8, 4.2), (20.8, 7.6), (16.8, 8.2)])
    c.polyline([(13.2, 6.5), (9.2, 12.2), (12.6, 12.2), (10.8, 17.5), (14.8, 11.8), (11.4, 11.8)])


def _draw_trigger(c: IconCanvas) -> None:
    c.polygon([(13.2, 2.5), (4.8, 13.5), (11.6, 13.5), (10.2, 21.5), (19.2, 10.2), (12.4, 10.2)])


def _draw_approval(c: IconCanvas) -> None:
    # Octagonal seal frame + check
    pts = []
    for k in range(8):
        ang = math.radians(22.5 + k * 45.0)
        pts.append((12.0 + 9.0 * math.cos(ang), 12.0 + 9.0 * math.sin(ang)))
    c.polygon(pts)
    c.polyline([(8.2, 12.2), (10.8, 14.8), (16.2, 9.2)])


def _draw_permission(c: IconCanvas) -> None:
    c.rect(3.0, 5.0, 18.0, 14.0, rx=2.2)
    c.circle(9.2, 11.5, 2.6)
    c.line(11.8, 11.5, 17.8, 11.5)
    c.line(16.2, 11.5, 16.2, 14.2)


def _draw_handoff(c: IconCanvas) -> None:
    c.line(4.0, 8.0, 19.5, 8.0)
    c.polyline([(15.5, 4.2), (19.8, 8.0), (15.5, 11.8)])
    c.line(20.0, 16.0, 4.5, 16.0)
    c.polyline([(8.5, 12.2), (4.2, 16.0), (8.5, 19.8)])


def _draw_skill(c: IconCanvas) -> None:
    c.polygon([(12.0, 3.0), (20.2, 7.5), (12.0, 12.0), (3.8, 7.5)])
    c.polyline([(4.0, 12.0), (12.0, 16.5), (20.0, 12.0)])
    c.polyline([(4.0, 16.5), (12.0, 21.0), (20.0, 16.5)])


def _draw_knowledge(c: IconCanvas) -> None:
    c.polygon([(12.0, 6.2), (3.5, 4.2), (3.5, 18.2), (12.0, 20.2)])
    c.polygon([(12.0, 6.2), (20.5, 4.2), (20.5, 18.2), (12.0, 20.2)])


def _draw_context(c: IconCanvas) -> None:
    c.polyline([(3.5, 8.0), (3.5, 3.5), (8.0, 3.5)])
    c.polyline([(16.0, 3.5), (20.5, 3.5), (20.5, 8.0)])
    c.polyline([(20.5, 16.0), (20.5, 20.5), (16.0, 20.5)])
    c.polyline([(8.0, 20.5), (3.5, 20.5), (3.5, 16.0)])
    c.circle(12.0, 12.0, 3.2)


def _draw_source(c: IconCanvas) -> None:
    c.circle(12.0, 12.0, 9.0)
    c.polygon([(16.2, 7.8), (13.8, 13.8), (7.8, 16.2), (10.2, 10.2)])


def _draw_citation(c: IconCanvas) -> None:
    c.polyline([(7.5, 5.0), (4.0, 5.0), (4.0, 19.0), (7.5, 19.0)])
    c.polyline([(16.5, 5.0), (20.0, 5.0), (20.0, 19.0), (16.5, 19.0)])
    c.line(10.5, 9.2, 8.8, 14.8)
    c.line(15.2, 9.2, 13.5, 14.8)


def _draw_prompt(c: IconCanvas) -> None:
    c.rect(3.0, 4.5, 18.0, 15.0, rx=3.5)
    c.polyline([(7.2, 9.2), (10.5, 12.0), (7.2, 14.8)])
    c.line(13.2, 14.8, 16.8, 14.8)


def _draw_model(c: IconCanvas) -> None:
    c.polygon([(12.0, 2.8), (20.0, 7.2), (20.0, 16.8), (12.0, 21.2), (4.0, 16.8), (4.0, 7.2)])
    c.line(4.5, 7.5, 12.0, 12.0)
    c.line(19.5, 7.5, 12.0, 12.0)
    c.line(12.0, 12.0, 12.0, 21.0)


def _draw_background_task(c: IconCanvas) -> None:
    c.arc(12.0, 12.0, 8.6, 30.0, 295.0)
    c.dot(18.5, 5.5, r=1.5)
    c.line(12.0, 8.0, 12.0, 12.4)
    c.line(12.0, 12.4, 15.2, 14.2)


# --- 3. Navigation and layout (32) ---

def _draw_back(c: IconCanvas) -> None:
    c.line(19.5, 12.0, 4.5, 12.0)
    c.polyline([(10.8, 5.8), (4.5, 12.0), (10.8, 18.2)])


def _draw_forward(c: IconCanvas) -> None:
    c.line(4.5, 12.0, 19.5, 12.0)
    c.polyline([(13.2, 5.8), (19.5, 12.0), (13.2, 18.2)])


def _draw_up(c: IconCanvas) -> None:
    c.line(12.0, 19.5, 12.0, 4.5)
    c.polyline([(5.8, 10.8), (12.0, 4.5), (18.2, 10.8)])


def _draw_down(c: IconCanvas) -> None:
    c.line(12.0, 4.5, 12.0, 19.5)
    c.polyline([(5.8, 13.2), (12.0, 19.5), (18.2, 13.2)])


def _draw_chevron_left(c: IconCanvas) -> None:
    c.polyline([(15.0, 5.0), (8.0, 12.0), (15.0, 19.0)])


def _draw_chevron_right(c: IconCanvas) -> None:
    c.polyline([(9.0, 5.0), (16.0, 12.0), (9.0, 19.0)])


def _draw_chevron_up(c: IconCanvas) -> None:
    c.polyline([(5.0, 15.0), (12.0, 8.0), (19.0, 15.0)])


def _draw_chevron_down(c: IconCanvas) -> None:
    c.polyline([(5.0, 9.0), (12.0, 16.0), (19.0, 9.0)])


def _draw_arrow_up_right(c: IconCanvas) -> None:
    c.line(6.0, 18.0, 18.0, 6.0)
    c.polyline([(9.5, 6.0), (18.0, 6.0), (18.0, 14.5)])


def _draw_arrow_down_left(c: IconCanvas) -> None:
    c.line(18.0, 6.0, 6.0, 18.0)
    c.polyline([(6.0, 9.5), (6.0, 18.0), (14.5, 18.0)])


def _draw_arrow_up_left(c: IconCanvas) -> None:
    c.line(18.0, 18.0, 6.0, 6.0)
    c.polyline([(14.5, 6.0), (6.0, 6.0), (6.0, 14.5)])


def _draw_arrow_down_right(c: IconCanvas) -> None:
    c.line(6.0, 6.0, 18.0, 18.0)
    c.polyline([(9.5, 18.0), (18.0, 18.0), (18.0, 9.5)])


def _draw_double_chevron_left(c: IconCanvas) -> None:
    c.polyline([(11.5, 5.8), (5.2, 12.0), (11.5, 18.2)])
    c.polyline([(18.8, 5.8), (12.5, 12.0), (18.8, 18.2)])


def _draw_double_chevron_right(c: IconCanvas) -> None:
    c.polyline([(5.2, 5.8), (11.5, 12.0), (5.2, 18.2)])
    c.polyline([(12.5, 5.8), (18.8, 12.0), (12.5, 18.2)])


def _draw_expand(c: IconCanvas) -> None:
    c.polyline([(14.8, 4.0), (20.0, 4.0), (20.0, 9.2)])
    c.line(13.8, 10.2, 19.8, 4.2)
    c.polyline([(4.0, 14.8), (4.0, 20.0), (9.2, 20.0)])
    c.line(10.2, 13.8, 4.2, 19.8)


def _draw_collapse(c: IconCanvas) -> None:
    c.polyline([(14.0, 4.8), (14.0, 10.0), (19.2, 10.0)])
    c.line(20.0, 4.0, 14.2, 9.8)
    c.polyline([(4.8, 14.0), (10.0, 14.0), (10.0, 19.2)])
    c.line(4.0, 20.0, 9.8, 14.2)


def _draw_fullscreen(c: IconCanvas) -> None:
    c.polyline([(3.5, 8.5), (3.5, 3.5), (8.5, 3.5)])
    c.polyline([(15.5, 3.5), (20.5, 3.5), (20.5, 8.5)])
    c.polyline([(20.5, 15.5), (20.5, 20.5), (15.5, 20.5)])
    c.polyline([(8.5, 20.5), (3.5, 20.5), (3.5, 15.5)])


def _draw_exit_fullscreen(c: IconCanvas) -> None:
    c.polyline([(8.5, 3.5), (8.5, 8.5), (3.5, 8.5)])
    c.polyline([(15.5, 3.5), (15.5, 8.5), (20.5, 8.5)])
    c.polyline([(20.5, 15.5), (15.5, 15.5), (15.5, 20.5)])
    c.polyline([(3.5, 15.5), (8.5, 15.5), (8.5, 20.5)])


def _draw_home(c: IconCanvas) -> None:
    c.polyline([(3.0, 10.8), (12.0, 3.2), (21.0, 10.8)])
    c.polyline([(5.2, 9.2), (5.2, 20.5), (18.8, 20.5), (18.8, 9.2)])
    c.polyline([(9.8, 20.5), (9.8, 14.2), (14.2, 14.2), (14.2, 20.5)])


def _draw_menu(c: IconCanvas) -> None:
    c.line(4.0, 6.0, 20.0, 6.0)
    c.line(4.0, 12.0, 20.0, 12.0)
    c.line(4.0, 18.0, 20.0, 18.0)


def _draw_more_horizontal(c: IconCanvas) -> None:
    for cx in (5.0, 12.0, 19.0):
        c.dot(cx, 12.0, r=1.45)


def _draw_more_vertical(c: IconCanvas) -> None:
    for cy in (5.0, 12.0, 19.0):
        c.dot(12.0, cy, r=1.45)


def _draw_close(c: IconCanvas) -> None:
    c.line(5.5, 5.5, 18.5, 18.5)
    c.line(18.5, 5.5, 5.5, 18.5)


def _draw_sidebar_left(c: IconCanvas) -> None:
    c.rect(3.0, 4.0, 18.0, 16.0, rx=2.2)
    c.line(9.2, 4.0, 9.2, 20.0)


def _draw_sidebar_right(c: IconCanvas) -> None:
    c.rect(3.0, 4.0, 18.0, 16.0, rx=2.2)
    c.line(14.8, 4.0, 14.8, 20.0)


def _draw_grid(c: IconCanvas) -> None:
    c.rect(3.5, 3.5, 6.8, 6.8, rx=1.4)
    c.rect(13.7, 3.5, 6.8, 6.8, rx=1.4)
    c.rect(3.5, 13.7, 6.8, 6.8, rx=1.4)
    c.rect(13.7, 13.7, 6.8, 6.8, rx=1.4)


def _draw_list(c: IconCanvas) -> None:
    for cy in (6.0, 12.0, 18.0):
        c.dot(4.5, cy, r=1.15)
        c.line(8.8, cy, 20.2, cy)


def _draw_dashboard(c: IconCanvas) -> None:
    c.rect(3.5, 3.5, 7.2, 9.5, rx=1.5)
    c.rect(13.8, 3.5, 6.7, 6.0, rx=1.4)
    c.rect(13.8, 13.0, 6.7, 7.5, rx=1.4)
    c.rect(3.5, 16.2, 7.2, 4.3, rx=1.2)


def _draw_tabs(c: IconCanvas) -> None:
    c.rect(3.0, 4.5, 18.0, 15.0, rx=2.2)
    c.polyline([(3.0, 9.8), (11.5, 9.8), (11.5, 4.5)])
    c.line(15.5, 7.2, 18.0, 7.2)


def _draw_window(c: IconCanvas) -> None:
    c.rect(3.0, 4.0, 18.0, 16.0, rx=2.2)
    c.line(3.0, 9.2, 21.0, 9.2)
    c.dot(6.2, 6.6, r=0.95)
    c.dot(9.4, 6.6, r=0.95)


def _draw_new_window(c: IconCanvas) -> None:
    c.polyline([(11.5, 4.5), (5.0, 4.5), (4.0, 5.5), (4.0, 19.0), (5.0, 20.0), (18.5, 20.0), (19.5, 19.0), (19.5, 12.5)])
    c.line(12.0, 12.0, 20.2, 3.8)
    c.polyline([(15.0, 3.8), (20.2, 3.8), (20.2, 9.0)])


def _draw_split_view(c: IconCanvas) -> None:
    c.rect(3.0, 4.0, 18.0, 16.0, rx=2.2)
    c.line(12.0, 4.0, 12.0, 20.0)


# --- 4. Status and feedback (19) ---

def _draw_check(c: IconCanvas) -> None:
    c.polyline([(4.5, 12.5), (9.8, 17.8), (19.8, 6.2)])


def _draw_check_circle(c: IconCanvas) -> None:
    c.circle(12.0, 12.0, 9.0)
    c.polyline([(8.0, 12.4), (10.8, 15.2), (16.5, 9.0)])


def _draw_info(c: IconCanvas) -> None:
    c.circle(12.0, 12.0, 9.0)
    c.dot(12.0, 7.6, r=1.15)
    c.line(12.0, 11.4, 12.0, 16.8)


def _draw_warning(c: IconCanvas) -> None:
    c.polygon([(12.0, 3.2), (21.4, 19.8), (2.6, 19.8)])
    c.line(12.0, 9.2, 12.0, 13.6)
    c.dot(12.0, 16.8, r=1.1)


def _draw_error(c: IconCanvas) -> None:
    c.circle(12.0, 12.0, 9.0)
    c.line(9.0, 9.0, 15.0, 15.0)
    c.line(15.0, 9.0, 9.0, 15.0)


def _draw_help(c: IconCanvas) -> None:
    c.circle(12.0, 12.0, 9.0)
    c.arc(12.0, 9.2, 2.6, 195.0, 388.0)
    c.line(12.0, 12.0, 12.0, 13.8)
    c.dot(12.0, 17.0, r=1.1)


def _draw_loading(c: IconCanvas) -> None:
    c.arc(12.0, 12.0, 8.5, -80.0, 195.0)


def _draw_progress(c: IconCanvas) -> None:
    c.rect(2.5, 8.2, 19.0, 7.6, rx=3.8)
    c.fill_round_rect(5.2, 10.6, 8.5, 2.8, rx=1.4)


def _draw_offline(c: IconCanvas) -> None:
    c.arc(12.0, 18.0, 11.5, 224.0, 316.0)
    c.arc(12.0, 18.0, 6.8, 224.0, 316.0)
    c.dot(12.0, 18.0, r=1.3)
    c.slash_off(3.0, 3.0, 21.0, 21.0)


def _draw_online(c: IconCanvas) -> None:
    c.arc(12.0, 18.2, 11.8, 224.0, 316.0)
    c.arc(12.0, 18.2, 7.0, 224.0, 316.0)
    c.dot(12.0, 18.2, r=1.4)


def _draw_sync(c: IconCanvas) -> None:
    c.arc(12.0, 12.0, 7.8, 15.0, 148.0)
    c.polyline([(16.0, 4.2), (19.6, 7.0), (15.8, 9.8)])
    c.arc(12.0, 12.0, 7.8, 195.0, 328.0)
    c.polyline([(8.0, 19.8), (4.4, 17.0), (8.2, 14.2)])


def _draw_verified(c: IconCanvas) -> None:
    # 12-point smooth scalloped seal outline + check
    pts = []
    for k in range(12):
        ang = math.radians(k * 30.0)
        rad = 9.4 if k % 2 == 0 else 7.6
        pts.append((12.0 + rad * math.cos(ang), 12.0 + rad * math.sin(ang)))
    c.polygon(pts)
    c.polyline([(8.8, 12.2), (11.2, 14.6), (15.6, 9.6)])


def _draw_new(c: IconCanvas) -> None:
    c.rect(2.8, 6.2, 18.4, 11.6, rx=3.0)
    c.polyline([(6.8, 14.5), (6.8, 9.5), (10.5, 14.5), (10.5, 9.5)])
    c.line(15.5, 9.8, 15.5, 14.2)
    c.line(13.3, 12.0, 17.7, 12.0)


def _draw_beta(c: IconCanvas) -> None:
    c.line(8.8, 3.5, 15.2, 3.5)
    c.polyline([(10.0, 3.5), (10.0, 9.0), (4.2, 19.2), (5.5, 20.5), (18.5, 20.5), (19.8, 19.2), (14.0, 9.0), (14.0, 3.5)])
    c.line(7.0, 15.2, 17.0, 15.2)


def _draw_badge(c: IconCanvas) -> None:
    c.circle(12.0, 9.2, 6.0)
    c.polyline([(8.5, 14.2), (7.5, 21.2), (12.0, 18.8), (16.5, 21.2), (15.5, 14.2)])


def _draw_notification_dot(c: IconCanvas) -> None:
    c.polyline([(12.5, 4.5), (4.5, 4.5), (3.8, 5.2), (3.8, 19.2), (4.5, 20.0), (18.5, 20.0), (19.2, 19.2), (19.2, 11.5)])
    c.fill_circle(18.0, 6.0, 2.8)


def _draw_pending(c: IconCanvas) -> None:
    c.line(5.8, 3.5, 18.2, 3.5)
    c.line(5.8, 20.5, 18.2, 20.5)
    c.polyline([(7.0, 3.5), (7.0, 7.8), (17.0, 16.2), (17.0, 20.5)])
    c.polyline([(17.0, 3.5), (17.0, 7.8), (7.0, 16.2), (7.0, 20.5)])


def _draw_timeout(c: IconCanvas) -> None:
    c.arc(11.6, 12.0, 8.2, 38.0, 322.0)
    c.line(11.6, 7.6, 11.6, 12.2)
    c.line(11.6, 12.2, 14.6, 14.2)
    c.line(19.6, 14.6, 19.6, 18.0)
    c.dot(19.6, 20.8, r=1.05)


def _draw_bell(c: IconCanvas) -> None:
    c.polyline([(6.2, 11.5), (6.2, 15.5), (4.0, 17.5), (20.0, 17.5), (17.8, 15.5), (17.8, 11.5)])
    c.arc(12.0, 10.5, 5.8, 180.0, 360.0)
    c.arc(12.0, 18.8, 2.2, 0.0, 180.0)


SYMBOLS_PHASE1_A: List[SymbolSpec] = [
    # 1. Chat (24)
    SymbolSpec("send", "Chat", ("message", "submit", "paper-plane", "prompt"), _draw_send, rtl_mirror=True),
    SymbolSpec("stop", "Chat", ("halt", "abort", "generation", "square"), _draw_stop),
    SymbolSpec("mic", "Chat", ("microphone", "voice", "record", "audio"), _draw_mic),
    SymbolSpec("mic-off", "Chat", ("mute", "microphone", "silent"), _draw_mic_off),
    SymbolSpec("attach", "Chat", ("paperclip", "file", "upload"), _draw_attach),
    SymbolSpec("image", "Chat", ("photo", "picture", "gallery"), _draw_image),
    SymbolSpec("camera", "Chat", ("capture", "snapshot", "photo"), _draw_camera),
    SymbolSpec("copy", "Chat", ("duplicate", "clipboard", "clone"), _draw_copy),
    SymbolSpec("paste", "Chat", ("clipboard", "insert"), _draw_paste),
    SymbolSpec("cut", "Chat", ("scissors", "trim", "remove"), _draw_cut),
    SymbolSpec("retry", "Chat", ("reload", "repeat", "again"), _draw_retry),
    SymbolSpec("regenerate", "Chat", ("refresh", "rerun", "ai"), _draw_regenerate),
    SymbolSpec("edit", "Chat", ("pencil", "modify", "compose"), _draw_edit),
    SymbolSpec("delete", "Chat", ("backspace", "erase", "remove"), _draw_delete),
    SymbolSpec("reply", "Chat", ("respond", "answer", "message"), _draw_reply, rtl_mirror=True),
    SymbolSpec("forward-message", "Chat", ("relay", "redirect", "message"), _draw_forward_message, rtl_mirror=True),
    SymbolSpec("quote", "Chat", ("citation", "excerpt", "reply"), _draw_quote),
    SymbolSpec("pin", "Chat", ("stick", "anchor", "keep"), _draw_pin),
    SymbolSpec("unpin", "Chat", ("detach", "unstick"), _draw_unpin),
    SymbolSpec("mention", "Chat", ("at", "handle", "ping"), _draw_mention),
    SymbolSpec("emoji", "Chat", ("smile", "reaction", "face"), _draw_emoji),
    SymbolSpec("thumbs-up", "Chat", ("like", "approve", "good"), _draw_thumbs_up),
    SymbolSpec("thumbs-down", "Chat", ("dislike", "reject", "bad"), _draw_thumbs_down),
    SymbolSpec("voice-message", "Chat", ("waveform", "speech", "audio"), _draw_voice_message),

    # 2. Agent and AI (24)
    SymbolSpec("agent", "Agent and AI", ("assistant", "bot", "companion", "ai"), _draw_agent),
    SymbolSpec("user", "Agent and AI", ("person", "human", "profile"), _draw_user),
    SymbolSpec("team", "Agent and AI", ("group", "members", "collaboration"), _draw_team),
    SymbolSpec("tool", "Agent and AI", ("wrench", "function", "utility"), _draw_tool),
    SymbolSpec("plug", "Agent and AI", ("mcp", "connector", "integration", "plugin"), _draw_plug),
    SymbolSpec("memory", "Agent and AI", ("chip", "recall", "store"), _draw_memory),
    SymbolSpec("task-list", "Agent and AI", ("todo", "checklist", "tasks"), _draw_task_list, rtl_mirror=True),
    SymbolSpec("reminder", "Agent and AI", ("alarm", "clock", "schedule"), _draw_reminder),
    SymbolSpec("sparkle", "Agent and AI", ("ai", "magic", "smart", "enhance"), _draw_sparkle),
    SymbolSpec("plan", "Agent and AI", ("roadmap", "steps", "strategy"), _draw_plan),
    SymbolSpec("workflow", "Agent and AI", ("dag", "pipeline", "nodes"), _draw_workflow),
    SymbolSpec("automation", "Agent and AI", ("loop", "run", "automatic"), _draw_automation),
    SymbolSpec("trigger", "Agent and AI", ("lightning", "event", "fire"), _draw_trigger),
    SymbolSpec("approval", "Agent and AI", ("confirm", "accept", "gate"), _draw_approval),
    SymbolSpec("permission", "Agent and AI", ("access", "keycard", "grant"), _draw_permission),
    SymbolSpec("handoff", "Agent and AI", ("transfer", "delegate", "swap"), _draw_handoff, rtl_mirror=True),
    SymbolSpec("skill", "Agent and AI", ("layers", "capability", "module"), _draw_skill),
    SymbolSpec("knowledge", "Agent and AI", ("book", "docs", "library"), _draw_knowledge),
    SymbolSpec("context", "Agent and AI", ("window", "focus", "scope"), _draw_context),
    SymbolSpec("source", "Agent and AI", ("compass", "origin", "reference"), _draw_source),
    SymbolSpec("citation", "Agent and AI", ("brackets", "footnote", "quote"), _draw_citation),
    SymbolSpec("prompt", "Agent and AI", ("instruction", "bubble", "input"), _draw_prompt),
    SymbolSpec("model", "Agent and AI", ("cube", "llm", "engine"), _draw_model),
    SymbolSpec("background-task", "Agent and AI", ("daemon", "async", "worker"), _draw_background_task),

    # 3. Navigation and layout (32)
    SymbolSpec("back", "Navigation and layout", ("arrow-left", "previous", "return"), _draw_back, rtl_mirror=True),
    SymbolSpec("forward", "Navigation and layout", ("arrow-right", "next"), _draw_forward, rtl_mirror=True),
    SymbolSpec("up", "Navigation and layout", ("arrow-up", "top"), _draw_up),
    SymbolSpec("down", "Navigation and layout", ("arrow-down", "bottom"), _draw_down),
    SymbolSpec("chevron-left", "Navigation and layout", ("angle-left", "previous"), _draw_chevron_left, rtl_mirror=True),
    SymbolSpec("chevron-right", "Navigation and layout", ("angle-right", "next"), _draw_chevron_right, rtl_mirror=True),
    SymbolSpec("chevron-up", "Navigation and layout", ("angle-up", "collapse"), _draw_chevron_up),
    SymbolSpec("chevron-down", "Navigation and layout", ("angle-down", "expand"), _draw_chevron_down),
    SymbolSpec("arrow-up-right", "Navigation and layout", ("external", "open"), _draw_arrow_up_right, rtl_mirror=True),
    SymbolSpec("arrow-down-left", "Navigation and layout", ("return", "diagonal"), _draw_arrow_down_left, rtl_mirror=True),
    SymbolSpec("arrow-up-left", "Navigation and layout", ("insert", "diagonal"), _draw_arrow_up_left, rtl_mirror=True),
    SymbolSpec("arrow-down-right", "Navigation and layout", ("expand", "diagonal"), _draw_arrow_down_right, rtl_mirror=True),
    SymbolSpec("double-chevron-left", "Navigation and layout", ("rewind", "first"), _draw_double_chevron_left, rtl_mirror=True),
    SymbolSpec("double-chevron-right", "Navigation and layout", ("fast-forward", "last"), _draw_double_chevron_right, rtl_mirror=True),
    SymbolSpec("expand", "Navigation and layout", ("enlarge", "maximize"), _draw_expand),
    SymbolSpec("collapse", "Navigation and layout", ("shrink", "minimize"), _draw_collapse),
    SymbolSpec("fullscreen", "Navigation and layout", ("maximize", "viewport"), _draw_fullscreen),
    SymbolSpec("exit-fullscreen", "Navigation and layout", ("unmaximize", "viewport"), _draw_exit_fullscreen),
    SymbolSpec("home", "Navigation and layout", ("house", "start", "root"), _draw_home),
    SymbolSpec("menu", "Navigation and layout", ("hamburger", "navigation", "bars"), _draw_menu),
    SymbolSpec("more-horizontal", "Navigation and layout", ("dots", "overflow", "ellipsis"), _draw_more_horizontal),
    SymbolSpec("more-vertical", "Navigation and layout", ("kebab", "overflow", "options"), _draw_more_vertical),
    SymbolSpec("close", "Navigation and layout", ("dismiss", "x", "cancel"), _draw_close),
    SymbolSpec("sidebar-left", "Navigation and layout", ("panel", "drawer", "layout"), _draw_sidebar_left, rtl_mirror=True),
    SymbolSpec("sidebar-right", "Navigation and layout", ("inspector", "panel", "layout"), _draw_sidebar_right, rtl_mirror=True),
    SymbolSpec("grid", "Navigation and layout", ("tiles", "cards", "gallery"), _draw_grid),
    SymbolSpec("list", "Navigation and layout", ("rows", "items", "index"), _draw_list, rtl_mirror=True),
    SymbolSpec("dashboard", "Navigation and layout", ("bento", "overview", "metrics"), _draw_dashboard),
    SymbolSpec("tabs", "Navigation and layout", ("browser", "sheets", "pages"), _draw_tabs),
    SymbolSpec("window", "Navigation and layout", ("app", "frame", "dialog"), _draw_window),
    SymbolSpec("new-window", "Navigation and layout", ("popup", "launch", "detach"), _draw_new_window, rtl_mirror=True),
    SymbolSpec("split-view", "Navigation and layout", ("columns", "compare", "panes"), _draw_split_view),

    # 4. Status and feedback (19)
    SymbolSpec("check", "Status and feedback", ("done", "ok", "tick"), _draw_check),
    SymbolSpec("check-circle", "Status and feedback", ("success", "complete"), _draw_check_circle),
    SymbolSpec("info", "Status and feedback", ("information", "details"), _draw_info),
    SymbolSpec("warning", "Status and feedback", ("caution", "alert", "triangle"), _draw_warning),
    SymbolSpec("error", "Status and feedback", ("fail", "danger", "cross"), _draw_error),
    SymbolSpec("help", "Status and feedback", ("question", "support"), _draw_help),
    SymbolSpec("loading", "Status and feedback", ("spinner", "busy", "wait"), _draw_loading),
    SymbolSpec("progress", "Status and feedback", ("bar", "percent", "meter"), _draw_progress),
    SymbolSpec("offline", "Status and feedback", ("disconnected", "wifi-off"), _draw_offline),
    SymbolSpec("online", "Status and feedback", ("connected", "wifi", "live"), _draw_online),
    SymbolSpec("sync", "Status and feedback", ("refresh", "update"), _draw_sync),
    SymbolSpec("verified", "Status and feedback", ("trusted", "seal", "authentic"), _draw_verified),
    SymbolSpec("new", "Status and feedback", ("fresh", "badge", "release"), _draw_new),
    SymbolSpec("beta", "Status and feedback", ("lab", "experimental", "flask"), _draw_beta),
    SymbolSpec("badge", "Status and feedback", ("award", "ribbon", "medal"), _draw_badge),
    SymbolSpec("notification-dot", "Status and feedback", ("unread", "indicator"), _draw_notification_dot),
    SymbolSpec("pending", "Status and feedback", ("hourglass", "waiting", "queued"), _draw_pending),
    SymbolSpec("timeout", "Status and feedback", ("expired", "clock-alert"), _draw_timeout),
    SymbolSpec("bell", "Status and feedback", ("notification", "alert", "chime"), _draw_bell),
]
