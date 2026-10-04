"""Shared construction for the v12 solder station modules (FreeCAD Python).

Every module hangs on the same receiver as the v11 tweezer rack: the PF02 #9 hook and
crush ribs on the top row, loose conformal bearing pegs every other row between, and the
PF07 #5 hoop (0.8 mm arm, 2.0 tip, even catch wall, 0.9 mm nose, 0.4 mm root gusset) on
the bottom row.

Owner rules carried into every module (2026-10-02):
- Choose the bed face first: the right cheek (-X) or the flat bottom. Nothing prints in
  the air but the pegs. Bridges or overhangs, never a cantilever.
- Flexing features flex in the print layers: the hoop is turned -90 deg about the peg
  axis for cheek prints, and left as is (flexing in X) for upright prints.
- Glue-in parts seat in blind pockets, never through-holes.
- Thin cheeks flex: stiffen with edge flanges, triangulated struts, gussets and webs.
- Minimal plastic without sacrificing looks, strength or function.

Coordinates as v9-v11: X lateral, Y out of the board (pegs at Y < 0.15), Z up; the top
peg row's hole centre is at Z = 0.12 and the plate's sharp lip at Z = 5.12.
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
from peg_fit_ladder import box               # noqa: E402,F401  (re-exported for modules)
from peg_interface import receive_pegs       # noqa: E402

V = A.Vector
PITCH, FACE = 25.4, 0.15
PLATE_Y0, PLATE_Y1 = 0.15, 5.55             # rear contact face and front of the 5.4 mm wall
PLATE_Z1 = 5.12                             # the sharp lip, 5 mm above the top hole centre
TOP = dict(upper_ribs_mm=0.50, clamp_mm=0.49)
HOOP = {'concept': 'HOOP', 'arm_mm': 0.8, 'tip_half': 2.0, 'even_catch_wall': True,
        'ramp_wall': True, 'nose_mm': 0.9, 'root_gusset_mm': 0.4}
BODY_RIBS = 0.30
# Install-arc study (bench/reviews/v12-build/install-arc, 2026-10-02): swinging a part in on its
# hooks holds the hoop row 0.16-0.30 mm above the hole centre, and the hoop's rigid root (the
# 0.4 mm root gusset, clipped only 0.05 mm inside the hole, and the band shoulder in front of
# the catch) hit the hole wall by 0.04-0.15 mm. Clipping that root to r 2.95 about the hole axis,
# and dropping the turned (cheek-print) hoop 0.10 mm so both arms share the lift, clears all
# rigid material on rows 1-6 in both poses; arms flex no more than the tested PF07 #5 coupon and
# the seated catch still holds on 3.80 and 3.94 mm boards. Catch, crest, ramp and nose unchanged.
HOOP_ROOT_CLIP_R = 2.95
HOOP_CHEEK_DROP = 0.10
POSES = ('right-cheek', 'upright')
ASA_G_PER_CM3 = 1.07


def row_z(k):
    return 0.12-PITCH*k


def columns(cells):
    """Two mounting columns, one cell in from each edge (BENCH_HOLDERS: use two whenever they fit)."""
    if cells < 2:
        return [0.0]
    h = (cells-1)*PITCH/2
    return [-h, h]


def half_width(cells):
    """Width = 25.4 mm x cells - 2 mm."""
    return PITCH*cells/2-1.0


def turn(shape, x, z, deg=-90):
    """Rotate about the peg axis (parallel to Y) through (x, z); -90 maps +X to +Z."""
    s = shape.copy(); s.rotate(V(x, 0, z), V(0, 1, 0), deg); return s


def poly_prism(points, axis, a0, a1):
    """Extrude a closed 2D outline. axis 'x': points are (y, z), extruded x=a0..a1;
    'y': (x, z), y=a0..a1; 'z': (x, y), z=a0..a1."""
    if axis == 'x':
        vs = [V(a0, p, q) for p, q in points]; d = V(a1-a0, 0, 0)
    elif axis == 'y':
        vs = [V(p, a0, q) for p, q in points]; d = V(0, a1-a0, 0)
    else:
        vs = [V(p, q, a0) for p, q in points]; d = V(0, 0, a1-a0)
    return Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(d)


def pointed_window(x0, x1, za, zb, up, angle_deg=50.0, y0=PLATE_Y0-0.01, y1=PLATE_Y1+0.01):
    """A window through the plate whose print-top end is a point with faces at angle_deg
    from horizontal, so it never needs a bridge. up='+X' for cheek prints, '+Z' for
    upright prints (print-up direction in holder coordinates)."""
    t = math.tan(math.radians(angle_deg))
    if up == '+X':
        h = (zb-za)/2*t                          # rise in X of each roof face over its half-height run
        pent = [(x0, za), (x1-h, za), (x1, (za+zb)/2), (x1-h, zb), (x0, zb)]
    elif up == '+Z':
        h = (x1-x0)/2*t
        pent = [(x0, za), (x1, za), (x1, zb-h), ((x0+x1)/2, zb), (x0, zb-h)]
    else:
        raise ValueError(up)
    return poly_prism(pent, 'y', y0, y1)


def hoop_geometry(zl, pose, fix=True):
    """PF07 #5 hoop (add, cut, info) at the column origin (x = 0), before any turn. With
    fix, the install-arc root clip and, for cheek prints, the 0.10 mm drop (applied along
    local -X, which the -90 deg turn maps to -Z)."""
    add, cut, info = C.concept_geometry(HOOP, zl, FACE)
    if not fix:
        return add, cut, info
    rear = FACE-G.BOARD
    dz = HOOP_CHEEK_DROP if pose == 'right-cheek' else 0.0
    add = [a.copy() for a in add]; cut = [c.copy() for c in cut]
    if dz:
        for a in add+cut:
            a.translate(V(-dz, 0, 0))
    cyl = Part.makeCylinder(HOOP_ROOT_CLIP_R, 40, V(0, rear-25, zl), V(0, 1, 0))
    front = box(-10, rear-0.05, zl-10, 20, 10, 20)
    band = add[0].cut(front.cut(cyl))
    add = [band]+[a.common(cyl) for a in add[1:]]
    info = dict(info, root_clip_radius_mm=HOOP_ROOT_CLIP_R, cheek_offset_down_mm=dz)
    return add, cut, info


def receiver(cells, hoop_row, pose, bearing_rows=None, x0=None, x1=None, z0=None, z1=PLATE_Z1, hoop_fix=True):
    """The receiving plate with integral pegs.

    hooks on row 0; bearing locators on bearing_rows (default every other row between);
    the PF07 #5 hoop on hoop_row, turned into the cheek plane for 'right-cheek' prints.
    Returns (shape, info). The plate spans x0..x1 (default the full module width),
    Y 0.15..5.55 and z0..z1 (default 6 mm below the hoop row's centre).
    """
    assert pose in POSES, pose
    cols = columns(cells)
    hw = half_width(cells)
    x0 = -hw if x0 is None else x0
    x1 = hw if x1 is None else x1
    zl = row_z(hoop_row)
    z0 = zl-6.0 if z0 is None else z0
    if bearing_rows is None:
        bearing_rows = [k for k in range(2, hoop_row, 2)]
    path = G.fit_file(TOP['clamp_mm'])
    canonical = P.FIT_SOURCE
    P.FIT_SOURCE = PV.FIT_SOURCE = path
    try:
        fit = P.parse(path.read_bytes())
        plate = box(x0, PLATE_Y0, z0, x1-x0, PLATE_Y1-PLATE_Y0, z1-z0)
        reference = P.load_reference()
        upper = [s for s in reference.Solids if s.BoundBox.ZMax > -9.9]
        lower = [s for s in reference.Solids if s.BoundBox.ZMax < -9.9][0]
        shape, reports = plate, []
        for x in cols:
            ref = Part.makeCompound(upper+[lower]); ref.translate(V(x, 0, 0))
            shape, r = receive_pegs(ref, shape, include_lower=False)
            reports.append(r)
        elbow = reports[0]['peg_profile']['elbow_center_y_mm']
        add, cut = [], []
        zu = fit['PEG_SEAT_DROP']
        for x in cols:
            for s in G.side_ribs(zu, TOP['upper_ribs_mm'], max(elbow, FACE-G.BOARD)+0.3, FACE+1.0, lead=G.UPPER_LEAD)[0]:
                s = s.copy(); s.translate(V(x, 0, 0)); add.append(s)
            for k in bearing_rows+[hoop_row]:
                loc = lower.copy(); loc.translate(V(x, 0, row_z(k)-row_z(1))); add.append(loc)
            for s in G.side_ribs(zl, BODY_RIBS, FACE-G.BOARD+0.2, FACE+1.0, lead=1.0)[0]:
                s = s.copy(); s.translate(V(x, 0, 0)); add.append(s)
            ha, hc, hinfo = hoop_geometry(zl, pose, hoop_fix)
            for s in ha:
                s = s.copy(); s.translate(V(x, 0, 0))
                add.append(turn(s, x, zl) if pose == 'right-cheek' else s)
            for s in hc:
                s = s.copy(); s.translate(V(x, 0, 0))
                cut.append(turn(s, x, zl) if pose == 'right-cheek' else s)
        shape = shape.multiFuse(add).removeSplitter()
        shape = shape.cut(cut).removeSplitter()
        assert shape.isValid() and len(shape.Solids) == 1
        orient = ('hoop band in the cheek plane (turned -90 deg about the peg axis), flexes in Z'
                  if pose == 'right-cheek' else 'hoop band horizontal, flexes in X (the print layers)')
        info = dict(fit_file=str(path.relative_to(P.ROOT)), top=TOP, columns_x_mm=cols,
                    plate=dict(x0=x0, x1=x1, y0=PLATE_Y0, y1=PLATE_Y1, z0=z0, z1=z1),
                    hoop=dict(HOOP, body_ribs_mm=BODY_RIBS, orientation=orient, detail=hinfo),
                    rows=dict(hooks=[0], bearing=bearing_rows, hoop=[hoop_row],
                              empty=[k for k in range(1, hoop_row) if k not in bearing_rows]),
                    predicted_clamp_interference_at_3p94_mm=-reports[0]['peg_profile']['predicted_clearance_at_3p94_board_mm'])
        return shape, info
    finally:
        P.FIT_SOURCE = PV.FIT_SOURCE = canonical


def peg_keepout(cells, hoop_row, bearing_rows=None, r=4.6):
    """Cylinders (Y 0.15..PLATE_Y1+1) around each peg row/column: keep windows and cuts
    out of the peg roots. Use as `window.cut(peg_keepout(...))`."""
    if bearing_rows is None:
        bearing_rows = [k for k in range(2, hoop_row, 2)]
    out = []
    for x in columns(cells):
        for k in [0]+bearing_rows+[hoop_row]:
            out.append(Part.makeCylinder(r, PLATE_Y1+1.0, V(x, -0.5, row_z(k)), V(0, 1, 0)))
    return Part.makeCompound(out)


def band(p, q, inward, width, x0, x1, extend=0.0):
    """A straight strip in a YZ section from p to q (each (y, z)), width toward `inward`
    (a (dy, dz) hint), extruded X = x0..x1. Cheek flanges, struts, ribs."""
    dy, dz = q[0]-p[0], q[1]-p[1]; L = math.hypot(dy, dz); uy, uz = dy/L, dz/L
    ny, nz = -uz, uy
    if ny*inward[0]+nz*inward[1] < 0:
        ny, nz = -ny, -nz
    a = (p[0]-uy*extend, p[1]-uz*extend); b = (q[0]+uy*extend, q[1]+uz*extend)
    poly = [a, b, (b[0]+ny*width, b[1]+nz*width), (a[0]+ny*width, a[1]+nz*width)]
    return poly_prism(poly, 'x', x0, x1)


def pose_transform(shape, pose):
    """(print-pose shape, 4x4 matrix) for 'right-cheek' (the -X cheek on the bed: print
    z = holder X - XMin) or 'upright' (the flat bottom on the bed). Rotation is exact
    (transformShape, no B-spline conversion) and the shift uses a tight bounding box,
    so the matrix maps the installed STL onto the print STL."""
    m = A.Matrix()
    if pose == 'right-cheek':
        m.rotateY(math.radians(-90))
    elif pose != 'upright':
        raise ValueError(pose)
    s = shape.copy(); s.transformShape(m)
    bb = s.optimalBoundingBox()
    t = A.Matrix(); t.move(V(-bb.XMin, -bb.YMin, -bb.ZMin))
    s.transformShape(t)
    return s, t.multiply(m)


def print_pose(shape, pose):
    return pose_transform(shape, pose)[0]


def pose_matrix(shape, pose):
    """4x4 (row-major list) taking installed holder coordinates to the print pose."""
    m = pose_transform(shape, pose)[1]
    return [m.A11, m.A12, m.A13, m.A14, m.A21, m.A22, m.A23, m.A24, m.A31, m.A32, m.A33, m.A34, 0, 0, 0, 1]


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


def export(shape, out, name, pose, extra=None):
    """Installed STEP/STL, print-pose STL and the base design record.
    Returns the info dict (caller adds module detail and writes __design.json)."""
    assert shape.isValid() and len(shape.Solids) == 1, (shape.isValid(), len(shape.Solids))
    out.mkdir(parents=True, exist_ok=True)
    shape.exportStep(str(out/f'{name}__installed.step'))
    files = [write(shape, out/f'{name}__installed.stl')]
    tag = 'print-right-cheek' if pose == 'right-cheek' else 'print-upright'
    pp, pm = pose_transform(shape, pose)
    pm = [pm.A11, pm.A12, pm.A13, pm.A14, pm.A21, pm.A22, pm.A23, pm.A24, pm.A31, pm.A32, pm.A33, pm.A34, 0, 0, 0, 1]
    pp.exportStep(str(out/f'{name}__{tag}.step'))
    files.append(write(pp, out/f'{name}__{tag}.stl'))
    info = dict(name=name, pose=pose, print_file=f'{name}__{tag}.stl', pose_matrix=pm,
                volume_mm3=shape.Volume, solid_mass_asa_g=shape.Volume/1000*ASA_G_PER_CM3,
                bounds_installed=[shape.BoundBox.XMin, shape.BoundBox.YMin, shape.BoundBox.ZMin,
                                  shape.BoundBox.XMax, shape.BoundBox.YMax, shape.BoundBox.ZMax],
                print_bounds=[round(v, 3) for v in (lambda b: (b.XLength, b.YLength, b.ZLength))(pp.optimalBoundingBox())], files=files)
    if extra:
        info.update(extra)
    return info


def save_design(out, name, info):
    (out/f'{name}__design.json').write_text(json.dumps(info, indent=1))
