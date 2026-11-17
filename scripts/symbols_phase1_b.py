"""
Admiralty Symbols Phase 1 — Part B (119 icons):
  5. Files and content (36)
  6. Search and filter (12)
  7. Settings and preferences (16)
  8. Security and privacy (16)
  9. Cloud and sync (10)
 10. Account and help (16)
 11. Code and developer (5)
 12. Filled active variants (8)
"""

from __future__ import annotations
import math
from typing import List

from symbols_engine import IconCanvas, SymbolSpec


def _file_outline(c: IconCanvas, dx: float = 0.0, dy: float = 0.0) -> None:
    c.polygon([
        (5.0 + dx, 3.0 + dy),
        (13.8 + dx, 3.0 + dy),
        (19.0 + dx, 8.2 + dy),
        (19.0 + dx, 21.0 + dy),
        (5.0 + dx, 21.0 + dy),
    ])
    c.polyline([(13.8 + dx, 3.0 + dy), (13.8 + dx, 8.2 + dy), (19.0 + dx, 8.2 + dy)])


def _shield_outline(c: IconCanvas) -> None:
    c.polyline([
        (12.0, 2.8),
        (20.0, 6.2),
        (20.0, 11.5),
    ])
    c.cubic_stroke((20.0, 11.5), (20.0, 16.5), (16.5, 19.6), (12.0, 21.4))
    c.cubic_stroke((12.0, 21.4), (7.5, 19.6), (4.0, 16.5), (4.0, 11.5))
    c.polyline([
        (4.0, 11.5),
        (4.0, 6.2),
        (12.0, 2.8),
    ])


def _cloud_outline(c: IconCanvas, bottom_open: bool = False) -> None:
    # Seamless 3-lobe cloud silhouette (note: SVG/screen angles increase CW, so a1 > a0)
    c.arc(7.6, 14.2, 4.0, 90.0, 260.0)
    c.arc(12.0, 10.4, 5.0, 185.0, 355.0)
    c.arc(16.8, 14.4, 3.8, 275.0, 450.0)
    if not bottom_open:
        c.line(7.6, 18.2, 16.8, 18.2)
    else:
        c.line(7.4, 18.2, 8.6, 18.2)
        c.line(15.4, 18.2, 16.8, 18.2)


# --- 5. Files and content (36) ---

def _draw_file(c: IconCanvas) -> None:
    _file_outline(c)


def _draw_new_file(c: IconCanvas) -> None:
    _file_outline(c)
    c.cut_circle(17.5, 17.2, 4.8)
    c.line(17.5, 14.0, 17.5, 20.4)
    c.line(14.3, 17.2, 20.7, 17.2)


def _draw_folder(c: IconCanvas) -> None:
    c.polygon([(3.0, 5.2), (9.5, 5.2), (11.8, 8.0), (21.0, 8.0), (21.0, 19.5), (3.0, 19.5)])


def _draw_new_folder(c: IconCanvas) -> None:
    _draw_folder(c)
    c.line(12.0, 11.2, 12.0, 16.4)
    c.line(9.4, 13.8, 14.6, 13.8)


def _draw_document(c: IconCanvas) -> None:
    _file_outline(c)
    c.line(8.5, 12.8, 15.5, 12.8)
    c.line(8.5, 16.8, 13.8, 16.8)


def _draw_spreadsheet(c: IconCanvas) -> None:
    c.rect(3.5, 4.0, 17.0, 16.0, rx=2.2)
    c.line(3.5, 9.6, 20.5, 9.6)
    c.line(3.5, 14.8, 20.5, 14.8)
    c.line(10.2, 4.0, 10.2, 20.0)


def _draw_presentation(c: IconCanvas) -> None:
    c.rect(3.0, 3.8, 18.0, 12.4, rx=1.8)
    c.line(12.0, 16.2, 12.0, 20.5)
    c.line(7.2, 20.5, 12.0, 16.4)
    c.line(16.8, 20.5, 12.0, 16.4)
    c.polyline([(7.5, 12.2), (10.5, 9.2), (13.2, 11.2), (16.5, 7.6)])


def _draw_pdf(c: IconCanvas) -> None:
    _file_outline(c)
    c.rect(7.6, 12.0, 8.8, 5.4, rx=2.7)


def _draw_image_file(c: IconCanvas) -> None:
    _file_outline(c)
    c.dot(9.4, 11.4, r=1.15)
    c.polyline([(5.8, 19.2), (10.6, 14.5), (14.0, 17.5), (18.4, 13.6)])


def _draw_audio_file(c: IconCanvas) -> None:
    _file_outline(c)
    c.line(8.5, 12.2, 8.5, 17.4)
    c.line(12.0, 10.2, 12.0, 18.2)
    c.line(15.5, 13.2, 15.5, 16.8)


def _draw_video_file(c: IconCanvas) -> None:
    _file_outline(c)
    c.polygon([(9.6, 11.2), (15.8, 14.8), (9.6, 18.4)])


def _draw_code_file(c: IconCanvas) -> None:
    _file_outline(c)
    c.polyline([(10.0, 12.2), (7.6, 14.8), (10.0, 17.4)])
    c.polyline([(14.0, 12.2), (16.4, 14.8), (14.0, 17.4)])


def _draw_archive(c: IconCanvas) -> None:
    c.rect(2.8, 4.0, 18.4, 4.8, rx=1.4)
    c.polyline([(4.2, 8.8), (4.2, 20.0), (19.8, 20.0), (19.8, 8.8)])
    c.line(9.5, 13.5, 14.5, 13.5)


def _draw_link(c: IconCanvas) -> None:
    c.polyline([(10.0, 14.0), (7.2, 16.8)])
    c.arc(6.8, 17.2, 3.8, 45.0, 225.0)
    c.line(13.8, 10.2, 10.2, 13.8)
    c.arc(17.2, 6.8, 3.8, 225.0, 405.0)
    c.polyline([(14.0, 10.0), (16.8, 7.2)])


def _draw_unlink(c: IconCanvas) -> None:
    c.arc(6.6, 17.4, 3.6, 45.0, 225.0)
    c.arc(17.4, 6.6, 3.6, 225.0, 405.0)
    c.line(8.2, 4.2, 8.2, 7.5)
    c.line(4.2, 8.2, 7.5, 8.2)
    c.line(15.8, 16.5, 15.8, 19.8)
    c.line(16.5, 15.8, 19.8, 15.8)


def _draw_share(c: IconCanvas) -> None:
    c.circle(17.8, 5.5, 2.6)
    c.circle(6.2, 12.0, 2.6)
    c.circle(17.8, 18.5, 2.6)
    c.line(8.6, 10.6, 15.4, 6.8)
    c.line(8.6, 13.4, 15.4, 17.2)


def _draw_export(c: IconCanvas) -> None:
    # Bracket tray + rightward exit vector
    c.polyline([(11.5, 4.5), (4.5, 4.5), (4.5, 19.5), (11.5, 19.5)])
    c.line(10.0, 12.0, 20.2, 12.0)
    c.polyline([(15.8, 7.6), (20.2, 12.0), (15.8, 16.4)])


def _draw_import(c: IconCanvas) -> None:
    # Bracket tray + rightward incoming vector
    c.polyline([(12.5, 4.5), (19.5, 4.5), (19.5, 19.5), (12.5, 19.5)])
    c.line(3.8, 12.0, 14.0, 12.0)
    c.polyline([(9.6, 7.6), (14.0, 12.0), (9.6, 16.4)])


def _draw_download(c: IconCanvas) -> None:
    c.line(12.0, 3.8, 12.0, 15.2)
    c.polyline([(7.5, 10.8), (12.0, 15.2), (16.5, 10.8)])
    c.polyline([(4.0, 15.5), (4.0, 20.0), (20.0, 20.0), (20.0, 15.5)])


def _draw_upload(c: IconCanvas) -> None:
    c.line(12.0, 15.2, 12.0, 3.8)
    c.polyline([(7.5, 8.2), (12.0, 3.8), (16.5, 8.2)])
    c.polyline([(4.0, 15.5), (4.0, 20.0), (20.0, 20.0), (20.0, 15.5)])


def _draw_bookmark(c: IconCanvas) -> None:
    c.polygon([(5.5, 3.2), (18.5, 3.2), (18.5, 20.8), (12.0, 16.2), (5.5, 20.8)])


def _draw_tag(c: IconCanvas) -> None:
    c.polygon([(3.5, 3.5), (11.8, 3.5), (20.6, 12.3), (12.3, 20.6), (3.5, 11.8)])
    c.dot(8.2, 8.2, r=1.25)


def _draw_star(c: IconCanvas) -> None:
    pts = []
    for k in range(10):
        ang = math.radians(-90.0 + k * 36.0)
        rad = 9.5 if k % 2 == 0 else 4.3
        pts.append((12.0 + rad * math.cos(ang), 12.6 + rad * math.sin(ang)))
    c.polygon(pts)


def _draw_note(c: IconCanvas) -> None:
    # Bottom-right curled sticky note
    c.polygon([(4.0, 3.5), (20.0, 3.5), (20.0, 14.8), (14.8, 20.0), (4.0, 20.0)])
    c.polyline([(14.8, 20.0), (14.8, 14.8), (20.0, 14.8)])
    c.line(8.0, 9.5, 16.0, 9.5)


def _draw_clipboard(c: IconCanvas) -> None:
    c.rect(5.0, 5.2, 14.0, 15.8, rx=2.0)
    c.rect(8.5, 2.5, 7.0, 3.8, rx=1.1)


def _draw_trash(c: IconCanvas) -> None:
    c.line(3.5, 6.0, 20.5, 6.0)
    c.polyline([(9.0, 6.0), (9.0, 3.4), (15.0, 3.4), (15.0, 6.0)])
    c.polyline([(5.6, 6.0), (6.8, 20.4), (17.2, 20.4), (18.4, 6.0)])
    c.line(10.0, 10.2, 10.3, 16.5)
    c.line(14.0, 10.2, 13.7, 16.5)


def _draw_restore(c: IconCanvas) -> None:
    c.arc(12.0, 12.0, 8.4, 15.0, 305.0)
    c.polyline([(3.2, 8.2), (4.2, 12.5), (8.2, 10.5)])
    c.line(12.0, 16.2, 12.0, 8.2)
    c.polyline([(9.0, 11.2), (12.0, 8.2), (15.0, 11.2)])


def _draw_history(c: IconCanvas) -> None:
    c.arc(12.0, 12.0, 8.4, -150.0, 150.0)
    c.polyline([(3.2, 6.5), (4.0, 10.6), (8.0, 9.2)])
    c.line(12.0, 7.5, 12.0, 12.2)
    c.line(12.0, 12.2, 15.4, 14.2)


def _draw_version(c: IconCanvas) -> None:
    c.circle(6.2, 6.5, 2.2)
    c.circle(6.2, 17.5, 2.2)
    c.line(6.2, 8.8, 6.2, 15.2)
    c.circle(17.8, 12.0, 2.2)
    c.polyline([(8.5, 6.5), (12.8, 6.5), (15.5, 10.5)])


def _draw_compare(c: IconCanvas) -> None:
    c.rect(2.8, 5.2, 6.0, 13.6, rx=1.4)
    c.rect(15.2, 5.2, 6.0, 13.6, rx=1.4)
    c.line(12.0, 3.0, 12.0, 21.0)


def _draw_template(c: IconCanvas) -> None:
    c.rect(3.5, 4.0, 17.0, 16.0, rx=2.2)
    c.line(3.5, 9.4, 20.5, 9.4)
    c.line(9.6, 9.4, 9.6, 20.0)


def _draw_print(c: IconCanvas) -> None:
    c.polyline([(6.8, 8.5), (6.8, 3.5), (17.2, 3.5), (17.2, 8.5)])
    c.rect(3.0, 8.5, 18.0, 8.2, rx=2.0)
    c.cut_round_rect(6.0, 13.2, 12.0, 8.0, rx=1.0)
    c.rect(6.8, 13.8, 10.4, 6.7, rx=0.8)


def _draw_save(c: IconCanvas) -> None:
    c.polygon([(4.0, 3.5), (16.5, 3.5), (20.5, 7.5), (20.5, 20.5), (4.0, 20.5)])
    c.polyline([(8.0, 3.5), (8.0, 8.5), (15.0, 8.5), (15.0, 3.5)])
    c.rect(7.2, 13.5, 9.6, 7.0, rx=0.8)


def _draw_duplicate(c: IconCanvas) -> None:
    c.rect(8.5, 8.5, 12.0, 12.0, rx=2.0)
    c.polyline([(15.5, 5.5), (15.5, 4.0), (4.0, 4.0), (4.0, 15.5), (5.5, 15.5)])
    c.line(14.5, 12.0, 14.5, 17.0)
    c.line(12.0, 14.5, 17.0, 14.5)


def _draw_rename(c: IconCanvas) -> None:
    c.rect(2.8, 7.2, 18.4, 9.6, rx=2.0)
    c.line(6.2, 12.0, 11.2, 12.0)
    c.cut_line(15.2, 3.8, 15.2, 20.2, gap=c.sw + 1.8)
    c.line(15.2, 4.0, 15.2, 20.0)
    c.line(13.0, 4.0, 17.4, 4.0)
    c.line(13.0, 20.0, 17.4, 20.0)


def _draw_label(c: IconCanvas) -> None:
    c.polygon([(3.2, 6.0), (14.5, 6.0), (20.8, 12.0), (14.5, 18.0), (3.2, 18.0)])
    c.dot(8.0, 12.0, r=1.25)


# --- 6. Search and filter (12) ---

def _draw_search(c: IconCanvas) -> None:
    c.circle(10.4, 10.4, 6.6)
    c.line(15.4, 15.4, 20.6, 20.6)


def _draw_zoom_in(c: IconCanvas) -> None:
    c.circle(10.4, 10.4, 6.6)
    c.line(15.4, 15.4, 20.6, 20.6)
    c.line(10.4, 7.6, 10.4, 13.2)
    c.line(7.6, 10.4, 13.2, 10.4)


def _draw_zoom_out(c: IconCanvas) -> None:
    c.circle(10.4, 10.4, 6.6)
    c.line(15.4, 15.4, 20.6, 20.6)
    c.line(7.6, 10.4, 13.2, 10.4)


def _draw_filter(c: IconCanvas) -> None:
    c.polygon([(3.2, 4.5), (20.8, 4.5), (14.0, 12.8), (14.0, 19.2), (10.0, 20.8), (10.0, 12.8)])


def _draw_sort(c: IconCanvas) -> None:
    c.line(7.8, 19.2, 7.8, 4.8)
    c.polyline([(4.2, 8.4), (7.8, 4.8), (11.4, 8.4)])
    c.line(16.2, 4.8, 16.2, 19.2)
    c.polyline([(12.6, 15.6), (16.2, 19.2), (19.8, 15.6)])


def _draw_sort_ascending(c: IconCanvas) -> None:
    c.line(6.2, 19.2, 6.2, 4.8)
    c.polyline([(3.2, 7.8), (6.2, 4.8), (9.2, 7.8)])
    c.line(12.2, 6.2, 15.5, 6.2)
    c.line(12.2, 12.0, 18.2, 12.0)
    c.line(12.2, 17.8, 21.0, 17.8)


def _draw_sort_descending(c: IconCanvas) -> None:
    c.line(6.2, 4.8, 6.2, 19.2)
    c.polyline([(3.2, 16.2), (6.2, 19.2), (9.2, 16.2)])
    c.line(12.2, 6.2, 21.0, 6.2)
    c.line(12.2, 12.0, 18.2, 12.0)
    c.line(12.2, 17.8, 15.5, 17.8)


def _draw_find_in_page(c: IconCanvas) -> None:
    _file_outline(c)
    c.cut_circle(16.2, 16.2, 4.8)
    c.circle(15.5, 15.5, 3.6)
    c.line(18.2, 18.2, 21.2, 21.2)


def _draw_recent(c: IconCanvas) -> None:
    c.circle(12.0, 12.0, 8.8)
    c.line(12.0, 7.2, 12.0, 12.2)
    c.line(12.0, 12.2, 15.6, 14.5)


def _draw_saved_search(c: IconCanvas) -> None:
    c.circle(9.8, 11.2, 6.0)
    c.line(14.2, 15.6, 19.2, 20.6)
    c.line(18.5, 3.5, 18.5, 8.2)
    c.line(16.2, 5.8, 20.8, 5.8)


def _draw_advanced_search(c: IconCanvas) -> None:
    c.circle(9.8, 10.0, 5.8)
    c.line(14.0, 14.2, 17.6, 17.8)
    c.line(13.5, 20.2, 21.0, 20.2)
    c.dot(18.0, 20.2, r=1.15)


def _draw_clear(c: IconCanvas) -> None:
    # Slanted eraser + swept baseline
    c.polygon([(14.2, 3.6), (20.4, 9.8), (11.2, 19.0), (5.2, 19.0), (3.4, 14.4)])
    c.line(10.0, 7.8, 16.2, 14.0)
    c.line(11.2, 19.0, 21.0, 19.0)


# --- 7. Settings and preferences (16) ---

def _draw_settings(c: IconCanvas) -> None:
    # Crisp 8-tooth precision gear (stays open at 14px in Bold)
    c.circle(12.0, 12.0, 3.2)
    pts = []
    for k in range(16):
        ang = math.radians(k * 22.5 - 11.25)
        is_tooth = (k % 4) in (1, 2)
        rad = 9.5 if is_tooth else 6.6
        pts.append((12.0 + rad * math.cos(ang), 12.0 + rad * math.sin(ang)))
    c.polygon(pts)


def _draw_sliders(c: IconCanvas) -> None:
    for y, kx in ((5.8, 8.2), (12.0, 15.8), (18.2, 10.2)):
        c.line(3.5, y, 20.5, y)
        c.cut_circle(kx, y, 2.6)
        c.circle(kx, y, 2.0)


def _draw_toggle_on(c: IconCanvas) -> None:
    c.rect(2.5, 6.2, 19.0, 11.6, rx=5.8)
    c.fill_circle(15.8, 12.0, 3.2)


def _draw_toggle_off(c: IconCanvas) -> None:
    c.rect(2.5, 6.2, 19.0, 11.6, rx=5.8)
    c.circle(8.2, 12.0, 2.9)


def _draw_theme(c: IconCanvas) -> None:
    c.circle(12.0, 12.0, 8.8)
    c.line(12.0, 3.5, 12.0, 20.5)
    # Right dark crescent fill wedge
    pts = [(12.0, 5.2)]
    for step in range(9):
        ang = math.radians(-90.0 + step * 22.5)
        pts.append((12.0 + 6.8 * math.cos(ang), 12.0 + 6.8 * math.sin(ang)))
    pts.append((12.0, 18.8))
    c.fill_polygon(pts)


def _draw_dark_mode(c: IconCanvas) -> None:
    c.arc(12.0, 12.0, 8.8, 25.0, 260.0)
    c.arc(16.8, 8.2, 6.2, 85.0, 225.0)


def _draw_light_mode(c: IconCanvas) -> None:
    c.circle(12.0, 12.0, 4.2)
    for k in range(8):
        ang = math.radians(k * 45.0)
        c.line(12.0 + 7.2 * math.cos(ang), 12.0 + 7.2 * math.sin(ang), 12.0 + 9.6 * math.cos(ang), 12.0 + 9.6 * math.sin(ang))


def _draw_auto_mode(c: IconCanvas) -> None:
    c.arc(12.0, 12.0, 9.0, -50.0, 270.0)
    c.polyline([(8.8, 16.0), (12.0, 7.8), (15.2, 16.0)])
    c.line(9.8, 13.6, 14.2, 13.6)


def _draw_font_size(c: IconCanvas) -> None:
    c.line(3.5, 5.2, 13.5, 5.2)
    c.line(8.5, 5.2, 8.5, 19.2)
    c.line(14.5, 10.8, 20.8, 10.8)
    c.line(17.65, 10.8, 17.65, 19.2)


def _draw_language(c: IconCanvas) -> None:
    c.circle(12.0, 12.0, 8.8)
    c.ellipse(12.0, 12.0, 3.8, 8.8)
    c.line(3.2, 12.0, 20.8, 12.0)


def _draw_accessibility(c: IconCanvas) -> None:
    c.circle(12.0, 12.0, 9.2)
    c.dot(12.0, 6.8, r=1.15)
    c.line(6.8, 10.2, 17.2, 10.2)
    c.line(12.0, 10.2, 12.0, 14.0)
    c.polyline([(8.8, 18.0), (12.0, 14.0), (15.2, 18.0)])


def _draw_notification_settings(c: IconCanvas) -> None:
    c.polyline([(5.5, 11.2), (5.5, 15.2), (3.5, 17.0), (14.5, 17.0)])
    c.arc(10.8, 10.2, 5.3, 180.0, 345.0)
    c.cut_circle(17.5, 16.8, 4.0)
    c.circle(17.5, 16.8, 2.8)
    c.dot(17.5, 16.8, r=0.9)


def _draw_privacy_settings(c: IconCanvas) -> None:
    _shield_outline(c)
    c.dot(12.0, 11.2, r=1.2)
    c.line(12.0, 12.4, 12.0, 15.2)


def _draw_data_controls(c: IconCanvas) -> None:
    c.ellipse(12.0, 6.0, 7.6, 2.8)
    c.line(4.4, 6.0, 4.4, 18.0)
    c.line(19.6, 6.0, 19.6, 18.0)
    c.arc(12.0, 12.0, 7.6, 15.0, 165.0)
    c.arc(12.0, 18.0, 7.6, 15.0, 165.0)


def _draw_profile(c: IconCanvas) -> None:
    c.rect(2.8, 4.5, 18.4, 15.0, rx=2.2)
    c.dot(8.0, 10.0, r=1.45)
    c.arc(8.0, 16.8, 3.6, 210.0, 330.0)
    c.line(13.2, 9.8, 18.2, 9.8)
    c.line(13.2, 14.2, 17.2, 14.2)


def _draw_account(c: IconCanvas) -> None:
    c.circle(12.0, 12.0, 9.2)
    c.circle(12.0, 8.8, 2.8)
    c.arc(12.0, 19.5, 5.8, 212.0, 328.0)


# --- 8. Security and privacy (16) ---

def _draw_lock(c: IconCanvas) -> None:
    c.rect(4.5, 10.2, 15.0, 10.6, rx=2.2)
    c.arc(12.0, 7.8, 4.0, 180.0, 360.0)
    c.line(8.0, 7.8, 8.0, 10.2)
    c.line(16.0, 7.8, 16.0, 10.2)
    c.dot(12.0, 15.5, r=1.3)


def _draw_unlock(c: IconCanvas) -> None:
    c.rect(4.5, 10.2, 15.0, 10.6, rx=2.2)
    c.arc(15.2, 7.2, 4.0, 180.0, 345.0)
    c.line(11.2, 7.2, 11.2, 10.2)
    c.dot(12.0, 15.5, r=1.3)


def _draw_key(c: IconCanvas) -> None:
    c.circle(7.4, 12.0, 4.0)
    c.line(11.4, 12.0, 20.8, 12.0)
    c.line(17.0, 12.0, 17.0, 15.8)
    c.line(20.6, 12.0, 20.6, 16.2)


def _draw_passkey(c: IconCanvas) -> None:
    c.circle(8.8, 7.4, 3.2)
    c.arc(8.8, 20.2, 5.8, 198.0, 330.0)
    c.circle(18.0, 8.2, 2.4)
    c.line(18.0, 10.6, 18.0, 19.8)
    c.line(18.0, 16.5, 20.8, 16.5)


def _draw_password(c: IconCanvas) -> None:
    c.rect(2.5, 7.5, 19.0, 9.0, rx=2.2)
    for dx in (7.0, 12.0, 17.0):
        c.dot(dx, 12.0, r=1.25)


def _draw_shield_check(c: IconCanvas) -> None:
    _shield_outline(c)
    c.polyline([(8.5, 12.0), (11.0, 14.6), (16.0, 9.2)])


def _draw_shield_alert(c: IconCanvas) -> None:
    _shield_outline(c)
    c.line(12.0, 7.8, 12.0, 12.6)
    c.dot(12.0, 16.0, r=1.15)


def _draw_eye(c: IconCanvas) -> None:
    c.cubic_stroke((2.5, 12.0), (6.5, 5.2), (17.5, 5.2), (21.5, 12.0))
    c.cubic_stroke((21.5, 12.0), (17.5, 18.8), (6.5, 18.8), (2.5, 12.0))
    c.circle(12.0, 12.0, 3.2)


def _draw_eye_off(c: IconCanvas) -> None:
    _draw_eye(c)
    c.slash_off(3.0, 3.0, 21.0, 21.0)


def _draw_incognito(c: IconCanvas) -> None:
    c.line(2.8, 11.8, 21.2, 11.8)
    c.polyline([(6.2, 11.8), (8.2, 5.2), (12.0, 6.6), (15.8, 5.2), (17.8, 11.8)])
    c.circle(8.0, 16.8, 2.8)
    c.circle(16.0, 16.8, 2.8)
    c.line(10.8, 16.8, 13.2, 16.8)


def _draw_encryption(c: IconCanvas) -> None:
    pts = []
    for k in range(6):
        ang = math.radians(-90.0 + k * 60.0)
        pts.append((12.0 + 9.2 * math.cos(ang), 12.0 + 9.2 * math.sin(ang)))
    c.polygon(pts)
    c.circle(12.0, 10.6, 2.3)
    c.line(12.0, 12.9, 12.0, 16.5)


def _draw_consent(c: IconCanvas) -> None:
    c.rect(4.2, 3.5, 13.6, 17.0, rx=2.0)
    c.line(8.0, 8.5, 14.0, 8.5)
    c.cubic_stroke((7.5, 14.5), (9.5, 11.5), (12.0, 17.0), (14.5, 14.0))
    c.cut_circle(18.0, 17.5, 4.2)
    c.polyline([(15.2, 17.5), (17.2, 19.5), (20.8, 15.5)])


def _draw_audit_log(c: IconCanvas) -> None:
    c.rect(4.0, 3.5, 16.0, 17.0, rx=2.2)
    c.dot(8.0, 8.5, r=0.95)
    c.line(11.5, 8.5, 16.5, 8.5)
    c.dot(8.0, 12.5, r=0.95)
    c.line(11.5, 12.5, 16.5, 12.5)
    c.dot(8.0, 16.5, r=0.95)
    c.line(11.5, 16.5, 15.0, 16.5)


def _draw_block(c: IconCanvas) -> None:
    c.circle(12.0, 12.0, 8.8)
    c.line(6.0, 6.0, 18.0, 18.0)


def _draw_report_flag(c: IconCanvas) -> None:
    c.line(5.2, 3.5, 5.2, 21.0)
    c.polygon([(5.2, 4.2), (19.6, 4.2), (16.8, 9.2), (19.6, 14.2), (5.2, 14.2)])


def _draw_two_factor(c: IconCanvas) -> None:
    c.rect(5.4, 2.8, 10.6, 18.4, rx=2.2)
    c.line(9.5, 5.8, 12.1, 5.8)
    c.cut_round_rect(12.6, 9.4, 9.2, 10.6, rx=2.2)
    c.rect(13.8, 13.0, 6.8, 5.8, rx=1.2)
    c.arc(17.2, 11.2, 2.0, 180.0, 360.0)
    c.line(15.2, 11.2, 15.2, 13.0)
    c.line(19.2, 11.2, 19.2, 13.0)


# --- 9. Cloud and sync (10) ---

def _draw_cloud(c: IconCanvas) -> None:
    _cloud_outline(c, bottom_open=False)


def _draw_cloud_upload(c: IconCanvas) -> None:
    _cloud_outline(c, bottom_open=True)
    c.line(12.0, 20.8, 12.0, 12.5)
    c.polyline([(8.8, 15.5), (12.0, 12.2), (15.2, 15.5)])


def _draw_cloud_download(c: IconCanvas) -> None:
    _cloud_outline(c, bottom_open=True)
    c.line(12.0, 12.2, 12.0, 20.8)
    c.polyline([(8.8, 17.6), (12.0, 20.8), (15.2, 17.6)])


def _draw_cloud_off(c: IconCanvas) -> None:
    _cloud_outline(c, bottom_open=False)
    c.slash_off(3.0, 3.0, 21.0, 21.0)


def _draw_backup(c: IconCanvas) -> None:
    _cloud_outline(c, bottom_open=False)
    c.rect(4.2, 19.2, 15.6, 2.4, rx=1.2)


def _draw_restore_backup(c: IconCanvas) -> None:
    c.arc(8.0, 12.8, 3.4, 90.0, 260.0)
    c.arc(12.0, 9.4, 4.4, 185.0, 355.0)
    c.arc(16.2, 13.0, 3.2, 275.0, 450.0)
    c.line(8.0, 16.2, 16.2, 16.2)
    c.arc(12.0, 12.0, 9.5, 20.0, 165.0)
    c.polyline([(3.2, 11.2), (2.6, 15.0), (6.5, 14.5)])


def _draw_sync_now(c: IconCanvas) -> None:
    _cloud_outline(c, bottom_open=True)
    c.arc(12.0, 17.0, 3.5, 195.0, 345.0)
    c.arc(12.0, 17.0, 3.5, 15.0, 165.0)


def _draw_auto_sync(c: IconCanvas) -> None:
    _cloud_outline(c, bottom_open=False)
    c.dot(18.5, 5.2, r=1.45)


def _draw_sync_paused(c: IconCanvas) -> None:
    _cloud_outline(c, bottom_open=True)
    c.line(10.0, 15.5, 10.0, 20.8)
    c.line(14.0, 15.5, 14.0, 20.8)


def _draw_sync_error(c: IconCanvas) -> None:
    _cloud_outline(c, bottom_open=True)
    c.line(12.0, 13.5, 12.0, 17.2)
    c.dot(12.0, 20.4, r=1.15)


# --- 10. Account and help (16) ---

def _draw_sign_in(c: IconCanvas) -> None:
    c.polyline([(13.5, 4.0), (19.5, 4.0), (19.5, 20.0), (13.5, 20.0)])
    c.line(3.8, 12.0, 15.0, 12.0)
    c.polyline([(10.6, 7.6), (15.0, 12.0), (10.6, 16.4)])


def _draw_sign_out(c: IconCanvas) -> None:
    c.polyline([(10.5, 4.0), (4.5, 4.0), (4.5, 20.0), (10.5, 20.0)])
    c.line(9.2, 12.0, 20.2, 12.0)
    c.polyline([(15.8, 7.6), (20.2, 12.0), (15.8, 16.4)])


def _draw_switch_account(c: IconCanvas) -> None:
    c.circle(8.5, 8.2, 3.0)
    c.arc(8.5, 19.2, 5.2, 200.0, 340.0)
    c.polyline([(14.2, 5.2), (19.5, 5.2), (16.8, 2.8)])
    c.polyline([(19.5, 11.2), (14.2, 11.2), (16.8, 13.6)])


def _draw_add_account(c: IconCanvas) -> None:
    c.circle(9.2, 7.6, 3.3)
    c.arc(9.2, 20.2, 6.2, 198.0, 336.0)
    c.line(18.5, 8.2, 18.5, 14.2)
    c.line(15.5, 11.2, 21.5, 11.2)


def _draw_upgrade(c: IconCanvas) -> None:
    c.circle(12.0, 12.0, 9.0)
    c.line(12.0, 16.8, 12.0, 7.5)
    c.polyline([(8.0, 11.5), (12.0, 7.5), (16.0, 11.5)])


def _draw_help_center(c: IconCanvas) -> None:
    c.circle(12.0, 12.0, 9.0)
    c.circle(12.0, 12.0, 4.0)
    c.line(5.8, 5.8, 9.1, 9.1)
    c.line(14.9, 5.8, 18.2, 9.1)
    c.line(5.8, 18.2, 9.1, 14.9)
    c.line(14.9, 14.9, 18.2, 18.2)


def _draw_feedback(c: IconCanvas) -> None:
    c.polygon([(3.5, 4.2), (20.5, 4.2), (20.5, 16.5), (10.0, 16.5), (5.2, 20.5), (5.2, 16.5), (3.5, 16.5)])
    c.line(8.2, 8.8, 15.8, 8.8)
    c.line(8.2, 12.6, 13.2, 12.6)


def _draw_support(c: IconCanvas) -> None:
    c.arc(12.0, 11.5, 7.8, 180.0, 360.0)
    c.rect(3.2, 11.5, 3.8, 5.8, rx=1.4)
    c.rect(17.0, 11.5, 3.8, 5.8, rx=1.4)
    c.arc(13.8, 17.5, 3.2, 0.0, 90.0)
    c.line(10.8, 20.7, 13.8, 20.7)


def _draw_report_a_problem(c: IconCanvas) -> None:
    c.polygon([(3.5, 4.2), (20.5, 4.2), (20.5, 16.5), (10.0, 16.5), (5.2, 20.5), (5.2, 16.5), (3.5, 16.5)])
    c.line(12.0, 7.4, 12.0, 10.6)
    c.dot(12.0, 13.4, r=1.0)


def _draw_about(c: IconCanvas) -> None:
    c.rect(3.5, 3.5, 17.0, 17.0, rx=3.6)
    c.dot(12.0, 8.0, r=1.15)
    c.line(12.0, 11.5, 12.0, 16.5)


def _draw_whats_new(c: IconCanvas) -> None:
    c.rect(4.2, 9.8, 15.6, 10.6, rx=1.8)
    c.rect(3.0, 6.5, 18.0, 3.6, rx=1.0)
    c.line(12.0, 6.5, 12.0, 20.4)
    c.polyline([(12.0, 6.5), (7.5, 3.2), (6.8, 6.5)])
    c.polyline([(12.0, 6.5), (16.5, 3.2), (17.2, 6.5)])


def _draw_tutorial(c: IconCanvas) -> None:
    c.polygon([(2.5, 9.5), (12.0, 4.5), (21.5, 9.5), (12.0, 14.5)])
    c.polyline([(6.2, 12.2), (6.2, 17.5), (12.0, 19.8), (17.8, 17.5), (17.8, 12.2)])
    c.line(20.5, 10.2, 20.5, 17.0)


def _draw_tips(c: IconCanvas) -> None:
    c.arc(12.0, 9.2, 5.6, 135.0, 405.0)
    c.polyline([(9.0, 14.2), (9.0, 17.5), (15.0, 17.5), (15.0, 14.2)])
    c.line(9.8, 20.8, 14.2, 20.8)


def _draw_share_app(c: IconCanvas) -> None:
    c.rect(5.5, 2.5, 11.0, 19.0, rx=2.2)
    c.line(10.0, 18.2, 12.0, 18.2)
    c.cut_circle(16.8, 9.5, 4.0)
    c.line(12.5, 12.2, 20.2, 4.5)
    c.polyline([(15.2, 4.5), (20.2, 4.5), (20.2, 9.5)])


def _draw_rate_app(c: IconCanvas) -> None:
    pts = []
    for k in range(10):
        ang = math.radians(-90.0 + k * 36.0)
        rad = 6.5 if k % 2 == 0 else 3.0
        pts.append((12.0 + rad * math.cos(ang), 9.5 + rad * math.sin(ang)))
    c.polygon(pts)
    c.line(5.2, 19.8, 18.8, 19.8)


def _draw_legal(c: IconCanvas) -> None:
    c.line(12.0, 3.2, 12.0, 20.8)
    c.line(7.5, 20.8, 16.5, 20.8)
    c.line(4.2, 7.2, 19.8, 7.2)
    c.polygon([(4.5, 7.4), (2.5, 13.8), (6.5, 13.8)])
    c.polygon([(19.5, 7.4), (17.5, 13.8), (21.5, 13.8)])


# --- 11. Code and developer (5 Phase-1 pull-ins per Section 23) ---

def _draw_code(c: IconCanvas) -> None:
    c.polyline([(7.5, 7.2), (3.0, 12.0), (7.5, 16.8)])
    c.polyline([(16.5, 7.2), (21.0, 12.0), (16.5, 16.8)])
    c.line(13.8, 5.2, 10.2, 18.8)


def _draw_terminal(c: IconCanvas) -> None:
    c.rect(2.8, 4.2, 18.4, 15.6, rx=1.8)
    c.line(2.8, 8.8, 21.2, 8.8)
    c.polyline([(6.8, 12.0), (9.8, 14.4), (6.8, 16.8)])
    c.line(12.2, 16.8, 16.8, 16.8)


def _draw_code_block(c: IconCanvas) -> None:
    c.rect(3.5, 3.5, 17.0, 17.0, rx=2.2)
    c.line(7.2, 8.4, 12.6, 8.4)
    c.line(9.5, 12.0, 16.8, 12.0)
    c.line(7.2, 15.6, 14.5, 15.6)


def _draw_run_code(c: IconCanvas) -> None:
    c.polygon([(6.5, 4.2), (19.6, 12.0), (6.5, 19.8)])


def _draw_branch(c: IconCanvas) -> None:
    c.circle(6.5, 6.2, 2.2)
    c.circle(6.5, 17.8, 2.2)
    c.line(6.5, 8.4, 6.5, 15.6)
    c.circle(17.5, 8.5, 2.2)
    c.cubic_stroke((6.5, 15.4), (11.5, 15.4), (17.5, 14.5), (17.5, 10.7))


# --- 12. Filled active variants (8 per Section 23) ---

def _draw_star_filled(c: IconCanvas) -> None:
    pts = []
    for k in range(10):
        ang = math.radians(-90.0 + k * 36.0)
        rad = 10.0 if k % 2 == 0 else 4.5
        pts.append((12.0 + rad * math.cos(ang), 12.6 + rad * math.sin(ang)))
    c.fill_polygon(pts)


def _draw_bookmark_filled(c: IconCanvas) -> None:
    c.fill_polygon([(5.2, 3.0), (18.8, 3.0), (18.8, 21.0), (12.0, 16.2), (5.2, 21.0)])


def _draw_pin_filled(c: IconCanvas) -> None:
    c.fill_polygon([
        (8.2, 3.6), (15.8, 3.6), (14.6, 10.4),
        (19.0, 14.4), (5.0, 14.4), (9.4, 10.4),
    ])
    c.line(12.0, 14.0, 12.0, 21.5)


def _draw_thumbs_up_filled(c: IconCanvas) -> None:
    c.fill_round_rect(2.6, 10.2, 4.4, 10.2, rx=1.4)
    c.fill_polygon([
        (8.6, 11.2), (11.8, 3.4), (14.4, 3.8), (13.6, 9.2),
        (20.0, 9.2), (21.6, 12.0), (19.6, 20.4), (8.6, 20.4),
    ])


def _draw_thumbs_down_filled(c: IconCanvas) -> None:
    c.fill_round_rect(2.6, 3.6, 4.4, 10.2, rx=1.4)
    c.fill_polygon([
        (8.6, 12.8), (11.8, 20.6), (14.4, 20.2), (13.6, 14.8),
        (20.0, 14.8), (21.6, 12.0), (19.6, 3.6), (8.6, 3.6),
    ])


def _draw_bell_filled(c: IconCanvas) -> None:
    pts = [(4.0, 17.8), (6.0, 15.5), (6.0, 10.5)]
    for step in range(13):
        ang = math.radians(180.0 + step * 15.0)
        pts.append((12.0 + 6.0 * math.cos(ang), 10.5 + 6.5 * math.sin(ang)))
    pts.extend([(18.0, 15.5), (20.0, 17.8)])
    c.fill_polygon(pts)
    c.arc(12.0, 18.8, 2.3, 0.0, 180.0)


def _draw_mic_filled(c: IconCanvas) -> None:
    c.fill_round_rect(8.6, 2.2, 6.8, 11.6, rx=3.4)
    c.arc(12.0, 10.2, 6.8, 12.0, 168.0)
    c.line(12.0, 17.0, 12.0, 21.2)
    c.line(8.2, 21.2, 15.8, 21.2)


def _draw_stop_filled(c: IconCanvas) -> None:
    c.fill_round_rect(4.6, 4.6, 14.8, 14.8, rx=3.2)


SYMBOLS_PHASE1_B: List[SymbolSpec] = [
    # 5. Files and content (36)
    SymbolSpec("file", "Files and content", ("document", "blank", "page"), _draw_file),
    SymbolSpec("new-file", "Files and content", ("create", "add", "page"), _draw_new_file),
    SymbolSpec("folder", "Files and content", ("directory", "collection"), _draw_folder),
    SymbolSpec("new-folder", "Files and content", ("create", "directory", "add"), _draw_new_folder),
    SymbolSpec("document", "Files and content", ("article", "text", "report"), _draw_document),
    SymbolSpec("spreadsheet", "Files and content", ("table", "csv", "grid"), _draw_spreadsheet),
    SymbolSpec("presentation", "Files and content", ("slides", "deck", "chart"), _draw_presentation),
    SymbolSpec("pdf", "Files and content", ("portable", "document", "export"), _draw_pdf),
    SymbolSpec("image-file", "Files and content", ("picture", "png", "jpg"), _draw_image_file),
    SymbolSpec("audio-file", "Files and content", ("sound", "wav", "mp3"), _draw_audio_file),
    SymbolSpec("video-file", "Files and content", ("movie", "mp4", "clip"), _draw_video_file),
    SymbolSpec("code-file", "Files and content", ("source", "script", "dev"), _draw_code_file),
    SymbolSpec("archive", "Files and content", ("zip", "compress", "box"), _draw_archive),
    SymbolSpec("link", "Files and content", ("url", "chain", "connect"), _draw_link),
    SymbolSpec("unlink", "Files and content", ("disconnect", "break", "detach"), _draw_unlink),
    SymbolSpec("share", "Files and content", ("network", "publish", "broadcast"), _draw_share, rtl_mirror=True),
    SymbolSpec("export", "Files and content", ("output", "extract", "out"), _draw_export, rtl_mirror=True),
    SymbolSpec("import", "Files and content", ("ingest", "load", "in"), _draw_import, rtl_mirror=True),
    SymbolSpec("download", "Files and content", ("save-local", "fetch", "down"), _draw_download),
    SymbolSpec("upload", "Files and content", ("send-cloud", "push", "up"), _draw_upload),
    SymbolSpec("bookmark", "Files and content", ("save", "favorite", "ribbon"), _draw_bookmark),
    SymbolSpec("tag", "Files and content", ("label", "category", "badge"), _draw_tag),
    SymbolSpec("star", "Files and content", ("favorite", "important", "rating"), _draw_star),
    SymbolSpec("note", "Files and content", ("memo", "sticky", "jot"), _draw_note),
    SymbolSpec("clipboard", "Files and content", ("copy", "board", "notes"), _draw_clipboard),
    SymbolSpec("trash", "Files and content", ("bin", "discard", "delete"), _draw_trash),
    SymbolSpec("restore", "Files and content", ("recover", "undelete", "undo"), _draw_restore, rtl_mirror=True),
    SymbolSpec("history", "Files and content", ("timeline", "log", "past"), _draw_history, rtl_mirror=True),
    SymbolSpec("version", "Files and content", ("revision", "release", "snapshot"), _draw_version),
    SymbolSpec("compare", "Files and content", ("diff", "split", "review"), _draw_compare),
    SymbolSpec("template", "Files and content", ("blueprint", "layout", "preset"), _draw_template),
    SymbolSpec("print", "Files and content", ("printer", "paper", "hardcopy"), _draw_print),
    SymbolSpec("save", "Files and content", ("disk", "commit", "store"), _draw_save),
    SymbolSpec("duplicate", "Files and content", ("clone", "copy-plus"), _draw_duplicate),
    SymbolSpec("rename", "Files and content", ("title", "cursor", "edit"), _draw_rename),
    SymbolSpec("label", "Files and content", ("pill", "marker", "classify"), _draw_label),

    # 6. Search and filter (12)
    SymbolSpec("search", "Search and filter", ("find", "magnifier", "lookup"), _draw_search),
    SymbolSpec("zoom-in", "Search and filter", ("magnify", "plus", "enlarge"), _draw_zoom_in),
    SymbolSpec("zoom-out", "Search and filter", ("shrink", "minus", "reduce"), _draw_zoom_out),
    SymbolSpec("filter", "Search and filter", ("funnel", "narrow", "facet"), _draw_filter),
    SymbolSpec("sort", "Search and filter", ("order", "rank", "swap"), _draw_sort),
    SymbolSpec("sort-ascending", "Search and filter", ("a-z", "low-to-high"), _draw_sort_ascending, rtl_mirror=True),
    SymbolSpec("sort-descending", "Search and filter", ("z-a", "high-to-low"), _draw_sort_descending, rtl_mirror=True),
    SymbolSpec("find-in-page", "Search and filter", ("grep", "scan", "search-doc"), _draw_find_in_page),
    SymbolSpec("recent", "Search and filter", ("clock", "latest", "time"), _draw_recent),
    SymbolSpec("saved-search", "Search and filter", ("starred", "query", "preset"), _draw_saved_search),
    SymbolSpec("advanced-search", "Search and filter", ("query", "options", "tune"), _draw_advanced_search),
    SymbolSpec("clear", "Search and filter", ("eraser", "reset", "wipe"), _draw_clear),

    # 7. Settings and preferences (16)
    SymbolSpec("settings", "Settings and preferences", ("gear", "cog", "preferences"), _draw_settings),
    SymbolSpec("sliders", "Settings and preferences", ("tune", "controls", "adjust"), _draw_sliders),
    SymbolSpec("toggle-on", "Settings and preferences", ("switch", "enabled", "active"), _draw_toggle_on),
    SymbolSpec("toggle-off", "Settings and preferences", ("switch", "disabled", "inactive"), _draw_toggle_off),
    SymbolSpec("theme", "Settings and preferences", ("appearance", "contrast", "mode"), _draw_theme),
    SymbolSpec("dark-mode", "Settings and preferences", ("moon", "night", "theme"), _draw_dark_mode),
    SymbolSpec("light-mode", "Settings and preferences", ("sun", "day", "bright"), _draw_light_mode),
    SymbolSpec("auto-mode", "Settings and preferences", ("system", "adaptive", "theme"), _draw_auto_mode),
    SymbolSpec("font-size", "Settings and preferences", ("typography", "scale", "text"), _draw_font_size),
    SymbolSpec("language", "Settings and preferences", ("globe", "locale", "i18n"), _draw_language),
    SymbolSpec("accessibility", "Settings and preferences", ("a11y", "universal", "inclusive"), _draw_accessibility),
    SymbolSpec("notification-settings", "Settings and preferences", ("alerts", "bell-gear"), _draw_notification_settings),
    SymbolSpec("privacy-settings", "Settings and preferences", ("shield", "guard", "data"), _draw_privacy_settings),
    SymbolSpec("data-controls", "Settings and preferences", ("database", "storage", "retention"), _draw_data_controls),
    SymbolSpec("profile", "Settings and preferences", ("card", "identity", "bio"), _draw_profile),
    SymbolSpec("account", "Settings and preferences", ("user-circle", "member", "identity"), _draw_account),

    # 8. Security and privacy (16)
    SymbolSpec("lock", "Security and privacy", ("secure", "private", "padlock"), _draw_lock),
    SymbolSpec("unlock", "Security and privacy", ("open", "decrypted", "public"), _draw_unlock),
    SymbolSpec("key", "Security and privacy", ("secret", "token", "credential"), _draw_key),
    SymbolSpec("passkey", "Security and privacy", ("fido", "webauthn", "biometric"), _draw_passkey),
    SymbolSpec("password", "Security and privacy", ("pin", "secret", "masked"), _draw_password),
    SymbolSpec("shield-check", "Security and privacy", ("protected", "safe", "verified"), _draw_shield_check),
    SymbolSpec("shield-alert", "Security and privacy", ("risk", "warning", "security"), _draw_shield_alert),
    SymbolSpec("eye", "Security and privacy", ("show", "visible", "preview"), _draw_eye),
    SymbolSpec("eye-off", "Security and privacy", ("hide", "masked", "private"), _draw_eye_off),
    SymbolSpec("incognito", "Security and privacy", ("ephemeral", "private", "hat"), _draw_incognito),
    SymbolSpec("encryption", "Security and privacy", ("cipher", "hex-lock", "vault"), _draw_encryption),
    SymbolSpec("consent", "Security and privacy", ("agree", "signed", "terms"), _draw_consent),
    SymbolSpec("audit-log", "Security and privacy", ("trail", "records", "compliance"), _draw_audit_log, rtl_mirror=True),
    SymbolSpec("block", "Security and privacy", ("ban", "deny", "prohibit"), _draw_block),
    SymbolSpec("report-flag", "Security and privacy", ("flag", "abuse", "moderation"), _draw_report_flag),
    SymbolSpec("two-factor", "Security and privacy", ("2fa", "mfa", "otp"), _draw_two_factor),

    # 9. Cloud and sync (10)
    SymbolSpec("cloud", "Cloud and sync", ("remote", "server", "storage"), _draw_cloud),
    SymbolSpec("cloud-upload", "Cloud and sync", ("push", "publish", "save"), _draw_cloud_upload),
    SymbolSpec("cloud-download", "Cloud and sync", ("pull", "fetch", "get"), _draw_cloud_download),
    SymbolSpec("cloud-off", "Cloud and sync", ("offline", "disconnected"), _draw_cloud_off),
    SymbolSpec("backup", "Cloud and sync", ("snapshot", "save", "archive"), _draw_backup),
    SymbolSpec("restore-backup", "Cloud and sync", ("rollback", "recover"), _draw_restore_backup, rtl_mirror=True),
    SymbolSpec("sync-now", "Cloud and sync", ("cloud-sync", "update"), _draw_sync_now),
    SymbolSpec("auto-sync", "Cloud and sync", ("background", "continuous"), _draw_auto_sync),
    SymbolSpec("sync-paused", "Cloud and sync", ("hold", "suspend"), _draw_sync_paused),
    SymbolSpec("sync-error", "Cloud and sync", ("conflict", "alert", "fail"), _draw_sync_error),

    # 10. Account and help (16)
    SymbolSpec("sign-in", "Account and help", ("login", "enter", "auth"), _draw_sign_in, rtl_mirror=True),
    SymbolSpec("sign-out", "Account and help", ("logout", "exit", "leave"), _draw_sign_out, rtl_mirror=True),
    SymbolSpec("switch-account", "Account and help", ("swap", "profile", "change"), _draw_switch_account),
    SymbolSpec("add-account", "Account and help", ("register", "invite", "plus"), _draw_add_account),
    SymbolSpec("upgrade", "Account and help", ("pro", "tier", "promote"), _draw_upgrade),
    SymbolSpec("help-center", "Account and help", ("docs", "lifebuoy", "faq"), _draw_help_center),
    SymbolSpec("feedback", "Account and help", ("comment", "review", "suggest"), _draw_feedback),
    SymbolSpec("support", "Account and help", ("headset", "agent", "care"), _draw_support),
    SymbolSpec("report-a-problem", "Account and help", ("bug", "issue", "incident"), _draw_report_a_problem),
    SymbolSpec("about", "Account and help", ("info-box", "version", "credits"), _draw_about),
    SymbolSpec("whats-new", "Account and help", ("gift", "changelog", "release"), _draw_whats_new),
    SymbolSpec("tutorial", "Account and help", ("guide", "learn", "cap"), _draw_tutorial),
    SymbolSpec("tips", "Account and help", ("idea", "bulb", "hint"), _draw_tips),
    SymbolSpec("share-app", "Account and help", ("invite", "mobile", "refer"), _draw_share_app, rtl_mirror=True),
    SymbolSpec("rate-app", "Account and help", ("review", "star", "score"), _draw_rate_app),
    SymbolSpec("legal", "Account and help", ("terms", "policy", "justice"), _draw_legal),

    # 11. Code and developer (5 Phase-1 pull-ins per Section 23)
    SymbolSpec("code", "Code and developer", ("brackets", "markup", "syntax"), _draw_code),
    SymbolSpec("terminal", "Code and developer", ("cli", "shell", "console"), _draw_terminal),
    SymbolSpec("code-block", "Code and developer", ("snippet", "pre", "source"), _draw_code_block),
    SymbolSpec("run-code", "Code and developer", ("play", "execute", "start"), _draw_run_code),
    SymbolSpec("branch", "Code and developer", ("git", "fork", "vcs"), _draw_branch),

    # 12. Filled active variants (8 per Section 23)
    SymbolSpec("star-filled", "Filled active variants", ("favorite", "active", "solid"), _draw_star_filled, is_filled=True),
    SymbolSpec("bookmark-filled", "Filled active variants", ("saved", "active", "solid"), _draw_bookmark_filled, is_filled=True),
    SymbolSpec("pin-filled", "Filled active variants", ("pinned", "active", "solid"), _draw_pin_filled, is_filled=True),
    SymbolSpec("thumbs-up-filled", "Filled active variants", ("liked", "active", "solid"), _draw_thumbs_up_filled, is_filled=True),
    SymbolSpec("thumbs-down-filled", "Filled active variants", ("disliked", "active", "solid"), _draw_thumbs_down_filled, is_filled=True),
    SymbolSpec("bell-filled", "Filled active variants", ("subscribed", "active", "solid"), _draw_bell_filled, is_filled=True),
    SymbolSpec("mic-filled", "Filled active variants", ("recording", "active", "solid"), _draw_mic_filled, is_filled=True),
    SymbolSpec("stop-filled", "Filled active variants", ("halt", "active", "solid"), _draw_stop_filled, is_filled=True),
]
