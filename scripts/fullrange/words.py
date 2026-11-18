import sys, cairosvg
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.varLib.instancer import instantiateVariableFont
svg=[];y=0;W=0
for w,d in [tuple(map(float,a.split("/"))) for a in sys.argv[3].split(",")]:
    inst=instantiateVariableFont(TTFont(sys.argv[1]),{"wght":w,"wdth":d})
    gs=inst.getGlyphSet(); cmap=inst.getBestCmap(); x=10
    for ch in (sys.argv[4] if len(sys.argv) > 4 else "minimum moon roll hill"):
        g=cmap.get(ord(ch),"space") if ch!=" " else cmap[32]; pen=SVGPathPen(gs)
        gs[g].draw(TransformPen(pen,(0.16,0,0,-0.16,x,y+130)))
        svg.append(f'<path d="{pen.getCommands()}"/>'); x+=gs[g].width*0.16
    W=max(W,x); y+=150
cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W+10}" height="{y}"><rect width="100%" height="100%" fill="white"/>{"".join(svg)}</svg>'.encode(),write_to=sys.argv[2])
