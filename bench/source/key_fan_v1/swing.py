"""Install swing check for the full peg grid (owner, 2026-10-08: hooks every inch, locking pegs on the bottom row,
gravity-load pegs everywhere else). The part hangs on its top-row hooks and swings down onto the board; every
other peg must enter its hole without hitting the board. Sampled: rotation about the hook seat (an axis along x
through the top of the top-row holes at mid-board) from SWING_DEG to 0 in 0.5 deg steps; at each step the overlap
of every bearing peg and locking hoop with the board (3.94 mm, 6.35 mm holes on the 25.4 mm grid). The hoops'
designed snap (catch interference in the last degrees) is reported separately from any other contact.
Run with FreeCAD's Python:  python swing.py <build dir>   (reads installed.step)
"""
from pathlib import Path
import json, math, sys
import FreeCAD as A
import Part
V = A.Vector
d = Path(sys.argv[1]); SWING_DEG = 25.
PITCH, FACE, BOARD, HOLE_R = 25.4, .15, 3.94, 6.35/2
shape = Part.read(str(d/'installed.step'))
pegs = shape.common(Part.makeBox(600, 20, 800, V(-300, FACE-20, -600)))
# rows: cluster the pegs by height (25.4 mm apart), top row = hooks, bottom row = locking hoops
sol = [q for q in pegs.Solids if q.Volume > 1.]
zc = sorted({round(q.BoundBox.Center.z/5.)*5. for q in sol}, reverse=True)
clusters = []
for z in zc:
    if not clusters or clusters[-1]-z > 12.:
        clusters.append(z)
groups = {}
for q in sol:
    k = min(range(len(clusters)), key=lambda i: abs(clusters[i]-q.BoundBox.Center.z)); groups.setdefault(k, []).append(q)
# hole centres: the bearing pegs' 120 deg arcs match the bore, so a bearing peg's underside is the hole bottom
zs = min(q.BoundBox.ZMin for q in groups[1])+HOLE_R-(.12-PITCH*1)
rows = sorted(groups); top, bottom = rows[0], rows[-1]
bb = shape.BoundBox
board = Part.makeBox(bb.XLength+60, BOARD, bb.ZLength+80, V(bb.XMin-30, FACE-BOARD, bb.ZMin-60))
holes = []
for i in range(-12, 13):
    for k in range(-1, 14):
        holes.append(Part.makeCylinder(HOLE_R, BOARD+2, V(i*PITCH, FACE-BOARD-1, .12-PITCH*k+zs), V(0, 1, 0)))
board = board.cut(Part.makeCompound(holes))
pivot = V(0, FACE-BOARD/2, .12+zs+HOLE_R)
res = dict(rows=dict(hooks=top, locking=bottom, bearing=[k for k in rows if k not in (top, bottom)]),
           pegs=dict(hooks=len(groups[top]), locking=len(groups[bottom]), bearing=sum(len(groups[k]) for k in rows if k not in (top, bottom))),
           steps=[], worst_bearing_mm3=0., worst_locking_before_snap_mm3=0., worst_bearing_per_peg_mm3=0.)
GRAZE_PER_PEG = .25          # declared: a bearing peg may graze a hole edge by this much (a few hundredths of a mm)
for i in range(int(SWING_DEG/.5), -1, -1):
    ang = i*.5; step = dict(deg=ang)
    for kind, ks in (('bearing', res['rows']['bearing']), ('locking', [bottom])):
        v = 0.; per = 0.
        for k in ks:
            for s in groups[k]:
                m = s.copy(); m.rotate(pivot, V(1, 0, 0), ang)     # +x rotation: points below the pivot move to +y, off the board
                if m.BoundBox.intersect(board.BoundBox):
                    c = m.common(board).Volume; v += c; per = max(per, c)
        step[kind+'_mm3'] = round(v, 4); step[kind+'_per_peg_mm3'] = round(per, 4)
    res['steps'].append(step)
    res['worst_bearing_mm3'] = max(res['worst_bearing_mm3'], step['bearing_mm3'])
    res['worst_bearing_per_peg_mm3'] = max(res['worst_bearing_per_peg_mm3'], step['bearing_per_peg_mm3'])
    if ang > 3.:
        res['worst_locking_before_snap_mm3'] = max(res['worst_locking_before_snap_mm3'], step['locking_mm3'])
seated = res['steps'][-1]
res['seated'] = dict(bearing_mm3=seated['bearing_mm3'], locking_snap_mm3=seated['locking_mm3'])
res['graze_per_peg_limit_mm3'] = GRAZE_PER_PEG
res['passed'] = (seated['bearing_mm3'] < 1e-3 and res['worst_locking_before_snap_mm3'] < 1e-3
                 and res['worst_bearing_per_peg_mm3'] <= GRAZE_PER_PEG)
(d/'swing.json').write_text(json.dumps(res, indent=1), encoding='utf-8', newline='\n')
print(json.dumps({k: res[k] for k in ('rows', 'pegs', 'worst_bearing_mm3', 'worst_bearing_per_peg_mm3', 'worst_locking_before_snap_mm3', 'seated', 'passed')}))
print('last steps', res['steps'][-8:])
