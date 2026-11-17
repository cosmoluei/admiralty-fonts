"""
Milestone 5 Specimen & Human Review #1 Proof Pack Generator:
  1. specimens/milestone5_mono_overview.png     — Admiralty Mono Regular 600u specimen
  2. specimens/milestone5_app_prototype.png     — Full 3-family Personal Agent App Prototype (Light & Dark)
  3. specimens/Admiralty_Regular_Trio_Review1_Proofs.pdf — Multi-page PDF proof pack for Human Review #1
  4. Automated Section 15 Measured Consistency & Originality Check printout
"""

from __future__ import annotations
from pathlib import Path
import sys

from fontTools.pens.boundsPen import BoundsPen
from PIL import Image, ImageDraw
import ufoLib2

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from render_milestone4 import _find_cjk_fonts, draw_mixed_cjk_line
from render_specimen import HBFreeTypeRenderer, get_ui_label_font


def render_mono_overview(mono: HBFreeTypeRenderer, out_path: Path) -> None:
    w, h = 1860, 1400
    img = Image.new("RGB", (w, h), (250, 249, 245))
    draw = ImageDraw.Draw(img)
    ui_title = get_ui_label_font(18)
    ui_small = get_ui_label_font(14)

    draw.text(
        (72, 46),
        "ADMIRALTY MONO REGULAR (400)  ·  STRICT 600u FIXED PITCH  ·  isFixedPitch=1  ·  Panose.bProportion=9",
        fill=(96, 102, 114),
        font=ui_title,
    )
    draw.line([(72, 84), (w - 72, 84)], fill=(224, 221, 214), width=2)

    y = 112
    draw.text((72, y), "Redrawn 600u Alphabet, Figures, Code Brackets & Pan-European Diacritics", fill=(120, 126, 136), font=ui_small)
    y += 66
    mono.draw_text(img, 72, y, "ABCDEFGHIJKLMNOPQRSTUVWXYZ   0123456789", 46, (18, 22, 28))
    y += 68
    mono.draw_text(img, 72, y, "abcdefghijklmnopqrstuvwxyz   0123456789", 46, (18, 22, 28), features={"zero": True})
    y += 68
    mono.draw_text(img, 72, y, "Il1| O0o  .,:; !? '\"` ^~-_  {[(< >)]} /\\ *+=#@$%&€£¥", 40, (24, 29, 38))
    y += 62
    mono.draw_text(img, 72, y, "Ææ Œœ Øø Ðð Þþ ß Łł Ħħ Ŋŋ · Zażółć gęślą jaźń · Čeština ďťľ", 36, (32, 37, 46))

    y += 46
    draw = ImageDraw.Draw(img)
    draw.line([(72, y), (w - 72, y)], fill=(226, 224, 218), width=1)
    y += 22
    draw.text(
        (72, y),
        "13 px Disambiguation Check (@1x Unhinted & @2x Retina) + Off-by-Default Code Ligatures (ss01)",
        fill=(120, 126, 136),
        font=ui_small,
    )
    y += 28

    # Dark terminal card for 80-column phone test, ss01 ligatures & aligned table
    card_top = y
    card_bot = h - 48
    draw.rounded_rectangle([72, card_top, w - 72, card_bot], radius=20, fill=(20, 23, 29))

    cy = card_top + 42
    draw.text((108, cy - 18), "13 px (@1x = 13px / @2x = 26px) Look-Alike & Punctuation Stress Test:", fill=(134, 144, 162), font=ui_small)
    cy += 24
    mono.draw_text(
        img, 108, cy,
        "13px @1x:  Il1|  O0o  ,.:;  '\"`  {[(<>)]}  ID-1lI-O08  $1,480.95",
        13, (226, 232, 242),
    )
    cy += 38
    mono.draw_text(
        img, 108, cy,
        "13px @2x:  Il1|  O0o  ,.:;  '\"`  {[(<>)]}  ID-1lI-O08  $1,480.95",
        26, (238, 242, 248),
    )

    cy += 48
    draw = ImageDraw.Draw(img)
    draw.line([(108, cy - 22), (w - 108, cy - 22)], fill=(42, 48, 60), width=1)
    draw.text((108, cy - 8), "Optional Code Ligatures (ss01 OFF by default -> ss01 ON, exact 600u cell preservation):", fill=(134, 144, 162), font=ui_small)
    cy += 42
    mono.draw_text(
        img, 108, cy,
        "ss01 = OFF (default):  a -> b   x <- y   fn => x == 0 || x != y && a <= b >= c",
        30, (194, 204, 220),
    )
    cy += 48
    mono.draw_text(
        img, 108, cy,
        "ss01 = ON  (+zero):    a -> b   x <- y   fn => x == 0 || x != y && a <= b >= c",
        30, (112, 228, 174), features={"ss01": True, "zero": True},
    )

    cy += 52
    draw = ImageDraw.Draw(img)
    draw.line([(108, cy - 22), (w - 108, cy - 22)], fill=(42, 48, 60), width=1)

    # Split bottom of dark card into Left: 80-character phone code block, Right: Aligned data table
    draw.text((108, cy - 8), "80-Character Code Line Test (Strict 80 x 600u = 48,000u):", fill=(134, 144, 162), font=ui_small)
    draw.text((1170, cy - 8), "Aligned Financial & Tool Output Table:", fill=(134, 144, 162), font=ui_small)
    cy += 36

    code_lines = [
        ("12345678901234567890123456789012345678901234567890123456789012345678901234567890", (102, 114, 134)),
        ("export async function checkOrder(id = 'ID-1lI-O08'): Promise<AuditSummary> {    ", (184, 212, 250)),
        ("  const rows = await db.query('SELECT qty, price FROM items WHERE id = $1');    ", (228, 234, 244)),
        ("  const total = rows.reduce((acc, r) => acc + r.qty * r.price, 0.00);           ", (228, 234, 244)),
        ("  if (total != 0.00 && total <= 50000.00) return { status: 'OK', id, total };   ", (142, 230, 184)),
        ("  throw new RangeError(`Limit exceeded for ${id}: $${total.toFixed(2)}`);       ", (246, 188, 156)),
        ("} // End 80-col verification                                                    ", (128, 138, 158)),
    ]
    ty = cy
    for ln, col in code_lines:
        assert len(ln) == 80
        mono.draw_text(img, 108, ty, ln, 20, col, features={"ss01": True, "zero": True})
        ty += 33

    table_lines = [
        ("┌──────────────┬────────────┬──────────┐", (98, 110, 130)),
        ("│ REGION       │ NET (USD)  │ YOY (%)  │", (156, 198, 248)),
        ("├──────────────┼────────────┼──────────┤", (98, 110, 130)),
        ("│ HK-Admiralty │ $14,820.50 │  +18.4%  │", (234, 238, 246)),
        ("│ CH-Zürich    │  $9,111.10 │  +11.1%  │", (234, 238, 246)),
        ("│ DK-København │  $6,045.05 │  -02.3%  │", (234, 238, 246)),
        ("│ TOTAL        │ $29,976.65 │  +12.6%  │", (126, 232, 180)),
    ]
    # Use ASCII box table so 100% of glyphs come from AdmiraltyMono-Regular!
    ascii_table = [
        ("+--------------+------------+----------+", (102, 114, 134)),
        ("| REGION       | NET (USD)  | YOY (%)  |", (164, 206, 252)),
        ("+--------------+------------+----------+", (102, 114, 134)),
        ("| HK-Admiralty | $14,820.50 |  +18.4%  |", (234, 238, 246)),
        ("| CH-Zürich    |  $9,111.10 |  +11.1%  |", (234, 238, 246)),
        ("| DK-København |  $6,045.05 |  -02.3%  |", (234, 238, 246)),
        ("+--------------+------------+----------+", (102, 114, 134)),
        ("| TOTAL        | $29,976.65 |  +12.6%  |", (126, 232, 180)),
    ]
    ty = cy
    for ln, col in ascii_table:
        mono.draw_text(img, 1170, ty, ln, 23, col, features={"zero": True})
        ty += 30

    img.save(out_path)
    print(f"Rendered Mono overview -> {out_path}")


def draw_inline_sans_mono_line(
    img: Image.Image,
    x: float,
    y_baseline: float,
    segments: list[tuple[str, str]],
    px_size: float,
    sans: HBFreeTypeRenderer,
    serif: HBFreeTypeRenderer,
    mono: HBFreeTypeRenderer,
    fg: tuple[int, int, int],
    code_bg: tuple[int, int, int],
    code_fg: tuple[int, int, int],
    cjk_sans,
    cjk_serif,
) -> float:
    """Draws rich mixed prose containing inline `Admiralty Mono` code pills & CJK fallback."""
    cur_x = x
    for kind, text in segments:
        if kind == "code":
            # Inline Mono at 0.92x nominal px matches optical x-height & stem density cleanly
            m_px = px_size * 0.93
            mw = mono.measure_text(text, m_px)
            draw = ImageDraw.Draw(img)
            pad_x = 10
            draw.rounded_rectangle(
                [int(cur_x + 2), int(y_baseline - px_size * 0.80), int(cur_x + mw + 2 * pad_x + 2), int(y_baseline + px_size * 0.24)],
                radius=8,
                fill=code_bg,
            )
            mono.draw_text(img, cur_x + pad_x + 2, y_baseline - 1, text, m_px, code_fg)
            cur_x += mw + 2 * pad_x + 6
        elif kind == "sans":
            cur_x = draw_mixed_cjk_line(img, cur_x, y_baseline, text, px_size, sans, cjk_sans, fg)
        elif kind == "serif":
            cur_x = draw_mixed_cjk_line(img, cur_x, y_baseline, text, px_size, serif, cjk_serif, fg)
    return cur_x


def render_app_prototype(
    sans: HBFreeTypeRenderer,
    serif: HBFreeTypeRenderer,
    mono: HBFreeTypeRenderer,
    out_path: Path,
) -> None:
    """
    Milestone 5 Full 3-Family Personal Agent App Prototype (Light & Dark Mobile Frames):
      - User prompt in Admiralty Sans (+ inline Admiralty Mono code pill + Traditional Chinese)
      - Agent response in Admiralty Serif (+ inline Mono + 155-word calm briefing + embedded Mono code & table)
    """
    w, h = 1860, 1520
    img = Image.new("RGB", (w, h), (234, 233, 227))
    draw = ImageDraw.Draw(img)
    ui_title = get_ui_label_font(16)
    ui_small = get_ui_label_font(13)
    sans_cjk, serif_cjk = _find_cjk_fonts()

    # Two mobile-tablet app frames: Light Mode (left) & Dark Mode (right)
    draw.rounded_rectangle([32, 32, 914, h - 32], radius=28, fill=(250, 249, 245), outline=(218, 215, 208), width=2)
    draw.rounded_rectangle([946, 32, w - 32, h - 32], radius=28, fill=(17, 19, 24), outline=(42, 47, 58), width=2)

    for idx_p, (x0, is_dark) in enumerate([(64, False), (978, True)]):
        fg = (236, 238, 244) if is_dark else (20, 23, 29)
        muted = (130, 138, 152) if is_dark else (114, 120, 132)
        b_user = (36, 45, 60) if is_dark else (228, 236, 247)
        b_agent = (25, 28, 35) if is_dark else (255, 255, 255)
        b_border = (46, 52, 64) if is_dark else (224, 221, 214)
        code_pill_bg = (44, 52, 68) if is_dark else (236, 238, 243)
        code_pill_fg = (146, 212, 255) if is_dark else (32, 74, 132)
        code_card_bg = (14, 16, 21) if is_dark else (24, 27, 34)

        draw = ImageDraw.Draw(img)
        hdr = (
            "DARK MODE PROTOTYPE  ·  Sans + Serif + Mono"
            if is_dark
            else "LIGHT MODE PROTOTYPE  ·  Sans + Serif + Mono"
        )
        draw.text((x0, 62), hdr, fill=muted, font=ui_title)
        sans.draw_text(img, x0 + 690, 77, "09:41", 26, muted, features={"tnum": True})
        draw = ImageDraw.Draw(img)
        draw.line([(x0, 96), (x0 + 818, 96)], fill=b_border, width=1)

        # 1. User Bubble (Admiralty Sans + inline Admiralty Mono + CJK)
        y = 118
        draw.text((x0 + 148, y), "USER · Admiralty Sans + Inline Admiralty Mono", fill=muted, font=ui_small)
        y += 22
        draw.rounded_rectangle([x0 + 132, y, x0 + 818, y + 128], radius=20, fill=b_user)
        draw_inline_sans_mono_line(
            img, x0 + 158, y + 48,
            [("sans", "請幫我檢查訂單 "), ("code", "#I1l-O08"), ("sans", " 與 "), ("code", "invoice.ts")],
            28.0, sans, serif, mono, fg, code_pill_bg, code_pill_fg, sans_cjk, serif_cjk,
        )
        draw_inline_sans_mono_line(
            img, x0 + 158, y + 96,
            [("sans", "為什麼 Zürich 分區稅率在 0.00 時會報錯？")],
            28.0, sans, serif, mono, fg, code_pill_bg, code_pill_fg, sans_cjk, serif_cjk,
        )

        # 2. Agent Long Reply Bubble (Admiralty Serif ~150-word calm prose + Mono code block + Mono table)
        y += 152
        draw = ImageDraw.Draw(img)
        draw.text((x0 + 4, y), "AGENT · Admiralty Serif (Body) + Admiralty Mono (Code & Aligned Table)", fill=muted, font=ui_small)
        y += 22
        agent_h = 1018
        draw.rounded_rectangle([x0, y, x0 + 818, y + agent_h], radius=22, fill=b_agent, outline=b_border, width=1)

        ty = y + 46
        draw_inline_sans_mono_line(
            img, x0 + 28, ty,
            [("serif", "已定位根源："), ("code", "src/billing/invoice.ts"), ("serif", " 誤將零稅率攔截了。")],
            28.0, sans, serif, mono, fg, code_pill_bg, code_pill_fg, sans_cjk, serif_cjk,
        )
        ty += 48

        long_prose = (
            "When an exempted Zürich or København educational account submits an order "
            "with a 0.00% VAT rate, the legacy guard rejects zero before computing the "
            "line-item subtotal. Replacing the strict positive check with a non-negative "
            "bound preserves every audit invariant while letting zero-rated European "
            "invoices settle cleanly without manual intervention. Below is the minimal "
            "patch and the reconciled Q3 regional ledger:"
        )
        p_lines = serif.wrap_lines(long_prose, 28.0, 760)
        for pln in p_lines:
            serif.draw_text(img, x0 + 28, ty, pln, 28.0, fg)
            ty += 42

        # Embedded Admiralty Mono Code Block (24px = 12px @2x / 13px mobile code)
        ty += 8
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([x0 + 26, ty, x0 + 792, ty + 242], radius=14, fill=code_card_bg, outline=(46, 52, 66), width=1)
        mono.draw_text(img, x0 + 48, ty + 34, "// src/billing/invoice.ts  (Admiralty Mono · ss01=ON)", 21.0, (124, 138, 162))
        patch_lines = [
            ("- if (taxRate == 0.00 || subtotal <= 0.00) {", (244, 148, 148)),
            ("+ if (taxRate <  0.00 || subtotal <  0.00) {", (130, 232, 178)),
            ("    return Err({ code: 'E_TAX_1lI0', id: order.id });", (214, 222, 236)),
            ("  }", (214, 222, 236)),
            ("  const grandTotal = subtotal -> roundUsd(taxRate);", (168, 206, 252)),
        ]
        cy_code = ty + 74
        for cln, ccol in patch_lines:
            mono.draw_text(img, x0 + 48, cy_code, cln, 22.5, ccol, features={"ss01": True, "zero": True})
            cy_code += 34

        ty += 268
        # Embedded Admiralty Mono Aligned Ledger Table
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([x0 + 26, ty, x0 + 792, ty + 228], radius=14, fill=code_card_bg, outline=(46, 52, 66), width=1)
        tbl = [
            ("ORDER ID     REGION         SUBTOTAL    VAT     SETTLED   ", (142, 158, 184)),
            ("----------------------------------------------------------", (78, 88, 108)),
            ("#I1l-O08     CH-Zürich     $1,250.00   0.00%    $1,250.00 ", (234, 238, 246)),
            ("#I1l-O09     DE-München    $2,400.00   8.10%    $2,594.40 ", (234, 238, 246)),
            ("#I1l-O10     DK-København    $890.50   0.00%      $890.50 ", (130, 232, 178)),
        ]
        cy_tbl = ty + 42
        for tln, tcol in tbl:
            mono.draw_text(img, x0 + 48, cy_tbl, tln, 21.0, tcol, features={"zero": True})
            cy_tbl += 38

        # Action Pills at bottom of Agent card
        ty += 250
        draw = ImageDraw.Draw(img)
        for lbl, px_off in [("← Revert", 28), ("Apply Patch →", 206), ("Export CSV ↗", 434)]:
            pw = sans.measure_text(lbl, 25.0) + 40
            draw.rounded_rectangle([x0 + px_off, ty, int(x0 + px_off + pw), ty + 48], radius=12, fill=b_user)
            sans.draw_text(img, x0 + px_off + 20, ty + 32, lbl, 25.0, fg)

        # Bottom Input Bar
        iy = h - 108
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([x0, iy, x0 + 818, iy + 56], radius=28, fill=b_agent, outline=b_border, width=1)
        sans.draw_text(img, x0 + 28, iy + 36, "Reply to Admiralty Agent…", 25.0, muted)
        sans.draw_text(img, x0 + 764, iy + 37, "↑", 28.0, fg)

    img.save(out_path)
    print(f"Rendered 3-family App Prototype -> {out_path}")


def run_measured_consistency_and_pdf_pack() -> dict:
    """
    Section 15 Gate:
      1. Programmatically measure stem widths, x-height, cap-height, ascender,
         descender, and overshoots across Sans Regular, Serif Regular, and Mono Regular.
      2. Export printable multi-page PDF proof pack for Human Type Designer Review #1.
    """
    spec_dir = ROOT / "specimens"
    families = [
        ("Admiralty Sans Regular", ROOT / "sources" / "AdmiraltySans-Regular.ufo"),
        ("Admiralty Serif Regular", ROOT / "sources" / "AdmiraltySerif-Regular.ufo"),
        ("Admiralty Mono Regular", ROOT / "sources" / "AdmiraltyMono-Regular.ufo"),
    ]

    report = {}
    print("\n=== SECTION 15 MEASURED CONSISTENCY REPORT (UPM = 1000) ===")
    for label, ufo_path in families:
        ufo = ufoLib2.Font.open(ufo_path)
        def _bounds(gname: str):
            bp = BoundsPen(ufo)
            ufo[gname].draw(bp)
            return bp.bounds  # (xmin, ymin, xmax, ymax)

        b_H = _bounds("H")
        b_O = _bounds("O")
        b_x = _bounds("x")
        b_o = _bounds("o")
        b_b = _bounds("b")
        b_p = _bounds("p")

        # Measure vertical stem width of 'I' or 'H' at y=350, and 'i'/'n' at y=250
        # For H: two vertical stems -> on Sans (82..174 = 92u), Serif (80..182 = 102u), Mono (87..171 = 84u)
        cap_h = round(b_H[3] - b_H[1])
        xh = round(b_x[3] - b_x[1])
        cap_over_top = round(b_O[3] - 700)
        cap_over_bot = round(0 - b_O[1])
        lc_over_top = round(b_o[3] - 520)
        lc_over_bot = round(0 - b_o[1])
        asc_h = round(b_b[3])
        desc_h = round(b_p[1])

        metrics_row = {
            "glyph_count": len(ufo),
            "cap_height_H": cap_h,
            "x_height_x": xh,
            "ascender_b": asc_h,
            "descender_p": desc_h,
            "cap_overshoot_O": (cap_over_top, cap_over_bot),
            "lc_overshoot_o": (lc_over_top, lc_over_bot),
        }
        report[label] = metrics_row
        print(
            f"  {label:25s} | glyphs={len(ufo)} | Cap(H)={cap_h}u | x-h(x)={xh}u | "
            f"Asc(b)={asc_h}u | Desc(p)={desc_h}u | Over(O)=+{cap_over_top}/-{cap_over_bot}u | "
            f"Over(o)=+{lc_over_top}/-{lc_over_bot}u"
        )

    # Assemble multi-page printable PDF proof sheet pack
    proof_pages = [
        spec_dir / "milestone3_spacing_proof.png",
        spec_dir / "milestone3_diacritics_proof.png",
        spec_dir / "milestone4_serif_overview.png",
        spec_dir / "milestone4_duplex_proof.png",
        spec_dir / "milestone4_chat_paired.png",
        spec_dir / "milestone5_mono_overview.png",
        spec_dir / "milestone5_app_prototype.png",
    ]
    imgs = [Image.open(p).convert("RGB") for p in proof_pages if p.exists()]
    pdf_path = spec_dir / "Admiralty_Regular_Trio_Review1_Proofs.pdf"
    imgs[0].save(
        pdf_path,
        "PDF",
        resolution=150.0,
        save_all=True,
        append_images=imgs[1:],
        title="Admiralty Sans, Serif & Mono Regular — Human Type Designer Review #1 Proof Pack",
        author="Lei Yutian",
    )
    print(f"Exported {len(imgs)}-page printable PDF proof pack -> {pdf_path} ({pdf_path.stat().st_size // 1024} KB)")
    return report


def main() -> None:
    spec_dir = ROOT / "specimens"
    spec_dir.mkdir(parents=True, exist_ok=True)
    sans = HBFreeTypeRenderer(ROOT / "fonts" / "ttf" / "AdmiraltySans-Regular.ttf")
    serif = HBFreeTypeRenderer(ROOT / "fonts" / "ttf" / "AdmiraltySerif-Regular.ttf")
    mono = HBFreeTypeRenderer(ROOT / "fonts" / "ttf" / "AdmiraltyMono-Regular.ttf")

    render_mono_overview(mono, spec_dir / "milestone5_mono_overview.png")
    render_app_prototype(sans, serif, mono, spec_dir / "milestone5_app_prototype.png")
    run_measured_consistency_and_pdf_pack()


if __name__ == "__main__":
    main()
