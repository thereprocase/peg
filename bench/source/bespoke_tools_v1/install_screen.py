"""Fresh front-body obstruction screen using the preserved nominal reference route."""
from pathlib import Path
import json,sys
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'bench/source/gallery_current_mounts_v1'))
import remount
for id in ['HX01','TM01','CL01']:
 d=ROOT/'bench/reviews/bespoke-tools-v1'/id;r=json.loads((d/'report.json').read_text());p=d/r['assets']['installed_step'];s=Part.read(str(p));front=s.common(remount.box(-300,.15,-300,300,300,300))
 result=remount.screen(front);result['input_sha256']=remount.sha(p);result['checker_sha256']=remount.sha(Path(remount.__file__));(d/'installation-screen.json').write_text(json.dumps(result,indent=2)+'\n');print(id,result,flush=True);assert result['pass']
