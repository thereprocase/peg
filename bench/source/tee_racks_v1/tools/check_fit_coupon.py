"""Verify exported straight-guide coupon files with the local FreeCAD runtime."""
import hashlib,json,sys
from pathlib import Path
import FreeCAD as A
import Mesh,Part
p=Path(sys.argv[1]);report=json.loads((p/'fit-v2-check.json').read_text())
source=Path(__file__).resolve().parents[1]/'fit_coupon_v2.py'
assert report['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
m=Mesh.Mesh(str(p/'HX05-fit-v2__left-end__print.stl'))
assert m.isSolid() and m.Volume>0 and m.countComponents()==3
assert not m.hasInvalidPoints() and not m.hasInvalidNeighbourhood()
s=Part.Shape();s.read(str(p/'HX05-fit-v2__left-end__print.step'))
assert s.isValid() and len(s.Solids)==3
assert abs(m.Volume-s.Volume)/s.Volume<.005
for q in report['pieces']:
 assert q['native_valid'] and q['native_solids']==1
 assert q['clearance_per_flat_mm']==.1 and q['bore_af_mm']==q['af_mm']+.2
 assert q['collision_at_30_deg_mm3']>0 and q['floor_probe_mm']==3
s5=next(q for q in report['pieces'] if q['tool']=='T5')
assert s5['bore_af_mm']==5.2 and abs(s5['straight_guide_mm']-19.2)<1e-8
# Reload the delivered FreeCAD document as well as the STEP and mesh.
doc=A.openDocument(str(p/'HX05-fit-v2.FCStd'))
objects=[o for o in doc.Objects if hasattr(o,'Shape')]
assert len(objects)==3 and all(o.Shape.isValid() and len(o.Shape.Solids)==1 for o in objects)
A.closeDocument(doc.Name)
checks=dict(native_step_valid=True,step_solids=len(s.Solids),freecad_document_solids=3,closed_mesh=m.isSolid(),mesh_components=m.countComponents(),mesh_positive_volume=m.Volume>0,mesh_volume_mm3=m.Volume,step_volume_mm3=s.Volume,mesh_step_relative_volume_error=abs(m.Volume-s.Volume)/s.Volume,files={name:hashlib.sha256((p/name).read_bytes()).hexdigest() for name in ('HX05-fit-v2.FCStd','HX05-fit-v2__left-end__print.stl','HX05-fit-v2__left-end__print.step')},checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='native and export geometry checks; actual slicing and physical fit pending')
(p/'export-check.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
