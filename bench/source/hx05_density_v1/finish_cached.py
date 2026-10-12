"""Export the saved, already recomputed selected solid without repeating its union."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'.local-runtime/hx05-density-v1'
sys.path[:0]=[str(Path(__file__).parent),str(ROOT/'bench/source/matched_fans_v1'),str(ROOT/'bench/source/hx05_parametric_v1')]
import FreeCAD as A,Part,MeshPart
import hx05_density,hx05_family,hx05_parametric
ident=sys.argv[1];out=WORK/ident;doc=A.openDocument(str(next(out.glob('*_density_v1.FCStd'))))
row=next(r for r in json.loads((WORK/'genetic-check.json').read_text())['models'] if r['id']==ident)
assert all(abs(float(getattr(doc.DensityParameters,n))-v)<1e-9 for n,v in row['parameters'].items())
body=doc.StructuralHolder.Shape;core=doc.SolidInfillCore.Shape;baseline=doc.FinalHolder.Shape
assert body.isValid() and len(body.Solids)==1 and core.isValid() and not doc.StructuralHolder.LastError
assert doc.StructuralHolder.Core==doc.SolidInfillCore and doc.StructuralHolder.Mount==doc.ApprovedMount
original=hashlib.sha256(baseline.exportBrepToString().encode()).hexdigest()
reference=Part.Shape();reference.read(str(out/'body.brep'))
assert len(reference.Faces)==len(baseline.Faces)
assert abs(reference.Volume-baseline.Volume)<1e-5
def signatures(shape):
 return sorted((type(f.Surface).__name__,round(f.Area,5),tuple(round(v,5) for v in f.CenterOfMass)) for f in shape.Faces)
assert signatures(reference)==signatures(baseline),'Baseline face geometry differs'
bb=baseline.optimalBoundingBox();rb=reference.optimalBoundingBox()
assert max(abs(getattr(bb,k)-getattr(rb,k)) for k in ['XMin','XMax','YMin','YMax','ZMin','ZMax'])<1e-6
pc=json.loads((out/'check.json').read_text())['print_pose'];matrix=A.Matrix()
for i in range(3):
 for j in range(3):setattr(matrix,f'A{i+1}{j+1}',pc['rotation'][i][j])
body.exportBrep(str(out/'structural-body.brep'));core.exportBrep(str(out/'selected-core.brep'))
for name,s in [('print-structural-body',body),('print-selected-core',core)]:
 s=s.copy();s.transformShape(matrix);s.translate(A.Vector(*pc['translation']));s.exportBrep(str(out/(name+'.brep')))
 MeshPart.meshFromShape(Shape=s,LinearDeflection=.025,AngularDeflection=.1,Relative=False).write(str(out/(name+'-fine.stl')))
result=dict(id=ident,passed=True,baseline_construction_unchanged=True,baseline_shape_sha256=original,baseline_volume_mm3=baseline.Volume,structural_volume_mm3=body.Volume,selected_core_volume_mm3=core.Volume,removed_volume_percent=100*(1-body.Volume/baseline.Volume),valid_single_solid=True,parameters=row['parameters'],scope='Cached selected single solid from completed native recompute, exported without repeating union. Comparative genetic sizing; fresh print/installation/load checks pending.')
(out/'structure-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
