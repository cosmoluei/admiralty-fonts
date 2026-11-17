"""
Milestone 6 Visual Proof Suite Renderer:
  1. specimens/milestone6_bold_trio_proof.png
  2. specimens/milestone6_symbols_catalog.png
  3. specimens/milestone6_buttons_and_ui.png
"""

from __future__ import annotations
import json
from pathlib import Path
import sys
from typing import Dict, List, Optional, Tuple

import freetype
import numpy as np
from PIL import Image, ImageDraw
import uharfbuzz as hb

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from render_specimen import HBFreeTypeRenderer, get_ui_label_font


class DirHBRenderer(HBFreeTypeRenderer):
    """Extends HBFreeTypeRenderer with explicit direction/script shaping (for RTL rtlm)."""

    def draw_glyph_run(
        self,
        img: Image.Image,
        x: float,
        y_baseline: float,
        text: str,
        px_size: float,
        color: Tuple[int, int, int],
        features: Optional[Dict[str, bool]] = None,
        direction: Optional[str] = None,
        script: Optional[str] = None,
    ) -> float:
        if not text:
            return x
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        if direction:
            buf.direction = direction
        if script:
            buf.script = script
        hb.shape(self.hb_font, buf, features or {})
        if not buf.glyph_positions:
            return x

        ft_size_26_6 = max(64, int(round(px_size * 64)))
        self.ft_face.set_char_size(ft_size_26_6, ft_size_26_6, 72, 72)

        scale = px_size / self.upm
        pen_x = x
        pen_y = y_baseline
        arr = np.asarray(img).copy()
        h_img, w_img, _ = arr.shape
        col = np.array(color, dtype=np.float32)

        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            gid = info.codepoint
            if gid == 0 and text != "\ufffd":
                raise RuntimeError(f"Missing glyph (.notdef gid=0) on {text!r}")
            gx = pen_x + pos.x_offset * scale
            gy = pen_y - pos.y_offset * scale
            ix = int(np.floor(gx))
            frac_x = int(round((gx - ix) * 64))
            iy = int(round(gy))
            self.ft_face.set_transform(freetype.FT_Matrix(0x10000, 0, 0, 0x10000), freetype.FT_Vector(frac_x, 0))
            self.ft_face.load_glyph(gid, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_NO_HINTING)
            slot = self.ft_face.glyph
            bmp = slot.bitmap
            bw, bh = bmp.width, bmp.rows
            if bw > 0 and bh > 0:
                alpha = np.array(bmp.buffer, dtype=np.float32).reshape(bh, bw) / 255.0
                dx0 = ix + slot.bitmap_left
                dy0 = iy - slot.bitmap_top
                cx0, cy0 = max(0, dx0), max(0, dy0)
                cx1, cy1 = min(w_img, dx0 + bw), min(h_img, dy0 + bh)
                if cx1 > cx0 and cy1 > cy0:
                    sub_a = alpha[cy0 - dy0 : cy1 - dy0, cx0 - dx0 : cx1 - dx0][:, :, None]
                    roi = arr[cy0:cy1, cx0:cx1].astype(np.float32)
                    roi_lin = np.power(roi / 255.0, 1.8)
                    col_lin = np.power(col / 255.0, 1.8)
                    out_lin = roi_lin * (1.0 - sub_a) + col_lin * sub_a
                    arr[cy0:cy1, cx0:cx1] = np.clip(np.power(out_lin, 1.0 / 1.8) * 255.0, 0, 255).astype(np.uint8)
            pen_x += pos.x_advance * scale
            pen_y -= pos.y_advance * scale

        self.ft_face.set_transform(freetype.FT_Matrix(0x10000, 0, 0, 0x10000), freetype.FT_Vector(0, 0))
        img.paste(Image.fromarray(arr))
        return pen_x


def _draw_mixed_line(
    img: Image.Image,
    x: float,
    y: float,
    segments: List[Tuple[DirHBRenderer, str, Optional[Dict[str, bool]]]],
    px_size: float,
    color: Tuple[int, int, int],
) -> float:
    cx = x
    for rend, txt, feats in segments:
        cx = rend.draw_text(img, cx, y, txt, px_size, color, features=feats or {})
    return cx


def render_bold_trio_proof(out_path: Path) -> None:
    ttf_dir = ROOT / "fonts" / "ttf"
    sans_r = DirHBRenderer(ttf_dir / "AdmiraltySans-Regular.ttf")
    sans_b = DirHBRenderer(ttf_dir / "AdmiraltySans-Bold.ttf")
    serif_r = DirHBRenderer(ttf_dir / "AdmiraltySerif-Regular.ttf")
    serif_b = DirHBRenderer(ttf_dir / "AdmiraltySerif-Bold.ttf")
    mono_r = DirHBRenderer(ttf_dir / "AdmiraltyMono-Regular.ttf")
    mono_b = DirHBRenderer(ttf_dir / "AdmiraltyMono-Bold.ttf")

    W, H = 1920, 1780
    img = Image.new("RGB", (W, H), (247, 246, 241))
    draw = ImageDraw.Draw(img)
    ui_title = get_ui_label_font(17)
    ui_lbl = get_ui_label_font(13)
    ui_micro = get_ui_label_font(11)

    draw.rectangle((0, 0, W, 82), fill=(22, 25, 31))
    draw.text((54, 22), "ADMIRALTY MILESTONE 6  ·  BOLD (700) TRIO & MIXED REGULAR/BOLD ZERO-REFLOW PROOF  (v0.120)", fill=(244, 246, 250), font=ui_title)
    draw.text((54, 48), "Sans Bold (134-142u, 1:1 Duplex w/ Serif Bold)  |  Serif Bold (140-160u stems, ~2.3:1 contrast)  |  Mono Bold (600u fixed, 114-118u, ss01 88u)", fill=(162, 170, 184), font=ui_lbl)

    # Panel 1: Regular vs Bold Trio Hierarchy
    draw.rounded_rectangle((46, 104, 1874, 598), radius=14, fill=(255, 255, 255), outline=(224, 222, 214), width=2)
    draw.text((74, 122), "1. REGULAR (400) VS BOLD (700) FAMILY ARCHITECTURE — WEIGHT, CONTRAST & MONO COLUMN LOCK", fill=(70, 76, 88), font=ui_lbl)

    # Column 1: Sans & Serif
    col_x = 76
    sans_r.draw_text(img, col_x, 186, "Admiralty Sans Regular (400)", 22, (74, 80, 92))
    sans_b.draw_text(img, col_x, 226, "Admiralty Sans Bold (700) — Clean UI Emphasis", 26, (18, 20, 26))
    serif_r.draw_text(img, col_x, 276, "Admiralty Serif Regular (400)", 22, (74, 80, 92))
    serif_b.draw_text(img, col_x, 316, "Admiralty Serif Bold (700) — Calligraphic Editorial Contrast", 26, (18, 20, 26))

    # Diacritics + Symbols Strip
    sample_b = "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789"
    draw.text((col_x, 344), "SANS BOLD FULL CAPS / LC / FIGS", fill=(110, 116, 128), font=ui_micro)
    sans_b.draw_text(img, col_x, 380, sample_b, 20, (24, 28, 36))
    draw.text((col_x, 398), "SERIF BOLD FULL CAPS / LC / FIGS + DIACRITICS & PUNCTUATION", fill=(110, 116, 128), font=ui_micro)
    serif_b.draw_text(img, col_x, 434, sample_b, 20, (24, 28, 36))
    ext_line = "Œuvre & Æther · §4.2 © 2026 · 1ª 2º · nǐ hǎo ǖ ǘ ǚ ǜ Ǖ Ǘ Ǚ Ǜ ẞ Ĳ ĳ ð · ₹ ₩ ₽ ≈ ∞ √ π ∆ Ω ↔ ⇒ ✓ ✗ ‰ ′ ″ №"
    serif_b.draw_text(img, col_x, 476, ext_line, 18, (34, 38, 48))
    sans_b.draw_text(img, col_x, 514, ext_line, 18, (34, 38, 48))

    # Right half of Panel 1: Mono Regular vs Mono Bold aligned column proof
    mx = 1090
    draw.line((1058, 152, 1058, 578), fill=(232, 230, 224), width=2)
    draw.text((mx, 122), "ADMIRALTY MONO REGULAR vs BOLD — 600u LOCKED COLUMN + ss01 (88u)", fill=(70, 76, 88), font=ui_lbl)
    ruler = "01234567890123456789012345678901234567890123"
    code1 = "pub fn duplex(x: i32) -> bool { x != 0 && x <= 9 }"
    code2 = "const ID_MAP: &str = \"Il1_O0 => <= -> <- != ==\";"
    code3 = "// Tabular check: 0123456789  $1,480.95  €290  ¥99"
    # Vertical col guide lines every 10 chars (16px * 0.6 = 9.6 px/char)
    step_w = 15.0 * 0.6
    for k in range(0, 45, 10):
        gx = mx + k * step_w
        draw.line((gx, 160, gx, 560), fill=(212, 228, 246), width=1)

    mono_r.draw_text(img, mx, 184, ruler, 15, (112, 118, 130), {"zero": True})
    mono_b.draw_text(img, mx, 214, ruler, 15, (20, 24, 32), {"zero": True})
    mono_r.draw_text(img, mx, 256, code1, 15, (42, 48, 60), {"ss01": True, "zero": True})
    mono_b.draw_text(img, mx, 286, code1, 15, (16, 18, 24), {"ss01": True, "zero": True})
    mono_r.draw_text(img, mx, 328, code2, 15, (42, 48, 60), {"ss01": True, "zero": True})
    mono_b.draw_text(img, mx, 358, code2, 15, (16, 18, 24), {"ss01": True, "zero": True})
    mono_r.draw_text(img, mx, 400, code3, 15, (42, 48, 60), {"ss01": True, "zero": True})
    mono_b.draw_text(img, mx, 430, code3, 15, (16, 18, 24), {"ss01": True, "zero": True})

    # Verify exact Mono Reg == Mono Bold width on canvas!
    w_mr = mono_r.measure_text(code1, 15, {"ss01": True, "zero": True})
    w_mb = mono_b.measure_text(code1, 15, {"ss01": True, "zero": True})
    draw.text((mx, 472), f"Measured 50-char width @15px (ss01 ON): Reg={w_mr:.2f}px | Bold={w_mb:.2f}px (Δ={abs(w_mr-w_mb):.2f}px)", fill=(22, 128, 68), font=ui_lbl)
    mono_b.draw_text(img, mx, 524, "=> != <= -> <- >=  &  Il1 O0 @ # %", 22, (20, 24, 32), {"ss01": True, "zero": True})
    draw.text((mx, 548), "22px Bold ss01 ligatures & anti-confusable glyphs", fill=(110, 116, 128), font=ui_micro)

    # Panel 2: Mixed Regular + Bold Duplex Zero-Reflow Proof
    draw.rounded_rectangle((46, 618, 1874, 1020), radius=14, fill=(255, 255, 255), outline=(224, 222, 214), width=2)
    draw.text((74, 636), "2. MIXED REGULAR + BOLD ZERO-REFLOW PROOF — SANS vs SERIF IDENTICAL METRICS & TABULAR LOCK", fill=(70, 76, 88), font=ui_lbl)

    mixed_runs = [
        [
            ("Admiralty Personal Agent ", False, None),
            ("executes plan v0.120 ", True, None),
            ("with zero text reflow across Sans & Serif weights.", False, None),
        ],
        [
            ("Critical tokens: ", True, None),
            ("WAVEY To Va Yo Ti fV fW fY qj gj ", False, None),
            ("Bold Emphasis $1,480.95 & €290.00 ", True, {"tnum": True}),
            ("(tnum=580u).", False, {"tnum": True}),
        ],
        [
            ("Multilingual: ", True, None),
            ("Voix ambiguë d'un cœur · Œuvre & Æther · Příliš žluťoučký kůň · nǐ hǎo ǖ ǘ ǚ ǜ ẞ", False, None),
        ],
    ]

    for card_i, (label, cx0, cw, r_reg, r_bld, bg_col, brd_col) in enumerate([
        ("SERIF REGULAR + BOLD (Agent Bubble)", 74, 860, serif_r, serif_b, (250, 249, 245), (222, 218, 208)),
        ("SANS REGULAR + BOLD (User Bubble)", 986, 860, sans_r, sans_b, (238, 244, 252), (200, 216, 238)),
    ]):
        draw.rounded_rectangle((cx0, 668, cx0 + cw, 996), radius=12, fill=bg_col, outline=brd_col, width=2)
        draw.text((cx0 + 22, 684), label, fill=(76, 84, 98), font=ui_lbl)
        cy = 740
        for row_idx, run in enumerate(mixed_runs):
            segs = [(r_bld if is_b else r_reg, txt, ft) for txt, is_b, ft in run]
            end_x = _draw_mixed_line(img, cx0 + 24, cy, segs, 17, (20, 24, 32))
            line_w = end_x - (cx0 + 24)
            draw.line((end_x, cy - 18, end_x, cy + 8), fill=(214, 72, 72), width=2)
            draw.text((end_x + 8, cy - 14), f"{line_w:.2f}px", fill=(192, 54, 54), font=ui_micro)
            cy += 42
        # Tabular Regular vs Bold numeric comparison inside each bubble
        cy += 10
        for num_txt, is_b_row, tag_n in [
            ("2026-11-16   $1,480.95   98.42%   (Reg tnum)", False, "R"),
            ("2026-11-16   $1,480.95   98.42%   (Bold tnum)", True, "B"),
        ]:
            rend_u = r_bld if is_b_row else r_reg
            end_nx = rend_u.draw_text(img, cx0 + 24, cy, num_txt, 17, (20, 24, 32), {"tnum": True, "zero": True})
            draw.text((end_nx + 12, cy - 14), f"w={end_nx-(cx0+24):.2f}px", fill=(24, 128, 72), font=ui_micro)
            cy += 34

    # Panel 3: Small-Size @1x Bold Counter Openness Test + Magnifier Zoom
    draw.rounded_rectangle((46, 1042, 1874, 1736), radius=14, fill=(255, 255, 255), outline=(224, 222, 214), width=2)
    draw.text((74, 1060), "3. BOLD @1x COUNTER OPENNESS AUDIT (12px, 14px, 16px LIGHT & DARK) + MICROSCOPE ZOOM (42px)", fill=(70, 76, 88), font=ui_lbl)

    probe_str = "ABRP aegmsw 4689 &@§%‰ æœßẞ ǖđø"
    probe_code = "def fn(x): a+e*g == [0, 8] != &@§"

    # Light & Dark @1x panels side-by-side
    for is_dark, px0 in ((False, 74), (True, 986)):
        panel_bg = (19, 21, 25) if is_dark else (250, 249, 245)
        fg_col = (238, 240, 245) if is_dark else (18, 20, 25)
        sub_col = (144, 152, 166) if is_dark else (94, 100, 112)
        draw.rounded_rectangle((px0, 1094, px0 + 860, 1506), radius=12, fill=panel_bg, outline=(46, 52, 64) if is_dark else (222, 218, 208), width=2)
        draw.text((px0 + 20, 1110), f"{'DARK MODE' if is_dark else 'LIGHT MODE'} · REAL 12px / 14px / 16px BOLD COUNTER STRESS TEST", fill=sub_col, font=ui_micro)
        ry = 1152
        for sz in (12, 14, 16):
            draw.text((px0 + 20, ry - 12), f"{sz}px", fill=sub_col, font=ui_micro)
            sans_b.draw_text(img, px0 + 62, ry, "Sans:  " + probe_str, sz, fg_col)
            ry += sz + 14
            serif_b.draw_text(img, px0 + 62, ry, "Serif: " + probe_str, sz, fg_col)
            ry += sz + 14
            mono_b.draw_text(img, px0 + 62, ry, "Mono:  " + probe_code, sz, fg_col, {"ss01": True, "zero": True})
            ry += sz + 22

    # High-res 42px Microscope Row (Serif Bold, Sans Bold, Mono Bold)
    draw.text((74, 1524), "CRITICAL COUNTERS & LIGATURE SHAPES AT 42px MICROSCOPE (Inspect open apertures & crisp joins):", fill=(70, 76, 88), font=ui_lbl)
    zoom_chars = "A B R P Q a e g m w 4 8 & @ § æ œ ẞ ǖ Ǖ"
    sans_b.draw_text(img, 74, 1594, "SansB:  " + zoom_chars, 40, (20, 24, 30))
    serif_b.draw_text(img, 74, 1654, "SerifB: " + zoom_chars, 40, (20, 24, 30))
    mono_b.draw_text(img, 74, 1714, "MonoB:  A B M W a e g m w 4 8 & @ § æ œ -> != <=", 34, (20, 24, 30), {"ss01": True, "zero": True})

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out_path))
    print(f"Saved {out_path} ({W}x{H})")


def render_symbols_catalog(out_path: Path) -> None:
    meta = json.loads((ROOT / "symbols" / "admiralty-symbols.json").read_text(encoding="utf-8"))
    symbols = meta["symbols"]

    ttf_dir = ROOT / "fonts" / "ttf"
    sym_r = DirHBRenderer(ttf_dir / "AdmiraltySymbols-Regular.ttf")
    sym_b = DirHBRenderer(ttf_dir / "AdmiraltySymbols-Bold.ttf")

    groups: List[Tuple[str, List[dict]]] = []
    cur_cat = None
    for rec in symbols:
        if rec["category"] != cur_cat:
            cur_cat = rec["category"]
            groups.append((cur_cat, []))
        groups[-1][1].append(rec)

    cols = 10
    cell_w = 204
    cell_h = 84
    margin_x = 46
    top_y = 108

    # Compute exact canvas height dynamically
    total_y = top_y
    for cat, items in groups:
        rows = (len(items) + cols - 1) // cols
        total_y += 38 + rows * cell_h + 18

    W = margin_x * 2 + cols * cell_w
    H = total_y + 42
    img = Image.new("RGB", (W, H), (247, 246, 241))
    draw = ImageDraw.Draw(img)
    ui_title = get_ui_label_font(18)
    ui_hdr = get_ui_label_font(14)
    ui_name = get_ui_label_font(12)
    ui_code = get_ui_label_font(10)

    draw.rectangle((0, 0, W, 82), fill=(22, 25, 31))
    draw.text((margin_x, 20), f"ADMIRALTY SYMBOLS PHASE 1 CATALOG  ·  ALL {len(symbols)} ORIGINAL 24x24 ICONS (REGULAR 400 + BOLD 700, U+E000..U+E0D9)", fill=(244, 246, 250), font=ui_title)
    draw.text((margin_x, 48), "Each card displays Regular (left, 60u) & Bold (right, 84u) @26px, PUA codepoint, hyphen-case name, and [RTL] mirroring badge", fill=(162, 170, 184), font=ui_name)

    y = top_y
    for cat, items in groups:
        draw.text((margin_x, y + 6), f"{cat.upper()}  ({len(items)})", fill=(42, 48, 60), font=ui_hdr)
        draw.line((margin_x, y + 28, W - margin_x, y + 28), fill=(212, 208, 198), width=2)
        y += 38
        rows = (len(items) + cols - 1) // cols
        for idx, rec in enumerate(items):
            r = idx // cols
            c = idx % cols
            cx = margin_x + c * cell_w + 4
            cy = y + r * cell_h + 4
            cw = cell_w - 8
            ch = cell_h - 8
            card_bg = (242, 247, 255) if rec["filled"] else (255, 255, 255)
            card_brd = (182, 204, 236) if rec["filled"] else (226, 224, 216)
            draw.rounded_rectangle((cx, cy, cx + cw, cy + ch), radius=8, fill=card_bg, outline=card_brd, width=1)

            ch_sym = chr(rec["codepointInt"])
            # Subtle cap baseline + center ticks behind icon preview
            sym_r.draw_glyph_run(img, cx + 16, cy + 36, ch_sym, 26, (26, 30, 38))
            sym_b.draw_glyph_run(img, cx + 62, cy + 36, ch_sym, 26, (26, 30, 38))

            code_str = rec["codepoint"] + (" [RTL]" if rec["rtlMirror"] else "")
            draw.text((cx + 106, cy + 16), code_str, fill=(92, 108, 134) if rec["rtlMirror"] else (120, 126, 138), font=ui_code)
            draw.text((cx + 12, cy + 49), rec["name"], fill=(28, 32, 42), font=ui_name)

        y += rows * cell_h + 18

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out_path))
    print(f"Saved {out_path} ({W}x{H})")


def render_buttons_and_ui(out_path: Path) -> None:
    meta = json.loads((ROOT / "symbols" / "admiralty-symbols.json").read_text(encoding="utf-8"))
    by_name = {rec["name"]: chr(rec["codepointInt"]) for rec in meta["symbols"]}

    ttf_dir = ROOT / "fonts" / "ttf"
    sans_r = DirHBRenderer(ttf_dir / "AdmiraltySans-Regular.ttf")
    sans_b = DirHBRenderer(ttf_dir / "AdmiraltySans-Bold.ttf")
    serif_r = DirHBRenderer(ttf_dir / "AdmiraltySerif-Regular.ttf")
    serif_b = DirHBRenderer(ttf_dir / "AdmiraltySerif-Bold.ttf")
    sym_r = DirHBRenderer(ttf_dir / "AdmiraltySymbols-Regular.ttf")
    sym_b = DirHBRenderer(ttf_dir / "AdmiraltySymbols-Bold.ttf")

    W, H = 1920, 1520
    img = Image.new("RGB", (W, H), (247, 246, 241))
    draw = ImageDraw.Draw(img)
    ui_title = get_ui_label_font(17)
    ui_lbl = get_ui_label_font(13)
    ui_micro = get_ui_label_font(11)

    draw.rectangle((0, 0, W, 82), fill=(22, 25, 31))
    draw.text((54, 20), "ADMIRALTY SYMBOLS  ·  INLINE BUTTON CAP-CENTERING, 14px DISAMBIGUATION & RTL MIRRORING (rtlm)", fill=(244, 246, 250), font=ui_title)
    draw.text((54, 48), "Section 10 & 23 verification: 12-24px inline buttons (Light/Dark, Regular/Bold), subtle pairs at 14px, -filled toggles, HarfBuzz RTL", fill=(162, 170, 184), font=ui_lbl)

    # Panel 1: Inline Buttons & Alignment Matrix (12, 14, 16, 18, 24 px Light & Dark)
    draw.rounded_rectangle((46, 102, 1874, 650), radius=14, fill=(255, 255, 255), outline=(224, 222, 214), width=2)
    draw.text((74, 120), "1. INLINE ICON + TEXT BUTTON ALIGNMENT (12px, 14px, 16px, 18px, 24px — Regular 400 & Bold 700, Light & Dark)", fill=(70, 76, 88), font=ui_lbl)

    buttons_spec = [
        ("Send Prompt", "send"),
        ("Search Memory", "search"),
        ("Code Block", "code-block"),
        ("Settings", "settings"),
        ("Verified Source", "shield-check"),
        ("Run Workflow", "run-code"),
    ]

    for is_dark, px0 in ((False, 74), (True, 986)):
        p_bg = (19, 21, 25) if is_dark else (250, 249, 245)
        btn_bg = (34, 40, 50) if is_dark else (255, 255, 255)
        btn_brd = (58, 66, 82) if is_dark else (210, 208, 200)
        prim_bg = (74, 134, 232) if is_dark else (24, 30, 40)
        fg = (238, 240, 246) if is_dark else (20, 24, 32)
        sub = (146, 154, 168) if is_dark else (94, 100, 112)
        draw.rounded_rectangle((px0, 150, px0 + 860, 626), radius=12, fill=p_bg, outline=(46, 52, 64) if is_dark else (222, 218, 208), width=2)
        draw.text((px0 + 20, 164), f"{'DARK SURFACE' if is_dark else 'LIGHT SURFACE'} · CAP-CENTERED INLINE ICON+TEXT BUTTONS (Top Row = Sans/Sym Reg · Lower Row = Sans/Sym Bold)", fill=sub, font=ui_micro)

        ry = 204
        for sz in (12, 14, 16, 18, 24):
            draw.text((px0 + 18, ry + int(sz * 0.35)), f"{sz}px", fill=sub, font=ui_micro)
            bx = px0 + 62
            # Alternate Regular and Bold across sizes & primary button!
            pairs = [
                ("Send Prompt", "send", True, True),
                ("Settings", "settings", False, False),
                ("Run Code", "run-code", False, True),
                ("Share", "share", False, False),
            ]
            for lbl_txt, sym_name, is_prim, use_bold in pairs:
                t_rend = sans_b if use_bold else sans_r
                s_rend = sym_b if use_bold else sym_r
                pad_x = max(10, int(sz * 0.7))
                gap = max(5, int(sz * 0.38))
                btn_h = int(sz * 1.95)
                tw = t_rend.measure_text(lbl_txt, sz)
                iw = sz  # glyph advance 840u vs size ~ 0.84*sz
                bw_btn = int(pad_x * 2 + sz * 0.84 + gap + tw)
                if bx + bw_btn > px0 + 842:
                    break
                fill_b = prim_bg if is_prim else btn_bg
                txt_b = (255, 255, 255) if is_prim else fg
                draw.rounded_rectangle((bx, ry, bx + bw_btn, ry + btn_h), radius=max(6, int(sz * 0.45)), fill=fill_b, outline=prim_bg if is_prim else btn_brd, width=1)
                # Cap center baseline math: Cap height is 0.70*sz above baseline -> center at y_base - 0.35*sz == ry + btn_h/2
                y_base = ry + btn_h / 2.0 + 0.35 * sz
                s_rend.draw_glyph_run(img, bx + pad_x, y_base, by_name[sym_name], sz, txt_b)
                t_rend.draw_text(img, bx + pad_x + sz * 0.84 + gap, y_base, lbl_txt, sz, txt_b)
                if sz == 24 and lbl_txt == "Settings":
                    # Alignment guide ticks on 24px button (baseline y=0, cap y=700)
                    draw.line((bx + pad_x - 4, y_base, bx + bw_btn - pad_x + 4, y_base), fill=(0, 175, 195), width=1)
                    draw.line((bx + pad_x - 4, y_base - 0.70 * sz, bx + bw_btn - pad_x + 4, y_base - 0.70 * sz), fill=(0, 175, 195), width=1)
                bx += bw_btn + 14
            ry += int(sz * 1.95) + 18

    # Panel 2: 14px Disambiguation Stress Test & Filled Variants
    draw.rounded_rectangle((46, 668, 1874, 1110), radius=14, fill=(255, 255, 255), outline=(224, 222, 214), width=2)
    draw.text((74, 686), "2. 14px CRITICAL PAIR DISAMBIGUATION + SECTION 23 ACTIVE (-filled) VARIANTS", fill=(70, 76, 88), font=ui_lbl)

    compare_groups = [
        ("send vs share", ["send", "share", "forward-message"]),
        ("mic vs mic-off vs filled", ["mic", "mic-off", "mic-filled"]),
        ("info vs warning vs error vs about", ["info", "warning", "error", "about"]),
        ("flags & reports", ["report-flag", "report-a-problem", "feedback"]),
        ("code & agent UI", ["prompt", "terminal", "code", "code-block", "branch"]),
        ("filled state toggles (Reg vs -filled)", ["star", "star-filled", "bookmark", "bookmark-filled", "pin", "pin-filled", "bell", "bell-filled"]),
    ]

    gx = 74
    gy = 720
    for grp_title, names in compare_groups:
        col_w = 574
        draw.rounded_rectangle((gx, gy, gx + col_w, gy + 114), radius=10, fill=(250, 249, 245), outline=(224, 222, 214), width=1)
        draw.text((gx + 14, gy + 10), grp_title, fill=(76, 84, 98), font=ui_lbl)
        ix = gx + 16
        step_x = min(130, (col_w - 28) // len(names))
        for nm in names:
            # Render @14px Reg, @14px Bold, and @28px reference cleanly
            sym_r.draw_glyph_run(img, ix, gy + 54, by_name[nm], 14, (20, 24, 32))
            sym_b.draw_glyph_run(img, ix + 18, gy + 54, by_name[nm], 14, (20, 24, 32))
            sym_r.draw_glyph_run(img, ix, gy + 90, by_name[nm], 24, (44, 52, 68))
            lbl_show = nm if len(nm) <= 10 or step_x >= 90 else nm.replace("-filled", "+F").replace("report-", "rep-")
            draw.text((ix, gy + 96), lbl_show, fill=(104, 110, 122), font=ui_micro)
            ix += step_x
        gx += col_w + 18
        if gx + col_w > 1880:
            gx = 74
            gy += 126

    # Also add Serif Bold & Sans Bold mixed status chips row inside Panel 2 bottom
    draw.text((74, 984), "INLINE CHAT ACTIONS & STATUS CHIPS @14px (Serif & Sans Regular/Bold + Symbols):", fill=(76, 84, 98), font=ui_lbl)
    chip_items = [
        ("Copy", "copy", serif_r, sym_r),
        ("Regenerate", "regenerate", sans_b, sym_b),
        ("Thumbs Up", "thumbs-up-filled", sans_b, sym_b),
        ("Thumbs Down", "thumbs-down", sans_r, sym_r),
        ("Run Code", "run-code", serif_b, sym_b),
        ("Pinned", "pin-filled", sans_b, sym_b),
        ("Report Flag", "report-flag", sans_r, sym_r),
        ("Offline", "offline", sans_r, sym_r),
        ("Sync Error", "sync-error", sans_b, sym_b),
        ("Verified", "verified", serif_b, sym_b),
    ]
    cx = 74
    cy = 1020
    for c_lbl, c_sym, c_tr, c_sr in chip_items:
        tw = c_tr.measure_text(c_lbl, 14)
        bw_c = int(20 + 12 + 6 + tw)
        draw.rounded_rectangle((cx, cy, cx + bw_c, cy + 32), radius=8, fill=(242, 245, 250), outline=(204, 214, 232), width=1)
        yb = cy + 16 + 0.35 * 14
        c_sr.draw_glyph_run(img, cx + 10, yb, by_name[c_sym], 14, (28, 36, 52))
        c_tr.draw_text(img, cx + 26, yb, c_lbl, 14, (28, 36, 52))
        cx += bw_c + 12

    # Panel 3: Live HarfBuzz RTL Mirroring Strip (feature rtlm)
    draw.rounded_rectangle((46, 1130, 1874, 1476), radius=14, fill=(255, 255, 255), outline=(224, 222, 214), width=2)
    draw.text((74, 1148), "3. LIVE OPENTYPE RTL MIRRORING (feature 'rtlm', hb.direction='rtl', script='arab') — LTR vs RTL AUTOMATIC GLYPH SUBSTITUTION", fill=(70, 76, 88), font=ui_lbl)

    rtl_samples = [
        "back", "forward", "chevron-left", "chevron-right", "double-chevron-left",
        "send", "reply", "forward-message", "handoff", "task-list",
        "sidebar-left", "sidebar-right", "share", "export", "import",
        "restore", "history", "sort-ascending", "sign-in", "sign-out", "share-app",
    ]
    col_step = 86
    rx0 = 74
    draw.text((rx0, 1196), "LTR Reg", fill=(90, 96, 108), font=ui_micro)
    draw.text((rx0, 1252), "RTL rtlm", fill=(20, 110, 188), font=ui_micro)
    draw.text((rx0, 1326), "LTR Bold", fill=(90, 96, 108), font=ui_micro)
    draw.text((rx0, 1382), "RTL Bold", fill=(20, 110, 188), font=ui_micro)

    for idx, nm in enumerate(rtl_samples):
        sx = 148 + idx * 80
        ch_sym = by_name[nm]
        draw.line((sx - 6, 1180, sx - 6, 1430), fill=(238, 236, 230), width=1)
        sym_r.draw_glyph_run(img, sx + 12, 1212, ch_sym, 26, (28, 32, 40), features={}, direction="ltr")
        sym_r.draw_glyph_run(img, sx + 12, 1268, ch_sym, 26, (18, 96, 174), features={"rtlm": True}, direction="rtl", script="arab")
        sym_b.draw_glyph_run(img, sx + 12, 1342, ch_sym, 26, (28, 32, 40), features={}, direction="ltr")
        sym_b.draw_glyph_run(img, sx + 12, 1398, ch_sym, 26, (18, 96, 174), features={"rtlm": True}, direction="rtl", script="arab")
        draw.text((sx + 2, 1436), nm[:11], fill=(96, 102, 114), font=ui_micro)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out_path))
    print(f"Saved {out_path} ({W}x{H})")


if __name__ == "__main__":
    spec_dir = ROOT / "specimens"
    render_bold_trio_proof(spec_dir / "milestone6_bold_trio_proof.png")
    render_symbols_catalog(spec_dir / "milestone6_symbols_catalog.png")
    render_buttons_and_ui(spec_dir / "milestone6_buttons_and_ui.png")
