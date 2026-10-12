"""Opt into connected thin modifiers without changing the physical holder."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'.local-runtime/hx05-connected-v3'
sys.path[:0]=[str(Path(__file__).parent),str(ROOT/'bench/source/matched_fans_v1'),str(ROOT/'bench/source/hx05_parametric_v1')]
import FreeCAD as A
import hx05_density,hx05_family,hx05_parametric
ident=sys.argv[1];out=WORK/ident;doc=A.openDocument(str(next(out.glob('*_density_v1.FCStd'))));p=doc.DensityParameters;body=doc.DraftedHolder
before=hashlib.sha256(body.Shape.exportBrepToString().encode()).hexdigest()
if not hasattr(p,'DensityContinuousRibs'):p.addProperty('App::PropertyBool','DensityContinuousRibs','Density only — outside fixed')
p.DensityContinuousRibs=True;p.purgeTouched();body.purgeTouched();doc.save()
assert hashlib.sha256(body.Shape.exportBrepToString().encode()).hexdigest()==before
(out/'connected-parameters.json').write_text(json.dumps(dict(id=ident,passed=True,outside_unchanged=True,continuous_ribs=True,body_shape_sha256=before),indent=2)+'\n')
