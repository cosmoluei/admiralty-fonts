/*
  What the fonts can do. Change this together with fonts.css when the fonts change.

  axes:   the range of each axis the page offers, per family. Leave an axis out if the family
          does not have it; its slider is then disabled for that family.
  radius: the axis tag of the radius axis (Admiralty uses RADI).
  italic: "face" = a real italic font file (font-style: italic);
          "slnt" = an upright font with a slant axis;
          null   = no italic.
*/
window.TYPE = {
  radiusTag: "RADI",
  families: {
    sans:  { css: '"Admiralty Sans", system-ui, sans-serif',  label: "Sans",
             axes: { wght: [100, 900], wdth: [65, 150], radius: [0, 100] }, italic: "face" },
    serif: { css: '"Admiralty Serif", Georgia, serif',         label: "Serif",
             axes: { wght: [100, 900], wdth: [65, 150], radius: [0, 100] }, italic: "face" },
    mono:  { css: '"Admiralty Mono", ui-monospace, monospace', label: "Mono",
             axes: { wght: [100, 900], wdth: [65, 150], radius: [0, 100] }, italic: "face" },
  },
  // A note shown in the footer (for example while preview fonts are in use). Empty: no note.
  standinNote: "",
};
