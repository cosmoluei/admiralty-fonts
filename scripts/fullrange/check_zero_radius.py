"""Measure the two bowl-to-stem notches at zero radius in the exported fonts."""
import argparse
import hashlib
import json
from itertools import product
from pathlib import Path

import numpy as np
import uharfbuzz as hb
from fontTools.ttLib import TTFont

from build_text_family import OUTPUT, TEXT
from check_optical_inventory import unsheared
from check_word_proof import section

GRID = tuple(product(range(100, 901, 100), (65, 82.5, 100, 125, 150)))
BOWLS = {"b", "d", "p", "q", "thorn", "dcroat", "uni20AB"}


def bowl_name(glyf, name):
    while name not in BOWLS:
        g = glyf[name]
        if not g.isComposite():
            return None
        name = g.components[0].glyphName
    return name


def notch_angles(edges, base):
    # Reflect the left and descending stems into the same frame as d.
    if base in ("b", "p", "thorn"):
        edges = -edges.conjugate()
    if base in ("p", "q"):
        edges = edges.conjugate() + 520j
    breaks = np.flatnonzero(abs(edges[1:, 0] - edges[:-1, 1]) > .1) + 1

    def twice_area(edges):
        return np.sum((edges[:, 0].conj() * edges[:, 1]).imag)

    outer = max(np.split(edges, breaks), key=lambda e: abs(twice_area(e)))
    # Use only the outside of the base so an accent or currency bar cannot
    # masquerade as a corner at the foot of the letter.
    wall = section(outer, 648)[0]
    points = np.r_[outer[:, 0], outer[-1, 1]]
    arc = np.r_[0., np.cumsum(abs(np.diff(points)))]
    positions = np.linspace(0, arc[-1], int(np.ceil(arc[-1])), endpoint=False)
    z = np.interp(positions, arc, points)
    before = np.interp((positions - 5) % arc[-1], arc, points)
    after = np.interp((positions + 5) % arc[-1], arc, points)
    angles = np.degrees(np.angle((z-before).conj() * (after-z))) * -np.sign(twice_area(outer))
    scores = []
    for low, high in ((285, 563), (-5, 226)):
        mask = (z.real > wall-65) & (z.real < wall+48) & (z.imag > low) & (z.imag < high)
        scores.append(round(float(angles[mask].max()), 1) if mask.any() else 0.)
    return scores


def inspect(directory, family):
    path = directory / (family + "[wght,wdth,RADI].ttf")
    raw = path.read_bytes()
    font = hb.Font(hb.Face(raw))
    worst, failures = {}, []
    with TTFont(path) as tt:
        slope = np.tan(np.deg2rad(-tt["post"].italicAngle))
        bases = {n: base for n in tt.getGlyphOrder() if (base := bowl_name(tt["glyf"], n))}
        for weight, width in GRID:
            font.set_variations(dict(wght=weight, wdth=width, RADI=0))
            for name, base in bases.items():
                edge = unsheared(font, tt.getGlyphID(name), slope)
                angles = notch_angles(edge, base)
                for side, angle in zip(("upper", "lower"), angles):
                    key = name + "/" + side
                    if key not in worst or angle < worst[key][0]:
                        worst[key] = [angle, weight, width]
                    # A design may use an oblique junction. Even that notch
                    # must make a localized turn over a five-unit chord.
                    if angle < 55:
                        failures.append([name, side, weight, width, angle])
        if family == "AdmiraltySans-Italic":
            # The shape from the actual annotation must still react to RADI.
            for radius in (0, 100):
                font.set_variations(dict(wght=900, wdth=150, RADI=radius))
                angles = notch_angles(unsheared(font, tt.getGlyphID("d"), slope), "d")
                if radius == 0:
                    sharp = angles
                elif min(np.array(sharp)-angles) < 35:
                    failures.append(["d", "positive radius response", sharp, angles])
    return dict(sha256=hashlib.sha256(raw).hexdigest(), glyphs=len(bases),
                checks=2*len(GRID)*len(bases), minimumAngles=worst, failures=failures)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fonts", type=Path, default=OUTPUT)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    rows = {f: inspect(args.fonts, f) for f in TEXT}
    if args.out:
        args.out.write_text(json.dumps(rows, indent=2) + "\n")
    for f, row in rows.items():
        print(f, row["checks"], "junction checks,", len(row["failures"]), "failures", row["failures"][:1])
    raise SystemExit(any(row["failures"] for row in rows.values()))
