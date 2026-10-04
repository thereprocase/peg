"""V5 frame construction: four seats at 28 mm pitch and raised top rail.

Construction helper for inward20_v5.py; no import-time geometry.
Y is away from the board, Z up. Positive X-axis rotation makes +Y uphill.
Original contact geometry is rigidly transformed; shared receiver remains unrotated.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

import FreeCAD as A
import Part

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
saved_argv = sys.argv[:]
sys.argv = ['holder.py', 'unused', 'v11p3']
import holder as H
sys.argv = saved_argv
sys.path.insert(0, str(HERE.parent / 'solder_v12'))
import common as K

V = A.Vector
ANGLE = 20.0
PITCH = 28.0
HEIGHT = -37.0
EXTRA_Y = 19.05
V2 = HERE.parents[1] / 'reviews/tweezer-inward20-v2'
TRAYS = 4
HOOP_ROW = 4
BEARING_ROWS = [2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def moved(shape, placement):
    result = shape.copy()
    result.transformShape(placement.toMatrix())
    return result


def difference(a, b):
    return a.cut(b).Volume + b.cut(a).Volume


def round_outline(points, x0, thickness, radius):
    """Round only the extruded outline's X-directed edges; never a bearing seam."""
    shape = K.poly_prism(points, 'x', x0, x0 + thickness)
    edges = [e for e in shape.Edges if len(e.Vertexes) == 2 and
             abs(abs(e.Vertexes[1].Point.x-e.Vertexes[0].Point.x)-thickness) < 1e-7]
    return shape.makeFillet(radius, edges)


def make_frame():
    H.LEAN = H.RIB = 4.0
    H.RIBS = False
    H.TRAYS = TRAYS
    H.TOP_FLOOR_Z = 0.0
    mesh, pts = H.tool_points()
    pl, yaw = H.placement(pts)
    reference = H.tray(0, pl, pts)
    rotation = A.Rotation(V(1, 0, 0), ANGLE)
    pivot = V(0, 10, 0)
    pitch = A.Placement(pivot-rotation.multVec(pivot)+V(0, 0, HEIGHT), rotation)
    tool_pose = pitch.multiply(pl)
    # First reproduce v1, then translate globally without changing Z or orientation.
    tip_y = min(tool_pose.multVec(V(*p)).y for p in pts)
    pitch.move(V(0, max(0.0, 9.55-tip_y), 0))
    pitch.move(V(0, EXTRA_Y, 0))
    tool_pose = pitch.multiply(pl)
    v2 = json.loads((V2/'candidate.json').read_text())['cases'][0]
    translation = [a-b for a, b in zip(list(tool_pose.Base), v2['tool_pose']['base'])]
    assert max(abs(a-b) for a,b in zip(translation, [0, 0, 0])) < 1e-9
    assert max(abs(a-b) for a,b in zip(tool_pose.Rotation.Q, v2['tool_pose']['quaternion'])) < 1e-9
    host, receiver = K.receiver(2, HOOP_ROW, 'right-cheek', bearing_rows=BEARING_ROWS)
    floors, slots, wedges = [], [], []
    for k in range(TRAYS):
        transform = A.Placement(pitch)
        transform.move(V(0, 0, -PITCH*k))
        floors.append(moved(reference[0][0], transform))
        slots.append(moved(reference[1], transform))
        wedges.append(moved(reference[2], transform))
    # The cheek follows the receiving pitch; exposed heels overhang the open end.
    yf = max(f.optimalBoundingBox().YMax for f in floors)
    slope = math.tan(math.radians(ANGLE))
    valley_point = pitch.multVec(V(H.INNER, 70, 0))
    def valley(y):
        return valley_point.z + (y-valley_point.y)*slope
    top = lambda y: valley(y) + 32.0
    bottom = lambda y: valley(y) - PITCH*(TRAYS-1) - 9.0
    # One rounded silhouette controls shell, reinforcement and web boundaries.
    # No individually terminated diagonal strips or rail shards are added.
    outline = [(5.25, -107.48), (5.25, 5.12), (32, 5.12),
               (yf, top(yf)), (yf, bottom(yf)), (75, -121), (25, -126.7)]
    outer = round_outline(outline, H.CHEEK_X, 3.0, 3.0)
    envelope = round_outline(outline, H.CHEEK_X, 48.8, 3.0)
    rear_limit = min(f.optimalBoundingBox().YMin for f in floors)-5.0
    # Rounded openings leave a continuous mount spine, middle cross-member and
    # shelf-root spine. Their through-depth boundaries are shared by the cheek
    # and its shallow reinforcement, so no sliver remains at a strip junction.
    windows = [ [(18,-43),(18,-7),(rear_limit-5,-7),(rear_limit-5,-43)],
                [(18,-98),(18,-54),(rear_limit-5,-54),(rear_limit-5,-98)] ]
    for k in range(TRAYS):
        ya, yb = rear_limit+5, yf-7
        low, high = 3.5-PITCH*k, 12.0-PITCH*k
        windows.append([(ya,valley(ya)+low),(yb,valley(yb)+low),
                        (yb,valley(yb)+high),(ya,valley(ya)+high)])
    cheek = outer
    rear_profile=[(H.CHEEK_X,0),(H.CHEEK_X+7.0,0),
                  (H.CHEEK_X+7.0,rear_limit-3),(H.INNER,rear_limit+1),
                  (H.CHEEK_X,rear_limit+1)]
    rear_frame=envelope.common(K.poly_prism(rear_profile,'z',-150,50))
    for poly in windows:
        cutter = round_outline(poly,H.CHEEK_X-1,51,2.5)
        cheek = cheek.cut(cutter)
        rear_frame = rear_frame.cut(cutter)
    # Continuous top/bottom flanges share the outer contour and rounded inner
    # boundaries; both run into the mount spine, without an acute free strip end.
    top_inner = [(4,-140),(yf+2,-140),(yf+2,top(yf)-2.4),
                 (32,2.72),(4,2.72)]
    bottom_inner = [(4,40),(yf+2,40),(yf+2,bottom(yf)+6),
                    (74,-115),(25,-120.7),(4,-104.5)]
    flange_blank = round_outline(outline,H.CHEEK_X,20.0,3.0)
    top_rail = flange_blank.cut(round_outline(top_inner,H.CHEEK_X-1,23,2.5))
    bottom_rail = flange_blank.cut(round_outline(bottom_inner,H.CHEEK_X-1,23,2.5))
    shell = cheek.multiFuse([rear_frame,top_rail,bottom_rail]).removeSplitter()
    # Broad end webs merge into those same flanges and are clipped to their
    # silhouette, removing the former stepped/pointed web-to-rail overhangs.
    webs = []
    # A shared silhouette-derived skin gives each end web the same roof/floor
    # planes as its adjacent rail, eliminating intersecting triangular surface
    # shards. Only the broad footprint tapers toward the cheek.
    upper_web_inner=top_inner
    skins=[envelope.cut(round_outline(upper_web_inner,H.CHEEK_X-1,51,2.5)),
           envelope.cut(round_outline(bottom_inner,H.CHEEK_X-1,51,2.5))]
    for ye,skin in zip([45,75],skins):
        footprint=K.poly_prism([(H.CHEEK_X,4),(24.1,4),(H.CHEEK_X,ye)],'z',-150,50)
        webs.append(skin.common(footprint))
    root = K.poly_prism([(H.INNER-.05,5.4),(H.INNER+4.5,5.4),
                         (H.INNER-.05,10.0)],'z',-105,3.0)
    body = host.multiFuse([shell, root]+webs+floors).cut(slots).removeSplitter()
    # Pointed (+X print-up) plate opening; protect the complete shared peg roots.
    for offset in [0,50.8]:
        window = K.pointed_window(-17,17,-39-offset,-14-offset,'+X')
        body = body.cut(window.cut(K.peg_keepout(2,HOOP_ROW,bearing_rows=BEARING_ROWS))).removeSplitter()
    assert body.isValid() and len(body.Solids) == 1
    rear = K.box(-60, -40, -160, 120, 40.15, 240)
    peg_delta = difference(body.common(rear), host.common(rear))
    assert peg_delta < 1e-6, peg_delta
    return dict(body=body,host=host,receiver=receiver,reference=reference,pitch=pitch,tool_pose=tool_pose,floors=floors,slots=slots,mesh=mesh,pts=pts,root=root,webs=webs,outline=outline,windows=windows,peg_delta=peg_delta)
