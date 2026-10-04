"""v12 barrels: flux syringe, paste syringe and solder sucker, nozzles down, printed upright.

Design (2026-10-02):
- Upright print (flat bottom on the bed): every holding surface is the top of a wall, every
  cradle is a wall face, so nothing but the pegs prints in the air.
- Each tool stands in a V channel whose two walls are tangent to its barrel and lean with
  the tool (planes containing the tool axis). A V is self-centring and forgiving: a fatter
  or thinner barrel just sits a little forward or back. The V's 60 degree mouth is the lead-in.
- The V walls of neighbouring tools meet at the front and close triangular cells against
  the plate: in plan the module is a zig-zag truss, so a sideways push at the front runs
  down the walls as tension and compression instead of bending a cheek.
- Syringes hang by the finger flange. The wall tops are 4 mm above the seat plane, and a
  pocket the size of the flange (plus slack) is cut down to the seat plane: the flange sits
  in a cup. Lift 6 mm along the axis, then out toward the user.
- Below the flange collar the walls are cut back to just behind the barrel, so fingers can
  wrap the barrel (grab zone). The collar's underside there is a 50 degree ramp.
- The sucker stands on its nose cone in a conical cup (two corbels growing off its V walls,
  50 degree undersides, a slot for the PTFE tip) and leans back 5 degrees into its V. Lift
  9 mm, then out. Its V walls stay full height so the tip hangs inside them.
- Axes tilt 10 degrees (syringes) and 5 degrees (sucker) top-toward-board: the tool leans
  into its V, the seat slopes down toward the board, and the nozzles point out over the
  drip tray below (station z -127). The sucker leans less so a long sucker with its plunger
  out still clears the board.
- The end cells are boxes (side wall flush with the module edge, short chamfered front
  wall), pointed windows lighten the plate and both side walls, and a 22 mm foot along the
  plate's bottom edge carries the print's centre of mass.
- Order from the user's left (+X) to right: flux at x 37, paste at 0, sucker at -37 (B6's).

Coordinates as every v12 module (common.py). Run: FreeCAD python barrels.py OUT_DIR
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
X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)
NAME = 'part-solder-barrels__v12__upright__fit-pf02c9-hoop5'
POSE = 'upright'
CELLS, HOOP_ROW = 5, 4
STATION = (38.1, 0.0, 0.0)
REF = Path(__file__).resolve().parents[2]/'reference/solder-tools'
B6_VOLUME_CM3 = 257.0

# ---------------------------------------------------------------- parameters
BETA = 30.0                  # V half-angle (each wall from the forward direction)
T = 2.4                      # wall thickness
CLEAR = 0.15                 # V faces sit this far outside the barrel radius
W_TOP = 4.0                  # wall tops, in the 10 deg frame: the lip height above the seat (w = 0)
V_SYR = 28.0                 # syringe axes, 10 deg frame v (27.6 mm out from the board at the seat)
POCKET_G, POCKET_SWEEP = 2.0, 2.0   # flange pocket: radial slack, and +-v slack for barrel size
LIFT_SYR, LIFT_SUCK, OUT = 6.0, 9.0, 60.0
GRAB_KEEP = 1.5              # below the collar the walls end this far in front of the tangent line
COLLAR_FRONT = 8.0           # collar height at the front of the flux/paste cell
SLOPE = 50.0                 # every underside (collar, wall bottoms, corbels) from horizontal
FOOT = dict(y1=22.0, t=2.0)  # first-layer foot along the plate's front bottom edge (puts the print's
                             # centre of mass, installed y 13.8, well inside the first layer)
ROOT_Y = 14.0                # the walls' 50 deg root plane starts here on the bed
CORNER_CHAMFER = 3.0         # vertical chamfer on the end boxes' front-outer corners (along each face)
CUP = dict(top=6.0, front=11.0, drop=12.0, cone_clear=0.15, tip_clear=1.0)
SUCKER_C = V(-37.0, 42.0, -52.0)   # sucker axis point where the nose cone is 12 mm across
MID_X = 18.5                 # flux/paste split of the grab cut
WINDOW = dict(margin=3.0, top=-22.0, bottom=-98.0, min_width=8.0, roof_deg=55.0)   # plate slots between brace roots
SIDE_WINDOWS = dict(sucker=dict(y=(12.0, 38.0), peak=-18.0), flux=dict(y=(11.0, 24.0), peak=-28.0),
                    above_root=8.0, bottom=-98.0)   # pointed windows in the end cells' side walls

# Tool proxies (B6 placement files) and their profiles, t along the B6 axis from the vertex mean.
A_B6 = V(0.0, -0.17364817766693033, 0.984807753012208)
TOOLS = [
    dict(id='flux', label='flux syringe', parts=['0-0', '0-1', '0-2', '0-3'], x=37.0, tilt=10.0,
         R=9.53, flange_r=16.0, t_ref=52.509, colour='#d9b26a',
         profile=[(-49.491, 0.55), (-41.491, 0.55), (-41.491, 1.0), (-24.491, 3.3), (-24.491, 9.53),
                  (52.509, 9.53), (52.509, 16.0), (54.509, 16.0), (54.509, 3.536), (116.509, 3.536),
                  (116.509, 9.5), (118.509, 9.5)]),
    dict(id='paste', label='paste syringe', parts=['1-0', '1-1', '1-2'], x=0.0, tilt=10.0,
         R=7.53, flange_r=13.0, t_ref=38.807, colour='#8fb3d9',
         profile=[(-39.193, 1.0), (-22.193, 3.3), (-22.193, 7.53), (38.807, 7.53), (38.807, 13.0),
                  (40.807, 13.0), (40.807, 3.536), (83.807, 3.536), (83.807, 7.5), (85.807, 7.5)]),
    dict(id='sucker', label='solder sucker', parts=['2-0', '2-1'], x=-37.0, tilt=5.0,
         R=10.0, t_ref=-44.521, colour='#ccd2d5',
         profile=[(-61.521, 2.0), (-53.521, 2.0), (-35.521, 10.0), (48.479, 10.0), (48.479, 3.0),
                  (61.479, 3.0), (61.479, 9.0), (65.479, 9.0)]),
]
TOOL = {t['id']: t for t in TOOLS}

CEN = V(0, 30, -50)          # half-space boxes are centred near the module


def half(point, normal, S=700.0):
    """Solid {p : (p - point).normal <= 0} as a big box."""
    n = V(normal); n.normalize()
    p0 = CEN - n*((CEN-point).dot(n))
    b = Part.makeBox(S, S, S, V(-S/2, -S/2, -S))
    r = A.Rotation(V(0, 0, 1), n)
    if r.Angle > 1e-12:
        b.rotate(V(0, 0, 0), r.Axis, math.degrees(r.Angle))
    b.translate(p0)
    return b


def common(*shapes):
    s = shapes[0]
    for h in shapes[1:]:
        s = s.common(h)
    return s


def frame(tilt):
    """Unit axis a (top toward the board) and forward perpendicular v for a tilt about X."""
    s, c = math.sin(math.radians(tilt)), math.cos(math.radians(tilt))
    return V(0, -s, c), V(0, c, s)


A10, V10 = frame(10.0)


def slope_normal():
    """Upward normal of a plane rising toward +Y at SLOPE."""
    a = math.radians(SLOPE)
    return V(0, -math.sin(a), math.cos(a))


# ---------------------------------------------------------------- tool placement
def setup():
    for t in TOOLS:
        t['a'], t['v'] = frame(t['tilt'])
        t['Rp'] = t['R']+CLEAR
        if t['id'] == 'sucker':
            t['S'] = V(SUCKER_C)
        else:
            t['S'] = V(t['x'], 0, 0)+V10*V_SYR          # flange underside centre on the seat plane w = 0
        b = math.radians(BETA)
        t['nr'] = X*math.cos(b)-t['v']*math.sin(b)      # outward normals of the +X and -X V faces
        t['nl'] = X*(-math.cos(b))-t['v']*math.sin(b)


def to_inst(t, u, v, w):
    return t['S']+X*u+t['v']*v+t['a']*w


def env_r(prof, tt):
    """Envelope radius of a tabulated (t, r) profile at tt (steps take the larger radius)."""
    best = -1.0
    for (t0, r0), (t1, r1) in zip(prof, prof[1:]):
        if min(t0, t1)-1e-3 <= tt <= max(t0, t1)+1e-3:
            best = max(best, r0, r1) if abs(t1-t0) < 1e-9 else max(best, r0+(r1-r0)*(tt-t0)/(t1-t0))
    return best


def proxy_mesh(t):
    """The B6 proxy parts merged, moved from the B6 placement to this one. Returns (mesh, max
    distance of any proxy vertex outside the tabulated profile, B6 axis origin)."""
    parts = [Mesh.Mesh(str(REF/f'barrels__tool-{p}.stl')) for p in t['parts']]
    o, n = V(0, 0, 0), 0
    for m in parts:                                   # the vertex mean of the parts (as probed)
        for q in m.Points:
            o += q.Vector; n += 1
    o = o*(1.0/n)
    worst = 0.0
    for m in parts:
        for q in m.Points:
            d = q.Vector-o
            tt = d.dot(A_B6)
            worst = max(worst, (d-A_B6*tt).Length-env_r(t['profile'], tt))
    merged = Mesh.Mesh()
    for m in parts:
        merged.addMesh(m)
    # rotate the B6 axis onto this tool's axis about X, and put t_ref at S
    ang = math.degrees(math.atan2(A_B6.cross(t['a']).x, A_B6.dot(t['a'])))
    ref = o+A_B6*t['t_ref']
    pl = A.Placement(t['S'], A.Rotation(X, ang)).multiply(A.Placement(ref*-1.0, A.Rotation()))
    merged.transformGeometry(pl.toMatrix())
    return merged, worst, o


# ---------------------------------------------------------------- envelopes (cut along the removal path)
def frustum(t, t0, t1, r0, r1, shift=0.0):
    base = to_inst(t, 0, 0, t0-t['t_ref']+shift)
    if abs(r0-r1) < 1e-6:
        return Part.makeCylinder(r0, t1-t0, base, t['a'])
    return Part.makeCone(r0, r1, t1-t0, base, t['a'])


def trapezoid_sweep(t, t0, t1, r0, r1, shift, dist):
    """The axial section |u| <= r(t) of a frustum, swept forward along v by dist."""
    pts = [to_inst(t, -r0, 0, t0-t['t_ref']+shift), to_inst(t, r0, 0, t0-t['t_ref']+shift),
           to_inst(t, r1, 0, t1-t['t_ref']+shift), to_inst(t, -r1, 0, t1-t['t_ref']+shift)]
    return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(t['v']*dist)


def sweep_cut(t, segments, lift):
    """Seated + lifted + carried forward, for (t0, t1, r0, r1) segments with r growing upward."""
    out = []
    for t0, t1, r0, r1 in segments:
        out.append(frustum(t, t0, t1, r0, r1))
        out.append(frustum(t, t1, t1+lift, r1, r1))             # the lift (r grows with t)
        out.append(frustum(t, t0, t1, r0, r1, shift=lift))
        lifted_fwd = frustum(t, t0, t1, r0, r1, shift=lift); lifted_fwd.translate(t['v']*OUT)
        out.append(lifted_fwd)
        out.append(trapezoid_sweep(t, t0, t1, r0, r1, lift, OUT))
    return out


# ---------------------------------------------------------------- body
def cell(left_tool, right_tool):
    """A triangular cell between the +X V face of left_tool and the -X V face of right_tool,
    closed by the plate. Behind each V's apex the two faces run on to the plate (an X brace)."""
    def face(tool, side, off):
        n = tool['nr'] if side == 'r' else tool['nl']
        return half(tool['S']+n*(tool['Rp']+off), -n)            # keeps n.(p-S) >= Rp+off
    solid = common(face(left_tool, 'r', 0.0), face(right_tool, 'l', 0.0), half(V(0, K.PLATE_Y1-0.5, 0), -Y))
    hole = common(face(left_tool, 'r', T), face(right_tool, 'l', T), half(V(0, K.PLATE_Y1, 0), -Y))
    return solid.cut(hole)


def apex_top(left_tool, right_tool):
    """Where the two inner V faces meet the wall-top plane (installed point)."""
    import numpy as np
    rows, rhs = [], []
    for tool, n in [(left_tool, left_tool['nr']), (right_tool, right_tool['nl'])]:
        rows.append([n.x, n.y, n.z]); rhs.append(tool['Rp']+n.dot(tool['S']))
    rows.append([A10.x, A10.y, A10.z]); rhs.append(W_TOP)
    p = np.linalg.solve(np.array(rows), np.array(rhs))
    return V(*p)


def end_cell(tool, side, front_point, front_normal):
    """The cell between tool's outer V face and the module's side: a side wall flush with the
    module edge and a short front wall through the neighbouring divider's nose, so the end
    of the zig-zag closes as a box instead of a 20 degree knife edge."""
    hw = K.half_width(CELLS)
    n = tool['nr'] if side == 'r' else tool['nl']
    sg = 1.0 if side == 'r' else -1.0
    fn = V(front_normal); fn.normalize()
    corner = V(sg*hw, front_point.y, front_point.z)                 # on the front plane and the side plane
    nc = X*sg+fn; nc.normalize()
    cut = CORNER_CHAMFER*math.sqrt(0.5)
    solid = common(half(tool['S']+n*tool['Rp'], -n), half(V(sg*hw, 0, 0), X*sg), half(front_point, fn),
                   half(V(0, K.PLATE_Y1-0.5, 0), -Y), half(corner-nc*cut, nc))
    hole = common(half(tool['S']+n*(tool['Rp']+T), -n), half(V(sg*(hw-T), 0, 0), X*sg),
                  half(front_point-fn*T, fn), half(V(0, K.PLATE_Y1, 0), -Y), half(corner-nc*(cut+T), nc))
    return solid.cut(hole)


def arm_x(t, n, off, z, y=K.PLATE_Y1):
    """x where the plane n.(p - S) = off meets the plate face y at height z."""
    S = t['S']
    return S.x+(off-n.y*(y-S.y)-n.z*(z-S.z))/n.x


def plate_windows():
    """Tapered slots through the plate between the brace roots of neighbouring V's, below
    the collar band: sides follow the roots (inset by a margin), pointed 55 deg roof, so
    printed upright nothing hangs over the hole."""
    pa, fl, su = TOOL['paste'], TOOL['flux'], TOOL['sucker']
    k = math.tan(math.radians(WINDOW['roof_deg']))
    out, polys = [], []
    for (lt, ln), (ht, hn) in [((pa, pa['nl']), (fl, fl['nr'])), ((su, su['nl']), (pa, pa['nr']))]:
        def xlo(z):
            return max(arm_x(lt, ln, lt['Rp'], z), arm_x(lt, ln, lt['Rp']+T, z))+WINDOW['margin']

        def xhi(z):
            return min(arm_x(ht, hn, ht['Rp'], z), arm_x(ht, hn, ht['Rp']+T, z))-WINDOW['margin']
        w1 = ((xhi(0)-xlo(0))-(xhi(-100)-xlo(-100)))/100.0
        w0 = xhi(0)-xlo(0)
        top = WINDOW['top']
        zs = (top-w0*k/2)/(1+w1*k/2)
        zb = max(WINDOW['bottom'], (WINDOW['min_width']-w0)/w1)
        pts = [(xlo(zb), zb), (xhi(zb), zb), (xhi(zs), zs), ((xlo(zs)+xhi(zs))/2, top), (xlo(zs), zs)]
        polys.append([(round(x, 2), round(z, 2)) for x, z in pts])
        out.append(K.poly_prism(pts, 'y', K.PLATE_Y0-0.01, K.PLATE_Y1+0.01))
    return out, polys


def side_windows(root_p):
    """Pointed windows (55 deg roof) through the end cells' side walls; the sill follows the
    50 deg root plane 8 mm up, so the frame keeps an even width."""
    hw = K.half_width(CELLS)
    k = math.tan(math.radians(WINDOW['roof_deg']))
    tr = math.tan(math.radians(SLOPE))
    out, polys = [], {}
    for key, sg in (('sucker', -1.0), ('flux', 1.0)):
        y0, y1 = SIDE_WINDOWS[key]['y']
        peak = SIDE_WINDOWS[key]['peak']

        def sill(y):
            return max(SIDE_WINDOWS['bottom'], root_p.z+(y-root_p.y)*tr+SIDE_WINDOWS['above_root'])
        yk = root_p.y+(SIDE_WINDOWS['bottom']-SIDE_WINDOWS['above_root']-root_p.z)/tr   # where the sill leaves the floor
        zs = peak-(y1-y0)/2*k
        pts = [(y0, sill(y0))]+([(yk, sill(yk))] if y0 < yk < y1 else [])+[(y1, sill(y1)), (y1, zs), ((y0+y1)/2, peak), (y0, zs)]
        assert sill(y1) < zs-5, (key, sill(y1), zs)
        polys[key] = [(round(a, 2), round(b, 2)) for a, b in pts]
        x0, x1 = (hw-T-1.0, hw+1.0) if sg > 0 else (-hw-1.0, -hw+T+1.0)
        out.append(K.poly_prism(pts, 'x', x0, x1))
    return out, polys


def build(out):
    setup()
    host, info = K.receiver(CELLS, HOOP_ROW, POSE)
    hw = K.half_width(CELLS)
    z0 = info['plate']['z0']
    fl, pa, su = TOOL['flux'], TOOL['paste'], TOOL['sucker']
    # Cells: sucker-outer, sucker|paste, paste|flux, flux-outer.
    ap_pf = apex_top(pa, fl)
    ap_sp = apex_top(su, pa)
    cells = [end_cell(su, 'l', ap_sp, su['v']), cell(su, pa), cell(pa, fl), end_cell(fl, 'r', ap_pf, V10)]
    body = cells[0].multiFuse(cells[1:]).removeSplitter()
    # Height: the wall-top plane, and a 50 deg root plane rising from ROOT_Y on the bed.
    root_p = V(0, ROOT_Y, z0)
    keep = common(half(A10*W_TOP, A10), half(root_p, slope_normal()*-1.0), half(V(0, 0, z0), -Z),
                  half(V(hw, 0, 0), X), half(V(-hw, 0, 0), -X))
    body = body.common(keep)
    # Grab zone: below the collar plane, cut the syringe channels' walls back to just
    # behind each barrel's tangent line.
    collar_p = V(0, ap_pf.y, ap_pf.z-COLLAR_FRONT)
    below_collar = half(collar_p, slope_normal())
    b = math.radians(BETA)
    grab = []
    for t, x_lo, x_hi in [(pa, None, MID_X), (fl, MID_X, None)]:
        vc = -t['Rp']*math.sin(b)+GRAB_KEEP
        hs = [half(t['S']+t['v']*vc, -t['v']), below_collar]
        if x_lo is not None:
            hs.append(half(V(x_lo, 0, 0), -X))
        if x_hi is not None:
            hs.append(half(V(x_hi, 0, 0), X))
        if t is pa:                                              # spare the sucker's +X wall
            hs.append(half(su['S']+su['nr']*(su['Rp']+T), -su['nr']))
        grab.append(common(*hs))
    body = body.cut(grab)
    # Sucker cup: two corbels growing off its V faces (50 deg undersides), a cone bore and a tip slot.
    zb = su['S'].z-CUP['drop']
    corbels = []
    for n in (su['nr'], su['nl']):
        h = V(-n.x, -n.y, 0); h.normalize()                         # inward, horizontal
        dvec = Z.cross(h)
        P = V(su['S'].x, su['S'].y, zb)
        mu = (su['Rp']-n.dot(P-su['S']))/n.dot(h*-1.0)
        q = P+h*(-mu)
        up = h*math.cos(math.radians(SLOPE))+Z*math.sin(math.radians(SLOPE))
        N = dvec.cross(up)
        if N.z < 0:
            N = N*-1.0
        corbels.append(half(q, N*-1.0))                              # keeps N.(p-q) >= 0
    channel = [half(su['S']+su['nr']*(su['Rp']+0.5), su['nr']), half(su['S']+su['nl']*(su['Rp']+0.5), su['nl']),
               half(su['S']+su['v']*CUP['front'], su['v']), half(su['S']+su['a']*CUP['top'], su['a']),
               half(V(0, K.PLATE_Y1-0.5, 0), -Y)]
    cup = common(*channel, corbels[0]).fuse(common(*channel, corbels[1])).removeSplitter()
    cup = cup.common(keep)          # never below the walls' root plane: no island starts in the air
    # Foot (first layer) along the plate's bottom edge.
    foot = K.box(-hw, K.PLATE_Y1-0.5, z0, 2*hw, FOOT['y1']-K.PLATE_Y1+0.5, FOOT['t'])
    windows, wpolys = plate_windows()
    shape = host.cut(windows).multiFuse([body, cup, foot]).removeSplitter()
    # Tool cuts: flange pockets (cups) and every tool's envelope along its removal path.
    cuts = []
    for t in (fl, pa):
        r = t['flange_r']+POCKET_G
        for dv in (-POCKET_SWEEP, POCKET_SWEEP):
            cuts.append(Part.makeCylinder(r, 40.0, to_inst(t, 0, dv, 0), t['a']))
        pts = [to_inst(t, -r, -POCKET_SWEEP, 0), to_inst(t, r, -POCKET_SWEEP, 0),
               to_inst(t, r, POCKET_SWEEP, 0), to_inst(t, -r, POCKET_SWEEP, 0)]
        cuts.append(Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(t['a']*40.0))
        prof = t['profile']
        tb = prof[[i for i, (tt, rr) in enumerate(prof) if abs(rr-t['R']) < 1e-6][0]][0]
        segs = [(prof[0][0]-1.0, tb, 3.6, 3.6), (tb, t['t_ref'], t['Rp']-0.05, t['Rp']-0.05)]
        cuts += sweep_cut(t, segs, LIFT_SYR)
    # One continuous profile (never narrowing upward, so no ceiling): the tip slot's radius
    # until the cone, grown by the clearance, is wider; then the cone; then the body.
    c, rt = CUP['cone_clear'], 2.0+CUP['tip_clear']
    t3 = -53.521+(rt-2.0-c)*18.0/8.0
    segs = [(-61.521-2.0, t3, rt, rt), (t3, -35.521, rt, su['Rp']-0.05), (-35.521, 48.479, su['Rp']-0.05, su['Rp']-0.05)]
    cuts += sweep_cut(su, segs, LIFT_SUCK)
    sw, swp = side_windows(root_p)
    info['side_windows_yz'] = swp
    shape = shape.cut(cuts+sw).removeSplitter()
    assert shape.isValid() and len(shape.Solids) == 1, (shape.isValid(), len(shape.Solids))
    info['plate_windows_xz'] = wpolys
    return shape, info, dict(apex_paste_flux=ap_pf, apex_sucker_paste=ap_sp, collar_point=collar_p, root_point=root_p)


def vec(p):
    return [round(p.x, 3), round(p.y, 3), round(p.z, 3)]


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    shape, info, geo = build(out)
    info.update(K.export(shape, out, NAME, POSE))
    tools, tips = [], {}
    for t in TOOLS:
        m, dev, o = proxy_mesh(t)
        assert dev < 0.05, (t['id'], 'proxy outside its tabulated profile by', dev)
        f = f'{NAME}__tool-{t["id"]}.stl'
        m.write(str(out/f))
        lift = t['a']*(LIFT_SUCK if t['id'] == 'sucker' else LIFT_SYR)
        fwd = t['v']*OUT
        tip = to_inst(t, 0, 0, t['profile'][0][0]-t['t_ref'])
        top = to_inst(t, 0, 0, t['profile'][-1][0]-t['t_ref'])
        tips[t['id']] = dict(module=vec(tip), station=vec(tip+V(*STATION)), top_module=vec(top))
        tools.append(dict(id=t['id'], stl=f, colour=t['colour'], seat=dict(gravity=True), samples=6000,
                          removal=[vec(lift), vec(fwd)]))
    # FEA load points: on the wall top at each syringe's front lip, and on the sucker cup's front shoulder.
    b = math.radians(BETA)
    loads = []
    for t, side in [(TOOL['flux'], 'l'), (TOOL['paste'], 'r')]:
        r_lip = t['flange_r']+POCKET_G+POCKET_SWEEP+1.5
        s = math.sqrt(r_lip**2-t['Rp']**2)
        sg = -1.0 if side == 'l' else 1.0
        u = sg*(t['Rp']*math.cos(b)+s*math.sin(b)+T/2*math.cos(b))
        v = -t['Rp']*math.sin(b)+s*math.cos(b)-T/2*math.sin(b)
        p = to_inst(t, u, v, 0)
        p = p+A10*(W_TOP-p.dot(A10))
        loads.append((t['id']+'-lip', p))
    su = TOOL['sucker']
    p = to_inst(su, -(su['Rp']/math.cos(b)+CUP['front']*math.tan(b)-1.2), CUP['front']-1.0, CUP['top'])
    loads.append(('sucker-cup', p))
    fea_loads = []
    for lid, p in loads:
        fea_loads.append(dict(id='wag-'+lid, what=f'5 N sideways at the {lid}', point=vec(p), radius=3.0, force=[5, 0, 0]))
        fea_loads.append(dict(id='press-'+lid, what=f'5 N down at the {lid}', point=vec(p), radius=3.0, force=[0, 0, -5]))
    spec = dict(name=NAME, title='Barrels v12 (flux, paste, sucker)', pose=POSE, pose_matrix=info['pose_matrix'],
                installed=f'{NAME}__installed.stl', print=info['print_file'], glued=[], tools=tools,
                overhang_exceptions=[],
                render_notes=dict(loaded='Syringes hang by the flange in 4 mm cups; the sucker stands on its nose cone. Lift, then out.',
                                  empty='Zig-zag V walls: collar on top, cut back below it so fingers wrap the barrel.',
                                  front='Nozzles point down over the drip tray (station z -127).',
                                  side='Syringes lean 10 deg, the sucker 5 deg, tops toward the board.',
                                  print='Flat bottom on the bed; organic supports under the pegs only.'))
    (out/f'{NAME}__checks-spec.json').write_text(json.dumps(spec, indent=1))
    fea = dict(step=f'{NAME}__installed.step', h=2.0, supports=['pegs'], loads=fea_loads)
    (out/f'{NAME}__fea-spec.json').write_text(json.dumps(fea, indent=1))
    info.update(module='barrels', cells=CELLS, hoop_row=HOOP_ROW, station_origin=list(STATION),
                b6_volume_cm3=B6_VOLUME_CM3, volume_vs_b6=info['volume_mm3']/1000/B6_VOLUME_CM3,
                params=dict(beta_deg=BETA, wall_mm=T, clear_mm=CLEAR, w_top_mm=W_TOP, v_syr_mm=V_SYR,
                            pocket_slack_mm=POCKET_G, pocket_sweep_mm=POCKET_SWEEP, lift_syringe_mm=LIFT_SYR,
                            lift_sucker_mm=LIFT_SUCK, grab_keep_mm=GRAB_KEEP, collar_front_mm=COLLAR_FRONT,
                            slope_deg=SLOPE, foot=FOOT, root_y_mm=ROOT_Y, corner_chamfer_mm=CORNER_CHAMFER,
                            cup=CUP, sucker_cone_point=vec(SUCKER_C), window=WINDOW, side_windows=SIDE_WINDOWS),
                tools={t['id']: dict(tilt_deg=t['tilt'], axis=vec(t['a']), seat_point=vec(t['S']),
                                     barrel_r_mm=t['R'], v_face_r_mm=t['Rp']) for t in TOOLS},
                tips=tips, geometry={k: vec(v) for k, v in geo.items()})
    K.save_design(out, NAME, info)
    print(json.dumps({k: info[k] for k in ('volume_mm3', 'solid_mass_asa_g', 'print_bounds', 'tips', 'geometry')}, indent=1))


if __name__ == '__main__':
    main(Path(sys.argv[1]))
