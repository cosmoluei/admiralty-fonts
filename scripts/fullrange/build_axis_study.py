"""Compile the hand-drawn Sans proof as a single, independently adjustable OpenType font."""
import base64
import itertools
import re
from array import array
from io import BytesIO

import numpy as np
from fontTools.fontBuilder import FontBuilder
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import ttProgram
from fontTools.ttLib.tables.TupleVariation import TupleVariation
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from fontTools.varLib.models import VariationModel, normalizeLocation

from build_word_proof import HERE, RELEASE, REVIEW, WIDTHS, make_instance
from compatible import OutlinePen, Profile, compatible_points, ordered_contours
from study_shapes import LETTERS as WORD_LETTERS
from related_letters import RELATED, related_outline
from remaining_lowercase import LETTERS as EXTRA, remaining_outline

LETTERS = "".join(sorted(WORD_LETTERS + RELATED + EXTRA))


AXES = {"wght": (100, 400, 900), "wdth": (65, 100, 150), "RADI": (0, 0, 100)}
CELLS = [(400, 100)] + [p for p in itertools.product((100, 400, 900), WIDTHS) if p != (400, 100)]
LOCATIONS = [dict(wght=w, wdth=d, RADI=r) for w, d in CELLS for r in (0, 100)]
MODEL = VariationModel([normalizeLocation(loc, AXES) for loc in LOCATIONS], axisOrder=list(AXES))
FILENAME = "AdmiraltySans-AxisStudy"
# Shape design stays in the 1000-unit project coordinate system. Subunits in the
# proof reduce the influence of integer rounding on adjoining smooth curves.
SCALE = 4


def master_glyph_sets():
    first = (REVIEW / "fonts/word-proof-first.css").read_text()
    prior = dict(re.findall(r"font-family:(First\w+);src:url\(data:font/woff2;base64,([^)]*)", first))
    pilot = TTFont(REVIEW / "fonts/AdmiraltyPilot9.ttf")
    release = TTFont(RELEASE)
    masters = []
    for w, d in CELLS:
        if (w, d) == (400, 100):
            gs = release.getGlyphSet()
        elif w == 400:
            gs = pilot.getGlyphSet(location={"wght": w, "wdth": d})
        else:
            gs = make_instance(w, d, prior[f"First{w}x{d}"], blend_branches=False).getGlyphSet()
        masters.append(gs)
    return masters


def master_outline(name, cell, source, regular):
    w, d = cell
    if (name in RELATED and w != 400) or (name in EXTRA and cell != (400, 100)):
        sibling = "n" if name in "hrkf" else "i" if name in "jt" else "m" if name=="w" else "d"
        advance = round(source[sibling].width+(regular[name].width-regular[sibling].width)*d/100)
        designer = remaining_outline if name in EXTRA else related_outline
        return designer(name, advance, w, d), advance
    return source[name], source[name].width


def compile_glyph(name, sources):
    outlines, widths = [], []
    regular = sources[0]
    for (w, d), gs in zip(CELLS, sources):
        pen = OutlinePen(gs)
        shape, advance = master_outline(name, (w, d), gs, regular)
        shape.draw(pen)
        outlines.append(pen.contours)
        if name == "space":
            advance = round(260*d/100)
        widths.extend([advance]*2)

    reference = outlines[0]
    ordered = [ordered_contours(reference, cs) for cs in outlines]
    tracks = [[] for loc in LOCATIONS]
    ends = []
    for i, base in enumerate(reference):
        anchors = base.terminals(bar=name == "e")
        if len(anchors) >= 2:
            base = base.roll(anchors[0])
        profiles = []
        for j, (weight, width) in enumerate(CELLS):
            c = ordered[j][i]
            registered = c.registered(base, bar=name == "e") if j else (base, [0, 1], [0, 1])
            max_radius = 0 if name == ".notdef" else {100: 9, 400: 30, 900: 49}[weight]
            profiles.extend(Profile(*registered, radius) for radius in (0, max_radius))
        paths = compatible_points(profiles, tolerance=.19)
        for track, path in zip(tracks, paths):
            track.extend(path)
        ends.append(len(tracks[0])-1)

    all_coords = []
    for track, advance in zip(tracks, widths):
        coords = np.array([*track, 0, advance, 0, 0], dtype=complex)
        all_coords.append(np.rint(SCALE*np.column_stack([coords.real, coords.imag])).astype(int))
    glyph = Glyph()
    glyph.numberOfContours = len(ends)
    glyph.coordinates = GlyphCoordinates(all_coords[0][:-4].tolist())
    glyph.endPtsOfContours = ends
    glyph.flags = array("B", [1, 0]*(len(tracks[0])//2))
    glyph.program = ttProgram.Program()
    glyph.program.fromBytecode([])
    lsb = min((x for x, y in glyph.coordinates), default=0)
    deltas = MODEL.getDeltas(all_coords)
    var = [TupleVariation(region, [tuple(p) for p in delta.tolist()])
           for region, delta in zip(MODEL.supports[1:], deltas[1:]) if np.any(delta)]
    return glyph, (round(widths[0]*SCALE), lsb), var


def build():
    sources = master_glyph_sets()
    release = TTFont(RELEASE)
    glyphs, metrics, variations = {}, {}, {}
    order = [".notdef", "space", *LETTERS]
    for name in order:
        if name == ".notdef":
            # Retain the release's missing-glyph sign at every point on each axis.
            gs = [sources[0]]*len(sources)
        else:
            gs = sources
        glyphs[name], metrics[name], variations[name] = compile_glyph(name, gs)
    b = FontBuilder(1000*SCALE, isTTF=True)
    b.setupGlyphOrder(order)
    b.setupCharacterMap({ord(c): c for c in LETTERS} | {32: "space"})
    b.setupGlyf(glyphs)
    b.setupHorizontalMetrics(metrics)
    hh = release["hhea"]
    b.setupHorizontalHeader(ascent=hh.ascent*SCALE, descent=hh.descent*SCALE, lineGap=hh.lineGap*SCALE)
    name = "Admiralty Sans Axis Study"
    b.setupNameTable({"familyName": name, "styleName": "Regular", "psName": FILENAME,
                      "fullName": name, "uniqueFontIdentifier": "0.301;" + FILENAME,
                      "version": "Version 0.301 (study)", "copyright": release["name"].getDebugName(0),
                      "licenseDescription": release["name"].getDebugName(13),
                      "licenseInfoURL": release["name"].getDebugName(14)})
    os2 = release["OS/2"]
    b.setupOS2(**{k: SCALE*getattr(os2, k) for k in [
        "sTypoAscender", "sTypoDescender", "sTypoLineGap", "usWinAscent", "usWinDescent", "sxHeight", "sCapHeight"]},
        version=4, fsSelection=os2.fsSelection)
    b.setupPost()
    axis_names = {"wght": "Weight", "wdth": "Width", "RADI": "Corner radius"}
    weights = ["Thin", "ExtraLight", "Light", "Regular", "Medium", "SemiBold", "Bold", "ExtraBold", "Black"]
    b.setupFvar([(k, *v, axis_names[k]) for k, v in AXES.items()],
                [{"location": {"wght": i*100, "wdth": 100, "RADI": 0}, "stylename": n}
                 for i, n in enumerate(weights, 1)])
    b.setupStat([{"tag": k, "name": v} for k, v in axis_names.items()])
    b.setupGvar(variations)
    b.font["head"].created = b.font["head"].modified = release["head"].created
    b.font.recalcTimestamp = False
    dest = REVIEW / "fonts" / (FILENAME + ".ttf")
    b.save(dest)
    b.font.flavor = "woff2"
    output = BytesIO()
    b.save(output)
    (REVIEW / "fonts" / (FILENAME + ".woff2")).write_bytes(output.getvalue())
    return base64.b64encode(output.getvalue()).decode()


if __name__ == "__main__":
    webfont = build()
    template = (HERE / "axis_study.template.html").read_text()
    (REVIEW / "axis-study.html").write_text(template.replace("{{FONT}}", webfont).replace("{{LETTERS}}", LETTERS))
