"""Measure the large-scale ink distribution and compare local stem widths in each proof cell."""

import ctypes
import hashlib
import json
from concurrent.futures import ProcessPoolExecutor
from itertools import product
from pathlib import Path

import freetype as ft
import numpy as np
from fontTools.ttLib import TTFont
from PIL import Image
from scipy.ndimage import distance_transform_edt, maximum_filter

from build_text_family import OUTPUT, REVIEW, TEXT
from glyph_peers import reference_names

PPEM = 384
GRID = tuple(product((100,), (65, 82.5, 100, 125, 150), (0, 100))) + tuple(
    product((700, 900), (65, 150), (0, 100))
)
FIELDS = [
    "selected median diameter",
    "Regular median diameter",
    "selected ink / Regular ink",
    "ink redistribution",
    "peer 1 selected diameter difference",
    "peer 2 selected diameter difference",
]


def measurement(face, gid):
    face.load_glyph(gid, ft.FT_LOAD_RENDER | ft.FT_LOAD_NO_HINTING | ft.FT_LOAD_NO_BITMAP)
    b = face.glyph.bitmap
    if not b.width or not b.rows:
        return 0.0, 0.0, np.zeros(144)
    raw = np.frombuffer(ctypes.string_at(b._FT_Bitmap.buffer, b.pitch * b.rows), np.uint8)
    image = raw.reshape(b.rows, b.pitch)[:, : b.width]
    # Include the white exterior, even where the crop touches a solid edge.
    mask = np.pad(image >= 128, 1)
    distance = distance_transform_edt(mask)
    ridge = (distance > 0) & (distance >= maximum_filter(distance, 3) - 0.08)
    # A median of local in-ink diameters is comparable across width changes.
    # On filled shapes it measures the body itself. It is not a pen width there.
    diameter = np.median(distance[ridge]) * 2000 / PPEM if ridge.any() else 0.0
    area = float(image.sum()) / (255 * PPEM**2)
    thumbnail = np.asarray(Image.fromarray(image).resize((12, 12), Image.Resampling.BOX), float).ravel()
    return diameter, area, thumbnail / max(thumbnail.sum(), 1)


def examine(args):
    directory, family = args
    path = directory / (family + "[wght,wdth,RADI].ttf")
    with TTFont(path) as tt:
        names = tt.getGlyphOrder()
        peers = reference_names(tt)
        ids = {n: i for i, n in enumerate(names)}
        neighbors = np.array([[ids[p] for p in peers[n]] for n in names])
    faces = [ft.Face(str(path)) for w in (100, 400)]
    for face in faces:
        face.set_pixel_sizes(0, PPEM)
    rows = [[] for n in names]
    for weight, width, radius in GRID:
        for face, w in zip(faces, (weight, 400)):
            face.set_var_design_coords((w, width, radius))
        pairs = [[measurement(face, gid) for face in faces] for gid in range(len(names))]
        stems = np.array([[x[0] for x in pair] for pair in pairs])
        for i, (light, regular) in enumerate(pairs):
            a, ink0, profile0 = light
            b, ink1, profile1 = regular
            if bool(ink0) != bool(ink1):
                raise ValueError((family, names[i], width, radius, "visible at only one weight"))
            # Total variation of two unit-mass images, independent of origin
            # and total ink. This highlights displaced bowls, shoulders or bars.
            change = np.abs(profile1 - profile0).sum() / 2
            deltas = a - stems[neighbors[i], 0]
            rows[i].append(
                [
                    round(a, 1),
                    round(b, 1),
                    round(ink0 / ink1, 3) if ink1 else None,
                    round(float(change), 3),
                    *np.round(deltas, 1),
                ]
            )
    print(
        f"{family}: {len(names)} GIDs at {PPEM}px, {len(names) * len(GRID)} weight pairs, "
        f"{len(names) * len(GRID) * 2} same-setting peer comparisons",
        flush=True,
    )
    return family, dict(
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        glyphs={n: dict(peers=peers[n], cells=c) for n, c in zip(names, rows)},
    )


def build(directory=OUTPUT, out=REVIEW / "audits" / "thin-reference.json"):
    with ProcessPoolExecutor(4) as pool:
        faces = dict(pool.map(examine, [(directory, f) for f in TEXT]))
    out.write_text(json.dumps(dict(ppem=PPEM, grid=GRID, fields=FIELDS, faces=faces), separators=(",", ":")))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fonts", type=Path, default=OUTPUT)
    parser.add_argument("--out", type=Path, default=REVIEW / "audits" / "thin-reference.json")
    args = parser.parse_args()
    build(args.fonts, args.out)
