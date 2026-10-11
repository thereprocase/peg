"""Real installer/document-load smoke, with display-only calls stubbed.
This does not claim a GUI or Windows test; the local GUI stalls before loading
any model. All file installation, imports, documents and CAD are real FreeCAD.
"""
from pathlib import Path
import sys,types,runpy,json
import FreeCAD as A
b=Path(sys.argv[1]).resolve();out=Path(sys.argv[2])
A.getUserAppDataDir=lambda:'/tmp/hx05-family-setup-headless/'
view=types.SimpleNamespace(viewAxonometric=lambda:None,fitAll=lambda:None)
gui=types.ModuleType('FreeCADGui');gui.activeDocument=lambda:types.SimpleNamespace(activeView=lambda:view)
sys.modules['FreeCADGui']=gui
runpy.run_path(str(b/'SETUP_MATCHED_FANS.FCMacro'))
import hx05_family as H
rows=[]
for d in A.listDocuments().values():
 assert d.FinalHolder.Shape.isValid() and len(d.FinalHolder.Shape.Solids)==1
 custom=[o for o in d.Objects if hasattr(o,'Kind')]
 assert len(custom)==49 and all(isinstance(o.Proxy,H.Generator) for o in custom)
 d.START_HERE.Text=(b/'README.txt').read_text();d.save()
 rows.append(dict(filename=Path(d.FileName).name,volume_mm3=d.FinalHolder.Shape.Volume,valid_single_solid=True,custom_features=len(custom)))
assert len(rows)==2
r=dict(passed=True,models=rows,scope='Actual module installation and native document opening. Only display framing calls are stubbed; GUI behavior is not tested.',platform='FreeCAD 1.1.3 Linux headless; GUI startup stalled before model loading; Windows GUI first open remains untested.')
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
