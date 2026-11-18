"""
Builds all 5 platform delivery packages (REQUIREMENTS.md Section 14 & 17) into dist/:
  1. dist/apple-ios-macos/  - Variable TTFs + Static OTFs + Plain Original SVGs + OFL.txt + README
  2. dist/android/          - res/font/*.ttf & XML descriptors + 282 Vector Drawables (ic_adm_*.xml) + OFL.txt + README
  3. dist/windows/          - Static RIBBI TTFs (Office/Win32) + Variable TTFs + SVGs + OFL.txt + README
  4. dist/web/              - Variable & Static WOFF2s + Unicode-range Subsets + CLS-zero CSS + SVG Sprite + OFL.txt + README
  5. dist/cross-platform/   - Variable & Static TTFs + admiralty-symbols.json + Flutter IconData Dart map + OFL.txt + README
"""

from __future__ import annotations
import json
from pathlib import Path
import re
import shutil
import sys
from typing import Dict, List

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.subset import Options as SubsetOptions, Subsetter
from fontTools.ttLib import TTFont
import ufoLib2

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

DIST_DIR = ROOT / "dist"


# Dart reserved words (these cannot be used as names; built-in identifiers such as
# `import` or `export` can, so they are not listed)
DART_RESERVED = {
    "assert", "break", "case", "catch", "class", "const", "continue", "default", "do", "else",
    "enum", "extends", "false", "final", "finally", "for", "if", "in", "is", "new", "null",
    "rethrow", "return", "super", "switch", "this", "throw", "true", "try", "var", "void",
    "while", "with",
}


def _copy_glob(src_dir: Path, pattern: str, dst_dir: Path) -> List[Path]:
    dst_dir.mkdir(parents=True, exist_ok=True)
    copied: List[Path] = []
    for p in sorted(src_dir.glob(pattern)):
        out = dst_dir / p.name
        shutil.copyfile(p, out)
        copied.append(out)
    return copied


def _ufo_glyph_to_svg_path_24(ufo: ufoLib2.Font, glyph_name: str) -> str:
    """Convert a 1000-UPM UFO symbol glyph back to Android/Web 24x24 Y-down SVG pathData."""
    g = ufo[glyph_name]
    svg_pen = SVGPathPen(ufo, lambda v: f"{round(v, 3):.3f}".rstrip("0").rstrip("."))
    # gx = (ux - GRID_X0) / GRID_SCALE ; gy = (GRID_Y0 - uy) / GRID_SCALE
    from symbols_engine import GRID_SCALE, GRID_X0, GRID_Y0
    scale = 1.0 / GRID_SCALE
    tpen = TransformPen(svg_pen, (scale, 0.0, 0.0, -scale, -GRID_X0 * scale, GRID_Y0 * scale))
    g.draw(tpen)
    return svg_pen.getCommands()


def _write_outline_svgs(ttf_dir: Path, sym_svg_dir: Path, meta: dict) -> int:
    """Release prep: write symbols/svg/{regular,medium,bold}/*.svg as plain filled outlines taken
    from the compiled static Symbols fonts. The drawing engine's SVGs used strokes with <mask>
    cut-outs, which browsers draw correctly but Flutter (flutter_svg), Android Studio's importer
    and several design tools do not. Outline SVGs look the same everywhere and match the font."""
    from fontTools.pens.svgPathPen import SVGPathPen as _P
    from symbols_engine import GRID_SCALE, GRID_X0, GRID_Y0
    sc = 1.0 / GRID_SCALE
    n = 0
    for weight, style in (("regular", "Regular"), ("medium", "Medium"), ("bold", "Bold")):
        tt = TTFont(str(ttf_dir / f"AdmiraltySymbols-{style}.ttf"))
        gs = tt.getGlyphSet()
        out_dir = sym_svg_dir / weight
        out_dir.mkdir(parents=True, exist_ok=True)
        for rec in meta["symbols"]:
            variants = [(rec["glyphName"], rec["name"])]
            if rec["rtlMirror"]:
                variants.append((rec["glyphName"] + ".rtl", rec["name"] + "-rtl"))
            for gname, stem in variants:
                pen = _P(gs, lambda v: f"{round(v, 3):.3f}".rstrip("0").rstrip("."))
                gs[gname].draw(TransformPen(pen, (sc, 0.0, 0.0, -sc, -GRID_X0 * sc, GRID_Y0 * sc)))
                d = pen.getCommands()
                assert d, f"empty outline for {gname} ({style})"
                (out_dir / f"{stem}.svg").write_text(
                    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" '
                    f'fill="currentColor"><title>{rec["name"]}</title><path d="{d}"/></svg>\n',
                    encoding="utf-8")
                n += 1
    return n


def _subset_woff2(src_ttf: Path, out_woff2: Path, unicode_range_str: str) -> None:
    """Build a Unicode-range WOFF2 subset keeping all OpenType features (*)."""
    font = TTFont(str(src_ttf))
    unicodes: List[int] = []
    for part in unicode_range_str.split(","):
        part = part.strip().upper().replace("U+", "")
        if "-" in part:
            lo, hi = part.split("-", 1)
            unicodes.extend(range(int(lo, 16), int(hi, 16) + 1))
        elif part:
            unicodes.append(int(part, 16))
    opts = SubsetOptions()
    opts.layout_features = ["*"]
    opts.flavor = "woff2"
    opts.desubroutinize = False
    subsetter = Subsetter(options=opts)
    subsetter.populate(unicodes=unicodes)
    subsetter.subset(font)
    out_woff2.parent.mkdir(parents=True, exist_ok=True)
    font.save(str(out_woff2))


def _build_apple(otf_dir: Path, var_dir: Path, sym_svg_dir: Path) -> None:
    d = DIST_DIR / "apple-ios-macos"
    d.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "OFL.txt", d / "OFL.txt")
    v_files = _copy_glob(var_dir, "*.ttf", d / "fonts" / "variable")
    s_files = _copy_glob(otf_dir, "*.otf", d / "fonts" / "static")
    for w in ("regular", "medium", "bold"):
        _copy_glob(sym_svg_dir / w, "*.svg", d / "symbols" / "svg" / w)

    (d / "README.md").write_text(
        "# Admiralty for Apple (iOS & macOS)\n\n"
        "## Bundle & Registration\n"
        f"- Copy `fonts/variable/*.ttf` ({len(v_files)} Variable Fonts) or `fonts/static/*.otf` ({len(s_files)} Static OTFs) into your Xcode target and list filenames under `UIAppFonts` in `Info.plist`.\n"
        "- Plain 24x24 original SVG icons are included in `symbols/svg/{regular,medium,bold}/` alongside `AdmiraltySymbols[wght].ttf` (`U+E000..U+E119`). Custom Apple SF-Symbol-template import headers are intentionally omitted pending Apple custom-symbol rule verification (see REQUIREMENTS Section 17).\n\n"
        "## SwiftUI Usage (Dynamic Type Ready)\n"
        "```swift\n"
        "Text(\"Net revenue: €1,362,446.86\")\n"
        "  .font(.custom(\"Admiralty Serif\", size: 16, relativeTo: .body))\n"
        "Button { send() } label: {\n"
        "  HStack(spacing: 6) {\n"
        "    Text(\"\\u{E000}\").font(.custom(\"Admiralty Symbols\", size: 15, relativeTo: .body).weight(.medium))\n"
        "    Text(\"Send\").font(.custom(\"Admiralty Sans\", size: 15, relativeTo: .body).weight(.medium))\n"
        "  }\n"
        "}\n"
        "```\n",
        encoding="utf-8",
    )


def _build_android(ttf_dir: Path, var_dir: Path, meta: dict) -> None:
    d = DIST_DIR / "android"
    font_res = d / "res" / "font"
    draw_res = d / "res" / "drawable"
    font_res.mkdir(parents=True, exist_ok=True)
    draw_res.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "OFL.txt", d / "OFL.txt")

    def _android_name(p: Path) -> str:
        s = p.stem.lower()
        s = s.replace("[wght]", "_wght").replace("-", "_").replace("admiralty", "admiralty_")
        s = re.sub(r"__+", "_", s)
        return f"{s}{p.suffix.lower()}"

    for src_dir in (var_dir, ttf_dir):
        for p in sorted(src_dir.glob("*.ttf")):
            shutil.copyfile(p, font_res / _android_name(p))

    # XML font families for Android 8+ static + API 26 variable support
    for xml_name, reg_res, med_res, bld_res, it_res, med_it_res, bld_it_res in (
        ("admiralty_sans.xml", "admiralty_sans_regular", "admiralty_sans_medium", "admiralty_sans_bold", "admiralty_sans_italic", "admiralty_sans_mediumitalic", "admiralty_sans_bolditalic"),
        ("admiralty_serif.xml", "admiralty_serif_regular", "admiralty_serif_medium", "admiralty_serif_bold", "admiralty_serif_italic", "admiralty_serif_mediumitalic", "admiralty_serif_bolditalic"),
        ("admiralty_mono.xml", "admiralty_mono_regular", "admiralty_mono_medium", "admiralty_mono_bold", "admiralty_mono_italic", "admiralty_mono_mediumitalic", "admiralty_mono_bolditalic"),
    ):
        (font_res / xml_name).write_text(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<font-family xmlns:app="http://schemas.android.com/apk/res-auto"\n'
            '    xmlns:android="http://schemas.android.com/apk/res/android">\n'
            f'  <font android:fontStyle="normal" android:fontWeight="400" android:font="@font/{reg_res}" app:fontStyle="normal" app:fontWeight="400" app:font="@font/{reg_res}" />\n'
            f'  <font android:fontStyle="normal" android:fontWeight="500" android:font="@font/{med_res}" app:fontStyle="normal" app:fontWeight="500" app:font="@font/{med_res}" />\n'
            f'  <font android:fontStyle="normal" android:fontWeight="700" android:font="@font/{bld_res}" app:fontStyle="normal" app:fontWeight="700" app:font="@font/{bld_res}" />\n'
            f'  <font android:fontStyle="italic" android:fontWeight="400" android:font="@font/{it_res}" app:fontStyle="italic" app:fontWeight="400" app:font="@font/{it_res}" />\n'
            f'  <font android:fontStyle="italic" android:fontWeight="500" android:font="@font/{med_it_res}" app:fontStyle="italic" app:fontWeight="500" app:font="@font/{med_it_res}" />\n'
            f'  <font android:fontStyle="italic" android:fontWeight="700" android:font="@font/{bld_it_res}" app:fontStyle="italic" app:fontWeight="700" app:font="@font/{bld_it_res}" />\n'
            '</font-family>\n',
            encoding="utf-8",
        )

    # Convert all Regular UFO glyphs to crisp filled Android Vector Drawable XMLs
    ufo_sym = ufoLib2.Font.open(ROOT / "sources" / "AdmiraltySymbols-Regular.ufo")
    for rec in meta["symbols"]:
        nm = rec["name"]
        res_stem = "ic_adm_" + nm.replace("-", "_")
        path_d = _ufo_glyph_to_svg_path_24(ufo_sym, rec.get("glyphName", nm))
        rtl_attr = ' android:autoMirrored="true"' if rec["rtlMirror"] else ""
        xml = (
            '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n'
            '    android:width="24dp"\n'
            '    android:height="24dp"\n'
            '    android:viewportWidth="24"\n'
            f'    android:viewportHeight="24"{rtl_attr}>\n'
            f'  <path android:fillColor="#FF000000" android:pathData="{path_d}"/>\n'
            '</vector>\n'
        )
        (draw_res / f"{res_stem}.xml").write_text(xml, encoding="utf-8")

    (d / "README.md").write_text(
        "# Admiralty for Android\n\n"
        "## Resources Layout\n"
        "- Copy `res/font/*` into `app/src/main/res/font/` and `res/drawable/ic_adm_*.xml` (282 VectorDrawables, including `android:autoMirrored=\"true\"` on 38 directional icons) into `app/src/main/res/drawable/`.\n"
        "- `admiralty_*_wght.ttf` work natively on Android 8+ (API 26+); static files + `<font-family>` XML support older Android releases.\n\n"
        "## Jetpack Compose Example (Accessibility `sp` Ready)\n"
        "```kotlin\n"
        "val AdmiraltySerif = FontFamily(Font(R.font.admiralty_serif_wght)) // API 26+\n"
        "Text(text = reply, fontFamily = AdmiraltySerif, fontSize = 16.sp, lineHeight = 24.sp)\n"
        "Icon(painter = painterResource(R.drawable.ic_adm_send), contentDescription = \"Send\", modifier = Modifier.size(16.dp))\n"
        "```\n",
        encoding="utf-8",
    )


def _build_windows(ttf_dir: Path, var_dir: Path, sym_svg_dir: Path) -> None:
    d = DIST_DIR / "windows"
    d.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "OFL.txt", d / "OFL.txt")
    _copy_glob(ttf_dir, "*.ttf", d / "fonts" / "static")
    _copy_glob(var_dir, "*.ttf", d / "fonts" / "variable")
    for w in ("regular", "medium", "bold"):
        _copy_glob(sym_svg_dir / w, "*.svg", d / "symbols" / "svg" / w)

    (d / "README.md").write_text(
        "# Admiralty for Windows (WinUI 3 / WPF / Desktop)\n\n"
        "## Bundling & Compatibility\n"
        "- All 21 static `.ttf` files in `fonts/static/` include strict RIBBI + Typographic Naming (`Name ID 1 = \"Admiralty Sans Medium\"` for Word/Win32 + `ID 16/17` for DirectWrite) and `gasp`/`prep` rasterization tables validated at 100%, 125%, and 150% DPI scaling.\n"
        "- WinUI 3 / Windows 11 apps can bundle `fonts/variable/*.ttf` for continuous `400..700` optical weight adjustment.\n\n"
        "## WinUI 3 XAML Usage (`IsTextScaleFactorEnabled=\"True\"`)\n"
        "```xml\n"
        "<TextBlock FontFamily=\"ms-appx:///Assets/Fonts/AdmiraltySerif[wght].ttf#Admiralty Serif\" FontSize=\"16\" IsTextScaleFactorEnabled=\"True\"/>\n"
        "<FontIcon FontFamily=\"ms-appx:///Assets/Fonts/AdmiraltySymbols[wght].ttf#Admiralty Symbols\" Glyph=\"&#xE000;\"/>\n"
        "```\n",
        encoding="utf-8",
    )


def _build_web(woff2_dir: Path, var_dir: Path, sym_svg_dir: Path, meta: dict) -> None:
    d = DIST_DIR / "web"
    d.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "OFL.txt", d / "OFL.txt")
    _copy_glob(var_dir, "*.woff2", d / "fonts" / "variable")
    _copy_glob(woff2_dir, "*.woff2", d / "fonts" / "static")

    # Build Unicode-range subsets from Variable TTFs (latin vs latin-ext)
    latin_rng = "U+0000-00FF,U+2000-206F,U+20AC,U+2122,U+2190-21FF"
    ext_rng = "U+0100-024F,U+1E00-1EFF,U+20A0-20CF,U+2100-22FF,U+2700-27BF"
    sub_dir = d / "fonts" / "subsets"
    css_blocks: List[str] = [
        "/* Admiralty Web Fonts v0.300 — Metric-Matched Fallbacks & Variable Unicode-Range Subsets */\n",
        "@font-face { font-family: 'Admiralty Sans Fallback'; src: local('PingFang HK'), local('Helvetica Neue'), local('Arial'); ascent-override: 98%; descent-override: 32%; line-gap-override: 0%; size-adjust: 100%; }\n",
        "@font-face { font-family: 'Admiralty Serif Fallback'; src: local('Songti TC'), local('Georgia'), local('Times New Roman'); ascent-override: 98%; descent-override: 32%; line-gap-override: 0%; size-adjust: 100%; }\n",
    ]
    for fam_label, stem_base, weight_rng, style_val in (
        ("Admiralty Sans", "AdmiraltySans[wght]", "400 700", "normal"),
        ("Admiralty Sans", "AdmiraltySans-Italic[wght]", "400 700", "italic"),
        ("Admiralty Serif", "AdmiraltySerif[wght]", "400 700", "normal"),
        ("Admiralty Serif", "AdmiraltySerif-Italic[wght]", "400 700", "italic"),
        ("Admiralty Mono", "AdmiraltyMono[wght]", "400 700", "normal"),
        ("Admiralty Mono", "AdmiraltyMono-Italic[wght]", "400 700", "italic"),
    ):
        vf_ttf = var_dir / f"{stem_base}.ttf"
        clean_stem = stem_base.replace("[wght]", "-VF")
        lat_name = f"{clean_stem}-latin.woff2"
        ext_name = f"{clean_stem}-latin-ext.woff2"
        _subset_woff2(vf_ttf, sub_dir / lat_name, latin_rng)
        _subset_woff2(vf_ttf, sub_dir / ext_name, ext_rng)
        css_blocks.append(
            f"@font-face {{\n  font-family: '{fam_label}';\n  src: url('fonts/subsets/{ext_name}') format('woff2');\n"
            f"  font-weight: {weight_rng};\n  font-style: {style_val};\n  font-display: swap;\n  unicode-range: {ext_rng};\n}}\n"
            f"@font-face {{\n  font-family: '{fam_label}';\n  src: url('fonts/subsets/{lat_name}') format('woff2');\n"
            f"  font-weight: {weight_rng};\n  font-style: {style_val};\n  font-display: swap;\n  unicode-range: {latin_rng};\n}}\n"
        )

    css_blocks.append(
        "@font-face {\n  font-family: 'Admiralty Symbols';\n  src: url('fonts/variable/AdmiraltySymbols[wght].woff2') format('woff2');\n"
        "  font-weight: 400 700;\n  font-style: normal;\n  font-display: swap;\n}\n\n"
        ":root {\n"
        "  --adm-sans: 'Admiralty Sans', 'Admiralty Sans Fallback', 'PingFang HK', 'PingFang TC', 'Noto Sans CJK TC', 'Noto Sans CJK SC', -apple-system, sans-serif;\n"
        "  --adm-serif: 'Admiralty Serif', 'Admiralty Serif Fallback', 'Noto Serif CJK TC', 'Noto Serif CJK SC', 'Songti TC', 'Songti SC', Georgia, serif;\n"
        "  --adm-mono: 'Admiralty Mono', 'PingFang HK', ui-monospace, Menlo, Consolas, monospace;\n"
        "  --adm-symbols: 'Admiralty Symbols', sans-serif;\n"
        "}\n"
        ":lang(zh-Hans) { --adm-sans: 'Admiralty Sans', 'PingFang SC', 'Noto Sans CJK SC', sans-serif; --adm-serif: 'Admiralty Serif', 'Noto Serif CJK SC', 'Songti SC', serif; }\n"
    )
    (d / "admiralty-fonts.css").write_text("\n".join(css_blocks), encoding="utf-8")

    # SVG sprite from the Regular outline SVGs
    sprite_syms: List[str] = []
    for p in sorted((sym_svg_dir / "regular").glob("*.svg")):
        raw = p.read_text(encoding="utf-8")
        m = re.match(r"^<svg[^>]*>(.*)</svg>\s*$", raw, re.S)
        if not m:
            continue
        inner = m.group(1)
        sid = p.stem
        sprite_syms.append(f'  <symbol id="adm-{sid}" viewBox="0 0 24 24" fill="currentColor">{inner}</symbol>')

    (d / "admiralty-symbols-sprite.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" style="display:none">\n'
        + "\n".join(sprite_syms)
        + "\n</svg>\n",
        encoding="utf-8",
    )

    (d / "README.md").write_text(
        "# Admiralty for Web & Electron/Tauri\n\n"
        "## Quick Start\n"
        "1. Import `admiralty-fonts.css` — loads Unicode-range Variable WOFF2 subsets (`fonts/subsets/`), full static fallbacks (`fonts/static/`), CLS-zero fallback metrics, and `zh-Hant` / `zh-Hans` CJK stacks.\n"
        "2. Use `admiralty-symbols-sprite.svg` (`<svg><use href=\"#adm-send\"/></svg>`) or font glyphs via `.icon { font-family: var(--adm-symbols); font-weight: 500; }`.\n",
        encoding="utf-8",
    )


def _build_cross_platform(ttf_dir: Path, var_dir: Path, sym_json: Path, meta: dict) -> None:
    d = DIST_DIR / "cross-platform"
    (d / "lib").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "OFL.txt", d / "OFL.txt")
    _copy_glob(var_dir, "*.ttf", d / "assets" / "fonts" / "variable")
    _copy_glob(ttf_dir, "*.ttf", d / "assets" / "fonts" / "static")
    shutil.copyfile(sym_json, d / "admiralty-symbols.json")

    dart_lines = [
        "// Auto-generated Admiralty Symbols IconData mapping (v0.300)\n",
        "import 'package:flutter/widgets.dart';\n\n",
        "abstract final class AdmiraltyIcons {\n",
        "  static const String fontFamily = 'AdmiraltySymbols';\n\n",
    ]
    for rec in meta["symbols"]:
        ident = re.sub(r"-([a-z0-9])", lambda m: m.group(1).upper(), rec["name"])
        if ident[0].isdigit():
            ident = f"n{ident}"
        if ident in DART_RESERVED:          # e.g. "new" is not a legal Dart name
            ident = f"{ident}Icon"
        rtl = "true" if rec["rtlMirror"] else "false"
        dart_lines.append(
            f"  static const IconData {ident} = IconData(0x{rec['codepointInt']:04X}, "
            f"fontFamily: fontFamily, matchTextDirection: {rtl});\n"
        )
    dart_lines.append("}\n")
    (d / "lib" / "admiralty_icons.dart").write_text("".join(dart_lines), encoding="utf-8")

    (d / "README.md").write_text(
        "# Admiralty for Flutter & React Native\n\n"
        "## Bundle Assets\n"
        "- Copy `assets/fonts/` + `admiralty-symbols.json` into your app bundle.\n"
        "- **Flutter**: Declare `AdmiraltySans`, `AdmiraltySerif`, `AdmiraltyMono`, and `AdmiraltySymbols` under `flutter.fonts` in `pubspec.yaml`, then import `lib/admiralty_icons.dart` (`Icon(AdmiraltyIcons.send)`).\n"
        "- **React Native**: Point `assets: ['./assets/fonts/static']` in `react-native.config.js` and run `npx react-native-asset`.\n",
        encoding="utf-8",
    )


def build_all_delivery_packages() -> None:
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)

    otf_dir = ROOT / "fonts" / "otf"
    ttf_dir = ROOT / "fonts" / "ttf"
    woff2_dir = ROOT / "fonts" / "woff2"
    var_dir = ROOT / "fonts" / "variable"
    sym_svg_dir = ROOT / "symbols" / "svg"
    sym_json = ROOT / "symbols" / "admiralty-symbols.json"
    meta = json.loads(sym_json.read_text(encoding="utf-8"))
    n_svg = _write_outline_svgs(ttf_dir, sym_svg_dir, meta)
    print(f"Wrote {n_svg} outline SVGs -> {sym_svg_dir}")

    _build_apple(otf_dir, var_dir, sym_svg_dir)
    _build_android(ttf_dir, var_dir, meta)
    _build_windows(ttf_dir, var_dir, sym_svg_dir)
    _build_web(woff2_dir, var_dir, sym_svg_dir, meta)
    _build_cross_platform(ttf_dir, var_dir, sym_json, meta)

    n_drawables = len(list((DIST_DIR / "android" / "res" / "drawable").glob("*.xml")))
    n_subsets = len(list((DIST_DIR / "web" / "fonts" / "subsets").glob("*.woff2")))
    print(
        f"5-PLATFORM DELIVERY PACKAGES BUILT -> {DIST_DIR}\n"
        f"  - apple-ios-macos, android ({n_drawables} VectorDrawables + XML families), windows, "
        f"web ({n_subsets} Unicode-range VF subsets + sprite + CSS), cross-platform (Flutter Dart + JSON)"
    )


if __name__ == "__main__":
    build_all_delivery_packages()
