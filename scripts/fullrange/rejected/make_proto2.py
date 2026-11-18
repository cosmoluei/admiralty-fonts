"""Prototype round 2: weights 100-900, widths 65-150, keeping Admiralty's shapes.

Thin (100) is Regular's own outline with its strokes made thinner (every point moved inward
along the outline's normal); Black (900) is Bold's outline made thicker the same way. Because
no shape is extrapolated, the letters keep their proportions and details. Widths scale the
outlines horizontally and correct the vertical stems by a horizontal-only offset first.
All masters come from the same points, so they stay compatible for the variable font.
"""
import sys, math
from pathlib import Path
import ufoLib2, pathops
from fontTools.pens.recordingPen import DecomposingRecordingPointPen
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor
import ufo2ft
sys.path.insert(0, str(Path(__file__).resolve().parent))
import seg_offset

SRC = Path(__file__).resolve().parents[3] / "sources"
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)

STEM = {100: 0.28, 200: 0.47, 300: 0.70, 400: 1.00, 500: 1.21, 600: 1.37, 700: 1.56, 800: 1.84, 900: 2.16}
WIDTHS = [65, 100, 150]
THIN_ADV, BLACK_ADV = -30, 40          # same for Sans and Serif, so their widths stay equal
CHARS = ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
         " .,:;!?'\"-–—()[]{}/&@#%*+=<>$€£¥_|~^`"
         "ÀÁÂÄÅÆÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØÙÚÛÜÝàáâäåæçèéêëìíîïñòóôõöøùúûüýÿßŒœĀāĒēŌōŪūƠơƯưẠạẤấệỆộỘờỜữỮ")


def measure(ufo):
    def cut(g, box):
        p = pathops.Path(); ufo[g].draw(p.getPen())
        r = pathops.Path(); pen = r.getPen()
        x0, y0, x1, y1 = box
        pen.moveTo((x0, y0)); pen.lineTo((x1, y0)); pen.lineTo((x1, y1)); pen.lineTo((x0, y1)); pen.closePath()
        return pathops.op(p, r, pathops.PathOp.INTERSECTION).bounds
    nb = ufo["n"].getBounds(ufo)
    b = cut("n", (-2000, 250, (nb[0] + nb[2]) / 2, 252))
    hb = ufo["H"].getBounds(ufo); cx = (hb[0] + hb[2]) / 2
    h = cut("H", (cx - 1, -2000, cx + 1, 4000))
    return b[2] - b[0], h[3] - h[1]


def contours_of(ufo, name):
    rec = DecomposingRecordingPointPen(ufo)
    ufo[name].drawPoints(rec)
    cs, cur = [], None
    for op, args, kw in rec.value:
        if op == "beginPath":
            cur = []
        elif op == "addPoint":
            pt, seg = args[0], (args[1] if len(args) > 1 else kw.get("segmentType"))
            cur.append([pt[0], pt[1], seg])
        elif op == "endPath":
            cs.append(cur)
    return cs


def _flatten(cs, steps=8):
    """Line segments of the outline (for measuring stroke thickness)."""
    segs = []
    for c in cs:
        n = len(c)
        on = [k for k in range(n) if c[k][2] is not None]
        if not on:
            continue
        start = on[0]
        k = start
        while True:
            # collect off-curves up to the next on-curve
            offs, j = [], (k + 1) % n
            while c[j][2] is None:
                offs.append(c[j]); j = (j + 1) % n
            p0, p1 = c[k], c[j]
            if len(offs) == 2:
                pts = []
                for t in range(1, steps + 1):
                    u = t / steps; m = 1 - u
                    pts.append((m**3*p0[0] + 3*m*m*u*offs[0][0] + 3*m*u*u*offs[1][0] + u**3*p1[0],
                                m**3*p0[1] + 3*m*m*u*offs[0][1] + 3*m*u*u*offs[1][1] + u**3*p1[1]))
            elif len(offs) == 1:
                pts = [((1-t/steps)**2*p0[0] + 2*(1-t/steps)*(t/steps)*offs[0][0] + (t/steps)**2*p1[0],
                        (1-t/steps)**2*p0[1] + 2*(1-t/steps)*(t/steps)*offs[0][1] + (t/steps)**2*p1[1]) for t in range(1, steps+1)]
            else:
                pts = [(p1[0], p1[1])]
            prev = (p0[0], p0[1])
            for q in pts:
                segs.append((prev[0], prev[1], q[0], q[1])); prev = q
            k = j
            if k == start:
                break
    return segs


def _ray(px, py, dx, dy, segs, skip=1.0):
    best = None
    for x0, y0, x1, y1 in segs:
        ex, ey = x1 - x0, y1 - y0
        den = dx * ey - dy * ex
        if abs(den) < 1e-9:
            continue
        t = ((x0 - px) * ey - (y0 - py) * ex) / den
        u = ((x0 - px) * dy - (y0 - py) * dx) / den
        if t > skip and -1e-6 <= u <= 1 + 1e-6 and (best is None or t < best):
            best = t
    return best


def offset(cs, fx, fy, cap):
    """Make every stroke fx times as thick horizontally and fy times vertically, in proportion to
    its own thickness (thin strokes change less), by moving each point along its normal.
    Handles move with their on-curve point, so the point structure never changes."""
    segs = _flatten(cs)
    out = []
    for c in cs:
        n = len(c)
        on = [i for i in range(n) if c[i][2] is not None]
        if len(on) < 2:
            out.append([p[:] for p in c]); continue
        disp = [None] * n
        for i in on:
            p = c[i]
            def direction(step):
                j = i
                for _ in range(n):
                    j = (j + step) % n
                    vx, vy = c[j][0] - p[0], c[j][1] - p[1]
                    L = math.hypot(vx, vy)
                    if L > 0.5:
                        return vx / L, vy / L
                return 0.0, 0.0
            ox, oy = direction(1)
            ix, iy = direction(-1)
            ix, iy = -ix, -iy
            tx, ty = ix + ox, iy + oy
            L = math.hypot(tx, ty)
            if L < 1e-6:
                tx, ty = ox, oy; L = 1.0
            tx, ty = tx / L, ty / L
            nx, ny = ty, -tx                      # outward (away from the ink)
            T = _ray(p[0], p[1], -nx, -ny, segs)  # thickness of the stroke under this point
            T = cap if T is None else min(T, cap)
            disp[i] = ((fx - 1) / 2 * T * nx, (fy - 1) / 2 * T * ny)
        for i in range(n):
            if disp[i] is not None:
                continue
            a = i
            while disp[a] is None:
                a = (a - 1) % n
            b = i
            while disp[b] is None:
                b = (b + 1) % n
            da = (i - a) % n; db = (b - i) % n
            if da < db:
                disp[i] = disp[a]
            elif db < da:
                disp[i] = disp[b]
            else:
                disp[i] = ((disp[a][0] + disp[b][0]) / 2, (disp[a][1] + disp[b][1]) / 2)
        out.append([[p[0] + d[0], p[1] + d[1], p[2]] for p, d in zip(c, disp)])
    return out


def build_family(fam, italic):
    st = "Italic" if italic else ""
    R = ufoLib2.Font.open(SRC / f"Admiralty{fam}-{'Italic' if italic else 'Regular'}.ufo")
    B = ufoLib2.Font.open(SRC / f"Admiralty{fam}-Bold{st}.ufo")
    mono = fam == "Mono"
    sR, hR = measure(R); sB, hB = measure(B)
    k_heavy = (sB / sR - 1) / 0.56          # Mono's bold is lighter than Sans's: scale the heavy side
    def stem_target(w):
        f = STEM[w]
        if f > 1:
            f = 1 + (f - 1) * k_heavy
        return sR * f
    def bar_target(w):
        f = STEM[w]
        f = f if f <= 1 else 1 + (f - 1) * 0.8 * k_heavy     # horizontals grow a little less
        return hR * f
    cmap = {u: g.name for g in R for u in g.unicodes}
    names = [".notdef"] + sorted({cmap[ord(ch)] for ch in CHARS if ord(ch) in cmap})
    names = [n for n in names if n in R and n in B]
    cR = {n: contours_of(R, n) for n in names}
    cB = {n: contours_of(B, n) for n in names}
    # the four weight masters at 100% width: (contours, advance)
    base = {}
    def top(g): return R[g].getBounds(R)[3]
    def bot(g): return R[g].getBounds(R)[1]
    zones = sorted({0, R.info.xHeight, R.info.capHeight, round(top("l")), round(bot("p")), round(top("one"))})
    print("  alignment heights", zones)
    fT = stem_target(100) / sR                      # Thin from Regular
    fK = stem_target(900) / sB                      # Black from Bold
    fKy = 1 + (fK - 1) * 0.8                        # horizontals grow a little less
    for n in names:
        aR, aB = R[n].width, B[n].width
        if mono:
            aT, aK = aR, aB
        else:
            aT, aK = aR + THIN_ADV, aB + BLACK_ADV
        thin = seg_offset.offset(cR[n], fT, fT, sR, zones); black = seg_offset.offset(cB[n], fK, fKy, sB, zones)
        sh_t = (aT - aR) / 2; sh_k = (aK - aB) / 2
        thin = [[[p[0] + sh_t, p[1], p[2]] for p in c] for c in thin]
        black = [[[p[0] + sh_k, p[1], p[2]] for p in c] for c in black]
        base[n] = {100: (thin, aT), 400: (cR[n], aR), 700: (cB[n], aB), 900: (black, aK)}
    stems = {100: stem_target(100), 400: sR, 700: sB, 900: stem_target(900)}
    ds = DesignSpaceDocument()
    for tag, nm, lo, de, hi in (("wght", "Weight", 100, 400, 900), ("wdth", "Width", 65, 100, 150)):
        a = AxisDescriptor(); a.tag, a.name, a.minimum, a.default, a.maximum = tag, nm, lo, de, hi
        ds.addAxis(a)
    for w in (100, 400, 700, 900):
        for wd in WIDTHS:
            s = wd / 100.0
            # stems after narrowing: thinner when narrow, heavier when wide, for even colour
            want = stems[w] * s ** 0.35
            gx = (want / s) / stems[w]                    # horizontal thickening before scaling
            ddx = (want / s - stems[w]) / 2               # what that adds to each side of a stem
            u = ufoLib2.Font()
            u.info.familyName = f"Admiralty {fam} Proto"; u.info.styleName = f"w{w} d{wd}"
            u.info.unitsPerEm = 1000
            for attr in ("ascender", "descender", "xHeight", "capHeight", "italicAngle"):
                setattr(u.info, attr, getattr(R.info, attr))
            for n in names:
                cs, adv = base[n][w]
                cs2 = seg_offset.offset(cs, gx, 1.0, stems[w], zones) if abs(gx - 1) > 1e-6 else cs
                g = u.newGlyph(n)
                g.width = round((adv + 2 * ddx) * s) if not mono else round(600 * s)
                sh = 0 if not mono else (600 * s - (adv + 2 * ddx) * s) / 2 / s
                if R[n].unicodes:
                    g.unicodes = list(R[n].unicodes)
                pen = g.getPointPen()
                for c in cs2:
                    pen.beginPath()
                    for x, y, seg in c:
                        pen.addPoint(((x + ddx + sh) * s, y), segmentType=seg)
                    pen.endPath()
            path = OUT / f"{fam}{st}-w{w}-d{wd}.ufo"
            u.save(path, overwrite=True)
            src = SourceDescriptor(); src.path = str(path); src.font = u
            src.location = {"Weight": w, "Width": wd}
            ds.addSource(src)
    ds.write(OUT / f"{fam}{st}.designspace")
    vf = ufo2ft.compileVariableTTF(ds, optimizeGvar=True)
    vf.save(OUT / f"AdmiraltyProto{fam}{st}.ttf")
    print(fam, st, "stems", {w: round(v) for w, v in stems.items()}, "glyphs", len(names))


for fam, it in (("Sans", False), ("Serif", False), ("Mono", False), ("Sans", True), ("Serif", True)):
    build_family(fam, it)
