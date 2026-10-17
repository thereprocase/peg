"""Parameterized native Gridfinity shelves. Run in FreeCAD Python; no printer actions."""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import sys

import FreeCAD as A
import Part
import MeshPart

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("connectors", ROOT / "bench/source/peg_connectors_v1/build.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
V = A.Vector
TOP = 5.72
CY = 28.55

def rounded_wire(cx, cy, width, depth, radius, z):
    """Exact tangent arcs and straight edges, counterclockwise."""
    x0, x1 = cx-width/2, cx+width/2
    y0, y1 = cy-depth/2, cy+depth/2
    points = [(x0+radius,y0),(x1-radius,y0),(x1,y0+radius),
              (x1,y1-radius),(x1-radius,y1),(x0+radius,y1),
              (x0,y1-radius),(x0,y0+radius)]
    corners = [(x1-radius,y0+radius,-45),(x1-radius,y1-radius,45),
               (x0+radius,y1-radius,135),(x0+radius,y0+radius,225)]
    edges = []
    for i in range(4):
        a,b,c = points[2*i],points[2*i+1],points[(2*i+2)%8]
        edges.append(Part.makeLine(V(*a,z),V(*b,z)))
        x,y,ang = corners[i]
        mid = V(x+radius*math.cos(math.radians(ang)),y+radius*math.sin(math.radians(ang)),z)
        edges.append(Part.Arc(V(*b,z),mid,V(*c,z)).toShape())
    return Part.Wire(edges)


def frame_wire(width, back, front, z):
    """One outer outline: straight rear/side joins and tangent R5 front corners."""
    x=width/2; r=5; q=r/math.sqrt(2)
    a,b,c,d,e,f=[V(*p,z) for p in [(-x,back),(x,back),(x,front-r),(x-r,front),(-x+r,front),(-x,front-r)]]
    return Part.Wire([Part.makeLine(a,b),Part.makeLine(b,c),
        Part.Arc(c,V(x-r+q,front-r+q,z),d).toShape(),Part.makeLine(d,e),
        Part.Arc(e,V(-x+r-q,front-r+q,z),f).toShape(),Part.makeLine(f,a)])


def profile(cx, cy, sections):
    wires = [rounded_wire(cx,cy,w,w,r,z) for z,w,r in sections]
    return Part.makeLoft(wires,True,True)


def export(shape, name, OUT):
    assert shape.isValid() and len(shape.Solids)==1, name
    p = OUT/(name+'.step')
    shape.exportStep(str(p))
    back = Part.read(str(p))
    delta = shape.cut(back).Volume+back.cut(shape).Volume
    assert delta < 1e-5, (name,delta)
    mesh = MeshPart.meshFromShape(Shape=shape,LinearDeflection=.005,AngularDeflection=.087,Relative=False)
    mesh.write(str(OUT/(name+'.stl')))
    doc = A.newDocument(name.replace('-','_'))
    obj = doc.addObject('PartDesign::Feature','Shelf')
    obj.Shape=shape
    doc.recompute()
    doc.saveAs(str(OUT/(name+'.FCStd')))
    A.closeDocument(doc.Name)
    return {'native_valid':True,'native_solids':1,'volume_mm3':shape.Volume,
            'step_roundtrip_difference_mm3':delta,
            'bounds_mm':[[shape.BoundBox.XMin,shape.BoundBox.YMin,shape.BoundBox.ZMin],
                         [shape.BoundBox.XMax,shape.BoundBox.YMax,shape.BoundBox.ZMax]]}


def generate(values, out):
    from parameters import validate
    p = validate(values)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    receiver, _ = C.K.receiver(1, 1, 'upright')
    upper = receiver.common(C.region(-10, 15))
    lower = receiver.common(C.region(-40, -10))
    lower.translate(V(0, 0, 25.4))
    upper, _ = C.with_nub(upper, 5.6)
    lower, _ = C.with_nub(lower, 6.35)
    original_fit = C.K.P.FIT_SOURCE
    C.K.P.FIT_SOURCE = C.K.G.fit_file(.49)
    reference = C.K.P.load_reference()
    C.K.P.FIT_SOURCE = original_fit
    locator = next(s for s in reference.Solids if s.BoundBox.ZMax < -9.9).common(C.region(-40,-10))
    locator.translate(V(0,0,25.4))
    locator, _ = C.with_nub(locator,6.35)
    peg_rows = [(upper,0)] + [(lower if i == p['mount_rows']-1 else locator,z) for i,z in enumerate(p['mount_z']) if i]
    angle=p['angle']; tangent=math.tan(math.radians(angle))
    # Lift the seat hinge enough to keep both the complete root wall and the
    # fixed hook below the eventual inverted bed plane, including tilted cases.
    rear_y=upper.BoundBox.YMin if tangent >= 0 else upper.BoundBox.YMax
    hinge=max(TOP, 3.48-tangent*5.4+.25,
              upper.BoundBox.ZMax-tangent*(rear_y-.15)+.275)
    def tilt(shape):
        shape=shape.copy()
        shape.rotate(V(0,.15,TOP),V(1,0,0),angle)
        shape.translate(V(0,0,hinge-TOP))
        return shape
    def tilted_point(y,z):
        a=math.radians(angle)
        return (.15+(y-.15)*math.cos(a)-(z-TOP)*math.sin(a),
                hinge+(y-.15)*math.sin(a)+(z-TOP)*math.cos(a))
    # These exact native connector meshes are also the browser kernel's inputs.
    for name, peg in [('upper', upper), ('lower', lower), ('locator', locator)]:
        MeshPart.meshFromShape(Shape=peg, LinearDeflection=.005, AngularDeflection=.087,
                              Relative=False).write(str(out / (name + '.stl')))
    pieces, pockets, feet, pegs = [], [], [], []
    front=p['front_y']; frame_width=p['frame_width']
    pieces.append(tilt(Part.Face(frame_wire(frame_width,5.55,front,.72)).extrude(V(0,0,5))))
    front_mask=tilt(Part.Face(frame_wire(frame_width,-1000,front,-1000)).extrude(V(0,0,2000)))
    c = p['clearance']
    for j in range(p['rows']):
        y = CY + 42*j
        for i in range(p['columns']):
            x = (i - (p['columns']-1)/2)*42
            sections = [(-1,36.5,1.25),(1.42,36.5,1.25),(2.12,37.9,1.95),
                        (3.92,37.9,1.95),(6.07,42.2,4.1),(7.6,42.2,4.1)]
            pocket = profile(x,y,[(z,w+2*c,r+c) for z,w,r in sections])
            lip = profile(x,y,[(5.52,41.1+2*c,3.55+c),(5.72,41.9+2*c,3.95+c),
                               (6.72,41.9+2*c,3.95+c)])
            pockets.append(tilt(pocket.fuse(lip)))
            feet.append(tilt(profile(x,y,[(.97,35.6,.8),(1.77,37.2,1.6),
                                    (3.57,37.2,1.6),(TOP,41.5,3.75)])))
    width, front = p['mount_width'], p['front_y']
    pieces.append(Part.makeBox(p['frame_width'],5.4,hinge+1-.72,V(-p['frame_width']/2,.15,.72)))
    # Continuous front beam, clipped to the tangent outer frame corners.
    if p['columns'] > 1 or p['beam'] > 5:
        pieces.append(tilt(Part.makeBox(42*p['columns'],2.4,p['beam'],
                                  V(-21*p['columns'],front-2.4,TOP-p['beam']))).common(front_mask))
    roots=[]
    bottom=p['back_bottom']
    if p['backplate']:
        pieces.append(Part.makeBox(frame_width,5.4,hinge+1-bottom,V(-frame_width/2,.15,bottom)))
    else:
        # Open-back option retains bottom cross-tie and posts at both grids.
        pieces.append(Part.makeBox(frame_width,5.4,4.28,V(-frame_width/2,.15,bottom)))
        for x in p['mount_columns']:
            pieces.append(Part.makeBox(10,5.4,hinge+1-bottom,V(x-5,.15,bottom)))
        for x in p['web_columns']:
            pieces.append(Part.makeBox(p['web'],5.4,hinge+1-bottom,V(x-p['web']/2,.15,bottom)))
    for x in p['web_columns']:
        pieces.append(C.K.poly_prism([(5,bottom+2.18),tilted_point(front,TOP-p['beam']),tilted_point(front,TOP-1),(5,hinge+tangent*4.85-3.12)],
                                     'x',x-p['web']/2,x+p['web']/2).common(front_mask))
    for x in p['mount_columns']:
        for peg,z in peg_rows:
            q=peg.copy();q.translate(V(x,0,z));pegs.append(q);pieces.append(q)
    shape=pieces[0].multiFuse(pieces[1:]).removeSplitter()
    # Trim receiving material to the seat plane. Peg bounds were accounted for
    # in hinge height; the exact board-side preservation gate follows below.
    reach=width/2+20
    below=C.K.poly_prism([(-60,-1000),(1000,-1000),
                          (1000,hinge+tangent*(1000-.15)),
                          (-60,hinge+tangent*(-60-.15))],'x',-reach,reach)
    shape=shape.common(below)
    for pocket in pockets:
        shape=shape.cut(pocket)
    envelope=json.loads((ROOT/'cad/conformal/host-envelope/allowed_host_volume.json').read_text())
    reach=width/2+20
    vertices=envelope['envelope_vertices_design_yz_mm']
    # The lower board-front boundary is vertical; extend its export bounds.
    vertices[0][1]=vertices[-1][1]=-200
    allowed=C.K.poly_prism(vertices,'x',-reach,reach)
    forbidden=Part.makeBox(2*reach,60,400,V(-reach,.15,-200)).cut(allowed)
    shape=shape.cut(forbidden).removeSplitter()
    protected=Part.makeBox(2*reach,60.15,400,V(-reach,-60,-200))
    original=Part.makeCompound(pegs).common(protected)
    actual=shape.common(protected)
    delta=original.cut(actual).Volume+actual.cut(original).Volume
    assert delta < 1e-6, ('connector changed',delta)
    for x in p['mount_columns']:
        for index,z0 in enumerate(p['mount_z']):
            z,d=z0+.12,6.72 if index==0 else 7.62
            block=Part.makeBox(d,5.4,d,V(x-d/2,.15,z-d/2))
            missing=block.cut(shape).Volume
            assert missing < 1e-6, ('root wall',x,z,missing)
            roots.append(dict(x=x,z=z,missing_mm3=missing))
    # For nonnegative added clearance, the reference feet must enter and withdraw.
    # A negative tuning value intentionally tightens fit and can hold the bin proud.
    foot_overlap=Part.makeCompound(feet).common(shape).Volume
    if c >= 0:
        assert foot_overlap < 1e-6, ('reference foot overlap',foot_overlap)
    core_depth=min(1.9,2.05-c)  # largest clearance consumes 0.05 mm of the top rim
    core=tilt(Part.makeBox(p['mount_columns'][-1]-p['mount_columns'][0],core_depth,p['beam'],
            V(p['mount_columns'][0],front-core_depth,TOP-p['beam'])))
    core_missing=core.cut(shape).Volume
    assert core_missing < 1e-6, ('front beam continuity',core_missing)
    lift_max=0.0
    if c >= 0:
        a=math.radians(angle)
        for foot in feet:
            for lift in [i*.5 for i in range(13)]:
                moved=foot.copy();moved.translate(V(0,-math.sin(a)*lift,math.cos(a)*lift))
                overlap=moved.common(shape).Volume;lift_max=max(lift_max,overlap)
                assert overlap < 1e-6, ('lift collision',lift,overlap)
    posed=shape.copy();posed.rotate(V(0,0,0),V(1,0,0),180-angle)
    posed.translate(V(0,0,-posed.BoundBox.ZMin))
    record=export(posed,'shelf-print',out)
    shape.exportStep(str(out/'shelf-installed.step'))
    record.update(parameters=p,hinge_z_mm=hinge,board_side_difference_mm3=delta,root_checks=roots,
                  reference_feet_overlap_mm3=foot_overlap,front_core_missing_mm3=core_missing,front_core_depth_mm=core_depth,
                  lift_poses_per_cell=13 if c>=0 else 0,lift_max_overlap_mm3=lift_max,
                  print_bed_xy_mm=[posed.BoundBox.XLength,posed.BoundBox.YLength],
                  status='Generated geometry; slice and physical fit/load checks required')
    (out/'CHECKS.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record),flush=True)


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output')
    parser.add_argument('--config',help='JSON shelf parameters including mount_rows and backplate')
    args=parser.parse_args()
    generate(json.loads(Path(args.config).read_text()) if args.config else {},args.output)


