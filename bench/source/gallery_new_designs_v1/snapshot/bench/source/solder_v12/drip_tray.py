"""v12 drip tray: a 5-cell tray hung under the barrels, catching flux and paste drips in a
removable vase-mode liner. Run with FreeCAD Python: python drip_tray.py OUT_DIR

Design (2026-10-02, v12 brief):
- Printed upright, the flat floor on the bed: a wide, shallow module, so the floor is
  the biggest first layer and every wall rises straight off it. Nothing prints in the
  air but the pegs (hooks on row 0, the PF07 #5 hoop on row 1, flexing in X = the print
  layers for an upright print). common.receiver applies the install-arc hoop fix.
- One tray: a 2 mm floor, two deep side cheeks (webs from the plate's top edge sloping
  28 deg down to a 14 mm front post), a back curb, and a 6 mm front lip, a chamfered
  beam across the front. The cheeks carry the tray's load straight into the plate beside
  the peg columns; with the floor and the lip they make the tray a stiff open box.
  First cut: 45 deg cheeks that dropped to a 5 mm lip at y 50; 5 N down at the lip
  centre sagged 0.503 mm (0.17 of it in the cheeks' thin front strip). Deep cheeks:
  0.358 mm; then the 6 mm lip: 0.261 mm (pegs support).
- Rev 2 (Frodo bench review, finding 2): a 20 mm wide, 3 mm deep finger scallop in the
  lip's top centre, a circular arc (r 18.2) cut straight through the lip in Y. Its faces
  all look up (steepest 33 deg from horizontal at the edges), so the upright print has no
  new overhang and no island; the lip stays 6 mm tall either side, so the liner's base
  still bears on full-height lip over 2 x 40 mm and retention is unchanged. The finger
  goes in at the centre, 37 mm from the flux needle, and lifts the liner's front wall
  from the outside instead of a thumb inside a flux-coated rim.
- Every wall rises straight off the floor; the only sloped faces face up. The plate is
  opened by a row of pointed (55 deg) windows between the peg columns, sill flush with
  the curb top, so it carries no bridges.
- The liner fills the tray from the back curb to the lip: a tapered rounded box printed
  in spiral vase mode from a filled solid. Located by the curb and the lip (base, 1 mm)
  and the cheeks (rim, 2 mm a side, so the return needs no aiming); the rim stays 2 mm
  off the plate windows. Out: lift the front 6.4 mm and pull forward; it passes under
  the stored nozzles with ~10 mm to spare. Back: rest it on the lip's 55 deg outer ramp
  and push; it drops in behind the lip's 60 deg inner face, which holds it when bumped.
- Tip-height rule (hard number, asserted below against the barrels-b6seats tools): every
  barrel tip must sit above station z -141.6 = liner rim -151.0 + removal lift 6.4 +
  3.0 margin, and inside the usable catch window. A lower cup, a longer needle or a
  taller liner trips the assert instead of being rediscovered at the bench.

Coordinates: module-local holder coordinates as common.py (X lateral, +X is the user's
left facing the board; Y out of the board, Z up, top peg row at Z 0.12). Station
position: x 38.1, z -127 (top-row centre).
"""
from pathlib import Path
import json
import math
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as K                            # noqa: E402
import FreeCAD as A                           # noqa: E402
import Mesh                                   # noqa: E402
import MeshPart                               # noqa: E402
import Part                                   # noqa: E402

V = A.Vector
ID = 'drip-tray'
POSE = 'upright'
NAME = f'part-solder-{ID}__v12__{POSE}__fit-pf02c9-hoop5'
LINER = f'part-solder-{ID}-liner__v12__vase-filled'
CELLS, HOOP_ROW = 5, 1
STATION = (38.1, 0.0, -127.0)                  # module origin in station coordinates
REF = Path(__file__).resolve().parents[2]/'reference/solder-tools'
BARRELS_TO_LOCAL_Z = 127.0                     # barrels origin z 0, drip tray origin z -127
# The barrels module this tray serves (FINAL: B6 seats, owner-photo-scaled tools, unmoved).
BARRELS_DIR = Path(__file__).resolve().parents[2]/'reviews/v12-build/barrels-b6seats'
BARRELS_NAME = 'part-solder-barrels__v12__upright__fit-pf02c9-hoop5'
BARRELS_STATION = (38.1, 0.0, 0.0)
BARREL_TOOLS = {'flux': 0, 'paste': 1, 'sucker': 2}   # barrels-b6seats tool id -> B6 proxy group
BARREL_TILT = 10.0                             # tool axes lean 10 deg, tips toward +Y

HW = K.half_width(CELLS)                       # 62.5
Y0, Y1 = K.PLATE_Y0, K.PLATE_Y1                # plate 0.15 .. 5.55
Z1 = K.PLATE_Z1                                # 5.12, the plate's top lip

# Tray
FLOOR_T = 2.0
Z_FT = -44.0                                   # floor top (the liner sits here)
Z_FB = Z_FT-FLOOR_T                            # floor bottom = the bed face
CHEEK_T = 2.4
XI = HW-CHEEK_T                                # cheek inner face, +-60.1
CURB_D, CURB_H = 4.0, 3.0                      # back curb: base stop, keeps the rim off the plate windows
LIP_H, LIP_TOP = 6.0, 3.0                      # front lip above the floor top; flat top width
LIP_IN_DEG = 60.0                              # lip inner face (retention), from horizontal
LIP_OUT_DEG = 55.0                             # lip outer face (lead-in for the return)
# FEA with the deep cheeks (5 N down at the lip centre, pegs support): lip 5/2/45 0.358 mm; 5/3.5/55
# 0.329; 6/2/45 0.268; floor 2.4 instead of 2.0 0.294 (+3.9 cm3). The lip's height is
# the cheap lever; 6 mm keeps the lifted liner 9.9 mm under the lowest B6 tip.
CORNER = 2.0                                   # plan-view 45 deg chamfer on the front corners (cheek posts)
CLR = 1.0                                      # liner clearance to the curb and the lip (base)
CLR_SIDE = 2.0                                 # rim to cheek: lateral play, so the return needs no aiming
CHEEK_FRONT_H = 12.0                           # cheek front top above the floor top (rim is at 20)
CHEEK_FRONT_C = 4.0                            # 45 deg chamfer on the cheek's top front corner
# Finger scallop (Frodo rev 2 #2): a circular arc through the lip, chord SCALLOP_W at the lip top,
# SCALLOP_D deep at x 0. Edge slope asin(W/2/R) = 33 deg: every cut face looks up.
SCALLOP_W, SCALLOP_D = 20.0, 3.0
SCALLOP_R = (SCALLOP_W**2/4+SCALLOP_D**2)/(2*SCALLOP_D)

# Liner (vase mode): tapered rounded box
L_H = 20.0
L_TAPER = 3.0                                  # per side over L_H (8.5 deg draft: nests, slides out)
L_RB = 8.0                                     # base corner radius (top = L_RB + L_TAPER)
L_WALL, L_BOTTOM = 0.6, 1.0                    # in-use model: vase wall line width, bottom layers
L_HX_T = XI-CLR_SIDE                           # rim half-length 58.1
L_HX_B = L_HX_T-L_TAPER                        # base half-length 55.1
L_YB = Y1+CURB_D+CLR                           # base back edge 10.55
L_YF = 68.0                                    # base front edge
LIP_Y = L_YF+CLR                               # lip inner foot 69.0
LIP_Y_TOP = LIP_Y+LIP_H/math.tan(math.radians(LIP_IN_DEG))
Y_FRONT = LIP_Y_TOP+LIP_TOP+LIP_H/math.tan(math.radians(LIP_OUT_DEG))
REMOVE_LIFT = LIP_H+0.4

# Catch window and the tip-height rule
USABLE_INSET = 2.0                             # off the inner rim: liner play (2 side / 1 fore-aft) + 1 drip spread
TIP_MARGIN = 3.0                               # tips stay this far above the lifted rim
LINER_PLATE_COPIES = 3                         # spares: liners per vase job (scratch/slice_liner_plate.py stagger3 69 5)

# Plate windows: pointed arches between the peg columns
WIN_X = 43.0                                   # windows within +-WIN_X (peg columns at +-50.8)
WIN_N, WIN_POST = 4, 5.0
WIN_Z = (Z_FT+CURB_H, -1.0)                    # sill flush with the curb top; top chord 6.1 mm
WIN_DEG = 55.0


def rrect(cx, cy, hx, hy, r, z):
    """Closed rounded-rectangle wire in the plane Z = z."""
    c = [(cx+hx-r, cy+hy-r, 0), (cx-hx+r, cy+hy-r, 90), (cx-hx+r, cy-hy+r, 180), (cx+hx-r, cy-hy+r, 270)]
    edges = []
    for i, (px, py, a) in enumerate(c):
        arc = Part.ArcOfCircle(Part.Circle(V(px, py, z), V(0, 0, 1), r), math.radians(a), math.radians(a+90)).toShape()
        edges.append(arc)
        nx, ny, na = c[(i+1) % 4]
        p0 = V(px+r*math.cos(math.radians(a+90)), py+r*math.sin(math.radians(a+90)), z)
        p1 = V(nx+r*math.cos(math.radians(na)), ny+r*math.sin(math.radians(na)), z)
        edges.append(Part.LineSegment(p0, p1).toShape())
    return Part.Wire(Part.__sortEdges__(edges))


def frustum(cx, cy, hx, hy, r, z0, z1, k):
    """Rounded box from z0 to z1 whose outline grows by k per mm of height."""
    h = z1-z0
    w0 = rrect(cx, cy, hx, hy, r, z0)
    w1 = rrect(cx, cy, hx+k*h, hy+k*h, r+k*h, z1)
    return Part.makeLoft([w0, w1], True, True)


def liner():
    """(filled solid for vase mode, hollow in-use model), installed coordinates."""
    k = L_TAPER/L_H
    cy, hy = (L_YB+L_YF)/2, (L_YF-L_YB)/2
    filled = frustum(0, cy, L_HX_B, hy, L_RB, Z_FT, Z_FT+L_H, k)
    t = L_WALL/math.cos(math.atan(k))           # horizontal wall thickness
    zb = Z_FT+L_BOTTOM
    inner = frustum(0, cy, L_HX_B+k*L_BOTTOM-t, hy+k*L_BOTTOM-t, L_RB+k*L_BOTTOM-t, zb, Z_FT+L_H+1.0, k)
    hollow = filled.cut(inner)
    assert filled.isValid() and hollow.isValid() and len(hollow.Solids) == 1
    return filled, hollow


def tray():
    """Floor, cheeks, back curb and front lip (installed coordinates)."""
    floor = K.box(-HW, Y0, Z_FB, 2*HW, Y_FRONT-Y0, FLOOR_T)
    zl = Z_FT+LIP_H
    yo = Y_FRONT-LIP_H/math.tan(math.radians(LIP_OUT_DEG))
    # Cheek: a deep web from the plate's top edge sloping straight down to a 14 mm tall
    # front post (the first cut fell to the 5 mm lip height at y 50 and its thin front
    # strip let the lip sag 0.50 mm at 5 N).
    zf = Z_FT+CHEEK_FRONT_H
    prof = [(Y0, Z_FB), (Y0, Z1), (Y1, Z1), (Y_FRONT-CHEEK_FRONT_C, zf), (Y_FRONT, zf-CHEEK_FRONT_C), (Y_FRONT, Z_FB)]
    cheeks = [K.poly_prism(prof, 'x', XI, HW), K.poly_prism(prof, 'x', -HW, -XI)]
    lip = K.poly_prism([(LIP_Y, Z_FT-0.01), (LIP_Y_TOP, zl), (yo, zl), (Y_FRONT, Z_FT), (Y_FRONT, Z_FT-0.01)],
                       'x', -XI-0.01, XI+0.01)
    curb = K.box(-XI-0.01, Y1-0.01, Z_FT-0.01, 2*XI+0.02, CURB_D+0.01, CURB_H+0.01)
    return [floor, lip, curb]+cheeks, dict(cheek_profile_yz=prof, lip_top_z=zl, cheek_slope_deg=math.degrees(math.atan2(Z1-zf, Y_FRONT-CHEEK_FRONT_C-Y1)))


def scallop():
    """The finger scallop: a cylinder along Y through the lip only (y LIP_Y-0.5 .. Y_FRONT+0.5),
    bottom SCALLOP_D below the lip top at x 0. It stays 3 mm above the floor top."""
    zc = Z_FT+LIP_H-SCALLOP_D+SCALLOP_R
    y0, y1 = LIP_Y-0.5, Y_FRONT+0.5
    assert zc-SCALLOP_R > Z_FT+0.5
    cyl = Part.makeCylinder(SCALLOP_R, y1-y0, V(0, y0, zc), V(0, 1, 0))
    return cyl, dict(width_mm=SCALLOP_W, depth_mm=SCALLOP_D, radius_mm=round(SCALLOP_R, 3),
                     bottom_z_local=Z_FT+LIP_H-SCALLOP_D, centre_x_local=0.0,
                     edge_slope_deg=round(math.degrees(math.asin(SCALLOP_W/2/SCALLOP_R)), 1),
                     full_lip_each_side_mm=round(XI-SCALLOP_W/2, 1))


def windows():
    w = (2*WIN_X-(WIN_N-1)*WIN_POST)/WIN_N
    out = []
    for i in range(WIN_N):
        x0 = -WIN_X+i*(w+WIN_POST)
        out.append(K.pointed_window(x0, x0+w, WIN_Z[0], WIN_Z[1], '+Z', angle_deg=WIN_DEG))
    cut = Part.makeCompound(out).cut(K.peg_keepout(CELLS, HOOP_ROW))
    return cut, dict(count=WIN_N, width_mm=w, post_mm=WIN_POST, z=WIN_Z, roof_deg=WIN_DEG,
                     roof_rise_mm=w/2*math.tan(math.radians(WIN_DEG)))


def corner_cuts():
    out = []
    for s in (1, -1):
        tri = [(s*(HW-CORNER-1), Y_FRONT+1), (s*(HW+1), Y_FRONT+1), (s*(HW+1), Y_FRONT-CORNER-1)]
        out.append(K.poly_prism(tri, 'z', Z_FB-1, Z1+1))
    return out


def reference_nozzles(out):
    """B6 barrel nozzle tips (barrels-local -> module-local), for the catch window and renders.
    Flux nozzle + needle, paste nozzle, and the solder sucker's lower 30 mm."""
    m = Mesh.Mesh()
    tips = {}
    for f in ['barrels__tool-0-2.stl', 'barrels__tool-0-3.stl', 'barrels__tool-1-2.stl']:
        p = Mesh.Mesh(str(REF/f)); p.translate(0, 0, BARRELS_TO_LOCAL_Z); m.addMesh(p)
        b = p.BoundBox; tips[f] = [round(v, 2) for v in (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin)]
    s = Mesh.Mesh(str(REF/'barrels__tool-2-0.stl')); s.translate(0, 0, BARRELS_TO_LOCAL_Z)
    sh = Part.Shape(); sh.makeShapeFromMesh(s.Topology, 0.05)
    solid = Part.makeSolid(sh)
    zb = s.BoundBox.ZMin
    low = solid.common(K.box(-200, -200, zb-1, 400, 400, 31))
    lm = MeshPart.meshFromShape(Shape=low, LinearDeflection=0.05, AngularDeflection=0.2, Relative=False)
    m.addMesh(lm)
    b = low.BoundBox; tips['barrels__tool-2-0.stl (lower 30 mm)'] = [round(v, 2) for v in (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin)]
    m.write(str(out/f'{NAME}__ref-b6-nozzles.stl'))
    return tips


def barrel_tips():
    """Lowest point of each barrels-b6seats tool in station coordinates (the module's own tool
    STLs; the B6 proxy groups if that build is missing). The centre of the lowest 0.05 mm."""
    out = {}
    for key, grp in BARREL_TOOLS.items():
        f = BARRELS_DIR/f'{BARRELS_NAME}__tool-{key}.stl'
        if f.exists():
            m, src = Mesh.Mesh(str(f)), f'reviews/v12-build/barrels-b6seats/{f.name}'
        else:
            m, src = Mesh.Mesh(), f'reference/solder-tools/barrels__tool-{grp}-*.stl'
            for p in sorted(REF.glob(f'barrels__tool-{grp}-*.stl')):
                m.addMesh(Mesh.Mesh(str(p)))
        pts = [(p.x, p.y, p.z) for p in m.Points]
        zmin = min(p[2] for p in pts)
        low = [p for p in pts if p[2] <= zmin+0.05]
        c = [sum(p[i] for p in low)/len(low) for i in range(3)]
        out[key] = dict(source=src, station=[round(c[0]+BARRELS_STATION[0], 2), round(c[1]+BARRELS_STATION[1], 2),
                                             round(zmin+BARRELS_STATION[2], 2)])
    return out


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    host, info = K.receiver(CELLS, HOOP_ROW, POSE, z0=Z_FB)
    win, winfo = windows()
    host = host.cut(win).removeSplitter()
    parts, tinfo = tray()
    shape = host.multiFuse(parts).removeSplitter()
    sc, sinfo = scallop()
    shape = shape.cut(corner_cuts()+[sc]).removeSplitter()
    assert shape.isValid() and len(shape.Solids) == 1, (shape.isValid(), len(shape.Solids))
    info.update(K.export(shape, out, NAME, POSE))

    # The liner: filled solid for spiral vase mode (print pose: base on the bed), and the
    # hollow in-use model as the checked tool.
    filled, hollow = liner()
    K.write(hollow, out/f'{NAME}__tool-liner.stl', lin=0.02)
    filled.exportStep(str(out/f'{LINER}__installed.step'))
    fp = filled.copy(); bb = fp.BoundBox; fp.translate(V(-bb.XMin, -bb.YMin, -bb.ZMin))
    fp.exportStep(str(out/f'{LINER}__print-vase.step'))
    lfile = K.write(fp, out/f'{LINER}__print-vase.stl', lin=0.01)
    tips = reference_nozzles(out)

    # Catch window (inner rim) in module-local and station coordinates.
    k = L_TAPER/L_H
    t = L_WALL/math.cos(math.atan(k))
    rim = dict(x=[-(L_HX_T-t), L_HX_T-t], y=[L_YB-L_TAPER+t, L_YF+L_TAPER-t], z=Z_FT+L_H)
    st = dict(x=[round(v+STATION[0], 2) for v in rim['x']], y=[round(v, 2) for v in rim['y']], z=round(rim['z']+STATION[2], 2))
    usable = dict(x=[round(st['x'][0]+USABLE_INSET, 1), round(st['x'][1]-USABLE_INSET, 1)],
                  y=[round(st['y'][0]+USABLE_INSET, 1), round(st['y'][1]-USABLE_INSET, 1)])
    lowest_tip = min(v[4] for v in tips.values())
    removal = [[0, 0, REMOVE_LIFT], [0, 95, 0]]

    # The tip-height rule, checked against the barrels module's own tools (station coordinates).
    tip_floor = round(st['z']+REMOVE_LIFT+TIP_MARGIN, 2)          # -141.6
    btips = barrel_tips()
    c10, s10 = math.cos(math.radians(BARREL_TILT)), math.sin(math.radians(BARREL_TILT))
    for key, bt in btips.items():
        x, y, z = bt['station']
        assert z >= tip_floor, (f'{key} tip at station z {z} is below the drip-tray rule {tip_floor}', bt)
        assert usable['x'][0] <= x <= usable['x'][1] and usable['y'][0] <= y <= usable['y'][1], \
            (f'{key} tip outside the usable catch window', bt, usable)
        extra = (z-tip_floor)/c10                                 # more nozzle/needle length along the 10 deg axis
        bt.update(above_floor_mm=round(z-tip_floor, 2), above_lifted_rim_mm=round(z-st['z']-REMOVE_LIFT, 2),
                  above_rim_mm=round(z-st['z'], 2), x_margin_mm=round(min(x-usable['x'][0], usable['x'][1]-x), 1),
                  y_margin_mm=round(min(y-usable['y'][0], usable['y'][1]-y), 1),
                  longer_tip_allowed_mm=round(extra, 1), tip_y_at_that_length=round(y+extra*s10, 1))

    spec = dict(name=NAME, title='v12 drip tray + vase liner', pose=POSE, pose_matrix=info['pose_matrix'],
                installed=f'{NAME}__installed.stl', print=info['print_file'], glued=[], glued_print=[],
                tools=[dict(id='liner', stl=f'{NAME}__tool-liner.stl', colour='#e0a040', seat=dict(gravity=True),
                            removal=removal, samples=4000),
                       dict(id='ref-b6-nozzles', stl=f'{NAME}__ref-b6-nozzles.stl', colour='#ccd2d5',
                            seat=dict(min_contacts=0), reference_only=True,
                            note='Reference only: the B6 barrels nozzle tips (held by the barrels module, not here).')],
                overhang_exceptions=[],
                render_notes=dict(
                    loaded='Liner (amber) under the barrel nozzles (grey, reference). Finger in the lip scallop, lift the front 6.4, pull.',
                    empty='Floor, deep cheek webs, back curb, 6 mm chamfered front lip with a 20 x 3 mm finger scallop at the centre.',
                    front=f'Catch window x +-57.5, y 8.2-70.4; rim at station z -151. Every barrel tip must stay above station z {tip_floor}.',
                    side='Cheek web: plate top down to a 14 mm front post; lip 6 mm (3 at the scallop). Liner rim 2 mm off cheeks and plate.',
                    print='Floor on the bed; organic supports under the pegs only. Liners: separate job, spiral vase, by object.'))
    (out/f'{NAME}__checks-spec.json').write_text(json.dumps(spec, indent=1))
    zs = Z_FT+LIP_H-SCALLOP_D-0.5                                   # 0.5 under the scallop's lowest line
    ys = (LIP_Y+(zs-Z_FT)/math.tan(math.radians(LIP_IN_DEG))+Y_FRONT-(zs-Z_FT)/math.tan(math.radians(LIP_OUT_DEG)))/2
    scallop_pt = [0.0, round(ys, 3), zs]
    lip_pt = [SCALLOP_W/2+5.0, LIP_Y_TOP+LIP_TOP/2, Z_FT+LIP_H-0.5]
    corner_pt = [L_HX_B-6.0, LIP_Y_TOP+LIP_TOP/2, Z_FT+LIP_H-0.5]
    ym = (Y1+Y_FRONT)/2
    cheek_pt = [HW-0.5, ym, Z1-(Z1-Z_FT-CHEEK_FRONT_H)*(ym-Y1)/(Y_FRONT-CHEEK_FRONT_C-Y1)-1.5]
    fea = dict(step=f'{NAME}__installed.step', h=2.0, supports=['pegs'],
               loads=[dict(id='wag', what='5 N sideways at the lip centre, under the scallop (the liner bears on the lip: the farthest tool-bearing point)',
                           point=scallop_pt, radius=3.0, force=[5, 0, 0]),
                      dict(id='press', what='5 N down at the lip centre, under the scallop', point=scallop_pt, radius=3.0, force=[0, 0, -5]),
                      dict(id='press-lip-beside', what='5 N down on the full-height lip top 15 mm off centre (beside the scallop)',
                           point=lip_pt, radius=3.0, force=[0, 0, -5]),
                      dict(id='press-floor', what='5 N down on the floor centre under the liner', point=[0.0, 40.0, Z_FT], radius=3.0,
                           force=[0, 0, -5]),
                      dict(id='press-corner', what='5 N down on the lip near the right end', point=corner_pt, radius=3.0,
                           force=[0, 0, -5]),
                      dict(id='poke-cheek', what='5 N sideways (inward) on the right cheek top edge, mid-length',
                           point=cheek_pt, radius=3.0, force=[-5, 0, 0])])
    (out/f'{NAME}__fea-spec.json').write_text(json.dumps(fea, indent=1))
    info.update(module=ID, cells=CELLS, hoop_row=HOOP_ROW, station_origin=STATION, tray=dict(
        floor_t=FLOOR_T, floor_top_z=Z_FT, cheek_t=CHEEK_T, curb=[CURB_D, CURB_H], lip_h=LIP_H, lip_top=LIP_TOP,
        lip_inner_deg=LIP_IN_DEG, lip_outer_deg=LIP_OUT_DEG, lip_foot_y=LIP_Y, front_y=Y_FRONT, corner_chamfer=CORNER,
        finger_scallop=sinfo, **tinfo),
        windows=winfo,
        liner=dict(file=lfile, height=L_H, taper_per_side=L_TAPER, base=[2*L_HX_B, L_YF-L_YB], top=[2*L_HX_T, L_YF-L_YB+2*L_TAPER],
                   base_corner_r=L_RB, base_y=[L_YB, L_YF], floor_z=Z_FT, clearance=CLR, filled_volume_mm3=filled.Volume,
                   in_use_model_volume_mm3=hollow.Volume, removal=removal,
                   plate=dict(copies=LINER_PLATE_COPIES, how='one spiral-vase job, print_sequence by object',
                              script='reviews/v12-build/drip-tray/scratch/slice_liner_plate.py', args='stagger3 69 5',
                              layout='two along Y + one turned 90 deg, 69 mm rim to rim (Orca wants the P1S 68 mm '
                                     'extruder clearance between by-object prints taller than the 4.2 mm nozzle)',
                              job='print/slice-v12/V12-drip-tray-liner-stagger3-ASA-vase')),
        catch_window=dict(local=rim, station=st, usable_station=usable, b6_tips_local=tips, lowest_tip_z_local=lowest_tip,
                          rim_below_lowest_tip_mm=round(lowest_tip-rim['z'], 2),
                          rim_below_lowest_tip_while_removing_mm=round(lowest_tip-rim['z']-REMOVE_LIFT, 2)),
        tip_rule=dict(rule=f'every barrel tip above station z {tip_floor} (rim {st["z"]} + lift {REMOVE_LIFT} + margin {TIP_MARGIN}) '
                           f'and inside usable x {usable["x"]}, y {usable["y"]}',
                      tip_floor_station_z=tip_floor, barrels_b6seats_tips=btips))
    K.save_design(out, NAME, info)
    print(json.dumps({k: info[k] for k in ('volume_mm3', 'solid_mass_asa_g', 'print_bounds', 'tip_rule')}, indent=1))
    print(json.dumps(info['tray']['finger_scallop']), json.dumps(info['hoop']['detail'].get('root_clip_radius_mm')))


if __name__ == '__main__':
    main(Path(sys.argv[1]))
