"""Exercise saved proxies and a helper parameter edit without changing the holder."""
from pathlib import Path
import sys, hashlib, json
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(Path(__file__).parent),str(ROOT/'bench/source/matched_fans_v1'),str(ROOT/'bench/source/hx05_parametric_v1')]
import FreeCAD as App
import hx05_density, hx05_family, hx05_parametric
ident=sys.argv[1]
out=ROOT/'.local-runtime/hx05-density-v1'/ident
path=next(out.glob('*_density_v1.FCStd'))
doc=App.openDocument(str(path))
body=doc.FinalHolder
digest=lambda:hashlib.sha256(body.Shape.exportBrepToString().encode()).hexdigest()
before=digest()
core=doc.SolidInfillCore
assert isinstance(core.Proxy,hx05_density.DensityZone)
initial=core.Shape.Volume
default=float(doc.DensityParameters.RibWidth)
doc.DensityParameters.RibWidth=default+.5
doc.recompute()
assert core.Shape.isValid() and not core.LastError
if hasattr(doc,'StructuralHolder'):assert doc.StructuralHolder.Shape.isValid() and len(doc.StructuralHolder.Shape.Solids)==1
assert core.Shape.Volume>initial and digest()==before
edited=core.Shape.Volume
doc.DensityParameters.RibWidth=default
doc.recompute()
assert abs(core.Shape.Volume-initial)<.01 and digest()==before
result=dict(passed=True,id=ident,proxy_restored=True,parameter='RibWidth',default_mm=default,edited_mm=default+.5,
            default_core_volume_mm3=initial,edited_core_volume_mm3=edited,holder_unchanged=True,
            scope='Fresh-process native reopen and helper edit/reset; Windows GUI first-open not tested.')
(out/'edit-check.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result),flush=True)
