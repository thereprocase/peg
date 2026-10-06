"""Verify pinned external short-key STEP references against HX01. Download separately.

Usage with FreeCAD Python: check_external_keys.py DIRECTORY_WITH_2_3_4-HexKey.step
The source geometry remains external; this writes numerical fit evidence only.
"""
from pathlib import Path
import hashlib,json,sys
import FreeCAD as A
import Part
import build as B
root=B.OUT/'HX01';r=json.loads((root/'report.json').read_text());holder=Part.read(str(root/r['assets']['installed_step']))
refs=Path(sys.argv[1]);rows=[]
for af,index in [(2,1),(3,3),(4,4)]:
 p=refs/f'{af}-HexKey.step';s=Part.read(str(p));s.rotate(A.Vector(),A.Vector(1,0,0),180);s.rotate(A.Vector(),A.Vector(0,0,1),-90)
 s.translate(A.Vector(72-index*18,12,-53.8-s.optimalBoundingBox().ZMin+.06))
 poses=[(0,0,k*.5) for k in range(19)]+[(0,k,9) for k in range(1,71)]
 peak=max(holder.common(B.moved(s,v)).Volume for v in poses)
 rows.append(dict(af_mm=af,source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),valid=s.isValid(),solids=len(s.Solids),seated_clearance_mm=holder.distToShape(s)[0],max_intersection_mm3=peak,poses=len(poses),passed=peak<1e-6))
result=dict(holder_step_sha256=B.sha(root/r['assets']['installed_step']),references=rows,passed=all(r['passed'] for r in rows),limits='Nominal rigid CAD clearance. The models are unmeasured generic short keys; physical fit and handling remain pending.')
(root/'external-key-fit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert result['passed']
