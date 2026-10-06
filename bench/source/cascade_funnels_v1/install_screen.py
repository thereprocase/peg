"""Sample the CF01 front body along the existing nominal installation route."""
from pathlib import Path
import sys,json
import FreeCAD
import Part
R=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(R/'bench/source/gallery_current_mounts_v1'))
import remount
D=R/'bench/reviews/bespoke-tools-v1/CF01'
r=json.loads((D/'report.json').read_text());p=D/r['assets']['installed_step']
s=Part.read(str(p));front=s.common(remount.box(-300,.15,-300,300,300,300))
result=remount.screen(front)
result.update(input_sha256=remount.sha(p),checker_sha256=remount.sha(Path(remount.__file__)))
(D/'installation-screen.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2));assert result['pass']
