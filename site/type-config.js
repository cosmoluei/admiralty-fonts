/*
  What the fonts can do. Change this together with fonts.css when the real fonts arrive.

  axes:   the range of each axis the page offers, per family. Leave an axis out if the family
          does not have it; its slider is then disabled for that family.
  radius: the axis tag of the radius axis. Custom axes are four capital letters (the stand-in
          uses ROND). Use Admiralty's own tag here.
  italic: "face" = a real italic font file (font-style: italic);
          "slnt" = an upright font with a slant axis (the stand-in Sans);
          null   = no italic.
*/
window.TYPE = {
  radiusTag: "ROND",
  families: {
    sans:  { css: '"Admiralty Sans", system-ui, sans-serif',  label: "Sans",
             axes: { wght: [100, 900], wdth: [65, 150], radius: [0, 100] }, italic: "slnt", slnt: -10 },
    serif: { css: '"Admiralty Serif", Georgia, serif',         label: "Serif",
             axes: { wght: [100, 900], wdth: [65, 150] }, italic: "face" },
    mono:  { css: '"Admiralty Mono", ui-monospace, monospace', label: "Mono",
             axes: { wght: [400, 700] }, italic: "face" },
  },
  // Shown in the footer while stand-ins are in use. Set to "" when the real fonts are in.
  standinNote: "Preview: until the full Admiralty variable fonts are ready, this page uses open stand-in fonts with the same kinds of axes (Google Sans Flex and Roboto Serif, under the SIL Open Font License). Mono, the icons and the same-width demo already use the released Admiralty fonts.",
};
