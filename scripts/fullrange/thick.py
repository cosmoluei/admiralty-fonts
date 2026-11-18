import sys, math
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.basePen import BasePen
class Flat(BasePen):
    def __init__(s,gs): super().__init__(gs); s.segs=[]; s.cur=None
    def _moveTo(s,p): s.cur=s.start=p
    def _lineTo(s,p): s.segs.append((s.cur,p)); s.cur=p
    def _curveToOne(s,a,b,c):
        p0=s.cur
        for i in range(1,25):
            u=i/24; m=1-u
            q=tuple(m**3*p0[k]+3*m*m*u*a[k]+3*m*u*u*b[k]+u**3*c[k] for k in (0,1))
            s.segs.append((s.cur,q)); s.cur=q
    def _qCurveToOne(s,a,b):
        p0=s.cur
        for i in range(1,17):
            u=i/16; m=1-u
            q=tuple(m*m*p0[k]+2*m*u*a[k]+u*u*b[k] for k in (0,1))
            s.segs.append((s.cur,q)); s.cur=q
    def _closePath(s):
        if s.cur!=s.start: s.segs.append((s.cur,s.start))
def ray(px,py,dx,dy,segs):
    best=None
    for (x0,y0),(x1,y1) in segs:
        ex,ey=x1-x0,y1-y0; den=dx*ey-dy*ex
        if abs(den)<1e-9: continue
        t=((x0-px)*ey-(y0-py)*ex)/den; u=((x0-px)*dy-(y0-py)*dx)/den
        if t>0.5 and -1e-6<=u<=1+1e-6 and (best is None or t<best): best=t
    return best
w,d=float(sys.argv[2]),float(sys.argv[3])
f=instantiateVariableFont(TTFont(sys.argv[1]),{"wght":w,"wdth":d})
gs=f.getGlyphSet()
for ch in sys.argv[4]:
    fp=Flat(gs); gs[ch].draw(fp)
    vals=[]
    for (x0,y0),(x1,y1) in fp.segs:
        L=math.hypot(x1-x0,y1-y0)
        if L<1e-6: continue
        mx,my=(x0+x1)/2,(y0+y1)/2; tx,ty=(x1-x0)/L,(y1-y0)/L
        # TrueType outlines run clockwise: ink is on the right
        nx,ny=ty,-tx
        t=ray(mx,my,nx,ny,fp.segs)
        if t is not None and t<60: vals.append((t,round(mx),round(my)))
    vals.sort()
    print(ch, "min %.1f at %s  p10 %.1f  median %.1f  max(<60) %.1f"%(vals[0][0],vals[0][1:],vals[len(vals)//10][0],vals[len(vals)//2][0],vals[-1][0]))
