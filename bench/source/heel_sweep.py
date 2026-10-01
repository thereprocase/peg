"""PF04 HEEL: does the lower peg + tail + heel pass the board on a lifted path?

Sweeps the baseline removal path shifted up by (heel + 0.05 mm) at every pose
after seating, against a board with nominal 6.35 mm holes. Lower peg only; the
upper hook's seated headroom is reported from geometry. Run with FreeCAD's Python.
"""
import json, sys
import numpy as np
import FreeCAD as A, Part
import peg_profile as P
import peg_fit_ladder_v2 as G
import peg_fit_ladder_v4 as C
V = A.Vector
ROOT = P.ROOT
poses = json.loads((ROOT/'reference/conformal_motion_results.json').read_text())['removal_poses']
path = np.array([[p['y'], p['z'], p['theta_deg']] for p in poses])
def samples(lift):
    pts = [path[0], path[0]+[0, lift, 0]] + [p+[0, lift, 0] for p in path[1:]]
    out = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        n = max(2, int(np.linalg.norm(b[:2]-a[:2])/0.1 + abs(b[2]-a[2])/0.5))
        out += [a+(b-a)*i/n for i in range(1, n+1)]
    return out
T, R = G.BOARD, 6.35/2
board = Part.makeBox(40, T, 80, V(-20, -T, -60))
for zc in (0, -25.4):
    board = board.cut(Part.makeCylinder(R, T+2, V(0, -T-1, zc), V(0, 1, 0)))
face, zl = 0.15, 0.12-25.4
lower = [s for s in P.load_reference().Solids if s.BoundBox.ZMax < -9.9][0]
HEELS = [float(x) for x in (sys.argv[1].split(',') if len(sys.argv) > 1 else ['0.3', '0.5', '0.7'])]
LIFTS = [float(x) for x in (sys.argv[2].split(',') if len(sys.argv) > 2 else ['0', '0.75'])]
report = {}
for hb in HEELS:
    add, _, _ = C.concept_geometry({'concept': 'HEEL', 'heel_mm': hb}, zl, face)
    probe = lower.fuse(add).removeSplitter()
    worst = {}
    for lift in LIFTS:
        w = (0.0, None)
        for y, z, th in samples(lift):
            s = probe.copy(); s.rotate(V(), V(1, 0, 0), float(th)); s.translate(V(0, float(y), float(z)))
            v = s.common(board).Volume
            if v > w[0]: w = (round(v, 4), [round(float(y), 3), round(float(z), 3), round(float(th), 2)])
        worst[f'lift_{lift:.2f}'] = w
    report[f'heel_{hb}'] = worst
    print(hb, worst, flush=True)
report['upper_seated_headroom_mm'] = 6.35-5.6
report['scope'] = 'Lower peg, tail and heel only; ribs excluded (they are intended compliance). Sampled, not certified.'
(ROOT/'reviews/pf04-heel-sweep.json').write_text(json.dumps(report, indent=2)+'\n')
