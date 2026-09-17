"""Small single-repair magnetic screw dish (part swd01): a loose hand-carry tray
nested in a peg-mounted cradle.

Cradle: canonical peg fit, flush back plate ending just below the lower peg
locators, a shelf with a shallow recess that locates the tray on four sides,
and a thin diagonal brace from the shelf front back to the plate. The cradle is
an X-extrusion apart from the pegs and recess, so it prints on its RIGHT CHEEK
(negative-X face on the bed, the project's preferred construction): every wall
is vertical, no foot, no overhang constraint on the brace. Peg tongues take the
accepted local support and need review in the emitted paths.

Tray: 60 x 40 x 12 mm, flat bottom on the bed. Two 20 x 10 x 3 mm block magnets
in pockets open to the underside with removal clearance (prototype retention is
tape). Thumb scallop in the FRONT (+Y) wall. No holes through the floor.

File names follow the repo pattern part-<id>-<name>__v1__<part>__<pose>[__fit-<hash>];
the fit hash is carried only by the peg-bearing cradle.

Run with FreeCAD's python:
  "C:/Program Files/FreeCAD 1.1/bin/python.exe" screw_tray_magnetic.py --out <dir>
"""
import argparse, json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "source"))

import FreeCAD as A  # noqa: E402
import Part  # noqa: E402
from geometry import box, cyl, union, cut, prism_yz, translated, export_mesh, ENVELOPE  # noqa: E402
from peg_interface import receive_pegs  # noqa: E402
from peg_profile import load_reference, parameters  # noqa: E402

V = A.Vector
BACK = 0.15
T = 5.4
TOP = 5.12
PART_ID = "swd01"
PART_NAME = "screw-dish-magnetic"

# Tray
TRAY_X, TRAY_Y, TRAY_H = 60.0, 40.0, 12.0
WALL = 1.8
FLOOR_OVER_MAGNET = 1.2
MAG_L, MAG_W, MAG_T = 20.0, 10.0, 3.0          # owned block magnets
POCKET_L, POCKET_W, POCKET_H = 20.4, 10.4, 3.2  # removal clearance, not a press fit
FLOOR = FLOOR_OVER_MAGNET + POCKET_H            # 4.4
MAG_XY = [(-14.0, 0.0), (14.0, 0.0)]            # long axis along X
SCALLOP_W, SCALLOP_D = 16.0, 3.0                # thumb lift in the +Y (front) wall; 4.6 mm wall stays above the floor

# Cradle
CELLS = 3
SHELF_TOP = -6.0        # installed z of the shelf's top face (recess rim)
RECESS = 1.5            # tray sits this deep in the shelf; recess walls locate it on four sides
SHELF_T = 4.0           # shelf thickness under the recess floor
CLEAR = 1.0             # tray-to-recess clearance per side
FRONT_WALL = 2.4        # recess front wall = the lip
BRACE_T = 4.0
PLATE_BELOW_LOCATOR = 3.0
LIFT_FOR_RENDER = 30.0


def width(cells):
    return cells * 25.4 - 2


def mounts(cells):
    if cells <= 2:
        return [(-cells / 2 + 0.5 + i) * 25.4 for i in range(cells)]
    return [(-cells / 2 + 0.5) * 25.4, (cells / 2 - 0.5) * 25.4]


def back(cells, bottom):
    return box(-width(cells) / 2, BACK, bottom, width(cells), T, TOP - bottom)


def mounted(host, cells):
    host = host.common(ENVELOPE).removeSplitter()
    result = host
    reports = []
    for x in mounts(cells):
        result, r = receive_pegs(translated(load_reference(), x=x), result)
        r["profile"] = parameters()["variant"]
        reports.append(r)
    return result, reports


def pose_flat(s):
    q = s.copy()
    b = q.BoundBox
    q.translate(V(-(b.XMin + b.XMax) / 2, -(b.YMin + b.YMax) / 2, -b.ZMin))
    return q


def pose_right_cheek(s):
    # Same construction as solder_modules.print_pose(s, 'right-cheek'): negative-X face on the bed.
    q = s.copy()
    q.rotate(V(), V(0, 1, 0), -90)
    b = q.BoundBox
    q.translate(V(-(b.XMin + b.XMax) / 2, -(b.YMin + b.YMax) / 2, -b.ZMin))
    return q


def tray():
    outer = box(-TRAY_X / 2, -TRAY_Y / 2, 0, TRAY_X, TRAY_Y, TRAY_H)
    cavity = box(-TRAY_X / 2 + WALL, -TRAY_Y / 2 + WALL, FLOOR, TRAY_X - 2 * WALL, TRAY_Y - 2 * WALL, TRAY_H)
    holes = [cavity]
    for (x, y) in MAG_XY:
        holes.append(box(x - POCKET_L / 2, y - POCKET_W / 2, -0.01, POCKET_L, POCKET_W, POCKET_H + 0.01))
    # Thumb scallop through the FRONT wall (+Y, away from the board): a horizontal
    # cylinder along Y whose centre sits above the wall top so it dips SCALLOP_D.
    r = (SCALLOP_W ** 2 / 4 + SCALLOP_D ** 2) / (2 * SCALLOP_D)
    holes.append(cyl(0, TRAY_Y / 2 - WALL - 1.0, TRAY_H + (r - SCALLOP_D), r, WALL + 2.0, axis=(0, 1, 0)))
    return cut(outer, holes)


def cradle():
    w = width(CELLS)
    ref_zmin = load_reference().BoundBox.ZMin
    bottom = math.floor(ref_zmin - PLATE_BELOW_LOCATOR)     # just below the lower locators
    recess_x = TRAY_X + 2 * CLEAR
    recess_y = TRAY_Y + 2 * CLEAR
    shelf_d = T + CLEAR + TRAY_Y + CLEAR + FRONT_WALL         # from BACK forward
    front = BACK + shelf_d
    shelf_bottom = SHELF_TOP - RECESS - SHELF_T
    plate = back(CELLS, bottom)
    shelf = box(-w / 2, BACK, shelf_bottom, w, shelf_d, RECESS + SHELF_T)
    recess = box(-recess_x / 2, BACK + T, SHELF_TOP - RECESS, recess_x, recess_y, RECESS + 1.0)
    # Diagonal brace: a slab from the shelf's front underside back to the plate at the bottom.
    # Overlap 1 mm into the shelf and into the plate so the union is one manifold solid.
    y0, z0 = front - BRACE_T, shelf_bottom + 1.0
    y1, z1 = BACK + 1.0, bottom + 2.0
    brace = prism_yz(-w / 2, w, [(y1, z1), (y1, z1 + BRACE_T / math.cos(math.atan2(z0 - z1, y0 - y1))),
                                 (y0 + BRACE_T, z0), (y0, z0)])
    host = cut(union([plate, shelf, brace]), [recess])
    shape, reports = mounted(host, CELLS)
    solid = shape.Solids[0] if shape.Solids else shape
    brace_deg = math.degrees(math.atan2(z0 - z1, y0 - y1))
    spec = dict(cells=CELLS, width_mm=w, plate_bottom_mm=bottom, peg_reference_zmin_mm=round(ref_zmin, 3),
                installed_height_mm=TOP - bottom, shelf_top_z_mm=SHELF_TOP, shelf_depth_mm=shelf_d,
                recess_mm=[recess_x, recess_y, RECESS], tray_clearance_per_side_mm=CLEAR,
                front_wall_mm=FRONT_WALL, brace_thickness_mm=BRACE_T, brace_angle_deg=round(brace_deg, 1),
                mount_columns_x_mm=mounts(CELLS), volume_cm3=round(solid.Volume / 1000, 2),
                peg_reports=reports)
    return shape, spec


def export(shape, path):
    path = Path(path)
    shape.exportStep(str(path.with_suffix(".step")))
    reread = Part.read(str(path.with_suffix(".step")))
    assert reread.isValid() and len(reread.Solids) == 1, f"{path.name}: STEP round-trip is not one valid solid"
    mesh, report = export_mesh(shape, path.with_suffix(".stl"))
    assert mesh.isSolid() and mesh.countComponents() == 1, f"{path.name}: mesh is not one closed solid"
    return report


def bed_contact_mm2(shape, tol=0.05):
    """Area of faces lying on z = 0 in the given pose."""
    total = 0.0
    for f in shape.Faces:
        bb = f.BoundBox
        if abs(bb.ZMin) < tol and abs(bb.ZMax) < tol:
            total += f.Area
    return round(total, 1)


def render_shapes(shapes, png_path, title, elev=25, azim=-60):
    """Raw triangle render (tessellated at 0.4 mm). Honest, not pretty."""
    try:
        import numpy as np
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        fig = plt.figure(figsize=(6.5, 5.5))
        ax = fig.add_subplot(111, projection="3d")
        allpts = []
        for shape, color in shapes:
            verts, faces = shape.tessellate(0.4)
            pts = np.array([[v.x, v.y, v.z] for v in verts])
            allpts.append(pts)
            ax.add_collection3d(Poly3DCollection(pts[np.array(faces)], facecolor=color, edgecolor="#123", linewidth=0.05, alpha=0.95))
        pts = np.vstack(allpts)
        mn, mx = pts.min(0), pts.max(0)
        c = (mn + mx) / 2
        r = (mx - mn).max() / 2
        ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r); ax.set_zlim(c[2] - r, c[2] + r)
        ax.set_title(title); ax.view_init(elev=elev, azim=azim)
        fig.savefig(png_path, dpi=110)
        plt.close(fig)
        return True
    except Exception as e:  # noqa: BLE001
        print("render skipped:", e)
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    pp = parameters()
    fit = "__fit-" + pp["config_sha256"][:10]
    P = f"part-{PART_ID}-{PART_NAME}__v1__"
    catalog = {"id": PART_ID.upper(), "part": "small single-repair magnetic screw dish, 60 x 40", "version": 1,
               "magnets": dict(count=2, size_mm=[MAG_L, MAG_W, MAG_T], pocket_mm=[POCKET_L, POCKET_W, POCKET_H],
                               floor_over_magnet_mm=FLOOR_OVER_MAGNET, positions_xy_mm=MAG_XY,
                               retention="pockets open to the underside with removal clearance; prototype "
                                         "retention is tape across the underside; lid or latch left to hands-on feedback"),
               "peg_profile": pp, "files": {}}
    # Tray
    t = tray()
    tp = pose_flat(t)
    catalog["files"]["tray_installed"] = P + "tray__installed"
    catalog["files"]["tray_print"] = P + "tray__print-flat"
    catalog["tray"] = dict(outer_mm=[TRAY_X, TRAY_Y, TRAY_H], wall_mm=WALL, floor_mm=FLOOR,
                           thumb_scallop_mm=[SCALLOP_W, SCALLOP_D], scallop_wall="front (+Y, away from the board)",
                           retaining_wall_above_floor_at_scallop_mm=TRAY_H - SCALLOP_D - FLOOR,
                           volume_cm3=round(t.Volume / 1000, 2),
                           installed=export(t, out / catalog["files"]["tray_installed"]),
                           print_flat=export(tp, out / catalog["files"]["tray_print"]),
                           print_bounds_mm=[tp.BoundBox.XLength, tp.BoundBox.YLength, tp.BoundBox.ZLength],
                           print_bed_contact_mm2=bed_contact_mm2(tp),
                           print_pose="flat bottom on bed; the two 10.4 mm pocket roofs at z = 3.2 mm are expected bridges, not a certified no-support result")
    # Cradle
    c, cspec = cradle()
    cp = pose_right_cheek(c)
    catalog["files"]["cradle_installed"] = P + "cradle__installed" + fit
    catalog["files"]["cradle_print"] = P + "cradle__print-right-cheek" + fit
    cspec["installed"] = export(c, out / catalog["files"]["cradle_installed"])
    cspec["print_right_cheek"] = export(cp, out / catalog["files"]["cradle_print"])
    cspec["print_bounds_mm"] = [cp.BoundBox.XLength, cp.BoundBox.YLength, cp.BoundBox.ZLength]
    cspec["print_bed_contact_mm2"] = bed_contact_mm2(cp)
    cspec["print_pose"] = ("right cheek: negative-X face on the bed; plate, shelf and brace are vertical walls; "
                           "the recess walls are 1.5 mm ledges; peg tongues lie in the layer plane and take the "
                           "accepted local support, to be reviewed in the emitted paths")
    catalog["cradle"] = cspec
    # Assembly reference and removal render
    seat_offset = V(0, BACK + T + CLEAR + TRAY_Y / 2, SHELF_TOP - RECESS)
    seated = t.copy(); seated.translate(seat_offset)
    lifted = t.copy(); lifted.translate(seat_offset + V(0, 0, LIFT_FOR_RENDER))
    catalog["assembly"] = dict(tray_offset_mm=[seat_offset.x, seat_offset.y, seat_offset.z],
                               interference_mm3=round(c.common(seated).Volume, 4),
                               tray_wall_above_recess_rim_mm=TRAY_H - RECESS,
                               scallop_faces="+Y, away from the board")
    catalog["files"]["assembly_reference"] = P + "assembly-reference__installed" + fit
    Part.makeCompound([c, seated]).exportStep(str(out / (catalog["files"]["assembly_reference"] + ".step")))
    R = {"cradle_print_a": P + "cradle__print-right-cheek__render-a.png",
         "cradle_print_b": P + "cradle__print-right-cheek__render-b.png",
         "tray_print": P + "tray__print-flat__render.png",
         "assembly_seated": P + "assembly__installed__render-seated.png",
         "assembly_lifted": P + "assembly__installed__render-lifted.png"}
    catalog["files"]["renders"] = R
    catalog["renders_ok"] = dict(
        cradle_print_a=render_shapes([(cp, "#3a8f8a")], out / R["cradle_print_a"], "cradle, right-cheek print pose", 25, -55),
        cradle_print_b=render_shapes([(cp, "#3a8f8a")], out / R["cradle_print_b"], "cradle, right-cheek print pose, other side", 25, 125),
        tray_print=render_shapes([(tp, "#c98a3a")], out / R["tray_print"], "tray, flat-bottom print pose", 30, -120),
        assembly_seated=render_shapes([(c, "#3a8f8a"), (seated, "#c98a3a")], out / R["assembly_seated"], "installed: tray seated in cradle (board at low Y)", 22, 125),
        assembly_lifted=render_shapes([(c, "#3a8f8a"), (lifted, "#c98a3a")], out / R["assembly_lifted"], f"installed: tray lifted {LIFT_FOR_RENDER:.0f} mm for removal", 22, 125))
    catalog["qualification"] = ("Geometric construction only; not sliced, not physically print-qualified; no print-time "
                                "or mass estimate is claimed. Magnet pockets have removal clearance and no designed "
                                "retention: tape the underside for the prototype. Bed-contact areas are exact planar "
                                "face areas at z = 0 in each print pose.")
    (out / (P + "catalog.json")).write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    slim = {k: v for k, v in catalog.items() if k != "peg_profile"}
    slim["cradle"] = {k: v for k, v in slim["cradle"].items() if k != "peg_reports"}
    print(json.dumps(slim, indent=2))


if __name__ == "__main__":
    main()
