# Admiralty website

A one-page site that works like a type tool. The opening word sits in a selection box: drag
its handles to change weight, width and radius. A divider runs through one paragraph with
Serif on one side and Sans on the other. "Put it to work" is a workbench with six real
interfaces (code editor, operations dashboard, reading app, assistant chat, poster maker,
station sign) whose main text follows one set of controls. Then the 282 symbols, the
character set and install code. Plain HTML, CSS and JavaScript: no build step.

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
| `styles.css` | Layout and colours (blue #3A86D4 for everything you can act on, a dotted canvas, night colours for dark mode) |
| `app.js` | Hero handles, the Serif/Sans divider and its live check, the workbench and its six interfaces, symbols, characters |
| `fonts.css` | **Which font files the page uses** |
| `type-config.js` | **What the fonts can do**: axis ranges, the radius axis tag, how italic works |
| `symbols.js` | The symbol list (name, label, code point, category, tags) from `symbols/admiralty-symbols.json` |
| `fonts/standin/` | Open stand-in fonts (see below) |
| `fonts/admiralty/` | Released Admiralty files: Mono, Symbols, and Sans and Serif for the same-width demo |

## Stand-in fonts, and how to swap in the real ones

Until the full Admiralty variable fonts (weight, width and radius) are ready, the page uses
open fonts with the same kinds of axes, under the SIL Open Font License. Mono already uses the
released Admiralty Mono (weight 400–700, with italic and box drawing):

| Page family | Stand-in | Axes used |
| --- | --- | --- |
| Admiralty Sans | Google Sans Flex | weight 100–900, width 65–150, radius `ROND` 0–100, slant for italic |
| Admiralty Serif | Roboto Serif | weight 100–900, width 65–150, real italic |

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

- Chromium at 1440 × 900 and 390 × 844, day and night colours: no console errors and no
  sideways scrolling, in every workbench interface.
- Hero handles work with the pointer and the arrow keys.
- The divider demo measures the lines live: with the released fonts all lines break on the
  same word in Sans and Serif.
- Workbench: the controls change the main text of each interface; the dashboard period,
  sorting and chart tooltip, the chat composer, the poster colours and layout, the sign's
  fit-by-width and the editor's files and lines all work.
- Reduced motion: no opening animation, no handle pulse and no blinking caret.
