"""v9 vs v8: tool clearances at rest and along the lift-then-left removal path.
Run with cadpy: tool_check.py <v9-build-dir> <v8-regen-dir>"""
import sys, json
from pathlib import Path
import numpy as np, trimesh
from trimesh.collision import CollisionManager
v9, v8 = Path(sys.argv[1]), Path(sys.argv[2])
P8 = 'part-solder-modules-tweezers__v8__long-body-cradle__fit-e586ab4ff6'
N9 = 'part-solder-modules-tweezers__v9__cheek-cradle__fit-pf02c9-latch'
out = {}
for tag, path in [('v8', v8/f'{P8}__installed.stl'), ('v9', v9/f'{N9}__installed.stl')]:
    holder = trimesh.load(path)
    tools = [trimesh.load(v8/f'{P8}__reference-tool-{i+1}.stl') for i in range(4)]
    res = []
    for i, m in enumerate(tools):
        others = CollisionManager(); others.add_object('holder', holder)
        for j, n in enumerate(tools):
            if i != j: others.add_object(f'n{j}', n)
        path_pts = [np.array([0, 0, z]) for z in np.arange(0, 5.01, .25)] + [np.array([-x, 0, 5]) for x in np.arange(0, 30.01, .5)]
        d = []
        for p in path_pts:
            q = np.eye(4); q[:3, 3] = p; d.append(float(others.min_distance_single(m, transform=q)))
        res.append(dict(slot=i+1, rest_mm=d[0], path_min_mm=min(d)))
    out[tag] = res
    print(tag, [(r['slot'], round(r['rest_mm'], 4), round(r['path_min_mm'], 4)) for r in res], flush=True)
same = all(abs(a['rest_mm']-b['rest_mm']) < 1e-4 and abs(a['path_min_mm']-b['path_min_mm']) < 1e-4 for a, b in zip(out['v8'], out['v9']))
out['identical_to_v8'] = same
(v9/'tool-check.json').write_text(json.dumps(out, indent=2)+'\n')
print('identical to v8:', same)
