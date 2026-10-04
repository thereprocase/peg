"""v12 barrels (flux syringe, paste syringe, solder sucker; nozzles down), keeping the B6 seats.

Owner (2026-10-02): "I like the action on the old version of the three syringes very much
so those seats are great." So every surface a tool touches or passes is B6's, rebuilt as
clean solids on each tool's 10-degree axis, at B6's tool positions; everything around the
seats is new.

The B6 seat, per tool (measured from docs/gallery/solder-modules/barrels/holder.stl, see
NOTES.md for the table), in the tool frame (e1 = X, e2 out of the board across the axis,
u along the axis, top toward the board):
- upper ring: bore rb = barrel radius + 0.65, a U open to the front (straight walls on
  the bore's tangents), 3 mm walls, the tips chamfered outside, 14 mm tall along the axis,
  a 1.2 mm cone lead-in at the top of the bore;
- lower cup: the barrel stands on a ledge square to the axis inside the same bore; two
  posts in front of it rise 10 mm (14 for the sucker) with a 2 mm, 1.36 mm-deep cone
  lead-in; a front slot (8.4 mm, the sucker 12.4) lets the nozzle hub through; the side
  walls rise to a level top.
- action: lift 18 mm along the axis (the barrel clears the posts), then 80 mm out (+Y).

What is new (owner rules for v12):
- Upright print, flat bottom on the bed. Each station is one U-channel on its tool axis
  from the bed to the ring top: the ring is its top, the cup its bottom, and its back half
  (the bore continued) carries the ring down to the cup. Below each ring the side walls
  are corbels whose undersides rise at 50 degrees to the ring tips, so no ring or ledge
  hangs in the air; between corbel and cup the barrel shows as on B6.
- Back cheeks tie each channel to the plate: a 50-degree rail from the ring's back corner
  down to the plate, a strip on the bed, a band behind the channel, and a diagonal from
  the plate's foot to the ring's back corner that triangulates the frame (two windows).
- A 2.4 mm floor on the bed, full width from the plate to the cups, is a diaphragm that
  ties every cheek foot and cup to the plate (triangulated windows behind each channel).
- The receiver: common.receiver(5, 4, 'upright'): hooks on row 0, a bearing on row 2, the
  PF07 #5 hoop on row 4 (flexing in X, the print layers), the plate run down to the bed.
  Pointed windows lighten the plate between the cheek lines.
Rev 2 (2026-10-02, after Frodo's bench-user review and the shared install-arc hoop fix):
- common.receiver's default hoop fix (root clipped to r 2.95; nothing changes for upright).
- 1 mm chamfers on each channel's sharp outer front edges below the ring (the half-tube's
  front edges between corbel and cup, and the cup's outer front corners). No seat surface.
- The floor's two free front corners rounded in plan (r 8) as ASA corner relief.
Run: FreeCAD python barrels_b6seats.py OUT_DIR
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
NAME = 'part-solder-barrels__v12__upright__fit-pf02c9-hoop5'
POSE = 'upright'
CELLS, HOOP_ROW = 5, 4
REF = Path(__file__).resolve().parents[2]/'reference/solder-tools'
B6_VOLUME_CM3 = 257.3

TILT = 10.0                                   # tool axes lean top toward the board
S, C = math.sin(math.radians(TILT)), math.cos(math.radians(TILT))
BED = -120.0                                  # B6's underside, 1.9 mm above the drip tray
WALL = 3.0                                    # B6 ring and cup wall
LIFT, OUT = 18.0, 80.0                        # the B6 action
RING_H = 14.0
TOP_CONE_H = 1.2                              # ring bore lead-in, axial length
POST_CONE = (2.0, 1.36)                       # post lead-in: axial length, radial depth
CORBEL = 50.0                                 # corbel underside, degrees from horizontal
CORBEL_BACK = -2.0                            # e2 where the corbel window stops (just behind the axis)
RAIL, RAIL_DEG = 5.0, 50.0                    # back-cheek rail width and slope
JOINT = 3.0                                   # back-cheek band left behind the channel
STRIP = 4.0                                   # back-cheek strips on the bed and the plate
DIAG = 4.0                                    # back-cheek diagonal, plate-bed corner to the ring's back-top corner
# v12 FEA run 1: without the diagonal the cheek was a four-bar frame (plate, bed strip,
# channel, rail) and racked: 0.66 mm down at the paste cup, 0.79 mm sideways at its ring.
FLOOR_T, FLOOR_Y = 2.4, 44.0                  # bed diaphragm: plate to the cups' backs, full width
FLOOR_EDGE = 4.0                              # floor kept round each window and along the diagonal
# v12 rev 2 (Frodo NICE 2 and 3, 2026-10-02):
EDGE_CH = 1.0                                 # 45-deg chamfer on each channel's sharp outer front edges below the
#   ring: the half-tube's two front edges between corbel and cup, and the cup's two outer front
#   corners. Wall edges in the upright print (no overhang); none is a seat surface.
FLOOR_CORNER_R = 8.0                          # plan-view round on the floor's two free front corners (ASA corner lift)

# B6 seats, hand-transcribed from the holder sections (tool frame, mm). cy: axis offset
# along e2 from the origin (the axis passes (cx, cy*C, cy*S)); ring: (u bottom, u top);
# tip: (e2 where the outer wall ends, e2 of the tip on the bore tangent); ledge: u of the
# barrel's seat; post: u of the post tops; hub: (hole radius, slot half-width);
# y_front: the cup's front face (world Y); cup_top: the cup sides' level top (world Z).
B6 = {
    'flux': dict(tool=0, cx=37.0, cy=32.109, rb=10.15, ring=(-76.36, -62.36), tip=(10.39, 12.49),
                 top_chamfer=0.91, ledge=-117.36, post=-107.36, hub=(4.2, 4.2), y_front=65.15,
                 cup_top=-97.0, colour='#d9b26a'),
    'paste': dict(tool=1, cx=0.0, cy=33.151, rb=8.15, ring=(-78.45, -64.45), tip=(8.81, 10.91),
                  top_chamfer=0.86, ledge=-111.45, post=-101.45, hub=(4.2, 4.2), y_front=63.15,
                  cup_top=-91.0, colour='#8fb3d9'),
    'sucker': dict(tool=2, cx=-37.0, cy=34.019, rb=10.65, ring=(-65.53, -51.53), tip=(10.78, 12.88),
                   top_chamfer=0.85, ledge=-106.53, post=-92.53, hub=(6.0, 6.2), y_front=65.65,
                   cup_top=-82.0, colour='#c97b6b'),
}
UBOT = -150.0                                 # tool-frame columns start below the bed, then get clipped


# ---------------------------------------------------------------- tool frame
def frame(st):
    """Tool frame (e1, e2, u) -> installed: a +10 deg turn about X, then the axis offset."""
    return A.Placement(V(st['cx'], st['cy']*C, st['cy']*S), A.Rotation(V(1, 0, 0), TILT))


def placed(shape, st):
    s = shape.copy(); s.transformShape(frame(st).toMatrix()); return s


def world(st, e2, u):
    """(Y, Z) of a tool-frame point (any e1)."""
    return ((st['cy']+e2)*C-u*S, (st['cy']+e2)*S+u*C)


def u_at(st, e2, z):
    """u where the tool line at e2 reaches height z."""
    return (z-(st['cy']+e2)*S)/C


AXIS = (-S, C)                                # +u in the YZ plane


def meet(p, d, q, e):
    """Intersection of the 2D lines p + t d and q + s e."""
    det = -d[0]*e[1]+d[1]*e[0]
    t = (-(q[0]-p[0])*e[1]+(q[1]-p[1])*e[0])/det
    return (p[0]+t*d[0], p[1]+t*d[1])


def d_prism(r, u0, u1, front=45.0, slot=None):
    """A bore of radius r with B6's front opening: the arc round the back, straight sides
    on the bore's tangents (or a slot of half-width `slot`) out to e2 = front."""
    w = r if slot is None else slot
    edges = [Part.Arc(V(r, 0, u0), V(0, -r, u0), V(-r, 0, u0)).toShape()]
    pts = [V(-r, 0, u0)]+([V(-w, 0, u0)] if w != r else [])+[V(-w, front, u0), V(w, front, u0)]
    pts += ([V(w, 0, u0)] if w != r else [])+[V(r, 0, u0)]
    edges += [Part.LineSegment(a, b).toShape() for a, b in zip(pts, pts[1:])]
    return Part.Face(Part.Wire(edges)).extrude(V(0, 0, u1-u0))


def yz_prism(points, x0, x1):
    return K.poly_prism(points, 'x', x0, x1)


# ---------------------------------------------------------------- one station
def station(st):
    """The U-channel with the B6 ring on top and the B6 cup at the bottom (one solid)."""
    rb, W = st['rb'], st['rb']+WALL
    r0, r1 = st['ring']
    t_o, t_t = st['tip']
    ul, up = st['ledge'], st['post']
    r_s, w_s = st['hub']
    assert abs(r1-r0-RING_H) < 1e-6
    # Outer column: B6's ring outline (3 mm walls, the tips chamfered outside), bed to ring top.
    column = K.poly_prism([(-W, -W), (W, -W), (W, t_o), (rb, t_t), (-rb, t_t), (-W, t_o)], 'z', UBOT, r1)
    # Cup: posts and side walls share B6's post front (square to e2 = rb + 3, then B6's
    # front face lower down; B6's side walls stood 1-3 mm proud of it, touching nothing),
    # the posts up to their tops, the side walls up to the cup's level top.
    posts = K.box(-rb, 0, UBOT, 2*rb, W, up-UBOT)
    sides = [K.box(rb, 0, UBOT, WALL, W, r1-UBOT), K.box(-W, 0, UBOT, WALL, W, r1-UBOT)]
    cup = placed(posts.multiFuse(sides), st).common(
        K.box(st['cx']-W, -10, BED, 2*W, st['y_front']+10, st['cup_top']-BED))
    body = placed(column, st).fuse(cup)
    # The seat: every surface a tool touches or passes, cut as B6 has it.
    tc = st['top_chamfer']
    cutters = [
        Part.makeCylinder(rb, up-ul, V(0, 0, ul), V(0, 0, 1)),                    # bore from the ledge to the post tops
        d_prism(rb, up, r1+5),                                                     # bore + front opening above the posts
        Part.makeCone(rb, rb+POST_CONE[1], POST_CONE[0], V(0, 0, up-POST_CONE[0]), V(0, 0, 1)).common(
            K.box(-rb, 0, up-POST_CONE[0]-0.5, 2*rb, 45, POST_CONE[0]+0.5)),       # post lead-in (posts only)
        Part.makeCone(rb, rb+tc*(TOP_CONE_H+1)/TOP_CONE_H, TOP_CONE_H+1, V(0, 0, r1-TOP_CONE_H), V(0, 0, 1)),  # ring lead-in
        d_prism(r_s, UBOT, up, slot=w_s),                                          # nozzle hub hole + front slot
    ]
    for c in cutters:
        body = body.cut(placed(c, st))
    # Corbels: below the ring the side walls are cut back along a CORBEL-degree line from
    # the ring's front-bottom tip to just behind the axis, down to the cup's level top.
    T = world(st, t_t, r0)
    dc = (-math.cos(math.radians(CORBEL)), -math.sin(math.radians(CORBEL)))
    Ps = meet(T, dc, world(st, CORBEL_BACK, 0), AXIS)
    Pc = world(st, CORBEL_BACK, u_at(st, CORBEL_BACK, st['cup_top']))
    assert Ps[1] > st['cup_top']+3, ('corbel meets the cup', Ps)
    window = yz_prism([T, Ps, Pc, (T[0]+40, st['cup_top']), (T[0]+40, T[1])], st['cx']-W-1, st['cx']+W+1)
    body = body.cut(window)
    body = body.common(K.box(st['cx']-W-1, -50, BED, 2*W+2, 200, 200)).removeSplitter()
    edges = front_edges(body, st)
    assert len(edges) >= 4, ('front edges to chamfer', len(edges))
    body = body.makeChamfer(EDGE_CH, edges)
    assert body.isValid() and len(body.Solids) == 1, ('chamfer', body.isValid(), len(body.Solids))
    info = dict(ring_tip_bottom_yz=T, corbel_back_yz=Ps, corbel_window_sill_yz=Pc, front_edges_chamfered=len(edges))
    return body.removeSplitter(), info


def e2_of(st, p):
    """Tool-frame e2 of an installed point."""
    return p.y*C+p.z*S-st['cy']


def front_edges(body, st):
    """The channel's sharp outer front edges below the ring (Frodo NICE 2): straight edges on
    the outer wall planes X = cx +- W that are (a) the half-tube's front edge at e2 =
    CORBEL_BACK between corbel and cup top, or (b) the cup's outer front corner, on the post
    front plane (e2 = W) or B6's Y front face, from the bed to the cup's level top."""
    W = st['rb']+WALL
    out = []
    for e in body.Edges:
        if e.Curve.TypeId != 'Part::GeomLine' or e.Length < 1.0:
            continue
        p, q = e.Vertexes[0].Point, e.Vertexes[-1].Point
        if not any(abs(p.x-x) < 1e-3 and abs(q.x-x) < 1e-3 for x in (st['cx']-W, st['cx']+W)):
            continue
        tube = abs(e2_of(st, p)-CORBEL_BACK) < 1e-3 and abs(e2_of(st, q)-CORBEL_BACK) < 1e-3
        cup = (max(p.z, q.z) <= st['cup_top']+1e-3 and abs(q.z-p.z) > 0.5 and
               ((abs(p.y-st['y_front']) < 1e-3 and abs(q.y-st['y_front']) < 1e-3) or
                (abs(e2_of(st, p)-W) < 1e-3 and abs(e2_of(st, q)-W) < 1e-3)))
        if tube or cup:
            out.append(e)
    return out


def back_cheeks(st):
    """Two cheeks (X = cx +- rb .. rb+3) from the plate to the channel's back: a RAIL_DEG
    rail from the ring's back-top corner down to the plate, a strip on the bed, the plate
    strip and a band behind the channel, with one window (its roof is the rail, 50 deg)."""
    rb, W = st['rb'], st['rb']+WALL
    r1 = st['ring'][1]
    y_plate = K.PLATE_Y1-1.0                                          # start inside the plate
    e2j = -(rb+1.5)                                                   # joint line inside the channel's back wall
    Rbt = world(st, -W, r1)                                           # ring back-top corner
    tr = math.tan(math.radians(RAIL_DEG))
    z_rail_plate = Rbt[1]-(Rbt[0]-K.PLATE_Y1)*tr
    outline = [(y_plate, BED), world(st, e2j, u_at(st, e2j, BED)), world(st, e2j, r1), Rbt,
               (y_plate, Rbt[1]-(Rbt[0]-y_plate)*tr)]
    # Window: behind the band (e2 < -(W + JOINT)), above the bed strip, beside the plate
    # strip, under the rail (its underside is the window's 50-degree roof).
    e2w = -(W+JOINT)
    drop = RAIL/math.cos(math.radians(RAIL_DEG))
    rail_under = (Rbt[0], Rbt[1]-drop)
    dr = (-1.0, -tr)
    w1 = (K.PLATE_Y1+STRIP, BED+STRIP)
    w2 = world(st, e2w, u_at(st, e2w, BED+STRIP))
    w3 = meet(rail_under, dr, world(st, e2w, 0), AXIS)
    w4 = meet(rail_under, dr, (K.PLATE_Y1+STRIP, 0), (0, 1))
    hole = [w1, w2, w3, w4]
    # The diagonal triangulates the frame (plate, bed strip, channel, rail); it rises
    # forward at 65-72 deg, so both windows it leaves have roofs of 50 deg or steeper.
    p, q = (K.PLATE_Y1, BED), Rbt
    L = math.hypot(q[0]-p[0], q[1]-p[1]); d = ((q[0]-p[0])/L, (q[1]-p[1])/L); n = (-d[1]*DIAG/2, d[0]*DIAG/2)
    a, b = (p[0]-d[0]*5, p[1]-d[1]*5), (q[0]+d[0]*5, q[1]+d[1]*5)
    strut = [(a[0]+n[0], a[1]+n[1]), (b[0]+n[0], b[1]+n[1]), (b[0]-n[0], b[1]-n[1]), (a[0]-n[0], a[1]-n[1])]
    cheeks = []
    for x0, x1 in [(st['cx']+rb, st['cx']+W), (st['cx']-W, st['cx']-rb)]:
        win = yz_prism(hole, x0-1, x1+1).cut(yz_prism(strut, x0-2, x1+2))
        cheeks.append(yz_prism(outline, x0, x1).cut(win))
    return cheeks, dict(rail_top_at_plate_z=z_rail_plate, window_yz=hole,
                        diagonal_deg=math.degrees(math.atan2(q[1]-p[1], q[0]-p[0])))


def floor(spans):
    """The bed diaphragm: full width, plate to the cups' backs. Behind each channel (between
    its cheeks) two triangular windows split by a diagonal keep it a triangulated truss."""
    hw = K.half_width(CELLS)
    slab = K.box(-hw, K.PLATE_Y1-1.0, BED, 2*hw, FLOOR_Y-K.PLATE_Y1+1.0, FLOOR_T)
    cuts = []
    for st in B6.values():
        x0, x1 = st['cx']-st['rb']+2.5, st['cx']+st['rb']-2.5          # the station's plate-window span
        y0 = K.PLATE_Y1+FLOOR_EDGE
        y1 = world(st, -(st['rb']+WALL), u_at(st, -(st['rb']+WALL), BED))[0]-FLOOR_EDGE   # channel back on the bed
        g = FLOOR_EDGE/2*math.hypot(x1-x0, y1-y0)/(y1-y0)              # half the diagonal's width, along X
        for tri in ([(x0+g, y0), (x1, y0), (x1, y1-g*(y1-y0)/(x1-x0))],
                    [(x0, y0+g*(y1-y0)/(x1-x0)), (x0, y1), (x1-g, y1)]):
            cuts.append(K.poly_prism(tri, 'z', BED-1, BED+FLOOR_T+1))
    # Corner relief: the floor's two free front corners (outboard of the outer cheeks, the
    # only first-layer corners with nothing standing on them) get a plan-view round, so an
    # ASA corner has no point to start peeling from. The flap behind them stays: it anchors
    # the plate's ends on the bed.
    R = FLOOR_CORNER_R
    for sx in (-1, 1):
        cx = sx*(hw-R)
        sq = K.box(min(cx, sx*(hw+1)), FLOOR_Y-R, BED-1, R+1, R+1, FLOOR_T+2)
        cuts.append(sq.cut(Part.makeCylinder(R, FLOOR_T+4, V(cx, FLOOR_Y-R, BED-2), V(0, 0, 1))))
    return slab.cut(Part.makeCompound(cuts))


# ---------------------------------------------------------------- plate windows
def plate_windows():
    """Pointed (+Z, 50 deg) windows through the plate between the cheek lines; 8 mm
    mullions continue each cheek up the plate, a rail at z -76..-70 ties them."""
    lines = sorted([(st['cx']-st['rb']-WALL, st['cx']-st['rb']) for st in B6.values()] +
                   [(st['cx']+st['rb'], st['cx']+st['rb']+WALL) for st in B6.values()])
    m = 2.5
    spans = [(a[1]+m, b[0]-m) for a, b in zip(lines, lines[1:])]
    cuts = []
    for x0, x1 in spans:
        for za, zb in [(BED+STRIP, -76.0), (-70.0, -8.0)]:
            cuts.append(K.pointed_window(x0, x1, za, zb, '+Z'))
    return cuts, spans


# ---------------------------------------------------------------- tools
def write_tools(out):
    tools = []
    for key, st in B6.items():
        m = Mesh.Mesh()
        for f in sorted(REF.glob(f"barrels__tool-{st['tool']}-*.stl")):
            m.addMesh(Mesh.Mesh(str(f)))
        path = out/f'{NAME}__tool-{key}.stl'
        m.write(str(path))
        lo = min(p.z for p in m.Points)
        tip = [p for p in m.Points if p.z < lo+0.05]
        tip = [sum(p.x for p in tip)/len(tip), sum(p.y for p in tip)/len(tip), lo]
        tools.append(dict(id=key, stl=path.name, colour=st['colour'], tip=tip))
    return tools


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    host, info = K.receiver(CELLS, HOOP_ROW, POSE, z0=BED)
    win, spans = plate_windows()
    keep = K.peg_keepout(CELLS, HOOP_ROW)
    host = host.cut(Part.makeCompound([w.cut(keep) for w in win])).removeSplitter()
    parts, detail = [], {}
    plastic = dict(receiver_plate_cm3=host.Volume/1000)
    base = floor(spans)
    parts.append(base)
    plastic['floor_cm3'] = base.Volume/1000
    for key, st in B6.items():
        body, sinfo = station(st)
        cheeks, cinfo = back_cheeks(st)
        parts += [body]+cheeks
        detail[key] = dict(sinfo, **cinfo)
        plastic[f'{key}_channel_cm3'] = body.Volume/1000
        plastic[f'{key}_back_cheeks_cm3'] = sum(c.Volume for c in cheeks)/1000
    shape = host.multiFuse(parts).removeSplitter()
    assert shape.isValid() and len(shape.Solids) == 1, (shape.isValid(), len(shape.Solids))
    info.update(K.export(shape, out, NAME, POSE))
    tools = write_tools(out)
    lift = [0.0, round(-LIFT*S, 4), round(LIFT*C, 4)]
    spec = dict(name=NAME, title='v12 barrels, B6 seats kept', pose=POSE, pose_matrix=info['pose_matrix'],
                installed=f'{NAME}__installed.stl', print=info['print_file'], glued=[], glued_print=[],
                tools=[dict(id=t['id'], stl=t['stl'], colour=t['colour'],
                            seat=dict(gravity=True, captured=True),
                            removal=[lift, [0.0, OUT, 0.0]], samples=4000,
                            note='Stands on the B6 ledge and leans 10 deg back into the B6 ring and cup bore '
                                 '(0.65 mm radial play): captured, as on B6.') for t in tools],
                overhang_exceptions=[],
                render_notes=dict(
                    loaded='B6 seats kept: lift 18 mm along the tool, then straight out. Flux (amber), paste (blue), sucker (red).',
                    empty='Rings on U-channels along each tool axis; 50 deg corbels; 1 mm front-edge chamfers; triangulated cheeks; bed floor.',
                    front='Nozzles down into the drip tray below; nothing in front of the barrels.',
                    side='Tool axes lean 10 deg toward the board; cheeks: 50 deg rail + diagonal from the plate foot to the ring.',
                    print='Flat bottom on the bed (floor front corners rounded r 8); only the pegs need support.'))
    (out/f'{NAME}__checks-spec.json').write_text(json.dumps(spec, indent=1))
    loads = []
    for key in ('paste', 'sucker', 'flux'):
        st = B6[key]; W = st['rb']+WALL
        ring = world(st, st['tip'][0]-1.0, st['ring'][1]-2.0)            # ring tip, outer face, near the top
        cup = (st['y_front']-1.0, st['cup_top']-2.0)                       # cup side wall, front top corner
        for what, (y, z) in [('ring', ring), ('cup', cup)]:
            p = [round(st['cx']+W, 3), round(y, 3), round(z, 3)]
            loads.append(dict(id=f'wag-{key}-{what}', what=f'5 N sideways at the {key} {what} front', point=p,
                              radius=3.0, force=[5, 0, 0]))
            loads.append(dict(id=f'press-{key}-{what}', what=f'5 N down at the {key} {what} front', point=p,
                              radius=3.0, force=[0, 0, -5]))
    fea = dict(step=f'{NAME}__installed.step', h=2.0, supports=['pegs'], loads=loads)
    (out/f'{NAME}__fea-spec.json').write_text(json.dumps(fea, indent=1))
    info.update(b6_volume_cm3=B6_VOLUME_CM3, volume_vs_b6=info['volume_mm3']/1000/B6_VOLUME_CM3,
                seats_b6=B6, action=dict(lift_along_axis_mm=LIFT, out_mm=OUT, lift_vector=lift),
                corbel_deg=CORBEL, rail_deg=RAIL_DEG, plate_window_spans_x=spans, stations=detail,
                edge_chamfer_mm=EDGE_CH, floor_corner_round_mm=FLOOR_CORNER_R,
                plastic_before_fuse=plastic,
                nozzle_tips=dict({t['id']: dict(module=[round(v, 2) for v in t['tip']],
                                                station=[round(t['tip'][0]+38.1, 2), round(t['tip'][1], 2), round(t['tip'][2], 2)])
                                  for t in tools}))
    K.save_design(out, NAME, info)
    print(json.dumps({k: info[k] for k in ('volume_mm3', 'solid_mass_asa_g', 'print_bounds', 'volume_vs_b6', 'nozzle_tips')}, indent=1))


if __name__ == '__main__':
    main(Path(sys.argv[1]))
