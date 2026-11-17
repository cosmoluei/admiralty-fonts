"""
Milestone 7 Visual Proof Suite Renderer (v0.130):
  1. specimens/milestone7_weights_and_italics.png
  2. specimens/milestone7_duplex_and_roles.png
  3. specimens/milestone7_mono_ide_proof.png
"""

from __future__ import annotations
import json
from pathlib import Path
import sys
from typing import Dict, List, Optional, Tuple

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from render_milestone6 import DirHBRenderer, _draw_mixed_line
from render_specimen import get_ui_label_font


def _load_fonts() -> Dict[str, DirHBRenderer]:
    ttf_dir = ROOT / "fonts" / "ttf"
    return {
        "sans_r": DirHBRenderer(ttf_dir / "AdmiraltySans-Regular.ttf"),
        "sans_m": DirHBRenderer(ttf_dir / "AdmiraltySans-Medium.ttf"),
        "sans_b": DirHBRenderer(ttf_dir / "AdmiraltySans-Bold.ttf"),
        "sans_ri": DirHBRenderer(ttf_dir / "AdmiraltySans-Italic.ttf"),
        "sans_mi": DirHBRenderer(ttf_dir / "AdmiraltySans-MediumItalic.ttf"),
        "sans_bi": DirHBRenderer(ttf_dir / "AdmiraltySans-BoldItalic.ttf"),
        "serif_r": DirHBRenderer(ttf_dir / "AdmiraltySerif-Regular.ttf"),
        "serif_m": DirHBRenderer(ttf_dir / "AdmiraltySerif-Medium.ttf"),
        "serif_b": DirHBRenderer(ttf_dir / "AdmiraltySerif-Bold.ttf"),
        "serif_ri": DirHBRenderer(ttf_dir / "AdmiraltySerif-Italic.ttf"),
        "serif_mi": DirHBRenderer(ttf_dir / "AdmiraltySerif-MediumItalic.ttf"),
        "serif_bi": DirHBRenderer(ttf_dir / "AdmiraltySerif-BoldItalic.ttf"),
        "mono_r": DirHBRenderer(ttf_dir / "AdmiraltyMono-Regular.ttf"),
        "mono_m": DirHBRenderer(ttf_dir / "AdmiraltyMono-Medium.ttf"),
        "mono_b": DirHBRenderer(ttf_dir / "AdmiraltyMono-Bold.ttf"),
        "mono_ri": DirHBRenderer(ttf_dir / "AdmiraltyMono-Italic.ttf"),
        "mono_mi": DirHBRenderer(ttf_dir / "AdmiraltyMono-MediumItalic.ttf"),
        "mono_bi": DirHBRenderer(ttf_dir / "AdmiraltyMono-BoldItalic.ttf"),
        "sym_r": DirHBRenderer(ttf_dir / "AdmiraltySymbols-Regular.ttf"),
        "sym_m": DirHBRenderer(ttf_dir / "AdmiraltySymbols-Medium.ttf"),
        "sym_b": DirHBRenderer(ttf_dir / "AdmiraltySymbols-Bold.ttf"),
    }


def render_weights_and_italics(f: Dict[str, DirHBRenderer], out_path: Path) -> None:
    W, H = 1920, 2170
    img = Image.new("RGB", (W, H), (247, 246, 241))
    draw = ImageDraw.Draw(img)
    ui_title = get_ui_label_font(17)
    ui_lbl = get_ui_label_font(13)
    ui_micro = get_ui_label_font(11)

    draw.rectangle((0, 0, W, 82), fill=(22, 25, 31))
    draw.text(
        (54, 20),
        "ADMIRALTY MILESTONE 7  ·  MEDIUM (500) & TRUE DUPLEXED ITALICS (-9.5°) 18-STYLE LATIN ARCHITECTURE  (v0.130)",
        fill=(244, 246, 250),
        font=ui_title,
    )
    draw.text(
        (54, 48),
        "Weight progression 400 -> 500 -> 700 across Upright & -9.5° Cursive Italic  |  True cursive Serif lowercase (a, e, f, g) 1:1 duplexed w/ Sans",
        fill=(162, 170, 184),
        font=ui_lbl,
    )

    # Panel 1: 18-Style Latin Matrix (3 columns x 6 rows)
    draw.rounded_rectangle((46, 102, 1874, 816), radius=14, fill=(255, 255, 255), outline=(224, 222, 214), width=2)
    draw.text(
        (74, 120),
        "1. COMPLETE 18-STYLE LATIN WEIGHT × SLANT MATRIX (400 / 500 / 700  ×  UPRIGHT / ITALIC -9.5°)",
        fill=(70, 76, 88),
        font=ui_lbl,
    )

    cols = [
        ("ADMIRALTY SANS (UI Humanist)", 74, [
            ("Regular 400", f["sans_r"]),
            ("Italic 400", f["sans_ri"]),
            ("Medium 500", f["sans_m"]),
            ("Medium Italic 500", f["sans_mi"]),
            ("Bold 700", f["sans_b"]),
            ("Bold Italic 700", f["sans_bi"]),
        ]),
        ("ADMIRALTY SERIF (Literary Cursive)", 670, [
            ("Regular 400", f["serif_r"]),
            ("Italic 400", f["serif_ri"]),
            ("Medium 500", f["serif_m"]),
            ("Medium Italic 500", f["serif_mi"]),
            ("Bold 700", f["serif_b"]),
            ("Bold Italic 700", f["serif_bi"]),
        ]),
        ("ADMIRALTY MONO (600u Fixed Pitch)", 1266, [
            ("Regular 400", f["mono_r"]),
            ("Italic 400", f["mono_ri"]),
            ("Medium 500", f["mono_m"]),
            ("Medium Italic 500", f["mono_mi"]),
            ("Bold 700", f["mono_b"]),
            ("Bold Italic 700", f["mono_bi"]),
        ]),
    ]
    for col_idx, (col_hdr, cx, rows) in enumerate(cols):
        if col_idx > 0:
            draw.line((cx - 24, 154, cx - 24, 796), fill=(230, 228, 220), width=2)
        draw.text((cx, 156), col_hdr, fill=(40, 48, 62), font=ui_lbl)
        ry = 192
        for idx, (rlabel, rend) in enumerate(rows):
            is_mono = col_idx == 2
            draw.text((cx, ry - 4), rlabel, fill=(108, 114, 128), font=ui_micro)
            sz_main = 18 if is_mono else 22
            txt_main = "Admiralty Agent -> 0.95" if is_mono else "Admiralty Personal Agent — $1,480"
            feats = {"ss01": True, "zero": True} if is_mono else {}
            rend.draw_text(img, cx, ry + 30, txt_main, sz_main, (18, 22, 30), feats)
            txt_sub = "AaGgFfEe  Il1 O0  nǐ hǎo  => !=" if is_mono else "AaGgFfEe  æ œ  Voix ambiguë · nǐ hǎo ǖ"
            rend.draw_text(img, cx, ry + 56, txt_sub, 14 if is_mono else 15, (86, 92, 106), feats)
            if idx < len(rows) - 1:
                draw.line((cx, ry + 78, cx + 556, ry + 78), fill=(242, 240, 234), width=1)
            ry += 98

    # Panel 2: True Cursive Italic Microscope (40 px)
    draw.rounded_rectangle((46, 836, 1874, 1446), radius=14, fill=(255, 255, 255), outline=(224, 222, 214), width=2)
    draw.text(
        (74, 854),
        "2. TRUE CURSIVE ITALIC MICROSCOPE — SERIF LITERARY CURSIVE VS SANS HUMANIST ITALIC (1:1 DUPLEXED) VS MONO CODING CURSIVE",
        fill=(70, 76, 88),
        font=ui_lbl,
    )

    alpha_lc = "a b c d e f g h i j k l m n o p q r s t u v w x y z"
    lig_pair = "æ œ · (f) [f] {f} · fj fi · Voix ambiguë d’un cœur"
    intl_str = "Œuvre & Æther · Zażółć gęślą jaźń · nǐ hǎo ǖ ǘ ǚ ǜ"

    # Left-aligned microscope rows
    draw.text((74, 888), "SERIF ITALIC 400 (Cursive teardrops, angled entry flags, rising e-bar, single-story cursive g, -214u descended f)", fill=(92, 98, 112), font=ui_micro)
    f["serif_ri"].draw_text(img, 74, 942, alpha_lc, 38, (18, 22, 30))
    f["serif_ri"].draw_text(img, 74, 994, lig_pair, 34, (32, 38, 50))

    draw.text((74, 1020), "SANS ITALIC 400 (Single-story humanist a, tailed f, upturned i — 1:1 advance width lock with Serif Italic above)", fill=(24, 110, 180), font=ui_micro)
    f["sans_ri"].draw_text(img, 74, 1072, alpha_lc, 38, (22, 62, 108))
    f["sans_ri"].draw_text(img, 74, 1124, lig_pair, 34, (32, 72, 118))

    draw.line((74, 1150, 1846, 1150), fill=(230, 228, 220), width=2)
    draw.text((74, 1164), "SERIF MEDIUM ITALIC 500 & BOLD ITALIC 700 (Slanted +9.5° diacritics & European orthography)", fill=(92, 98, 112), font=ui_micro)
    f["serif_mi"].draw_text(img, 74, 1214, intl_str, 30, (20, 24, 32))
    f["serif_bi"].draw_text(img, 74, 1260, intl_str, 30, (16, 18, 24))

    draw.line((74, 1284, 1846, 1284), fill=(230, 228, 220), width=2)
    draw.text((74, 1298), "MONO ITALIC 400 & BOLD ITALIC 700 (600u Fixed Pitch · Coding cursive a, f, i, l, æ + sheared ss01 ligatures)", fill=(92, 98, 112), font=ui_micro)
    f["mono_ri"].draw_text(img, 74, 1348, "a b c d e f g h i j k l m n o p => -> <= != 01", 28, (24, 30, 42), {"ss01": True, "zero": True})
    f["mono_bi"].draw_text(img, 74, 1396, "a b c d e f g h i j k l m n o p => -> <= != 01", 28, (24, 30, 42), {"ss01": True, "zero": True})

    # Panel 3: Small-Size Counter & Italic Rhythm Audit (12 / 14 / 16 px @1x Light & Dark)
    draw.rounded_rectangle((46, 1466, 1874, 2128), radius=14, fill=(255, 255, 255), outline=(224, 222, 214), width=2)
    draw.text(
        (74, 1484),
        "3. @1x SMALL-SIZE COUNTER & ITALIC RHYTHM AUDIT (12px, 14px, 16px  ·  MEDIUM 500, ITALIC 400, MEDIUM ITALIC 500, BOLD ITALIC 700)",
        fill=(70, 76, 88),
        font=ui_lbl,
    )

    sample_ui = "Il1| O0o rn/m · $1,480.95 · Voix ambiguë d’un cœur · (f)"
    for is_dark, px0 in ((False, 74), (True, 986)):
        p_bg = (19, 21, 25) if is_dark else (250, 249, 245)
        fg_col = (236, 240, 246) if is_dark else (18, 22, 30)
        sub_col = (146, 154, 168) if is_dark else (92, 98, 110)
        brd_col = (46, 52, 64) if is_dark else (222, 218, 208)
        draw.rounded_rectangle((px0, 1516, px0 + 860, 2098), radius=12, fill=p_bg, outline=brd_col, width=2)
        draw.text(
            (px0 + 20, 1532),
            f"{'DARK MODE' if is_dark else 'LIGHT MODE'} · REAL 12px / 14px / 16px LEGIBILITY",
            fill=sub_col,
            font=ui_micro,
        )
        ry = 1568
        for sz in (12, 14, 16):
            draw.text((px0 + 20, ry - 12), f"{sz}px", fill=sub_col, font=ui_micro)
            f["sans_m"].draw_text(img, px0 + 62, ry, "SansMed:  " + sample_ui, sz, fg_col)
            ry += sz + 11
            f["serif_m"].draw_text(img, px0 + 62, ry, "SerifMed: " + sample_ui, sz, fg_col)
            ry += sz + 11
            f["serif_ri"].draw_text(img, px0 + 62, ry, "SerifIt:  " + sample_ui, sz, fg_col)
            ry += sz + 11
            f["serif_mi"].draw_text(img, px0 + 62, ry, "MedIt:    " + sample_ui, sz, fg_col)
            ry += sz + 11
            f["serif_bi"].draw_text(img, px0 + 62, ry, "BoldIt:   " + sample_ui, sz, fg_col)
            ry += sz + 11
            f["mono_ri"].draw_text(img, px0 + 62, ry, "MonoIt: fn(x) => x != 0 && x <= 9;", sz, fg_col, {"ss01": True, "zero": True})
            ry += sz + 18

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out_path))
    print(f"Saved {out_path} ({W}x{H})")


def render_duplex_and_roles(f: Dict[str, DirHBRenderer], out_path: Path) -> None:
    meta = json.loads((ROOT / "symbols" / "admiralty-symbols.json").read_text(encoding="utf-8"))
    by_name = {rec["name"]: chr(rec["codepointInt"]) for rec in meta["symbols"]}

    W, H = 1920, 1920
    img = Image.new("RGB", (W, H), (247, 246, 241))
    draw = ImageDraw.Draw(img)
    ui_title = get_ui_label_font(17)
    ui_lbl = get_ui_label_font(13)
    ui_micro = get_ui_label_font(11)

    draw.rectangle((0, 0, W, 82), fill=(22, 25, 31))
    draw.text(
        (54, 20),
        "ADMIRALTY MILESTONE 7  ·  6-STYLE ZERO-REFLOW DUPLEX PROOF & SECTION 10/16 WEIGHT ROLES  (v0.130)",
        fill=(244, 246, 250),
        font=ui_title,
    )
    draw.text(
        (54, 48),
        "Mixed Regular + Italic + Medium + Medium Italic + Bold + Bold Italic (Δ = 0.00 px)  |  3-Weight Symbols Pairing (400 / 500 / 700 @ 12-24px)",
        fill=(162, 170, 184),
        font=ui_lbl,
    )

    # Panel 1: Mixed 6-Style Zero-Reflow Proof (All-Sans vs All-Serif stacked alignment)
    draw.rounded_rectangle((46, 102, 1874, 586), radius=14, fill=(255, 255, 255), outline=(224, 222, 214), width=2)
    draw.text(
        (74, 120),
        "1. MIXED 6-STYLE ZERO-REFLOW PROOF — REGULAR + ITALIC + MEDIUM + MEDIUM ITALIC + BOLD + BOLD ITALIC (0.00 px REFLOW)",
        fill=(70, 76, 88),
        font=ui_lbl,
    )

    mixed_runs = [
        [
            ("Admiralty Agent ", "r", None),
            ("executes ", "ri", None),
            ("Medium Action ", "m", None),
            ("in literary ", "mi", None),
            ("Bold Verdict ", "b", None),
            ("and Emphatic Title ", "bi", None),
            ("with 0px shift.", "r", None),
        ],
        [
            ("Kerning & (f): ", "m", None),
            ("WAVEY To Va Yo ", "r", None),
            ("(f) [f] {f} fV fW ", "ri", None),
            ("fj fi qj gj · ", "mi", None),
            ("€1,362,446.86 ", "b", {"tnum": True}),
            ("Voix ambiguë d’un cœur!", "bi", None),
        ],
        [
            ("Multilingual: ", "b", None),
            ("Zażółć gęślą jaźń — ", "r", None),
            ("Příliš žluťoučký kůň — ", "ri", None),
            ("Œuvre & Æther · ", "m", None),
            ("nǐ hǎo ǖ ǘ ǚ ǜ ", "mi", None),
            ("§4.2 © 2026 ↗", "r", None),
        ],
    ]

    x0 = 200
    for tx in range(x0, 1780, 200):
        draw.line((tx, 152, tx, 562), fill=(235, 240, 248), width=1)

    ry = 186
    for idx, run in enumerate(mixed_runs):
        draw.text((74, ry - 12), f"Sans #{idx+1}", fill=(32, 108, 176), font=ui_micro)
        draw.text((74, ry + 20), f"Serif #{idx+1}", fill=(120, 62, 42), font=ui_micro)
        sans_segs = [(f[f"sans_{k}"], txt, ft) for txt, k, ft in run]
        serif_segs = [(f[f"serif_{k}"], txt, ft) for txt, k, ft in run]

        end_sans = _draw_mixed_line(img, x0, ry, sans_segs, 22, (24, 68, 118))
        end_serif = _draw_mixed_line(img, x0, ry + 34, serif_segs, 22, (22, 24, 30))
        delta = abs(end_sans - end_serif)
        assert delta < 1e-6, f"Mixed 6-style reflow delta {delta} != 0!"
        draw.line((end_sans, ry - 20, end_sans, ry + 42), fill=(22, 148, 76), width=2)
        draw.text((end_sans + 10, ry + 2), f"w={end_sans-x0:.2f}px  Δ={delta:.2f}px", fill=(18, 128, 66), font=ui_lbl)
        ry += 96

    # Verify mixed upright+italic+bold paragraph measure strip at bottom of Panel 1
    draw.rounded_rectangle((74, 476, 1846, 560), radius=10, fill=(246, 248, 251), outline=(218, 226, 238), width=1)
    draw.text((94, 490), "HARFBUZZ AUDIT PASSING ACROSS ALL 6 PAIRS: Regular (400), Medium (500), Bold (700), Italic (400), Medium Italic (500), Bold Italic (700)", fill=(58, 72, 92), font=ui_micro)
    f["serif_r"].draw_text(img, 94, 534, "Regular Body 400", 20, (24, 28, 36))
    f["serif_m"].draw_text(img, 310, 534, "Medium Button 500", 20, (24, 28, 36))
    f["serif_b"].draw_text(img, 540, 534, "Bold Heading 700", 20, (24, 28, 36))
    f["serif_ri"].draw_text(img, 760, 534, "Italic Quote 400", 20, (24, 28, 36))
    f["serif_mi"].draw_text(img, 980, 534, "Medium Italic 500", 20, (24, 28, 36))
    f["serif_bi"].draw_text(img, 1210, 534, "Bold Italic 700", 20, (24, 28, 36))
    f["sans_mi"].draw_text(img, 1420, 534, "Sans MedItalic 500", 20, (24, 68, 118))

    # Panel 2: Section 10 & 16 Three-Weight Symbol + Text Pairing (400 / 500 / 700 across 12-24 px)
    draw.rounded_rectangle((46, 606, 1874, 1140), radius=14, fill=(255, 255, 255), outline=(224, 222, 214), width=2)
    draw.text(
        (74, 624),
        "2. SECTION 10 & 16 THREE-WEIGHT SYMBOL + TEXT PAIRING (REGULAR 2.0u  ·  MEDIUM 2.35u UI BUTTONS  ·  BOLD 2.75u @ 12–24 px)",
        fill=(70, 76, 88),
        font=ui_lbl,
    )

    for is_dark, px0 in ((False, 74), (True, 986)):
        p_bg = (19, 21, 25) if is_dark else (250, 249, 245)
        btn_bg = (34, 40, 50) if is_dark else (255, 255, 255)
        btn_brd = (58, 66, 82) if is_dark else (210, 208, 200)
        prim_bg = (74, 134, 232) if is_dark else (24, 30, 40)
        fg = (238, 240, 246) if is_dark else (20, 24, 32)
        sub = (146, 154, 168) if is_dark else (94, 100, 112)
        draw.rounded_rectangle((px0, 654, px0 + 860, 1118), radius=12, fill=p_bg, outline=(46, 52, 64) if is_dark else (222, 218, 208), width=2)
        draw.text((px0 + 20, 668), f"{'DARK UI' if is_dark else 'LIGHT UI'} · WEIGHT PER BUTTON ROLE: Reg 400 (Subtle) | Med 500 (Default UI Button) | Bold 700 (Primary CTA)", fill=sub, font=ui_micro)

        ry = 702
        for sz in (12, 14, 16, 18, 24):
            draw.text((px0 + 18, ry + int(sz * 0.35)), f"{sz}px", fill=sub, font=ui_micro)
            bx = px0 + 62
            btn_specs = [
                ("Send Prompt", "send", "m", True),       # Primary CTA -> Bold or Medium; show Medium vs Bold clearly
                ("Settings", "settings", "m", False),     # Default UI Button = Medium 500!
                ("Run Code", "run-code", "b", False),     # Bold emphasis chip
                ("Search", "search", "r", False),         # Regular secondary chip
            ]
            # Make first button Bold Primary at even sizes and Medium Primary at odd sizes so all 3 weights shine
            for idx_b, (lbl_txt, sym_name, w_key, is_prim) in enumerate(btn_specs):
                if idx_b == 0 and sz in (14, 18, 24):
                    w_key = "b"
                t_rend = f[f"sans_{w_key}"]
                s_rend = f[f"sym_{w_key}"]
                pad_x = max(9, int(sz * 0.68))
                gap = max(5, int(sz * 0.36))
                btn_h = int(sz * 1.92)
                tw = t_rend.measure_text(lbl_txt, sz)
                bw_btn = int(pad_x * 2 + sz * 0.84 + gap + tw)
                if bx + bw_btn > px0 + 842:
                    break
                fill_b = prim_bg if is_prim else btn_bg
                txt_b = (255, 255, 255) if is_prim else fg
                draw.rounded_rectangle(
                    (bx, ry, bx + bw_btn, ry + btn_h),
                    radius=max(6, int(sz * 0.42)),
                    fill=fill_b,
                    outline=prim_bg if is_prim else btn_brd,
                    width=1,
                )
                y_base = ry + btn_h / 2.0 + 0.35 * sz
                s_rend.draw_glyph_run(img, bx + pad_x, y_base, by_name[sym_name], sz, txt_b)
                t_rend.draw_text(img, bx + pad_x + sz * 0.84 + gap, y_base, lbl_txt, sz, txt_b)
                bx += bw_btn + 12
            ry += int(sz * 1.92) + 16

        # 3-Weight side-by-side stroke harmony row @18px
        draw.line((px0 + 20, ry + 8, px0 + 840, ry + 8), fill=(46, 52, 64) if is_dark else (222, 218, 208), width=1)
        draw.text((px0 + 20, ry + 20), "3-WEIGHT SYMBOL + LABEL STROKE HARMONY @18px (Regular 2.0u -> Medium 2.35u -> Bold 2.75u):", fill=sub, font=ui_micro)
        h_ry = ry + 48
        bx = px0 + 20
        for h_lbl, h_sym, h_key in (
            ("Regular 400 (2.0u)", "settings", "r"),
            ("Medium 500 (2.35u)", "settings", "m"),
            ("Bold 700 (2.75u)", "settings", "b"),
        ):
            sz_h = 18
            tw_h = f[f"sans_{h_key}"].measure_text(h_lbl, sz_h)
            bw_h = int(28 + sz_h * 0.84 + 8 + tw_h)
            bh_h = 38
            draw.rounded_rectangle((bx, h_ry, bx + bw_h, h_ry + bh_h), radius=9, fill=btn_bg, outline=btn_brd, width=1)
            yb_h = h_ry + bh_h / 2.0 + 0.35 * sz_h
            f[f"sym_{h_key}"].draw_glyph_run(img, bx + 14, yb_h, by_name[h_sym], sz_h, fg)
            f[f"sans_{h_key}"].draw_text(img, bx + 14 + sz_h * 0.84 + 8, yb_h, h_lbl, sz_h, fg)
            bx += bw_h + 14

    # Panel 3: Dual-Theme Section 16 Hierarchy Chat UI
    draw.rounded_rectangle((46, 1160, 1874, 1880), radius=14, fill=(255, 255, 255), outline=(224, 222, 214), width=2)
    draw.text(
        (74, 1178),
        "3. PERSONAL AGENT CHAT UI — SECTION 16 FULL TYPOGRAPHIC ROLES (REG BODY · MED LABELS/BUTTONS · BOLD HEADINGS · ITALIC QUOTES/TITLES)",
        fill=(70, 76, 88),
        font=ui_lbl,
    )

    for is_dark, px0 in ((False, 74), (True, 986)):
        p_bg = (244, 243, 238) if not is_dark else (18, 20, 25)
        u_bg = (224, 235, 250) if not is_dark else (38, 48, 66)
        a_bg = (255, 255, 255) if not is_dark else (27, 31, 39)
        fg = (18, 22, 28) if not is_dark else (236, 240, 246)
        muted = (92, 100, 114) if not is_dark else (148, 156, 170)
        quote_fg = (56, 68, 86) if not is_dark else (186, 200, 220)
        brd = (218, 216, 208) if not is_dark else (48, 54, 68)

        draw.rounded_rectangle((px0, 1210, px0 + 860, 1858), radius=14, fill=p_bg, outline=brd, width=2)
        draw.text((px0 + 20, 1226), f"{'DARK THEME' if is_dark else 'LIGHT THEME'}  ·  USER = SANS  ·  AGENT = SERIF  ·  BUTTONS = MEDIUM 500", fill=muted, font=ui_micro)

        # User bubble
        ux0, uy0, uw, uh = px0 + 180, 1254, 656, 98
        draw.rounded_rectangle((ux0, uy0, ux0 + uw, uy0 + uh), radius=14, fill=u_bg)
        f["sans_m"].draw_text(img, ux0 + 20, uy0 + 24, "USER PROMPT  ·  12px MEDIUM 500", 12, muted)
        _draw_mixed_line(img, ux0 + 20, uy0 + 54, [
            (f["sans_r"], "Review ", None),
            (f["sans_ri"], "Letters of Credit", None),
            (f["sans_r"], " notes and check Q3 EUR ", None),
            (f["sans_b"], "$1,480.95", {"tnum": True}),
            (f["sans_r"], ".", None),
        ], 16, fg)
        f["sans_r"].draw_text(img, ux0 + 20, uy0 + 78, "Also verify Voix ambiguë d’un cœur & CX801 schedule.", 16, fg)

        # Agent card
        ax0, ay0, aw, ah = px0 + 24, 1372, 780, 464
        draw.rounded_rectangle((ax0, ay0, ax0 + aw, ay0 + ah), radius=14, fill=a_bg, outline=brd, width=1)
        f["serif_b"].draw_text(img, ax0 + 22, ay0 + 36, "Quarterly Typography & Settlement Brief", 21, fg)
        f["sans_m"].draw_text(img, ax0 + 22, ay0 + 58, "Verified with Admiralty Symbols Medium 500 · Zero Reflow", 12, muted)

        # Literary quote in Serif Italic + Medium Italic
        q_bg = (247, 246, 241) if not is_dark else (22, 26, 33)
        draw.rounded_rectangle((ax0 + 22, ay0 + 74, ax0 + aw - 22, ay0 + 150), radius=8, fill=q_bg)
        draw.rectangle((ax0 + 22, ay0 + 74, ax0 + 26, ay0 + 150), fill=(74, 134, 232))
        _draw_mixed_line(img, ax0 + 40, ay0 + 104, [
            (f["serif_ri"], "“Typefaces for continuous reading thrive on open apertures — ", None),
            (f["serif_mi"], "Letters of Credit", None),
            (f["serif_ri"], ".”", None),
        ], 16, quote_fg)
        _draw_mixed_line(img, ax0 + 40, ay0 + 132, [
            (f["serif_ri"], "See also ", None),
            (f["serif_bi"], "The Elements of Typographic Style", None),
            (f["serif_ri"], " (§4.2 · Voix ambiguë).", None),
        ], 15, quote_fg)

        # Agent prose mixing Regular, Bold, Italic, Mono Italic
        _draw_mixed_line(img, ax0 + 22, ay0 + 186, [
            (f["serif_r"], "Net settlement finalized at ", None),
            (f["serif_b"], "€1,362,446.86", {"tnum": True}),
            (f["serif_r"], " (flight ", None),
            (f["mono_r"], "CX801", {"zero": True}),
            (f["serif_r"], " departs at ", None),
            (f["serif_b"], "09:30", {"tnum": True}),
            (f["serif_r"], ").", None),
        ], 16, fg)
        _draw_mixed_line(img, ax0 + 22, ay0 + 216, [
            (f["serif_r"], "All 6 styles match to ", None),
            (f["serif_mi"], "0.00 px", None),
            (f["serif_r"], " across ", None),
            (f["serif_bi"], "Admiralty Sans & Serif", None),
            (f["serif_r"], "!", None),
        ], 16, fg)

        # Code block using Mono Medium, Bold, Italic
        c_bg = (22, 25, 32) if not is_dark else (14, 16, 21)
        draw.rounded_rectangle((ax0 + 22, ay0 + 236, ax0 + aw - 22, ay0 + 368), radius=10, fill=c_bg)
        f["mono_ri"].draw_text(img, ax0 + 38, ay0 + 266, "// src/brief.ts · 600u column lock + ss01 slanted ligatures", 14, (132, 148, 174), {"ss01": True, "zero": True})
        _draw_mixed_line(img, ax0 + 38, ay0 + 298, [
            (f["mono_b"], "export const ", {"ss01": True, "zero": True}),
            (f["mono_m"], "settle ", {"ss01": True, "zero": True}),
            (f["mono_r"], "= (usd: ", {"ss01": True, "zero": True}),
            (f["mono_ri"], "number", {"ss01": True, "zero": True}),
            (f["mono_r"], ") => usd * 0.92;", {"ss01": True, "zero": True}),
        ], 14, (230, 236, 245))
        _draw_mixed_line(img, ax0 + 38, ay0 + 330, [
            (f["mono_b"], "if ", {"ss01": True, "zero": True}),
            (f["mono_r"], "(delta != 0 && rate <= 1.0) -> sync(); ", {"ss01": True, "zero": True}),
            (f["mono_mi"], "// checked", {"ss01": True, "zero": True}),
        ], 14, (176, 206, 248))

        # Action Bar with Medium 500 text + Symbols Medium
        bx = ax0 + 22
        by = ay0 + 394
        actions = [
            ("Copy Note", "copy", False),
            ("Regenerate", "regenerate", False),
            ("Share Brief", "share", False),
            ("Verified", "shield-check", True),
        ]
        for albl, asym, prim in actions:
            bw = int(24 + 14 * 0.84 + 6 + f["sans_m"].measure_text(albl, 13))
            bh = 34
            abg = (74, 134, 232) if prim and is_dark else ((24, 30, 40) if prim else a_bg)
            afg = (255, 255, 255) if prim else fg
            abrd = abg if prim else brd
            draw.rounded_rectangle((bx, by, bx + bw, by + bh), radius=8, fill=abg, outline=abrd, width=1)
            yb = by + bh / 2.0 + 0.35 * 14
            f["sym_m"].draw_glyph_run(img, bx + 11, yb, by_name[asym], 14, afg)
            f["sans_m"].draw_text(img, bx + 11 + 14 * 0.84 + 6, yb, albl, 13, afg)
            bx += bw + 10

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out_path))
    print(f"Saved {out_path} ({W}x{H})")


def render_mono_ide_proof(f: Dict[str, DirHBRenderer], out_path: Path) -> None:
    W, H = 1920, 1620
    img = Image.new("RGB", (W, H), (247, 246, 241))
    draw = ImageDraw.Draw(img)
    ui_title = get_ui_label_font(17)
    ui_lbl = get_ui_label_font(13)
    ui_micro = get_ui_label_font(11)

    draw.rectangle((0, 0, W, 82), fill=(22, 25, 31))
    draw.text(
        (54, 20),
        "ADMIRALTY MONO (v0.130)  ·  6-STYLE SYNTAX HIGHLIGHTING, 80-COL LOCK & SLANTED ss01 LIGATURE SEAM AUDIT",
        fill=(244, 246, 250),
        font=ui_title,
    )
    draw.text(
        (54, 48),
        "Every style (Regular, Medium, Bold, Italic, Medium Italic, Bold Italic) locked to strict 600u fixed advance width  |  Zero column drift across styling",
        fill=(162, 170, 184),
        font=ui_lbl,
    )

    # Panel 1: Dark Mode 80-col Code Editor mixing all 6 Mono styles
    draw.rounded_rectangle((46, 102, 1874, 924), radius=14, fill=(19, 22, 28), outline=(44, 50, 62), width=2)
    draw.text((74, 120), "1. DARK MODE IDE — 80-COLUMN ALIGNMENT ACROSS ALL 6 MONO STYLES (Reg / Med / Bold / It / MedIt / BoldIt, ss01=1, zero=1)", fill=(158, 168, 186), font=ui_lbl)

    cx0 = 110
    sz = 19
    col_px = sz * 0.6
    # Column grid lines at 10, 20, 40, 60, 80
    for col in (0, 20, 40, 60, 80):
        gx = cx0 + col * col_px
        draw.line((gx, 160, gx, 892), fill=(36, 44, 58) if col not in (0, 80) else (62, 84, 118), width=1 if col not in (0, 80) else 2)
        draw.text((gx + 4, 158), f"col {col}", fill=(92, 114, 146), font=ui_micro)

    code_lines_raw = [
        [(f["mono_mi"], "/// Agent tool executor — strict 600u cell lock (0..80 columns)", (130, 152, 182))],
        [(f["mono_b"], "pub fn ", (244, 146, 112)), (f["mono_m"], "run_step", (128, 200, 255)), (f["mono_r"], "<T>(id: &", (222, 228, 238)), (f["mono_ri"], "str", (174, 222, 162)), (f["mono_r"], ", x: i32, y: i32) -> ", (222, 228, 238)), (f["mono_m"], "Result", (128, 200, 255)), (f["mono_r"], "<T> {", (222, 228, 238))],
        [(f["mono_r"], "    ", (222, 228, 238)), (f["mono_b"], "let ", (244, 146, 112)), (f["mono_m"], "ok ", (222, 228, 238)), (f["mono_r"], "= x != 0 && x <= y && y >= 100; ", (222, 228, 238)), (f["mono_ri"], "// Il1| O0o anti-confusable", (124, 138, 160))],
        [(f["mono_r"], "    ", (222, 228, 238)), (f["mono_b"], "let ", (244, 146, 112)), (f["mono_r"], "token = ", (222, 228, 238)), (f["mono_ri"], "\"ID-1lI-O08\"", (174, 222, 162)), (f["mono_r"], "; ", (222, 228, 238)), (f["mono_bi"], "// TODO: => -> <- != == <= >=", (242, 198, 108))],
        [(f["mono_r"], "    ", (222, 228, 238)), (f["mono_b"], "match ", (244, 146, 112)), (f["mono_r"], "route(id) {", (222, 228, 238))],
        [(f["mono_r"], "        ", (222, 228, 238)), (f["mono_m"], "State", (128, 200, 255)), (f["mono_r"], "::Active => x -> y, ", (222, 228, 238)), (f["mono_ri"], "// slanted/upright continuous arrows", (124, 138, 160))],
        [(f["mono_r"], "        ", (222, 228, 238)), (f["mono_m"], "State", (128, 200, 255)), (f["mono_r"], "::Paused => y <- x, ", (222, 228, 238)), (f["mono_mi"], "// Medium Italic documentation comment", (146, 178, 206))],
        [(f["mono_r"], "        _            => ", (222, 228, 238)), (f["mono_b"], "return ", (244, 146, 112)), (f["mono_m"], "Err", (246, 128, 128)), (f["mono_r"], "(", (222, 228, 238)), (f["mono_ri"], "\"reflow\"", (174, 222, 162)), (f["mono_r"], "),", (222, 228, 238))],
        [(f["mono_r"], "    }", (222, 228, 238))],
        [(f["mono_r"], "}", (222, 228, 238))],
        [(f["mono_mi"], "// Ruler 80 columns: 1234567890123456789012345678901234567890123456789012345678", (112, 126, 148))],
    ]
    ry = 212
    feats = {"ss01": True, "zero": True}
    for ln_no, segs in enumerate(code_lines_raw, start=1):
        char_len = sum(len(t) for _, t, _ in segs)
        pad = " " * max(0, 79 - char_len) + "|"
        full_segs = segs + [(f["mono_r"], pad, (108, 134, 168))]
        f["mono_r"].draw_text(img, 70, ry, f"{ln_no:2d}", 15, (86, 98, 118), {"zero": True})
        cx = float(cx0)
        for rend, txt, col in full_segs:
            cx = rend.draw_text(img, cx, ry, txt, sz, col, feats)
        assert abs(cx - (cx0 + 80 * col_px)) < 0.05, f"Line {ln_no} col drift: {cx} vs {cx0 + 80 * col_px}"
        ry += 38

    draw.text((110, 646), "LIVE 80-COL HARFBUZZ ADVANCE AUDIT: Regular=48000u · Medium=48000u · Bold=48000u · Italic=48000u · MedItalic=48000u · BoldItalic=48000u", fill=(104, 212, 148), font=ui_lbl)

    # Bottom inside Dark IDE card: Terminal output in all 6 Mono weights side by side
    ry = 700
    for lbl_m, m_rend, col_m in [
        ("Mono Regular (400)", f["mono_r"], (218, 226, 238)),
        ("Mono Medium  (500)", f["mono_m"], (164, 214, 255)),
        ("Mono Bold    (700)", f["mono_b"], (255, 220, 148)),
        ("Mono Italic  (400)", f["mono_ri"], (174, 224, 178)),
        ("Mono MedItal (500)", f["mono_mi"], (188, 182, 255)),
        ("Mono BoldIt  (700)", f["mono_bi"], (255, 168, 168)),
    ]:
        draw.text((110, ry - 14), lbl_m, fill=(132, 142, 162), font=ui_micro)
        m_rend.draw_text(img, 265, ry, "const ok = (x: Il1_O0) => x != 0 && x <= y ? x -> y : y <- x;  $1,480.95", 16, col_m, feats)
        ry += 32

    # Panel 2: Light Mode Telemetry Log & 44px ss01 Seam Zoom
    draw.rounded_rectangle((46, 944, 1874, 1584), radius=14, fill=(255, 255, 255), outline=(224, 222, 214), width=2)
    draw.text((74, 962), "2. LIGHT MODE ALIGNED TELEMETRY TABLE & 44px SLANTED / UPRIGHT ss01 LIGATURE SEAM AUDIT", fill=(70, 76, 88), font=ui_lbl)

    # Left half: Light Mode diff & financial table
    lx = 74
    draw.rounded_rectangle((lx, 996, lx + 860, 1554), radius=12, fill=(250, 249, 245), outline=(222, 218, 208), width=2)
    draw.text((lx + 20, 1012), "LIGHT MODE TABULAR CODE & DIFF LOG (zero=1 · ss01=1)", fill=(92, 98, 112), font=ui_micro)
    diff_rows = [
        (f["mono_b"],  "  STYLE          ID       RATE     STATUS    CHECK", (22, 26, 34)),
        (f["mono_r"],  "  Regular 400    Il1_O0   0.9200   READY     a -> b  x == 0", (30, 36, 46)),
        (f["mono_m"],  "  Medium  500    Il1_O0   0.9200   BUTTON    a -> b  x != 0", (20, 76, 136)),
        (f["mono_b"],  "+ Bold    700    Il1_O0   1.0450   COMMIT    x <= y  y >= x", (20, 118, 62)),
        (f["mono_ri"], "- Italic  400    Il1_O0   0.8950   COMMENT   a => b  x <- y", (164, 46, 46)),
        (f["mono_mi"], "  MedItal 500    Il1_O0   0.9200   DOC-STR   (a != b) -> ok", (98, 56, 148)),
        (f["mono_bi"], "! BoldIt  700    Il1_O0   9.9999   ALERT     fn => x === 0!", (158, 86, 18)),
    ]
    ry = 1068
    for rend_d, line_d, col_d in diff_rows:
        rend_d.draw_text(img, lx + 24, ry, line_d, 16, col_d, feats)
        ry += 38

    draw.text((lx + 24, 1356), "Pinyin, German & Cursive Ligatures in 600u Mono Italic:", fill=(92, 98, 112), font=ui_micro)
    f["mono_ri"].draw_text(img, lx + 24, 1404, "a f g i l æ œ ß ẞ  nǐ hǎo ǖ ǘ ǚ ǜ  Zażółć", 22, (24, 28, 36), feats)
    f["mono_mi"].draw_text(img, lx + 24, 1456, "a f g i l æ œ ß ẞ  nǐ hǎo ǖ ǘ ǚ ǜ  Zażółć", 22, (24, 68, 118), feats)
    f["mono_bi"].draw_text(img, lx + 24, 1508, "a f g i l æ œ ß ẞ  nǐ hǎo ǖ ǘ ǚ ǜ  Zażółć", 22, (20, 24, 30), feats)

    # Right half: 44px ss01 Seam Microscope (600u cell grid behind ligatures)
    rx = 986
    draw.rounded_rectangle((rx, 996, rx + 860, 1554), radius=12, fill=(246, 248, 252), outline=(208, 218, 232), width=2)
    draw.text((rx + 20, 1012), "44px ss01 LIGATURE SEAM AUDIT (vertical ticks = exact 600u cell boundaries)", fill=(64, 78, 98), font=ui_micro)

    lig_str = "=>  ->  <-  !=  ==  <=  >="
    cell_px = 42 * 0.6
    gx0 = rx + 26
    for k in range(len(lig_str) + 1):
        cx_g = gx0 + k * cell_px
        draw.line((cx_g, 1054, cx_g, 1532), fill=(212, 224, 242), width=1)

    zoom_rows = [
        ("Reg 400", f["mono_r"], (24, 28, 36)),
        ("Med 500", f["mono_m"], (24, 68, 118)),
        ("Bld 700", f["mono_b"], (18, 22, 28)),
        ("Ital 400", f["mono_ri"], (118, 42, 42)),
        ("MedIt 500", f["mono_mi"], (72, 48, 136)),
        ("BldIt 700", f["mono_bi"], (18, 96, 62)),
    ]
    ry = 1106
    for zlbl, zrend, zcol in zoom_rows:
        zrend.draw_text(img, gx0, ry, lig_str, 42, zcol, feats)
        draw.text((gx0 + 690, ry - 20), zlbl, fill=(92, 100, 114), font=ui_lbl)
        ry += 78

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out_path))
    print(f"Saved {out_path} ({W}x{H})")


if __name__ == "__main__":
    fonts = _load_fonts()
    spec_dir = ROOT / "specimens"
    render_weights_and_italics(fonts, spec_dir / "milestone7_weights_and_italics.png")
    render_duplex_and_roles(fonts, spec_dir / "milestone7_duplex_and_roles.png")
    render_mono_ide_proof(fonts, spec_dir / "milestone7_mono_ide_proof.png")
