"""Build a self-contained before/after proof and follow-up annotation page."""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
import uharfbuzz as hb

from audit_symbol_family import BY_NAME, shape

HERE = Path(__file__).resolve().parent


@lru_cache(None)
def load_font(path):
    raw = path.read_bytes()
    with TTFont(path) as font:
        ids = {name: i for i, name in enumerate(font.getGlyphOrder())}
    return hb.Font(hb.Face(raw)), hashlib.sha256(raw).hexdigest(), ids


def path_at(font, gid, x, y, scale):
    pen = SVGPathPen(None)
    font.draw_glyph_with_pen(gid, pen)
    return f'<path transform="translate({x:g} {y:g}) scale({scale:g} {-scale:g})" d="{pen.getCommands()}"/>'


def render(issue, folder, frame, original=False):
    font, digest, ids = load_font(folder / Path(issue["fontFile"]).name)
    name = issue["glyph"]
    if original and (digest != issue["fontSha256"] or ids[name] != issue["glyphID"]):
        raise ValueError(f"Original font does not match the marked case: {issue['family']} {name}")
    font.set_variations({axis: issue[axis] for axis in ("wght", "wdth", "RADI")})
    gid = ids[name]
    if issue["family"] == "AdmiraltySymbols":
        symbol = BY_NAME[name.removesuffix(".rtl").replace("_", "-")]
        gid, _ = shape(font, symbol.codepoint, "rtl" if name.endswith(".rtl") else "ltr")
    scale = frame["fontSize"] / font.face.upem
    center, baseline = frame["textX"], frame["baseline"]
    x = center - font.get_glyph_h_advance(gid) * scale / 2
    glyph = path_at(font, gid, x, baseline, scale)
    sequence = []
    if issue.get("sequence"):
        buf = hb.Buffer()
        buf.add_str(issue["sequence"])
        buf.guess_segment_properties()
        hb.shape(font, buf, {"ss01": True})
        x = center - sum(pos.x_advance for pos in buf.glyph_positions) * scale / 2
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            sequence.append(path_at(font, info.codepoint, x + pos.x_offset * scale,
                                    baseline - pos.y_offset * scale, scale))
            x += pos.x_advance * scale
    return {"glyph": glyph, "sequence": "".join(sequence)}, digest, ids[name], gid


def build(report_path, original, revised, output):
    data = report_path.read_bytes()
    report = json.loads(data)
    frame = report["annotationFrame"]
    rows = []
    for issue in sorted(report["issues"], key=lambda r: (r["glyph"].casefold(), r["glyph"], r["family"],
                                                          r["wght"], r["wdth"], r["RADI"])):
        old, _, _, _ = render(issue, original, frame, original=True)
        new, digest, new_id, rendered_id = render(issue, revised, frame)
        rows.append(dict(issue=issue, old=old, new=new, fontSha256=digest,
                         glyphID=new_id, renderedGlyphID=rendered_id))
    payload = dict(rows=rows, annotationFrame=frame, sourceExport=report["exportedAt"],
                   sourceSha256=hashlib.sha256(data).hexdigest())
    if "axisProof" in report:
        payload["axisProof"] = report["axisProof"]
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("<", r"\u003c")
    html = (HERE / "comparison_review.html.in").read_text().replace("/* REVIEW DATA */", encoded)
    output.write_text(html)
    print(f"{len(rows)} marked combinations in {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("report", "original", "revised", "output"):
        parser.add_argument(arg, type=Path)
    args = parser.parse_args()
    build(args.report, args.original, args.revised, args.output)
