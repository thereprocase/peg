"""Remove rear peg detail only from the comparison mesh, preserving deliverable CAD."""
from pathlib import Path
import FreeCAD as A,Part,MeshPart,json
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'.local-runtime/hx05-density-v1'
for ident in ['HX05C','HX05B','HX05A']:
 out=WORK/ident;s=Part.Shape();s.read(str(out/'drafted-body.brep'))
 front=s.common(Part.makeBox(1000,500,1000,A.Vector(-500,0,-500)));assert front.isValid() and len(front.Solids)==1
 front.exportBrep(str(out/'fea-front-domain.brep'))
 MeshPart.meshFromShape(Shape=front,LinearDeflection=.025,AngularDeflection=.1,Relative=False).write(str(out/'fea-front-domain.stl'))
 result=dict(id=ident,native_volume_mm3=s.Volume,front_domain_volume_mm3=front.Volume,scope='Analysis domain y>=0. Rear peg deformation/contact excluded. Peg-root boundary patches and whole-back-face bound will be compared; full manufacturing CAD unchanged.')
 (out/'fea-domain-check.json').write_text(json.dumps(result,indent=2)+'\n');print(ident,'front domain exported',flush=True)
