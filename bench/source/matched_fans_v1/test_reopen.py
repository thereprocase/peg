from pathlib import Path
import sys,json
import FreeCAD as A
import hx05_family as H
folder=Path(sys.argv[1]);model=next(folder.glob('HX05[AB]_*_matched_v1.FCStd'));d=A.openDocument(str(model))
r=json.loads((folder/'edit-check.json').read_text())
assert all(isinstance(o.Proxy,H.Generator) for o in d.Objects if hasattr(o,'Kind'))
assert d.FinalHolder.Shape.isValid() and len(d.FinalHolder.Shape.Solids)==1
assert abs(d.FinalHolder.Shape.Volume-r['edited_volume_mm3'])<1e-5
key=next(o for o in d.Objects if getattr(o,'Kind','')=='Key');key.Proxy.execute(key)
assert key.Shape.isValid() and not key.LastError
r['fresh_process_reopen_and_execute_passed']=True
(folder/'edit-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
