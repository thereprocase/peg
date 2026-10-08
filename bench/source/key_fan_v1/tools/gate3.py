import sys, json, numpy as np, trimesh
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2]/'gallery_new_designs_v1/snapshot/bench/source/solder_v12'))
import checks
from pathlib import Path
d=Path(sys.argv[1]); pr=trimesh.load(d/'print.stl',force='mesh'); inv=np.linalg.inv(np.array(json.loads((d/'pose.json').read_text())).reshape(4,4))
oh=checks.overhangs(pr,inv,[]); isl=checks.islands(pr,inv)
print('components',len(pr.split(only_watertight=False)),'vol cm3',round(pr.volume/1000,1),'extents',pr.extents.round(1),'overhang features',len(oh['features']),'area',oh['other_area_mm2'])
for f in sorted(oh['features'],key=lambda f:-f['area_mm2'])[:12]: print(' ',f['area_mm2'],f['mean_normal_z'],f['short_span_mm'],f['installed_bbox'])
pts=[p['installed_xyz'] for p in isl['points']]
print('islands',len(pts)); print(pts[:40])
