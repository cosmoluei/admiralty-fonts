# Admiralty: guide for coding agents

This repository holds the **Admiralty** font family and its icon font. Read this file before
adding the fonts or symbols to an app. Everything you need is already built and checked in;
you do not need to run the build scripts to *use* the fonts.

## What is here

| Family | Use it for | Styles |
| --- | --- | --- |
| **Admiralty Sans** | Interface text and the user's own messages | Regular 400, Medium 500, Bold 700, each with Italic |
| **Admiralty Serif** | The agent's (assistant's) messages | Same six styles. Same letter widths and kerning as Sans, so switching between them never changes line breaks |
| **Admiralty Mono** | Code, logs, IDs, terminal output | Same six styles. Every character is 600 units wide. Box drawing `U+2500`–`U+259F` joins at line height 1.3 |
| **Admiralty Symbols** | 311 interface icons on a 24 × 24 grid | Regular, Medium, Bold |

Character coverage: Latin (Google Fonts Latin Core and Latin Plus), Latin Extended-A, Pinyin,
Vietnamese. **No Chinese, Japanese or Korean**: always put a CJK fallback after Admiralty
(for Hong Kong: `PingFang HK`, then `Noto Sans CJK TC`).

Version 0.500 is a test release; names and code points of existing symbols will not change.

## Where things are

| Path | What |
| --- | --- |
| `packages/ios/Admiralty` + `Package.swift` (repo root) | Swift package: all fonts, `Font.admiralty(...)`, `AdmiraltyIcon("name")` |
| `packages/android/admiralty` | Android library module: fonts, `<font-family>` XML, 311 vector drawables, `AdmiraltySymbol` enum |
| `packages/flutter/admiralty` | Flutter package: fonts, `AdmiraltyFonts`, `AdmiraltyIcons` |
| `packages/web` | `admiralty-fonts.css` (text fonts) and `admiralty-symbols.css` (icon classes), with the font files |
| `symbols/admiralty-symbols.json` | **The list of all symbols**: `name`, `label`, `codepoint`, `category`, `tags`, `rtlMirror` |
| `symbols/svg/{regular,medium,bold}/<name>.svg` | Each symbol as a filled SVG (`fill="currentColor"`) |
| `fonts/ttf`, `fonts/otf`, `fonts/woff2`, `fonts/variable` | The raw font files, if a platform has no package |
| `tokens/admiralty-design-tokens.json` | Sizes, line heights, weights per role and OpenType feature settings |
| `docs/USAGE_GUIDE.md` | Longer guide with sizes and do's and don'ts |

## Rules

1. **Find symbols by name in `symbols/admiralty-symbols.json`.** Search `name`, `label` and
   `tags` (for example "like" finds `heart`). The `aliases` map resolves `globe` to
   `language`, `pause-filled` to `pause`, and `phone-off` to `end-call`. Look up the
   canonical name for raw SVG files. Never invent a name, and never hard-code a
   Private Use Area code point such as `\uE118` (heart-filled) in app code: use the package APIs below.
   Filled variants end in `-filled` (`heart-filled`, `play-filled`, `star-filled` ...); use
   them for the selected or active state.
2. **Match the symbol weight to the text beside it**: regular next to body text, medium next
   to buttons and labels, bold next to bold text.
3. **Accessibility.** An icon that has a meaning on its own (an icon-only button) needs a
   label: use the symbol's `label` (the packages do this for you on iOS; pass
   `contentDescription` on Android). An icon next to a text label is decorative: hide it from
   screen readers (`aria-hidden="true"`, `contentDescription = null`).
4. **Right-to-left.** Symbols with `rtlMirror: true` (send, back, reply, play ...) flip in
   right-to-left layouts. The packages handle this; with raw SVGs, flip them yourself.
5. **Do not fake styles.** Always load the real italic and bold files; never use synthetic
   bold or oblique (`skewX`).
6. **Roles** (from the design tokens): chat body 16 px / line height 1.5, Sans or Serif 400;
   buttons and labels Medium 500; headings Bold 700; code Mono 14 px / 1.5 with `"zero" 1`.
   Programming ligatures in Mono are optional (`"ss01" 1`, off by default).
7. **Do not edit generated files** (`fonts/`, `packages/`, `symbols/`, `sources/`). They are
   rebuilt from `scripts/` (see README). Report problems instead of patching outlines.
8. **License: SIL Open Font License 1.1.** Bundling the fonts in an app is fine; include
   `OFL.txt` (or the license text) with the app's other open-source notices.

## iOS (SwiftUI / UIKit)

Add the Swift package: Xcode › File › Add Package Dependencies ›
`https://github.com/cosmoluei/admiralty-fonts`, product **Admiralty** (iOS 15+). The package
registers its fonts itself; do not add them to `Info.plist`.

```swift
import Admiralty

Text(reply).font(.admiralty(.serif, size: 17))                     // agent message
Text(prompt).font(.admiralty(.sans, size: 17))                     // user message
Text(code).font(.admiralty(.mono, size: 14, relativeTo: .callout))
Text("Send").font(.admiralty(.sans, size: 15, weight: .medium))

AdmiraltyIcon("heart-filled")                                      // like Image(systemName:)
AdmiraltyIcon(.send, size: 17, weight: .medium).foregroundStyle(.tint)
Text(admiralty: .heartFilled) + Text(" Liked")                     // inline, grows with Dynamic Type
Label { Text("Settings") } icon: { AdmiraltyIcon(.settings) }

label.font = UIFont.admiralty(.sans, size: 17)                     // UIKit
button.setImage(UIImage.admiralty(.send), for: .normal)
```

Swift case names are the symbol names in lowerCamelCase (`heart-filled` → `.heartFilled`).
`import` and `extension` need back-ticks in a declaration but not after a dot (`.import`).

## Android (Jetpack Compose / Views)

Copy `packages/android/admiralty` into the project as a module, add `include(":admiralty")` to
`settings.gradle.kts` and `implementation(project(":admiralty"))` to the app module.

```kotlin
import io.github.cosmoluei.admiralty.AdmiraltySymbol
import io.github.cosmoluei.admiralty.R as AdmiraltyR

val AdmiraltySans = FontFamily(
    Font(AdmiraltyR.font.admiralty_sans_regular, FontWeight.Normal),
    Font(AdmiraltyR.font.admiralty_sans_italic, FontWeight.Normal, FontStyle.Italic),
    Font(AdmiraltyR.font.admiralty_sans_medium, FontWeight.Medium),
    Font(AdmiraltyR.font.admiralty_sans_mediumitalic, FontWeight.Medium, FontStyle.Italic),
    Font(AdmiraltyR.font.admiralty_sans_bold, FontWeight.Bold),
    Font(AdmiraltyR.font.admiralty_sans_bolditalic, FontWeight.Bold, FontStyle.Italic),
)
// The same for admiralty_serif_* and admiralty_mono_*.

Text(reply, fontFamily = AdmiraltySerif, fontSize = 16.sp, lineHeight = 24.sp)
Icon(painterResource(AdmiraltySymbol.HeartFilled.drawable), contentDescription = AdmiraltySymbol.HeartFilled.label)
AdmiraltySymbol.named("heart-filled")                 // look up by name, null if unknown

// Views
textView.typeface = ResourcesCompat.getFont(context, AdmiraltyFonts.SANS)   // or android:fontFamily="@font/admiralty_sans"
imageView.setImageResource(AdmiraltySymbol.Send.drawable)
```

Kotlin enum names are the symbol names in PascalCase (`heart-filled` → `HeartFilled`).
Direction icons are drawables with `android:autoMirrored="true"`.

## Flutter

```yaml
# pubspec.yaml
dependencies:
  admiralty:
    git:
      url: https://github.com/cosmoluei/admiralty-fonts
      path: packages/flutter/admiralty
```

```dart
import 'package:admiralty/admiralty.dart';

Text(reply, style: const TextStyle(fontFamily: AdmiraltyFonts.serif, package: AdmiraltyFonts.package, fontSize: 16, height: 1.5));
Icon(AdmiraltyIcons.heartFilled);
Icon(AdmiraltyIcons.named('heart-filled'));
```

Dart names are lowerCamelCase; `new` is `AdmiraltyIcons.newIcon` (reserved word).

## Web (also Electron and Tauri)

Copy `packages/web` into the site's static files.

```html
<link rel="stylesheet" href="/admiralty/admiralty-fonts.css">
<link rel="stylesheet" href="/admiralty/admiralty-symbols.css">

<p style="font-family: var(--adm-serif)">Agent reply …</p>
<button><i class="adm-icon adm-send" aria-hidden="true"></i> Send</button>
<button aria-label="Like"><i class="adm-icon adm-heart-filled" aria-hidden="true"></i></button>
```

`--adm-sans`, `--adm-serif` and `--adm-mono` already include the CJK fallbacks. The icon takes
the text colour and size; set `font-weight: 400 | 500 | 700` on it to match the text. The CSS
classes are `adm-` + the symbol name. An SVG sprite is also there:
`<svg><use href="admiralty-symbols-sprite.svg#adm-send"/></svg>`.

## React Native and other platforms

There is no package yet. Copy the files from `fonts/ttf/`. iOS refers to a font by its
PostScript name (`AdmiraltySans-Medium`), Android by its file name. For symbols, use the SVGs in
`symbols/svg/` (with react-native-svg) or the Symbols font with the code point from
`symbols/admiralty-symbols.json`, wrapped in a small helper that looks names up.
