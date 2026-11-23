# Admiralty Font Family — App Team Usage Guide (`v0.601`)

Machine-readable tokens: [`admiralty-design-tokens.json`](../tokens/admiralty-design-tokens.json) · License: **SIL Open Font License 1.1** (no Reserved Font Name) · Latin (Google Fonts Latin Core and Latin Plus, Latin Extended-A, Pinyin, Vietnamese) + **311 original PUA UI icons** (`U+E000–U+E136`). Ready-made packages for iOS, Android, Flutter and the web are in [`packages/`](../packages); the short guide for coding agents is [`AGENTS.md`](../AGENTS.md).

---

## 1. Text Styles & Weight Roles

All four families share unified vertical metrics (`1000 UPM`, `x-height = 520`, `cap = 700`, `typoAscender = hhea.ascent = +980`, `typoDescender = hhea.descent = -320`, `lineGap = 0`).

| Style Role | Size | Line Height | Weight / Slant | OpenType Notes |
| --- | --- | --- | --- | --- |
| **Chat Body** | **16 px** | `1.50` (`24 px`) | `400 Regular` | `kern=1`, `pnum=1`, `lnum=1`, `ccmp=1`, `locl=1` |
| **UI Button & Label** | `14–16 px` | `1.25` | **`500 Medium`** | Pair with `Admiralty Symbols` at weight `500` |
| **Quotes & Titles** | `16–18 px` | `1.50` | **`400/500 Italic`** (`-9.5°`) | True cursive lowercase in Serif; humanist italic in Sans |
| **Headings & Strong** | `20–24 px` | `1.30` | **`700 Bold`** (or `600 SemiBold` from the variable fonts) | Use `case=1` for all-caps labels/badges only |
| **Code / IDs / Logs** | **14 px** | `1.50` | `Admiralty Mono` (`400/500/700`, `±Italic`) | Always `600u` fixed pitch; `zero=1` default, `ss01` optional (`off` by default) |
| **Aligned Numerals** | any | inherit | `Admiralty Sans/Serif` | Turn on `tnum=1` (`580u` fixed figure width) + `zero=1` |
| **Caption / Metadata** | **12 px** | `1.42` | `400 Regular` / `500 Medium` | Never below `11 px`; keep open apertures |

---

## 2. Speaker Role Mapping & One-Setting Swap

Because **Admiralty Sans** and **Admiralty Serif** share identical advance widths (`0.0u` HarfBuzz delta across `400`, `500`, `700`, `Italic`, `Medium Italic`, `Bold Italic`, and any continuous variable weight `400..700`), toggling speaker voices triggers **0 px layout reflow**:

- **Default mapping**: `Agent = Admiralty Serif` · `User = Admiralty Sans`
- **One-setting swap (CSS example)**:

```css
:root { --adm-agent-font: var(--adm-serif); --adm-user-font: var(--adm-sans); }
[data-swap-fonts="true"] { --adm-agent-font: var(--adm-sans); --adm-user-font: var(--adm-serif); }
```

---

## 3. System Accessibility Text Scaling (All Platforms)

Always honor OS font scaling so users at the largest Dynamic Type / Accessibility sizes keep crisp hierarchy without vertical clipping:

- **iOS (SwiftUI)**: `.font(.admiralty(.serif, size: 16))` from the Admiralty Swift package (or `Font.custom("AdmiraltySerif-Regular", size: 16, relativeTo: .body)` with the font files) — scales with Dynamic Type.
- **Android (Jetpack Compose)**: define text sizes strictly in `16.sp` (never `.dp`) with `FontFamily(Font(R.font.admiralty_serif_wght))` (`Android 8+`) or static resources (`res/font/admiralty_serif.xml`).
- **Windows (WinUI 3)**: set `IsTextScaleFactorEnabled="True"` and reference `Medium` (`ID 1: Admiralty Sans Medium`) or static RIBBI weights in WPF/Office compatibility paths.
- **Web**: express sizes in `rem` (`1rem = 16px`, `--adm-body: 1rem`), allowing browser zoom & OS default font-size overrides.

---

## 4. Symbols Next to Text (`Admiralty Symbols`)

- **Same Size, Cap-Centered**: Use the **exact same `font-size`** (`1.0×`) and **weight (`400 / 500 / 700`)** as adjacent `Admiralty Sans` text; every `24×24` icon sits in an `840u` advance box centered around `y = 350u` (`CapHeight / 2`), aligning cleanly on the baseline without vertical CSS offsets (`display: inline-flex; align-items: baseline; gap: 0.38em; line-height: inherit`).
- **Colors & RTL**: Inherit `color: currentColor` from parent button text; enable `direction: rtl` + OpenType `rtlm` (or `android:autoMirrored="true"` on VectorDrawables) for the 39 directional icons (`send`, `back`, `chevron-*`, etc.).

---

## 5. Dark Mode & CJK / Emoji Fallbacks

- **Dark Mode Halation**: Light text on dark surfaces (`#131519`) appears slightly bolder. With Variable Fonts, step body weight slightly lighter (`wght: 410–420`) or keep `400 Regular` with generous `1.5` line-height (never jump Dark Mode body copy to `Medium 500`).
- **Chinese & Script Language Tags**: Always tag text regions with `lang="zh-Hant-HK"` (Hong Kong), `lang="zh-Hant-TW"`, or `lang="zh-Hans"` so fallback selects region-accurate Hanzi glyphs without line-height jumps:
  - **Sans Fallback**: `'Admiralty Sans', 'PingFang HK', 'PingFang TC', 'Noto Sans CJK TC', 'Noto Sans CJK SC', sans-serif`
  - **Serif Fallback**: `'Admiralty Serif', 'Noto Serif CJK TC', 'Songti TC', 'Songti SC', serif`
  - **Emoji**: Leave emoji out of icon glyphs; fall back to system color emoji (`Apple Color Emoji`, `Noto Color Emoji`, `Segoe UI Emoji`) with `line-height: 1.5` so emoji never stretches line boxes.

---

## 6. Quick Platform Code Samples

**Web CSS (`packages/web/admiralty-fonts.css`; icons by class with `packages/web/admiralty-symbols.css`)**

```css
.agent-reply { font-family: 'Admiralty Serif', 'Admiralty Serif Fallback', 'Noto Serif CJK TC', 'Songti TC', serif; font-size: 1rem; line-height: 1.5; font-feature-settings: "kern" 1, "pnum" 1; }
.ui-button   { font-family: 'Admiralty Sans', 'PingFang HK', sans-serif; font-weight: 500; display: inline-flex; align-items: baseline; gap: 0.38em; }
.ui-button .icon { font-family: 'Admiralty Symbols', sans-serif; font-weight: 500; }
.code-block  { font-family: 'Admiralty Mono', ui-monospace, monospace; font-size: 0.875rem; line-height: 1.5; font-variant-numeric: slashed-zero; }
```

**iOS (Swift package `Admiralty`)** &bull; Add this repository in Xcode (File › Add Package Dependencies); the package registers the fonts itself:

```swift
import Admiralty
Text("Summary ready").font(.admiralty(.sans, size: 16, weight: .medium))
AdmiraltyIcon("heart-filled")
```

**Android (module `packages/android/admiralty`)** &bull; Fonts, `<font-family>` XML and the 311 vector drawables (build `AdmiraltySerif` as shown in [`AGENTS.md`](../AGENTS.md)):

```kotlin
Text(text = response, fontFamily = AdmiraltySerif, fontSize = 16.sp, lineHeight = 24.sp)
Icon(painterResource(AdmiraltySymbol.HeartFilled.drawable), contentDescription = AdmiraltySymbol.HeartFilled.label)
```

---

## 7. Do & Don't Checklist

| Do | Don't |
| --- | --- |
| Keep long chat prose at **400 Regular**, buttons/labels at **500 Medium**, emphasis/headings at **700 Bold**, titles/quotes in **Italic**. | Don't set multi-sentence paragraphs in **700 Bold** or **ALL CAPS** (fatigue + slower reading). |
| Keep **Admiralty Mono** strictly `600u` on tabular logs and `zero=1` on IDs (`CX801`, `ID-1lI-O08`). | Don't synthetically skew (`skewX`) or stretch (`scaleX`) fonts; always load true `-9.5°` Italic faces. |
| Enable `tnum=1` on currency/table columns across Sans & Serif. | Don't mix emojis into button icon slots or omit `zh-Hant-HK` / `zh-Hans` `lang` attributes. |
