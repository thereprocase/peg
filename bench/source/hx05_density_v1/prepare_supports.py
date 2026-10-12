"""Add editable bore support exclusions, retaining holder and density-core shapes."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(Path(__file__).parent),str(ROOT/'bench/source/matched_fans_v1'),str(ROOT/'bench/source/hx05_parametric_v1')]
import FreeCAD as A, Part, MeshPart
import hx05_density,hx05_family,hx05_parametric
WORK=ROOT/'.local-runtime/hx05-density-v1'
for ident,num in [('HX05C','13190'),('HX05B','13189'),('HX05A','33034')]:
 out=WORK/ident;path=out/f'{ident}_{num}_density_v1.FCStd';doc=A.openDocument(str(path))
 digest=lambda s:hashlib.sha256(s.exportBrepToString().encode()).hexdigest()
 before=digest(doc.FinalHolder.Shape);core=digest(doc.SolidInfillCore.Shape)
 obj=doc.getObject('SocketSupportBlocker') or doc.addObject('Part::FeaturePython','SocketSupportBlocker')
 obj.Label='83_SUPPORT BLOCKER — sockets and entrances (not material)'
 if not hasattr(obj,'DensityRole'):
  for kind,name in [('App::PropertyString','DensityRole'),('App::PropertyLink','Holder'),('App::PropertyLink','DensityParameters'),('App::PropertyLinkList','Keys'),('App::PropertyString','LastError')]:obj.addProperty(kind,name)
 obj.DensityRole='SupportBlocker';obj.Holder=doc.FinalHolder;obj.DensityParameters=doc.DensityParameters
 obj.Keys=[k for k in doc.Objects if getattr(k,'Kind',None)=='Key'];hx05_density.DensityZone(obj)
 doc.recompute();assert obj.Shape.isValid() and not obj.LastError
 assert digest(doc.FinalHolder.Shape)==before and digest(doc.SolidInfillCore.Shape)==core
 obj.Visibility=False;doc.save()
 pc=json.loads((out/'check.json').read_text())['print_pose'];matrix=A.Matrix()
 for i in range(3):
  for j in range(3):setattr(matrix,f'A{i+1}{j+1}',pc['rotation'][i][j])
 s=obj.Shape.copy();s.transformShape(matrix);s.translate(A.Vector(*pc['translation']))
 MeshPart.meshFromShape(Shape=s,LinearDeflection=.025,AngularDeflection=.1,Relative=False).write(str(out/'print-support-blocker.stl'))
 (out/'support-blocker-check.json').write_text(json.dumps(dict(passed=True,id=ident,holder_unchanged=True,core_unchanged=True,blocker_count=len(obj.Keys),skin_overlap_mm=.15,entrance_extension_mm=5,scope='Editable support exclusion only; socket roofs must bridge without internal supports. Toolpath review still required.'),indent=2)+'\n')
 print(ident,'support exclusions exported',flush=True)
 A.closeDocument(doc.Name)
