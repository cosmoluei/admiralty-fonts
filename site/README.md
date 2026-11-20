# Admiralty website

A one-page site that works like a type tool. The opening word is the control: drag it sideways
for width and up or down for weight, or use the sliders, which also set the radius. A divider runs through one paragraph with
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
| `styles.css` | Layout and colours (warm neutrals with blue #3A86D4 for the selected word, main actions and focus, plus coral, yellow and green accents; night colours for dark mode) |
| `app.js` | The draggable hero word and its sliders, the Serif/Sans divider and its live check, the workbench and its six interfaces, symbols, characters |
| `fonts.css` | **Which font files the page uses** |
| `type-config.js` | **What the fonts can do**: axis ranges, the radius axis tag, how italic works |
| `symbols.js` | The symbol list (name, label, code point, category, tags) from `symbols/admiralty-symbols.json` |
| `fonts/admiralty/` | The Admiralty variable fonts: Sans, Serif and Mono with italics, and Symbols |

## Fonts

The page uses the full-range Admiralty variable fonts from `fonts/variable/fullrange/`
(weight 100–900, width 65–150%, corner radius `RADI` 0–100, with real italics), copied into
`fonts/admiralty/` with simpler file names. The Symbols file is reduced to its weight axis
(width 100, radius 0) with fontTools, to keep it small. Sans and Serif share letter widths at every
setting, so the Serif/Sans divider uses the same files as the rest of the page.

When the fonts change:

1. Copy the new WOFF2 files into `fonts/admiralty/` (or point `fonts.css` at new names).
2. If an axis range or tag changes, update `type-config.js`. The sliders, CSS output and
   animations read their ranges from there.

## Checks done

- Chromium at 1440 × 900 and 390 × 844, day and night colours: no console errors and no
  sideways scrolling, in every workbench interface.
- Hero: dragging the word, the arrow keys and the sliders all work; dragging never selects text.
- The divider demo measures the lines live: with the released fonts all lines break on the
  same word in Sans and Serif.
- Workbench: the controls change the main text of each interface; the dashboard period,
  sorting and chart tooltip, the chat composer, the poster colours and layout, the sign's
  fit-by-width and the editor's files and lines all work.
- Reduced motion: no opening animation, no handle pulse and no blinking caret.
