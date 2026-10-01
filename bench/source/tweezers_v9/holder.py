"""v9 tweezer station: v8 cradles, flat right cheek, best-guess peg set.

Receiver: v7/v8's 48.8 x 180.1 mm plate (Y 0.15..5.55, Z -175..5.12). Pegs at
X = +-12.7 mm, following the tall-part rule (2026-10-01):
  row 0      PF02 #9 hooks: upper side ribs +0.50, tongue clamp 0.49 on 3.94
  rows 2, 4  loose conformal bearing pegs (stock lower locator, no ribs)
  row 6      PF06-style latch: 1.2 mm hook, 60 deg return, meaty arm, 0.3 crest,
             turned 90 deg about the peg axis so it flexes in Z, i.e. in the
             layer plane of this right-cheek print; in-hole ribs +0.30
  rows 1,3,5 empty
Best guess ahead of PF06 results. Run with FreeCAD's Python:
  holder.py <build-dir>   (expects front-to-cheek.step from front.py there)
"""
from pathlib import Path
import sys, json, hashlib, math
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import FreeCAD as A, Part
import peg_profile as P
import peg_print_variant as PV
import peg_fit_ladder_v2 as G
import peg_fit_ladder_v4 as C
from peg_fit_ladder import box, write_stl
from peg_interface import receive_pegs
V = A.Vector
PITCH, FACE = 25.4, 0.15
COLS = [-12.7, 12.7]
PLATE = dict(x=24.4, y0=0.15, y1=5.55, z0=-175.0, z1=5.12)
CHEEK_T = 3.0
BEARING_ROWS = [2, 4]
LATCH_ROW = 6
TOP = dict(upper_ribs_mm=0.50, clamp_mm=0.49)
# Gap 1.8 (not 1.5): the board sweep needed 1.425 mm of fold at row 6 with a 1.5 gap.
LATCH = {'concept': 'LATCH2', 'hook_mm': 1.2, 'catch_deg': 60, 'contact_ref_deg': 60, 'crest_mm': 0.3, 'gap_mm': 1.8}
LATCH_BODY_RIBS = 0.30
NAME = 'part-solder-modules-tweezers__v9__cheek-cradle__fit-pf02c9-latch'


def row_z(k):
    return 0.12-PITCH*k          # hole centre of row k, design coordinates (seated pose -0.12)


def turn(shape, x, z, deg=-90):
    """Rotate about the peg axis (parallel to Y) through (x, z); -90 maps +X to +Z."""
    s = shape.copy(); s.rotate(V(x, 0, z), V(0, 1, 0), deg); return s


def build(build_dir):
    path = G.fit_file(TOP['clamp_mm'])
    canonical = P.FIT_SOURCE
    P.FIT_SOURCE = PV.FIT_SOURCE = path
    try:
        fit = P.parse(path.read_bytes())
        plate = box(-PLATE['x'], PLATE['y0'], PLATE['z0'], 2*PLATE['x'], PLATE['y1']-PLATE['y0'], PLATE['z1']-PLATE['z0'])
        front = Part.read(str(build_dir/'front-to-cheek.step'))
        host = plate.fuse(front).removeSplitter()
        # Cheek: flat right face for the bed, inside the allowed host volume.
        from geometry import ENVELOPE, ROOT as BR   # noqa: F401  (bench envelope, X-independent)
        pts = [(v.Y, v.Z) for v in host.Vertexes]
        hull = convex_hull(pts)
        vs = [V(PLATE['x']-CHEEK_T, y, z) for y, z in hull]
        cheek = Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(CHEEK_T, 0, 0)).common(ENVELOPE)
        host = host.fuse(cheek).removeSplitter()
        outside = host.cut(ENVELOPE).Volume
        reference = P.load_reference()
        upper = [s for s in reference.Solids if s.BoundBox.ZMax > -9.9]
        lower = [s for s in reference.Solids if s.BoundBox.ZMax < -9.9][0]
        shape = host
        reports = []
        for x in COLS:
            ref = Part.makeCompound(upper+[lower]); ref.translate(V(x, 0, 0))
            shape, r = receive_pegs(ref, shape, include_lower=False)
            reports.append(r)
        elbow = reports[0]['peg_profile']['elbow_center_y_mm']
        add, cut = [], []
        zu = fit['PEG_SEAT_DROP']
        for x in COLS:
            for s in G.side_ribs(zu, TOP['upper_ribs_mm'], max(elbow, FACE-G.BOARD)+0.3, FACE+1.0, lead=G.UPPER_LEAD)[0]:
                s = s.copy(); s.translate(V(x, 0, 0)); add.append(s)
            for k in BEARING_ROWS+[LATCH_ROW]:
                loc = lower.copy(); loc.translate(V(x, 0, row_z(k)-row_z(1))); add.append(loc)
            zl = row_z(LATCH_ROW)
            for s in G.side_ribs(zl, LATCH_BODY_RIBS, FACE-G.BOARD+0.2, FACE+1.0, lead=1.0)[0]:
                s = s.copy(); s.translate(V(x, 0, 0)); add.append(s)
            la, lc, linfo = C.concept_geometry(LATCH, zl, FACE)
            for s in la:
                s = s.copy(); s.translate(V(x, 0, 0)); add.append(turn(s, x, zl))
            for s in lc:
                s = s.copy(); s.translate(V(x, 0, 0)); cut.append(turn(s, x, zl))
        shape = shape.multiFuse(add).removeSplitter()
        shape = shape.cut(cut).removeSplitter()
        assert shape.isValid() and len(shape.Solids) == 1, (shape.isValid(), len(shape.Solids))
        # Latch measured on the built part: hook reaches 1.2 past the hole wall in +Z.
        yc = sum(linfo['crest_y_mm'])/2
        for x in COLS:
            cr = shape.common(box(x-.005, yc-.005, row_z(LATCH_ROW)-10, .01, .01, 20))
            assert len(cr.Solids) == 2, 'latch arm must be free'
            reach = cr.BoundBox.ZMax-row_z(LATCH_ROW)-6.35/2
            assert abs(reach-LATCH['hook_mm']) < 1e-4, reach
        # Bearing pegs: loose sideways, conformal underneath.
        bw = shape.common(box(-30, FACE-2.005, row_z(2)-.005, 60, .01, .01))
        widths = sorted(s.BoundBox.XLength for s in bw.Solids)
        info = dict(fit_file=str(path.relative_to(P.ROOT)), top=TOP, latch=dict(LATCH, body_ribs_mm=LATCH_BODY_RIBS,
                    orientation='flexes in Z (rotated 90 deg about the peg axis), hook toward +Z', detail=linfo),
                    rows=dict(hooks=[0], bearing=BEARING_ROWS, latch=[LATCH_ROW], empty=[1, 3, 5]),
                    bearing_peg_widths_mm=widths, host_outside_envelope_mm3=outside, cheek_thickness_mm=CHEEK_T,
                    predicted_clamp_interference_at_3p94_mm=-reports[0]['peg_profile']['predicted_clearance_at_3p94_board_mm'])
        return shape, info
    finally:
        P.FIT_SOURCE = PV.FIT_SOURCE = canonical


def convex_hull(points):
    pts = sorted(set((round(a, 6), round(b, 6)) for a, b in points))
    def cross(o, a, b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0: lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0: upper.pop()
        upper.append(p)
    return lower[:-1]+upper[:-1]


def print_pose(shape):
    """Right cheek on the bed, as v8: rotate +90 deg about Y (X -> -Z)."""
    s = shape.copy(); s.rotate(V(), V(0, 1, 0), 90)
    b = s.BoundBox; s.translate(V(-b.XMin, -b.YMin, -b.ZMin)); return s


if __name__ == '__main__':
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    shape, info = build(out)
    shape.exportStep(str(out/f'{NAME}__installed.step'))
    p = print_pose(shape)
    bed = [f for f in p.Faces if isinstance(f.Surface, Part.Plane) and abs(f.BoundBox.ZMax) < 1e-6 and abs(f.BoundBox.ZMin) < 1e-6]
    info['bed_contact_area_mm2'] = sum(f.Area for f in bed)
    p.exportStep(str(out/f'{NAME}__print-right-cheek.step'))
    info['files'] = [write_stl(shape, out/f'{NAME}__installed.stl'), write_stl(p, out/f'{NAME}__print-right-cheek.stl')]
    info['print_bounds_mm'] = [p.BoundBox.XLength, p.BoundBox.YLength, p.BoundBox.ZLength]
    (out/f'{NAME}__design-and-checks.json').write_text(json.dumps(info, indent=2)+'\n')
    print(json.dumps({k: info[k] for k in ['bearing_peg_widths_mm', 'host_outside_envelope_mm3', 'bed_contact_area_mm2', 'print_bounds_mm']}))
