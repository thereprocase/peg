"""Separate density-only parameters; keep the outside construction unchanged."""
from pathlib import Path
import sys,hashlib,json
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'.local-runtime/hx05-light-v2'
sys.path[:0]=[str(Path(__file__).parent),str(ROOT/'bench/source/matched_fans_v1'),str(ROOT/'bench/source/hx05_parametric_v1')]
import FreeCAD as A
import hx05_density,hx05_family,hx05_parametric
ident=sys.argv[1];out=WORK/ident;path=next(out.glob('*_density_v1.FCStd'));doc=A.openDocument(str(path));body=doc.DraftedHolder
before=hashlib.sha256(body.Shape.exportBrepToString().encode()).hexdigest();p=doc.DensityParameters
values=dict(DensityFoundationDepth=1.6,DensityPegRootRadius=5.5,DensityRootDepth=8.,DensityCollectorHeight=8.,DensityRibWidth=1.2,DensityRootWidth=2.5,DensityRootFanout=4.,DensitySocketSkin=1.2)
for name,val in values.items():
 if not hasattr(p,name):p.addProperty('App::PropertyLength',name,'Density only — outside fixed')
 setattr(p,name,val)
p.BaseInfill=5;p.WallLoops=3
# Earlier cut-back constructions are history, not dependencies of DraftedHolder.
# Keep their cached solids without recomputing them using the new thin masks.
for name in ['SolidInfillCore','StructuralHolder','PrintInfillCore']:
 old=doc.getObject(name)
 if old:
  old.Proxy=None
  if not hasattr(old,'FrozenHistory'):old.addProperty('App::PropertyBool','FrozenHistory','History')
  old.FrozenHistory=True;old.setEditorMode('FrozenHistory',1);old.purgeTouched()
doc.START_HERE.Text+='\nLIGHT V2: edit the Density only — outside fixed group for internal reinforcement. Bulk: 5% gyroid, three continuous walls; four 100% masks. Original RibWidth/RootWidth control outside construction. FrozenHistory objects are cached earlier designs; do not restore their proxies.\n'
p.purgeTouched();body.purgeTouched();doc.save()
assert hashlib.sha256(body.Shape.exportBrepToString().encode()).hexdigest()==before
(out/'light-parameters.json').write_text(json.dumps(dict(id=ident,passed=True,outside_unchanged=True,body_shape_sha256=before,base_infill_percent=5,wall_loops=3,parameters=values),indent=2)+'\n')
print(ident,'Density-only light parameters saved',flush=True)
