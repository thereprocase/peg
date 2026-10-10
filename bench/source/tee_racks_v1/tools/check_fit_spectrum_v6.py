"""Reload and verify the delivered angle-matched spectrum meshes and CAD."""
import FreeCAD as A
import Part,Mesh,hashlib,json,sys,math,re
from pathlib import Path
p=Path(sys.argv[1]);r=json.loads((p/'fit-v6-check.json').read_text());source=Path(__file__).resolve().parents[1]/'fit_spectrum_v6.py';assert hashlib.sha256(source.read_bytes()).hexdigest()==r['source_sha256']
assert r['orientation_source_sha256']==hashlib.sha256((source.parent/'fan_orientation_v6.json').read_bytes()).hexdigest()
checks=[]
for prefix,count in [(f'HX05-fit-v6-{size}mm__fan-angle__print',1) for size in (3,5,7)]+[('HX05-fit-v6__three-spectra__print',3)]:
 s=Part.Shape();s.read(str(p/(prefix+'.step')));m=Mesh.Mesh(str(p/(prefix+'.stl')))
 assert s.isValid() and len(s.Solids)==count and m.isSolid() and m.countComponents()==count
 assert not m.hasInvalidPoints() and not m.hasInvalidNeighbourhood()
 assert abs(m.Volume-s.Volume)/s.Volume<.005 and abs(s.BoundBox.ZMin)<1e-7
 checks.append(dict(part=prefix,native_solids=count,mesh_components=count,closed_mesh=True,volume_error=abs(m.Volume-s.Volume)/s.Volume))
 if count==1:
  size=int(re.search(r'fit-v6-(\d+)mm',prefix).group(1));q=next(q for q in r['coupons'] if q['size_mm']==size);axis=A.Vector(*q['shaft_print'])
  assert q['fan_frame_match']
  for slot in q['slots']:
   point=A.Vector(*slot['vent_outer_point_print_mm']);vent=Part.makeCylinder(.49,3,point,axis)
   assert s.common(vent).Volume<1e-7
 if count==3:total=s.Volume
 d=A.openDocument(str(p/'HX05-fit-v6.FCStd')) if count==3 else None
 if d:
  assert len(d.Objects)==3 and all(o.Shape.isValid() and len(o.Shape.Solids)==1 for o in d.Objects)
  assert abs(sum(o.Shape.Volume for o in d.Objects)-total)<1e-6
  assert max(o.Shape.BoundBox.YMax for o in d.Objects)>100 # all three laid out, not overlapping at origin
  A.closeDocument(d.Name)
result=dict(checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),native_and_mesh_exports=checks,freecad_document_matches_combined_step=True,scope='Geometry only; owner-profile slicing, print submission and physical fit pending')
(p/'export-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
