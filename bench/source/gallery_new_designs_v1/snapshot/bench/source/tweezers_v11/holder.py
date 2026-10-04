"""v11 tweezer station (v11.3): v9/v10's receiver and pegs with the PF07 #5 hoop on the bottom
row, and the tweezers standing on edge in 15-degree trays on the right cheek.

Owner's design (2026-10-02):
- Print on the right cheek; nothing prints in the air but the pegs.
- Each tweezer stands on edge, points toward the board, heel out front. Its right
  (lower) arm rides the valley between a floor and the cheek. The floor is gravity
  down but 15 degrees up toward the left when facing the pegboard, so the tool leans
  into the cheek.
- A wedge on the floor sits in the crotch of the tweezer; the tool slides along the
  floor, points first, until the wedge impinges the crotch. The wedges are separate
  parts printed alongside and glued (CA) into slots in the floors.
- The tool leans on two low ribs, not the cheek face, so its points clear the cheek.
- The bottom pegs are PF07 #5 (hoop, 0.8 mm arm, 2.0 tip, even catch wall) with a
  thinner nose and ramp wall and a 0.4 mm root gusset, turned 90 degrees about the
  peg axis so the hoop lies in the cheek plane and flexes in the print layers.
- Minimal plastic without sacrificing looks, strength or function.

Coordinates as v9/v10: X lateral (the right cheek is at -X), Y out of the board
(pegs at Y < 0.15), Z up. Run with FreeCAD Python: python holder.py OUT_DIR
"""
from pathlib import Path
import hashlib
import json
import math
import sys

import FreeCAD as A
import Mesh
import MeshPart
import Part

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import peg_profile as P                      # noqa: E402
import peg_print_variant as PV               # noqa: E402
import peg_fit_ladder_v2 as G                # noqa: E402
import peg_fit_ladder_v4 as C                # noqa: E402
from peg_fit_ladder import box               # noqa: E402
from peg_interface import receive_pegs       # noqa: E402

V = A.Vector
NAME = 'part-solder-modules-tweezers__%s__edge-trays-right-cheek__fit-pf02c9-hoop5' % (sys.argv[2] if len(sys.argv) > 2 else 'v11p3')

# Receiver and pegs: exactly v9's, except the bottom row.
PITCH, FACE = 25.4, 0.15
COLS = [-12.7, 12.7]
PLATE = dict(x0=-24.4, x1=19.4, y0=0.15, y1=5.55, z0=-175.0, z1=5.12)
TOP = dict(upper_ribs_mm=0.50, clamp_mm=0.49)
BEARING_ROWS, HOOP_ROW = [2, 4], 6
HOOP = {'concept': 'HOOP', 'arm_mm': 0.8, 'tip_half': 2.0, 'even_catch_wall': True,
        'ramp_wall': True, 'nose_mm': 0.9, 'root_gusset_mm': 0.4}
BODY_RIBS = 0.30

# Cheek and trays.
CHEEK_X, CHEEK_T = PLATE['x0'], 3.0            # v11.1: 2.4 was "too flexy"
INNER = CHEEK_X + CHEEK_T                   # cheek face toward the tools
CANT = math.radians(15.0)
FLOOR_T = 2.4
# v11.3 (owner, on the printed v11.2: "Tweezer arm doesn't fit between crotch peg and cheek
# ... the tweezer just slides downhill until it hangs on the wedge ... This is an imaginary
# constraint turning into a real clash"): v11.2's lean ribs and the wedge both located the
# right arm, the wedge's front being the V's exact width beside the front rib, so the arm had
# zero clearance between them. v11.3 has no ribs: the tool slides down the 15 deg cant until
# its crotch hangs on the wedge, the only locator, and the right arm rides LEAN mm off the
# cheek face, leaving about 5 mm between the cheek and the wedge.
VARIANTS = {'v11p3': dict(lean=4.0, ribs=False, hoop_fix=True),
            'v11p2': dict(lean=3.5, ribs=True, hoop_fix=False),          # as printed
            'v11p2-noribs': dict(lean=3.5, ribs=False, hoop_fix=False)}  # printed, ribs snipped off
VARIANT = sys.argv[2] if len(sys.argv) > 2 else 'v11p3'
LEAN = VARIANTS[VARIANT]['lean']            # right arm's outer edge off the cheek face
RIBS = VARIANTS[VARIANT]['ribs']
RIB = LEAN                                  # v11.2 lean ribs stood LEAN proud of the cheek face
CONTACT_S = (30.0, 70.0)                    # tool stations (mm from the heel) on the ribs
FLOOR_S = (18.0, 76.0)                      # tool stations the floor spans
WEDGE_S = (31.0, 51.0)
WEDGE_BACK_RELIEF = 0.4                     # wedge narrower than the V at its back end, so
                                            # the crotch, not the tips' side, meets it first
SLOT_CLEAR = 0.15
POCKET_D = 1.5                              # blind wedge pocket, normal to the floor
GLUE_GAP = 0.1                              # wedge foot stops short of the pocket floor
CHAMFER_DEG = 50.0                          # pocket/foot chamfer on the print-top side, from horizontal
FLANGE_W, FLANGE_H = 2.0, 5.0               # cheek edge flanges (in-plane width, height off the cheek)
STRUT_W = 8.0
BRACE_RIB_W, BRACE_RIB_H = 2.0, 2.5          # rib standing proud along each window diagonal
GUSSET_L, GUSSET_T = 8.0, 2.4                 # cheek-to-plate corner webs (8: stays 1.1+ clear of the points)
GUSSET_Z = (-5.0, -47.5, -96.0, -158.0)     # plate solid there, no tool in the way
WEB_T = 2.4                                  # top/bottom plate-to-cheek webs
WEB_TOP_Y, WEB_BOTTOM_Y = 40.0, 70.0         # where each web meets the cheek's edge
TRAYS, TRAY_PITCH = 4, 23.0
TOP_FLOOR_Z = -66.0                         # valley height of the top tray
TIP_CLEAR = 3.0
TOOL = Path(__file__).resolve().parents[2] / 'reviews/v8-regen/tweezers_open_rest.stl'


def row_z(k):
    return 0.12-PITCH*k


def turn(shape, x, z, deg=-90):
    """Rotate about the peg axis (parallel to Y) through (x, z); -90 maps +X to +Z."""
    s = shape.copy(); s.rotate(V(x, 0, z), V(0, 1, 0), deg); return s


def rounded_window(x0, x1, z0, z1, r, y0, y1):
    """A slot through the plate (Y) with rounded corners, from x0..x1, z0..z1."""
    w = box(x0+r, y0, z0, x1-x0-2*r, y1-y0, z1-z0).fuse(box(x0, y0, z0+r, x1-x0, y1-y0, z1-z0-2*r))
    for cx, cz in [(x0+r, z0+r), (x1-r, z0+r), (x0+r, z1-r), (x1-r, z1-r)]:
        w = w.fuse(Part.makeCylinder(r, y1-y0, V(cx, y0, cz), V(0, 1, 0)))
    return w.removeSplitter()


def receiver():
    """v9's plate and pegs with the PF07 #5 hoop on the bottom row, from the shared v12
    receiver (solder_v12/common.py). v11.3: the install-arc hoop fix (root clipped to r 2.95,
    the turned hoop dropped 0.10 mm); with hoop_fix=False this is exactly v11.2's receiver
    (solder_v12/selftest_receiver.py)."""
    sys.path.insert(0, str(HERE.parent/'solder_v12'))
    import common as K
    shape, info = K.receiver(2, HOOP_ROW, 'right-cheek', bearing_rows=BEARING_ROWS,
                             x0=PLATE['x0'], x1=PLATE['x1'], z0=PLATE['z0'], z1=PLATE['z1'],
                             hoop_fix=VARIANTS[VARIANT]['hoop_fix'])
    # Plastic: open the plate between the occupied rows (0, 2, 4, 6).
    # Pointed at +X, the top when printing on the cheek, at 50 degrees: no bridge.
    for za, zb in [(-42.7, -14.0), (-93.5, -58.7), (-144.3, -109.5)]:
        shape = shape.cut(K.pointed_window(-18.4, 13.4, za, zb, '+X', angle_deg=math.degrees(math.atan(1.2))))
    return shape, info


# ---------------------------------------------------------------- tool placement
def tool_points():
    m = Mesh.Mesh(str(TOOL))
    return m, [(p.x, p.y, p.z) for p in m.Points]   # tool frame: x width (+x tips bend), y heel->tips, z opening


def slice_at(pts, s, w=0.4):
    return [p for p in pts if abs(p[1]-s) < w]


def outer_right(pts, s):
    return min(p[2] for p in slice_at(pts, s))


def gap(pts, s):
    sl = slice_at(pts, s)
    return min(p[2] for p in sl if p[2] > 0) - max(p[2] for p in sl if p[2] < 0)


def placement(pts):
    """Tool frame -> holder frame for the top tray, and the cheek-lean yaw."""
    z30, z70 = outer_right(pts, CONTACT_S[0]), outer_right(pts, CONTACT_S[1])
    phi = math.atan2(z30-z70, CONTACT_S[1]-CONTACT_S[0])
    c, s_ = math.cos(phi), math.sin(phi)

    def lin(p):                                      # (tx, ty, tz) -> holder, before translation
        X, Y, Z = p[2], -p[1], p[0]
        return (X*c-Y*s_, X*s_+Y*c, Z)
    lp = [lin(p) for p in pts]
    contact = lin((0, CONTACT_S[0], z30))
    tx = INNER+RIB-contact[0]
    ty = PLATE['y1']+TIP_CLEAR-min(q[1] for q in lp)
    t = math.tan(CANT)
    on_floor = [q for q, p in zip(lp, pts) if FLOOR_S[0] <= p[1] <= FLOOR_S[1]]
    rest = min(q[2]-((q[0]+tx)-INNER)*t for q in on_floor)
    tz = TOP_FLOOR_Z-rest
    pl = A.Placement(V(tx, ty, tz), A.Rotation(V(0, 0, 1), math.degrees(phi)).multiply(
        A.Rotation(A.Matrix(0, 0, 1, 0, 0, -1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1))))
    return pl, math.degrees(phi)


def floor_top(x, k):
    return TOP_FLOOR_Z-k*TRAY_PITCH+(x-INNER)*math.tan(CANT)


def tray(k, pl, pts):
    """Floor (with gusset) and two lean ribs for tray k; the wedge and its slot."""
    dz = -k*TRAY_PITCH
    held = [pl.multVec(V(*p)) for p in pts if FLOOR_S[0] <= p[1] <= FLOOR_S[1]]
    xmax = max(v.x for v in held)+1.5
    yb, yf = min(v.y for v in held)-1.0, max(v.y for v in held)+1.0
    tv = FLOOR_T/math.cos(CANT)
    section = [(CHEEK_X, floor_top(CHEEK_X, k)), (xmax, floor_top(xmax, k)),
               (xmax, floor_top(xmax, k)-tv), (INNER+4.0, floor_top(INNER+4.0, k)-tv),
               (INNER, floor_top(INNER, k)-tv-4.0), (CHEEK_X, floor_top(CHEEK_X, k)-tv-4.0)]
    vs = [V(x, yb, z) for x, z in section]
    floor = Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(0, yf-yb, 0))
    parts = [floor]
    for s in (CONTACT_S if RIBS else ()):
        c = pl.multVec(V(0, s, 0))
        zc = pl.multVec(V(0, s, 0)).z+dz
        parts.append(box(INNER-0.01, c.y-2.0, floor_top(INNER, k)-0.5, RIB+0.01, 4.0, zc+3.0-floor_top(INNER, k)))
    # Wedge in the tool frame: centred between the arms, the V's width at its front.
    g0, g1 = gap(pts, WEDGE_S[0]), gap(pts, WEDGE_S[1])
    h0, h1 = g0/2, g1/2-WEDGE_BACK_RELIEF
    for s in range(int(WEDGE_S[0])+1, int(WEDGE_S[1])):
        hs = h0+(h1-h0)*(s-WEDGE_S[0])/(WEDGE_S[1]-WEDGE_S[0])
        assert hs <= gap(pts, s)/2+1e-6, ('wedge wider than the V', s, hs, gap(pts, s))

    def prism(h_front, h_back, grow):
        prof = [(-h_front-grow, WEDGE_S[0]-grow), (h_front+grow, WEDGE_S[0]-grow),
                (h_back+grow, WEDGE_S[1]+grow), (-h_back-grow, WEDGE_S[1]+grow)]
        vs = [V(-30, y, z) for z, y in prof]          # tool frame: (tx, ty, tz)
        solid = Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(30+1.0, 0, 0))   # up to tx = +1.0
        solid = solid.transformGeometry(pl.toMatrix())
        solid.translate(V(0, 0, dz))
        return solid
    floor_band = floor.copy()
    def below(depth):
        """Half-space under a plane parallel to the floor top, depth below it (normal)."""
        z0 = floor_top(INNER, k)-depth/math.cos(CANT)
        b = box(INNER-200, -200, z0-400, 400, 600, 400)
        b.rotate(V(INNER, 0, z0), V(0, 1, 0), -math.degrees(CANT))
        return b
    # v11.1 (owner): "wedge pocket should be a pocket - not a through hole. That way you
    # always have wall to web to so this isn't a pure cantilever." The through-slot's top
    # edge printed as spaghetti; a blind pocket keeps its back wall under every layer.
    # Owner: a 90 on the bed side and a chamfer on the other, "so the back wall is
    # supporting a 45 chamfer on the socket growing upwards". Printed on the cheek, +X is
    # up: the pocket's cheek-side wall stays vertical, and its far side slopes down into
    # the floor at CHAMFER_DEG, so no layer of the socket hangs over air.
    def cavity_side(grow):
        """Half-space on the cheek side of the chamfer plane through the pocket's far
        (+X) opening edge, for the wedge outline grown by grow."""
        ends = []
        for ty, tz in [(WEDGE_S[0]-grow, h0+grow), (WEDGE_S[1]+grow, h1+grow)]:
            q = pl.multVec(V(0, ty, tz))
            ends.append(V(q.x, q.y, floor_top(q.x, k)))
        a = math.radians(CHAMFER_DEG)
        w = V(-math.sin(a), 0, -math.cos(a))           # into the floor, falling in the print pose
        d = ends[1]-ends[0]
        m = d.cross(w); m.normalize()
        if m.x < 0:
            m = m*-1.0                                  # toward the material beyond the far edge
        e1 = V(d); e1.normalize()
        e2 = m.cross(e1); e2.normalize()
        c = ends[0]
        sq = [c+e1*300+e2*300, c-e1*300+e2*300, c-e1*300-e2*300, c+e1*300-e2*300]
        return Part.Face(Part.makePolygon(sq+[sq[0]])).extrude(m*-300.0)
    body = prism(h0, h1, 0.0)
    foot = body.common(below(0.0)).cut(below(POCKET_D-GLUE_GAP)).common(cavity_side(0.0))
    wedge = body.cut(below(0.0)).fuse(foot).removeSplitter()
    slot = (prism(h0, h1, SLOT_CLEAR).common(floor_band).cut(below(POCKET_D))
            .common(cavity_side(SLOT_CLEAR)).removeSplitter())
    return parts, slot, wedge, dict(xmax=xmax, y_back=yb, y_front=yf, wedge_front_mm=2*h0, wedge_back_mm=2*h1)


def cheek(trays):
    y1 = max(t['y_front'] for t in trays)
    z_lo = floor_top(INNER, TRAYS-1)-FLOOR_T/math.cos(CANT)-4.0-FLANGE_W-2.0   # below the gusset and flange
    z_hi = TOP_FLOOR_Z+24.0                                                     # top flange clears the top tool
    outline = [(PLATE['y0'], PLATE['z0']), (PLATE['y0'], PLATE['z1']), (PLATE['y1']+4, PLATE['z1']),
               (y1, z_hi), (y1, z_lo), (PLATE['y1']+4, PLATE['z0'])]
    vs = [V(CHEEK_X, y, z) for y, z in outline]
    sheet = Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(CHEEK_T, 0, 0))
    # Plastic: open the cheek behind the trays, where only the points hover, leaving
    # 9 mm rails that follow the tapered outline.
    yb = min(t['y_back'] for t in trays)
    ya, yz = PLATE['y1']+12, yb-8

    def lo(y):
        return PLATE['z0']+(z_lo-PLATE['z0'])*(y-PLATE['y1']-4)/(y1-PLATE['y1']-4)

    def hi(y):
        return PLATE['z1']+(z_hi-PLATE['z1'])*(y-PLATE['y1']-4)/(y1-PLATE['y1']-4)
    quad = [(ya, lo(ya)+9), (yz, lo(yz)+9), (yz, hi(yz)-9), (ya, hi(ya)-9)]
    ws = [V(CHEEK_X-1, y, z) for y, z in quad]
    window = Part.Face(Part.makePolygon(ws+[ws[0]])).extrude(V(CHEEK_T+2, 0, 0))
    sheet = sheet.cut(window)
    # v11.1 stiffness (owner: "the cheek is too flexy"): a diagonal strut triangulates the
    # window, flanges along the top and bottom edges make the cheek a channel, and a fillet
    # stiffens the cheek-to-plate joint. All of them rise straight off the bed.
    def band(p, q, inward, width, height, extend=0.0):
        dy, dz = q[0]-p[0], q[1]-p[1]; L = math.hypot(dy, dz); uy, uz = dy/L, dz/L
        ny, nz = -uz, uy
        if ny*inward[0]+nz*inward[1] < 0:
            ny, nz = -ny, -nz
        a = (p[0]-uy*extend, p[1]-uz*extend); b = (q[0]+uy*extend, q[1]+uz*extend)
        poly = [a, b, (b[0]+ny*width, b[1]+nz*width), (a[0]+ny*width, a[1]+nz*width)]
        pv = [V(CHEEK_X+0.01, y, z) for y, z in poly]
        return Part.Face(Part.makePolygon(pv+[pv[0]])).extrude(V(height-0.01, 0, 0))
    q0, q1, q2, q3 = quad
    mid = ((q3[0]+q1[0])/2, (q3[1]+q1[1])/2)
    # Owner: "gusset the wall with some diagonal struts for stiffness". Both window
    # diagonals (an X), each a flat 8 mm strut with a rib standing BRACE_RIB_H proud of
    # the cheek face (a T section, for out-of-plane stiffness); behind the trays, where
    # the hovering points stay farther from the cheek.
    strut = None
    for a_, b_ in [(q3, q1), (q0, q2)]:
        for side in [(0, 1), (0, -1)]:
            piece = band((a_[0], a_[1]), (b_[0], b_[1]), side, STRUT_W/2, CHEEK_T, extend=6.0)
            rib = band((a_[0], a_[1]), (b_[0], b_[1]), side, BRACE_RIB_W/2, CHEEK_T+BRACE_RIB_H, extend=-2.0)
            piece = piece.fuse(rib)
            strut = piece if strut is None else strut.fuse(piece)
    centre = (sum(y for y, _ in outline)/len(outline), sum(z for _, z in outline)/len(outline))
    flanges = []
    for p, q in [(outline[1], outline[2]), (outline[2], outline[3]), (outline[0], outline[5]), (outline[5], outline[4])]:
        inward = (centre[0]-(p[0]+q[0])/2, centre[1]-(p[1]+q[1])/2)
        flanges.append(band(p, q, inward, FLANGE_W, CHEEK_T+FLANGE_H))
    fillet = Part.Face(Part.makePolygon([V(INNER-0.01, PLATE['y1']-0.01, 0), V(INNER+5, PLATE['y1']-0.01, 0),
                                         V(INNER-0.01, PLATE['y1']+5, 0), V(INNER-0.01, PLATE['y1']-0.01, 0)]))
    fillet = fillet.extrude(V(0, 0, PLATE['z1']-PLATE['z0']-6)); fillet.translate(V(0, 0, PLATE['z0']+3))
    # Corner gussets between the cheek and the receiver plate, in bands with no tool.
    gussets = []
    for zg in GUSSET_Z:
        tri = [V(INNER-0.01, PLATE['y1']-0.01, zg-GUSSET_T/2), V(INNER+GUSSET_L, PLATE['y1']-0.01, zg-GUSSET_T/2),
               V(INNER-0.01, PLATE['y1']+GUSSET_L, zg-GUSSET_T/2)]
        gussets.append(Part.Face(Part.makePolygon(tri+[tri[0]])).extrude(V(0, 0, GUSSET_T)))
    # Owner's sketch: big gussets from the plate's far corners to the cheek's top and bottom
    # edges, closing the plate-cheek corner into a box section against sideways wag. Each
    # web's plane contains X, so printed on the cheek it is a vertical wall leaning on the
    # plate with its free edge as a sloping top: no overhang.
    def edge_z(p, q, y):
        return p[1]+(q[1]-p[1])*(y-p[0])/(q[0]-p[0])
    webs = []
    for p, q, ye, up in [(outline[2], outline[3], WEB_TOP_Y, -1), (outline[5], outline[4], WEB_BOTTOM_Y, 1)]:
        zc = p[1]                                        # plate's top (or bottom) edge height
        ze = edge_z(p, q, ye)                            # the cheek edge where the web lands
        slope = (ze-zc)/(ye-PLATE['y1'])

        def zs(y):
            return zc+(y-PLATE['y1'])*slope
        y0 = PLATE['y1']-2.5                             # start inside the plate to merge
        tri = [V(CHEEK_X+0.01, y0, zs(y0)), V(PLATE['x1']-0.3, y0, zs(y0)), V(CHEEK_X+0.01, ye, zs(ye))]
        n = (tri[1]-tri[0]).cross(tri[2]-tri[0]); n.normalize()
        if (n.z > 0) != (up > 0):
            n = n*-1.0                                   # into the rack: down from the top edge, up from the bottom
        web = Part.Face(Part.makePolygon(tri+[tri[0]])).extrude(n*WEB_T)
        clip = box(-100, -100, PLATE['z0'], 200, 400, PLATE['z1']-PLATE['z0'])   # never past the plate's ends
        webs.append(web.common(clip))
    return sheet.multiFuse([strut, fillet]+flanges+gussets+webs).removeSplitter()


def print_pose(shape):
    """Right cheek (-X) on the bed."""
    s = shape.copy(); s.rotate(V(), V(0, 1, 0), -90)
    b = s.BoundBox; s.translate(V(-b.XMin, -b.YMin, -b.ZMin))
    return s


def write(shape, path, lin=0.005):
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=lin, AngularDeflection=0.087, Relative=False)
    for method in ['removeDuplicatedPoints', 'removeDuplicatedFacets', 'harmonizeNormals']:
        getattr(mesh, method)()
    mesh.write(str(path))
    read = Mesh.Mesh(str(path))
    assert read.isSolid() and not read.hasNonManifolds(), path
    return dict(file=path.name, facets=read.CountFacets,
                volume_error_fraction=abs(abs(read.Volume)-shape.Volume)/shape.Volume,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    tool_mesh, pts = tool_points()
    pl, yaw = placement(pts)
    host, info = receiver()
    trays, slots, wedges, extras = [], [], [], []
    for k in range(TRAYS):
        parts, slot, wedge, t = tray(k, pl, pts)
        extras += parts; slots.append(slot); wedges.append(wedge); trays.append(t)
    shape = host.multiFuse([cheek(trays)]+extras).removeSplitter()
    shape = shape.cut(slots).removeSplitter()
    assert shape.isValid() and len(shape.Solids) == 1, (shape.isValid(), len(shape.Solids))
    for w in wedges:
        assert w.isValid() and len(w.Solids) == 1
    shape.exportStep(str(out/f'{NAME}__installed.step'))
    files = [write(shape, out/f'{NAME}__installed.stl')]
    files.append(write(print_pose(shape), out/f'{NAME}__print-right-cheek.stl'))
    # Tools as placed, and the glued wedges in place.
    for k in range(TRAYS):
        m = tool_mesh.copy(); mp = A.Placement(pl); mp.move(V(0, 0, -k*TRAY_PITCH))
        m.Placement = mp; m.write(str(out/f'{NAME}__tool-{k+1}.stl'))
        wedges[k].exportStep(str(out/f'{NAME}__wedge-{k+1}__installed.step'))
        write(wedges[k], out/f'{NAME}__wedge-{k+1}__installed.stl', lin=0.005)
    # Wedge print pose: lie it on its tool-right tapered face.
    w = wedges[0].copy()
    inv = pl.inverse(); w = w.transformGeometry(inv.toMatrix())       # back to the tool frame
    h0, h1 = trays[0]['wedge_front_mm']/2, trays[0]['wedge_back_mm']/2
    n = V(0, -(h1-h0), -(WEDGE_S[1]-WEDGE_S[0])); n.normalize()       # tool-right tapered face, outward
    w = w.transformGeometry(A.Placement(V(), A.Rotation(n, V(0, 0, -1))).toMatrix())
    b = w.BoundBox; w.translate(V(-b.XMin, -b.YMin, -b.ZMin))
    files.append(write(w, out/f'{NAME}__wedge__print.stl', lin=0.005))
    info.update(name=NAME, tool=str(TOOL.name), tool_yaw_deg=yaw, trays=trays, tray_pitch_mm=TRAY_PITCH,
                cant_deg=15.0, rib_mm=RIB, contact_stations_mm=CONTACT_S, floor_stations_mm=FLOOR_S,
                wedge_stations_mm=WEDGE_S, slot_clearance_mm=SLOT_CLEAR, cheek_thickness_mm=CHEEK_T,
                floor_thickness_mm=FLOOR_T, volume_mm3=shape.Volume, wedge_volume_mm3=wedges[0].Volume,
                placement=dict(base=[pl.Base.x, pl.Base.y, pl.Base.z], rotation=list(pl.Rotation.Q)), files=files)
    (out/f'{NAME}__design.json').write_text(json.dumps(info, indent=1))
    print(json.dumps({k: info[k] for k in ('tool_yaw_deg', 'volume_mm3', 'wedge_volume_mm3', 'trays')}, indent=1))


if __name__ == '__main__':
    main(Path(sys.argv[1]))
