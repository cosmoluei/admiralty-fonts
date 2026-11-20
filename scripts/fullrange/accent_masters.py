"""Compact diacritic masters, in the base font's attachment coordinate system."""
import numpy as np
import pathops
from fontTools.pens.transformPen import TransformPen

from compatible import Contour, OutlinePen, Profile, compatible_points, ordered_contours

NAMES = {
    "grave","acute","circumflex","tilde","macron","breve","dotaccent","dieresis","ringabove",
    "hungarumlaut","caron","commaaccent","cedilla","ogonek","dotbelow","hookabove","horn","ring"
}


def accent_name(name):
    name = name.split(".")[0].removesuffix("comb")
    return name if name in NAMES else None


def as_path(gs,name,transform):
    p = pathops.Path()
    gs[name].draw(TransformPen(p.getPen(), transform))
    return p


def designed_accent(kind, box, w, sx, dx, slant, alt):
    x0,y0,x1,y1 = box
    cx = ((x0+x1)/2)*sx+dx
    rx = (x1-x0)*sx/2
    height = y1-y0
    # The top and bottom of stacked accents remain inside their allocated band.
    width = min(24 if w==100 else 79, height*.68, rx*.94)
    if kind in ("hookabove","cedilla"):
        width = min(width,.235*height,.47*rx)
    result = pathops.Path()

    def polygon(vertices):
        pen = result.getPen()
        pen.moveTo(vertices[0])
        for pt in vertices[1:]:
            pen.lineTo(pt)
        pen.closePath()

    def oval(x,y,rx,ry):
        pen = result.getPen()
        k = .55228475
        pen.moveTo((x+rx,y))
        pen.curveTo((x+rx,y+k*ry),(x+k*rx,y+ry),(x,y+ry))
        pen.curveTo((x-k*rx,y+ry),(x-rx,y+k*ry),(x-rx,y))
        pen.curveTo((x-rx,y-k*ry),(x-k*rx,y-ry),(x,y-ry))
        pen.curveTo((x+k*rx,y-ry),(x+rx,y-k*ry),(x+rx,y))
        pen.closePath()

    if kind in ("grave","acute","hungarumlaut"):
        copies = 2 if kind=="hungarumlaut" else 1
        each = rx if copies==2 else 2*rx
        for i in range(copies):
            x = cx+((i+.5)/copies-.5)*2*rx
            h = min(width*1.13,each*.58)
            slope = max(each*.18,each-h-8)*(1 if kind!="grave" else -1)
            polygon([(x-slope/2-h/2,y0),(x-slope/2+h/2,y0),
                     (x+slope/2+h/2,y1),(x+slope/2-h/2,y1)])
    elif kind=="macron":
        y = (y0+y1)/2
        width = min(24 if w==100 else 84,height*1.15)
        polygon([(cx-rx,y-width/2),(cx+rx,y-width/2),(cx+rx,y+width/2),(cx-rx,y+width/2)])
    elif kind in ("dotaccent","dotbelow","dieresis"):
        # A detached accent needs enough integrated ink to survive between
        # pixels. Keep it slightly smaller than the 40-unit Thin period.
        rr = min((38 if w==100 else min(112,height*1.15))*.5,rx)
        xs = [cx] if kind!="dieresis" else [cx-rx+.5*height*sx,cx+rx-.5*height*sx]
        for x in xs:
            oval(x,(y0+y1)/2,rr,rr)
    elif kind in ("ringabove","ring"):
        ry = height/2
        rr = min(.5*width,rx*.50,ry*.50)
        outer = result
        oval(cx,y0+ry,rx,ry)
        result = pathops.Path()
        oval(cx,y0+ry,max(rx-2*rr,rx*.32),max(ry-2*rr,ry*.32))
        result = pathops.op(outer,result,pathops.PathOp.DIFFERENCE)
    else:
        # Open paths keep a single physical stroke through each hook or wave.
        round_cap = kind in ("hookabove","horn","commaaccent") or alt
        half = width/2
        ax,ay = max(2*rx-width,3),max(height-width,3)
        def point(x,y):
            return cx+(x-.5)*ax,y0+half+y*ay
        def move(x,y): result.moveTo(*point(x,y))
        def line(x,y): result.lineTo(*point(x,y))
        def curve(*pts): result.cubicTo(*(v for i in (0,2,4) for v in point(*pts[i:i+2])))
        if alt or kind=="commaaccent":
            move(.66,1);curve(.97,.74,.80,.30,.13,0)
        elif kind in ("circumflex","caron"):
            top = 1 if kind=="circumflex" else 0
            move(0,1-top);line(.5,top);line(1,1-top)
        elif kind=="breve":
            move(0,.97);curve(.04,.37,.22,0,.50,0);curve(.78,0,.96,.37,1,.97)
        elif kind=="tilde":
            move(0,.18);curve(.12,1.31,.33,1.13,.52,.55);curve(.72,-.06,.87,-.34,1,.81)
        elif kind=="hookabove":
            move(0,.65);curve(.08,.91,.31,1,.53,1);curve(.83,1,1,.86,1,.66)
            curve(1,.47,.82,.37,.56,.33);curve(.49,.32,.48,.26,.48,.18);line(.48,0)
        elif kind=="horn":
            move(.05,0);curve(.55,.27,.94,.66,.94,1)
        elif kind=="ogonek":
            move(.73,1);curve(.56,.78,.15,.53,.15,.32);curve(.15,.06,.53,-.09,.98,.10)
        elif kind=="cedilla":
            move(.42,1);line(.29,.66);curve(.68,.67,.96,.51,.92,.31)
            curve(.86,-.01,.40,-.06,0,.09)
        else:
            raise ValueError(kind)
        cap = pathops.LineCap.ROUND_CAP if round_cap else pathops.LineCap.BUTT_CAP
        join = pathops.LineJoin.ROUND_JOIN if round_cap else pathops.LineJoin.BEVEL_JOIN
        result.stroke(width,cap,join,3)
        result.convertConicsToQuads(.04)
    result.simplify(clockwise=True)
    clean = pathops.Path()
    for contour in result.contours:
        if abs(contour.area)>.1:
            clean.addPath(contour)
    return clean.transform(1,0,slant,1,0,0)


def angular_tracks(design, name, cells, kind):
    # All four signs in 0.300 are polygons. Register the named corners
    # directly, including the bevel and notch of a circumflex. Matching by
    # perimeter length lets the notch slide along an arm at intermediate weights.
    def vertices(font):
        pen = OutlinePen(None)
        font.getGlyphSet()[name].draw(TransformPen(pen, (1,0,-design.slant,1,0,0)))
        return pen.contours[0].pieces[:,0]

    ref = vertices(design.regular)
    bold = vertices(design.bold)
    bottom, top = ref.imag.min(), ref.imag.max()
    advance = design.advance0[name]
    profiles = []
    for w,d in cells:
        sx,dx = design.transform(name,w,d)
        if advance:
            sx = 1+.36*(d/100-1)
            dx = (design.advance(name,w,d)-advance*sx)/2
        z = ref.copy()
        if w==900:
            z = bold.real + 1j*(bottom+(bold.imag-bold.imag.min())*(top-bottom)/np.ptp(bold.imag))
        z = z.real*sx+dx + 1j*z.imag
        if w==100:
            if kind in ('acute','grave'):
                # Centre the physical pen on the original sloping stroke.
                floors = z.imag==bottom
                mid0,mid1 = z.real[floors].mean(),z.real[~floors].mean()
                half = 12*np.hypot(1,(mid1-mid0)/(top-bottom))
                axis = np.where(floors,mid0,mid1)
                z = axis+half*np.sign(z.real-axis) + 1j*z.imag
            else:
                # Both chevrons have two flat end cuts, one bevel and one notch.
                tips = z.imag==(bottom if kind=='circumflex' else top)
                xs = np.sort(z.real[tips])
                left,right = xs[:2].mean(),xs[2:].mean()
                mid = (left+right)/2
                pen = 22
                height = top-bottom
                slope = (right-left)/(2*height)
                half = pen*.5*np.hypot(1,slope)
                apex = top if kind=='circumflex' else bottom
                ends = bottom if kind=='circumflex' else top
                direction = np.sign(apex-ends)
                for i,p in enumerate(z):
                    if tips[i]:
                        center = left if p.real<mid else right
                        z[i] = center+np.sign(p.real-center)*half + 1j*ends
                    elif p.imag==apex:
                        z[i] = mid+np.sign(p.real-mid)*pen*.24 + 1j*apex
                    else:
                        z[i] = mid + 1j*(apex-direction*(2*half-pen*.24)/slope)
        z = z + design.slant*z.imag
        end = np.roll(z,-1)
        ring = Contour(np.column_stack((z,(2*z+end)/3,(z+2*end)/3,end)))
        if not profiles:
            stations = ring.knots
        for radius in (0,{100:5,400:12,900:19}[w]):
            profiles.append(Profile(ring,stations,ring.knots,radius))
    rows = list(map(np.asarray,compatible_points(profiles,.16)))
    return rows,[len(rows[0])-1]


def accent_tracks(design,name,cells):
    slant = design.slant
    gs = design.regular.getGlyphSet()
    kind = accent_name(name)
    if kind in ('grave','acute','circumflex','caron') and not name.endswith('.alt'):
        return angular_tracks(design,name,cells,kind)
    plain = as_path(gs,name,(1,0,-slant,1,0,0))
    ref = OutlinePen(gs)
    gs[name].draw(ref)
    all_shapes = []
    for w,d in cells:
        sx,dx = design.transform(name,w,d)
        # Spacing versions use the same amount of optical expansion as
        # combining marks, expressed relative to their own advance center.
        advance = design.advance0[name]
        if advance:
            sx = 1+.36*(d/100-1)
            dx = (design.advance(name,w,d)-advance*sx)/2
        pen = OutlinePen(None)
        if w==400:
            plain.transform(sx,0,slant,1,dx,0).draw(pen)
        elif w==900:
            # The original heavy accent is individually drawn for this
            # family, including its head, tail and spacing from a second mark.
            bold = as_path(design.bold.getGlyphSet(),name,(1,0,-slant,1,0,0))
            x0,y0,x1,y1 = plain.bounds
            _,v0,_,v1 = bold.bounds
            # Use exactly the original height band for combinations stacked
            # by mkmk. Move a spacing accent back to the new advance center.
            sy = (y1-y0)/max(v1-v0,1)
            bold.transform(sx,0,slant*sy,sy,dx+slant*(y0-sy*v0),y0-sy*v0).draw(pen)
        else:
            thin = designed_accent(accent_name(name),plain.bounds,w,sx,dx,slant,name.endswith(".alt"))
            kind = accent_name(name)
            if kind in ("ogonek","cedilla","horn"):
                before = plain.bounds
                after = thin.bounds
                dy = before[1]-after[1] if kind=="horn" else before[3]-after[3]
                thin = thin.transform(1,0,0,1,0,dy)
            thin.draw(pen)
        all_shapes.append(ordered_contours(ref.contours,pen.contours))
    return tracks_for(ref.contours,all_shapes,cells,{100:5,400:12,900:19})


def tracks_for(reference,all_shapes,cells,radii,bar=False):
    out = [[] for _ in range(2*len(cells))]
    ends = []
    for i,b in enumerate(reference):
        anchors=b.terminals(bar)
        if len(anchors)>=2:
            b=b.roll(anchors[0])
        profiles=[]
        for j,(w,d) in enumerate(cells):
            reg=all_shapes[j][i].registered(b,bar=bar) if j else (b,[0,1],[0,1])
            for r in (0,radii[w]):
                profiles.append(Profile(*reg,r))
        for track,z in zip(out,compatible_points(profiles,.20)):
            track.extend(z)
        ends.append(len(out[0])-1)
    return [np.asarray(z) for z in out],ends
