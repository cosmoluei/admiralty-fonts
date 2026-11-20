"""Matched pen widths for the Latin diagonal capitals and open four."""
import math

import numpy as np
import pathops
from fontTools.pens.transformPen import TransformPen

from compatible import OutlinePen, ordered_contours
from accent_masters import as_path, tracks_for


DIAGONALS = {"A","M","N","V","W","X","Y","four","four.tnum"}
SLASHED_ZEROS={"zero.slash","zero.tnum.slash"}


def y_tracks(design,cells):
    # Preserve the ten named corners, including the small flat at the
    # crotch. A boolean union of three sticks can swap left and right arms
    # between masters even when the two end drawings are individually sound.
    glyph=design.regular['glyf']['Y']
    raw=np.asarray(glyph.coordinates)
    regular=raw[:,0]-design.slant*raw[:,1]+1j*raw[:,1]
    out=[]
    for w,d in cells:
        sx,dx=design.transform('Y',w,d)
        if (w,d)==(400,100):
            z=regular
        else:
            left,right=regular.real.min()*sx+dx,regular.real.max()*sx+dx
            mid=(left+right)/2
            t={100:24,400:92,900:129}[w]
            h=700
            shoulder=300
            slope=(mid-t/2-left)/(h-shoulder)
            arm=t*math.hypot(1,slope)
            floor=shoulder+(arm-.5*t)/max(slope,.1)
            small=min(.085*t,5)
            z=np.array([mid+t/2,mid-t/2,mid-t/2+1j*shoulder,left+1j*h,
                        left+arm+1j*h,mid-small+1j*floor,mid+small+1j*floor,
                        right-arm+1j*h,right+1j*h,mid+t/2+1j*shoulder])
        for radius in (0,{100:9,400:30,900:49}[w]):
            back,forward=np.roll(z,1)-z,np.roll(z,-1)-z
            angle=np.arccos(np.clip((back.conj()*forward).real/abs(back*forward),-1,1))
            trim=np.minimum(radius/np.tan(angle/2),.40*np.minimum(abs(back),abs(forward)))
            before=z+trim*back/abs(back)
            after=z+trim*forward/abs(forward)
            pts=np.column_stack([before,z,after,(after+np.roll(before,-1))/2]).ravel()
            out.append(pts+design.slant*pts.imag)
    return out,[len(out[0])-1]


def slashed_zero_tracks(design,name,cells):
    gs=design.regular.getGlyphSet()
    upright=(1,0,-design.slant,1,0,0)
    original=as_path(gs,name,upright)
    rings=sorted(as_path(gs,'zero',upright).contours,key=lambda p:abs(p.area),reverse=True)
    outer,inner=rings[:2]
    ax,ay,bx,by=outer.bounds
    ix,iy,jx,jy=inner.bounds
    cx,cy=(ax+bx)/2,(ay+by)/2
    native_stem=((ix-ax)+(bx-jx))/2
    native_bar=((iy-ay)+(by-jy))/2
    base_cx=(original.bounds[0]+original.bounds[2])/2
    ref=OutlinePen(None)
    original.draw(ref)
    shapes=[]
    for w,d in cells:
        sx,dx=design.transform(name,w,d)
        if (w,d)==(400,100):
            shape=original
        else:
            stem={100:24,400:native_stem,900:native_stem+37}[w]
            bar={100:24,400:native_bar,900:native_bar+28}[w]
            center=base_cx*sx+dx
            outer_scaled=outer.transform(sx,0,0,1,center-sx*cx,0)
            inner_x=max(42,(bx-ax)*sx-2*stem)/(jx-ix)
            inner_y=(by-ay-2*bar)/(jy-iy)
            inner_scaled=inner.transform(inner_x,0,0,inner_y,center-inner_x*(ix+jx)/2,cy-inner_y*(iy+jy)/2)
            thickness={100:24,400:58,900:86}[w]
            direction=complex(.55*sx,1)
            normal=1j*direction/abs(direction)
            diag=pathops.Path()
            pen=diag.getPen()
            pts=[complex(center,cy)+direction*dy+normal*t*thickness/2 for dy,t in [(-700,-1),(700,-1),(700,1),(-700,1)]]
            pen.moveTo((pts[0].real,pts[0].imag))
            for z in pts[1:]:
                pen.lineTo((z.real,z.imag))
            pen.closePath()
            holes=pathops.op(inner_scaled,diag,pathops.PathOp.DIFFERENCE)
            shape=pathops.op(outer_scaled,holes,pathops.PathOp.DIFFERENCE)
        p=OutlinePen(None)
        shape.draw(p)
        shapes.append(ordered_contours(ref.contours,p.contours))
    points,ends=tracks_for(ref.contours,shapes,cells,{100:5,400:15,900:25})
    return [z+design.slant*z.imag for z in points],ends


def pen_drawing(name, left, right, t):
    h = 690 if name.startswith("four") else 700
    path=pathops.Path()
    def x(f): return left+(right-left)*f
    def polygon(points):
        nonlocal path
        shape=pathops.Path()
        p=shape.getPen()
        p.moveTo(points[0])
        for z in points[1:]: p.lineTo(z)
        p.closePath()
        path = pathops.op(path,shape,pathops.PathOp.UNION)
    def diagonal(x0,y0,x1,y1):
        half=t/2*math.hypot(x1-x0,y1-y0)/abs(y1-y0)
        polygon([(x0-half,y0),(x1-half,y1),(x1+half,y1),(x0+half,y0)])
    def band(x0,x1,y,thickness):
        polygon([(x0,y-thickness/2),(x1,y-thickness/2),(x1,y+thickness/2),(x0,y+thickness/2)])
    mid=x(.5)
    if name=="A":
        diagonal(left,0,mid,h)
        diagonal(right,0,mid,h)
        bar=230
        band(left+(mid-left)*bar/h,right+(mid-right)*bar/h,bar,t)
    elif name=="M":
        diagonal(left,0,left,h)
        diagonal(left,h,mid,0)
        diagonal(mid,0,right,h)
        diagonal(right,0,right,h)
    elif name=="N":
        diagonal(left,0,left,h)
        diagonal(left,h,right,0)
        diagonal(right,0,right,h)
    elif name=="V":
        diagonal(left,h,mid,0)
        diagonal(mid,0,right,h)
    elif name=="W":
        a,b=x(.223),x(.777)
        diagonal(left,h,a,0); diagonal(a,0,mid,680)
        diagonal(mid,680,b,0); diagonal(b,0,right,h)
    elif name=="X":
        diagonal(left,h,right,0); diagonal(left,0,right,h)
    elif name=="Y":
        diagonal(left,h,mid,313); diagonal(right,h,mid,313)
        diagonal(mid,0,mid,313+t/2)
    else:
        upright=x(.74)
        cross=210
        stem_l,stem_r=upright-t/2,upright+t/2
        L,R=left-t/2,right+t/2
        y0,y1=cross-t/2,cross+t/2
        rise_y=cross+.30*t
        cap_l=stem_l-.13*t
        slope=(cap_l-L)/(h-rise_y)
        flank=t*math.hypot(1,slope)
        def inside(y):
            return L+(y-rise_y)*slope+flank
        y_peak=rise_y+(stem_l-.04*t-L-flank)/slope
        polygon([(stem_l,0),(stem_l,y0),(L,y0),(L,rise_y),(cap_l,h),
                 (stem_r,h),(stem_r,y1),(R,y1),(R,y0),(stem_r,y0),(stem_r,0)])
        outside=path
        path=pathops.Path()
        polygon([(inside(y_peak),y_peak),(inside(y1),y1),(stem_l,y1),(stem_l,y_peak)])
        path=pathops.op(outside,path,pathops.PathOp.DIFFERENCE)
    path.simplify(clockwise=True)
    return path


def capital_tracks(design,name,cells):
    if name=='Y':
        return y_tracks(design,cells)
    base=design.regular["glyf"][name]
    gs=design.regular.getGlyphSet()
    ref=OutlinePen(gs)
    gs[name].draw(TransformPen(ref,(1,0,-design.slant,1,0,0)))
    shapes=[]
    for w,d in cells:
        sx,dx=design.transform(name,w,d)
        pen=OutlinePen(None)
        if w==400 and d==100:
            gs[name].draw(TransformPen(pen,(1,0,-design.slant,1,0,0)))
        else:
            coords=np.asarray(base.coordinates,dtype=float)
            native_x=coords[:,0]-coords[:,1]*design.slant
            t={100:24,400:88,900:129}[w]
            left=native_x.min()*sx+dx+t/2
            right=native_x.max()*sx+dx-t/2
            pen_drawing(name,left,right,t).draw(pen)
        shapes.append(ordered_contours(ref.contours,pen.contours))
    points,ends=tracks_for(ref.contours,shapes,cells,{100:9,400:30,900:49})
    return [z+design.slant*z.imag for z in points],ends
