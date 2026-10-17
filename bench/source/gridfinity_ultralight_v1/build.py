"""Prototype open Gridfinity shelves using the repository's current native pegs.

Run with FreeCAD Python. Coordinates: X across, Y out of board, Z installed up.
The inverted top pose is a print-preparation candidate, not a qualified job.
"""
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
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
TOP = 5.72
LIFT = .60
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


def profile(cx, cy, sections):
    wires = [rounded_wire(cx,cy,w,w,r,z) for z,w,r in sections]
    return Part.makeLoft(wires,True,True)


def export(shape, name):
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


receiver,_ = C.K.receiver(1,1,'upright')
upper=receiver.common(C.region(-10,15))
lower=receiver.common(C.region(-40,-10))
lower.translate(V(0,0,25.4))
upper,upper_info=C.with_nub(upper,5.6)
lower,lower_info=C.with_nub(lower,6.35)
records=[]
for n,cells in [(1,2),(2,4)]:
    width=25.4*cells-2
    columns=[-(cells-1)*25.4/2,(cells-1)*25.4/2]
    centers=[(i-(n-1)/2)*42 for i in range(n)]
    pieces=[]
    pockets=[]
    for x in centers:
        outer=Part.Face(rounded_wire(x,CY,46,46,5,.12+LIFT)).extrude(V(0,0,5))
        # Shift the standard receiver up so gravity taper contact occurs at the
        # coplanar frame/ridge datum. Relieve the first-layer mouth separately.
        pocket=profile(x,CY,[(-1,36.5,1.25),(.47+LIFT+.35,36.5,1.25),
                             (1.17+LIFT+.35,37.9,1.95),(2.97+LIFT+.35,37.9,1.95),
                             (TOP+.35,42.2,4.1),(7+LIFT,42.2,4.1)])
        lip=profile(x,CY,[(TOP-.2,41.1,3.55),(TOP,41.9,3.95),(TOP+1,41.9,3.95)])
        pocket=pocket.fuse(lip)
        pockets.append(pocket)
        pieces.append(outer.cut(pocket))
    pieces.append(Part.makeBox(width,5.4,5,V(-width/2,.15,.12+LIFT)))
    if n==2:
        # Deepen the front perimeter rather than adding a centre web without a
        # corresponding lower mounting reaction. It remains below the bin feet.
        pieces.append(Part.makeBox(84,2.4,5.2,V(-42,49.15,.12+LIFT-5)))
        # Keep the assumed 1.9 x 10 mm beam core continuous between supports;
        # rounded adjacent rings otherwise leave an upper central scallop.
        pieces.append(Part.makeBox(76.2,1.9,10,V(-38.1,49.65,.12+LIFT-5)))
    pegs=[]
    for x in columns:
        pieces.append(Part.makeBox(10,5.4,34.8+LIFT,V(x-5,.15,-29.68)))
        # Triangular webs directly connect the lower receiver to the shelf front.
        pieces.append(C.K.poly_prism([(5,-27.5),(50.0,.12+LIFT),(5,2.0+LIFT)],'x',x-1.2,x+1.2))
        for peg,z in [(upper,0),(lower,-25.4)]:
            p=peg.copy();p.translate(V(x,0,z));pegs.append(p);pieces.append(p)
    shape=pieces[0].multiFuse(pieces[1:]).removeSplitter()
    # The receiving void also trims any brace material entering the foot envelope.
    for pocket in pockets:
        shape=shape.cut(pocket)
    # Preserve the repository's conservative host envelope at the raised rear edge.
    # This is a nominal host containment screen, not an interference-fit motion proof.
    envelope_data=json.loads((ROOT/'cad/conformal/host-envelope/allowed_host_volume.json').read_text())
    allowed=C.K.poly_prism(envelope_data['envelope_vertices_design_yz_mm'],'x',-150,150)
    host_box=Part.makeBox(300,60,150,V(-150,.15,-50))
    forbidden=host_box.cut(allowed)
    envelope_removed=shape.common(forbidden).Volume
    shape=shape.cut(forbidden)
    shape=shape.removeSplitter()
    protected=Part.makeBox(300,60.15,150,V(-150,-60,-75))
    expected=Part.makeCompound(pegs).common(protected)
    actual=shape.common(protected)
    peg_delta=expected.cut(actual).Volume+actual.cut(expected).Volume
    assert peg_delta<1e-6,peg_delta
    name=f'GF{n}1-v1-shelf-pf02c9-hoop5'
    assert upper.BoundBox.ZMax < TOP
    record=export(shape,name+'-installed')
    record['hook_crown_z_mm']=upper.BoundBox.ZMax
    record['hook_below_bed_plane_mm']=TOP-upper.BoundBox.ZMax
    record['nominal_host_envelope_trim_mm3']=envelope_removed
    record['nominal_host_envelope_residue_mm3']=shape.common(forbidden).Volume
    posed=shape.copy();posed.rotate(V(0,0,0),V(1,0,0),180)
    posed.translate(V(0,0,-posed.BoundBox.ZMin))
    record['print_pose']=export(posed,name+'-print-inverted')
    # Analytic reference bin feet plus body outline; no claim of compatibility with every remix.
    feet=[profile(x,CY,[(.37+LIFT,35.6,.8),(1.17+LIFT,37.2,1.6),(2.97+LIFT,37.2,1.6),(TOP,41.5,3.75)]) for x in centers]
    body=Part.Face(rounded_wire(0,CY,42*n-.5,41.5,3.75,TOP)).extrude(V(0,0,30))
    void=Part.Face(rounded_wire(0,CY,42*n-3.5,38.5,2.25,6.62+LIFT)).extrude(V(0,0,31))
    binshape=body.multiFuse(feet).cut(void).removeSplitter()
    nominal_overlap=binshape.common(shape).Volume
    assert nominal_overlap<1e-6,nominal_overlap
    # Find first downward contact; gravity support must exist despite the open floor.
    lo,hi=0.,2.
    for _ in range(18):
        mid=(lo+hi)/2;b=binshape.copy();b.translate(V(0,0,-mid))
        if b.common(shape).Volume>1e-6:hi=mid
        else:lo=mid
    assert hi<.6,(n,hi)
    export(binshape,name+'-reference-bin')
    record.update(name=name,grid=[n,1],mount_width_mm=width,peg_columns_x_mm=columns,
        seat_center_y_mm=CY,seat_top_z_mm=TOP,receiver_wall_mm=5.4,
        receiver_profile_shift_up_mm=.35,first_layer_mouth_relief_mm=.20,
        mouth_width_at_bed_plane_mm=41.9,board_side_difference_mm3=peg_delta,
        nominal_bin_overlap_mm3=nominal_overlap,downward_first_contact_mm=hi,
        asa_solid_mass_estimate_g=shape.Volume*.00107,
        assumed_contents_kg=.25*n,gravity_moment_Nmm=.25*n*9.81*(CY-.15),
        accidental_lift_N=10,front_lift_moment_Nmm=10*(CY+23-.15),
        equivalent_total_mount_couple_N=10*(CY+23-.15)/25.4,
        front_beam_added_depth_mm=5 if n==2 else 0,
        front_beam_local_estimate={'E_assumed_MPa':1000,'section_width_mm':1.9,
          'section_height_mm':10 if n==2 else 5,'span_mm':columns[1]-columns[0],
          'all_contents_point_load_at_midspan_N':.25*n*9.81,
          'deflection_mm':(.25*n*9.81)*(columns[1]-columns[0])**3/(48*1000*(1.9*(10 if n==2 else 5)**3/12)),
          'scope':'Simply-supported local perimeter beam idealization; excludes roots, webs, anisotropy, creep, board and snap retention. Assumed modulus is not measured.'},
        status='CAD prototype; physical bin fit, snap retention, installation and print supports unqualified')
    records.append(record)
    print(name,shape.Volume,hi,flush=True)
data={'source_repo_commit':'e84f83872fd867ac0cdd8c7de7819579f912839b',
      'profile_source':'https://github.com/kennetek/gridfinity-rebuilt-openscad/blob/main/src/core/gridfinity-baseplate.scad',
      'connector_sources':[upper_info,lower_info],'parts':records,
      'limits':'Loads are comparison scenarios only; no measured hoop unsnap force or physical rating. No print submission.'}
(OUT/'CHECKS.json').write_text(json.dumps(data,indent=2)+'\n')
(OUT/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in sorted(OUT.iterdir()) if p.suffix in ['.step','.stl','.FCStd']))
