"""
Milestone 4 Specimen Renderer for Admiralty Serif Regular + Duplex Pairing with
Admiralty Sans Regular:
  1. milestone4_serif_overview.png  — Full character set, features & disambiguation
  2. milestone4_duplex_proof.png    — Ghost skeleton overlay & 0.00px reflow registration
  3. milestone4_chat_paired.png     — Light & Dark Agent/User chat bubbles + Role Swap + CJK
"""

from __future__ import annotations
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from render_specimen import HBFreeTypeRenderer, get_ui_label_font


def _find_cjk_fonts() -> tuple[tuple[Path, int] | None, tuple[Path, int] | None]:
    sans_cjk = None
    for p in Path("/System/Library/AssetsV2").rglob("PingFang.ttc"):
        sans_cjk = (p, 0)  # PingFang HK Regular
        break
    if sans_cjk is None:
        p_hira = Path("/System/Library/Fonts/Hiragino Sans GB.ttc")
        if p_hira.exists():
            sans_cjk = (p_hira, 0)
    p_song = Path("/System/Library/Fonts/Supplemental/Songti.ttc")
    serif_cjk = (p_song, 7) if p_song.exists() else sans_cjk  # Songti TC Regular
    return sans_cjk, serif_cjk


def draw_mixed_cjk_line(
    img: Image.Image,
    x: float,
    y_baseline: float,
    text: str,
    px_size: float,
    latin_renderer: HBFreeTypeRenderer,
    cjk_spec: tuple[Path, int] | None,
    color: tuple[int, int, int],
) -> float:
    """Draws Latin runs with Admiralty (HarfBuzz+FreeType) and CJK runs with system CJK font."""
    cjk_pil = (
        ImageFont.truetype(str(cjk_spec[0]), int(round(px_size * 0.94)), index=cjk_spec[1])
        if cjk_spec is not None
        else get_ui_label_font(int(round(px_size)))
    )
    draw = ImageDraw.Draw(img)
    cur_x = x

    # Group contiguous ASCII/Latin-ext vs CJK characters
    runs: list[tuple[bool, str]] = []
    for ch in text:
        is_cjk = ord(ch) >= 0x2E80
        if runs and runs[-1][0] == is_cjk:
            runs[-1] = (is_cjk, runs[-1][1] + ch)
        else:
            runs.append((is_cjk, ch))

    for is_cjk, chunk in runs:
        if not is_cjk:
            cur_x = latin_renderer.draw_text(img, cur_x, y_baseline, chunk, px_size, color)
            draw = ImageDraw.Draw(img)  # refresh after numpy writeback
        else:
            # Anchor 'ls' places text directly on baseline in Pillow >= 8
            draw.text((cur_x, y_baseline), chunk, fill=color, font=cjk_pil, anchor="ls")
            cur_x += draw.textlength(chunk, font=cjk_pil)
    return cur_x


def render_serif_overview(serif: HBFreeTypeRenderer, out_path: Path) -> None:
    w, h = 1860, 1340
    img = Image.new("RGB", (w, h), (250, 249, 245))
    draw = ImageDraw.Draw(img)
    ui_title = get_ui_label_font(18)
    ui_small = get_ui_label_font(14)

    draw.text(
        (72, 48),
        "ADMIRALTY SERIF REGULAR (400)  ·  MILESTONE 4 FULL SPECIMEN  ·  466 GLYPHS · v0.110  ·  1:1 DUPLEXED WITH SANS",
        fill=(96, 102, 114),
        font=ui_title,
    )
    draw.line([(72, 86), (w - 72, 86)], fill=(224, 221, 214), width=2)

    y = 166
    serif.draw_text(
        img, 72, y,
        "Calm, literary clarity for your Personal Agent.",
        68, (18, 21, 27),
    )

    y += 66
    draw = ImageDraw.Draw(img)
    draw.text((72, y), "Uppercase, Lowercase & Proportional / Tabular / Slashed Figures", fill=(124, 128, 138), font=ui_small)
    y += 74
    serif.draw_text(img, 72, y, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", 54, (20, 23, 29))
    y += 76
    serif.draw_text(img, 72, y, "abcdefghijklmnopqrstuvwxyz", 56, (20, 23, 29))
    y += 74
    x_end = serif.draw_text(img, 72, y, "0123456789   $ ¢ € £ ¥   ", 48, (24, 28, 35))
    x_end = serif.draw_text(img, x_end, y, "0123456789 (tnum+zero)", 44, (44, 78, 126), features={"tnum": True, "zero": True})

    y += 52
    draw = ImageDraw.Draw(img)
    draw.line([(72, y), (w - 72, y)], fill=(228, 225, 218), width=1)
    y += 24
    draw.text((72, y), "13 px – 48 px Disambiguation & Spacing Harmony (Il1 · O0 · rn vs m · cl vs d · fi fl fj)", fill=(124, 128, 138), font=ui_small)
    y += 64
    serif.draw_text(
        img, 72, y,
        "Il1  |lI1!   O0  O0Q   rn m   cl d   vv w   fi fl fj   ‘quote’ “double” 'straight' `grave`",
        44, (20, 23, 29),
    )

    y += 52
    draw = ImageDraw.Draw(img)
    draw.line([(72, y), (w - 72, y)], fill=(228, 225, 218), width=1)
    y += 24
    draw.text((72, y), "Pan-European GF Latin Core Diacritics, Ligatures, Fractions & Symbols", fill=(124, 128, 138), font=ui_small)
    y += 62
    serif.draw_text(
        img, 72, y,
        "Æther & Œuvre · Voix ambiguë d’un cœur · Straße · Zażółć gęślą jaźń · Čeština ďťľň",
        38, (22, 25, 31),
    )
    y += 58
    serif.draw_text(
        img, 72, y,
        "Þór & Ægir (Ísland) · Blåbærsyltetøy fra Tromsø · Łódź & Gdańsk · Sâme Ŋŋ Ħħ Đđ",
        38, (22, 25, 31),
    )
    y += 58
    serif.draw_text(
        img, 72, y,
        "Section §4.2 · ¶9 · © 2026 Admiralty™ · 1ª 2º · x¹ m² cm³ · ¼ ½ ¾ · ← ↑ → ↓ ↗ ↘ ↩",
        38, (22, 25, 31),
    )

    y += 52
    draw = ImageDraw.Draw(img)
    draw.line([(72, y), (w - 72, y)], fill=(228, 225, 218), width=1)
    y += 24
    draw.text((72, y), "Mobile & Desktop Reading Waterfall (12 px, 14 px, 16 px, 18 px, 24 px @ 2x Retina)", fill=(124, 128, 138), font=ui_small)
    y += 28
    sample = "A calm assistant formats figures ($1,480.95) cleanly and never shifts layout."
    for pt in (12, 14, 16, 18, 22):
        px = pt * 2.0
        draw = ImageDraw.Draw(img)
        y += int(px * 0.98) + 12
        draw.text((72, y - int(px * 0.65)), f"{pt} px", fill=(140, 144, 154), font=ui_small)
        serif.draw_text(img, 148, y, sample, px, (20, 23, 29))

    img.save(out_path)
    print(f"Rendered Serif overview -> {out_path}")


def render_duplex_proof(
    sans: HBFreeTypeRenderer, serif: HBFreeTypeRenderer, out_path: Path
) -> None:
    w, h = 1860, 1280
    img = Image.new("RGB", (w, h), (250, 249, 245))
    draw = ImageDraw.Draw(img)
    ui_title = get_ui_label_font(18)
    ui_small = get_ui_label_font(14)

    draw.text(
        (72, 48),
        "SHARED SKELETON & ZERO-REFLOW DUPLEX AUDIT  ·  ADMIRALTY SANS ↔ ADMIRALTY SERIF",
        fill=(96, 102, 114),
        font=ui_title,
    )
    draw.line([(72, 86), (w - 72, 86)], fill=(224, 221, 214), width=2)

    # Section 1: High-zoom Ghost Skeleton Overlay (cyan-blue Sans behind deep ink Serif)
    draw.text(
        (72, 108),
        "1. Shared Humanist Skeleton Overlay (Cyan = Admiralty Sans Ghost · Ink = Admiralty Serif)",
        fill=(118, 124, 136),
        font=ui_small,
    )
    showcase = list("HagenRSl2&")
    cell_w = 168
    for idx, ch in enumerate(showcase):
        cx0 = 72 + idx * cell_w
        cy0 = 144
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([cx0, cy0, cx0 + cell_w - 12, cy0 + 226], radius=12, fill=(255, 255, 255), outline=(228, 226, 218))
        yb = cy0 + 174
        adv = sans.measure_text(ch, 154)
        gx = cx0 + (cell_w - 12 - adv) / 2.0
        for yu, col in [(0, (232, 200, 200)), (520, (208, 220, 236)), (700, (220, 220, 220))]:
            yy = int(round(yb - yu * 0.154))
            draw.line([(cx0 + 10, yy), (cx0 + cell_w - 22, yy)], fill=col, width=1)

        # Render Sans on separate layer and composite at 38% opacity in cyan-blue, then Serif on top at 82%
        layer_sans = Image.new("RGB", img.size, (255, 255, 255))
        sans.draw_text(layer_sans, gx, yb, ch, 154, (36, 132, 218))
        layer_serif = Image.new("RGB", img.size, (255, 255, 255))
        serif.draw_text(layer_serif, gx, yb, ch, 154, (18, 22, 28))

        base_arr = np.asarray(img, dtype=np.float32)
        s_mask = 1.0 - (np.asarray(layer_sans, dtype=np.float32).mean(axis=2, keepdims=True) / 255.0)
        # Re-probe alpha from white background
        s_alpha = np.clip((255.0 - np.asarray(layer_sans, dtype=np.float32)[:, :, 0:1]) / (255.0 - 36.0), 0.0, 1.0)
        r_alpha = np.clip((255.0 - np.asarray(layer_serif, dtype=np.float32)[:, :, 0:1]) / (255.0 - 18.0), 0.0, 1.0)

        cyan = np.array([42.0, 148.0, 235.0], dtype=np.float32)
        ink = np.array([18.0, 22.0, 29.0], dtype=np.float32)
        sub_y0, sub_y1 = cy0, cy0 + 226
        sub_x0, sub_x1 = cx0, cx0 + cell_w - 12
        patch = base_arr[sub_y0:sub_y1, sub_x0:sub_x1]
        sa = s_alpha[sub_y0:sub_y1, sub_x0:sub_x1] * 0.42
        ra = r_alpha[sub_y0:sub_y1, sub_x0:sub_x1] * 0.84
        patch = patch * (1.0 - sa) + cyan * sa
        patch = patch * (1.0 - ra) + ink * ra
        base_arr[sub_y0:sub_y1, sub_x0:sub_x1] = patch
        img.paste(Image.fromarray(np.clip(base_arr, 0, 255).astype(np.uint8)))

    # Section 2: Stacked Sans vs Serif Zero-Reflow Registration Lines
    draw = ImageDraw.Draw(img)
    y = 404
    draw.text(
        (72, y),
        "2. 1:1 Duplexed Advance Width & Class Kerning Registration (Δwidth = 0.00 px across every word & character)",
        fill=(118, 124, 136),
        font=ui_small,
    )
    y += 38

    reg_runs = [
        ("Admiralty Personal Agent — Zero Layout Reflow (2026)", 48),
        ("WAVEY To Va Yo Ti LT P. F, “Hello, world!” $1,480.95 €290 £75 ¥3,600", 38),
        ("Voix ambiguë d’un cœur · Zażółć gęślą jaźń · Čeština ďťľ · Tromsø & Þór (Ísland)", 34),
        ("Tabellen & Zahlen (tnum+zero):  0123456789   $98,765.43   ±0.00%   ← ↑ → ↓ ↩", 34),
    ]

    for idx_r, (txt, px) in enumerate(reg_runs):
        feats = {"tnum": True, "zero": True} if idx_r == 3 else None
        w_sans = sans.measure_text(txt, px, feats)
        w_serif = serif.measure_text(txt, px, feats)
        assert abs(w_sans - w_serif) < 1e-4, f"Mismatch: {w_sans} vs {w_serif}"

        draw = ImageDraw.Draw(img)
        box_h = int(px * 2.75) + 28
        draw.rounded_rectangle([72, y, w - 72, y + box_h], radius=14, fill=(255, 255, 255), outline=(230, 228, 220))

        x_start = 168.0
        yb1 = y + int(px * 1.08) + 6
        yb2 = yb1 + int(px * 1.28)

        # Draw vertical registration hairlines at every word boundary!
        words = txt.split(" ")
        probe = ""
        for wi, wd in enumerate(words):
            probe = wd if wi == 0 else probe + " " + wd
            wx = int(round(x_start + sans.measure_text(probe, px, feats)))
            draw.line([(wx, y + 10), (wx, y + box_h - 10)], fill=(232, 238, 246), width=1)
        draw.line([(int(x_start), y + 10), (int(x_start), y + box_h - 10)], fill=(210, 175, 175), width=1)
        end_x = int(round(x_start + w_sans))
        draw.line([(end_x, y + 10), (end_x, y + box_h - 10)], fill=(210, 175, 175), width=1)

        draw.text((92, yb1 - int(px * 0.55)), "SANS", fill=(86, 126, 178), font=ui_small)
        draw.text((92, yb2 - int(px * 0.55)), "SERIF", fill=(138, 98, 62), font=ui_small)
        draw.text(
            (w - 390, y + 12),
            f"Sans = {w_sans:.2f}px | Serif = {w_serif:.2f}px",
            fill=(44, 128, 86),
            font=ui_small,
        )

        sans.draw_text(img, x_start, yb1, txt, px, (68, 76, 90), feats)
        serif.draw_text(img, x_start, yb2, txt, px, (18, 21, 27), feats)
        y += box_h + 18

    img.save(out_path)
    print(f"Rendered Duplex Zero-Reflow proof -> {out_path}")


def render_paired_chat_and_cjk(
    sans: HBFreeTypeRenderer, serif: HBFreeTypeRenderer, out_path: Path
) -> None:
    w, h = 1860, 1400
    img = Image.new("RGB", (w, h), (235, 234, 228))
    draw = ImageDraw.Draw(img)
    ui_title = get_ui_label_font(16)
    ui_small = get_ui_label_font(13)

    sans_cjk, serif_cjk = _find_cjk_fonts()

    # Left panel: Light Mode (Default: Serif = Agent, Sans = User)
    # Right panel: Dark Mode (Swapped: Sans = Agent, Serif = User — proving zero reflow!)
    draw.rounded_rectangle([32, 32, 914, h - 32], radius=24, fill=(250, 249, 245))
    draw.rounded_rectangle([946, 32, w - 32, h - 32], radius=24, fill=(18, 20, 25))

    draw.text(
        (68, 62),
        "LIGHT MODE  ·  DEFAULT ROLES (Agent = Serif · User = Sans)",
        fill=(94, 100, 112),
        font=ui_title,
    )
    draw.text(
        (982, 62),
        "DARK MODE  ·  SWAPPED ROLES (Agent = Sans · User = Serif) · 0px REFLOW",
        fill=(152, 160, 174),
        font=ui_title,
    )

    dialogue = [
        ("user", "↩ Summarize Q3 revenue & draft a calm note to Søren in Zürich."),
        (
            "agent",
            "Q3 net revenue reached $1,480,920.50 (+14.2% YoY), driven by European "
            "subscriptions in Zürich, München, and København. Operating margin held "
            "steady at 28.5% (±0.2%).\n"
            "Draft for Søren: “Hi Søren — Q3 closed cleanly ahead of plan. Let’s review "
            "the 2027 roadmap on Thursday at 10:30.”",
        ),
        ("user", "Looks great! Convert $1,480,920.50 to EUR at 0.92 and pin it →"),
        (
            "agent",
            "Pinned to Q3 Board ↗ — €1,362,446.86 at 0.9200 EUR/USD (ref #A1-I0-l9).",
        ),
    ]

    px = 30.0  # 15px @ 2x Retina
    lh = 44

    configs = [
        # (x_base, is_dark, user_font, agent_font, user_lbl, agent_lbl)
        (68, False, sans, serif, "USER · Admiralty Sans", "AGENT · Admiralty Serif"),
        (982, True, serif, sans, "USER · Admiralty Serif (Swapped)", "AGENT · Admiralty Sans (Swapped)"),
    ]

    recorded_heights: list[list[int]] = []

    for x_base, is_dark, u_font, a_font, u_lbl, a_lbl in configs:
        fg = (236, 238, 244) if is_dark else (20, 23, 29)
        muted = (124, 130, 144) if is_dark else (120, 125, 136)
        b_user = (38, 46, 60) if is_dark else (229, 236, 246)
        b_agent = (27, 30, 37) if is_dark else (255, 255, 255)
        b_border = (48, 53, 64) if is_dark else (224, 221, 214)

        y = 112
        panel_right = x_base + 810
        heights_this_panel: list[int] = []

        for role, msg in dialogue:
            draw = ImageDraw.Draw(img)
            fnt = u_font if role == "user" else a_font
            lbl = u_lbl if role == "user" else a_lbl

            if role == "user":
                lines = fnt.wrap_lines(msg, px, 640)
                bw = int(max(fnt.measure_text(ln, px) for ln in lines) + 52)
                bh = 32 + len(lines) * lh
                bx0 = panel_right - bw
                draw.text((bx0, y), lbl, fill=muted, font=ui_small)
                y += 22
                draw.rounded_rectangle([bx0, y, panel_right, y + bh], radius=20, fill=b_user)
                ty = y + 40
                for ln in lines:
                    fnt.draw_text(img, bx0 + 26, ty, ln, px, fg)
                    ty += lh
                y += bh + 22
                heights_this_panel.append(bh)
            else:
                all_lines: list[str] = []
                for para in msg.split("\n"):
                    all_lines.extend(fnt.wrap_lines(para, px, 708))
                bh = 36 + len(all_lines) * lh
                draw.text((x_base + 4, y), lbl, fill=muted, font=ui_small)
                y += 22
                draw.rounded_rectangle(
                    [x_base, y, x_base + 764, y + bh],
                    radius=20,
                    fill=b_agent,
                    outline=b_border,
                    width=1,
                )
                ty = y + 42
                for ln in all_lines:
                    fnt.draw_text(img, x_base + 28, ty, ln, px, fg)
                    ty += lh
                y += bh + 24
                heights_this_panel.append(bh)

        recorded_heights.append(heights_this_panel)

        # Mixed English + Traditional Chinese Fallback Card at bottom of each panel (Section 11)
        draw = ImageDraw.Draw(img)
        y += 8
        draw.line([(x_base, y), (panel_right, y)], fill=b_border, width=1)
        y += 18
        draw.text(
            (x_base, y),
            "Section 11 · Mixed English + Traditional Chinese Fallback Alignment (1000 UPM · 1.30x Line Box)",
            fill=muted,
            font=ui_small,
        )
        y += 28
        draw.rounded_rectangle(
            [x_base, y, panel_right, y + 186],
            radius=16,
            fill=b_agent,
            outline=b_border,
            width=1,
        )
        cjk_line_1 = "Admiralty 你好 Hello 世界 2026 · Sans + PingFang 繁體"
        cjk_line_2 = "Admiralty 你好 Hello 世界 2026 · Serif + Songti 書卷"
        yb_c1 = y + 66
        yb_c2 = y + 138
        # Draw baseline guides
        draw.line([(x_base + 24, yb_c1), (panel_right - 24, yb_c1)], fill=b_border, width=1)
        draw.line([(x_base + 24, yb_c2), (panel_right - 24, yb_c2)], fill=b_border, width=1)

        draw_mixed_cjk_line(img, x_base + 28, yb_c1, cjk_line_1, 30.0, sans, sans_cjk, fg)
        draw_mixed_cjk_line(img, x_base + 28, yb_c2, cjk_line_2, 30.0, serif, serif_cjk, fg)

    assert recorded_heights[0] == recorded_heights[1], (
        f"Bubble height reflow detected on role swap! {recorded_heights[0]} vs {recorded_heights[1]}"
    )
    print(f"Verified identical chat bubble heights on Sans↔Serif swap: {recorded_heights[0]} px")
    img.save(out_path)
    print(f"Rendered paired Chat + CJK proof -> {out_path}")


def main() -> None:
    spec_dir = ROOT / "specimens"
    spec_dir.mkdir(parents=True, exist_ok=True)
    sans = HBFreeTypeRenderer(ROOT / "fonts" / "ttf" / "AdmiraltySans-Regular.ttf")
    serif = HBFreeTypeRenderer(ROOT / "fonts" / "ttf" / "AdmiraltySerif-Regular.ttf")

    render_serif_overview(serif, spec_dir / "milestone4_serif_overview.png")
    render_duplex_proof(sans, serif, spec_dir / "milestone4_duplex_proof.png")
    render_paired_chat_and_cjk(sans, serif, spec_dir / "milestone4_chat_paired.png")


if __name__ == "__main__":
    main()
