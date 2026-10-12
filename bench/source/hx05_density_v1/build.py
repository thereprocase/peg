"""Add independent editable helper volumes; preserve every existing holder feature."""
from pathlib import Path
import sys,json,hashlib,math,time
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(Path(__file__).parent),str(ROOT/'bench/source/matched_fans_v1'),str(ROOT/'bench/source/hx05_parametric_v1')]
import FreeCAD as App,Part,MeshPart
import hx05_family,hx05_parametric,hx05_density
V=App.Vector
ident=sys.argv[1];out=ROOT/'.local-runtime/hx05-density-v1'/ident;out.mkdir(parents=True,exist_ok=True)
number={'HX05A':'33034','HX05B':'13189','HX05C':'13190'}[ident]
source=(ROOT/'.local-runtime/hx05-parametric-v1/bundle/HX05C_13190_parametric_v1.FCStd') if ident=='HX05C' else ROOT/f'.local-runtime/matched-fans-v1/bundle/{ident}_{number}_matched_v1.FCStd'
layout=json.loads((ROOT/'.local-runtime/matched-fans-v1/layout.json').read_text());rack=next(r for r in layout['racks'] if r['id']==ident)
print(ident,'open',flush=True);doc=App.openDocument(str(source));body=doc.getObject('FinalHolder');native=body.Shape
original=hashlib.sha256(native.exportBrepToString().encode()).hexdigest()
params=doc.addObject('App::FeaturePython','DensityParameters');params.Label='80_Density parameters — geometry helpers + slicer intent'
for name,default in [('FoundationDepth',3.),('PegRootRadius',7.5),('RootDepth',8.),('CollectorHeight',10.),('RibWidth',3.),('RootWidth',9.),('RootFanout',9.)]:
 params.addProperty('App::PropertyLength',name,'Helper geometry');setattr(params,name,default)
params.addProperty('App::PropertyPercent','BaseInfill','Slicer intent');params.BaseInfill=12
params.addProperty('App::PropertyPercent','HelperInfill','Slicer intent');params.HelperInfill=100;params.setEditorMode('HelperInfill',1)
params.addProperty('App::PropertyInteger','WallLoops','Slicer intent');params.WallLoops=4
mount=doc.getObject('ApprovedMount');bb=mount.Shape.optimalBoundingBox()
# Original grids are on the 25.4 mm pitch; no peg geometry is modified.
columns=[25.4*i for i in range(-20,21) if bb.XMin+6<=25.4*i<=bb.XMax-6]
if len(columns)%2==0:columns=[c+12.7 for c in columns if bb.XMin+6<=c+12.7<=bb.XMax-6]
rows=[-25.4*i for i in range(20) if -25.4*i-6>=float(doc.Parameters.PlateBottom)]
group=doc.addObject('App::DocumentObjectGroup','DensityHelpers');group.Label='81_RAW modifier construction — not printable parts'
keys=[obj for obj in doc.Objects if getattr(obj,'Kind',None)=='Key']
helpers=[]
for role in ['Foundation','Mounts','Sockets','Ribs']:
 obj=doc.addObject('Part::FeaturePython','Dense'+role);obj.Label=role+' — 100% infill helper envelope'
 obj.addProperty('App::PropertyString','DensityRole');obj.DensityRole=role;obj.setEditorMode('DensityRole',1)
 obj.addProperty('App::PropertyLink','Holder');obj.Holder=body
 obj.addProperty('App::PropertyLink','Mount');obj.Mount=mount
 obj.addProperty('App::PropertyLink','DensityParameters');obj.DensityParameters=params
 obj.addProperty('App::PropertyLinkList','Keys');obj.Keys=keys
 obj.addProperty('App::PropertyFloatList','PegColumns');obj.PegColumns=columns
 obj.addProperty('App::PropertyFloatList','PegRows');obj.PegRows=rows
 obj.addProperty('App::PropertyString','LastError')
 hx05_density.DensityZone(obj);group.addObject(obj);helpers.append(obj)
core=doc.addObject('Part::FeaturePython','SolidInfillCore');core.Label='82_MODIFIER — clipped strategic solid core (100% infill)'
for kind,name in [('App::PropertyString','DensityRole'),('App::PropertyLink','Holder'),('App::PropertyLink','DensityParameters'),('App::PropertyLinkList','Helpers'),('App::PropertyString','LastError'),('App::PropertyVolume','ZoneVolume'),('App::PropertyFloat','BodyVolumeFraction')]:core.addProperty(kind,name)
core.DensityRole='SolidCore';core.Holder=body;core.DensityParameters=params;core.Helpers=helpers;hx05_density.DensityZone(core)
print(ident,'recompute modifiers',flush=True);doc.recompute()
for obj in helpers+[core]:print(obj.Name,obj.State,obj.LastError,flush=True)
assert not core.Shape.isNull() and core.Shape.isValid()
assert hashlib.sha256(body.Shape.exportBrepToString().encode()).hexdigest()==original,'Holder shape changed'
assert all(not obj.LastError for obj in helpers+[core])
for o in helpers:o.Visibility=False
body.Visibility=True;core.Visibility=False
readme=doc.getObject('START_HERE');readme.Text+='\n\nDENSITY OVERLAY: outer holder, fits and mounts are unchanged. Edit 80_Density parameters; F5 rebuilds helper volumes. SolidInfillCore is a SLICER MODIFIER, not another physical part. Load the supplied 3MF as an Orca project: body 12% infill / four walls, core 100%. Select your actual P1S/filament profile and supports; review bed clearance and slicing. HelperInfill metadata does not change FreeCAD material. Do not merge the core into an ordinary printable STL. Density changes are not load-qualified.\n'
path=out/f'{ident}_{number}_density_v1.FCStd';doc.saveAs(str(path));body.Shape.exportBrep(str(out/'body.brep'));core.Shape.exportBrep(str(out/'solid-core.brep'))
for name,shape in [('body',body.Shape),('solid-core',core.Shape)]:
 MeshPart.meshFromShape(Shape=shape,LinearDeflection=.1,AngularDeflection=.25,Relative=False).write(str(out/(name+'.stl')))
# Use the exact checked nominal print placement, equally for body and modifier.
check=ROOT/'bench/reviews/matched-fans-v1'/ident/'print-check.json'
if ident=='HX05C':check=ROOT/'bench/reviews/green-fan-v1/print-check.json'
pc=json.loads(check.read_text());matrix=App.Matrix()
for i in range(3):
 for j in range(3):setattr(matrix,f'A{i+1}{j+1}',pc['rotation'][i][j])
for name,shape in [('print-body',body.Shape),('print-solid-core',core.Shape)]:
 s=shape.copy();s.transformShape(matrix);s.translate(V(*pc['translation']));assert s.isValid()
 MeshPart.meshFromShape(Shape=s,LinearDeflection=.1,AngularDeflection=.25,Relative=False).write(str(out/(name+'.stl')))
 s.exportBrep(str(out/(name+'.brep')))
receipt=dict(id=ident,set=number,passed=True,body_shape_sha256=original,holder_unchanged=True,body_volume_mm3=body.Shape.Volume,modifier_volume_mm3=core.Shape.Volume,solid_core_percent=core.BodyVolumeFraction,base_infill_percent=12,modifier_infill_percent=100,wall_loops=4,print_pose=pc,columns_mm=columns,rows_mm=rows,helper_roles=[obj.DensityRole for obj in helpers],scope='Native helper-volume and unchanged-holder checks. Density-core structure not FEA/load qualified; actual profile/support slicing pending.')
(out/'check.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k not in ['print_pose']},indent=2),flush=True)
