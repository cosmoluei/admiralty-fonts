"""Prototype: Admiralty with weights 100-900 and widths 75-125 (draft, generated).

Thin..Black are extrapolated from the matched Regular and Bold masters along a stem-weight
curve; Condensed / Expanded scale the outlines horizontally and take the x coordinates from a
heavier (or lighter) weight, so vertical stems keep their thickness. Builds one 2-axis variable
font per family (subset: Latin letters, figures, punctuation and a few accented letters).
"""
import sys, math, json
from pathlib import Path
import ufoLib2
from ufoLib2.objects import Glyph
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.pointPen import SegmentToPointPen
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor
import ufo2ft

SRC = Path(__file__).resolve().parents[3] / "sources"
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

# stem thickness relative to Regular, per weight (a common weight curve, close to SF Pro's steps)
STEM = {100: 0.28, 200: 0.47, 300: 0.70, 400: 1.00, 500: 1.21, 600: 1.37, 700: 1.56, 800: 1.84, 900: 2.16}
WEIGHTS = [100, 400, 700, 900]          # masters on the weight axis
WIDTHS = [75, 100, 125]                 # masters on the width axis (per cent)
CHARS = ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
         " .,:;!?'\"-–—()[]{}/&@#%*+=<>$€£¥_|~^`"
         "ÀÁÂÄÅÆÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØÙÚÛÜÝàáâäåæçèéêëìíîïñòóôõöøùúûüýÿßŒœĀāĒēŌōŪūƠơƯưẠạẤấệỆộỘờỜữỮ")


def t_for(stem_ratio, sR, sB):
    # position on the Regular(0) -> Bold(1) line that gives this stem
    return (stem_ratio * sR - sR) / (sB - sR)


def glyph_points(ufo, name):
    rec = DecomposingRecordingPen(ufo)
    ufo[name].draw(rec)
    return rec.value


def blend(vr, vb, tx, ty, sx):
    out = []
    for (op, a), (op2, b) in zip(vr, vb):
        assert op == op2
        pts = []
        for p, q in zip(a, b):
            x = p[0] + tx * (q[0] - p[0])
            y = p[1] + ty * (q[1] - p[1])
            pts.append((x * sx, y))
        out.append((op, tuple(pts)))
    return out


def stem_of(ufo):
    import pathops
    p = pathops.Path(); ufo["n"].draw(p.getPen())
    nb = ufo["n"].getBounds(ufo); mid = (nb[0] + nb[2]) / 2
    r = pathops.Path(); pen = r.getPen()
    pen.moveTo((-2000, 250)); pen.lineTo((mid, 250)); pen.lineTo((mid, 252)); pen.lineTo((-2000, 252)); pen.closePath()
    b = pathops.op(p, r, pathops.PathOp.INTERSECTION).bounds
    return b[2] - b[0]


def build_family(fam: str, italic: bool):
    st = "Italic" if italic else ""
    R = ufoLib2.Font.open(SRC / f"Admiralty{fam}-{'Italic' if italic else 'Regular'}.ufo")
    B = ufoLib2.Font.open(SRC / f"Admiralty{fam}-Bold{st}.ufo")
    sR, sB = stem_of(R), stem_of(B)
    cmap = {}
    for g in R:
        for u in g.unicodes:
            cmap[u] = g.name
    names = [".notdef"] + sorted({cmap[ord(c)] for c in CHARS if ord(c) in cmap and cmap[ord(c)] in B})
    names = [n for n in names if n in R]
    ds = DesignSpaceDocument()
    for tag, nm, lo, de, hi in (("wght", "Weight", 100, 400, 900), ("wdth", "Width", 75, 100, 125)):
        a = AxisDescriptor(); a.tag, a.name, a.minimum, a.default, a.maximum = tag, nm, lo, de, hi
        ds.addAxis(a)
    rec_r = {n: glyph_points(R, n) for n in names}
    rec_b = {n: glyph_points(B, n) for n in names}
    for w in WEIGHTS:
        for wd in WIDTHS:
            s = wd / 100.0
            ty = t_for(STEM[w], sR, sB)
            # vertical stems after scaling: a little thinner when narrow, a little heavier when wide,
            # so the colour of the text stays even across widths (s ** 0.35)
            tx = t_for(STEM[w] * s ** 0.35 / s, sR, sB)
            u = ufoLib2.Font()
            u.info.familyName = f"Admiralty {fam} Proto"
            u.info.styleName = f"w{w} d{wd}"
            u.info.unitsPerEm = 1000
            u.info.ascender, u.info.descender = R.info.ascender, R.info.descender
            u.info.xHeight, u.info.capHeight = R.info.xHeight, R.info.capHeight
            u.info.italicAngle = R.info.italicAngle
            for n in names:
                g = u.newGlyph(n)
                adv_r, adv_b = R[n].width, B[n].width
                g.width = round((adv_r + tx * (adv_b - adv_r)) * s)
                if n in R and R[n].unicodes:
                    g.unicodes = list(R[n].unicodes)
                pen = g.getPen()
                for op, pts in blend(rec_r[n], rec_b[n], tx, ty, s):
                    getattr(pen, op)(*pts)
            path = OUT / f"{fam}{st}-w{w}-d{wd}.ufo"
            u.save(path, overwrite=True)
            src = SourceDescriptor(); src.path = str(path); src.font = u; src.location = {"Weight": w, "Width": wd}
            ds.addSource(src)
    ds_path = OUT / f"{fam}{st}.designspace"
    ds.write(ds_path)
    vf = ufo2ft.compileVariableTTF(ds, optimizeGvar=True)
    out = OUT / f"AdmiraltyProto{fam}{st}.ttf"
    vf.save(out)
    print(fam, st, "stems R/B", round(sR), round(sB), "glyphs", len(names), "->", out.name)


for fam in ("Sans", "Serif", "Mono"):
    build_family(fam, False)
build_family("Sans", True)
build_family("Serif", True)
