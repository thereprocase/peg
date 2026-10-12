"""Separate outside sleeve/rib volumes from internal peg-root density masks."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'.local-runtime/hx05-density-v1'
sys.path[:0]=[str(Path(__file__).parent),str(ROOT/'bench/source/matched_fans_v1'),str(ROOT/'bench/source/hx05_parametric_v1')]
import FreeCAD as A,Part,MeshPart
import hx05_density,hx05_family,hx05_parametric
ident=sys.argv[1];out=WORK/ident;path=next(out.glob('*_density_v1.FCStd'));doc=A.openDocument(str(path))
body=doc.StructuralHolder
if not hasattr(body,'EnvelopeParts'):body.addProperty('App::PropertyLinkList','EnvelopeParts')
body.EnvelopeParts=[doc.DenseFoundation,doc.DenseSockets,doc.DenseRibs];hx05_density.DensityZone(body)
body.Proxy.execute(body);assert not body.LastError and body.Shape.isValid() and len(body.Shape.Solids)==1;body.purgeTouched()
core=doc.getObject('PrintInfillCore') or doc.addObject('Part::FeaturePython','PrintInfillCore')
if not hasattr(core,'DensityRole'):
 for kind,name in [('App::PropertyString','DensityRole'),('App::PropertyLink','Holder'),('App::PropertyLink','Core'),('App::PropertyLink','DensityParameters'),('App::PropertyString','LastError')]:core.addProperty(kind,name)
core.DensityRole='PrintCore';core.Holder=body;core.Core=doc.SolidInfillCore;core.DensityParameters=doc.DensityParameters;hx05_density.DensityZone(core);core.Proxy.execute(core);assert core.Shape.isValid();core.purgeTouched()
body.Label='84_PRINT HOLDER — connected sleeves/ribs/foundation';body.purgeTouched()
core.Label='85_MODIFIER — 100% core clipped to current print holder';core.purgeTouched()
doc.SolidInfillCore.Label='82_DENSE CONSTRUCTION ENVELOPE — clipped again at 85';doc.SolidInfillCore.purgeTouched()
for o in doc.Objects:
 if hasattr(o,'Shape'):o.Visibility=o==body
old=doc.START_HERE.Text.split('\n\nDENSITY OVERLAY:',1)[0]
doc.START_HERE.Text='CURRENT STRUCTURAL REVIEW: print 84_StructuralHolder. 85_PrintInfillCore is the 100% Orca modifier; 83_SocketSupportBlocker is a nonphysical support exclusion. The original FinalHolder is a hidden construction envelope. Edit 80_Density parameters and F5. Print and loads need review.\n\nHISTORICAL BASE MODEL INSTRUCTIONS:\n'+old
doc.save();print(ident,'clean envelope saved',flush=True)
pc=json.loads((out/'check.json').read_text())['print_pose'];matrix=A.Matrix()
for i in range(3):
 for j in range(3):setattr(matrix,f'A{i+1}{j+1}',pc['rotation'][i][j])
body.Shape.exportBrep(str(out/'structural-body.brep'));core.Shape.exportBrep(str(out/'selected-core.brep'))
for name,s in [('print-structural-body',body.Shape),('print-selected-core',core.Shape)]:
 s=s.copy();s.transformShape(matrix);s.translate(A.Vector(*pc['translation']));s.exportBrep(str(out/(name+'.brep')))
 MeshPart.meshFromShape(Shape=s,LinearDeflection=.025,AngularDeflection=.1,Relative=False).write(str(out/(name+'-fine.stl')))
 baseline=doc.FinalHolder.Shape
result=dict(id=ident,passed=True,baseline_volume_mm3=baseline.Volume,structural_volume_mm3=body.Shape.Volume,selected_core_volume_mm3=core.Shape.Volume,removed_volume_percent=100*(1-body.Shape.Volume/baseline.Volume),valid_single_solid=True,density_masks_excluded_from_outer_envelope=True,scope='Clean cut-back review candidate. Sleeve/rib/foundation envelope plus unchanged approved receiver. Root masks clipped to this part; fresh slice and load checks pending.')
(out/'structure-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
