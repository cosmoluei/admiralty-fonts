"""Single-storey italic a and integral masters, drawn from continuous measured strokes."""
import numpy as np
import pathops
from functools import lru_cache

from accent_masters import as_path, tracks_for
from check_word_proof import Edges, section
from compatible import OutlinePen, ordered_contours
from stroke_geometry import round_branches, stroke
from study_shapes import Drawing, contour_sides, draw_d_bowl, draw_g, draw_letter
from build_axis_study import master_glyph_sets, master_outline

upright_sources=lru_cache(maxsize=1)(master_glyph_sets)
MONO_BOWLS={"b","d","p","q","thorn","dcroat"}


def inherited_italic_tracks(design,name,cells):
    # The 0.300 humanist italic shares these upright constructions. The
    # single-storey a, long f and flagged i have their own italic designs.
    letter="j" if name=="dotlessj" else name
    gs=design.regular.getGlyphSet()
    slant=design.slant
    reference=OutlinePen(None)
    as_path(gs,name,(1,0,-slant,1,260*slant,0)).draw(reference)
    sources=upright_sources()
    shapes=[]
    for cell,source in zip(cells,sources):
        w,d=cell
        if cell==(400,100):
            shapes.append(reference.contours)
            continue
        geometry,advance=master_outline(letter,cell,source,sources[0])
        p=OutlinePen(source)
        if w==100 and letter in ('s','g'):
            # Measure Thin at right angles to the already slanted spine.
            # A sheared circular pen would be too heavy on one diagonal.
            path=pathops.Path()
            for spine in draw_letter(letter,advance,w,d).spines:
                path.addPath(stroke([[z+slant*(z.imag-260) for z in seg] for seg in spine],24))
            path.simplify(clockwise=True)
            if letter=='g':
                path=round_branches(path,24)
            path.transform(1,0,-slant,1,260*slant,0).draw(p)
        else:
            geometry.draw(p)
        rings=p.contours
        if name=="dotlessj":
            rings=[min(rings,key=lambda c:c.center.imag)]
        shapes.append(ordered_contours(reference.contours,rings))
    points,ends=tracks_for(reference.contours,shapes,cells,{100:9,400:30,900:49},bar=letter=='e')
    return [z+slant*(z.imag-260) for z in points],ends


def cursive_a(outline, scale, offset, thickness, slant, contrast=1):
    edge = Edges(None, 1)
    outline.draw(edge)
    edges = np.asarray(edge.edges)
    left, _, shaft_l, shaft_r = section(edges, 260)
    left = left * scale + offset + thickness/2
    shaft = (shaft_l + shaft_r)/2 * scale + offset
    span = shaft-left
    low, high = -10+thickness/2, 530-thickness/2
    middle = left+.50*span
    end = max(outline.bounds[2]*scale+offset-thickness/2, shaft+thickness*.66)
    # Keep the oval and the exit independent. The upright segment supplies
    # the entire right edge of the counter, including in a compressed Black.
    bowl = [[(shaft,355),(shaft,440),(middle+.33*span,high),(middle,high)],
            [(middle,high),(middle-.28*span,high),(left,428),(left,260)],
            [(left,260),(left,90),(middle-.28*span,low),(middle,low)],
            [(middle,low),(middle+.33*span,low),(shaft,77),(shaft,172)]]
    tip_height = min(63,42+thickness*.17)
    tail_low = low+7
    stem = [[(shaft,520),(shaft,134)],
            [(shaft,134),(shaft,91),(shaft,tail_low),(shaft+.49*(end-shaft),tail_low)],
            [(shaft+.49*(end-shaft),tail_low),(shaft+.73*(end-shaft),tail_low),
             (end-.12*(end-shaft),tip_height-10),(end,tip_height)]]
    def ink(parts):
        upright=stroke([[complex(x+slant*y,y/contrast) for x,y in seg] for seg in parts],thickness)
        return upright.transform(1,0,0,contrast,0,0)
    path = pathops.op(ink(bowl),ink(stem),pathops.PathOp.UNION)
    path.simplify(clockwise=True)
    return path.transform(1,0,-slant,1,0,0)


def serif_a(scale, shift, weight):
    """Double-storey bowl, droplet at the top left and an upturned exit."""
    edge=48*scale+shift
    stem=24 if weight==100 else 128
    hair=24 if weight==100 else 68
    post=478*scale+shift
    wall=post-stem
    span=wall-edge
    crown=edge+.64*span
    bottom=edge+.45*span
    tail=post+max(26,54*scale)
    waist=310 if weight==100 else 326
    terminal=edge+.16*span
    bead=16 if weight==100 else 48
    path=pathops.Path()
    pen=path.getPen()
    side=contour_sides(pen,bottom,-10)
    side((bottom+.21*span,-10,wall-.10*span,23,wall+2,65))
    side((wall+.10*stem,12,post-.38*stem,-10,post-.14*stem,-10),
         (post+.40*(tail-post),-10,tail-5,6,tail,15))
    side((tail-4,15+.76*hair))
    side((post+.62*(tail-post),25,post,48,post,118),(post,355),
         (post,461,crown+.35*span,530,crown,530),
         (edge+.31*span,530,terminal-bead,480,terminal-bead,418),
         (terminal-bead,418-.61*bead,terminal-.49*bead,418-bead,terminal,418-bead),
         (terminal+.56*bead,418-bead,terminal+bead,418-.55*bead,terminal+bead,418),
         (terminal+bead,463,edge+.43*span,530-hair,crown,530-hair),
         (crown+.25*span,530-hair,wall,432,wall,354),(wall,waist))
    side((wall-.34*span,waist-5,edge,259,edge,136),
         (edge,46,edge+.21*span,-10,bottom,-10))
    pen.closePath()
    side=contour_sides(pen,bottom+.04*span,-10+hair)
    side((bottom-.18*span,-10+hair,edge+stem,87,edge+stem,137),
         (edge+stem,213,wall-.34*span,waist-hair-5,wall,waist-hair))
    side((wall,140),(wall,95,bottom+.21*span,-10+hair,bottom+.04*span,-10+hair))
    pen.closePath()
    path.simplify(clockwise=True)
    return path


def mono_g(outline, scale, shift, weight, width):
    # The released Mono g inherits the Sans skeleton centered in a 600-unit
    # cell. Draw the same bowl and tail while preserving Mono sidebearings.
    x0,_,x1,_=outline.bounds
    stem=24 if weight==100 else 121
    horizontal=24 if weight==100 else 98
    origin=x0*scale+shift+stem/2
    span=(x1-x0)*scale-stem
    drawing=Drawing(origin,span,stem,horizontal/stem)
    draw_g(drawing.add,530-horizontal/2,-10+horizontal/2,horizontal/2,weight,width,span)
    drawing.path.simplify(clockwise=True)
    return round_branches(drawing.path,stem).transform(1,0,0,horizontal/stem)


def mono_bowl(design,name,plain,scale,shift,weight):
    stroke_width=24 if weight==100 else 123
    bar=24 if weight==100 else 102
    x0,_,x1,_=plain.bounds
    left,right=x0*scale+shift,x1*scale+shift
    g=Drawing(left+stroke_width/2,right-left-stroke_width,stroke_width,bar/stroke_width)
    top,bottom=(740,-220) if name=='thorn' else (740,0)
    g.add((1,top),(1,bottom))
    draw_d_bowl(g.add,530-bar/2,-10+bar/2)
    g.path.simplify(clockwise=True)
    path=round_branches(g.path,stroke_width).transform(1,0,0,bar/stroke_width)
    if name in ('b','p','thorn'):
        path=path.transform(-1,0,0,1,left+right,0)
    if name in ('p','q'):
        path=path.transform(1,0,0,-1,0,520)
    path.simplify(clockwise=True)
    return path


def barred_d_tracks(design,cells):
    # Keep the complete d as one construction and overlay the bar. The
    # two exposed ends cannot exchange places when interpolating a join.
    points,ends=cursive_tracks(design,'d',cells)
    plain=as_path(design.regular.getGlyphSet(),'dcroat',(1,0,-design.slant,1,0,0))
    edges=Edges(None,1)
    plain.draw(edges)
    x=section(np.asarray(edges.edges),588)
    out=[]
    for idx,(w,d) in enumerate(cells):
        sx,dx=design.transform('d',w,d)
        x0,x1=x[0]*sx+dx,x[-1]*sx+dx
        thick={100:24,400:64,900:84}[w]
        z=np.array([x0+1j*(588-thick/2),x0+1j*(588+thick/2),
                    x1+1j*(588+thick/2),x1+1j*(588-thick/2)])
        for r,trim in enumerate((0,min(.40*thick,{100:9,400:20,900:32}[w]))):
            a,b=np.roll(z,1)-z,np.roll(z,-1)-z
            before,after=z+trim*a/abs(a),z+trim*b/abs(b)
            ring=np.column_stack([before,z,after,(after+np.roll(before,-1))/2]).ravel()
            out.append(np.r_[points[2*idx+r],ring+design.slant*ring.imag])
    return out,[*ends,len(out[0])-1]


def integral(outline, scale, shift, thickness, slant):
    x0,y0,x1,y1 = outline.bounds
    # The slanted upright and both hooked ends follow the original 0.300
    # integral pen path. Its overall height stays fixed as the pen changes.
    lo,hi = x0*scale+shift+thickness/2,x1*scale+shift-thickness/2
    def point(x,y):
        xx = lo+(x-70)/330*(hi-lo)
        yy = y0+thickness/2+(y+155)/905*(y1-y0-thickness)
        return complex(xx+slant*yy,yy)
    pieces = [[(70,-150),(150,-175),(205,-120),(215,-10)],
              [(215,-10),(250,610)],[(250,610),(258,720),(318,770),(400,745)]]
    path = stroke([[point(x,y) for x,y in seg] for seg in pieces],thickness)
    path.simplify(clockwise=True)
    return path.transform(1,0,-slant,1,0,0)


def script_l(outline,scale,shift,weight,slant):
    x0,y0,x1,y1=outline.bounds
    span=(x1-x0)*scale
    pen_width=24 if weight==100 else min(108,.30*span)
    lo=x0*scale+shift+pen_width/2
    def point(x,y):
        xx=lo+(x-90)/298*(span-pen_width)
        yy=y0+pen_width/2+(y+10)/745*(y1-y0-pen_width)
        return xx+slant*yy,yy
    # Original liter-sign ductus, including the crossing into the long stem.
    lines=[[(220,250),(320,420),(320,575)],[(320,690),(280,735),(236,735)],
           [(180,735),(158,662),(158,540)],[(158,190)],
           [(158,60),(205,-10),(285,-10)],[(328,-10),(360,12),(388,50)]]
    path=pathops.Path()
    path.moveTo(*point(90,150))
    for segment in lines:
        pts=[coord for xy in segment for coord in point(*xy)]
        if len(segment)==1:
            path.lineTo(*pts)
        else:
            path.cubicTo(*pts)
    path.stroke(pen_width,pathops.LineCap.ROUND_CAP,pathops.LineJoin.ROUND_JOIN,4)
    path.convertConicsToQuads(.04)
    path.simplify(clockwise=True)
    return path.transform(1,0,-slant,1,0,0)


def cursive_tracks(design, name, cells):
    if name=='dcroat':
        return barred_d_tracks(design,cells)
    gs = design.regular.getGlyphSet()
    plain = as_path(gs,name,(1,0,-design.slant,1,0,0))
    reference = OutlinePen(None)
    plain.draw(reference)
    shapes=[]
    for weight,width in cells:
        sx,dx = design.transform(name,weight,width)
        if weight==400:
            shape=plain.transform(sx,0,0,1,dx,0)
        elif name=='integral':
            shape=integral(plain,sx,dx,24 if weight==100 else 111,design.slant)
        elif name=='uni2113':
            shape=script_l(plain,sx,dx,weight,design.slant)
        elif name=='g':
            shape=mono_g(plain,sx,dx,weight,width)
        elif name in MONO_BOWLS:
            shape=mono_bowl(design,name,plain,sx,dx,weight)
        elif not design.slant:
            shape=serif_a(sx,dx,weight)
        else:
            contrast=1 if weight==100 else (.76 if design.serif else .86)
            shape=cursive_a(plain,sx,dx,24 if weight==100 else 121,design.slant,contrast)
        pen=OutlinePen(None)
        for ring in shape.contours:
            if abs(ring.area)>.1:
                ring.draw(pen)
        shapes.append(ordered_contours(reference.contours,pen.contours))
    points,ends=tracks_for(reference.contours,shapes,cells,{100:9,400:30,900:42})
    return [z+design.slant*z.imag for z in points],ends
