# Full weight and width range: work in progress (handoff)

**Status: unfinished experiment.** Nothing in this folder is used by the release build
(`scripts/build_fonts.py`), and the released fonts in `fonts/` and `packages/` are not changed by it.
This file explains where the work stands, so another person or coding agent can continue it.

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

## Status

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
