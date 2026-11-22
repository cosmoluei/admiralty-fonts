"""
Ready-to-use packages, so an app (or a coding agent) can use the fonts and the symbols by name,
much like SF Symbols. All are written to packages/ (tracked in git) by build_delivery.py:

  * iOS     packages/ios/Admiralty           Swift package (Package.swift at the repo root)
              .font(.admiralty(.serif, size: 17))   AdmiraltyIcon("heart-filled")
  * Android packages/android/admiralty        library module (fonts + symbol vector drawables)
              AdmiraltySymbol.HeartFilled.drawable   AdmiraltyFonts.SANS
  * Flutter packages/flutter/admiralty        Dart package with the fonts
              Icon(AdmiraltyIcons.heartFilled)       TextStyle(fontFamily: 'AdmiraltySans', package: 'admiralty')
  * Web     packages/web                      CSS with the fonts and icon classes
              <i class="adm-icon adm-heart-filled"></i>

Everything is generated from symbols/admiralty-symbols.json, so names and code points always
match the fonts.
"""

from __future__ import annotations
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SWIFT_KEYWORDS = {
    "associatedtype", "class", "deinit", "enum", "extension", "fileprivate", "func", "import", "init",
    "inout", "internal", "let", "open", "operator", "private", "protocol", "public", "rethrows",
    "static", "struct", "subscript", "typealias", "var", "break", "case", "continue", "default",
    "defer", "do", "else", "fallthrough", "for", "guard", "if", "in", "repeat", "return", "switch",
    "where", "while", "as", "catch", "false", "is", "nil", "super", "self", "throw", "throws", "true",
    "try", "Any", "Type", "some", "any",
}


def public_symbols(meta: dict):
    """Resolve API spellings while sharing the canonical font and vector artwork."""
    catalog = {s["name"]: s for s in meta["symbols"]}
    yield from catalog.values()
    for alias, target in meta.get("aliases", {}).items():
        if alias in catalog:
            raise ValueError(f"Alias shadows symbol {alias}")
        item = catalog[target]
        label = "Globe" if alias == "globe" else item["label"]
        yield {**item, "name": alias, "assetName": target, "label": label}


def _camel(name: str) -> str:
    return re.sub(r"-([a-z0-9])", lambda m: m.group(1).upper(), name)


def _pascal(name: str) -> str:
    c = _camel(name)
    return c[0].upper() + c[1:]


def _swift_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _kotlin_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$") + '"'


# ---------------------------------------------------------------------------------------------
# iOS: Swift package
# ---------------------------------------------------------------------------------------------

SWIFT_SUPPORT = r'''
// MARK: - Weights and families

/// The three weights of every Admiralty family. For symbols, match the text next to the icon:
/// regular for body text, medium for buttons and labels, bold for bold text.
public enum AdmiraltyWeight: Sendable {
    case regular, medium, bold

    fileprivate var styleName: String {
        switch self {
        case .regular: return "Regular"
        case .medium: return "Medium"
        case .bold: return "Bold"
        }
    }

    /// The PostScript name of the Admiralty Symbols font in this weight.
    public var symbolsPostScriptName: String { "AdmiraltySymbols-" + styleName }
}

/// The three text families. Sans: interface and the user's messages. Serif: the agent's
/// messages (same widths as Sans, so switching never changes line breaks). Mono: code and IDs.
public enum AdmiraltyFamily: Sendable {
    case sans, serif, mono

    fileprivate var postScriptFamily: String {
        switch self {
        case .sans: return "AdmiraltySans"
        case .serif: return "AdmiraltySerif"
        case .mono: return "AdmiraltyMono"
        }
    }

    /// The PostScript name of one style, e.g. "AdmiraltySerif-MediumItalic".
    public func postScriptName(weight: AdmiraltyWeight = .regular, italic: Bool = false) -> String {
        let style: String
        switch (weight, italic) {
        case (.regular, false): style = "Regular"
        case (.regular, true): style = "Italic"
        case (_, false): style = weight.styleName
        case (_, true): style = weight.styleName + "Italic"
        }
        return postScriptFamily + "-" + style
    }
}

// MARK: - Font registration

public enum Admiralty {
    /// Registers all Admiralty fonts that ship inside this package (Sans, Serif, Mono and Symbols,
    /// 21 styles). Every helper calls it; call it yourself before using a font by name in UIKit.
    public static func registerFonts() {
        _ = registered
    }

    private static let registered: Bool = {
        for url in Bundle.module.urls(forResourcesWithExtension: "ttf", subdirectory: "Fonts") ?? [] {
            CTFontManagerRegisterFontsForURL(url as CFURL, .process, nil)
        }
        return true
    }()
}

// MARK: - Text fonts

public extension Font {
    /// An Admiralty text font that scales with Dynamic Type:
    /// `.font(.admiralty(.serif, size: 17))`, `.font(.admiralty(.mono, size: 14, relativeTo: .callout))`.
    static func admiralty(_ family: AdmiraltyFamily = .sans, size: CGFloat, relativeTo textStyle: Font.TextStyle = .body,
                          weight: AdmiraltyWeight = .regular, italic: Bool = false) -> Font {
        Admiralty.registerFonts()
        return .custom(family.postScriptName(weight: weight, italic: italic), size: size, relativeTo: textStyle)
    }
}

#if canImport(UIKit)
public extension UIFont {
    /// An Admiralty text font for UIKit, scaled for the user's text size setting.
    static func admiralty(_ family: AdmiraltyFamily = .sans, size: CGFloat, textStyle: UIFont.TextStyle = .body,
                          weight: AdmiraltyWeight = .regular, italic: Bool = false) -> UIFont {
        Admiralty.registerFonts()
        let base = UIFont(name: family.postScriptName(weight: weight, italic: italic), size: size)
            ?? UIFont.systemFont(ofSize: size)
        return UIFontMetrics(forTextStyle: textStyle).scaledFont(for: base)
    }
}
#endif

// MARK: - SwiftUI

public extension Text {
    /// An Admiralty symbol as text. It scales with Dynamic Type, sits on the text baseline and
    /// takes the foreground colour, so it can be joined with other text:
    /// `Text(admiralty: .heartFilled) + Text(" Liked")`.
    init(admiralty symbol: AdmiraltySymbol, size: CGFloat = 17, relativeTo textStyle: Font.TextStyle = .body,
         weight: AdmiraltyWeight = .regular) {
        Admiralty.registerFonts()
        self = Text(verbatim: symbol.character)
            .font(.custom(weight.symbolsPostScriptName, size: size, relativeTo: textStyle))
    }

    /// The same, by name, like `Image(systemName:)`. An unknown name gives empty text.
    init(admiralty name: String, size: CGFloat = 17, relativeTo textStyle: Font.TextStyle = .body,
         weight: AdmiraltyWeight = .regular) {
        Admiralty.registerFonts()
        self = Text(verbatim: AdmiraltySymbol(rawValue: name)?.character ?? "")
            .font(.custom(weight.symbolsPostScriptName, size: size, relativeTo: textStyle))
    }
}

/// A ready-made icon view: scales with Dynamic Type, mirrors in right-to-left layouts when the
/// symbol should, and reads its name to VoiceOver.
///
///     AdmiraltyIcon("heart-filled")
///     AdmiraltyIcon(.send, size: 20, weight: .medium).foregroundStyle(.blue)
public struct AdmiraltyIcon: View {
    private let symbol: AdmiraltySymbol?
    private let size: CGFloat
    private let textStyle: Font.TextStyle
    private let weight: AdmiraltyWeight

    public init(_ symbol: AdmiraltySymbol, size: CGFloat = 17, relativeTo textStyle: Font.TextStyle = .body,
                weight: AdmiraltyWeight = .regular) {
        self.symbol = symbol
        self.size = size
        self.textStyle = textStyle
        self.weight = weight
    }

    public init(_ name: String, size: CGFloat = 17, relativeTo textStyle: Font.TextStyle = .body,
                weight: AdmiraltyWeight = .regular) {
        self.symbol = AdmiraltySymbol(rawValue: name)
        self.size = size
        self.textStyle = textStyle
        self.weight = weight
    }

    public var body: some View {
        if let symbol = symbol {
            Text(admiralty: symbol, size: size, relativeTo: textStyle, weight: weight)
                .flipsForRightToLeftLayoutDirection(symbol.mirrorsInRightToLeft)
                .accessibilityLabel(Text(symbol.accessibilityLabel))
        }
    }
}

#if canImport(UIKit)
public extension Image {
    /// An Admiralty symbol as a template image (it takes the tint or foreground colour).
    /// Its size is fixed by `pointSize`; use `Text(admiralty:)` or `AdmiraltyIcon` for an icon
    /// that grows with Dynamic Type.
    init(admiralty symbol: AdmiraltySymbol, pointSize: CGFloat = 17, weight: AdmiraltyWeight = .regular) {
        self = Image(uiImage: UIImage.admiralty(symbol, pointSize: pointSize, weight: weight))
            .renderingMode(.template)
    }

    /// The same, by name. An unknown name gives an empty image.
    init(admiralty name: String, pointSize: CGFloat = 17, weight: AdmiraltyWeight = .regular) {
        if let symbol = AdmiraltySymbol(rawValue: name) {
            self.init(admiralty: symbol, pointSize: pointSize, weight: weight)
        } else {
            self = Image(uiImage: UIImage())
        }
    }
}

// MARK: - UIKit

public extension UIImage {
    /// An Admiralty symbol as a template UIImage, for UIImageView, UIButton, tab bars and so on.
    /// The image is the symbol's full 24 x 24 grid box, so all symbols line up.
    static func admiralty(_ symbol: AdmiraltySymbol, pointSize: CGFloat = 17,
                          weight: AdmiraltyWeight = .regular) -> UIImage {
        Admiralty.registerFonts()
        let font = UIFont(name: weight.symbolsPostScriptName, size: pointSize) ?? UIFont.systemFont(ofSize: pointSize)
        // The symbol grid is 864 units square (24 x 36), from x = -12 and from 782 above the baseline.
        let side = (pointSize * 0.864).rounded(.up)
        let renderer = UIGraphicsImageRenderer(size: CGSize(width: side, height: side))
        let image = renderer.image { _ in
            let attributes: [NSAttributedString.Key: Any] = [.font: font, .foregroundColor: UIColor.black]
            let origin = CGPoint(x: pointSize * 0.012, y: pointSize * 0.782 - font.ascender)
            (symbol.character as NSString).draw(at: origin, withAttributes: attributes)
        }
        let template = image.withRenderingMode(.alwaysTemplate)
        return symbol.mirrorsInRightToLeft ? template.imageFlippedForRightToLeftLayoutDirection() : template
    }

    /// The same, by name, like `UIImage(systemName:)`. Returns nil for an unknown name.
    static func admiralty(named name: String, pointSize: CGFloat = 17,
                          weight: AdmiraltyWeight = .regular) -> UIImage? {
        guard let symbol = AdmiraltySymbol(rawValue: name) else { return nil }
        return admiralty(symbol, pointSize: pointSize, weight: weight)
    }
}
#endif
'''


def build_swift_package(meta: dict, ttf_dir: Path, out_root: Path, version: str) -> Path:
    pkg = out_root / "Admiralty"
    if pkg.exists():
        shutil.rmtree(pkg)
    src = pkg / "Sources" / "Admiralty"
    (src / "Fonts").mkdir(parents=True)
    for p in sorted(ttf_dir.glob("Admiralty*.ttf")):          # all 21 static styles
        shutil.copyfile(p, src / "Fonts" / p.name)
    shutil.copyfile(ROOT / "OFL.txt", pkg / "OFL.txt")

    (pkg / "Package.swift").write_text(
        "// swift-tools-version:5.7\n"
        "import PackageDescription\n\n"
        "let package = Package(\n"
        '    name: "Admiralty",\n'
        "    platforms: [.iOS(.v15)],\n"
        '    products: [.library(name: "Admiralty", targets: ["Admiralty"])],\n'
        "    targets: [\n"
        '        .target(name: "Admiralty", resources: [.copy("Fonts")])\n'
        "    ]\n"
        ")\n",
        encoding="utf-8",
    )

    syms = list(public_symbols(meta))
    cases, cps, rtl, labels = [], [], [], []
    for s in syms:
        c = _camel(s["name"])
        decl = f"`{c}`" if c in SWIFT_KEYWORDS else c
        cases.append(f"    case {decl} = {_swift_str(s['name'])}")
        cps.append(f"        case .{decl}: return 0x{s['codepointInt']:04X}")
        labels.append(f"        case .{decl}: return {_swift_str(s['label'])}")
        if s["rtlMirror"]:
            rtl.append(f".{decl}")
    body = (
        f"// Generated from admiralty-symbols.json (Admiralty {version}). Do not edit by hand.\n"
        "// Licensed under the SIL Open Font License 1.1 (see OFL.txt).\n\n"
        "import SwiftUI\nimport CoreText\n#if canImport(UIKit)\nimport UIKit\n#endif\n\n"
        f"/// Names for {len(meta['symbols'])} Admiralty Symbols, including their public aliases.\n"
        "/// Look up a symbol with `AdmiraltySymbol(rawValue: \"heart-filled\")`.\n"
        "public enum AdmiraltySymbol: String, CaseIterable, Sendable {\n"
        + "\n".join(cases)
        + "\n\n    /// The Private Use Area code point of the symbol in the Admiralty Symbols font.\n"
        "    public var codepoint: UInt32 {\n        switch self {\n" + "\n".join(cps) + "\n        }\n    }\n\n"
        "    /// A short English name for VoiceOver. (Not called `label`, because one symbol is named label.)\n"
        "    public var accessibilityLabel: String {\n        switch self {\n" + "\n".join(labels) + "\n        }\n    }\n\n"
        "    /// True for direction symbols (send, back, reply ...) that mirror in right-to-left languages.\n"
        "    public var mirrorsInRightToLeft: Bool {\n        switch self {\n"
        f"        case {', '.join(rtl)}: return true\n"
        "        default: return false\n        }\n    }\n\n"
        "    /// The symbol as a one-character string in the Admiralty Symbols font.\n"
        "    public var character: String {\n"
        "        String(Character(Unicode.Scalar(codepoint)!))\n    }\n}\n"
        + SWIFT_SUPPORT
    )
    (src / "Admiralty.swift").write_text(body, encoding="utf-8")
    return pkg


# ---------------------------------------------------------------------------------------------
# Android: library module
# ---------------------------------------------------------------------------------------------

def build_android_library(meta: dict, ttf_dir: Path, drawable_dir: Path, out_root: Path, version: str) -> Path:
    mod = out_root / "admiralty"
    if mod.exists():
        shutil.rmtree(mod)
    pkg_name = "io.github.cosmoluei.admiralty"
    main = mod / "src" / "main"
    kt_dir = main / "kotlin" / Path(*pkg_name.split("."))
    kt_dir.mkdir(parents=True)
    (main / "res" / "drawable").mkdir(parents=True)
    (main / "res" / "font").mkdir(parents=True)
    for p in sorted(drawable_dir.glob("ic_adm_*.xml")):
        shutil.copyfile(p, main / "res" / "drawable" / p.name)
    # text fonts: the static styles and their <font-family> XML files (Sans, Serif, Mono)
    font_src = drawable_dir.parent / "font"
    for p in sorted(font_src.iterdir()):
        if p.suffix == ".xml" or (p.suffix == ".ttf" and not p.stem.endswith("_wght")):
            shutil.copyfile(p, main / "res" / "font" / p.name)
    for w in ("Regular", "Medium", "Bold"):
        shutil.copyfile(ttf_dir / f"AdmiraltySymbols-{w}.ttf",
                        main / "res" / "font" / f"admiralty_symbols_{w.lower()}.ttf")
    shutil.copyfile(ROOT / "OFL.txt", mod / "OFL.txt")
    (main / "AndroidManifest.xml").write_text('<manifest xmlns:android="http://schemas.android.com/apk/res/android" />\n',
                                              encoding="utf-8")
    (mod / "build.gradle.kts").write_text(
        "plugins {\n"
        '    id("com.android.library")\n'
        '    id("org.jetbrains.kotlin.android")\n'
        "}\n\n"
        "android {\n"
        f'    namespace = "{pkg_name}"\n'
        "    compileSdk = 35\n"
        "    defaultConfig { minSdk = 21 }\n"
        "    compileOptions {\n"
        "        sourceCompatibility = JavaVersion.VERSION_17\n"
        "        targetCompatibility = JavaVersion.VERSION_17\n"
        "    }\n"
        '    kotlinOptions { jvmTarget = "17" }\n'
        "}\n",
        encoding="utf-8",
    )
    entries = []
    for s in public_symbols(meta):
        res = "ic_adm_" + s.get("assetName", s["name"]).replace("-", "_")
        entries.append(
            f"    {_pascal(s['name'])}({_kotlin_str(s['name'])}, {_kotlin_str(s['label'])}, "
            f"R.drawable.{res}, 0x{s['codepointInt']:04X}, {'true' if s['rtlMirror'] else 'false'})"
        )
    (kt_dir / "AdmiraltySymbol.kt").write_text(
        f"// Generated from admiralty-symbols.json (Admiralty {version}). Do not edit by hand.\n"
        "// Licensed under the SIL Open Font License 1.1 (see OFL.txt).\n"
        f"package {pkg_name}\n\n"
        f"/**\n * All {len(meta['symbols'])} Admiralty Symbols.\n *\n"
        " * Compose:  Icon(painterResource(AdmiraltySymbol.HeartFilled.drawable), AdmiraltySymbol.HeartFilled.label)\n"
        " * Views:    imageView.setImageResource(AdmiraltySymbol.HeartFilled.drawable)\n"
        " * By name:  AdmiraltySymbol.named(\"heart-filled\")\n"
        " *\n * Direction symbols (mirrorsInRtl) are drawables with android:autoMirrored=\"true\",\n"
        " * so they flip by themselves in right-to-left layouts.\n */\n"
        "enum class AdmiraltySymbol(\n"
        "    /** The symbol's name, as in the SVG files and the inspector. */\n"
        "    val symbolName: String,\n"
        "    /** A short English name for TalkBack (contentDescription). */\n"
        "    val label: String,\n"
        "    /** The vector drawable resource. */\n"
        "    val drawable: Int,\n"
        "    /** The Private Use Area code point in the Admiralty Symbols font. */\n"
        "    val codepoint: Int,\n"
        "    /** True for direction symbols that mirror in right-to-left languages. */\n"
        "    val mirrorsInRtl: Boolean,\n"
        ") {\n"
        + ",\n".join(entries)
        + ";\n\n"
        "    /** The symbol as text in the Admiralty Symbols font (R.font.admiralty_symbols_regular ...). */\n"
        "    val character: String get() = String(Character.toChars(codepoint))\n\n"
        "    companion object {\n"
        "        private val byName: Map<String, AdmiraltySymbol> = values().associateBy { it.symbolName }\n\n"
        "        /** Finds a symbol by its name, like \"heart-filled\". Returns null for an unknown name. */\n"
        "        fun named(name: String): AdmiraltySymbol? = byName[name]\n"
        "    }\n"
        "}\n",
        encoding="utf-8",
    )
    (kt_dir / "AdmiraltyFonts.kt").write_text(
        f"// Generated (Admiralty {version}). Licensed under the SIL Open Font License 1.1.\n"
        f"package {pkg_name}\n\n"
        "/**\n"
        " * Font family resources (Regular 400, Medium 500, Bold 700 and their italics).\n"
        " *\n"
        " * XML:     android:fontFamily=\"@font/admiralty_sans\"\n"
        " * Views:   textView.typeface = ResourcesCompat.getFont(context, AdmiraltyFonts.SANS)\n"
        " * Compose: see AGENTS.md in the Admiralty repository for a ready FontFamily.\n"
        " */\n"
        "object AdmiraltyFonts {\n"
        "    /** Interface text and the user's messages. */\n"
        "    val SANS: Int get() = R.font.admiralty_sans\n"
        "    /** The agent's messages; same widths as Sans, so switching never changes line breaks. */\n"
        "    val SERIF: Int get() = R.font.admiralty_serif\n"
        "    /** Code, logs and IDs (fixed width). */\n"
        "    val MONO: Int get() = R.font.admiralty_mono\n"
        "}\n",
        encoding="utf-8",
    )
    return mod


# ---------------------------------------------------------------------------------------------
# Flutter: Dart package with the fonts
# ---------------------------------------------------------------------------------------------

DART_RESERVED = {
    "assert", "break", "case", "catch", "class", "const", "continue", "default", "do", "else",
    "enum", "extends", "false", "final", "finally", "for", "if", "in", "is", "new", "null",
    "rethrow", "return", "super", "switch", "this", "throw", "true", "try", "var", "void",
    "while", "with",
}


def build_flutter_package(meta: dict, ttf_dir: Path, out_root: Path, version: str) -> Path:
    pkg = out_root / "admiralty"
    if pkg.exists():
        shutil.rmtree(pkg)
    (pkg / "lib").mkdir(parents=True)
    (pkg / "fonts").mkdir()
    for p in sorted(ttf_dir.glob("Admiralty*.ttf")):
        shutil.copyfile(p, pkg / "fonts" / p.name)
    shutil.copyfile(ROOT / "OFL.txt", pkg / "LICENSE")
    fam_yaml = []
    for fam in ("Sans", "Serif", "Mono"):
        fam_yaml.append(f"    - family: Admiralty{fam}\n      fonts:")
        for st, w, it in (("Regular", 400, False), ("Italic", 400, True), ("Medium", 500, False),
                          ("MediumItalic", 500, True), ("Bold", 700, False), ("BoldItalic", 700, True)):
            fam_yaml.append(f"        - asset: fonts/Admiralty{fam}-{st}.ttf\n          weight: {w}"
                            + ("\n          style: italic" if it else ""))
    fam_yaml.append("    - family: AdmiraltySymbols\n      fonts:")
    for st, w in (("Regular", 400), ("Medium", 500), ("Bold", 700)):
        fam_yaml.append(f"        - asset: fonts/AdmiraltySymbols-{st}.ttf\n          weight: {w}")
    (pkg / "pubspec.yaml").write_text(
        "name: admiralty\n"
        "description: Admiralty Sans, Serif, Mono and Symbols fonts, with the symbols as IconData.\n"
        f"version: {version}.0\n"
        "homepage: https://github.com/cosmoluei/admiralty-fonts\n"
        "environment:\n  sdk: '>=3.0.0 <4.0.0'\n  flutter: '>=3.10.0'\n"
        "dependencies:\n  flutter:\n    sdk: flutter\n"
        "flutter:\n  fonts:\n" + "\n".join(fam_yaml) + "\n",
        encoding="utf-8",
    )
    lines, names = [], []
    for s_ in public_symbols(meta):
        ident = _camel(s_["name"])
        if ident in DART_RESERVED:
            ident += "Icon"
        lines.append(f"  static const IconData {ident} = IconData(0x{s_['codepointInt']:04X}, "
                     f"fontFamily: _family, fontPackage: _package, matchTextDirection: {'true' if s_['rtlMirror'] else 'false'});")
        names.append(f"    '{s_['name']}': {ident},")
    (pkg / "lib" / "admiralty.dart").write_text(
        f"// Generated from admiralty-symbols.json (Admiralty {version}). Do not edit by hand.\n"
        "// Licensed under the SIL Open Font License 1.1 (see LICENSE).\n"
        "library admiralty;\n\n"
        "import 'package:flutter/widgets.dart';\n\n"
        "/// Text font families. Use with `package: AdmiraltyFonts.package`:\n"
        "/// `TextStyle(fontFamily: AdmiraltyFonts.serif, package: AdmiraltyFonts.package, fontWeight: FontWeight.w500)`.\n"
        "abstract final class AdmiraltyFonts {\n"
        "  static const String package = 'admiralty';\n"
        "  static const String sans = 'AdmiraltySans';\n"
        "  static const String serif = 'AdmiraltySerif';\n"
        "  static const String mono = 'AdmiraltyMono';\n"
        "  static const String symbols = 'AdmiraltySymbols';\n"
        "}\n\n"
        f"/// All {len(meta['symbols'])} Admiralty Symbols: `Icon(AdmiraltyIcons.heartFilled)`, or by name:\n"
        "/// `Icon(AdmiraltyIcons.named('heart-filled'))`. Direction icons mirror in right-to-left text.\n"
        "abstract final class AdmiraltyIcons {\n"
        "  static const String _family = 'AdmiraltySymbols';\n"
        "  static const String _package = 'admiralty';\n\n"
        + "\n".join(lines)
        + "\n\n  /// Every symbol by its name, as in the SVG files (\"heart-filled\").\n"
        "  static const Map<String, IconData> all = {\n" + "\n".join(names) + "\n  };\n\n"
        "  /// The symbol with this name, or null.\n"
        "  static IconData? named(String name) => all[name];\n"
        "}\n",
        encoding="utf-8",
    )
    return pkg


# ---------------------------------------------------------------------------------------------
# Web: CSS with fonts and icon classes
# ---------------------------------------------------------------------------------------------

def build_web_package(meta: dict, dist_web: Path, var_dir: Path, out_root: Path, version: str) -> Path:
    web = out_root / "web"
    if web.exists():
        shutil.rmtree(web)
    (web / "fonts").mkdir(parents=True)
    shutil.copytree(dist_web / "fonts" / "subsets", web / "fonts" / "subsets")
    italic_dir = web / "fonts" / "variable"
    italic_dir.mkdir()
    for italic in var_dir.glob("*-Italic*.woff2"):
        shutil.copyfile(italic, italic_dir / italic.name)
    # Both stylesheets in the standalone package use the same Symbols font URL.
    symbol_file = "AdmiraltySymbols[wght].woff2"
    symbol_url = "fonts/AdmiraltySymbols-VF.woff2"
    text_css = (dist_web / "admiralty-fonts.css").read_text(encoding="utf-8")
    (web / "admiralty-fonts.css").write_text(
        text_css.replace(f"fonts/variable/{symbol_file}", symbol_url), encoding="utf-8"
    )
    shutil.copyfile(dist_web / "admiralty-symbols-sprite.svg", web / "admiralty-symbols-sprite.svg")
    shutil.copyfile(var_dir / symbol_file, web / symbol_url)
    shutil.copyfile(ROOT / "OFL.txt", web / "OFL.txt")
    rules = []
    for s_ in public_symbols(meta):
        rules.append(f".adm-{s_['name']}::before {{ content: \"\\{s_['codepointInt']:X}\"; }}")
    mirrored = ", ".join(f'.adm-{s_["name"]}:dir(rtl)::before' for s_ in public_symbols(meta) if s_["rtlMirror"])
    (web / "admiralty-symbols.css").write_text(
        f"/* Admiralty Symbols {version}: icons by name. SIL Open Font License 1.1.\n"
        "   <i class=\"adm-icon adm-heart-filled\" aria-hidden=\"true\"></i>\n"
        "   The icon takes the text colour and size; set font-weight 400 / 500 / 700 to match the text. */\n"
        f"@font-face {{\n  font-family: 'Admiralty Symbols';\n  src: url('{symbol_url}') format('woff2');\n"
        "  font-weight: 400 700;\n  font-style: normal;\n  font-display: block;\n}\n"
        ".adm-icon {\n  font-family: 'Admiralty Symbols';\n  font-style: normal;\n  font-weight: inherit;\n"
        "  line-height: 1;\n  display: inline-block;\n  speak: never;\n  -webkit-font-smoothing: antialiased;\n}\n"
        ".adm-icon::before {\n  display: inline-block;\n  direction: ltr;\n  unicode-bidi: isolate;\n"
        '  font-feature-settings: "rtlm" 0;\n}\n'
        + mirrored + " {\n  transform: scaleX(-1);\n}\n"
        + "\n".join(rules) + "\n",
        encoding="utf-8",
    )
    return web
