"""Rebuild the self-contained corner proof with real web fonts (no font installation)."""
import base64
import re
import string
import unicodedata
from io import BytesIO
from pathlib import Path

from fontTools import subset
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.roundingPen import RoundingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

from study_shapes import LETTERS, letter_outline

HERE = Path(__file__).resolve().parent
REVIEW = HERE / "review"
RELEASE = HERE.parents[1] / "fonts/variable/AdmiraltySans[wght].ttf"
WIDTHS = (65, 100, 150)


def proof_subset(path, letters):
    font = TTFont(path, recalcTimestamp=False)
    options = subset.Options()
    options.name_IDs = [0, 1, 2, 3, 4, 5, 6, 13, 14, 16, 17]
    cutter = subset.Subsetter(options=options)
    cutter.populate(text=letters + " ")
    cutter.subset(font)
    return font


def face_rule(family, font):
    data = BytesIO()
    font["name"].setName("Copyright 2026 The Admiralty Project Authors", 0, 3, 1, 0x409)
    font["name"].setName("SIL Open Font License, Version 1.1", 13, 3, 1, 0x409)
    font["name"].setName("https://openfontlicense.org", 14, 3, 1, 0x409)
    font.flavor = "woff2"
    font.save(data)
    encoded = base64.b64encode(data.getvalue()).decode("ascii")
    return f"@font-face{{font-family:{family};src:url(data:font/woff2;base64,{encoded}) format('woff2')}}"


def make_instance(weight, width, prior, allowance=False):
    # Carry forward the corresponding first proof, including its A/B spacing.
    font = TTFont(BytesIO(base64.b64decode(prior)), recalcTimestamp=False)
    glyphs = font.getGlyphSet()
    strings = {}
    for name in font.getGlyphOrder():
        advance = font["hmtx"][name][0]
        if name == "space":
            advance = round(260 * width / 100)
        pen = T2CharStringPen(advance, glyphs, roundTolerance=0)
        if name in LETTERS:
            shape = letter_outline(name, advance, weight, width)
            # Absolute grid positions remain exactly representable as Type 2 deltas.
            shape.draw(RoundingPen(pen, roundFunc=lambda x: round(x * 4096) / 4096))
            font["hmtx"][name] = (advance, round(shape.bounds[0]))
        else:
            glyphs[name].draw(pen)
            font["hmtx"][name] = (advance, font["hmtx"][name][1])
        strings[name] = pen.getCharString()
    title = f"Admiralty A Study {weight} {width}" + (" B" if allowance else "")
    del font["glyf"], font["loca"], font["STAT"]
    builder = FontBuilder(font=font)
    builder.setupMaxp()
    builder.setupCFF(title.replace(" ", ""), {"FullName": title, "FamilyName": title},
                     strings, {})
    names = font["name"]
    for name_id, value in [(1,title),(2,"Regular"),(3,title),(4,title),(6,title.replace(" ","")),(16,title),(17,"Regular")]:
        names.setName(value,name_id,3,1,0x409)
    return font


def main():
    base = instantiateVariableFont(TTFont(RELEASE, recalcTimestamp=False), {"wght": 400}, inplace=True)
    mapped = base.getBestCmap()
    extended = [chr(cp) for cp in sorted(mapped) if cp > 127 and unicodedata.category(chr(cp)).startswith("L")]
    latin = [c for c in extended if "LATIN" in unicodedata.name(c, "")]
    other = [c for c in extended if c not in latin]
    pilot_path = REVIEW / "fonts/AdmiraltyPilot9.ttf"
    with TTFont(pilot_path) as pilot:
        pilot_only = "".join(c for c in string.ascii_lowercase if ord(c) in pilot.getBestCmap() and c not in LETTERS)
    missing = "".join(c for c in string.ascii_lowercase if c not in LETTERS + pilot_only)
    archive = (REVIEW / "fonts/word-proof-first.css").read_text()
    prior = dict(re.findall(r"font-family:(First\w+);src:url\(data:font/woff2;base64,([^)]*)", archive))
    previous = (REVIEW / "fonts/word-proof-letter-study.css").read_text()
    faces = [face_rule("Reference", base), face_rule("PilotLetters", proof_subset(pilot_path, pilot_only)), previous]
    for weight in (100, 900):
        for width in WIDTHS:
            faces.append(face_rule(f"Study{weight}x{width}", make_instance(weight, width, prior[f"First{weight}x{width}"])))
    faces.append(face_rule("StudyAllowance", make_instance(900, 65, prior["FirstAllowance"], allowance=True)))
    template = (HERE / "word_proof.template.html").read_text()
    license_text = (HERE.parents[1] / "OFL.txt").read_text()
    page = template.replace("/* FONT DATA */", "\n".join(faces))
    for key, value in {"PILOT_LETTERS": pilot_only, "STUDY_LETTERS": LETTERS, "MISSING_LETTERS": missing,
                       "LATIN_COUNT": str(len(latin)), "EXTENDED_LATIN": " ".join(latin),
                       "OTHER_LETTERS": " ".join(other)}.items():
        page = page.replace("{{" + key + "}}", value)
    (REVIEW / "word-proof.html").write_text(page.replace("<!-- FONT LICENSE -->", f'<script type="text/plain" id="font-license">{license_text}</script>'))


if __name__ == "__main__":
    main()
