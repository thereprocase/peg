"""Plain rectangular tapered through-hole; edge-on tool storage, mm."""
import argparse,json,hashlib,sys,math
from pathlib import Path
import FreeCAD as A
import Part
import MeshPart
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'solder_v12'))
import common as K
V=A.Vector
NAME='part-rectangular-tool-funnel__v3__upright__fit-pf02c9-hoop5'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fuse(parts):return parts[0].multiFuse(parts[1:]).removeSplitter()
def write(shape,path,deflection=.025):MeshPart.meshFromShape(Shape=shape,LinearDeflection=deflection,AngularDeflection=.10,Relative=False).write(str(path))


def rectangle(w,l,z):
    return Part.makePolygon([V(x,y,z) for x,y in [(-w/2,48-l/2),(w/2,48-l/2),(w/2,48+l/2),(-w/2,48+l/2),(-w/2,48-l/2)]])
def zflat(e,z):return abs(e.BoundBox.ZMin-z)<1e-6 and abs(e.BoundBox.ZMax-z)<1e-6

def build():
    outer=Part.makeLoft([rectangle(19,56,-42),rectangle(30,84,-10)],True,True).fuse(K.box(-9.5,20,-64,19,56,22)).removeSplitter()
    edges=[e for e in outer.Edges if not zflat(e,-64) and not zflat(e,-10)]
    outer=outer.makeFillet(2,edges);assert outer.isValid() and len(edges)==12
    outer=outer.makeChamfer(.6,[e for e in outer.Edges if zflat(e,-10)]);assert outer.isValid()
    web=K.box(-15,5.4,-64,30,25,54);edges=[e for e in web.Edges if e.BoundBox.ZLength>53 and e.BoundBox.YMin>30]
    web=web.makeFillet(2,edges);assert web.isValid() and len(edges)==2
    receiver,info=K.receiver(2,2,'upright',z0=-64)
    hole=Part.makeLoft([rectangle(10.65625,47.125,-43),rectangle(22.34375,76.875,-9)],True,True)
    lower=Part.makeLoft([rectangle(14,48,-65),rectangle(14,48,-43.5),rectangle(11,48,-42)],True,True)
    body=fuse([receiver,web,outer]).cut(hole.fuse(lower)).removeSplitter()
    edges=[e for e in body.Edges if e.BoundBox.ZLength>50 and abs(e.BoundBox.YMin-5.55)<1e-5 and abs(e.BoundBox.YMax-5.55)<1e-5 and abs(abs(e.CenterOfMass.x)-15)<1e-5]
    assert len(edges)==2
    body=body.makeFillet(2,edges);assert body.isValid()
    lead=Part.makeLoft([rectangle(21.79375,75.475,-10.6),rectangle(23.434375,77.4875,-9.9)],True,True)
    body=body.cut(lead).removeSplitter();assert body.isValid() and len(body.Solids)==1
    region=K.box(-60,-30,-140,120,30.15,180)
    a=receiver.common(region);b=body.common(region)
    delta=a.cut(b).Volume+b.cut(a).Volume
    assert delta<1e-7
    prior=Part.read(str(Path(__file__).resolve().parents[2]/'reviews/rectangular-tool-funnel-v2/part-rectangular-tool-funnel__v2__upright__fit-pf02c9-hoop5__installed.step'))
    style_delta=prior.cut(body).Volume+body.cut(prior).Volume
    bottoms=[f for f in body.Faces if abs(f.BoundBox.ZMin+64)<1e-6 and abs(f.BoundBox.ZMax+64)<1e-6]
    assert bottoms
    return body,receiver,info,delta,style_delta,bottoms

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);d=p.parse_args().output.resolve()
    if (d/'candidate.json').exists():raise SystemExit('Use a fresh directory')
    d.mkdir(parents=True,exist_ok=True);body,receiver,info,delta,style_delta,bottoms=build()
    report=K.export(body,d,NAME,'upright',dict(receiver=info))
    write(body.common(K.box(-100,.15,-180,200,250,300)),d/'front-material.stl',.005)
    write(receiver,d/'receiver-reference.stl')
    write(Part.makeCompound(bottoms),d/'bed-contact.stl',.005)
    doc=A.newDocument('RectangularToolFunnel');o=doc.addObject('PartDesign::Feature','Funnel');o.Shape=body
    dims=dict(top_aperture=[23.2,77.2],nominal_taper_top_aperture=[22,76],throat_aperture=[11,48],bottom_aperture=[14,48],top_z=-10,throat_z=-42,bottom_z=-64,extension_height=22,lower_transition_height=1.5,center_y=48,wall_nominal_horizontal=4,receiver_width=48.8,grid_spacing=50.8)
    o.addProperty('App::PropertyString','Dimensions').Dimensions=json.dumps(dims)
    doc.recompute();doc.saveAs(str(d/'editable.FCStd'))
    report.update(name=NAME,dimensions=dims,peg_symmetric_difference_mm3=delta,v2_styling_symmetric_difference_mm3=style_delta,bed_contact=dict(installed_z=-64,cad_face_area_mm2=sum(f.Area for f in bottoms),faces=len(bottoms)),source_sha256=sha(__file__),runtime=dict(FreeCAD=A.Version(),OCC=Part.OCC_VERSION),design='Styled simple open funnel; R2 exterior/web/root rounds and0.6 rim breaks; exact shared upright rear interface',styling=dict(exterior_corner_and_knee_radius_mm=2,exterior_corner_and_knee_edges=12,web_front_corner_radius_mm=2,web_front_corner_edges=2,web_root_radius_mm=2,web_root_edges=2,outer_rim_chamfer_mm=.6,inner_lead_axial_depth_mm=.6,inner_lead_horizontal_offset_mm=.6,bed_perimeter_not_rounded=True))
    (d/'candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    spec=dict(step=NAME+'__installed.step',h=2.,supports=['pegs'],loads=[dict(id='front-side-5N',point=[12, 74,-20],radius=5,force=[5,0,0],target=1.),dict(id='front-down-5N',point=[12,74,-20],radius=5,force=[0,0,-5],target=.5)])
    (d/(NAME+'__fea-spec.json')).write_text(json.dumps(spec,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
