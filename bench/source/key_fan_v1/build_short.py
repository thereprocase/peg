"""HX04 short-socket version (owner, 2026-10-07): every tool in the shortest socket that keeps it seated
(study/short.py: friction + pegboard bench physics), one socket rail per set tied to a back plate and the
pegboard receiver, printed on the user's LEFT end (+X on the bed, print up = -X).

Rails: convex hull of each set's socket barrels, swept 50 degrees down-and-back in the print (Minkowski
sum with a segment), so every face that looks down in the print is at least 50 degrees steep; trimmed at
the board. Sockets: teardrop roofs toward print-up, floors vertical in the print.
Installed frame: x = user's left, y = out from the board, z = up, mm.
"""
from pathlib import Path
import json, math, sys, argparse
import FreeCAD as A
import Part
import numpy as np
from scipy.spatial import ConvexHull

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT/'bench/source/bespoke_tools_v1'))
sys.path.insert(0, str(HERE/'study'))
import build as B
import short as SH
K = B.K; V = A.Vector
CELLS = int(__import__('os').environ.get('SHORT_CELLS', 8)); HALF = 25.4*CELLS/2-1
# owner, 2026-10-08: 'shave 5-10 mm off each side and let the fan be a little over width': the plate's half
# width can be set apart from the peg pattern (SHORT_PLATE_HALF), the receiver keeps its own cell count
HALF = float(__import__('os').environ.get('SHORT_PLATE_HALF', HALF))
REC_CELLS = int(__import__('os').environ.get('SHORT_REC_CELLS', CELLS))
CLEAR = .35; FLOOR = 3.; WALL = 3.; ROOF = math.radians(50); SINK = math.radians(50)
Y_BACK = .2
PLATE_T = 5.5                                     # wraps the receiver's 5.4 mm wall (PF02/PF07 pegs root in it)
EDGE_R = 1.6
UP = V(-1, 0, 0)                                  # print up: the user's left end is on the bed
D50 = np.array([math.sin(math.radians(50)), -math.cos(math.radians(50)), 0.])   # 50 deg down (+x) and back
LAYOUT = json.loads((HERE/'study'/__import__('os').environ.get('HX4S_LAYOUT', 'short_pol.json')).read_text())


def v(a): return V(*map(float, a))


def halfspace(origin, normal):
    n = V(normal); n.normalize()
    s = Part.makeBox(4000, 4000, 2000, V(-2000, -2000, 0))
    s.Placement = A.Placement(origin, A.Rotation(V(0, 0, 1), n))
    return s


def hull_solid(pts):
    pts = np.asarray(pts, float); h = ConvexHull(pts)
    groups = {}
    for simp, eq in zip(h.simplices, h.equations):
        key = None
        for kq in groups:
            if np.allclose(kq, eq, atol=1e-6):
                key = kq; break
        groups.setdefault(key if key is not None else tuple(eq), set()).update(simp)
    faces = []
    for eq, idx in groups.items():
        q = pts[sorted(idx)]; n = np.asarray(eq[:3]); c = q.mean(axis=0)
        a = q[0]-c; a /= np.linalg.norm(a); b = np.cross(n, a)
        q = q[np.argsort(np.arctan2((q-c)@b, (q-c)@a))]
        P = [v(r) for r in q]
        try:
            faces.append(Part.Face(Part.makePolygon(P+[P[0]])))
        except Part.OCCError:                            # near-coplanar group that is not quite planar: triangles
            for k in range(1, len(P)-1):
                faces.append(Part.Face(Part.makePolygon([P[0], P[k], P[k+1], P[0]])))
    s = Part.Solid(Part.Shell(faces))
    if s.Volume < 0:
        s.reverse()
    return s


def ring(c, axis, r, n=32):
    axis = np.asarray(axis, float); axis /= np.linalg.norm(axis)
    a = np.cross(axis, [1, 0, 0]) if abs(axis[0]) < .9 else np.cross(axis, [0, 1, 0]); a /= np.linalg.norm(a)
    b = np.cross(axis, a); t = np.linspace(0, 2*math.pi, n, endpoint=False)
    return np.asarray(c)+r*(np.outer(np.cos(t), a)+np.outer(np.sin(t), b))


def teardrop(p, r, axis):
    up = UP-axis*UP.dot(axis)
    if up.Length < 1e-6:
        up = V(0, 1, 0)-axis*axis.y
    up.normalize(); across = axis.cross(up); across.normalize()
    cx = r*math.cos(ROOF); cy = r*math.sin(ROOF)
    q = lambda a, b: p+up*a+across*b
    lo = q(cx, -cy); hi = q(cx, cy); apex = q(r/math.cos(ROOF), 0)
    return Part.Wire([Part.Arc(lo, q(-r, 0), hi).toShape(), Part.makeLine(hi, apex), Part.makeLine(apex, lo)])


# T-handle shafts: hex-keyed bores clock the grip turn (a T-handle has no preferred turn under gravity).
# HX4S_TBAR: how the bar sits on the hex shaft, 'corners' (the bar lies along a corner-to-corner line) or 'flats'
# (along a flat-to-flat line). ASSUMED 'corners' until the owner checks one handle.
TBAR = __import__('os').environ.get('HX4S_TBAR', 'corners')
TEE_KEYED_MIN = SH.TEE_KEYED_MIN


def hex_teardrop(p, af_bore, axis, bar):
    """Hex bore (across flats af_bore) clocked to the bar, its top in the print replaced by the 50 deg roof."""
    R = af_bore/math.sqrt(3)
    b = bar-axis*bar.dot(axis); b.normalize(); c = axis.cross(b)
    off = 0. if TBAR == 'corners' else math.radians(30)
    pts = [p+b*(R*math.cos(off+k*math.pi/3))+c*(R*math.sin(off+k*math.pi/3)) for k in range(6)]
    up = UP-axis*UP.dot(axis)
    if up.Length > 1e-6:
        up.normalize(); across = axis.cross(up)
        pts += [p+up*(R*math.cos(ROOF))+across*(s_*R*math.sin(ROOF)) for s_ in (-1, 1)]+[p+up*(R/math.cos(ROOF))]
    # convex hull in the section plane
    e1 = b; e2 = c
    q = np.array([[(x-p).dot(e1), (x-p).dot(e2)] for x in pts]); h = ConvexHull(q)
    P = [p+e1*float(q[i, 0])+e2*float(q[i, 1]) for i in h.vertices]
    return Part.makePolygon(P+[P[0]])


# Owner, 2026-10-08: 'tools that jiggle like to walk ... encourage walking in, not out'. A rattling tool's tip
# strikes the bore wall; the wall's normal decides which way each strike pushes. A bore narrowing toward the floor
# (a plain taper) pushes the tip OUT on every strike; one that widens toward the floor pushes it IN, and gravity's
# sideways part, pressing the resting tip on that slope, adds a steady inward pull. So: a straight neck (the land,
# 25% of the depth, at least 4 mm, which guides the tool and carries the T-handle hex clocking), then the wall
# flares at FLARE_DEG to the floor. The neck is short so the leaning tool's tip, not the neck's far end, limits
# the lean and reaches the flare and the corner seat. L-key bores have no step; T-handle bores go round below the
# hex neck (that step faces the floor, and the shaft is still clocked by the neck as it is drawn out).
flare, land = SH.flare, SH.land


def flare_cone(mouth, axis, r0, depth, d1, d0=None):
    """Teardrop cone from radius r0 at the end of the neck to r0 + flare at the floor, on past it to depth d1."""
    d0 = land(depth) if d0 is None else d0; df = flare(depth)
    r1 = r0+df*(d1-d0)/(depth-d0)
    return Part.makeLoft([teardrop(mouth-axis*d0, r0, axis), teardrop(mouth-axis*d1, r1, axis)], True, True)


def socket(mouth, axis, r, depth, ring_w=1.6, opening=150., hexkey=None, floor=None):
    """hexkey = (af_bore, bar direction) for a clocked T-handle bore, with a hex lead-in funnel.
    floor = (point, void-side normal, deepest depth): the sloped floor from study/short.py floor_plane, low on
    the side the resting tool's tip bears toward (its pinch), so jiggle slides the tip deeper."""
    fp, fn, fdeep = floor
    d1 = fdeep+3.                                       # every bore piece runs past the deepest floor point
    if hexkey is not None:
        afb, bar = hexkey; R = afb/math.sqrt(3)
        bore = Part.Face(hex_teardrop(mouth-axis*d1, afb, axis, bar)).extrude(axis*(d1+1))
        # round below the hex neck (the tip leans any way): a 35 deg cone from the flats out to the corners, no ledge
        # to print as a ceiling, then the flare
        d0 = land(depth); dA = (R-afb/2)/math.tan(math.radians(35))
        bore = bore.fuse(Part.makeLoft([teardrop(mouth-axis*d0, afb/2, axis), teardrop(mouth-axis*(d0+dA), R, axis)], True, True))
        bore = bore.fuse(flare_cone(mouth, axis, R, depth, d1, d0+dA))
        bore = bore.common(halfspace(fp, fn))
        hc = 2*ring_w/math.tan(SINK)                    # a deeper funnel: it turns the shaft into line as it drops
        funnel = Part.makeLoft([hex_teardrop(mouth-axis*hc, afb, axis, bar), hex_teardrop(mouth, afb+2*2*ring_w, axis, bar)], True, True)
        out = Part.Face(teardrop(mouth, R+2*ring_w, axis)).extrude(axis*opening)
        return [bore, funnel, out]
    bore = Part.Face(teardrop(mouth-axis*d1, r, axis)).extrude(axis*(d1+1))
    bore = bore.fuse(flare_cone(mouth, axis, r, depth, d1)).common(halfspace(fp, fn))
    out = Part.Face(teardrop(mouth, r+ring_w, axis)).extrude(axis*opening)
    parts = [bore, out]
    if ring_w > 0 and axis.dot(UP) > -.3:            # entry ring only where the mouth does not face down in print
        hc = ring_w/math.tan(SINK)
        parts.append(Part.makeLoft([teardrop(mouth-axis*hc, r, axis), teardrop(mouth, r+ring_w, axis)], True, True))
    return parts


LABEL = dict(depth=.8, cap=5.88)                 # Fillaprint reference size at w = 0.42 mm (capital height 14 w)
FONT = HERE/'fonts/Fillaprint-Regular.ttf'


def rail(tools, env, set_name=None, labels=None, roots=None):
    """One set's rail: the shared outline (study/short.py rail_points: socket rings past each sloped floor, and
    the label lip), swept 50 deg down-and-back, rounded by the owner's edge rule, trimmed at the board."""
    rings, P = SH.rail_points(tools, set_name, labels)
    if roots is not None:
        roots[set_name] = rings
    lam = (P[:, 1].max()-Y_BACK+2)/math.cos(math.radians(50))
    Q = np.vstack([P, P+D50*lam])
    # owner's edge rule as a Minkowski sum with a small bicone: a disc in the print's XY plane (installed y-z)
    # rounds the edges that stand vertical in the print; cone tips along the print's Z (installed x) at
    # 50 degrees chamfer every other edge. Always valid (a convex hull), always printable.
    th = np.linspace(0, 2*math.pi, 12, endpoint=False)
    bic = np.vstack([np.c_[np.zeros(12), EDGE_R*np.cos(th), EDGE_R*np.sin(th)],
                     [[EDGE_R*math.tan(math.radians(50)), 0, 0], [-EDGE_R*math.tan(math.radians(50)), 0, 0]]])
    hq = Q[ConvexHull(Q).vertices]
    G = hull_solid((hq[:, None, :]+bic[None, :, :]).reshape(-1, 3)).common(env).common(halfspace(V(0, Y_BACK, 0), V(0, 1, 0)))
    return G


def swept_hull(P, env):
    """Hull of P swept 50 deg down-and-back to the board, bicone-rounded, trimmed (as the rails)."""
    lam = (P[:, 1].max()-Y_BACK+2)/math.cos(math.radians(50))
    Q = np.vstack([P, P+D50*lam]); hq = Q[ConvexHull(Q).vertices]
    th = np.linspace(0, 2*math.pi, 12, endpoint=False)
    bic = np.vstack([np.c_[np.zeros(12), EDGE_R*np.cos(th), EDGE_R*np.sin(th)],
                     [[EDGE_R*math.tan(math.radians(50)), 0, 0], [-EDGE_R*math.tan(math.radians(50)), 0, 0]]])
    return hull_solid((hq[:, None, :]+bic[None, :, :]).reshape(-1, 3)).common(env).common(halfspace(V(0, Y_BACK, 0), V(0, 1, 0)))


GUSSET = __import__('os').environ.get('HX4S_GUSSET', 'webs,cheek')
WEB_Y = float(__import__('os').environ.get('HX4S_WEB_Y', 12.))      # back webs reach this far off the board


def blob(pts, rr, pad):
    """Sphere cloud -> points on each sphere (for convex hulls of swept tools)."""
    dirs = np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]]+
                    [[a, b, c] for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)], float)
    dirs /= np.linalg.norm(dirs, axis=1)[:, None]
    return (pts[:, None, :]+dirs[None, :, :]*(rr[:, None, None]+pad)).reshape(-1, 3)


def clearance(Lo, rep, pad=1.5):
    """Each stored tool, its lift out of the socket and its way out, as convex pieces (arm by arm)."""
    out = []
    esc = {r['name']+r['set']: r['escape'] for r in rep}
    for t in Lo.tools:
        u = np.asarray(t['u']); main = t['main']        # long arm / shaft (study, before the rest-pose tip)
        lift = u*(t['D']+3.)
        e = {'forward': np.array([0, 1., 0]), 'up-forward': np.array([0, 1, .4])/np.linalg.norm([0, 1, .4]), 'axis': u, None: u}[esc.get(t['name']+t['set'])]
        for sel in (main, ~main):
            if sel.sum() < 2:
                continue
            c = blob(t['pts'][sel], t['rr'][sel], pad)
            out += [hull_solid(np.vstack([c, c+lift])), hull_solid(np.vstack([c+lift, c+lift+e*220]))]
    return out


def fuse_all(parts):
    """Sequential fuse that refuses to lose material (OCC multiFuse dropped whole rails here)."""
    out = parts[0]
    for q in parts[1:]:
        t = None
        for tol in (0., 1e-3, 1e-2):                     # fuzzy retries: OCC returns null on near-coincident faces
            try:
                t = (out.fuse(q) if tol == 0 else out.fuse([q], tol)).removeSplitter()
                if t.isValid() and t.Volume >= max(out.Volume, q.Volume)-1.:
                    break
            except Exception:  # noqa: BLE001
                t = None
        if t is None:
            raise RuntimeError('fuse failed')
        if not (t.isValid() and t.Volume >= max(out.Volume, q.Volume)-1.):
            raise RuntimeError('fuse lost material %.0f -> %.0f (+%.0f)' % (out.Volume, t.Volume, q.Volume))
        out = t
    return out


def gussets(roots, Lo, rep, env, log):
    """Owner, 2026-10-08: 'it needs more material ... gusset more'. Webs tie neighbouring rails together
    along the board (hull of both rails' barrels, swept like the rails), and a cheek on the bed end ties all
    three; every tool's storage, lift and way out are then cut back out."""
    parts = []
    kinds = GUSSET.split(',')
    if 'webs' in kinds:
        for a, b in (('torx', 'hex'), ('hex', 'tee')):
            parts.append(swept_hull(np.vstack([roots[a], roots[b]]), env).common(B.box(-400, Y_BACK, -600, 800, WEB_Y-Y_BACK, 1200)))
    if 'full' in kinds:                                  # whole-depth webs between neighbouring rails
        for a, b in (('torx', 'hex'), ('hex', 'tee')):
            parts.append(swept_hull(np.vstack([roots[a], roots[b]]), env))
    if 'bigweb' in kinds:                                # only the T fan to the upper body, whole depth
        parts.append(swept_hull(np.vstack([roots['hex'], roots['tee']]), env))
    if 'cheek' in kinds:
        allp = np.vstack(list(roots.values()))
        slab = B.box(HALF-4., Y_BACK, -400, 4., 400, 800)
        raw = swept_hull(allp, env).common(slab)
        q = np.array([[vx.Point.x, vx.Point.y, vx.Point.z] for vx in raw.Vertexes])
        th = np.linspace(0, 2*math.pi, 12, endpoint=False); xr = EDGE_R*math.tan(math.radians(50))
        bic = np.vstack([np.c_[np.zeros(12), EDGE_R*np.cos(th), EDGE_R*np.sin(th)], [[xr, 0, 0], [-xr, 0, 0]]])
        parts.append(hull_solid((q[:, None, :]+bic[None, :, :]).reshape(-1, 3)).common(env).common(halfspace(V(0, Y_BACK, 0), V(0, 1, 0))))
    if not parts:
        return None
    G = fuse_all(parts); v0 = G.Volume
    G = G.cut(B.union(clearance(Lo, rep))).removeSplitter()
    if __import__('os').environ.get('HX4S_SOFT_WEB', '1') == '1':
        G = soften(G, lambda e: e.BoundBox.YMin > Y_BACK+.5 and e.BoundBox.XMax < HALF-.5, log, 'web cut', fillet_r=1.6, chamfer_r=1.2)
    log.append(dict(op='gussets', kinds=kinds, hull_mm3=round(v0), after_clearance_mm3=round(G.Volume)))
    return G


def font(): return str(FONT)


_CAP = {}


def size_for_cap(cap):
    if 'k' not in _CAP:
        ws = Part.makeWireString('H', font(), 10.)
        bb = Part.makeCompound([w for c in ws for w in (c if isinstance(c, list) else [c])]).BoundBox
        _CAP['k'] = 10./bb.YLength
    return cap*_CAP['k']


def engrave(text, size, centre, right, up, normal, depth, keep):
    """Straight 0.8 mm deboss (the owner paints the labels)."""
    faces = [Part.Face(w, 'Part::FaceMakerBullseye') for w in Part.makeWireString(text, font(), size) if w]
    sh = Part.makeCompound(faces); bb = sh.BoundBox
    sh.translate(V(-(bb.XMin+bb.XMax)/2, -(bb.YMin+bb.YMax)/2, 0))
    m = A.Matrix(right.x, up.x, normal.x, 0, right.y, up.y, normal.y, 0, right.z, up.z, normal.z, 0, 0, 0, 0, 1)
    sh = sh.copy(); sh.transformShape(m); sh.translate(centre+normal*3.)
    return Part.makeCompound([f.extrude(normal*-(3+3*depth)) for f in sh.Faces]).cut(keep)


def edge_dir(e):
    a, b = e.Vertexes[0].Point, e.Vertexes[-1].Point
    d = b-a
    if d.Length < 1e-6:
        return None
    d.normalize(); return d


def soften(shape, select, log, what, fillet_r=2., chamfer_r=1.2):
    """Owner: 'chamfer in Z, fillet in XY'. Edges standing vertical in the print (along installed x) get
    fillets; every other selected edge a chamfer, one edge at a time (OCC refuses most corner batches)."""
    def sharp(sh, e):
        if e.Length < 2.:
            return False
        fs = sh.ancestorsOfType(e, Part.Face)
        if len(fs) != 2:
            return False
        m = e.valueAt(.5*(e.FirstParameter+e.LastParameter))
        ns = [f.normalAt(*f.Surface.parameter(m)) for f in fs]
        return abs(ns[0].getAngle(ns[1])) > math.radians(25)
    out = shape; done = dict(chamfer=0, fillet=0)
    todo = [(e.valueAt(.5*(e.FirstParameter+e.LastParameter)), edge_dir(e)) for e in shape.Edges
            if select(e) and edge_dir(e) is not None and sharp(shape, e)]
    for m0, d0 in todo:
        cand = [e for e in out.Edges if edge_dir(e) is not None and abs(edge_dir(e).dot(d0)) > .999
                and (e.valueAt(.5*(e.FirstParameter+e.LastParameter))-m0).Length < .5]
        if not cand:
            continue
        kind = 'fillet' if abs(d0.x) > .85 else 'chamfer'
        for r in ((fillet_r, fillet_r*.6) if kind == 'fillet' else (chamfer_r, chamfer_r*.6)):
            try:
                t = (out.makeFillet(r, [cand[0]]) if kind == 'fillet' else out.makeChamfer(r, [cand[0]])).removeSplitter()
                if t.isValid() and len(t.Solids) == 1:
                    out = t; done[kind] += 1; break
            except Exception:  # noqa: BLE001
                pass
    log.append(dict(op=what+' edges', edges=len(todo), **done))
    return out


def receiver_grid(x0, x1, z0, pose='right-cheek'):
    """Owner, 2026-10-08: 'hook pegs every inch, locking pegs on the very bottom, and gravity load pegs in the
    other peg spots'. The reviewed peg profiles of common.receiver, unchanged, placed on every hole the plate
    covers: PF02 #9 upper hooks (with their side ribs) in every column of row 0, PF07 #5 locking hoops in every
    column of the lowest row, and the lower bearing peg (full board thickness, 120 deg bearing arcs) in every
    other hole. Plate x0..x1, z0..lip, Y 0.15..5.55 (the reviewed 5.4 mm wall), in common.receiver's frame."""
    G, P, PV, C = K.G, K.P, K.PV, K.C
    cols = [K.PITCH*i for i in range(-20, 21) if x0+6. <= K.PITCH*i <= x1-6.]
    if len(cols) % 2 == 0:                               # an even cell count puts holes on half-pitch offsets
        cols = [c+K.PITCH/2 for c in cols if x0+6. <= c+K.PITCH/2 <= x1-6.]
    rows = [k for k in range(0, 20) if K.row_z(k)-6. >= z0]
    hoop_row = rows[-1]; bearing_rows = rows[1:-1]; zl = K.row_z(hoop_row)
    path = G.fit_file(K.TOP['clamp_mm']); canonical = P.FIT_SOURCE
    P.FIT_SOURCE = PV.FIT_SOURCE = path
    try:
        fit = P.parse(path.read_bytes())
        shape = K.box(x0, K.PLATE_Y0, z0, x1-x0, K.PLATE_Y1-K.PLATE_Y0, K.PLATE_Z1-z0)
        reference = P.load_reference()
        upper = [q for q in reference.Solids if q.BoundBox.ZMax > -9.9]
        lower = [q for q in reference.Solids if q.BoundBox.ZMax < -9.9][0]
        reports = []
        for x in cols:
            ref = Part.makeCompound(upper+[lower]); ref.translate(V(x, 0, 0))
            shape, r = K.receive_pegs(ref, shape, include_lower=False); reports.append(r)
        elbow = reports[0]['peg_profile']['elbow_center_y_mm']
        add, cut = [], []; zu = fit['PEG_SEAT_DROP']
        for x in cols:
            for q in G.side_ribs(zu, K.TOP['upper_ribs_mm'], max(elbow, K.FACE-G.BOARD)+0.3, K.FACE+1.0, lead=G.UPPER_LEAD)[0]:
                q = q.copy(); q.translate(V(x, 0, 0)); add.append(q)
            for k in bearing_rows+[hoop_row]:
                loc = lower.copy(); loc.translate(V(x, 0, K.row_z(k)-K.row_z(1))); add.append(loc)
            for q in G.side_ribs(zl, K.BODY_RIBS, K.FACE-G.BOARD+0.2, K.FACE+1.0, lead=1.0)[0]:
                q = q.copy(); q.translate(V(x, 0, 0)); add.append(q)
            ha, hc, hinfo = K.hoop_geometry(zl, pose, True)
            for q in ha:
                q = q.copy(); q.translate(V(x, 0, 0)); add.append(K.turn(q, x, zl) if pose == 'right-cheek' else q)
            for q in hc:
                q = q.copy(); q.translate(V(x, 0, 0)); cut.append(K.turn(q, x, zl) if pose == 'right-cheek' else q)
        shape = shape.multiFuse(add).removeSplitter().cut(cut).removeSplitter()
        assert shape.isValid() and len(shape.Solids) == 1
        info = dict(fit_file=str(path.relative_to(P.ROOT)), top=K.TOP, columns_x_mm=cols,
                    plate=dict(x0=x0, x1=x1, y0=K.PLATE_Y0, y1=K.PLATE_Y1, z0=z0, z1=K.PLATE_Z1),
                    hoop=dict(K.HOOP, body_ribs_mm=K.BODY_RIBS, detail=hinfo),
                    rows=dict(hooks=[0], bearing=bearing_rows, hoop=[hoop_row]),
                    pegs=dict(hooks=len(cols), bearing=len(cols)*len(bearing_rows), locking=len(cols)),
                    predicted_clamp_interference_at_3p94_mm=-reports[0]['peg_profile']['predicted_clearance_at_3p94_board_mm'])
        return shape, info
    finally:
        P.FIT_SOURCE = PV.FIT_SOURCE = canonical


PEG_GRID = __import__('os').environ.get('HX4S_PEG_GRID', '1') == '1'


def build(quick=False):
    log = []
    Lo = SH.Layout(LAYOUT['x'])
    tools_d = Lo.tools
    bp = np.vstack([b[0] for b in Lo.bosses])
    zlo = float(np.min([t['tip'][2] for t in tools_d]))-20.; zhi = float(np.max([t['mouth'][2] for t in tools_d]))+12.
    zhi = max(zhi, zlo+80.)
    if PEG_GRID:
        # the receiver's top lip sits at the part's top (zhi); its plate stops 3 mm inside the rounded back plate,
        # which wraps it, so only the board side and the sharp top lip are the receiver's own faces
        top_local = K.PLATE_Z1+.325                     # common.receiver bounding-box top above its lip (side ribs)
        z0_local = (zlo-5.+3.)-(zhi-top_local)
        rec_raw, mount = receiver_grid(-HALF+3., HALF-3., z0_local)
    else:
        rec_raw, mount = K.receiver(REC_CELLS, 2, 'right-cheek', x0=-HALF, x1=HALF)
    receiver = rec_raw.mirror(V(0, 0, 0), V(1, 0, 0))           # left-cheek print: mirrored receiver (ASSUMED fit-equivalent)
    rb = receiver.BoundBox
    mount['z_shift'] = zhi-rb.ZMax
    receiver.translate(V(0, 0, zhi-(rb.ZMax)))
    rb = receiver.BoundBox
    if PEG_GRID:                                         # fillet the lip's front edge (off the board side)
        r_ = EDGE_R; yf = K.PLATE_Y1; zt = rb.ZMax-.325
        corner = Part.makeBox(4000, r_+1, r_+1, V(-2000, yf-r_, zt-r_)).cut(
            Part.makeCylinder(r_, 4000, V(-2000, yf-r_, zt-r_), V(1, 0, 0)))
        receiver = receiver.cut(corner).removeSplitter()
    env = B.box(-HALF, Y_BACK, zlo-5, 2*HALF, 300, zhi-zlo+5)
    rails, labels, roots = [], [], {}
    for s_ in SH.SETS:
        r_ = rail([t for t in tools_d if t['set'] == s_], env, s_, labels, roots)
        if __import__('os').environ.get('HX4S_SOFT', '0') == '1':
            r_ = soften(r_, lambda e: e.BoundBox.YMin > Y_BACK+.5, log, s_+' rail')
        rails.append(r_)
    # plate: the owner's edge rule as the rails (Minkowski with the bicone), back face flat on the board
    xr = EDGE_R*math.tan(math.radians(50))
    cpts = np.array([[sx, sy, sz] for sx in (-HALF+xr, HALF-xr) for sy in (Y_BACK-EDGE_R, Y_BACK+PLATE_T-EDGE_R)
                     for sz in (zlo-5+EDGE_R, zhi-EDGE_R)])
    th = np.linspace(0, 2*math.pi, 16, endpoint=False)
    bic = np.vstack([np.c_[np.zeros(16), EDGE_R*np.cos(th), EDGE_R*np.sin(th)], [[xr, 0, 0], [-xr, 0, 0]]])
    plate = hull_solid((cpts[:, None, :]+bic[None, :, :]).reshape(-1, 3)).common(halfspace(V(0, Y_BACK, 0), V(0, 1, 0)))
    rep_ = LAYOUT.get('rep') or SH.evaluate(LAYOUT['x'], True)[4]
    gs = gussets(roots, Lo, rep_, env, log)
    body = fuse_all([plate, receiver]+rails+([gs] if gs is not None else []))
    assert body.isValid() and len(body.Solids) == 1, ('body', len(body.Solids))
    log.append(dict(op='rails+plate', volume_mm3=round(body.Volume), z=[round(zlo, 1), round(zhi, 1)]))
    holes, tools, seats = [], [], []
    for t in tools_d:
        ax = v(t['u']); m = v(t['mouth'])
        hk = None
        if t['set'] == 'tee' and t['af'] >= TEE_KEYED_MIN:
            hk = (t['af']+2*SH.TEE_HEX_C, v(t['bar']))
        holes += socket(m, ax, t['bore'], t['D'], ring_w=1.6 if t['set'] != 'tee' else 2., hexkey=hk,
                        floor=(v(t['floor_p']), v(t['floor_n']), float(t['floor_depth'])))
        ur = v(t['u_rest'])                              # the tool rests leaned (study rest pose): open along that too
        if ur.getAngle(ax) > 1e-3:
            holes.append(Part.Face(teardrop(m, t['bore']+.8, ur)).extrude(ur*150.))
        seats.append(dict(set=t['set'], size=t['name'], mouth=list(m), axis=list(ax), depth=t['D'], radius=t['bore'],
                          radius_floor=SH.chamber_r(t), floor_deg=t['floor_deg'], pinch=round(float(t['pinch']), 2)))
    marks = []
    for L in labels:
        n = v(L['n']); c = v(L['centre'])
        try:
            marks.append(engrave(L['text'], size_for_cap(LABEL['cap']), c, v(L['right']), v(L['up']), n, LABEL['depth'],
                                 halfspace(c-n*LABEL['depth'], n*-1)))
        except Exception:  # noqa: BLE001
            marks.append(Part.Shape())
    body = body.cut(B.union(holes)).removeSplitter()      # drill after the receiver: nothing refills a bore
    for L, mk in zip(labels, marks):
        try:
            if mk.isNull():
                raise ValueError('no label solid')
            t = body.cut(mk)
            if (not t.isNull()) and t.isValid() and len(t.Solids) >= 1 and t.Volume > body.Volume-200:
                body = t
                continue
        except Exception:  # noqa: BLE001
            pass
        log.append(dict(op='label failed', text=L['text']))
    body = body.removeSplitter()
    if len(body.Solids) > 1 and sorted(so.Volume for so in body.Solids)[-2] < 1.:
        body = max(body.Solids, key=lambda so: so.Volume)
    shape = body
    assert shape.isValid() and len(shape.Solids) == 1, ('native', len(shape.Solids))
    rear = B.box(-300, -40, -400, 600, 40.15, 800)
    ra, rb_ = shape.common(rear), receiver.common(rear); delta = ra.cut(rb_).Volume+rb_.cut(ra).Volume
    assert delta < 1e-6, ('board-side geometry changed', delta)
    log.append(dict(op='board-side delta', mm3=delta))
    log.append(dict(op='done', volume_mm3=round(shape.Volume)))
    print('HX04-short geometry PASS', json.dumps(log), flush=True)
    return dict(shape=shape, receiver=receiver, mount=mount, tools=tools, seats=seats, finish=log, Lo=Lo, rails=rails)


BRACE_T = 1.6                                           # solid brace thickness, mm (4 perimeters' worth)
BULKHEAD_REACH = 6.                                     # a bulkhead reaches this far past the socket wall
PEG_ROOT_R = 4.5


def solid_zones(Lo, rails, mount, shape):
    """Owner, 2026-10-08: solid helpers should join the pockets to the walls - braces and strategic solid planes,
    not padded mass. Slicer zones printed at 100% infill:
      * a row shear web per rail: a BRACE_T plane through all its socket axes, containing the print's vertical
        (installed x), so it prints as an internal wall tying every socket to its neighbours, the rail ends and,
        through the rail's sweep, the back plate;
      * a socket bulkhead at every socket: a BRACE_T band of layers (normal = print vertical) out to
        BULKHEAD_REACH past the socket wall, tying the socket to the nearby rail walls all round;
      * a solid disc through the plate round every peg root.
    Each zone is clipped to its rail, so no solid mass lands in the webs or the open plate."""
    parts = []
    sets = SH.SETS
    for s_, rail in zip(sets, rails):
        T = [t for t in Lo.tools if t['set'] == s_]
        mids = np.array([np.asarray(t['mouth'])-np.asarray(t['u'])*t['D']/2 for t in T])
        ub = np.mean([np.asarray(t['u']) for t in T], axis=0); ub[0] = 0.; ub /= np.linalg.norm(ub)
        nrm = np.cross([1., 0, 0], ub); nrm /= np.linalg.norm(nrm)        # web normal: in y-z, across the axes
        c = mids.mean(axis=0)
        web = Part.makeBox(4000, 4000, BRACE_T, V(-2000, -2000, -BRACE_T/2))
        web.Placement = A.Placement(v(c), A.Rotation(V(0, 0, 1), v(nrm)))
        parts.append(web.common(rail))
        rb = rail.BoundBox
        for t in T:
            xm = float((np.asarray(t['mouth'])-np.asarray(t['u'])*t['D']/2)[0])
            m_ = np.asarray(t['mouth']); u_ = np.asarray(t['u']); R_ = SH.chamber_r(t)+WALL+BULKHEAD_REACH
            reach = hull_solid(np.vstack([ring(m_+u_*1., u_, R_, 24), ring(m_-u_*(t['floor_depth']+FLOOR+1.5), u_, R_, 24)]))
            parts.append(Part.makeBox(BRACE_T, rb.YLength+2, rb.ZLength+2, V(xm-BRACE_T/2, rb.YMin-1, rb.ZMin-1)).common(rail).common(reach))
    dz = mount.get('z_shift', 0.)
    for x in mount['columns_x_mm']:
        for k in sorted(set(mount['rows']['hooks']+mount['rows'].get('bearing', [])+mount['rows']['hoop'])):
            parts.append(Part.makeCylinder(PEG_ROOT_R, K.PLATE_Y1-K.PLATE_Y0+.2, V(-x, K.PLATE_Y0-.1, K.row_z(k)+dz), V(0, 1, 0)))
    bb = shape.BoundBox
    z = B.union([q for q in parts if q.Volume > 1e-3])
    return z.common(B.box(bb.XMin, bb.YMin, bb.ZMin, bb.XLength, bb.YLength, bb.ZLength)).removeSplitter()


def print_pose(shape):
    """Left-cheek print: rotate so +X (the user's left end) lies on the bed, then shift onto the plate."""
    m = A.Matrix(); m.rotateY(math.radians(90))
    s = shape.copy(); s.transformShape(m)
    bb = s.BoundBox; t = A.Matrix(); t.move(V(-bb.XMin, -bb.YMin, -bb.ZMin)); s.transformShape(t)
    return s, (t.multiply(m))


def hex_rod(a, b, af, bar):
    """Hex shaft from a to b (across flats af), clocked to the bar like the keyed bore (TBAR)."""
    d = b-a; L = d.Length; d.normalize()
    e1 = bar-d*bar.dot(d); e1.normalize(); e2 = d.cross(e1); R = af/math.sqrt(3)
    off = 0. if TBAR == 'corners' else math.radians(30)
    P = [a+e1*(R*math.cos(off+k*math.pi/3))+e2*(R*math.sin(off+k*math.pi/3)) for k in range(6)]
    return Part.Face(Part.makePolygon(P+[P[0]])).extrude(d*L)


def ref_tools(Lo):
    """Reference tool envelopes (sphere-swept segments from the layout study) as one FreeCAD compound. Keyed
    T-handle shafts are hex prisms (they sit in hex bores); everything else is round at the corner radius."""
    parts = []
    for t in Lo.tools:
        p, r = t['pts'], t['rr']
        runs, start = [], 0
        for i in range(1, len(p)+1):
            turn = False
            if 0 < i-start and i < len(p):
                d0 = p[start+1]-p[start] if i-start >= 1 and start+1 < len(p) else None
                d1 = p[i]-p[i-1]
                if d0 is not None and np.linalg.norm(d0) > 1e-9 and np.linalg.norm(d1) > 1e-9:
                    turn = (d0@d1)/(np.linalg.norm(d0)*np.linalg.norm(d1)) < .985      # the bend: a new straight run
            if i == len(p) or abs(r[i]-r[start]) > 1e-6 or np.linalg.norm(p[i]-p[i-1]) > 8 or turn:
                runs.append((start, i-1)); start = i
        keyed = t['set'] == 'tee' and t.get('af', 0) >= TEE_KEYED_MIN and len(runs) > 1
        for n_, (a, b) in enumerate(runs):
            if keyed and n_ == 0 and b > a:
                ba, bb = runs[-1]
                parts.append(hex_rod(v(p[a]), v(p[b]), t['af'], v(p[bb])-v(p[ba])))
                continue
            if b > a:
                d = v(p[b])-v(p[a])
                parts.append(Part.makeCylinder(float(r[a]), d.Length, v(p[a]), d))
            # flat at the socket floor (real key tips are flat), rounded elsewhere
            parts += ([] if a == 0 else [Part.makeSphere(float(r[a]), v(p[a]))])+[Part.makeSphere(float(r[b]), v(p[b]))]
    return Part.makeCompound(parts)


def ref_tool_list(Lo):
    class _L: pass
    out = []
    for t in Lo.tools:
        l = _L(); l.tools = [t]; out.append(ref_tools(l))
    return out


def quick_meshes(g, out):
    out.mkdir(parents=True, exist_ok=True)
    pp, m = print_pose(g['shape'])
    B.mesh(g['shape'], out/'installed.stl'); B.mesh(pp, out/'print.stl')
    if __import__('os').environ.get('HX4S_SOLID', '1') == '1':
        z = g['zones'] = solid_zones(g['Lo'], g['rails'], g['mount'], g['shape']); zp = z.copy(); zp.transformShape(m)
        B.mesh(zp, out/'print_solid.stl'); B.mesh(z, out/'installed_solid.stl')
    g['shape'].exportStep(str(out/'installed.step'))
    B.mesh(ref_tools(g['Lo']), out/'keys.stl')
    M = [[m.A11, m.A12, m.A13, m.A14], [m.A21, m.A22, m.A23, m.A24], [m.A31, m.A32, m.A33, m.A34], [0, 0, 0, 1]]
    (out/'pose.json').write_text(json.dumps([c for row in M for c in row]))
    bb = g['shape'].BoundBox
    print('quick meshes', out, 'volume', round(g['shape'].Volume), 'bbox', [round(x, 1) for x in (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)], flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--quick', type=Path, required=True); a = ap.parse_args()
    _G = build(True); quick_meshes(_G, a.quick)
    if __import__('os').environ.get('COUPON_OUT'):      # the fit coupon from this same build (no second build)
        import runpy; sys.modules['build_short'] = sys.modules['__main__']
        sys.argv = ['coupon.py', __import__('os').environ['COUPON_OUT']]
        runpy.run_path(str(HERE/'coupon.py'), run_name='__main__')
