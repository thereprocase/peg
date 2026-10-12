"""Build only the selected structural envelope; preserve approved receiver and fits."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'.local-runtime/hx05-density-v1'
sys.path[:0]=[str(Path(__file__).parent),str(ROOT/'bench/source/matched_fans_v1'),str(ROOT/'bench/source/hx05_parametric_v1')]
import FreeCAD as A,Part,MeshPart
import hx05_density,hx05_family,hx05_parametric
selected=json.loads((WORK/'genetic-check.json').read_text())
for row in selected['models']:
 if len(sys.argv)>1 and row['id']!=sys.argv[1]:continue
 ident=row['id'];out=WORK/ident;path=next(out.glob('*_density_v1.FCStd'));doc=A.openDocument(str(path));baseline=doc.FinalHolder.Shape
 digest=lambda s:hashlib.sha256(s.exportBrepToString().encode()).hexdigest()
 original=digest(baseline)
 for name,value in row['parameters'].items():
  if abs(float(getattr(doc.DensityParameters,name))-value)>1e-9:setattr(doc.DensityParameters,name,value)
 doc.recompute();core=doc.SolidInfillCore.Shape;assert core.isValid()
 doc.save()  # Retain selected helper shapes before the final native union.
 print(ident,'selected helpers cached; union with approved receiver',flush=True)
 # The original filled model remains an editable, hidden construction envelope.
 # Keep the full approved receiver plate; roots and sleeve/rib/foundation structure
 # come from the selected core. Clipping excludes all existing bores and vents.
 # Core was already intersected with the baseline. The unchanged receiver is
 # an original baseline constituent; another intersection is redundant.
 cached=doc.getObject('StructuralHolder')
 structural=cached.Shape if cached and cached.Shape.isValid() and not cached.LastError else core.fuse(doc.ApprovedMount.Shape)
 print(ident,'union complete',flush=True)
 assert structural.isValid() and len(structural.Solids)==1,(ident,'Disconnected or invalid trimmed structure',len(structural.Solids))
 body=doc.getObject('StructuralHolder') or doc.addObject('Part::FeaturePython','StructuralHolder')
 body.Label='84_PRINT HOLDER — trimmed structural envelope'
 if not hasattr(body,'DensityRole'):
  for kind,name in [('App::PropertyString','DensityRole'),('App::PropertyLink','Holder'),('App::PropertyLink','Mount'),('App::PropertyLink','DensityParameters'),('App::PropertyLink','Core'),('App::PropertyString','LastError')]:body.addProperty(kind,name)
 body.DensityRole='StructuralHolder';body.Holder=doc.FinalHolder;body.Mount=doc.ApprovedMount;body.Core=doc.SolidInfillCore;body.DensityParameters=doc.DensityParameters;hx05_density.DensityZone(body);body.Shape=structural;body.purgeTouched()
 assert digest(doc.FinalHolder.Shape)==original
 doc.FinalHolder.Visibility=False;body.Visibility=True;doc.SolidInfillCore.Visibility=False
 doc.START_HERE.Text+='\nCURRENT PRINT PART: StructuralHolder (84), trimmed from the previous filled envelope. FinalHolder is now a hidden historical construction input. Sleeve and receiver geometry are retained; the selected ribs and print foundation form the new outside. SocketSupportBlocker is a nonphysical slicer exclusion. Edit 80_Density parameters, F5. The changed structure has no load rating.\n'
 doc.save()
 pc=json.loads((out/'check.json').read_text())['print_pose'];matrix=A.Matrix()
 for i in range(3):
  for j in range(3):setattr(matrix,f'A{i+1}{j+1}',pc['rotation'][i][j])
 structural.exportBrep(str(out/'structural-body.brep'));core.exportBrep(str(out/'selected-core.brep'))
 for name,s in [('print-structural-body',structural),('print-selected-core',core)]:
  s=s.copy();s.transformShape(matrix);s.translate(A.Vector(*pc['translation']));s.exportBrep(str(out/(name+'.brep')))
  MeshPart.meshFromShape(Shape=s,LinearDeflection=.025,AngularDeflection=.1,Relative=False).write(str(out/(name+'-fine.stl')))
 result=dict(id=ident,passed=True,baseline_construction_unchanged=True,baseline_shape_sha256=original,baseline_volume_mm3=baseline.Volume,structural_volume_mm3=structural.Volume,selected_core_volume_mm3=core.Volume,removed_volume_percent=100*(1-structural.Volume/baseline.Volume),valid_single_solid=True,parameters=row['parameters'],scope='Selected structural-envelope candidate. Subset of approved baseline preserves clearances and receiver geometry; changed holder needs fresh print, installation and load checks. Genetic surrogate is comparative only.')
 (out/'structure-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True);A.closeDocument(doc.Name)
