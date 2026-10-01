"""v9 pegs vs the board along the baseline removal path (sampled).
Groups: hooks (row 0, intended clamp/rib squeeze at seat), bearing pegs (rows
2, 4: must be clear), latch (row 6: arm may flex; report how far it must move
versus its flex gap). Run with FreeCAD's Python: board_sweep.py <v9-build>"""
import sys, json
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE.parent))
import FreeCAD as A, Part
import peg_profile as P
V = A.Vector
d = Path(sys.argv[1])
N9 = 'part-solder-modules-tweezers__v9__cheek-cradle__fit-pf02c9-latch'
s = Part.read(str(d/f'{N9}__installed.step'))
rear = s.common(Part.makeBox(80, 40, 400, V(-40, -39.85, -300)))      # Y < 0.15: everything behind the face
poses = json.loads((P.ROOT/'reference/conformal_motion_results.json').read_text())['removal_poses']
path = np.array([[p['y'], p['z'], p['theta_deg']] for p in poses]); pts = [path[0]]
for a, b in zip(path[:-1], path[1:]):
    n = max(2, int(np.linalg.norm(b[:2]-a[:2])/0.15+abs(b[2]-a[2])/0.25))
    pts += [a+(b-a)*i/n for i in range(1, n+1)]
T, R = 3.94, 6.35/2
board = Part.makeBox(80, T, 260, V(-40, -T, -200))
for k in range(7):
    for x in (-12.7, 12.7):
        board = board.cut(Part.makeCylinder(R, T+2, V(x, -T-1, -25.4*k), V(0, 1, 0)))
groups = {'hooks': (-12, 40), 'bearing_row2': (-60, -40), 'bearing_row4': (-110, -90), 'latch_row6': (-165, -140)}
worst = {g: dict(volume_mm3=0.0) for g in groups}
for y, z, th in pts:
    m = rear.copy(); m.rotate(V(), V(1, 0, 0), float(th)); m.translate(V(0, float(y), float(z)))
    hit = m.common(board)
    if hit.Volume < 1e-6: continue
    for so in hit.Solids:
        c = so.BoundBox.Center.z
        for g, (lo, hi) in groups.items():
            if lo <= c <= hi and so.Volume > worst[g]['volume_mm3']:
                bb = so.BoundBox
                worst[g] = dict(volume_mm3=round(so.Volume, 4), pose=[round(float(y), 3), round(float(z), 3), round(float(th), 2)],
                                depth_x_mm=round(bb.XLength, 3), depth_z_mm=round(bb.ZLength, 3))
out = dict(poses=len(pts), worst_by_group=worst,
           note='Sampled, not certified. Hooks: intended clamp/side-rib squeeze. Latch: depth_z vs its 1.8 mm flex gap.')
(d/'board-sweep.json').write_text(json.dumps(out, indent=2)+'\n'); print(json.dumps(out, indent=1))
