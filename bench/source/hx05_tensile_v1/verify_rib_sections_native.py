import sys,json
from pathlib import Path
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'bench/source/hx05_tensile_v1'))
import FreeCAD as App
import Part
from rib_section_screen import hulls,section
cfg=json.loads((root/'bench/source/hx05_anisotropy_v1/config.json').read_text());results=[]
for rack in cfg['racks']:
 id=rack['id'];native=root/'.local-runtime/hx05-density-v1'/id/'fea-front-domain.brep';body=Part.Shape();body.read(str(native));checks=[]
 for tool in rack['tools'][:1]:
  for y in [1.3]:
   for part in hulls(tool,rack):
    polygon=section(part,y);points=list(polygon)+[polygon.mean(0)];inside=[body.isInside(App.Vector(float(p[0]),y,float(p[1])),1e-5,True) for p in points]
    checks.append(dict(tool=tool['name'],y=y,points=len(points),inside=all(inside)))
 results.append(dict(id=id,body_valid=body.isValid(),checks=checks,passed=all(c['inside'] for c in checks)))

(root/'bench/reviews/hx05-tensile-v1/rib-section-native-probes.json').write_text(json.dumps(dict(scope='Critical analytic rib-section vertices and centers in valid cached native front-domain BREP. Geometric point probes only, not an integration or load validation.',racks=results),indent=2)+'\n')
print([(r['id'],r['passed']) for r in results])
