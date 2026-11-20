"""
Builds Admiralty Symbols Phase 1 (218 original UI icons x Regular 400 & Bold 700):
  - UFO v3 sources (sources/AdmiraltySymbols-Regular.ufo, AdmiraltySymbols-Bold.ufo)
  - 2-source DesignSpace v5 (sources/AdmiraltySymbols.designspace)
  - Compiled OTF, TTF (with gasp+prep), WOFF2 binaries
  - Standalone 24x24 SVGs (symbols/svg/regular/*.svg, symbols/svg/bold/*.svg, plus -rtl.svg)
  - Machine-readable metadata catalog (symbols/admiralty-symbols.json)
"""

from __future__ import annotations
import json
from pathlib import Path
import re
import shutil
import sys
from typing import Dict, List, Tuple

from fontTools.designspaceLib import AxisDescriptor, DesignSpaceDocument, InstanceDescriptor, SourceDescriptor
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont
import ufo2ft
import ufoLib2
import uharfbuzz as hb

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from design_system import METRICS, rect_contour
from symbols_engine import (
    IconCanvas,
    STROKE_BOLD,
    STROKE_MEDIUM,
    STROKE_REGULAR,
    SYMBOL_ADVANCE_WIDTH,
    SymbolSpec,
)
from symbols_phase1_a import SYMBOLS_PHASE1_A
from symbols_phase1_b import SYMBOLS_PHASE1_B
from symbols_refine_r2 import SYMBOL_OVERRIDES_R2
from symbols_phase2 import SYMBOLS_PHASE2
from symbols_client import SYMBOLS_CLIENT, ALIASES

PUA_START = 0xE000
SYMBOLS_VERSION_MINOR = 300
SYMBOLS_VERSION_STR = "0.300"


_LABEL_OVERRIDES = {
    "pdf": "PDF",
    "whats-new": "What's new",
    "two-factor": "Two-factor authentication",
    "more-horizontal": "More options",
    "more-vertical": "More options, vertical",
    "mic": "Microphone",
    "mic-off": "Microphone off",
    "mic-filled": "Microphone, active",
    "up": "Up arrow",
    "down": "Down arrow",
    "back": "Back",
    "forward": "Forward",
    "new": "New",
    "send-check": "Sent to external group",
    "takeover": "Take control",
    "whisper": "Private message",
    "bell-off": "Notifications muted",
    "end-call": "End call",
    "user-remove": "Remove member",
    "info": "Information",
    "tips": "Tips",
}


def accessibility_label(name: str) -> str:
    """Short screen-reader label for a symbol, e.g. 'arrow-up-right' -> 'Arrow up right'."""
    if name in _LABEL_OVERRIDES:
        return _LABEL_OVERRIDES[name]
    if name.endswith("-filled"):
        return accessibility_label(name[: -len("-filled")]) + ", active"
    words = name.split("-")
    return (words[0].capitalize() + " " + " ".join(words[1:])).strip()


def ufo_glyph_name(name: str) -> str:
    """Glyph name inside the font. Hyphens are not valid in glyph names, so 'mic-off' -> 'mic_off'.
    The public symbol name (JSON, SVG file names) keeps its hyphens."""
    return name.replace("-", "_")


def get_phase1_catalog() -> List[SymbolSpec]:
    assert len(SYMBOLS_PHASE1_A + SYMBOLS_PHASE1_B) == 218, "Phase 1 must keep its 218 code points"
    # Phase 2 (0.300): new symbols get the code points after Phase 1, so old code points never move
    all_specs = SYMBOLS_PHASE1_A + SYMBOLS_PHASE1_B + SYMBOLS_PHASE2 + SYMBOLS_CLIENT
    unknown = set(SYMBOL_OVERRIDES_R2) - {sp.name for sp in all_specs}
    assert not unknown, f"Review 2 overrides for unknown symbols: {sorted(unknown)}"
    seen: set[str] = set()
    catalog: List[SymbolSpec] = []
    name_re = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
    for idx, spec in enumerate(all_specs):
        assert name_re.match(spec.name), f"Invalid non-hyphen-case symbol name: {spec.name!r}"
        assert spec.name not in seen, f"Duplicate symbol name: {spec.name!r}"
        seen.add(spec.name)
        cp = PUA_START + idx
        assert 0xE000 <= cp <= 0xF8FF, f"Symbol {spec.name} codepoint {hex(cp)} outside BMP PUA!"
        catalog.append(
            SymbolSpec(
                name=spec.name,
                category=spec.category,
                tags=spec.tags,
                draw_fn=SYMBOL_OVERRIDES_R2.get(spec.name, spec.draw_fn),
                rtl_mirror=spec.rtl_mirror,
                is_filled=spec.is_filled,
                codepoint=cp,
            )
        )
    return catalog


def _populate_symbols_metadata(ufo: ufoLib2.Font, style_name: str, weight_class: int) -> None:
    ps_family = "AdmiraltySymbols"
    info = ufo.info
    info.familyName = "Admiralty Symbols"
    info.styleName = style_name
    if weight_class == 500:
        info.styleMapFamilyName = "Admiralty Symbols Medium"
        info.styleMapStyleName = "regular"
        info.openTypeNamePreferredFamilyName = "Admiralty Symbols"
        info.openTypeNamePreferredSubfamilyName = "Medium"
    else:
        info.styleMapFamilyName = "Admiralty Symbols"
        info.styleMapStyleName = style_name.lower()
    info.postscriptFontName = f"{ps_family}-{style_name}"
    info.openTypeNameUniqueID = f"{SYMBOLS_VERSION_STR};LYT;{ps_family}-{style_name}"

    info.versionMajor = 0
    info.versionMinor = SYMBOLS_VERSION_MINOR
    info.openTypeNameVersion = f"Version {SYMBOLS_VERSION_STR}"
    info.copyright = (
        "Copyright 2026 The Admiralty Project Authors "
        "(https://github.com/cosmoluei/admiralty-fonts)"
    )
    info.openTypeNameDesigner = "Lei Yutian"
    info.openTypeNameManufacturer = "Lei Yutian"
    info.openTypeOS2VendorID = "LYT "
    info.openTypeNameDescription = (
        "Admiralty Symbols is an original 24x24 UI symbol and icon typeface "
        "calibrated to align with Admiralty Sans, Serif, and Mono."
    )
    info.openTypeNameLicense = (
        "This Font Software is licensed under the SIL Open Font License, Version 1.1. "
        "This license is available with a FAQ at: https://openfontlicense.org"
    )
    info.openTypeNameLicenseURL = "https://openfontlicense.org"

    info.unitsPerEm = METRICS.upm
    info.xHeight = METRICS.x_height
    info.capHeight = METRICS.cap_height
    info.ascender = METRICS.ascender
    info.descender = METRICS.descender

    info.openTypeOS2WeightClass = weight_class
    info.openTypeOS2WidthClass = 5
    info.openTypeOS2Type = []
    info.openTypeOS2TypoAscender = METRICS.typo_ascender
    info.openTypeOS2TypoDescender = METRICS.typo_descender
    info.openTypeOS2TypoLineGap = METRICS.typo_line_gap
    info.openTypeOS2WinAscent = METRICS.win_ascent
    info.openTypeOS2WinDescent = METRICS.win_descent
    info.openTypeOS2Selection = [7]

    # Panose: 5 = Pictorial, Weight 5 = Regular / 6 = Medium / 8 = Bold, Proportion 9 = Monospaced 840u
    pan_w = 8 if weight_class >= 700 else (6 if weight_class == 500 else 5)
    info.openTypeOS2Panose = [5, 0, pan_w, 9, 0, 0, 0, 0, 0, 0]

    info.openTypeHheaAscender = METRICS.hhea_ascender
    info.openTypeHheaDescender = METRICS.hhea_descender
    info.openTypeHheaLineGap = METRICS.hhea_line_gap

    info.postscriptUnderlinePosition = -100
    info.postscriptUnderlineThickness = 50
    info.italicAngle = 0
    info.postscriptIsFixedPitch = True
    stem_snap = 84 if weight_class >= 700 else (71 if weight_class == 500 else 60)
    info.postscriptStemSnapH = [stem_snap]
    info.postscriptStemSnapV = [stem_snap]
    info.postscriptBlueValues = [-10, 0, 700, 710]
    info.postscriptOtherBlues = [-226, -220]
    info.postscriptBlueScale = 0.039625
    info.postscriptBlueShift = 7
    info.postscriptBlueFuzz = 0


def _glyph_signature(ufo: ufoLib2.Font, gname: str) -> Tuple[float, Tuple[int, ...], int, int, int, int]:
    g = ufo[gname]
    apen = AreaPen(ufo)
    bpen = BoundsPen(ufo)
    g.draw(apen)
    g.draw(bpen)
    pts = [(pt.x, pt.y) for c in g.contours for pt in c.points if pt.type is not None]
    mx = int(round(sum(x for x, _ in pts) / len(pts))) if pts else 0
    my = int(round(sum(y for _, y in pts) / len(pts))) if pts else 0
    mr = int(round(sum(((x - 420.0) ** 2 + (y - 350.0) ** 2) ** 0.5 for x, y in pts) / len(pts))) if pts else 0
    bounds = tuple(int(round(v, -1)) for v in (bpen.bounds or (0, 0, 0, 0)))
    return (round(apen.value, -2), bounds, len(g.contours), mx, my, mr)


def _hb_shape_symbols(ttf_path: Path, codepoint: int, rtl: bool = False) -> List[int]:
    blob = hb.Blob.from_file_path(str(ttf_path))
    face = hb.Face(blob)
    font = hb.Font(face)
    font.scale = (1000, 1000)
    buf = hb.Buffer()
    buf.add_str(chr(codepoint))
    buf.direction = "rtl" if rtl else "ltr"
    buf.script = "arab" if rtl else "latn"
    hb.shape(font, buf, {"rtlm": True} if rtl else {})
    return [info.codepoint for info in (buf.glyph_infos or [])]


def build_all_symbols() -> Tuple[Path, Path, Path, Path]:
    from build_fonts import apply_ttf_nonhinting_tables, audit_ufo_geometry

    catalog = get_phase1_catalog()

    sources_dir = ROOT / "sources"
    otf_dir = ROOT / "fonts" / "otf"
    ttf_dir = ROOT / "fonts" / "ttf"
    woff2_dir = ROOT / "fonts" / "woff2"
    svg_reg_dir = ROOT / "symbols" / "svg" / "regular"
    svg_med_dir = ROOT / "symbols" / "svg" / "medium"
    svg_bold_dir = ROOT / "symbols" / "svg" / "bold"
    for d in (sources_dir, otf_dir, ttf_dir, woff2_dir):
        d.mkdir(parents=True, exist_ok=True)
    for sd in (svg_reg_dir, svg_med_dir, svg_bold_dir):
        if sd.exists():
            shutil.rmtree(sd)
        sd.mkdir(parents=True, exist_ok=True)

    # Check SVGs and UFOs per weight
    metadata_records: List[dict] = []
    svg_unique_check: Dict[str, set[str]] = {"regular": set(), "medium": set(), "bold": set()}

    for spec in catalog:
        reg_c = IconCanvas(STROKE_REGULAR)
        med_c = IconCanvas(STROKE_MEDIUM)
        bold_c = IconCanvas(STROKE_BOLD)
        spec.draw_fn(reg_c)
        spec.draw_fn(med_c)
        spec.draw_fn(bold_c)

        reg_svg = reg_c.to_svg(title=spec.name)
        med_svg = med_c.to_svg(title=spec.name)
        bold_svg = bold_c.to_svg(title=spec.name)
        reg_key = reg_c.to_svg(title=None)
        med_key = med_c.to_svg(title=None)
        bold_key = bold_c.to_svg(title=None)
        assert reg_key not in svg_unique_check["regular"], f"Duplicate Regular SVG geometry: {spec.name}"
        assert med_key not in svg_unique_check["medium"], f"Duplicate Medium SVG geometry: {spec.name}"
        assert bold_key not in svg_unique_check["bold"], f"Duplicate Bold SVG geometry: {spec.name}"
        svg_unique_check["regular"].add(reg_key)
        svg_unique_check["medium"].add(med_key)
        svg_unique_check["bold"].add(bold_key)

        (svg_reg_dir / f"{spec.name}.svg").write_text(reg_svg, encoding="utf-8")
        (svg_med_dir / f"{spec.name}.svg").write_text(med_svg, encoding="utf-8")
        (svg_bold_dir / f"{spec.name}.svg").write_text(bold_svg, encoding="utf-8")

        rec = {
            "name": spec.name,
            "label": accessibility_label(spec.name),
            "glyphName": ufo_glyph_name(spec.name),
            "codepoint": f"U+{spec.codepoint:04X}",
            "codepointInt": spec.codepoint,
            "category": spec.category,
            "tags": list(spec.tags),
            "rtlMirror": spec.rtl_mirror,
            "filled": spec.is_filled,
            "svgRegular": f"svg/regular/{spec.name}.svg",
            "svgMedium": f"svg/medium/{spec.name}.svg",
            "svgBold": f"svg/bold/{spec.name}.svg",
        }
        if spec.rtl_mirror:
            reg_rtl_svg = reg_c.mirrored_horiz().to_svg(title=f"{spec.name} (RTL)")
            med_rtl_svg = med_c.mirrored_horiz().to_svg(title=f"{spec.name} (RTL)")
            bold_rtl_svg = bold_c.mirrored_horiz().to_svg(title=f"{spec.name} (RTL)")
            (svg_reg_dir / f"{spec.name}-rtl.svg").write_text(reg_rtl_svg, encoding="utf-8")
            (svg_med_dir / f"{spec.name}-rtl.svg").write_text(med_rtl_svg, encoding="utf-8")
            (svg_bold_dir / f"{spec.name}-rtl.svg").write_text(bold_rtl_svg, encoding="utf-8")
            rec["svgRegularRtl"] = f"svg/regular/{spec.name}-rtl.svg"
            rec["svgMediumRtl"] = f"svg/medium/{spec.name}-rtl.svg"
            rec["svgBoldRtl"] = f"svg/bold/{spec.name}-rtl.svg"
        metadata_records.append(rec)

    json_path = ROOT / "symbols" / "admiralty-symbols.json"
    json_payload = {
        "family": "Admiralty Symbols",
        "version": SYMBOLS_VERSION_STR,
        "grid": 24,
        "advanceWidth": SYMBOL_ADVANCE_WIDTH,
        "strokeWidths": {"regular": STROKE_REGULAR, "medium": STROKE_MEDIUM, "bold": STROKE_BOLD},
        "weights": [400, 500, 700],
        "puaRange": f"U+{PUA_START:04X}-U+{PUA_START + len(catalog) - 1:04X}",
        "count": len(catalog),
        "aliases": ALIASES,
        "symbols": metadata_records,
    }
    json_path.write_text(json.dumps(json_payload, indent=2) + "\n", encoding="utf-8")
    print(f"[AdmiraltySymbols] Exported {len(catalog)} symbols (+Med & RTL SVGs) -> {json_path}")

    ds = DesignSpaceDocument()
    w_axis = AxisDescriptor()
    w_axis.tag = "wght"
    w_axis.name = "Weight"
    w_axis.minimum = 400
    w_axis.default = 400
    w_axis.maximum = 700
    ds.addAxis(w_axis)

    built_woff2: Dict[str, Path] = {}
    built_ttf: Dict[str, Path] = {}

    for style_name, weight_class, sw in (
        ("Regular", 400, STROKE_REGULAR),
        ("Medium", 500, STROKE_MEDIUM),
        ("Bold", 700, STROKE_BOLD),
    ):
        stem = f"AdmiraltySymbols-{style_name}"
        ufo = ufoLib2.Font()
        _populate_symbols_metadata(ufo, style_name, weight_class)

        glyph_order: List[str] = [".notdef", "space"]
        # Crisp hollow frame .notdef inside 840u
        g_nd = ufo.newGlyph(".notdef")
        g_nd.width = SYMBOL_ADVANCE_WIDTH
        pen_nd = g_nd.getPen()
        rect_contour(120, 40, 720, 660, clockwise=False).draw_to_pen(pen_nd)
        rect_contour(180, 100, 660, 600, clockwise=True).draw_to_pen(pen_nd)

        g_sp = ufo.newGlyph("space")
        g_sp.width = SYMBOL_ADVANCE_WIDTH
        g_sp.unicodes = [0x0020]

        rtl_pairs: List[Tuple[str, str]] = []
        ufo_sigs: Dict[Tuple[float, Tuple[int, ...], int], str] = {}

        for spec in catalog:
            canv = IconCanvas(sw)
            spec.draw_fn(canv)
            contours = canv.to_ufo_contours()
            assert len(contours) > 0, f"Empty contours for symbol {spec.name} ({style_name})"

            glyph_order.append(ufo_glyph_name(spec.name))
            g = ufo.newGlyph(ufo_glyph_name(spec.name))
            g.width = SYMBOL_ADVANCE_WIDTH
            g.unicodes = [spec.codepoint]
            pen = g.getPen()
            for cb in contours:
                cb.draw_to_pen(pen)

            sig = _glyph_signature(ufo, ufo_glyph_name(spec.name))
            if sig in ufo_sigs:
                # Raise only if BOTH area/bounds match AND SVG failed? Wait: check distinctness strictly!
                raise AssertionError(
                    f"Duplicate UFO geometry signature {sig} in {style_name}: {spec.name} vs {ufo_sigs[sig]}"
                )
            ufo_sigs[sig] = spec.name

            if spec.rtl_mirror:
                rtl_name = f"{ufo_glyph_name(spec.name)}.rtl"
                rtl_contours = canv.mirrored_horiz().to_ufo_contours()
                glyph_order.append(rtl_name)
                gr = ufo.newGlyph(rtl_name)
                gr.width = SYMBOL_ADVANCE_WIDTH
                rpen = gr.getPen()
                for cb in rtl_contours:
                    cb.draw_to_pen(rpen)
                rtl_pairs.append((ufo_glyph_name(spec.name), rtl_name))

        ufo.lib["public.glyphOrder"] = glyph_order

        rtl_rules = "\n".join(f"    sub {src} by {dst};" for src, dst in rtl_pairs)
        ufo.features.text = (
            "languagesystem DFLT dflt;\n"
            "languagesystem latn dflt;\n"
            "languagesystem arab dflt;\n"
            "languagesystem hebr dflt;\n\n"
            "feature rtlm {\n"
            f"{rtl_rules}\n"
            "} rtlm;\n"
        )

        audit_ufo_geometry(ufo)
        ufo_path = sources_dir / f"{stem}.ufo"
        ufo.save(ufo_path, overwrite=True)

        src_desc = SourceDescriptor()
        src_desc.path = str(ufo_path)
        src_desc.filename = ufo_path.name
        src_desc.familyName = "Admiralty Symbols"
        src_desc.styleName = style_name
        src_desc.location = {"Weight": weight_class}
        if weight_class == 400:
            src_desc.copyLib = True
            src_desc.copyInfo = True
            src_desc.copyGroups = True
            src_desc.copyFeatures = True
        ds.addSource(src_desc)

        inst = InstanceDescriptor()
        inst.name = f"Admiralty Symbols {style_name}"
        inst.familyName = "Admiralty Symbols"
        inst.styleName = style_name
        inst.postScriptFontName = f"AdmiraltySymbols-{style_name}"
        inst.styleMapFamilyName = "Admiralty Symbols Medium" if weight_class == 500 else "Admiralty Symbols"
        inst.styleMapStyleName = "regular" if weight_class == 500 else style_name.lower()
        inst.location = {"Weight": weight_class}
        ds.addInstance(inst)

        otf_font: TTFont = ufo2ft.compileOTF(ufo, removeOverlaps=True, optimizeCFF=True)
        otf_font["OS/2"].xAvgCharWidth = SYMBOL_ADVANCE_WIDTH
        otf_path = otf_dir / f"{stem}.otf"
        otf_font.save(str(otf_path))

        ttf_font: TTFont = ufo2ft.compileTTF(ufo, removeOverlaps=True)
        ttf_font["OS/2"].xAvgCharWidth = SYMBOL_ADVANCE_WIDTH
        apply_ttf_nonhinting_tables(ttf_font)
        ttf_path = ttf_dir / f"{stem}.ttf"
        ttf_font.save(str(ttf_path))

        woff2_font = TTFont(str(ttf_path))
        woff2_font.flavor = "woff2"
        woff2_path = woff2_dir / f"{stem}.woff2"
        woff2_font.save(str(woff2_path))

        # Binary verification
        tt = TTFont(str(ttf_path))
        assert tt["OS/2"].usWeightClass == weight_class
        if weight_class >= 700:
            assert bool(tt["OS/2"].fsSelection & (1 << 5))
            assert not bool(tt["OS/2"].fsSelection & (1 << 6))
            assert tt["head"].macStyle == 1
        elif weight_class == 500:
            n_map = {r.nameID: r.toUnicode() for r in tt["name"].names if r.platformID == 3}
            assert n_map.get(1) == "Admiralty Symbols Medium" and n_map.get(16) == "Admiralty Symbols" and n_map.get(17) == "Medium"
        assert bool(tt["OS/2"].fsSelection & (1 << 7))
        assert round(tt["head"].fontRevision, 3) == float(SYMBOLS_VERSION_STR)
        assert tt["post"].isFixedPitch == 1
        widths = {w for _, (w, _) in tt["hmtx"].metrics.items()}
        assert widths == {SYMBOL_ADVANCE_WIDTH}, f"Non-uniform symbol widths: {widths}"
        cmap = tt.getBestCmap() or {}
        for spec in catalog:
            assert spec.codepoint in cmap and cmap[spec.codepoint] == ufo_glyph_name(spec.name)
        assert all(cp < 0x1F000 for cp in cmap.keys()), "Emoji codepoint leaked into Admiralty Symbols!"

        # Verify HarfBuzz rtlm substitution on chevron-left (and send, back)
        for test_spec in (catalog[0], next(s for s in catalog if s.name == "chevron-left")):
            gid_ltr = _hb_shape_symbols(ttf_path, test_spec.codepoint, rtl=False)[0]
            gid_rtl = _hb_shape_symbols(ttf_path, test_spec.codepoint, rtl=True)[0]
            assert gid_ltr != gid_rtl, f"rtlm substitution failed on {test_spec.name} ({style_name})"
            assert tt.getGlyphName(gid_rtl) == f"{ufo_glyph_name(test_spec.name)}.rtl"

        woff2_kb = woff2_path.stat().st_size / 1024.0
        assert woff2_kb < 150.0, f"{stem}.woff2 size {woff2_kb:.1f} KB exceeds 150 KB target!"
        print(
            f"[{stem}] Compiled & audited: {len(catalog)} symbols + {len(rtl_pairs)} .rtl glyphs "
            f"(840u uniform, rtlm=OK, w={weight_class}, WOFF2={woff2_kb:.1f} KB)"
        )
        built_ttf[style_name] = ttf_path
        built_woff2[style_name] = woff2_path

    ds.write(str(sources_dir / "AdmiraltySymbols.designspace"))
    return built_ttf["Regular"], built_ttf["Medium"], built_ttf["Bold"], json_path


if __name__ == "__main__":
    build_all_symbols()
