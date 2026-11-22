# Full weight, width and corner-radius range

The full build places the three-axis text and symbol fonts in [fonts/variable/fullrange](../../fonts/variable/fullrange). The isolated design studies and earlier rounds below document how the masters were drawn.

## Seven variable fonts

[Review optical candidates by group](review/candidate-review.html) compares a marked instance with Regular at the same width and corner radius. Start with the visually selected groups, or search the full list. A group decision applies to its listed cases. Individual cases can override it and carry their own notes and circles. Export decisions before starting a new scan. The JSON keeps every explicit decision in `reviews` and puts approved cases in `issues` for the before/after proof.

To regenerate the queue from the compiled fonts, run these commands from the repository root:

```sh
python3 scripts/fullrange/scan_family_candidates.py --fonts fonts/variable/fullrange --out scripts/fullrange/review/audits/candidate-scan.json
python3 scripts/fullrange/build_candidate_review.py scripts/fullrange/review/audits/candidate-scan.json --fonts fonts/variable/fullrange --out scripts/fullrange/review/candidate-review.html
```

[Compare the Mono per-mille before and after revision](review/mono-permille-comparison.html) across both styles and all 270 sampled combinations. Select a weight to inspect and annotate its outlines.

[The original Mono ink-width review](review/mono-width-review.html) shows all nine weights at the same width and radius. The first group contains instances at least 75 units narrower than both weight endpoints. The second contains the other sampled instances of the reported glyph. To repeat the scan with an export from the same font build:

```sh
python3 scripts/fullrange/scan_mono_width.py "$review_json" --out scripts/fullrange/review/audits/mono-width-scan.json
python3 scripts/fullrange/build_candidate_review.py scripts/fullrange/review/audits/mono-width-scan.json --out scripts/fullrange/review/mono-width-review.html
```

[The glyph reviewer](review/glyph-review.html) fits the current glyph’s combinations on one screen. Hover over a cell or focus it with the keyboard for a larger sample. Open **视图** to filter faces and axes or change the sampling density. Use the left and right arrows to turn pages and `/` to search. Click a cell to flag it, or Shift-click to compare it with Regular, draw a region and leave a note. The page saves marks in this browser. **导出问题** downloads a single JSON report with each glyph, font checksum, axis position and annotation.

[The full-family proof](review/family-proof.html) loads Sans, Serif, Mono, their italics and Symbols. Select a family, search for a glyph or type a character, then compare weights and widths at the selected corner radius. The TTF downloads use their public character maps. An additional private mapping in the embedded proof makes otherwise unencoded glyphs inspectable.

The candidates live in [review/families](review/families). They have native OpenType axes `wght` 100–900, `wdth` 65–150 and `RADI` 0–100. Default text drawings are based on 0.300. Width changes preserve duplex Sans/Serif layout, the 600-unit Mono cells and the 840-unit Symbols cells. The symbol builder reconstructs icon strokes and knockouts from the source drawing commands. The reports in [review/audits](review/audits) identify the audited font by SHA-256 and list individual instances requiring inspection.

At each weight, punctuation uses the upright, normal-width outline and advance in both styles across the width and corner-radius ranges. This includes case-sensitive forms, the visible soft hyphen and the paired cells of Mono programming ligatures. Detached punctuation dots stay circular.

Serif upright and italic use the approved `t` construction as their reference for stroke weight and corner treatment. The alphabet masters follow the cubic landmarks of the 0.300 drawings. The upright `g` has two independently drawn bowls and a curved link. The italic keeps its single-storey `a` and `g` and its rising `e` crossbar. The dedicated checks compare the exported defaults with 0.300 and measure oval walls, diagonals, the crossbar and the link through the width and radius axes.

Curved outlines without a letter-specific drawing use paired ink edges and shared tangents. The Serif `S`, `ß` and `ẞ` have explicit spine, bowl and terminal landmarks. The straight Sans and Mono capitals share physical bars and stems across widths. The sloping cuts of `Z` and `7` are measured perpendicular to the stroke.

The small-size inventory renders every glyph ID at 24 pixels across 22 axis combinations. Its [per-glyph results](review/audits/optical-inventory.json) include the lightest rendered instance and measured Thin sections of `&`, `S`, `ß` and the period. The family proof pairs the selected weight with Regular at identical width and radius in the editable text, the selected glyph and the complete glyph grid. The magnifier shows each text glyph with two construction references at the same settings, up to 480 pixels. The single-glyph matrix spans 27 weight/width combinations. The [384-pixel comparison report](review/audits/thin-reference.json) records each text glyph and two construction references at ten Thin settings and eight compressed or expanded Bold/Black settings. Each row also includes Regular at identical width and radius. Separate outline checks measure opposite arms of X, x and the multiplication sign and the apertures of Mono a, æ, ß and ẞ.

The full-range æ uses a double-storey left bowl in the upright and italic faces. Its upper-left opening distinguishes it from œ across the weight and width ranges. The Turkish lira has a rising curved foot and two parallel slashes throughout the range, following the [central bank’s sign](https://www.tcmb.gov.tr/wps/wcm/connect/EN/TCMB%2BEN/Main%2BMenu/About%2BThe%2BBank/Turkish%2BLira%2BSign). Thin crossing strokes in the other currency signs are drawn whole before union. Mono's seven two-cell operators can be inspected as shaped text or as individual GIDs in the magnifier. `check_junctions.py` measures the two sides of Thin currency rules, tests the apertures of æ and œ and checks the exported operator seams after HarfBuzz substitution.

Build and inspect from the repository root. The font and proof builders use fontTools with Brotli, uharfbuzz, NumPy, SciPy, osqp and skia-pathops. The symbol raster comparison also uses freetype-py.

```sh
python3 scripts/fullrange/build_axis_study.py
python3 scripts/fullrange/build_text_family.py
python3 scripts/fullrange/build_symbol_family.py
python3 scripts/fullrange/build_family_proof.py
python3 scripts/fullrange/measure_sans_strokes.py
python3 scripts/fullrange/check_text_layout.py
python3 scripts/fullrange/check_punctuation.py
python3 scripts/fullrange/check_serif_t.py
python3 scripts/fullrange/check_serif_letters.py
python3 scripts/fullrange/check_optical_inventory.py
python3 scripts/fullrange/check_thin_reference.py
python3 scripts/fullrange/check_cross_heavy.py
python3 scripts/fullrange/magnified_audit.py
python3 scripts/fullrange/audit_text_family.py AdmiraltySans --out scripts/fullrange/review/audits/AdmiraltySans.json --strict
python3 scripts/fullrange/audit_symbol_family.py --strict
```

Run the text audit separately for each family. It compares contour topology, ink area and advances at 135 grid positions and 24 additional combinations between masters. The icon audit shapes both directions and compares the exported glyph with the construction at 175 positions in a fixed 128-pixel frame. Its image error is the sum of absolute pixel differences divided by the reference ink. The family proof also supports reading-size and display-size inspection.

## Three-axis Sans lowercase study

[Open the lowercase proof](review/axis-study.html) or install the [standalone study TTF](review/fonts/AdmiraltySans-AxisStudy.ttf). It covers the 26 basic Latin lowercase letters and space. The default shape and advances come from 0.300 Sans Regular. The outlined masters are sampled into compatible TrueType quadratics. Registration locks corresponding terminals, arch summits and the two edges of the e crossbar. The 4000-unit font retains quarter units of the original 1000-unit drawing grid.

The weight range is 100–900 and the width range is 65–150%. The custom `RADI` axis runs from 0 to 100. It controls local fillets at corners and terminals. Its maximum nominal radius is 9 original drawing units in Thin, 30 in Regular and 49 in Black. Trimming is limited by adjacent corners. The width and weight masters retain the original curve contours at radius 0. The narrow Black uses the A spacing from the static comparison.

The ten word-proof letters supply the Thin and Black anchors. The study draws the related bowls and shoulders from `d` and `n`. The remaining nine use individual hook or diagonal constructions. A reader can check the upper and lower white spaces in `a`, the change of bend in `s`, and the open space above the tail of `g` at normal reading size. Radius can change the terminal independently of the main curve.

Build with `python3 scripts/fullrange/build_axis_study.py` (fontTools with WOFF2, NumPy, SciPy, skia-pathops). Run `python3 scripts/fullrange/check_axis_study.py` with uharfbuzz installed. The audit compares 234 designed outlines and advances against the compiled font at radius 0. It samples nine weights, five widths and three radii for 3,510 per-glyph winding, advance and ink-area checks, plus flat-stem checks where applicable. These counts describe geometry checks. They do not establish a visual preference.

Admiralty's measured Regular lowercase stem (`n`, height 260) is 86 units. The `o` is 90 units at each side and 74 at top and bottom. These values anchor the family-specific optical contrast when changing width. [Adobe's multiple-master design notes](https://adobe-type-tools.github.io/font-tech-notes/pdfs/5091.Design_MM_Fonts.pdf) describe compensating horizontal strokes and adjusting heavy counters. [Raph Levien's curve design thesis](https://levien.com/phd/phd.html) gives a geometric basis for inspecting curvature along an arc.

`measure_sans_strokes.py` cuts through the exported Thin `s` at 201 positions normal to its design spine and measures the distance between its two ink edges. It also estimates signed curvature from the midpoints of those cuts using a local cubic fit over roughly 80 design units. In the 150% width at zero corner radius the revised stroke spans 23.31–24.85 units. Its normalized peak curvature fell from 7.52 to 6.31 while its median stroke stayed within 0.07 units of 24. The same tool measures both spaces in `a` and the gap above the tail of `g`.

## Word proof after Round 9

Open [the word proof](review/word-proof.html) directly for 0.300 Regular, the preceding word proof and the revised Thin
and Black drawings at 65%, 100% and 150%. At Black 65%, B adds 58 units to `m` and 36 to `e`
inside the letters. A and B share the remaining glyphs and spacing. The proof embeds static
web fonts for the ten letters in *minimum signal edges* and supports editing with that alphabet.
The current comparison adds the double-storey `a` to the preceding `m e s g` study. Its Thin
uses a 24-unit pen. Black has a rising waist, a separately drawn lower counter and a tapered foot.
Compare the two editions in *ananas* and *signals*. The alphabet section includes every mapped
Latin letter in the 0.300 Regular, the ten active study letters, and the seven other letters
from the Round 9 pilot. A mixed line shows how those two sets sit together at each extreme.
Rebuild with `python3 scripts/fullrange/build_word_proof.py`. Run
`python3 scripts/fullrange/check_word_proof.py` to measure the embedded fonts, including
free-stroke widths, inward seams, offset cusps and contour counts.

## Goal

The owner wants Admiralty to match the range of Apple's SF Pro:

- **Weight** 100 (Thin) to 900 (Black), as a variable `wght` axis.
- **Width** 65% (Compressed) to 150% (Expanded), as a variable `wdth` axis.
- For all families and styles: Sans, Serif and Mono, each upright and italic, all ~640 characters,
  with kerning and the Symbols font at nine weights.

The current release has only Regular, Medium and Bold (400–700) at one width.

## What the owner requires (from review feedback)

1. **Thin and Black must still look like Admiralty.** Shapes, proportions and details must not drift.
   Two automatic methods were rejected for this reason (see "Rejected approaches").
2. **At Thin, every stroke must be the same thickness**: stems, bars, curves, joints, dots and
   terminals. Measured, not eyeballed (`thick.py`).
3. **Curves must be smooth at every weight**, especially Thin, where any kink, flat spot, corner at a
   joint or change of thickness is easy to see. The owner checks joints (where an arch meets a stem),
   the middle of `m`, the bowl of `u`, the foot of `l`, and where curves meet straight stems.
4. **Regular at 100% must stay today's Regular**, and letter widths must not change there.
5. **Do not send work for review while you still know of a problem in it.** Fix and check first.

## Rejected approaches (kept in `rejected/` for reference)

| Test | Method | Why it was rejected |
| --- | --- | --- |
| 1 | `make_proto.py`: extrapolate past the Regular and Bold masters along a stem-weight curve; widths by scaling | "Thin and Black are not like Admiralty, they changed a lot" |
| 2 | `make_proto2.py` + `seg_offset.py`: offset Regular's outline thinner and Bold's thicker, segment by segment | "still not acceptable": at Thin 150% the arches came loose from the stems and the rounds looked stretched |

Conclusion: changing finished outlines automatically only works for roughly 300–800 and 85–115%.
The full range needs letters that are **drawn** for each weight and width.

## Current method (this folder)

Each letter is a function `glyph_x(p)` that draws the letter for one master from measurements in
`p` (`pilot.P(weight, width)`):

- `S` stem, `H` horizontal bar, `B` bowl side, `J` joint thickness, `sb` sidebearing, `Cn` counter
  width (the white inside, which takes most of the width change), `t`/`to`/`ti` curve tensions
  (squarer when narrow, rounder when wide). Values per weight are in `pilot.TAB`. At Thin all
  thicknesses are 24.
- `light(p)` is 1 at Thin and 0 from Regular up. At light weights every *outside* edge is computed
  from its *inside* edge with `offset_fit()`, so the two stay one stroke apart. From Regular up the
  designed shapes are used. Joints flow into the stem at light weights (`ease_joint`, `rot_end`)
  and keep Admiralty's crisp notch from Regular up. Where two curves meet, `match_apex()` and
  `smooth_joins()` give them the same curvature.
- Every master is built by the same code, so all masters have the same points and interpolate.
- `group1b.py` (a, s) works a little differently: the inside edges are placed by measurement maps,
  the outside edges are offsets, and today's Regular is matched exactly by carrying its small design
  differences over (they fade out towards Thin). From Bold up these letters start from today's
  Bold outlines, placed by the same maps, so Black keeps Bold's shapes.

Masters: weights 100, 400, 700, 900 × widths 65, 100, 150 (12 masters, 2 axes).

## Round 9 status (historical pilot)

| Done (Sans upright lowercase only) | Not started |
| --- | --- |
| a b c d e g h i l m n o p q r s u | f j k t v w x y z, all capitals, figures, punctuation, accents, Serif, Mono, italics, kerning, Symbols at 9 weights |

Measured at Thin 100%: every stroke 21–24 units (target 24; the 21 is the middle joint of `m`).
Regular at 100% matches today's Regular point for point in `a s` and within a few units elsewhere.
Bold (700) comes out close to today's Bold.

**Known weak points.** The owner's last verdict was "your work does not satisfy me", so treat
everything as open to change, not only these points:

- The owner never approved group 1 (a b c d e g p q s). Only the first 8 letters (n h m u r o i l)
  were judged "much better" at round 7.
- Black s and Black e at 65% are only acceptable. Their counters are very small.
- Black Compressed arches leave the stem low (deep crotches).
- In `pilot.py`, the arch letters' Regular differs from today's by up to ~10 units in some handles,
  because of the curvature smoothing.
- Heavy-weight joint thickness rules (`jo`, `arch_geometry`) were tuned by eye on a few letters.

## How to run

```sh
pip install ufoLib2 ufo2ft fonttools cairosvg pillow
python3 scripts/fullrange/build_lc.py /tmp/fr          # 12 UFO masters + AdmiraltyPilot.ttf (2-axis VF)

# checks
python3 scripts/fullrange/thick.py /tmp/fr/AdmiraltyPilot.ttf 100 100 abcdeghilmnopqrsu   # stroke thickness at Thin
python3 scripts/fullrange/overlay.py /tmp/fr/pilot-w400-d100.ufo /tmp/fr/overlay.png abcdegs   # new Regular (red) over today's (grey)
python3 scripts/fullrange/grid.py /tmp/fr/AdmiraltyPilot.ttf /tmp/fr/grid.png abcdeghilmnopqrsu 150   # 9 weights at one width
python3 scripts/fullrange/corners.py /tmp/fr/AdmiraltyPilot.ttf /tmp/fr/corners.png abcdeghilmnopqrsu
python3 scripts/fullrange/words.py /tmp/fr/AdmiraltyPilot.ttf /tmp/fr/w.png "100/150,900/65" "sea cage"
```

`review/index.html` is the last review page sent to the owner (round 9), with sliders for weight
and width. It loads `review/fonts/AdmiraltyPilot9.ttf`, which the build above reproduces.

## Rules that must survive the full build

- Sans and Serif keep **equal advance widths** per style (duplex), so switching never re-wraps lines.
- Mono stays **600 units** wide in every master.
- Italics slant **tan 9.5°**.
- Metrics: x-height 520, cap height 700, ascender 740, descender −220, overshoots 10/12, UPM 1000.
- Generated folders (`fonts/`, `packages/`, `symbols/`, `sources/`) are rebuilt from `scripts/`;
  see the main README and `AGENTS.md`.
