"""HX02 v2: the full-depth canted metric hex-key rack, finished.

Same contract as v1: nine blind sockets take each straight long arm, axes lean 30 degrees
outward from vertical, the bend and short arm stay exposed, print on the right cheek (-X).
Installed +Y points out from the board; +X is the user's left.

v2 finish, every surface chosen for the cheek print (print up = installed +X):
- Organ-pipe bank: each socket is a fluted column whose front is a cylinder about its own
  axis, swept +/-40 degrees, meeting its neighbours in crisp 100-degree valleys. No face leans
  past 45 degrees from vertical in print. Pitch is the width / 9, so the pipes tile exactly.
- One smooth monotone curve replaces the v1 staircase under the bank; it falls toward +X, so
  in the print every point of it faces upward. The bank sits 8 mm further out than v1 so the
  curve can keep falling at the bed end without reaching the board.
- Fillets wherever both faces point up or sideways in print; 45-degree chamfers round the bed.
- Round 100-degree countersinks swallow each teardrop roof at the mouth.
- Size numerals and fading V-reveals, continuing the pipe valleys, are cut in the top surface;
  the bed cheek carries an inset V border; the open +X end is closed by 45-degree hipped caps.
"""
from pathlib import Path
import json, math, sys, argparse
import FreeCAD as A
import Part
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'bench/source/bespoke_tools_v1'))
import build as B
K = B.K; V = A.Vector
OUT = ROOT/'bench/reviews/canted-hex-keys-v2/HX02'
INPUT = Path(__file__).with_name('key_set.json')
DATA = json.loads(INPUT.read_text())
U = V(0, .5, math.sqrt(3)/2); T = V(0, math.sqrt(3)/2, -.5)
CELLS = 8; HALF = 25.4*CELLS/2-1; PITCH = 2*HALF/9
MOUTH_Y = 132.; MOUTH_Z = -12.; P0 = V(0, MOUTH_Y, MOUTH_Z)
BACK = -10.                           # deepest bank back (the 10 mm pipe), for board clearance
TIE_T = 3.5                           # top tie plate thickness
WALL = 3.                             # graduated pipes: wall round each bore at the pipe crest
SWEEP = math.radians(40)              # pipe face: +/-40 deg, inside the 45 deg print limit
R_PIPE = (PITCH/2)/math.sin(SWEEP)
FLOOR = 3.; CLEAR = .35; ROOF = math.radians(50)
SINK = math.radians(50)               # countersink half-angle from the axis (>= 45 for the print)
TIE_TOP = ((4.55, 5.12), -.08886)     # v1 top tie: board point and slope dz/dy
REVEAL = dict(half_angle=math.radians(50), depth=1.2, run=45.)
BED_GROOVE = dict(inset=6., depth=1., half_angle=math.radians(40))
CAP = 2.                              # hipped end-cap shell thickness, normal to its faces
CAP_RISE = math.tan(math.radians(50)); PLUG_TOP = 2.  # cap faces 50 degrees from the print horizontal
LABEL_DEPTH = .6; LABEL_SIZE = 8.; LABEL_BACK = 24.
FACE_DEPTH = .6; FACE_SIZE = 6.5; FACE_Q = -45.   # numerals on each pipe face, below the key's short arm
CUT_TILT = math.radians(62)         # oblique cut rising toward print-up: no stroke ceilings (counters still start as tiny islands)
SINK_RING = 1.6                     # droplet countersink: radial growth at the mouth
FONT_CANDIDATES = [Path(A.getHomePath())/'bin/Lib/site-packages/matplotlib/mpl-data/fonts/ttf/DejaVuSans-Bold.ttf',
                   Path('/usr/share/fonts/TTF/DejaVuSans-Bold.ttf'), Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')]
SHORT = [15, 18, 20, 23, 29, 33, 38, 44, 50]


def pt(x, q, t):
    """Installed point from lateral x, axial q (along U from the mouth plane) and t (along T)."""
    return V(x, 0, 0)+P0+U*q+T*t


def qt(v):
    d = v-P0
    return d.dot(U), d.dot(T)


def socket_x(i):
    return HALF-PITCH*(i+.5)


def tie_z(y):
    (y0, z0), s = TIE_TOP
    return z0+s*(y-y0)


def tie_normal():
    s = TIE_TOP[1]; n = V(0, -s, 1); n.normalize(); return n


def crease_y():
    """Where the top tie's upper plane meets the mouth plane."""
    (y0, z0), s = TIE_TOP
    # (y-MOUTH_Y)*U.y + (z0+s*(y-y0)-MOUTH_Z)*U.z = 0
    return (MOUTH_Y*U.y-(z0-s*y0-MOUTH_Z)*U.z)/(U.y+s*U.z)


def meet(a0, a1, b0, b1):
    """Intersection of 2D lines a0-a1 and b0-b1 (y, z)."""
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = a0, a1, b0, b1
    d = (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
    u = ((x1-x3)*(y3-y4)-(y1-y3)*(x3-x4))/d
    return (x1+u*(x2-x1), y1+u*(y2-y1))


def yz(v):
    return (v.y, v.z)


def halfspace(origin, normal):
    """Solid {X : normal . (X - origin) >= 0}, as a large box."""
    n = V(normal); n.normalize()
    s = Part.makeBox(4000, 4000, 2000, V(-2000, -2000, 0))
    s.Placement = A.Placement(origin, A.Rotation(V(0, 0, 1), n))
    return s


def bore_r(i):
    return DATA['keys'][i]['across_flats']/math.sqrt(3)+CLEAR


def crest(i):
    """Pipe i's crest, front and back, in T: its bore radius plus WALL."""
    return bore_r(i)+WALL


VALLEY_DROP = R_PIPE*(1-math.cos(SWEEP))      # crest to pipe edge


def socket_wire(p, r):
    # Circular clearance below, tangent 50-degree roof toward +X (print up), as v1.
    cx = r*math.cos(ROOF); cy = r*math.sin(ROOF)
    q = lambda x, t: p+V(x, 0, 0)+T*t
    lo = q(cx, -cy); hi = q(cx, cy); apex = q(r/math.cos(ROOF), 0)
    return Part.Wire([Part.Arc(lo, q(-r, 0), hi).toShape(), Part.makeLine(hi, apex), Part.makeLine(apex, lo)])


def key(af, length, short, p):
    # Straight segment exact; bend radius and short arm are labelled assumptions (as v1).
    radius = af/math.sqrt(3); bend = 2*radius
    tip = p-U*(length-.06); a = tip+U*length
    b = a+U*bend+T*bend
    mid = a+U*(bend/math.sqrt(2))+T*(bend*(1-1/math.sqrt(2)))
    spine = Part.Wire([Part.makeLine(tip, a), Part.Arc(a, mid, b).toShape(), Part.makeLine(b, b+T*short)])
    points = [tip+V(radius*math.cos(i*math.pi/3), 0, 0)+T*(radius*math.sin(i*math.pi/3)) for i in range(6)]
    profile = Part.Wire(Part.makePolygon(points+[points[0]]).Edges)
    return spine.makePipeShell([profile], True, False)


def bottom_arc(keys):
    """Smooth monotone underside D(x) (depth below the mouth plane): a shape-preserving cubic
    through each bore's shallow-side corner at FLOOR below its blind end. D falls toward +X, so
    every bore section to the deep side of its knot keeps at least FLOOR, and in the cheek print
    the whole underside faces up. At the bed end it keeps falling at the 10 mm bore's slope,
    limited so the bank's lower back corner stays 3 mm in front of the board face."""
    import numpy as np
    from scipy.interpolate import PchipInterpolator
    kx, kd = [], []
    for i in reversed(range(len(keys))):
        r = keys[i]['across_flats']/math.sqrt(3)+CLEAR
        kx.append(socket_x(i)+r/math.cos(ROOF)+.6); kd.append(keys[i]['straight_length']+FLOOR)
    slope = (kd[0]-kd[1])/(kx[1]-kx[0])
    limit = (MOUTH_Y+BACK*T.y-.15-3)/U.y
    end = min(kd[0]+.8*slope*(kx[0]+HALF), limit)
    kx.insert(0, -HALF); kd.insert(0, end)
    kx.append(HALF); kd.append(kd[-1]-2)
    f = PchipInterpolator(np.array(kx), np.array(kd))
    return dict(kind='pchip', knots=[[float(x), float(d)] for x, d in zip(kx, kd)]), (lambda x: float(f(x)))


def font():
    return next(str(p) for p in FONT_CANDIDATES if p.exists())


def label(text, i):
    """Engraving tool for one size numeral on the top surface, LABEL_DEPTH deep, read from the front."""
    faces = [Part.Face(w, 'Part::FaceMakerBullseye') for w in Part.makeWireString(text, font(), LABEL_SIZE) if w]
    s = Part.makeCompound(faces); bb = s.BoundBox
    s.translate(V(-(bb.XMin+bb.XMax)/2, -(bb.YMin+bb.YMax)/2, 0))
    n = tie_normal(); up = V(0, -1, TIE_TOP[1]); up.normalize()      # text up points to the board
    m = A.Matrix(-1, 0, 0, 0, 0, up.y, n.y, 0, 0, up.z, n.z, 0, 0, 0, 0, 1)
    s = s.copy(); s.transformShape(m)
    y = crease_y()-LABEL_BACK
    # Oblique cut rising toward print-up: no stroke ceiling, so the slicer adds no support inside the
    # numerals (a straight cut drew supports into every stroke).
    w = n*-math.cos(CUT_TILT)+V(1, 0, 0)*math.sin(CUT_TILT)
    lift = .3/math.cos(CUT_TILT)
    s.translate(V(socket_x(i), y, tie_z(y))-w*lift)
    prism = Part.makeCompound([f.extrude(w*(lift+2*LABEL_DEPTH/math.cos(CUT_TILT))) for f in s.Faces])
    return prism.common(halfspace(V(0, y, tie_z(y))-n*LABEL_DEPTH, n))


def face_label(text, i):
    """Numeral on pipe i's face, FACE_Q along the axis below the mouth, FACE_DEPTH below the crest
    cylinder, cut obliquely like the top numerals; reads from the front."""
    faces = [Part.Face(w, 'Part::FaceMakerBullseye') for w in Part.makeWireString(text, font(), FACE_SIZE) if w]
    s = Part.makeCompound(faces); bb = s.BoundBox
    s.translate(V(-(bb.XMin+bb.XMax)/2, -(bb.YMin+bb.YMax)/2, 0))
    m = A.Matrix(-1, 0, 0, 0, 0, U.y, T.y, 0, 0, U.z, T.z, 0, 0, 0, 0, 1)     # x: viewer's right, y: U, normal: T
    s = s.copy(); s.transformShape(m)
    w = T*-math.cos(CUT_TILT)+V(1, 0, 0)*math.sin(CUT_TILT)
    lift = .3/math.cos(CUT_TILT)
    s.translate(pt(socket_x(i), FACE_Q, crest(i))-w*lift)
    prism = Part.makeCompound([f.extrude(w*(lift+2.5*FACE_DEPTH/math.cos(CUT_TILT))) for f in s.Faces])
    keep = Part.makeCylinder(R_PIPE-FACE_DEPTH, 120, pt(socket_x(i), FACE_Q-60, crest(i)-R_PIPE), U)
    return prism.cut(keep)


def reveal(x):
    """V-reveal on the top surface continuing a pipe valley: 100-degree V, REVEAL depth from the
    crease to a conical stop REVEAL['run'] mm toward the board; the numerals sit in the lanes."""
    yc = crease_y(); n = tie_normal(); a = REVEAL['half_angle']; d = REVEAL['depth']
    along = V(0, -1, TIE_TOP[1]); along.normalize()
    start = V(x, yc, tie_z(yc))-n*d                    # rounded start on the crease, clear of the mouth face
    end = V(x, yc-REVEAL['run'], tie_z(yc-REVEAL['run']))-n*d
    w = end-start; h = 4.
    tri = Part.Face(Part.makePolygon([start, start+n*h+V(h*math.tan(a), 0, 0), start+n*h-V(h*math.tan(a), 0, 0), start]))
    return tri.extrude(w).fuse([Part.makeCone(0, h*math.tan(a), h, end, n), Part.makeCone(0, h*math.tan(a), h, start, n)])


def convex_inward(poly):
    """(point, unit inward normal) for each edge of a convex (y, z) polygon."""
    n = len(poly); cy = sum(p[0] for p in poly)/n; cz = sum(p[1] for p in poly)/n
    out = []
    for i in range(n):
        (y0, z0), (y1, z1) = poly[i], poly[(i+1) % n]
        e = V(0, y1-y0, z1-z0); nin = V(0, -e.z, e.y); nin.normalize()
        if nin.dot(V(0, cy-y0, cz-z0)) < 0:
            nin = nin*-1
        out.append((V(0, y0, z0), nin))
    return out


def bed_groove(shape, poly, log, side=-1):
    """Inset V border in the bed cheek following the convex outline poly: walls 40 degrees from
    the print vertical, so the groove closes over itself without support."""
    g = BED_GROOVE; s, h, k = g['inset'], g['depth'], math.tan(g['half_angle'])
    xb = side*HALF; o = -side                         # o: inward along X from that end face
    A_ = B.box(min(xb+side*.5, xb+o*h), -400, -400, h+.5, 800, 800); B_ = A_.copy()   # from 0.5 outside the face
    for p, nin in convex_inward(poly):
        A_ = A_.common(halfspace(V(xb, 0, 0)+p+nin*(s-k*h), V(-k*o, nin.y, nin.z)))
        B_ = B_.common(halfspace(V(xb, 0, 0)+p+nin*(s+k*h), V(k*o, nin.y, nin.z)))
    out = shape.cut(A_.cut(B_)).removeSplitter()
    assert out.isValid() and len(out.Solids) == 1, 'bed groove'
    log.append(dict(op='inset V border', end='bed (-X)' if side < 0 else 'print top (+X)', inset_mm=s, depth_mm=h, removed_mm3=shape.Volume-out.Volume))
    return out


def bed_chamfer(shape, poly, insets, keep_y, log):
    """Chamfer round the bed outline (convex poly), insets[i] in from edge i on the bed, rising at
    50 degrees, so the chamfer never overhangs past the print limit. An inset of 0 leaves an edge
    whose face already leans out at that angle (the pipe flank). Near the board (y < keep_y) the
    geometry stays as it is."""
    m = math.tan(math.radians(50)); xb = -HALF; c = max(insets)
    keep = B.box(xb-1, -400, -400, c*m+1, 800, 800)
    for (p, nin), ci in zip(convex_inward(poly), insets):
        keep = keep.common(halfspace(V(xb, 0, 0)+p+nin*ci, V(1/m, nin.y, nin.z)))
    # Only the top edges (tie top, mouth) are chamfered; the pipe foot and web below z = -60 stay as they are.
    out = shape.cut(B.box(xb-1, keep_y, -60, c*m+1, 400, 100).cut(keep)).removeSplitter()
    assert out.isValid() and len(out.Solids) == 1, 'bed chamfer'
    log.append(dict(op='bed outline chamfer', inset_mm=c, rise_mm=c*m, pipe_flank='left as is (leans 40 deg already)', removed_mm3=shape.Volume-out.Volume))
    return out


def inradius(poly):
    """Largest distance from any interior point to the nearest edge of a convex polygon (sampled)."""
    edges = convex_inward(poly); ys = [p[0] for p in poly]; zs = [p[1] for p in poly]; best = 0.
    for a in range(81):
        for b in range(81):
            q = V(0, min(ys)+(max(ys)-min(ys))*a/80, min(zs)+(max(zs)-min(zs))*b/80)
            best = max(best, min((q-p).dot(nin) for p, nin in edges))
    return best


def end_plug(poly, log, what):
    """Close a convex opening at the +X end (the print top), flush with the end face. The cavity
    under it rises to a point: every ceiling face grows inward from its wall at 50 degrees, so
    nothing starts in mid-air. PLUG_TOP is the cover thickness over that point."""
    R = inradius(poly)
    base = HALF-PLUG_TOP-CAP_RISE*R                    # where the ceiling meets the walls
    plug = B.box(base-1, -400, -400, HALF-base+1, 800, 800).common(K.poly_prism(poly, 'x', base-1, HALF))
    air = B.box(base-2, -400, -400, HALF-base+2, 800, 800)
    for p, nin in convex_inward(poly):
        # air under the ceiling: x <= base + CAP_RISE * d, d measured inward from edge i
        air = air.common(halfspace(V(base, 0, 0)+p+nin*-.3, V(-1, nin.y*CAP_RISE, nin.z*CAP_RISE)))
    plug = plug.cut(air)
    log.append(dict(op='end plug', where=what, edges=len(poly), ceiling_deg=50, cover_mm=PLUG_TOP, inradius_mm=round(R, 2), volume_mm3=plug.Volume))
    return plug


def edges_where(shape, pred):
    return [e for e in shape.Edges if pred(e)]


def on_plane_x(e, x, tol=1e-4):
    b = e.BoundBox
    return abs(b.XMin-x) < tol and abs(b.XMax-x) < tol


def try_fillet(shape, edges, radius, what, log):
    if not edges:
        log.append(dict(op=what, edges=0)); return shape
    for r in [radius, radius*.75, radius*.5]:
        try:
            s = shape.makeFillet(r, edges).removeSplitter()
            if s.isValid() and len(s.Solids) == 1:
                log.append(dict(op=what, edges=len(edges), radius_mm=r)); return s
        except Exception:  # noqa: BLE001  OCC refuses some radii; try smaller
            pass
    # Fall back to one edge at a time (same radius), recording any OCC refuses.
    done, skipped = 0, []
    for e in edges:
        match = [c for c in shape.Edges if abs(c.Length-e.Length) < 1e-6 and c.CenterOfMass.distanceToPoint(e.CenterOfMass) < 1e-6]
        if not match:
            continue
        try:
            t = shape.makeFillet(radius*.6, match[:1]).removeSplitter()
            if t.isValid() and len(t.Solids) == 1:
                shape = t; done += 1; continue
        except Exception:  # noqa: BLE001
            pass
        skipped.append([round(v, 1) for v in e.CenterOfMass])
    if not done:
        raise RuntimeError(f'{what}: no fillet radius worked ({len(edges)} edges)')
    log.append(dict(op=what, edges=done, radius_mm=radius, one_by_one=True, skipped_at=skipped))
    return shape


def build(quick=False):
    log = []
    keys = DATA['keys']
    arc, D = bottom_arc(keys)
    receiver, mount = K.receiver(CELLS, 2, 'right-cheek', z0=-57)
    # --- organ-pipe bank -------------------------------------------------------------------
    deep = D(-HALF-1)+10
    frame = K.poly_prism([yz(v) for v in [pt(0, -deep, -40), pt(0, 0, -40), pt(0, 0, 40), pt(0, -deep, 40)]], 'x', -HALF, HALF)
    pipes = []
    for i in range(9):
        # Each pipe is the lens between two crest cylinders, front and back, sized to its key.
        x = socket_x(i); c = crest(i)
        front_cyl = Part.makeCylinder(R_PIPE, deep+20, pt(x, -deep-10, c-R_PIPE), U)
        back_cyl = Part.makeCylinder(R_PIPE, deep+20, pt(x, -deep-10, R_PIPE-c), U)
        pipes.append(front_cyl.common(back_cyl))   # neighbours meet where their crests cross: no steps
    bank = B.union(pipes).common(frame).common(B.box(-HALF, -50, -400, 2*HALF, 400, 600))
    # The curve below: a smooth ruled surface along T; everything under it removed.
    n = 96; xs = [-HALF+2*HALF*s/n for s in range(n+1)]
    pts = [pt(x, -D(x), -30) for x in xs]
    curve = Part.BSplineCurve(); curve.interpolate(pts)
    a0, a1 = pt(-HALF-2, -D(-HALF), -30), pt(HALF+2, -D(HALF), -30)
    b0, b1 = pt(-HALF-2, -deep-30, -30), pt(HALF+2, -deep-30, -30)
    floor = Part.Face(Part.Wire([Part.makeLine(a0, pts[0]), curve.toShape(), Part.makeLine(pts[-1], a1), Part.makeLine(a1, b1),
                                 Part.makeLine(b1, b0), Part.makeLine(b0, a0)])).extrude(T*60)
    bank = bank.cut(floor).removeSplitter()
    assert bank.isValid() and len(bank.Solids) == 1
    mid = lambda e: e.valueAt(.5*(e.FirstParameter+e.LastParameter))
    mouth = lambda e: all(abs(qt(v.Point)[0]) < 1e-4 for v in e.Vertexes) and abs(qt(mid(e))[0]) < 1e-4
    valley = lambda e: e.Curve.TypeId == 'Part::GeomLine' and abs(abs(e.Curve.Direction.dot(U))-1) < 1e-6 and min(abs(e.BoundBox.XMin-(HALF-PITCH*j)) for j in range(1, 9)) < 1e-3
    inner = lambda e: e.BoundBox.XMin > -HALF+1e-3 and e.BoundBox.XMax < HALF-1e-3
    lowest = lambda e: inner(e) and qt(mid(e))[0] < -60 and not valley(e) and e.Curve.TypeId != 'Part::GeomLine'
    bank = try_fillet(bank, edges_where(bank, lowest), 2., 'underside edges', log)
    bank = try_fillet(bank, edges_where(bank, lambda e: inner(e) and mouth(e) and not valley(e)), 2., 'mouth rim', log)
    # --- ties, bed-cheek web and +X end caps -----------------------------------------------
    yc = crease_y()
    top = K.poly_prism([(4.55, 5.12), (yc+40, tie_z(yc+40)), (yc+40, tie_z(yc+40)-TIE_T), (4.55, 5.12-TIE_T)], 'x', -HALF, HALF)
    top = top.common(K.poly_prism([yz(v) for v in [pt(0, -300, -300), pt(0, 0, -300), pt(0, 0, 0), pt(0, -300, 0)]], 'x', -HALF-1, HALF+1))
    lt_top, lt_bot = [(4.55, -51), yz(pt(0, -.5, -1.))], [(4.55, -55), yz(pt(0, -3.6, .3))]
    low_tie = K.poly_prism([lt_bot[0], lt_bot[1], lt_top[1], lt_top[0]], 'x', -HALF, HALF)
    corner = pt(0, -D(-HALF+2), -4)
    web_pts = [(4.55, 5.12), (yc, tie_z(yc))]+[yz(v) for v in [pt(0, 0, -4), pt(0, -D(-HALF+2)+2, -4), corner]]
    web_pts.append((4.55, corner.z) if corner.y > 4.55 else (4.55, corner.z+(4.55-corner.y)*math.tan(math.radians(60))))
    web = K.poly_prism(web_pts, 'x', -HALF, -HALF+2)
    # +X end openings: above and below the lower tie, between the receiver face and the bank back.
    back = (yz(pt(0, 0, -1)), yz(pt(0, -100, -1)))     # inside every pipe
    tie_u = ((4.55, 5.12-TIE_T), (yc+40, tie_z(yc+40)-TIE_T))
    rec = ((5.55, 10.), (5.55, -100.))
    cross = meet(*tie_u, *lt_top)
    if cross[0] < meet(*tie_u, *back)[0]:     # the ties meet before the bank: a triangle
        upper = [meet(*rec, *tie_u), cross, meet(*lt_top, *rec)]
    else:
        upper = [meet(*rec, *tie_u), meet(*tie_u, *back), meet(*back, *lt_top), meet(*lt_top, *rec)]
    low_corner = yz(pt(HALF, -D(HALF)+8, -1))
    lower = [meet(*rec, *lt_bot), meet(*lt_bot, *back), low_corner]
    below_mouth = K.poly_prism([yz(v) for v in [pt(0, -300, -300), pt(0, 0, -300), pt(0, 0, 0), pt(0, -300, 0)]], 'x', -HALF-1, HALF+1)
    # Only the upper opening is closed: every edge of it is a wall, so its ceiling grows from walls. The lower
    # opening has a free edge (open toward the board under the receiver); a cap there would bridge 80 mm in
    # the print and pull in supports, so it stays open like v1.
    caps = [end_plug(upper, log, 'upper +X opening').common(below_mouth)]
    front = B.union([bank, top, low_tie, web])
    assert front.isValid() and len(front.Solids) == 1, ('front', len(front.Solids))
    crease = lambda e: e.BoundBox.YMax < yc+1 and e.BoundBox.YMin > yc-1 and mouth(e)
    front = try_fillet(front, edges_where(front, crease), 8., 'top-to-mouth crease', log)
    clear_of_board = lambda e: e.BoundBox.YMin > 5.6
    front = try_fillet(front, edges_where(front, lambda e: on_plane_x(e, HALF) and clear_of_board(e)), 2.5, '+X end (print top)', log)
    front = B.union([front]+caps)
    assert front.isValid() and len(front.Solids) == 1, ('front with plugs', len(front.Solids))
    tvalley = crest(8)-VALLEY_DROP
    bed_corner = pt(0, -D(-HALF), -tvalley)
    bed_poly = [(4.55, 5.12), (yc, tie_z(yc))]+[yz(v) for v in [pt(0, 0, tvalley), pt(0, -D(-HALF), tvalley), bed_corner]]
    if bed_corner.y > 4.55:
        bed_poly.append((4.55, bed_corner.z))
    front = bed_chamfer(front, bed_poly, [1., 1., 0., 0., 0., 0.], 5.6, log)
    front = bed_groove(front, bed_poly, log)
    t0 = crest(0)-VALLEY_DROP
    front0 = (yz(pt(0, 0, t0)), yz(pt(0, -100, t0)))
    end_poly = [(4.55, 5.12), (yc, tie_z(yc)), yz(pt(0, 0, t0)), meet(*front0, *lt_bot), meet(*rec, *lt_bot)]   # the solid upper end
    front = bed_groove(front, end_poly, log, side=1)
    # --- sockets, countersinks, reveals and labels -----------------------------------------
    holes = []; tools = []; seats = []; marks = []
    for i, (item, short) in enumerate(zip(keys, SHORT)):
        af = item['across_flats']; length = item['straight_length']; x = socket_x(i)
        p = pt(x, 0, 0); r = af/math.sqrt(3)+CLEAR
        rc = r+SINK_RING; hc = SINK_RING/math.tan(SINK)
        bore = Part.Face(socket_wire(p-U*length, r)).extrude(U*(length+1))
        sink = Part.makeLoft([socket_wire(p-U*hc, r), socket_wire(p, rc)], True, True)   # the same droplet on every mouth
        opening = Part.Face(socket_wire(p, rc)).extrude(U*100)
        holes.extend([bore, sink, opening])
        marks.append(label('%g' % af, i)); marks.append(face_label('%g' % af, i))
        tools.append(key(af, length, short, p))
        seats.append(dict(**item, x_mm=x, axis=[U.x, U.y, U.z], mouth=[p.x, p.y, p.z], socket_depth_mm=length,
                          radial_clearance_mm=CLEAR, countersink_radius_mm=rc, countersink_depth_mm=hc, tip_floor_min_mm=FLOOR,
                          assumed_short_straight_mm=short, assumed_bend_radius_mm=2*af/math.sqrt(3)))
    label_boxes = [[[round(b.XMin-.5, 2), round(b.YMin-.5, 2), round(b.ZMin-.5, 2)], [round(b.XMax+.5, 2), round(b.YMax+.5, 2), round(b.ZMax+.5, 2)]]
                   for b in (m.BoundBox for m in marks)]
    marks += [reveal(HALF-PITCH*j) for j in range(1, 9)]
    body = front.cut(B.union(holes)).cut(Part.makeCompound(marks)).removeSplitter()
    shape = B.union([receiver, body])
    assert shape.isValid() and len(shape.Solids) == 1, ('native body', len(shape.Solids))
    rear = B.box(-300, -40, -400, 600, 40.15, 800)
    a, b = shape.common(rear), receiver.common(rear); delta = a.cut(b).Volume+b.cut(a).Volume
    assert delta < 1e-6, delta
    print('HX02 v2 geometry PASS', json.dumps(log), flush=True)
    return dict(shape=shape, receiver=receiver, mount=mount, tools=tools, seats=seats, arc=arc, D=D, finish=log, label_boxes=label_boxes)


def floors(shape, seats):
    """Measured blind-floor thickness: from a grid on each bore floor, along -U to the outside."""
    out = []
    for s in seats:
        p = V(*s['mouth']); r = s['across_flats']/math.sqrt(3)+CLEAR; base = p-U*s['socket_depth_mm']
        thick = []
        for a in range(-4, 5):
            for b in range(-4, 5):
                x, t = r*a/4, r*b/4
                if x*x+t*t > r*r*.98:
                    continue
                q = base+V(x, 0, 0)+T*t-U*1e-3
                seg = shape.common(Part.makeLine(q, q-U*40))
                thick.append(min((e.Length for e in seg.Edges if min((v.Point-q).Length for v in e.Vertexes) < 1e-2), default=0.))
        out.append(round(min(thick), 3))
    return out


def full(g):
    shape, receiver, tools, seats = g['shape'], g['receiver'], g['tools'], g['seats']
    OUT.mkdir(parents=True, exist_ok=True)
    rear = B.box(-300, -40, -400, 600, 40.15, 800)
    a, b = shape.common(rear), receiver.common(rear); delta = a.cut(b).Volume+b.cut(a).Volume
    thick = floors(shape, seats)
    for s, f in zip(seats, thick):
        s['tip_floor_measured_mm'] = f
        assert f >= FLOOR-.05, ('thin floor', s['across_flats'], f)
    routes = []
    for i, (tool, seat) in enumerate(zip(tools, seats)):
        assert tool.isValid() and len(tool.Solids) == 1
        distance = seat['straight_length']+3
        peak = 0; neighbor = 0
        for k in range(math.ceil(distance/4)+1):
            travel = min(k*4, distance); moved = B.moved(tool, [0, U.y*travel, U.z*travel])
            peak = max(peak, shape.common(moved).Volume)
            for j in [i-1, i+1]:
                if 0 <= j < len(tools):
                    neighbor = max(neighbor, tools[j].common(moved).Volume)
        assert peak < 1e-5 and neighbor < 1e-5, (seat['across_flats'], peak, neighbor)
        stop = shape.common(B.moved(tool, [0, -U.y*.2, -U.z*.2])).Volume
        assert stop > 1e-5, ('missing blind floor', seat['across_flats'], stop)
        routes.append(dict(af_mm=seat['across_flats'], max_intersection_mm3=peak, neighbor_intersection_mm3=neighbor,
                           axial_withdrawal_mm=distance, outward_travel_mm=U.y*distance, upward_travel_mm=U.z*distance,
                           downward_stop_intersection_mm3=stop, sample_step_mm=4))
    checks = dict(native_valid=True, solids=1, unchanged_board_side_delta_mm3=delta, tool_routes=routes,
                  full_straight_legs_enclosed=True, measured_tip_floors_mm=thick, finish=g['finish'],
                  limits='Nominal rigid tools, sampled axial withdrawal and blind-floor stop. Other tools above the rack are not modeled. Physical fit, friction, rotation, grip and bumps remain untested.')
    print('HX02 v2 full-depth seats, floors and withdrawal PASS', flush=True)
    pp, matrix = K.pose_transform(shape, 'right-cheek'); prefix = 'part-hx02__v2__right-cheek__fit-pf02c9-hoop5'; assets = {}
    roundtrip = {}
    for role, s in [('installed', shape), ('print', pp), ('tool-reference', Part.makeCompound(tools))]:
        step = OUT/(prefix+'__'+role+'.step'); s.exportStep(str(step)); again = Part.read(str(step))
        assert again.isValid() and len(again.Solids) == len(s.Solids)
        # Self-booleans of coincident solids are unreliable in OCC; compare volume, area and bounds instead.
        b1, b2 = s.BoundBox, again.BoundBox
        diff = max(abs(again.Volume-s.Volume)/s.Volume, abs(again.Area-s.Area)/s.Area,
                   max(abs(getattr(b1, k)-getattr(b2, k)) for k in ['XMin', 'XMax', 'YMin', 'YMax', 'ZMin', 'ZMax'])/100)
        assert diff < 2e-5, (role, diff)            # STEP writes ~1e-6 relative precision
        roundtrip[role] = diff
        stl = OUT/(prefix+'__'+role+'.stl'); B.mesh(s, stl)
        assets[role+'_step'] = step.name; assets[role+'_stl'] = stl.name
    checks['step_roundtrip'] = dict(method='volume, area and bounds of the re-read STEP vs the native solid (relative)', max_rel_diff=roundtrip)
    doc = A.newDocument('HX02v2'); body = doc.addObject('PartDesign::Body', 'Holder'); feature = body.newObject('PartDesign::Feature', 'HolderSolid'); feature.Shape = shape
    feature.addProperty('App::PropertyString', 'BuildSource', 'Provenance'); feature.BuildSource = 'bench/source/canted_hex_keys_v2/build.py'
    doc.recompute(); assets['freecad'] = prefix+'.FCStd'; doc.saveAs(str(OUT/assets['freecad'])); A.closeDocument(doc.Name)
    x0 = socket_x(0); load = pt(x0, -4, crest(0))
    record = dict(id='HX02', name='Full-depth canted metric hex-key rack', version=2, prefix=prefix, cells=CELLS, pose='right-cheek', mount=g['mount'],
                  volume_mm3=shape.Volume, print_bounds_mm=B.bounds(pp), pose_matrix=K.pose_matrix(shape, 'right-cheek'), assets=assets, checks=checks,
                  finish=dict(pipe_pitch_mm=PITCH, pipe_wall_mm=WALL, pipe_crests_mm=[round(crest(i), 3) for i in range(9)], pipe_face_radius_mm=R_PIPE, pipe_sweep_deg=math.degrees(SWEEP), underside=g['arc'],
                              labels=dict(font='DejaVu Sans Bold', size_mm=LABEL_SIZE, depth_mm=LABEL_DEPTH, on='top surface', installed_boxes=g['label_boxes']), operations=g['finish']),
                  tool_spec=dict(keys=seats, axis_angle_from_vertical_deg=30, short_arm_direction=[T.x, T.y, T.z],
                                 reference="Owner straight lengths; 4 mm interpolated. Short straight arms and bend radii are illustrative assumptions."),
                  load_point=[round(load.x, 3), round(load.y, 3), round(load.z, 3)], source_sha256=B.sha(Path(__file__)),
                  source_dependencies={p.relative_to(ROOT).as_posix(): B.sha(p) for p in [INPUT, Path(B.__file__), Path(K.__file__)]},
                  FreeCAD_version=A.Version(), files={p.name: dict(sha256=B.sha(p), bytes=p.stat().st_size) for p in OUT.iterdir() if p.suffix in ['.step', '.stl', '.FCStd']})
    (OUT/'report.json').write_text(json.dumps(record, indent=2)+'\n', newline='\n')
    fs = dict(step=assets['installed_step'], h=5., supports=['pegs'], loads=[dict(id='sideways', point=record['load_point'], force=[5, 0, 0], radius=4), dict(id='down', point=record['load_point'], force=[0, 0, -5], radius=4)])
    (OUT/(prefix+'__fea-spec.json')).write_text(json.dumps(fs, indent=2)+'\n', newline='\n')
    print('HX02 v2 native exports PASS', flush=True)


def quick_meshes(g, out):
    out.mkdir(parents=True, exist_ok=True)
    pp, _ = K.pose_transform(g['shape'], 'right-cheek')
    B.mesh(g['shape'], out/'installed.stl'); B.mesh(pp, out/'print.stl')
    B.mesh(Part.makeCompound(g['tools']), out/'keys.stl')
    (out/'pose.json').write_text(json.dumps(K.pose_matrix(g['shape'], 'right-cheek')))
    (out/'labels.json').write_text(json.dumps(g['label_boxes']))
    print('quick meshes', out, g['shape'].Volume, flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--quick', type=Path); a = ap.parse_args()
    g = build(quick=bool(a.quick))
    if a.quick:
        quick_meshes(g, a.quick)
    else:
        full(g)
