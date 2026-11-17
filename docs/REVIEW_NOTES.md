# Admiralty — review notes (rounds 1–4, November 2026)

Notes from the second review of version 0.200 and the four rounds of fixes that led to 0.300.
Numbers are measured from the outlines, in font units (1000 units per em).

## Files changed in round 1
- `scripts/symbols_refine_r2.py` (new) — 48 redrawn symbols; overrides the old drawings by name
- `scripts/vf_align.py` (new) — exact alignment of the three weight masters
- `scripts/symbols_engine.py` — symbol scale 1.2x
- `scripts/build_symbols.py` — uses the overrides; adds `label` and `glyphName` to the JSON
- `scripts/build_delivery.py` — follows the new scale and glyph names
- `scripts/glyphs_bold.py` — smoother Medium/Bold outlines; Serif Bold A V W Y v w y
- `scripts/glyphs_mono.py` — Mono K joint
- `scripts/glyphs_italic.py` — Mono Italic fraction spacing; bracket kerning group
- `scripts/spacing_kerning.py` — positive kerning pairs
- `scripts/build_variable.py` — uses vf_align; STAT, SemiBold 600 instance, name ID 25; audit
- `scripts/build_fonts.py` — kerning audit list; optional `ADMIRALTY_SKIP_VARIABLE=1`

## Measured results (before -> after)
Small outline kinks in 62 test glyphs:
- Sans Medium 152 -> 3, Sans Bold 154 -> 12, Sans Bold Italic 201 -> 44
- Serif Medium 330 -> 27, Serif Bold 222 -> 34, Serif Bold Italic 234 -> 97
- Mono Medium 160 -> 4, Mono Bold 164 -> 2
- Variable Sans at weight 400: 644 -> 6 (static Regular: 0)
Variable fonts: glyphs that break between weights: Latin 0 (was: ae, oe, Serif Italic a and y, Sans Italic i, and others);
only the prime marks in the two italic variable fonts are still about 12% off. Symbols: 0 (was 19).
Serif Bold stroke width at mid height (n stem = 140): v 116 -> 134, w 106 -> 121, y 120 -> 134, V 128 -> 148, W 115 -> 137, A 120 -> 149, Y 138 -> 150.
Touching pairs in Serif Bold: 11+ -> 1 (Qj still overlaps by 5 units).
Symbols: typical height 550 -> 676 units (cap height is 700); stroke 60/70/84 -> 72/85/101.
Font Bakery (Google Fonts profile) on the variable fonts: only "version must be 1.000 or higher" fails (the STAT failures are gone).

## Not fixed
- Italics (checked again on 2026-11-16, second pass): no redraw needed. Most of the "kinks" counted above in the
  italics are rounding noise: a curve meets a slanted stem with a 2-3 unit handle, and whole-number
  coordinates cannot hold a 9.5 degree direction on such a short handle. Counting only kinks that move the
  outline by 1.2 units or more: Sans Italic 2, Serif Italic 15, Mono Italic 3 (the two in `a` are the real
  corner where the bowl meets the stem). Medium/Bold italics: Sans 3 / 5, Serif 5 / 12, Mono 6 / 3
  (before this refinement: 63 / 95, 103 / 87, 39 / 98).
- Serif Regular: 6 visible kinks by the same count (x, g, v, y, J).
- `legal` (scales) is clearer than before but still weak at 16 px.
- Soft-dotted `i-ogonek` + accent, soft hyphen glyph, OTF hinting: unchanged.
- `OFL.txt` first line does not match the copyright text inside the fonts. Google Fonts wants
  "Copyright 2026 The Admiralty Project Authors (repository URL)" in both. It needs your repository URL.
- `specimens/inspector.html` was rebuilt with `python3 scripts/build_inspector.py` (it loads Tailwind from the internet, as before). The specimen PDF was not rebuilt.

## Round 3 (owner feedback on symbols, 2026-11-16)
Redrawn in `scripts/symbols_refine_r2.py` (section "Round 3").
- `help`: the question mark is one connected stroke now (the hook and the stem were separate pieces).
- `timeout`: the clock is open on the lower right and the alert mark stands apart from it.
- `history`, `restore` (and their `.rtl` mirrors): the arrow is the mirror image of `retry`; history keeps short clock hands, restore has a solid centre.
- `cloud-off`: wider cut around the slash; the outline now keeps one shape from 400 to 700, so `cloud_off.rvrn500` no longer exists.
- `link`: two interlocking chain links. `unlink` uses the same links pulled apart, so the pair matches.
- `automation`: the `retry` arrow around a solid bolt.
- `background-task`: the dot sits in the middle of a wider gap.
- `tabs`: a window with a tab strip; the left tab opens into the page.
Symbols that still switch outline between weights (22): see the `.rvrn500` / `.rvrn700` glyphs in the variable font.

## Round 4 (owner screenshots + all open items, 2026-11-16) — version is now 0.300

Outlines
- Serif `a` (all weights): the tail runs into the stem as one wide curve. The old tight corner folded into a spike in Medium and Bold.
- Serif `g` (all weights): the link ends exactly on top of the lower loop, and the ear starts inside the bowl wall and is level with its top. Both steps are gone.
- Serif Italic exit hooks (`a d h l m n r u i`, all weights): the top of the hook runs into the stem as one curve instead of a notch. In Medium Italic and Bold Italic the hook is drawn 8 / 18 units longer so the gap stays open. Same change for the tails of Sans Italic `a i` and Mono Italic `a`.
- Serif Italic `k`: the leg keeps an even width and both sides run into the tail without a corner.
- Prime marks (minute, second) in Medium and Bold: straight tapered strokes. They were copies of the curly quote, which was wrong and also broke the italic variable fonts.
- Serif `J` join, Mono `Q` tail (it poked into the counter).
- `glyphs_bold.py`: offset pieces that turn inside out are dropped. `design_system.clean_contour_nicks` runs on every glyph before it is written: removes segments of 2.5 units or less and small hook-backs.

Open items from the last report
- Kerning: `Qj`, `YW`, `WY`, hook letters before `z`.
- `i-ogonek` + accent now loses its dot (new glyph `iogonek.dotless`, `ccmp`).
- OTF files are hinted with `otfautohint` when AFDKO is installed (`pip install afdko`); 463 of 467 glyphs in Serif Bold carry hints.
- `OFL.txt` line 1 and the copyright inside every font are now the same: "Copyright 2026 The Admiralty Project Authors (https://github.com/cosmoluei/admiralty-fonts)". The URL was already inside the fonts; change it in `build_fonts.py`, `build_symbols.py` and `OFL.txt` if the repository will be somewhere else.
- Version 0.300 everywhere.
- `legal` symbol: a gavel instead of the scales.

Results
- Variable fonts: 0 glyphs break between weights in all 7 files (the prime marks were the last ones).
- Spikes / hook-backs in base letters: about 45 across the 18 text fonts -> 0. What the scan still lists are normal sharp joins (bowl meets stem, the waist of B and 3).
- Visible kinks (1.2 units or more, 62 test glyphs): Sans 0 / 0 / 0, italics 2 / 3 / 4; Serif 4 / 4 / 7, italics 13 / 5 / 14; Mono 0 / 1 / 2, italics 2 / 4 / 3.

Left as they are, on purpose
- 1 to 2 unit kinks where a diagonal meets its serif (Serif v x y A K k). Smaller than a pixel at 300 px.
- Soft hyphen: it has the hyphen shape, which is the usual practice. Font Bakery only gives a note.
- Soft-dotted: only rare combinations remain (i or j with a comma below plus an accent above).
- Font Bakery still fails "version must be 1.000 or higher" until you release 1.000.
- Specimen PDF: `scripts/render_milestone8.py` needs a macOS system font, so it must be run on your Mac: `python3 scripts/render_milestone8.py`.

## Release preparation (2026-11-17)
- `æ` in Sans, Serif and Mono Italic: the a now has its own straight stem up to the x-height, with an open notch before the e. Before, the a and e met in a round valley, and `æ` looked almost the same as `œ`.
- Mono `æ` (upright): redrawn as one outline with two counters, like the Mono Bold `æ`. The old one left a flat notch at the bottom and a pinched e counter.
- `gftools builder` builds Sans, Serif and Mono from `sources/` (configs `sources/config-*.yaml`). Compared with `scripts/build_fonts.py`: same glyph set, same advances at weights 400, 550 and 700, no outline differs by more than 0.5% in area. Font Bakery on the gftools fonts: the only failure is the version (below 1.000); the errors are checks that need the internet.

## New characters (2026-11-17)
- 62 new symbols, Latin Plus, Vietnamese and Mono box drawing (see `CHANGELOG.md`). Built and checked on the owner's Mac: all 21 static and 7 variable fonts build; duplex (Sans = Serif widths) and Mono 600-unit checks pass; OTS passes for every file; Font Bakery has no new failures (only the version number).
- Mono `Ⓓ` uses a smaller true circle that fits the 600-unit cell (it was squeezed into an ellipse).
- Fixed after review: the Serif `₨` kink and the other weight problems (see below). Still open: the Mono horn letters `Ơ Ư` reach slightly past the cell on the right, as in most monospaced fonts.
- Review page: `specimens/review.html`.

## Owner review of the new designs (2026-11-17)
- Unclear symbols redrawn: `browser` (compass), `brain` (side view with stem), `edit-message` (bubble with text lines and a large pencil), `schedule-send` (smaller arrow, clock with hands), `usage` (gauge with ticks). `command` fixed: the sides of the square now run into the loops.
- New `heart-filled` (U+E118) and `play-filled` (U+E119, mirrored in RTL).
- Weight problems: the old Medium superscripts were smaller than Regular and Bold, and Mono Medium/Bold superscripts were not centred, so the figures changed size as the weight moved. All superscripts, subscripts and fractions are now built from one fixed size in every weight, with separate (not merged) parts. `₨` keeps R and s apart. `deep-research` had its handle split off in Medium (a pathops edge case); the handle now overlaps the ring in every weight. Clock badges use one cut size in every weight.
- `₴`: the mirrored S had the opposite outline direction, so the bars cut gaps into it. Parts are now joined one at a time.
- Checked: no glyph moves out of place between weights in any variable font (except the existing `“ ”` pair, which touch at the heaviest weights when typed next to each other); Font Bakery interpolation check passes; OTS passes.
