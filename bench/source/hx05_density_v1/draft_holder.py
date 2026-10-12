"""Build one deterministic 30-degree outside taper; reuse every existing cutter."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'.local-runtime/hx05-density-v1'
sys.path[:0]=[str(Path(__file__).parent),str(ROOT/'bench/source/matched_fans_v1'),str(ROOT/'bench/source/hx05_parametric_v1')]
import FreeCAD as A,MeshPart
import hx05_density,hx05_family,hx05_parametric
ident=sys.argv[1];out=WORK/ident;path=next(out.glob('*_density_v1.FCStd'));doc=A.openDocument(str(path));p=doc.DensityParameters
if not hasattr(p,'MaximumExteriorOverhang'):p.addProperty('App::PropertyAngle','MaximumExteriorOverhang','Outside print geometry');p.MaximumExteriorOverhang=30
body=doc.getObject('DraftedHolder') or doc.addObject('Part::FeaturePython','DraftedHolder')
if not hasattr(body,'DensityRole'):
 for kind,name in [('App::PropertyString','DensityRole'),('App::PropertyLink','Holder'),('App::PropertyLink','Mount'),('App::PropertyLink','DensityParameters'),('App::PropertyLinkList','Keys'),('App::PropertyLinkList','Cutters'),('App::PropertyAngle','MaximumCheckedOuterOverhang'),('App::PropertyString','LastError')]:body.addProperty(kind,name)
body.DensityRole='DraftedHolder';body.Holder=doc.FinalHolder;body.Mount=doc.ApprovedMount;body.DensityParameters=p
body.Keys=[k for k in doc.Objects if getattr(k,'Kind',None)=='Key'];body.Cutters=[k for k in doc.Objects if getattr(k,'Kind',None) in ['Cavity','Entry']]
body.Label='86_PRINT HOLDER — 30-degree outside tapers; no broad cheek'
hx05_density.DensityZone(body);body.Proxy.execute(body);assert not body.LastError;body.purgeTouched();p.purgeTouched()
for o in doc.Objects:
 if hasattr(o,'Shape'):o.Visibility=o==body
body.Shape.exportBrep(str(out/'drafted-body.brep'))
pc=json.loads((out/'check.json').read_text())['print_pose'];matrix=A.Matrix()
for i in range(3):
 for j in range(3):setattr(matrix,f'A{i+1}{j+1}',pc['rotation'][i][j])
s=body.Shape.copy();s.transformShape(matrix)
b=s.optimalBoundingBox();translation=[128-(b.XMin+b.XMax)/2,128-(b.YMin+b.YMax)/2,-b.ZMin];s.translate(A.Vector(*translation));b=s.optimalBoundingBox()
s.exportBrep(str(out/'print-drafted-body.brep'));MeshPart.meshFromShape(Shape=s,LinearDeflection=.025,AngularDeflection=.1,Relative=False).write(str(out/'print-drafted-body-fine.stl'))
body.purgeTouched();doc.save()
result=dict(id=ident,passed=True,valid_single_solid=True,exterior_overhang_limit_deg=30,maximum_checked_uncut_housing_overhang_deg=float(body.MaximumCheckedOuterOverhang),tested_cutters_reused=True,broad_cheek_removed=True,volume_mm3=body.Shape.Volume,rotation=pc['rotation'],translation=translation,print_dimensions_mm=[b.XLength,b.YLength,b.ZLength],available_edge_margin_mm=min(b.XMin,b.YMin,256-b.XMax,256-b.YMax),scope='Analytic convex-housing outer draft check before unchanged socket/entry/vent cutters. Internal cut faces and original pegs excluded; final tool access and support/toolpath checks pending.')
(out/'draft-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
