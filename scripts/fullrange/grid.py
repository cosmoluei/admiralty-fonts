import sys, cairosvg
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.varLib.instancer import instantiateVariableFont
txt=sys.argv[3]; d=float(sys.argv[4]); sc=float(sys.argv[5]) if len(sys.argv)>5 else 0.07
svg=[];y=0;W=0
for w in range(100,1000,100):
    inst=instantiateVariableFont(TTFont(sys.argv[1]),{"wght":w,"wdth":d})
    gs=inst.getGlyphSet(); cmap=inst.getBestCmap(); x=10
    for ch in txt:
        g=cmap[ord(ch)]; pen=SVGPathPen(gs)
        gs[g].draw(TransformPen(pen,(sc,0,0,-sc,x,y+760*sc)))
        svg.append(f'<path d="{pen.getCommands()}"/>'); x+=gs[g].width*sc
    W=max(W,x); y+=1000*sc
cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W+10}" height="{y}"><rect width="100%" height="100%" fill="white"/>{"".join(svg)}</svg>'.encode(),write_to=sys.argv[2])
