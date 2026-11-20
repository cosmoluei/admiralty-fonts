"""Continuous icon geometry in the original 24-unit construction grid."""
import math
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import pathops

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from build_symbols import get_phase1_catalog
from symbols_engine import IconCanvas, GRID_SCALE, GRID_X0, GRID_Y0, _ccw_round_rect_path, _ccw_ellipse_path

CATALOG=get_phase1_catalog()
by_name={s.name:s for s in CATALOG}
# Distance reserved for the smallest open detail of each crowded icon on the
# 24-unit grid. The four levels are optically sized from the Regular artwork.
OPTICAL_CLEARANCE = {name: level for level, group in (
    (0.25, (
        "send cut trigger background-task error archive label toggle-off eye help-center "
        "browser pause "
    )),
    (0.5, (
        "edit plan workflow skill citation home list progress badge notification-dot link share tag "
        "restore sort language password sign-in sign-out laptop watch headphones bar-chart bug "
    )),
    (0.75, (
        "image quote emoji thumbs-up thumbs-down voice-message team tabs window info timeout presentation "
        "video-file version recent advanced-search settings accessibility shield-check shield-alert "
        "incognito encryption upgrade about tips branch wallet scheduled-task timer location "
    )),
    (1.0, (
        "code-file auto-mode mic mic-off copy regenerate delete agent memory task-list reminder automation approval "
        "permission source prompt grid dashboard new-window check-circle warning help verified bell file "
        "new-folder document pdf image-file audio-file unlink export note clipboard trash history compare "
        "duplicate rename zoom-in zoom-out sort-ascending sort-descending find-in-page sliders light-mode "
        "notification-settings profile passkey consent audit-log two-factor cloud-upload cloud-download "
        "backup restore-backup auto-sync sync-paused sync-error switch-account add-account feedback "
        "support report-a-problem whats-new share-app code terminal code-block bell-filled mic-filled "
        "phone tablet devices web-search artifact translate screen-share server new-chat edit-message "
        "schedule-send keyboard usage appearance billing receipt face-id fingerprint qr-code scan "
        "calendar volume mute read-aloud subtitles line-chart "
    )),
) for name in group.split()}


def primitive_path(cmd,width,radius,junctions=()):
    kind=cmd[0]
    def xy(pt):
        return (12+(pt[0]-12)*width, pt[1])
    p=pathops.Path()
    if kind in ("line","cut_line"):
        p.moveTo(*xy(cmd[1:3]));p.lineTo(*xy(cmd[3:5]))
    elif kind in ("polyline","cut_polyline","fill_polygon","cut_polygon"):
        filled=kind.endswith("polygon")
        closed=filled or cmd[2]
        points=np.asarray([xy(z) for z in cmd[1]])
        if len(points)<2:
            return p
        if closed and np.allclose(points[0],points[-1]):
            points=points[:-1]
        previous=np.roll(points,1,axis=0)-points
        following=np.roll(points,-1,axis=0)-points
        l=np.linalg.norm(previous,axis=1)
        m=np.linalg.norm(following,axis=1)
        reach=np.minimum(np.minimum(l,m)*.40, 1.72*radius)
        # Keep the centerline intersection where another stroke joins this
        # vertex. Rounding the isolated wing used to leave the shaft sticking out.
        for i, vertex in enumerate(cmd[1][:len(reach)]):
            if tuple(vertex) in junctions:
                reach[i]=0
        if not closed:
            reach[0]=reach[-1]=0
        before=points+previous*(reach/np.maximum(l,1e-8))[:,None]
        after=points+following*(reach/np.maximum(m,1e-8))[:,None]
        p.moveTo(*before[0])
        for i,z in enumerate(points):
            if i:p.lineTo(*before[i])
            if reach[i]>.00001:p.quadTo(*z,*after[i])
        if closed:p.close()
    elif kind in ("circle","ellipse","fill_circle","cut_circle"):
        cx,cy=xy(cmd[1:3])
        rx,ry=cmd[3]*width,cmd[4] if kind=="ellipse" else cmd[3]
        _ccw_ellipse_path(p,cx,cy,rx,ry)
    elif kind in ("rect","fill_round_rect","cut_round_rect"):
        x,y=xy(cmd[1:3])
        w,h=cmd[3]*width,cmd[4]
        r=cmd[5]+radius*min(2.5,.18*min(w,h))
        _ccw_round_rect_path(p,x,y,x+w,y+h,r)
    elif kind=="cubic_stroke":
        p.moveTo(*xy(cmd[1]));p.cubicTo(*(v for pt in cmd[2:5] for v in xy(pt)))
    elif kind=="arc":
        _,cx,cy,rx,a,b,_=cmd
        cx,cy=xy((cx,cy))
        # Cubic circular arcs avoid polygonal knees on thin, expanded icons.
        stops=np.linspace(math.radians(a),math.radians(b),int(math.ceil(abs(b-a)/90))+1)
        def point(t):return complex(cx+width*rx*math.cos(t),cy+rx*math.sin(t))
        def deriv(t):return complex(-width*rx*math.sin(t),rx*math.cos(t))
        first=point(stops[0]);p.moveTo(first.real,first.imag)
        for a,b in zip(stops,stops[1:]):
            h=4/3*math.tan((b-a)/4)
            a1,b1,end=point(a)+h*deriv(a),point(b)-h*deriv(b),point(b)
            p.cubicTo(a1.real,a1.imag,b1.real,b1.imag,end.real,end.imag)
    else:raise ValueError(kind)
    return p


@lru_cache(maxsize=1000)
def recipe(name,base_stroke):
    c=IconCanvas(base_stroke)
    by_name[name].draw_fn(c)
    commands=[]
    for cmd in c.commands:
        kind=cmd[0]
        if name in ('bell','bell-filled','notification-settings') and kind=='polyline':
            pts=list(cmd[1])
            y=10.2 if name=='notification-settings' else 10.5
            pts[0]=(pts[0][0],y)
            if name!='notification-settings':
                pts[-1]=(pts[-1][0],y)
            cmd=(kind,pts,*cmd[2:])
        elif name=='tips' and kind=='polyline':
            # Tangent shoulders connect the circular bulb to its narrow neck.
            dx=5.6 / math.sqrt(2)
            y=9.2+dx
            for sign in (-1,1):
                commands.append(('cubic_stroke',(12+sign*dx,y),
                                 (12+sign*(dx-.54),y+.54),
                                 (12+sign*3,14.15),(12+sign*3,15.0),None))
            cmd=(kind,[(9,15),(9,17.5),(15,17.5),(15,15)],False,None)
        elif name=='quote' and kind=='cubic_stroke':
            (x,y),_,b,end=cmd[1:5]
            cmd=(kind,(x+.2,10.5),(x+.2,15.3),b,end,None)
        elif name=='background-task' and kind=='fill_circle':
            angle=math.radians(-42)
            cmd=(kind,12+8.6*math.cos(angle),12+8.6*math.sin(angle),cmd[3])
        elif name=='privacy-settings':
            if kind=='fill_circle':
                cmd=(kind,12,8.5,1.12)
            elif kind=='line':
                cmd=(kind,12,12.95,12,16.2,None)
        commands.append(cmd)
    return commands


@lru_cache(maxsize=1000)
def junctions(name,base_stroke):
    # A shared vertex belongs to two distinct pen paths (shaft and arrow,
    # or page outline and fold). A closed path's own endpoints count once.
    counts={}
    for cmd in recipe(name,base_stroke):
        if cmd[0] in ('line','cut_line'):
            pts=(cmd[1:3],cmd[3:5])
        elif cmd[0] in ('polyline','cut_polyline'):
            pts=cmd[1]
        else:
            continue
        for pt in set(map(tuple,pts)):
            counts[pt]=counts.get(pt,0)+1
    return frozenset(pt for pt,n in counts.items() if n>1)


@lru_cache(maxsize=8192)
def expanded_scale(name,sw,native_sw):
    # Reserve the actual pen outside the centerline. Spread the available
    # expansion over the whole width axis so that a nearly full icon never
    # hits a hard width limit halfway between two master designs.
    allowed=1.29
    for cmd in recipe(name,native_sw):
        kind=cmd[0]
        if kind.startswith("cut_"):
            continue
        small_dot=kind=="fill_circle" and cmd[3]<=2.15
        if small_dot:
            extent=abs(cmd[1]-12)
            pad=cmd[3]*(sw/native_sw)**.65
        else:
            path=primitive_path(cmd,1,0)
            x0,_,x1,_=path.bounds
            extent=max(abs(x0-12),abs(x1-12))
            if kind.startswith("fill_"):
                pad=max(0,(sw-2)*.28) if by_name[name].is_filled else 0
            else:
                override=cmd[-1]
                pad=(sw if override is None else override*sw/native_sw)/2
        if extent>.01:
            allowed=min(allowed,(11.52-pad)/extent)
    return allowed


def boolean(a,b,op):
    if not len(a):
        return pathops.Path(b) if op==pathops.PathOp.UNION else pathops.Path()
    if not len(b):
        return pathops.Path(a)
    union=op==pathops.PathOp.UNION
    x0,y0,x1,y1=a.bounds
    u0,v0,u1,v1=b.bounds
    bounds=(min(x0,u0),min(y0,v0),max(x1,u1),max(y1,v1))
    for scale,offset in [(1.,0.),(3.7,0.),(1.,.014),(15.7,-.028)]:
        try:
            aa=a.transform(scale,0,0,scale,0,0)
            bb=b.transform(scale,0,0,scale,offset*scale,0)
            if scale!=1 or offset:
                aa.simplify()
                bb.simplify()
            result=pathops.op(aa,bb,op).transform(1/scale,0,0,1/scale,0,0)
        except pathops.PathOpsError:
            continue
        if union and max(abs(u-v) for u,v in zip(result.bounds,bounds))>.15:
            continue
        return result
    raise ArithmeticError("Boolean operation lost part of a symbol")


def glyph_parts(name,w,d,r,mirror=False,*,clearance=None):
    sw=float(np.interp(w,[100,400,500,700,900],[24/36,2,2.35,2.8,3.30]))
    native_sw=float(np.clip(sw,2,2.8))
    width=1+.83*(d/100-1)
    # Crowded icons reserve white between distinct lines and inside small
    # eyes. Keep round pens and the native recipe's filled/outline decisions.
    relief = OPTICAL_CLEARANCE.get(name,0.) if clearance is None else clearance
    compression = max(0.,(100-d)/35)
    heavy = max(0.,(w-400)/500)
    width += relief*compression*(.045+.095*heavy)
    sw -= relief*(.19*compression*min(1.,max(0.,(w-100)/300))
                  +heavy*(.59+.38*compression))
    height=1.
    if d>100:
        expanded=expanded_scale(name,sw,native_sw)
        t=(d-100)/50
        width=1+(expanded-1)*t
        height=1+(min(1,expanded/1.29)-1)*t
    radius=r/100
    parts=[]
    interior=max(heavy,compression*.48*min(1.,max(0.,(w-100)/300)))
    if name in ('keyboard','devices','appearance'):
        height+=(1-height)*interior
    for cmd in recipe(name,native_sw):
        kind=cmd[0]
        if name=='timer' and kind=='line' and cmd[1:3]==(18.,6.6) and w<400:
            # The upper-right button points radially at the dial. Extend its
            # inner end into the rim as the round caps lose their overlap.
            x,y=cmd[1:3]
            reach=(1-7.6/math.hypot(x-12,y-13.6))*min(1.,(400-w)/200)
            cmd=(kind,x+(12-x)*reach,y+(13.6-y)*reach,*cmd[3:])
        if name in ('new-window','share-app','download','upload') and kind in ('line','cut_line'):
            # Bring the shaft in under the two wings. The round end of a
            # full-length shaft protrudes past the outside of the corner
            # after condensing, most clearly in the mirrored arrow.
            x,y,xx,yy=cmd[1:5]
            if (xx,yy) in junctions(name,native_sw):
                length=math.hypot((xx-x)*width,(yy-y)*height)
                inset=min(.20,.52*sw/max(length,.01))
                cmd=(kind,x,y,xx-inset*(xx-x),yy-inset*(yy-y),cmd[-1])
        if name=='new-window' and kind=='polyline' and len(cmd[1])>3:
            pts=list(cmd[1])
            pts[0]=(pts[0][0]-.75*heavy*compression,pts[0][1])
            cmd=(kind,pts,*cmd[2:])
        # Only the compact detail strokes get this extra relief. The outer
        # frame still carries the selected weight and a regular round terminal.
        detail = heavy*relief
        if name=='find-in-page' and kind=='cut_circle':
            # Clear the document behind the entire loupe including its pen
            # and an open gap at the bottom edge at every weight.
            cmd=(kind,15.5,15.5,3.6+(sw+.60)/min(width,height))
        if name in ('grid','dashboard') and kind=='rect':
            _,x,y,bw,bh,corner,pen=cmd
            # Move the four panel interiors apart while holding the frame's
            # exterior edges. Opposed borders each need their own clearance.
            gap=.52*interior
            cmd=(kind,x+(gap if x>12 else 0),y+(gap if y>12 else 0),bw-gap,bh-gap,corner,pen)
        if name=='reminder' and kind=='line' and cmd[2]<7:
            cmd=(kind,cmd[1],cmd[2]-.68*interior,cmd[3],cmd[4]-.68*interior,cmd[-1])
        if name=='code-file' and kind=='polyline' and min(y for x,y in cmd[1])>10:
            center=np.mean(cmd[1],axis=0)
            pts=center+(np.asarray(cmd[1])-center)*(1-.18*interior)
            cmd=(kind,[tuple(p) for p in pts],False,cmd[-1])
        if name=='audio-file' and kind=='line':
            _,x,y,xx,yy,pen=cmd
            cmd=(kind,x,y+.54*interior,xx,yy-.45*interior,pen)
        if name == 'light-mode' and kind == 'line':
            a=np.array(cmd[1:3])
            b=np.array(cmd[3:5])
            a+=.6*detail*(b-a)/np.linalg.norm(b-a)
            cmd=(kind,*a,*b,cmd[-1])
        filled=kind.startswith("fill_") or kind in ("cut_round_rect","cut_circle","cut_polygon")
        cutting=kind.startswith("cut_")
        if kind in ("fill_circle","cut_circle") and cmd[3]<=2.15:
            # A status dot stays round as the rest of the drawing widens.
            cmd=(*cmd[:3],cmd[3]*(sw/native_sw)**(.65 if not cutting else .16))
            if not cutting and name in ("keyboard","appearance","audit-log","contacts","calendar"):
                cmd=(*cmd[:3],cmd[3]*(1-.15*detail))
            if name=='keyboard':
                cmd=(*cmd[:3],cmd[3]*(1-.12*interior))
            cx,cy=12+(cmd[1]-12)*width,12+(cmd[2]-12)*height
            p=pathops.Path()
            _ccw_ellipse_path(p,cx,cy,cmd[3],cmd[3])
        else:
            p=primitive_path(cmd,width,radius,junctions(name,native_sw))
            if height!=1:
                p=p.transform(1,0,0,height,0,12*(1-height))
        # Stroke and combine in the same 1000-UPM coordinates as the font.
        # On the 24-unit grid a valid union can silently discard a long arc
        # merging with a nearby cap, even when PathOps returns successfully.
        p=p.transform(GRID_SCALE,0,0,GRID_SCALE,0,0)
        if not filled:
            override=cmd[-1]
            ink=sw if override is None else override*sw/native_sw
            if not cutting and kind=='line':
                length=math.hypot(cmd[3]-cmd[1],cmd[4]-cmd[2])
                ink*=1-.18*detail*max(0,min(1,(10-length)/4))
            elif kind=='polyline' and not cmd[2] and len(cmd[1])<=3:
                ink*=1-.12*detail
            if name in ('code-file','audio-file') and (
                    kind=='line' or kind=='polyline' and min(y for x,y in cmd[1])>10):
                ink*=1-.18*interior
            if cutting and override is not None:
                ink=max(sw+.80,override+sw-native_sw)
            p.stroke(ink*GRID_SCALE,pathops.LineCap.ROUND_CAP,pathops.LineJoin.ROUND_JOIN,3)
            p.convertConicsToQuads(.002*GRID_SCALE)
        elif by_name[name].is_filled and not cutting and w!=400:
            # Filled-state icons remain a solid silhouette. Its weight gain
            # is calibrated independently from a neighbouring outline icon.
            amount=(sw-2)*.28*GRID_SCALE
            border=pathops.Path(p)
            border.stroke(abs(amount)*2,pathops.LineCap.ROUND_CAP,pathops.LineJoin.ROUND_JOIN,3)
            border.convertConicsToQuads(.002*GRID_SCALE)
            p=boolean(p,border,pathops.PathOp.UNION if amount>0 else pathops.PathOp.DIFFERENCE)
        p.simplify(clockwise=True)
        if cutting:
            # Subtraction distributes over the positive paint groups. A
            # badge cut out of a frame must not merge that frame's identity
            # with the unrelated text lines or clock hands underneath it.
            a,b,c,d=p.bounds
            for i,part in enumerate(parts):
                if not len(part):
                    continue
                x,y,z,t=part.bounds
                if a>z or b>t or c<x or d<y:
                    continue
                clipped=boolean(part,p,pathops.PathOp.DIFFERENCE)
                clipped.simplify(clockwise=True)
                parts[i]=clipped
        else:
            parts.append(p)
    transformed=[p.transform(1,0,0,-1,GRID_X0,GRID_Y0) for p in parts]
    for p in transformed:
        p.reverse()
    return [p.transform(-1,0,0,1,840,0) for p in transformed] if mirror else transformed


def glyph_path(name,w,d,r,mirror=False):
    # Each paint group has normalized winding, including its holes. Their
    # summed non-zero fill is the union. Another boolean pass on coincident
    # boundaries can discard a lobe even when its bounds remain unchanged.
    out=pathops.Path()
    for part in glyph_parts(name,w,d,r,mirror):
        out.addPath(part)
    return out
