"""Export four nonphysical 100% masks in the locked approved print pose."""
from pathlib import Path
import sys, json, hashlib, os
ROOT=Path(__file__).resolve().parents[3]
WORK=Path(os.environ.get('HX05_BUILD_DIR',str(ROOT/'.local-runtime/hx05-density-v1')))
sys.path[:0]=[str(Path(__file__).parent),str(ROOT/'bench/source/matched_fans_v1'),str(ROOT/'bench/source/hx05_parametric_v1')]
import FreeCAD as A, Part, MeshPart
import hx05_density, hx05_family, hx05_parametric

ident=sys.argv[1];out=WORK/ident
path=next(out.glob('*_density_v1.FCStd'))
doc=A.openDocument(str(path));body=doc.DraftedHolder
before=hashlib.sha256(body.Shape.exportBrepToString().encode()).hexdigest()
pose=json.loads((out/'draft-check.json').read_text())
matrix=A.Matrix()
for i in range(3):
 for j in range(3):setattr(matrix,f'A{i+1}{j+1}',pose['rotation'][i][j])
def placed(shape):
 s=shape.copy();s.transformShape(matrix);s.translate(A.Vector(*pose['translation']));return s
print_body=placed(body.Shape);box=print_body.optimalBoundingBox()
crop=Part.makeBox(box.XLength+4,box.YLength+4,box.ZMax,A.Vector(box.XMin-2,box.YMin-2,0))
checks=[]
for role in ['Foundation','Mounts','Sockets','Ribs']:
 obj=doc.getObject('Dense'+role)
 obj.Holder=body
 obj.Proxy.execute(obj);obj.purgeTouched()
 raw=placed(obj.Shape).common(crop)
 assert raw.isValid() and raw.Volume>0,(ident,role,'Invalid raw modifier')
 raw.exportBrep(str(out/('print-modifier-'+role.lower()+'.brep')))
 mesh=MeshPart.meshFromShape(Shape=raw,LinearDeflection=.025,AngularDeflection=.1,Relative=False)
 mesh.write(str(out/('print-modifier-'+role.lower()+'.stl')))
 checks.append(dict(role=role,subtype='modifier_part',infill_percent=100,raw_volume_mm3=raw.Volume,solids=len(raw.Solids),valid=True))
 print(ident,role,'exported',flush=True)
# The support blocker shares exactly the same transform, with no physical union.
blocker=doc.SocketSupportBlocker
placed(blocker.Shape).exportBrep(str(out/'print-drafted-support-blocker.brep'))
MeshPart.meshFromShape(Shape=placed(blocker.Shape),LinearDeflection=.025,AngularDeflection=.1,Relative=False).write(str(out/'print-drafted-support-blocker.stl'))
assert hashlib.sha256(body.Shape.exportBrepToString().encode()).hexdigest()==before,'Outside shape changed'
for o in doc.Objects:
 if hasattr(o,'Shape'):o.Visibility=o==body
doc.START_HERE.Text=('CURRENT PRINT PART: 86 DraftedHolder. Approved outside tapers and tested fits are unchanged. '
 'The chosen bed face and its print rotation are locked. DensityHelpers contains four independent, nonphysical '
 '100% infill masks: Foundation, Mounts, Sockets, Ribs. The raw masks may protrude through air as slicer selection '
 'handles. They are modifier parts, never printable material. Do not fuse them into DraftedHolder. '
 'The older clipped cores and StructuralHolder are history. Edit DensityParameters for helper dimensions; '
 'RibWidth/RootWidth also control outside construction, so changing them invalidates the approved outside geometry. '
 'No current physical load rating. Actual printer-profile and support/toolpath review is separate.')
body.purgeTouched();doc.save()
receipt=dict(id=ident,passed=True,body_shape_unchanged=True,body_shape_sha256=before,print_rotation_unchanged=True,rotation=pose['rotation'],translation=pose['translation'],modifier_count=4,modifiers=checks,scope='Native mask export only. Masks clipped to the build volume to preserve bed contact; no manufacturing geometry or fits changed. Mesh and Orca verification remain separate.')
(out/'modifiers-check.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(ident,'modifier native checks passed',flush=True)
