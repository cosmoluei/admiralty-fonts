"""Rank recurring optical defects in compiled fonts and localize them on the review canvas.

Run with --fonts pointing at one build. Optional --labels accepts an export from
that exact build and measures overlap without treating unmarked cells as negatives.
"""
import argparse
import hashlib
import json
from itertools import chain, product
from pathlib import Path

import numpy as np
import uharfbuzz as hb
from fontTools.ttLib import TTFont

from build_text_family import OUTPUT
from check_cross_heavy import waist_landmark
from check_optical_inventory import unsheared
from check_word_proof import section


def flat_ends(edges, cap, shoulder):
    # Fit away from the tip: a diagonal changes horizontal position with
    # height even when its perpendicular stroke width is exactly constant.
    for label, height, inward, band in (("stem-foot", 0, 1, 0), ("leg-foot", 0, 1, 1),
                                        ("stem-head", cap, -1, 0), ("arm-end", shoulder, -1, 1)):
        body_heights = height + inward * np.array([62., 72., 82.])
        body = [section(edges, y).reshape(-1, 2) for y in body_heights]
        count = len(body[0])
        if count <= band or any(len(row) != count for row in body):
            continue
        model = np.polyfit(body_heights, [np.ptp(row[band]) for row in body], 1)
        tips = []
        for y in height + inward * np.array([.5, 1., 1.5, 2., 3.]):
            cuts = section(edges, y).reshape(-1, 2)
            if len(cuts) != count:
                continue
            tip = cuts[band]
            predicted = np.polyval(model, y)
            if predicted > 0:
                tips.append((1 - np.ptp(tip)/predicted, y, tip, predicted))
        # A single slice through an almost coincident node can split one
        # stroke in two. Require support from distinct adjacent heights.
        if len(tips) < 3:
            continue
        loss, y, tip, predicted = sorted(tips, key=lambda item: item[0])[len(tips)//2]
        if loss > .20 and loss * predicted > 4:
            yield label, complex(tip.mean(), y), {
                "tipWidth": round(float(np.ptp(tip)), 2), "expectedWidth": round(float(predicted), 2),
                "fractionMissing": round(float(loss), 3)}


def arm_junction(edges, shoulder):
    # Follow the exposed upper edge of k back toward the stem. Its normal
    # departure measures a shelf or a kink independently of the arm slope.
    stem = section(edges, .79 * edges.imag.max())
    heights = np.linspace(.76 * shoulder, .87 * shoulder, 9)
    cuts = [section(edges, y) for y in heights]
    if len(stem) != 2 or any(len(row) != 4 for row in cuts):
        return
    xs = np.array([row[-2] for row in cuts])
    slope, intercept = np.polyfit(xs, heights, 1)
    if slope <= 0 or np.ptp(heights - slope * xs) > 2:
        return
    left, right = stem
    near = np.linspace(right+4, right+.39*(xs[-1]-right), 30)
    if near[-1] <= near[0]:
        return
    exposed = [section(edges, x, vertical=True) for x in near]
    if any(not len(row) for row in exposed):
        return
    ys = np.array([row[-1] for row in exposed])
    residual = (ys - (slope * near + intercept)) / np.hypot(1, slope)
    i = np.argmax(abs(residual))
    offset = abs(residual[i])
    if offset > max(6., .15 * (right-left)):
        yield "arm-junction", complex(near[i], ys[i]), {"normalOffset": round(float(offset), 2)}


def bowl_waist(edges):
    # Distance by which the waist recedes behind BOTH bowls, as a fraction
    # of total width. This threshold was calibrated for Admiralty Sans / Mono B.
    waist, recess = waist_landmark(edges)
    if recess <= .065:
        yield "bowl-waist", waist, {"relativeRecess": round(float(recess), 4)}


def scan(directory, widths=(65, 100, 150), radii=(0, 100)):
    rows = []
    for file in sorted(directory.glob("*[[]wght,wdth,RADI].ttf")):
        family = file.name.split("[")[0]
        if not family.startswith(("AdmiraltySans", "AdmiraltyMono")):
            continue
        binary = file.read_bytes()
        digest = hashlib.sha256(binary).hexdigest()
        font = hb.Font(hb.Face(binary))
        with TTFont(file) as tt:
            slope = np.tan(np.deg2rad(-tt["post"].italicAngle))
            upm = tt["head"].unitsPerEm
            shoulder = tt["OS/2"].sxHeight
            for name in (("k", "B") if "Sans" in family else ("B",)):
                gid = tt.getGlyphID(name)
                for w, d, r in product(range(100, 901, 100), widths, radii):
                    # A rounded end purposely narrows near the cut.
                    if name == "k" and r:
                        continue
                    font.set_variations(dict(wght=w, wdth=d, RADI=r))
                    edges = unsheared(font, gid, slope)
                    if name == "k":
                        checks = chain(flat_ends(edges, edges.imag.max(), shoulder), arm_junction(edges, shoulder))
                    else:
                        checks = bowl_waist(edges)
                    findings = []
                    for rule, point, measure in checks:
                        x = point.real + point.imag*slope - font.get_glyph_h_advance(gid)/2
                        findings.append(dict(rule=rule, x=round(.5+x*1000/upm/1440, 6),
                                             y=round((1030-point.imag*1000/upm)/1440, 6), **measure))
                    rows.append(dict(family=family, glyph=name, glyphID=gid, fontSha256=digest,
                                     wght=w, wdth=d, RADI=r, findings=findings))
    return rows


def label_matches(rows, exports):
    def key(r):
        return tuple(r[k] for k in ("fontSha256", "glyph", "wght", "wdth", "RADI"))
    scanned = {key(r): r for r in rows}
    results = []
    for path in exports:
        labels = json.loads(path.read_text())["issues"]
        matched = flagged = hit = region_count = 0
        for label in labels:
            row = scanned.get(key(label))
            if row is None:
                continue
            matched += 1
            flagged += bool(row["findings"])
            for box in label.get("regions", []):
                region_count += 1
                cx, cy = box["x"]+box["w"]/2, box["y"]+box["h"]/2
                hit += any(((p["x"]-cx)/(box["w"]/2))**2 + ((p["y"]-cy)/(box["h"]/2))**2 <= 1
                           for p in row["findings"] if box["w"] and box["h"])
        results.append(dict(file=path.name, labels=len(labels), sameBuildAndRule=matched,
                            flaggedCases=flagged, markedEllipses=region_count, hitEllipses=hit))
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fonts", type=Path, default=OUTPUT)
    parser.add_argument("--labels", type=Path, nargs="*", default=[])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    rows = scan(args.fonts)
    if not rows:
        parser.error("No supported Admiralty variable fonts in --fonts")
    result = dict(schema="admiralty-geometry-scan/1", units="font units; x/y normalized to 1440 review canvas",
                  rows=rows, labels=label_matches(rows, args.labels))
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"{sum(bool(r['findings']) for r in rows)} of {len(rows)} cells flagged", result["labels"])
