"""Second fresh process: verify persisted edits and live restored generators."""
from pathlib import Path
import sys,json
import FreeCAD as A
sys.path.insert(0,sys.argv[1]);import hx05_parametric as H
out=Path(sys.argv[2]);r=json.loads((out/'edit-check.json').read_text());d=A.openDocument(str(out/'EDIT_TEST.FCStd'))
assert all(isinstance(o.Proxy,H.Generator) for o in d.Objects if hasattr(o,'Kind'))
assert abs(d.Parameters.AFClearance.Value-.48)<1e-9
assert abs(d.Key_3_32.GuideLength.Value-65)<1e-9
assert abs(d.Key_3_8.UpAngle.Value-11.5)<1e-9
assert d.FinalHolder.Shape.isValid() and len(d.FinalHolder.Shape.Solids)==1
assert abs(d.FinalHolder.Shape.Volume-r['edited_volume_mm3'])<1e-5
# A restored feature must execute new code, not just display its saved shape.
k=d.Key_3_8;k.Proxy.execute(k)
assert k.LastError=='' and k.Shape.isValid()
r['second_process_reopen_passed']=True;r['restored_generator_execute_passed']=True
(out/'edit-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
