"""Check HX01 keys resting on the floor and leaning against the rear plate.

Rigid two-contact geometry only; this is not a friction or bump simulation.
"""
from pathlib import Path
import json,math
import FreeCAD as A
import Part
import build as B
D=B.OUT/'HX01';r=json.loads((D/'report.json').read_text());holder=Part.read(str(D/r['assets']['installed_step']));refs=Part.read(str(D/r['assets']['tool-reference_step']));floor=-53.8
seated=[];records=[]
for item in r['tool_spec']['sizes']:
 x=item['x_mm'];original=min(refs.Solids,key=lambda s:abs(s.CenterOfMass.x-x))
 def place(angle):
  s=original.copy();s.rotate(A.Vector(x,12,floor),A.Vector(1,0,0),angle);s.translate(A.Vector(0,0,floor+.06-s.optimalBoundingBox().ZMin));return s
 lo,hi=0,12
 assert holder.common(place(hi)).Volume>1e-6
 for _ in range(15):
  mid=(lo+hi)/2
  if holder.common(place(mid)).Volume>1e-7:hi=mid
  else:lo=mid
 angle=max(0,lo-.01);s=place(angle)
 peak=0
 for v in [(0,0,k*.5) for k in range(19)]+[(0,k,9) for k in range(1,71)]:peak=max(peak,holder.common(B.moved(s,v)).Volume)
 b=s.optimalBoundingBox();record=dict(af_mm=item['af_mm'],lean_back_deg=angle,closest_board_plane_mm=b.YMin-.15,floor_gap_mm=b.ZMin-floor,collision_mm3=holder.common(s).Volume,pickup_peak_intersection_mm3=peak)
 record['passed']=record['closest_board_plane_mm']>=0 and peak<1e-6
 assert record['passed'],record
 records.append(record);seated.append(s)
# All nine rest orientations coexist.
neighbor=max((a.common(b).Volume for i,a in enumerate(seated) for b in seated[i+1:]),default=0)
assert neighbor<1e-6
s=Part.makeCompound(seated);B.mesh(s,D/'seated-keys.stl');s.exportStep(str(D/'seated-keys.step'))
result=dict(passed=True,keys=records,neighbor_intersection_mm3=neighbor,holder_step_sha256=B.sha(D/r['assets']['installed_step']),limits='Floor plus rear-plate lean contact. Contact surfaces are approximated by a 0.06 mm floor gap and 0.01 degree angular backoff. Friction, spring compliance, bumps and human grip remain physical tests.')
(D/'key-seating.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
