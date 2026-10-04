"""v12 desoldering-braid module: a canted stub axle under a top-and-back hood, printed on the right cheek.

Owner's goals (brief 2026-10-02) and how this module meets them (rev 2, sourced bobbin envelope):
- Covers every common braid bobbin, not a guess (TOOLS.md section 2: OD 38-52, thickness 6-12,
  bore 7-10.5; MG 39.9, Chemtronics 44.5, Techspray 45, generic cross-hub 45.7, goot 51). The
  hood is open at the bottom (IMPACTS 2.2 option 1b): it wraps only the top and back of the
  roll, with R_IN 27.5, so a 52 mm roll's rim hangs free below while the module stays small.
  The hood is still the cheek's stiffening flange and the guard against things falling from
  the snips above.
- The user pulls braid off and snips it. The roll stands on edge facing sideways (its axis runs
  across the board, +X) on a stub axle that grows out of the right cheek: the braid pays off
  the roll's front rim toward the user, and the pull lies in the roll's plane, so it spins the
  roll and presses the bore onto the axle.
- The roll must not walk off. The axle is canted 15 degrees up toward its tip (v11's tweezer
  cant), so the roll leans into the cheek onto a 10 mm hub seat. Beyond the widest roll a
  0.8 mm lip on the axle's top line (where the hanging bore rests) blocks it: nothing flexes;
  to pass, the roll must be lifted 0.8 mm, the lift-and-slide the user already makes. The
  lip's keeper is a V nose pointing at the roll: its two faces are 50 degree print-down ramps
  (printable) that push sideways, not up, and the nose edge stands 65 degrees off the axle, so
  a sideways brush cannot climb it. Its tip side is a 30 degree loading ramp.
- 5.6 mm axle (PIN_R 2.8): a 7 mm cross-hub bore passes pin + lip with 0.6 mm to spare.
- 10 mm hub seat (HUB_R 5): sits inside every hub ring (12-16), so Chemtronics' domed face
  bears right whichever way round it goes on.
- Tool-free swap: lift the roll a millimetre and slide it off the axle tip (one motion); push
  a new one on over the loading ramp and let go.
- Print: the right cheek (-X) is the bed. The hub, axle and hood lean 15 degrees off vertical;
  the plate window has a 50 degree pointed roof at +X; the plate's free corners have
  45 degree chamfers; a flange along the cheek's lower edge stands straight up. Nothing prints
  in the air but the pegs.
- Receiver: hooks on row 0, the PF07 #5 hoop on row 1 (with the shared install-arc fix).

Coordinates as v9-v12 (common.py): +X is the user's LEFT facing the board, the right cheek is
-X. Run: FreeCAD python braid.py OUT_DIR
"""
from pathlib import Path
import json
import math
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as K                            # noqa: E402
import FreeCAD as A                           # noqa: E402
import Mesh                                   # noqa: E402
import Part                                   # noqa: E402

V = A.Vector
NAME = 'part-solder-braid__v12__right-cheek__fit-pf02c9-hoop5'
TITLE = 'Braid roll v12'
POSE = 'right-cheek'
CELLS, HOOP_ROW = 2, 1

# Bobbin envelope (TOOLS.md 2.2): the stand-ins below are built from these, not from the B6 proxy.
OD_MIN, OD_MAX = 38.0, 52.0
W_MIN, W_MAX = 6.0, 12.0
BORE_MIN, BORE_MAX = 7.0, 10.5

HW = K.half_width(CELLS)                    # 24.4
CHEEK_X0, CHEEK_T = -HW, 3.0
CHEEK_X1 = CHEEK_X0+CHEEK_T                 # the cheek's inner face
CANT = 15.0                                 # axle rises toward +X: the roll leans into the cheek
CA, SA = math.cos(math.radians(CANT)), math.sin(math.radians(CANT))
AX = V(CA, 0, SA)                           # axle direction
E1 = V(0, 1, 0)                             # front (toward the user), theta = 0
E2 = V(-SA, 0, CA)                          # up in the roll's plane, theta = 90
R_IN, WALL = 27.5, 2.4                      # hood: 52 mm roll keeps 1.5 back / 2.2 top
R_OUT = R_IN+WALL
YC = K.PLATE_Y1+R_IN                        # hood's inner back face is the plate's front face
Z0 = -27.2                                  # axle height at the cheek face: hood top stays under the lip
P0 = V(CHEEK_X1, YC, Z0)
HUB_R, FLARE_R = 5.0, 9.0                   # 10 mm seat inside every hub ring; 45 deg flare into the cheek
U_SEAT = 8.5                                # seat face: a 52 mm roll's leaning top clears the cheek by 1.6
PIN_R = 2.8                                 # 5.6 mm axle
LIP_H, LIP_W = 0.8, 2.0                     # retention lip on the top line: height, width across
U_KEEP = U_SEAT+W_MAX+0.6                   # V nose of the lip, 0.6 past the widest roll's face
LIP_FLAT = 2.0                              # lip top length from the nose
LOAD_RAMP = 30.0                            # loading ramp toward the tip (deg from the axle)
NOSE_RISE, V_ARM = 10.0, 50.0               # print: nose edge rises 10 deg outward; V faces 50 deg
U_RAMP_END = U_KEEP+LIP_FLAT+LIP_H/math.tan(math.radians(LOAD_RAMP))
PIN_LEAD = 1.6
PIN_TIP = U_RAMP_END+1.0+PIN_LEAD           # 1 mm of plain pin past the ramp, then the cone lead
U_RIM, RIM_CH = U_SEAT+4.0, 0.6             # hood covers the roll's inner 4 mm; rim chamfer
HOOD_TH = (50.0, 180.0)                     # hood arc: front-top to the back (theta 0 = front)
FOOT = 0.6                                  # cheek outline proud of the hood
FLANGE_H, FLANGE_T = 6.0, 2.4               # lower-edge flange: height off the cheek, thickness
WEB_H, WEB_T = 7.0, 2.4                     # hub webs: max height off the cheek, thickness
PLATE_Z0 = K.row_z(HOOP_ROW)-6.0
WIN_X, WIN_Z = (-8.0, 21.0), (-20.0, -5.0)          # plate window (holder X, Z)
CORNER_CH = 4.0                                     # chamfer on the plate's free corners


def ax(u, r=0.0, th=0.0):
    t = math.radians(th)
    return P0+AX*u+E1*(r*math.cos(t))+E2*(r*math.sin(t))


def revolve(profile, th0, sweep):
    """Revolve a closed (u, r) profile about the axle, from th0 through sweep degrees."""
    pts = [ax(u, r, th0) for u, r in profile]
    face = Part.Face(Part.makePolygon(pts+[pts[0]]))
    return face.revolve(P0, AX, sweep)


def above(x):
    return K.box(x, -100, -200, 300, 400, 400)


def hull(points):
    pts = sorted(set((round(p[0], 4), round(p[1], 4)) for p in points))

    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1]+hi[:-1]


def cheek():
    """The bed: the hood's footprint (the tilted hood cut by the cheek face, an ellipse arc),
    the hub flare's footprint and the plate edge, hulled: the cheek runs straight from the
    plate to the hood and round the hub."""
    ry = R_OUT+FOOT
    rz = ry/CA
    th0 = HOOD_TH[0]-math.degrees(WALL/2/((R_IN+R_OUT)/2))-4.0     # past the bullnose
    arc = [(YC+ry*math.cos(math.radians(t)), Z0+rz*math.sin(math.radians(t)))
           for t in [th0+(HOOD_TH[1]-th0)*i/60 for i in range(61)]]
    fl = []
    for u in (-4.0, 0.0):
        for t in range(0, 360, 6):
            p = ax(u, FLARE_R+FOOT, t)
            fl.append((p.y, p.z))
    outline = hull(arc+fl+[(K.PLATE_Y0, K.PLATE_Z1), (K.PLATE_Y0, PLATE_Z0)])
    return K.poly_prism(outline, 'x', CHEEK_X0, CHEEK_X1), outline


def lower_flange(outline):
    """An L flange along the cheek's lower edge, from the plate's bottom corner to the hub: it
    stands FLANGE_H off the cheek (a wall in the print), inside the roll's inner-face
    clearance (8.2 mm or more below the axle), and turns the cheek's open lower edge into a
    channel section."""
    # Follow the outline's bottom edge (plate corner -> tangent on the flare footprint), so the
    # flange's outer face is the cheek edge; it stands on the bed through the cheek.
    p = (K.PLATE_Y0, PLATE_Z0)
    i = min(range(len(outline)), key=lambda k: (outline[k][0]-p[0])**2+(outline[k][1]-p[1])**2)
    q = max((outline[(i-1) % len(outline)], outline[(i+1) % len(outline)]), key=lambda v: v[0])
    assert math.hypot(q[0]-p[0], q[1]-p[1]) > 10, (p, q)
    f = K.band(p, q, (0.0, 1.0), FLANGE_T, CHEEK_X0, CHEEK_X1+FLANGE_H)
    # Its free end tapers at 45 deg down into the cheek under the hub (faces up in the print).
    return f.cut(halfspace(V(CHEEK_X1, q[0], 0.0), V(-1.0, -1.0, 0.0)))


def webs(outline):
    """Two webs on the cheek's inner face crossing at the hub (FEA: the cheek's out-of-plane
    bending round the hub was the compliance): one runs back to the plate at the axle's
    height (wag, pull), one runs from the cheek's lower edge up toward the hood (press). Both
    stand on the bed through the cheek and are trimmed 1.5 mm under the widest roll's leaning
    inner face (the plane u = U_SEAT - 1.5), so the roll never touches them."""
    zb = min(z for y, z in outline if abs(y-YC) < 3.0)+1.0
    h = K.band((K.PLATE_Y1-0.5, Z0-WEB_T/2), (YC, Z0-WEB_T/2), (0.0, 1.0), WEB_T, CHEEK_X0, CHEEK_X1+WEB_H)
    v = K.band((YC-WEB_T/2, zb), (YC-WEB_T/2, Z0+R_IN/CA), (1.0, 0.0), WEB_T, CHEEK_X0, CHEEK_X1+WEB_H)
    clear = halfspace(P0+AX*(U_SEAT-1.5), -AX)
    return [h.cut(clear), v.cut(clear)]


def post(base, r, u0, u1, ch):
    """A round post parallel to the axle from u0 to u1 with a ch chamfer on its tip."""
    prof = [(u0, 0.0), (u0, r), (u1-ch, r), (u1, r-ch), (u1, 0.0)]
    pts = [base+AX*u+E1*q for u, q in prof]
    return Part.Face(Part.makePolygon(pts+[pts[0]])).revolve(base, AX, 360.0)


def hood():
    """Round the roll's top and back only (theta 50 to 180), open at the front and the bottom so
    the rim of any roll up to 52 mm hangs free; the front end is rounded (bullnose); the back
    end runs into the plate."""
    prof = [(-12.0, R_IN), (U_RIM-RIM_CH, R_IN), (U_RIM, R_IN+RIM_CH), (U_RIM, R_OUT-RIM_CH),
            (U_RIM-RIM_CH, R_OUT), (-12.0, R_OUT)]
    r_mid = (R_IN+R_OUT)/2
    d_end = math.degrees(WALL/2/r_mid)
    th0 = HOOD_TH[0]+d_end
    d = revolve(prof, th0, HOOD_TH[1]-th0)
    nose = post(ax(0.0, r_mid, th0), WALL/2, -12.0, U_RIM, RIM_CH)
    return d.fuse(nose).removeSplitter().common(above(CHEEK_X1-0.05))


def plate_windows():
    """Plastic: a pointed window (point at +X, the print top, 50 deg roof) in the plate's
    free left half, between the left column's hook and hoop, clear of the peg roots and of the
    hood's join to the plate."""
    w = K.pointed_window(WIN_X[0], WIN_X[1], WIN_Z[0], WIN_Z[1], '+X')
    w = w.cut(K.peg_keepout(CELLS, HOOP_ROW))
    # The plate's two free corners (far from the cheek) get 45 deg chamfers: printed on the
    # cheek they face up, so they need nothing under them.
    e, ch = 0.5, CORNER_CH
    corners = [K.poly_prism([(HW-ch, K.PLATE_Z1+e), (HW+e, K.PLATE_Z1+e), (HW+e, K.PLATE_Z1-ch)], 'y', -0.5, K.PLATE_Y1+0.5),
               K.poly_prism([(HW-ch, PLATE_Z0-e), (HW+e, PLATE_Z0-e), (HW+e, PLATE_Z0+ch)], 'y', -0.5, K.PLATE_Y1+0.5)]
    return Part.makeCompound([w]+corners)


def halfspace(point, normal, size=40.0):
    """A big box filling the side of the plane (point, normal) that the normal points AWAY from."""
    n = V(normal); n.normalize()
    b = Part.makeBox(2*size, 2*size, size)
    b.translate(V(-size, -size, -size))
    b.Placement = A.Placement(point, A.Rotation(V(0, 0, 1), n)).multiply(b.Placement)
    return b


def print_to_holder(d):
    """Print-pose direction -> holder direction (right cheek: print x = -Z, print z = X)."""
    return V(d[2], d[1], -d[0])


def lip():
    """0.8 mm retention lip on the axle's top line (+E2), where the hanging bore rests.
    - Keeper (faces the roll, print-down): a V nose. In the print its two faces rise 50 deg
      from horizontal on either side (print-down ramps, no overhang) and the nose edge rises
      10 deg outward, so the lip's lowest point is on the axle (no island). Seen by the roll,
      the faces push sideways, not up, and the nose edge stands 65 deg off the axle.
    - Top: flat at r 3.6, 2.0 wide (a 7 mm bore lifted clears its corners by 0.4).
    - Tip side: a 30 deg loading ramp, so pushing a roll on lifts it over the lip."""
    r_top = PIN_R+LIP_H
    u0 = U_KEEP-1.5
    prof = [(u0, 1.2), (u0, r_top), (U_KEEP+LIP_FLAT, r_top), (U_RAMP_END+0.3/math.tan(math.radians(LOAD_RAMP)), PIN_R-0.3),
            (U_RAMP_END+0.6, 1.2)]
    base = P0-E1*(LIP_W/2)
    pts = [base+AX*u+E2*r for u, r in prof]
    body = Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(E1*LIP_W)
    b = ax(U_KEEP, PIN_R, 90.0)                        # nose base, on the axle's top line
    eps, dl = math.radians(NOSE_RISE), math.radians(V_ARM)
    edge = print_to_holder((-math.cos(eps), 0.0, math.sin(eps)))
    for sgn in (1, -1):
        arm = print_to_holder((0.0, sgn*math.cos(dl), math.sin(dl)))
        n = edge.cross(arm)
        if n.x < 0:                                    # orient into the lip (print up = holder +X)
            n = -n
        body = body.cut(halfspace(b, n))
    return body


def axle():
    prof = [(-4.0, 0.0), (-4.0, FLARE_R), (0.0, FLARE_R), (FLARE_R-HUB_R, HUB_R), (U_SEAT, HUB_R),
            (U_SEAT, PIN_R), (PIN_TIP-PIN_LEAD, PIN_R), (PIN_TIP, PIN_R-PIN_LEAD), (PIN_TIP, 0.0)]
    a = revolve(prof, 0.0, 360.0).fuse(lip()).removeSplitter()
    return a.common(above(CHEEK_X0))


# ---------------------------------------------------------------- bobbin stand-ins
def roll_mesh(R, w, rb, dome=None, n=120):
    """A bobbin as a closed triangle mesh in local coordinates: axis +z, the inner face (toward
    the cheek) at z = 0, the outer face at z = w. dome=(r_flat, h): the inner face is flat out
    to r_flat (the hub ring) and recedes linearly by h at the rim (Chemtronics' domed face
    loaded dome-in). Rings every ~1 mm so seat and axle contacts are sampled."""
    def zin(r):
        if not dome or r <= dome[0]:
            return 0.0
        return dome[1]*(r-dome[0])/(R-dome[0])
    nr = max(2, int(math.ceil(R-rb)))
    radii = [rb+(R-rb)*i/nr for i in range(nr+1)]
    if dome and dome[0] not in radii:
        radii = sorted(radii+[dome[0]])
    th = [2*math.pi*j/n for j in range(n)]
    tris = []

    def ring(r, z):
        return [(r*math.cos(t), r*math.sin(t), z) for t in th]

    def strip(a, b, flip):
        for j in range(n):
            k = (j+1) % n
            q = (a[j], a[k], b[k], b[j])
            if flip:
                q = q[::-1]
            tris.append([q[0], q[1], q[2]]); tris.append([q[0], q[2], q[3]])
    inner = [ring(r, zin(r)) for r in radii]
    outer = [ring(r, w) for r in radii]
    for i in range(len(radii)-1):
        strip(inner[i], inner[i+1], False)            # inner face, normal -z
        strip(outer[i], outer[i+1], True)             # outer face, normal +z
    for r, zs, flip in ((rb, zin(rb), True), (R, zin(R), False)):
        m = max(1, int(math.ceil(w-zs)))
        rings = [ring(r, zs+(w-zs)*i/m) for i in range(m+1)]
        for i in range(m):
            strip(rings[i], rings[i+1], flip)
    mesh = Mesh.Mesh(tris)
    mesh.harmonizeNormals()
    if mesh.Volume < 0:
        mesh.flipNormals()
    return mesh


ROLLS = [
    # id, OD, width, bore, dome, removal lift (the hanging bore rises this much to clear the lip)
    dict(id='bobbin-52x12-bore7', od=OD_MAX, w=W_MAX, bore=BORE_MIN, dome=None, lift=1.2,
         why='largest OD and width, smallest bore: tightest at the hood top/back, the cheek and the lip'),
    dict(id='bobbin-38x6-bore10.5', od=OD_MIN, w=W_MIN, bore=BORE_MAX, dome=None, lift=1.0,
         why='smallest, thinnest, biggest bore: hangs lowest and loosest'),
    dict(id='chemtronics-44.5-domed', od=44.5, w=10.0, bore=8.0, dome=(7.5, 3.0), lift=1.3,
         why='Chemtronics Soder-Wick SD: domed face loaded dome-in, flat hub ring on the 10 mm seat'),
]


def place_roll(out, rd):
    R, rb = rd['od']/2, rd['bore']/2
    d = rb-PIN_R                                       # hangs on the axle's top line
    m = roll_mesh(R, rd['w'], rb, rd['dome'])
    o = P0+AX*U_SEAT-E2*d
    mat = A.Matrix(E1.x, E2.x, AX.x, o.x, E1.y, E2.y, AX.y, o.y, E1.z, E2.z, AX.z, o.z, 0, 0, 0, 1)
    m.transform(mat)
    path = out/f"{NAME}__tool-{rd['id']}.stl"
    m.write(str(path))
    centre = o+AX*(rd['w']/2)
    slide = PIN_TIP-U_SEAT+1.0                         # inner face past the axle tip
    removal = [[round(v, 3) for v in E2*rd['lift']], [round(v, 3) for v in AX*slide], [0, 70, 0]]
    return path, centre, removal, m


def place_tail(out, centre, R):
    """Render stand-in for the free end: a 2.5 x 0.5 mm braid leaving the roll's front rim and
    hanging 30 mm straight down past the open bottom."""
    top = centre+E1*(R+0.05)
    a, b = top-AX*1.25, top+AX*1.25
    pts = [a, b, b-V(0, 0, 30), a-V(0, 0, 30)]
    strip = Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0, 0.5, 0))
    path = out/f'{NAME}__tool-tail.stl'
    Mesh.Mesh(strip.tessellate(0.01)).write(str(path))
    return path


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    host, info = K.receiver(CELLS, HOOP_ROW, POSE)
    ck, outline = cheek()
    parts = [ck, lower_flange(outline), hood(), axle()]+webs(outline)
    shape = host.multiFuse(parts).removeSplitter()
    shape = shape.cut(plate_windows()).removeSplitter()
    assert shape.isValid() and len(shape.Solids) == 1, (shape.isValid(), len(shape.Solids))
    info.update(K.export(shape, out, NAME, POSE))
    tools, rolls = [], []
    for rd in ROLLS:
        path, centre, removal, m = place_roll(out, rd)
        # One colour for all three: they share the seat plane, so distinct colours z-fight in the
        # renders; the smaller two sit inside the 52 mm one and are checked separately.
        tools.append(dict(id=rd['id'], stl=path.name, colour='#ccd2d5', seat=dict(gravity=True), removal=removal))
        bb = m.BoundBox
        rolls.append(dict(rd, centre=[centre.x, centre.y, centre.z], removal=removal,
                          bounds=[bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax]))
    big = rolls[0]
    tail = place_tail(out, V(*big['centre']), big['od']/2)
    tools.append(dict(id='tail (render stand-in, the free end)', stl=tail.name, colour='#c87533',
                      seat=dict(min_contacts=0)))
    spec = dict(name=NAME, title=TITLE, pose=POSE, pose_matrix=info['pose_matrix'],
                installed=f'{NAME}__installed.stl', print=info['print_file'], glued=[], glued_print=[],
                tools=tools, overhang_exceptions=[],
                render_notes=dict(
                    loaded='52 x 12 mm bobbin (envelope max) on a 15 deg canted 5.6 mm axle; hood over the top and back, open below.',
                    empty='10 mm hub seat, 5.6 mm axle with the 0.8 mm V-nose lip on its top line, top-and-back hood.',
                    front='Tail hangs from the front rim past the open bottom; snip below the roll.',
                    side='Right cheek = bed face; flange along its lower edge.',
                    print='Right cheek on the bed; supports under the pegs only.'))
    (out/f'{NAME}__checks-spec.json').write_text(json.dumps(spec, indent=1))
    keep = ax(U_KEEP+0.5)                              # farthest tool-bearing point: the lip, where a pushed roll bears
    fea = dict(step=f'{NAME}__installed.step', h=2.0, supports=['pegs'],
               loads=[dict(id='wag', what='5 N sideways (+X, toward the user\'s left) on the axle at the lip',
                           point=[keep.x, keep.y, keep.z], radius=3.5, force=[5, 0, 0]),
                      dict(id='press', what='5 N down on the axle at the lip', point=[keep.x, keep.y, keep.z],
                           radius=3.5, force=[0, 0, -5]),
                      dict(id='pull', what='5 N toward the user on the axle at the lip (a braid yank)',
                           point=[keep.x, keep.y, keep.z], radius=3.5, force=[0, 5, 0])])
    (out/f'{NAME}__fea-spec.json').write_text(json.dumps(fea, indent=1))
    info.update(module='braid', cells=CELLS, hoop_row=HOOP_ROW, cant_deg=CANT,
                axle=dict(origin=[P0.x, P0.y, P0.z], direction=[AX.x, AX.y, AX.z], seat_u=U_SEAT,
                          hub_r=HUB_R, flare_r=FLARE_R, pin_r=PIN_R, tip_u=PIN_TIP),
                lip=dict(h=LIP_H, w=LIP_W, keeper_u=U_KEEP, flat_to_u=U_KEEP+LIP_FLAT, ramp_end_u=U_RAMP_END,
                         loading_ramp_deg=LOAD_RAMP, print_v_face_deg=V_ARM, print_nose_rise_deg=NOSE_RISE),
                hood=dict(r_in=R_IN, wall=WALL, rim_u=U_RIM, theta_deg=list(HOOD_TH), open='front and bottom'),
                flange=dict(h=FLANGE_H, t=FLANGE_T),
                envelope=dict(od=[OD_MIN, OD_MAX], width=[W_MIN, W_MAX], bore=[BORE_MIN, BORE_MAX]),
                rolls=rolls, cheek_outline=outline, b6_volume_cm3=39.0)
    K.save_design(out, NAME, info)
    print(json.dumps({k: info[k] for k in ('volume_mm3', 'solid_mass_asa_g', 'print_bounds', 'bounds_installed')}, indent=1))


if __name__ == '__main__':
    main(Path(sys.argv[1]))
