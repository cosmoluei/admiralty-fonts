import pathlib
SOURCES = str(pathlib.Path(__file__).resolve().parents[2] / "sources")
"""Draw today's Regular (grey) under the new 400/100 master (red outline) for each glyph."""
import sys, cairosvg, ufoLib2
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
R=ufoLib2.Font.open(sys.argv[4] if len(sys.argv) > 4 else SOURCES + '/AdmiraltySans-Regular.ufo')
N=ufoLib2.Font.open(sys.argv[1]); names=sys.argv[3]
out=[];x=20;sc=0.35
for n in names:
    for f,st in ((R,'fill="#ccc"'),(N,'fill="none" stroke="#e22" stroke-width="1.2"')):
        pen=SVGPathPen(f); f[n].draw(TransformPen(pen,(sc,0,0,-sc,x,330)))
        out.append(f'<path d="{pen.getCommands()}" {st}/>')
    x+=max(R[n].width,N[n].width)*sc+20
cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{x}" height="420"><rect width="100%" height="100%" fill="white"/>{"".join(out)}</svg>'.encode(),write_to=sys.argv[2])
