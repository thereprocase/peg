"""PF04 HEEL: per-pose lift window. For each sampled removal pose near the
board (theta < 14 deg), which extra lifts dz in [0, 0.9] leave the lower peg,
tail and heel clear of the board? A heel is installable only if every pose has
a window and the windows chain (checked coarsely). Run with FreeCAD's Python."""
import json, sys
import numpy as np
import FreeCAD as A, Part
import peg_profile as P
import peg_fit_ladder_v2 as G
import peg_fit_ladder_v4 as C
V = A.Vector
poses = json.loads((P.ROOT/'reference/conformal_motion_results.json').read_text())['removal_poses']
path = np.array([[p['y'], p['z'], p['theta_deg']] for p in poses])
pts = [path[0]]
for a, b in zip(path[:-1], path[1:]):
    n = max(2, int(np.linalg.norm(b[:2]-a[:2])/0.15 + abs(b[2]-a[2])/0.5))
    pts += [a+(b-a)*i/n for i in range(1, n+1)]
pts = [p for p in pts if p[2] < 14]
T, R = G.BOARD, 6.35/2
board = Part.makeBox(40, T, 80, V(-20, -T, -60))
for zc in (0, -25.4):
    board = board.cut(Part.makeCylinder(R, T+2, V(0, -T-1, zc), V(0, 1, 0)))
lower = [s for s in P.load_reference().Solids if s.BoundBox.ZMax < -9.9][0]
DZ = np.round(np.arange(0, 0.91, 0.1), 2)
out = {}
for hb in [float(x) for x in sys.argv[1].split(',')]:
    add, _, _ = C.concept_geometry({'concept': 'HEEL', 'heel_mm': hb}, 0.12-25.4, 0.15)
    probe = lower.fuse(add).removeSplitter()
    windows = []
    for y, z, th in pts:
        ok = []
        for dz in DZ:
            s = probe.copy(); s.rotate(V(), V(1, 0, 0), float(th)); s.translate(V(0, float(y), float(z+dz)))
            if s.common(board).Volume < 1e-4: ok.append(float(dz))
        windows.append([round(float(y), 3), round(float(z), 3), round(float(th), 2), ok])
    blocked = [w for w in windows if not w[3]]
    need = max((min(w[3]) for w in windows if w[3]), default=None)
    out[hb] = dict(poses=len(windows), blocked=len(blocked), max_min_lift=need, first_blocked=blocked[:3])
    print(hb, out[hb], flush=True)
(P.ROOT/'reviews/pf04-heel-window.json').write_text(json.dumps(out, indent=2)+'\n')
