# Admiralty website

A one-page site that introduces the Admiralty type family: a hero word you can change with
the mouse letter by letter, a moving word strip, a same-width demo, a type tester, axis animations, eight use-case mock-ups, the 282
symbols and the character set. Plain HTML, CSS and JavaScript: no build step.

## Run it

```sh
cd site
python3 -m http.server 8000      # then open http://localhost:8000
```

Opening `index.html` straight from the disk also works.

## Files

| File | What it does |
| --- | --- |
| `index.html` | The page and all its text |
| `styles.css` | Layout and colours (main colour #3A86D4 with navy ink and near-white paper; night colours for dark mode) |
| `app.js` | Hero, same-width check, tester, axis animations, symbols, characters, tabs |
| `fonts.css` | **Which font files the page uses** |
| `type-config.js` | **What the fonts can do**: axis ranges, the radius axis tag, how italic works |
| `symbols.js` | The symbol list (name, label, code point, category, tags) from `symbols/admiralty-symbols.json` |
| `fonts/standin/` | Open stand-in fonts (see below) |
| `fonts/admiralty/` | Released Admiralty files: Symbols, and Sans and Serif for the same-width demo |

## Stand-in fonts, and how to swap in the real ones

Until the full Admiralty variable fonts (weight, width and radius) are ready, the page uses
open fonts with the same kinds of axes, all under the SIL Open Font License:

| Page family | Stand-in | Axes used |
| --- | --- | --- |
| Admiralty Sans | Google Sans Flex | weight 100–900, width 65–150, radius `ROND` 0–100, slant for italic |
| Admiralty Serif | Roboto Serif | weight 100–900, width 65–150, real italic |
| Admiralty Mono | Martian Mono | weight 100–800, width 75–112.5, no italic |

The files were reduced to these axes with fontTools (other axes fixed at their defaults). The
page only ever refers to the names `"Admiralty Sans"`, `"Admiralty Serif"` and `"Admiralty Mono"`.

To switch to the real fonts:

1. Copy the Admiralty variable WOFF2 files into `fonts/admiralty/`.
2. In `fonts.css`, point each `@font-face` to them. Use the real ranges in `font-weight` and
   `font-stretch`, and add the italic files with `font-style: italic`.
3. In `type-config.js`, set the axis ranges, set `radiusTag` to Admiralty's radius axis tag, set
   `italic: "face"` for each family that has italic files, and set `standinNote` to `""`.
4. Optional: once the real Sans and Serif have the same widths at every weight, point the
   same-width demo (`.voice-text` in `styles.css`) at them instead of the released 400–700 files.
5. Delete `fonts/standin/`.

Nothing else needs to change: the sliders, CSS output and animations read their ranges from
`type-config.js`.

## Checks done

- Chromium at 1440 × 900 and 390 × 844, day and night palettes: no console errors and no
  sideways scrolling.
- Hero: pointer and arrow keys change weight and width; the radius slider works.
- Same-width demo: lines are measured live; with the released fonts all lines end on the
  same word in Sans and Serif.
- Symbol search finds by name, label and tags (for example "like" finds heart and thumbs-up).
- Reduced motion: the hero letters, ticker and other motion stay still; everything still works by pointer, keys and sliders.
