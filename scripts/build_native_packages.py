"""
Native packages that let an app use Admiralty Symbols by name, much like SF Symbols:

  * iOS  — a Swift package `AdmiraltySymbols` (dist/apple-ios-macos/AdmiraltySymbols/)
             Image(admiralty: .heartFilled)      Text(admiralty: "heart-filled")
             AdmiraltyIcon("heart-filled")        UIImage.admiralty(.heartFilled)
  * Android — a library module `admiralty-symbols` (dist/android/admiralty-symbols/)
             painterResource(AdmiraltySymbol.HeartFilled.drawable)
             AdmiraltySymbol.named("heart-filled")

Both are generated from symbols/admiralty-symbols.json, so names and code points always match
the fonts. Called by build_delivery.py.
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
// MARK: - Weights

/// The three weights of Admiralty Symbols. Match them to the text next to the icon:
/// regular for body text, medium for buttons and labels, bold for bold text.
public enum AdmiraltySymbolWeight: Sendable {
    case regular, medium, bold

    public var postScriptName: String {
        switch self {
        case .regular: return "AdmiraltySymbols-Regular"
        case .medium: return "AdmiraltySymbols-Medium"
        case .bold: return "AdmiraltySymbols-Bold"
        }
    }
}

// MARK: - Font registration

public enum AdmiraltySymbols {
    /// Registers the three symbol fonts that ship inside this package. Every helper below calls
    /// it, so you only need it yourself to use the fonts directly (for example in a UIFont).
    public static func registerFonts() {
        _ = registered
    }

    private static let registered: Bool = {
        for name in ["AdmiraltySymbols-Regular", "AdmiraltySymbols-Medium", "AdmiraltySymbols-Bold"] {
            if let url = Bundle.module.url(forResource: name, withExtension: "ttf", subdirectory: "Fonts") {
                CTFontManagerRegisterFontsForURL(url as CFURL, .process, nil)
            }
        }
        return true
    }()
}

// MARK: - SwiftUI

public extension Text {
    /// An Admiralty symbol as text. It scales with Dynamic Type, sits on the text baseline and
    /// takes the foreground colour, so it can be joined with other text:
    /// `Text(admiralty: .heartFilled) + Text(" Liked")`.
    init(admiralty symbol: AdmiraltySymbol, size: CGFloat = 17, relativeTo textStyle: Font.TextStyle = .body,
         weight: AdmiraltySymbolWeight = .regular) {
        AdmiraltySymbols.registerFonts()
        self = Text(verbatim: symbol.character)
            .font(.custom(weight.postScriptName, size: size, relativeTo: textStyle))
    }

    /// The same, by name, like `Image(systemName:)`. An unknown name gives empty text.
    init(admiralty name: String, size: CGFloat = 17, relativeTo textStyle: Font.TextStyle = .body,
         weight: AdmiraltySymbolWeight = .regular) {
        AdmiraltySymbols.registerFonts()
        self = Text(verbatim: AdmiraltySymbol(rawValue: name)?.character ?? "")
            .font(.custom(weight.postScriptName, size: size, relativeTo: textStyle))
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
    private let weight: AdmiraltySymbolWeight

    public init(_ symbol: AdmiraltySymbol, size: CGFloat = 17, relativeTo textStyle: Font.TextStyle = .body,
                weight: AdmiraltySymbolWeight = .regular) {
        self.symbol = symbol
        self.size = size
        self.textStyle = textStyle
        self.weight = weight
    }

    public init(_ name: String, size: CGFloat = 17, relativeTo textStyle: Font.TextStyle = .body,
                weight: AdmiraltySymbolWeight = .regular) {
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
    init(admiralty symbol: AdmiraltySymbol, pointSize: CGFloat = 17, weight: AdmiraltySymbolWeight = .regular) {
        self = Image(uiImage: UIImage.admiralty(symbol, pointSize: pointSize, weight: weight))
            .renderingMode(.template)
    }

    /// The same, by name. An unknown name gives an empty image.
    init(admiralty name: String, pointSize: CGFloat = 17, weight: AdmiraltySymbolWeight = .regular) {
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
                          weight: AdmiraltySymbolWeight = .regular) -> UIImage {
        AdmiraltySymbols.registerFonts()
        let font = UIFont(name: weight.postScriptName, size: pointSize) ?? UIFont.systemFont(ofSize: pointSize)
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
                          weight: AdmiraltySymbolWeight = .regular) -> UIImage? {
        guard let symbol = AdmiraltySymbol(rawValue: name) else { return nil }
        return admiralty(symbol, pointSize: pointSize, weight: weight)
    }
}
#endif
'''


def build_swift_package(meta: dict, ttf_dir: Path, out_root: Path, version: str) -> Path:
    pkg = out_root / "AdmiraltySymbols"
    if pkg.exists():
        shutil.rmtree(pkg)
    src = pkg / "Sources" / "AdmiraltySymbols"
    (src / "Fonts").mkdir(parents=True)
    for w in ("Regular", "Medium", "Bold"):
        shutil.copyfile(ttf_dir / f"AdmiraltySymbols-{w}.ttf", src / "Fonts" / f"AdmiraltySymbols-{w}.ttf")
    shutil.copyfile(ROOT / "OFL.txt", pkg / "OFL.txt")

    (pkg / "Package.swift").write_text(
        "// swift-tools-version:5.7\n"
        "import PackageDescription\n\n"
        "let package = Package(\n"
        '    name: "AdmiraltySymbols",\n'
        "    platforms: [.iOS(.v15)],\n"
        '    products: [.library(name: "AdmiraltySymbols", targets: ["AdmiraltySymbols"])],\n'
        "    targets: [\n"
        '        .target(name: "AdmiraltySymbols", resources: [.copy("Fonts")])\n'
        "    ]\n"
        ")\n",
        encoding="utf-8",
    )

    syms = meta["symbols"]
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
        f"/// All {len(syms)} Admiralty Symbols. The raw value is the symbol's name, as in the\n"
        "/// SVG files and the inspector: `AdmiraltySymbol(rawValue: \"heart-filled\")`.\n"
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
    (src / "AdmiraltySymbols.swift").write_text(body, encoding="utf-8")
    return pkg


# ---------------------------------------------------------------------------------------------
# Android: library module
# ---------------------------------------------------------------------------------------------

def build_android_library(meta: dict, ttf_dir: Path, drawable_dir: Path, out_root: Path, version: str) -> Path:
    mod = out_root / "admiralty-symbols"
    if mod.exists():
        shutil.rmtree(mod)
    pkg_name = "io.github.cosmoluei.admiralty.symbols"
    main = mod / "src" / "main"
    kt_dir = main / "kotlin" / Path(*pkg_name.split("."))
    kt_dir.mkdir(parents=True)
    (main / "res" / "drawable").mkdir(parents=True)
    (main / "res" / "font").mkdir(parents=True)
    for p in sorted(drawable_dir.glob("ic_adm_*.xml")):
        shutil.copyfile(p, main / "res" / "drawable" / p.name)
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
    for s in meta["symbols"]:
        res = "ic_adm_" + s["name"].replace("-", "_")
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
    return mod
