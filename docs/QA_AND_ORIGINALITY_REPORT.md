# Admiralty Font Family — Final QA, Measured Consistency & Originality Report (`v0.601`)

> Audit run across **77 compiled font binaries** (21 Static OTF, 21 Static TTF, 21 Static WOFF2, 7 Variable TTF, 7 Variable WOFF2) and **5 platform packages** in `dist/`.
> *Tooling note*: the checks below run with `fontTools`, `uharfbuzz`, `freetype` and `pathops`. Run Font Bakery (`fontbakery check-googlefonts fonts/variable/*.ttf`) and OTS (`pip install opentype-sanitizer`) separately; see `docs/REVIEW_NOTES.md` for the last results.

---

## 1. Automated Quality Checks Scorecard

| Check Suite | Result | Details |
| --- | --- | --- |
| Unified Vertical Metrics (980/-320/0) & OFL Metadata | **PASS** | 49 OTF/TTF/VF-TTF binaries verified |
| Forbidden Trademark Tokens Check (MTR / HongKong / Kowloon / SF Symbols) | **PASS** | 0 matches across all name tables |
| gasp + prep Non-Hinting & CFF Private Zones | **PASS** | 28 TTFs (gasp=0x000F + prep) & 21 OTFs verified |
| WOFF2 Decompression & Section 14 Size Budgets | **PASS** | Static 21=551.7 KB, Variable 7=429.5 KB, Combined=981.2 KB / 1536.0 KB |
| FreeType Full-Glyph Rasterization Audit (every GID @16px) | **PASS** | 31,724 glyphs loaded & rasterized across 49 binaries with 0 errors |
| Variable Font Tables (fvar, gvar, HVAR, STAT) | **PASS** | All 7 Variable TTFs pass wght 400..700 + STAT verification |
| 5-Platform Delivery Packages (dist/) | **PASS** | All 5 folders verified w/ OFL.txt + README (Android=311 VDs, Web=12 subsets, Apple=1050 SVGs) |

### File Size Summary vs Section 14 Targets

- **21 Static WOFF2 total**: `551.7 KB`
- **7 Variable WOFF2 total**: `429.5 KB` (`< 100 KB` per Latin VF, `< 150 KB` Symbols VF)
- **Combined WOFF2 budget**: `981.2 KB / 1536.0 KB` (`63.9%`)

### Variable Font Size Breakdown

| Variable Font Binary | TTF Size | WOFF2 Size | Axes |
| --- | --- | --- | --- |
| `AdmiraltyMono-Italic[wght]` | `131.1 KB` | `48.6 KB` | `wght (400..700)` |
| `AdmiraltyMono[wght]` | `121.9 KB` | `43.9 KB` | `wght (400..700)` |
| `AdmiraltySans-Italic[wght]` | `134.1 KB` | `54.5 KB` | `wght (400..700)` |
| `AdmiraltySans[wght]` | `118.4 KB` | `46.3 KB` | `wght (400..700)` |
| `AdmiraltySerif-Italic[wght]` | `155.7 KB` | `62.0 KB` | `wght (400..700)` |
| `AdmiraltySerif[wght]` | `135.7 KB` | `52.0 KB` | `wght (400..700)` |
| `AdmiraltySymbols[wght]` | `356.7 KB` | `122.4 KB` | `wght (400..700)` |

---

## 2. Measured Cross-Family Consistency (Section 15)

- Shared vertical metrics across **Sans, Serif, Mono, and Symbols**: `UPM = 1000`, `x-Height = 520`, `CapHeight = 700`, `Ascender = 740`, `Descender = -220`, `Typo/hhea Ascent = +980`, `Descent = -320`, `LineGap = 0`, `winAscent = 980`, `winDescent = 320`, `USE_TYPO_METRICS = True`.

| Family & Weight | Cap `H` Stem @150u | Lowercase `n` Stem @200u | Round `o` Bowl @260u |
| --- | --- | --- | --- |
| Sans Regular (400) | `92u` | `86u` | `90u` |
| Sans Medium (500) | `110u` | `104u` | `108u` |
| Sans Bold (700) | `140u` | `134u` | `138u` |
| Serif Regular (400) | `102u` | `92u` | `98u` |
| Serif Medium (500) | `121u` | `110u` | `116u` |
| Serif Bold (700) | `152u` | `140u` | `147u` |
| Mono Regular (400) | `84u` | `86u` | `88u` |
| Mono Medium (500) | `96u` | `98u` | `100u` |
| Mono Bold (700) | `114u` | `116u` | `118u` |
- **Symbols Stroke Progression (`24×24` grid -> `840u`)**: Regular `2.0u (72u)` · Medium `2.36u (85u)` · Bold `2.8u (101u)`, 36 font units per grid unit (`-filled` active variants and 31 `rtlm` RTL mirrors).

---

## 3. Originality & Reference Record (Section 15 & 17)

- **Clean-Room Parametric Generation**: Every Latin outline (`scripts/glyphs_*.py`, `scripts/serif_primitives.py`) and every UI icon (`scripts/symbols_engine.py`, `scripts/symbols_phase1_a.py`, `scripts/symbols_phase1_b.py`) was constructed mathematically from scratch in Python Bezier/CSG code (`design_system.ContourBuilder` + `skia-pathops`). No third-party `.ttf`, `.otf`, `.ufo`, or `.svg` paths were imported, traced, or copied.
- **Design Inspiration References (Proportions & Tone Only)**: Source Serif / Source Sans and IBM Plex Serif / Sans (for calm humanist UI readability pairing), plus Apple Human Interface Guidelines, Material Symbols, and Microsoft Fluent UI guidelines (studied for icon grid sizing and 24×24 visual balance only — zero shapes copied).
- **Exclusion Checks**: Zero `MTR`, `SF`, `HongKong`, or `Kowloon Type` strings exist anywhere in source metadata or compiled `name` tables.

---

## 4. Pre-1.0 Release Human & Legal Gate Checklist (Section 15, 17, 23)

- [x] Automated outline, extrema, interpolation, FreeType rasterization, zero-reflow duplex (`0.0u`), Mono column lock (`48000u`), and 5-platform packaging checks passed (`v0.601`).
- Prior Font Bakery and OTS results are recorded in `docs/REVIEW_NOTES.md`. They are checked separately from this audit.
- The prior `gftools builder` comparison for Sans, Serif and Mono is recorded in `docs/REVIEW_NOTES.md`.
- [ ] **Owner review** of every style in real use (chat app, phone, desktop) before 1.000.
- [ ] **Version 1.000** for the first stable release (Google Fonts requires 1.000 or higher).
- [ ] **Name clearance** for `Admiralty` (`Sans / Serif / Mono / Symbols`) and the decision on a Reserved Font Name (none today).
