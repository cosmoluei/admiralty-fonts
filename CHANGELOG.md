# Changelog — Admiralty Font Family

All notable pre-release milestones (`0.x` design track) are documented here. All releases use **SIL Open Font License 1.1** (without Reserved Font Name).

---

## `[0.300]` — 2026-11-16 (Review 2 refinement, rounds 1–4)

- **Release preparation**: `æ` in the italics has its own straight a-stem with an open notch before the e (it read as `œ`); Mono `æ` redrawn as one outline (no notch at the bottom); SemiBold 600 instances in the designspace files; `gftools builder` configs in `sources/`; Google Fonts descriptions in `documentation/`; `AUTHORS.txt`, `CONTRIBUTORS.txt`, `requirements.txt`; README, usage guide, QA report and tokens updated for 0.300; copyright URL `https://github.com/cosmoluei/admiralty-fonts`.
- **Round 4**: Serif `a` tail and `g` joins; italic exit hooks in all weights; Serif Italic `k`; straight prime marks in Medium/Bold; `i-ogonek` soft-dotted; `Qj` and other kerns; OTF hinting (needs AFDKO); one copyright line in the fonts and `OFL.txt`; `legal` symbol redrawn; a clean-up pass for tiny segments on every glyph. Details in `review2/REVIEW2_CHANGES.md`.

The notes below are from rounds 1–3.

Made from the findings of Review 2 and the owner's notes on the symbols.

- **Symbols**: 48 symbols redrawn in `scripts/symbols_refine_r2.py` (overrides the old drawings, which stay in `symbols_phase1_*.py`): correct arrow heads (`retry`, `regenerate`, `sync`, `restore`, `history`, `reply`, `forward-message`), one shared cloud for the whole cloud family, clearer `dark-mode`, `theme`, `tool`, `data-controls`, `tabs`, `timeout`, `advanced-search`, `help-center`, `legal`, `toggle-on/off`, `plan`, `mention`, `attach`, `pdf`, `share-app`, `new`, `settings`, `import/export`; `online/offline` share one drawing; filled variants are now the outline drawing plus fill.
- **Symbols size**: drawing scale 1.2× (`GRID_SCALE = 36`), so a typical symbol is about cap height (676 of 700 units) and strokes are 72 / 85 / 101 units (were 60 / 70 / 84).
- **Symbols metadata**: `label` (accessibility text) and `glyphName` added to `admiralty-symbols.json`; glyph names use `_` instead of `-`.
- **Medium / Bold / italics**: new join rules and curve fitting in `bolden_contours_smooth` (`glyphs_bold.py`): no dents at the top and bottom of round letters, stems no longer taper. Mono `K` joint fixed.
- **Serif Bold**: `A V W Y v w y` rebuilt with parallel stroke walls, so the diagonals carry the same weight as the upright stems.
- **Kerning** (same in Sans and Serif): positive pairs for `f` + tall letters and capitals, `j` after brackets, `qj`, `jj`, doubled `V W Y v w y`.
- **Variable fonts**: masters are now aligned by splitting segments (`scripts/vf_align.py`) instead of re-drawing outlines, so the variable fonts at 400 / 500 / 700 match the static fonts. `STAT` uses exact values, a SemiBold 600 named instance and name ID 25 were added.
- **Symbols, round 3**: `help`, `timeout`, `history`, `restore`, `cloud-off`, `link`, `unlink`, `automation`, `background-task`, `tabs` redrawn after owner feedback; `specimens/inspector.html` rebuilt.

---

## `[0.200]` — 2026-11-17 (Milestone 8: Variable Fonts, Final QA & 5-Platform Delivery)

- **7 Variable Fonts (`wght 400..700`)**: Compiled `AdmiraltySans[wght]`, `AdmiraltySans-Italic[wght]`, `AdmiraltySerif[wght]`, `AdmiraltySerif-Italic[wght]`, `AdmiraltyMono[wght]`, `AdmiraltyMono-Italic[wght]`, and `AdmiraltySymbols[wght]` (TTF + WOFF2) with canonical `STAT`, `fvar`, `gvar`, `HVAR`, `gasp` (`0x000F`), and `prep` tables.
- **Corner- & Extremum-Locked Contour Harmonizer** (`scripts/build_variable.py`): Aligned contour order, winding, sharp corners, and X/Y extrema across all 21 UFO masters (`Regular 400`, `Medium 500`, `Bold 700`) so non-master weights (`435`, `450`, `525`, `600`, `640`) interpolate cleanly without kinks or self-intersections (`0.0u` Sans vs Serif duplex advance parity across `wght 400..700`).
- **Symbols Variable `GSUB rvrn`**: Added smooth contour-count topology switching (`rvrn` + mirrored `rtlm`) across weights `450–700` for the 27 symbol icons whose stroke dilation merges or splits paths.
- **5-Platform Delivery (`dist/`)**: Generated platform packages for `apple-ios-macos`, `android` (218 VectorDrawables + XML font families), `windows`, `web` (Unicode-range Variable WOFF2 subsets + CLS-zero CSS + SVG sprite), and `cross-platform` (Flutter `IconData` Dart map + JSON).
- **Documentation & QA**: Delivered `docs/USAGE_GUIDE.md`, `tokens/admiralty-design-tokens.json`, `docs/QA_AND_ORIGINALITY_REPORT.md`, `specimens/Admiralty_Type_Review_Proof_v0.200.pdf`, and upgraded `specimens/inspector.html` with a live continuous `wght 400–700` slider.

---

## `[0.130]` — 2026-11-17 (Milestone 7: Medium 500 Quartet & True Duplexed Italics)

- Added **Medium (500)** across `Admiralty Sans`, `Admiralty Serif`, `Admiralty Mono`, and `Admiralty Symbols` (`2.35u/24` stroke width, 249 Medium SVGs) with RIBBI + Typographic Naming (`Name ID 1/2/16/17`).
- Added **True Duplexed Italics (`-9.5°`, `caretSlopeRun = 167`)** at `400`, `500`, and `700`: literary cursive Serif lowercase (`a`, `e`, `f`, `g`, entry flags, upturned exit hooks, `æ`, `œ`), calm humanist Sans Italic locked 1:1 to Serif Italic widths (`0.0u` reflow + `+28u` `(f` kerning), and 600u coding cursive Mono Italic with sheared `ss01` ligatures.

---

## `[0.120]` — 2026-11-16 (Milestone 6: Bold 700 Trio & Admiralty Symbols Phase 1)

- Built `Admiralty Sans Bold`, `Admiralty Serif Bold`, and `Admiralty Mono Bold` with open `@1x` `12–16 px` counters and unified `+980 / -320 / 0` metrics.
- Built **Admiralty Symbols Phase 1**: **218 original 24×24 UI icons** (`U+E000–U+E0D9`) in Regular (`2.0u`) and Bold (`2.8u`), with 31 `rtlm` RTL mirrors and JSON metadata.

---

## `[0.110]` — 2026-11-16 (Milestones 4–5: Admiralty Serif Regular, Admiralty Mono Regular & App Review 1 Fixes)

- Built `Admiralty Serif Regular` on the Sans skeleton (`92u/40u` stems, double-story `g`, calligraphic terminals) with strict `0.0u` Sans↔Serif layout parity (`167` shared kerning rules, `.tnum = 580u`).
- Built `Admiralty Mono Regular` (`600u` fixed pitch, redrawn `M/W/m/w/i/l/r`, optional `ss01` coding ligatures, `80 * 600 = 48000u`).
- Resolved App Review 1 findings (`§`, `æ`, `œ`, `X` serif notch clearance, Pinyin precomposition + `LatExtA 128/128`, `eth` contour cleanup, `gasp`+`prep`+CFF hinting).

---

## `[0.100]` — 2026-11-16 (Milestones 1–3: Admiralty Sans Regular Core)

- Designed `Admiralty Sans Regular` from scratch (`1000 UPM`, `x-height = 520`, `cap = 700`, `86u/76u` stems), full GF Latin Core glyph set, class kerning, and OpenType features (`ccmp`, `locl`, `lnum`, `pnum`, `tnum`, `zero`, `case`, `mark`, `mkmk`).
