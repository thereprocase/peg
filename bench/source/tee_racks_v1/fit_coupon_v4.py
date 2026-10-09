"""Straight-guide trial replacing HX04's flared/counterbored T and small-key seats.
Build locally with FreeCAD's Python; --plan needs only ordinary Python.
These are fit trials, not calibrated production bores or a load-qualified print.
"""
import argparse, hashlib, json, math, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'study'))
from socket_policy import burial_depth, ENTRY_LEAD_MM, guide_length
CLEARANCES=(.19,)  # owner: add 0.18 mm total AF clearance to v3
VENT_DIAMETER=1.
TOOLS=tuple((label,af,burial_depth(af)) for label,af in (('L2',2.),('T2.5',2.5),('T5',5.),('T10',10.)))
LEAD=ENTRY_LEAD_MM
WALL=3.
FLOOR=3.


def specs():
    return [dict(id=f'{label}_F_C{round(c*100):02d}',tool=label,af_mm=af,seat_depth_mm=depth,
                 clearance_per_flat_mm=c,bore_af_mm=af+2*c,lead_depth_mm=LEAD,
                 straight_guide_mm=depth-LEAD,floor_thickness_mm=FLOOR,vent_diameter_mm=VENT_DIAMETER,
                 roof='six original hex flats; bore roofs need actual slicer/print review')
            for label,af,depth in TOOLS for c in CLEARANCES]


def hex_play(af,c):
    q=(af/2+c)/(af/math.sqrt(3))
    return 30. if q>=1 else 30-math.degrees(math.acos(q))


def build(out):
    import FreeCAD as A
    import Part, MeshPart
    V=A.Vector
    out.mkdir(parents=True,exist_ok=True)
    doc=A.newDocument('HX05StraightGuideCouponV4')
    def polygon(af,z):
        r=af/math.sqrt(3)
        # Owner confirmed handle axis along flats: Y is the flat-to-flat direction.
        pts=[V(r*math.sin(k*math.pi/3+math.pi/6),r*math.cos(k*math.pi/3+math.pi/6),z) for k in range(6)]
        return Part.makePolygon(pts+[pts[0]])
    def rod(af,z,length):return Part.Face(polygon(af,z)).extrude(V(0,0,length))
    def mesh(shape,path):
        m=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.03,AngularDeflection=.12,Relative=False)
        m.write(str(path))
    def label(shape,text,depth,width):
        # Label on print top, safely within the 3 mm outer wall.
        wires=Part.makeWireString(text,str(HERE/'fonts/Fillaprint-Regular.ttf'),2.6)
        faces=[Part.Face(w,'Part::FaceMakerBullseye') for w in wires if w]
        glyphs=Part.makeCompound(faces);bb=glyphs.BoundBox
        glyphs.translate(V(-(bb.XMin+bb.XMax)/2,-(bb.YMin+bb.YMax)/2,0))
        # Local text X -> -Y, text Y -> Z, text normal -> -X.
        matrix=A.Matrix(0,0,-1,0,-1,0,0,0,0,1,0,0,0,0,0,1)
        glyphs.transformShape(matrix);glyphs.translate(V(-width/2-.1,0,depth/2))
        cutters=Part.makeCompound([f.extrude(V(.6,0,0)) for f in glyphs.Faces])
        result=shape.cut(cutters).removeSplitter()
        assert result.isValid() and len(result.Solids)==1 and result.Volume<shape.Volume,'label failed'
        return result
    reports=[];pieces=[];xoff=yoff=row_h=0.
    for spec in specs():
        af=spec['af_mm'];afb=spec['bore_af_mm'];d=spec['seat_depth_mm'];radius=afb/math.sqrt(3)
        width=2*radius+2*WALL
        blank=Part.makeBox(width,width,d+FLOOR,V(-width/2,-width/2,-FLOOR))
        bore=rod(afb,0,d+1)
        # A short lead at the mouth; no counterbore, flare, round chamber or sloped seat.
        lead=Part.makeLoft([polygon(afb,d-LEAD),polygon(afb+2*LEAD,d+.001)],True,True)
        vent=Part.makeCylinder(VENT_DIAMETER/2,FLOOR+.2,V(0,0,-FLOOR-.1),V(0,0,1))
        shape=blank.cut(bore.fuse(lead).fuse(vent)).removeSplitter()
        assert shape.isValid() and len(shape.Solids)==1
        tool=rod(af,.1,d-LEAD-.2)
        assert shape.common(tool).Volume<1e-7,'nominal shaft does not fit'
        samples=[]
        for angle in [i*.25 for i in range(121)]:
            moved=tool.copy();moved.rotate(V(0,0,0),V(0,0,1),angle)
            samples.append(dict(deg=angle,intersection_mm3=shape.common(moved).Volume))
        expected=hex_play(af,spec['clearance_per_flat_mm'])
        first=next((q['deg'] for q in samples if q['intersection_mm3']>1e-7),None)
        if expected==30.: assert first is None, 'unexpected stop in freely rotating bore'
        else:
            assert samples[-1]['intersection_mm3']>1e-4,'no hex rotational stop'
            assert expected<=first<=expected+.251,(first,expected)
        # Check open vent and retained square-ended stop beside it.
        assert shape.common(vent).Volume<1e-7
        floor_probe=Part.makeCylinder(.2,FLOOR,V(.75,0,-FLOOR),V(0,0,1))
        assert abs(shape.common(floor_probe).Volume-floor_probe.Volume)<1e-7
        text=f"{spec['tool']} F{round(spec['clearance_per_flat_mm']*100):02d}"
        shape=label(shape,text,d,width)
        shape.exportStep(str(out/(spec['id']+'__installed.step')))
        rotation=A.Matrix();rotation.rotateY(math.pi/2)
        printed=shape.copy();printed.transformShape(rotation);bb=printed.BoundBox
        if xoff and xoff+bb.XLength>220:xoff=0;yoff+=row_h+8;row_h=0
        printed.translate(V(xoff-bb.XMin,yoff-bb.YMin,-bb.ZMin))
        xoff+=bb.XLength+8;row_h=max(row_h,bb.YLength)
        feature=doc.addObject('Part::Feature',spec['id']);feature.Label=text;feature.Shape=printed
        for name,value in [('ToolAcrossFlats',af),('BoreAcrossFlats',afb),('SeatDepth',d),('StraightGuideDepth',d-LEAD),('ClearancePerFlat',spec['clearance_per_flat_mm'])]:
            feature.addProperty('App::PropertyLength',name,'Coupon dimensions');setattr(feature,name,value)
        pieces.append(printed)
        reports.append(dict(spec,native_valid=shape.isValid(),native_solids=len(shape.Solids),volume_mm3=shape.Volume,
                            ideal_one_sided_play_deg=expected,free_full_rotation=expected==30.,first_sampled_rotation_hit_deg=first,
                            collision_at_30_deg_mm3=samples[-1]['intersection_mm3'],floor_probe_mm=FLOOR))
    packed=Part.makeCompound(pieces)
    mesh(packed,out/'HX05-fit-v4__left-end__print.stl')
    packed.exportStep(str(out/'HX05-fit-v4__left-end__print.step'))
    doc.recompute();doc.saveAs(str(out/'HX05-fit-v4.FCStd'))
    bb=packed.BoundBox
    report=dict(version=4,guide_policy='max(40 mm, 8 x shaft size), with entrance chamfer additional',policy_sha256=hashlib.sha256((HERE/'study/socket_policy.py').read_bytes()).hexdigest(),part='HX05-fit-v4',status='native geometry checked; slicing and physical trial pending',
                handle_axis='flat-to-flat along design Y',freecad=A.Version(),occ=Part.OCC_VERSION,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                font_sha256=hashlib.sha256((HERE/'fonts/Fillaprint-Regular.ttf').read_bytes()).hexdigest(),
                print_extents_mm=[bb.XLength,bb.YLength,bb.ZLength],pieces=reports,
                note='Lengths are along shaft. F19 means handle flat-to-flat and 0.19 mm clearance per flat, with 0.38 mm total AF allowance. Each floor has a 1 mm through vent. The original six-flat section is intentional; review its roofs in the actual owner-profile toolpaths. No snug-fit or no-support claim.')
    (out/'fit-v4-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(report,indent=2))
    A.closeDocument(doc.Name)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--plan',action='store_true');ap.add_argument('--out',type=Path,default=HERE/'runs/fit-v4');a=ap.parse_args()
    if a.plan:print(json.dumps(specs(),indent=2))
    else:build(a.out.resolve())

if __name__=='__main__':main()
