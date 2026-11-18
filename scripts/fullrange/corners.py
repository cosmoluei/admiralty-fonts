import sys, cairosvg
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.varLib.instancer import instantiateVariableFont
svg=[];y=0;W=0
for w,d in ((100,65),(100,150),(900,65),(900,150)):
    inst=instantiateVariableFont(TTFont(sys.argv[1]),{"wght":w,"wdth":d})
    gs=inst.getGlyphSet(); cmap=inst.getBestCmap(); x=10
    for ch in (sys.argv[3] if len(sys.argv) > 3 else "nhmurlio"):
        g=cmap[ord(ch)]; pen=SVGPathPen(gs)
        gs[g].draw(TransformPen(pen,(0.2,0,0,-0.2,x,y+170)))
        svg.append(f'<path d="{pen.getCommands()}"/>'); x+=gs[g].width*0.2+12
    W=max(W,x); y+=200
cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{y}"><rect width="100%" height="100%" fill="white"/>{"".join(svg)}</svg>'.encode(),write_to=sys.argv[2])
