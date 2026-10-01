"""Modelled peg supports for flat-top coupon prints (user request 2026-10-01).

Replaces slicer supports: PF04's 22-29 mm slim trees toppled. For each coupon
in print pose (flat top on the bed, pegs along -Y off the wall):

* lower peg + tail (the tall zone): a stable frame of two straight walls, one
  each side of the peg, standing on a shared floor slab; a deck bridges between
  them and its top hugs the peg underside with a one-layer Z gap;
* upper hook (at the bed): a low cradle from the bed under its overhangs.

Supports are separate shells: every surface keeps GAP_Z below and GAP_XY beside
the part (Boolean subtraction of shifted copies of the part). Run with
FreeCAD's Python: print_supports.py <set>, set in SETS.
"""
from pathlib import Path
import json, sys, hashlib
import FreeCAD as A, Part, Mesh, MeshPart
from peg_fit_ladder import box, print_pose, write_stl
V = A.Vector
GALLERY = Path(__file__).resolve().parents[2]/'docs/gallery'
SETS = {
    'pf05': ('fit-ladder-v5', 'part-pf05-peg-latch-grid__v1'),
    'pf04': ('fit-ladder-v4', 'part-pf04-peg-retention-concepts__v1'),
    'pf06': ('fit-ladder-v6', 'part-pf06-peg-latch-tune__v1'),
}
# Z gap is one 0.2 mm layer: a 0.1 gap rounds to zero at 0.2 layers and welds
# (checked: holder peg underside 8.275 -> deck layer 8.0-8.2, part from 8.2).
# User 2026-10-01: XY 0.25 (was 0.35), hug higher around the pegs (was 1.2).
GAP_Z, GAP_XY = 0.2, 0.25
import os
if os.environ.get('PEG_SUPPORT_GAP_Z'):
    # Only valid when the slice uses 0.1 mm layers in bands around every deck
    # top (print/slice_pf.py --bands); otherwise a sub-layer gap welds.
    GAP_Z = float(os.environ['PEG_SUPPORT_GAP_Z'])
WALL_T, DECK_T, SLAB_T = 2.0, 1.0, 0.6
HUG = 2.0                     # how far the deck top climbs the peg underside
LOWER_ZONE_Z = 15.0


def clearance(part):
    """Part plus copies shifted down and sideways: subtracting them leaves the gaps."""
    shifted = [part.copy() for _ in range(5)]
    for s, d in zip(shifted, [(0, 0, -GAP_Z), (GAP_XY, 0, 0), (-GAP_XY, 0, 0), (0, GAP_XY, 0), (0, -GAP_XY, 0)]):
        s.translate(V(*d))
    return [part]+shifted


def carve(solid, keep):
    """Subtract each clearance copy in turn; one multi-tool cut failed silently on PF06 #8."""
    for k in keep:
        solid = solid.cut(k)
    return solid.removeSplitter()


def supports(part):
    """Support solids for one coupon already in print pose."""
    b = part.BoundBox
    wall_y = min(f.BoundBox.YMin for f in part.Faces
                 if isinstance(f.Surface, Part.Plane) and abs(f.normalAt(0, 0).y+1) < 1e-6
                 and f.Area > 50)                      # the coupon's board-facing plane
    keep = clearance(part)
    out, info = [], {}
    # Lower peg and tail: frame + bridged deck.
    zone = part.common(box(b.XMin-1, b.YMin-1, LOWER_ZONE_Z, b.XLength+2, wall_y-GAP_XY-b.YMin+1, 60))
    zb = zone.BoundBox
    deck_top = zb.ZMin+HUG
    deck_bot = zb.ZMin-GAP_Z-DECK_T
    y0, y1 = zb.YMin-0.5, wall_y-GAP_XY
    xl, xr = zb.XMin-GAP_XY-WALL_T, zb.XMax+GAP_XY+WALL_T
    frame = [box(xl, y0, 0, xr-xl, y1-y0, SLAB_T),                       # floor slab ties both walls
             box(xl, y0, 0, WALL_T, y1-y0, deck_bot),
             box(xr-WALL_T, y0, 0, WALL_T, y1-y0, deck_bot),
             box(xl, y0, deck_bot, xr-xl, y1-y0, deck_top-deck_bot)]     # bridged deck + hug
    lower = carve(frame[0].multiFuse(frame[1:]), keep)
    out.append(lower)
    info['lower'] = dict(peg_underside_z_mm=zb.ZMin, deck_bottom_z_mm=deck_bot, bridge_span_mm=xr-xl-2*WALL_T,
                         walls_x_mm=[xl, xr], y_mm=[y0, y1])
    # Upper hook: cradle from the bed under overhangs below 3 mm.
    up = part.common(box(b.XMin-1, b.YMin-1, 0, b.XLength+2, wall_y-GAP_XY-b.YMin+1, LOWER_ZONE_Z-1)).BoundBox
    cradle = carve(box(up.XMin-1, up.YMin-0.5, 0, up.XLength+2, wall_y-GAP_XY-(up.YMin-0.5), 3.0), keep)
    if cradle.Volume > 1:
        out = [out[0].fuse(cradle).removeSplitter()]       # one support body, no overlapping shells
        info['upper_cradle_mm3'] = cradle.Volume
    for s in out:
        touch = s.common(part).Volume
        assert touch < 1e-6, f'support touches the part: {touch:.6f} mm3'
    info['min_gap_check'] = 'support solids do not intersect the part; Z gap %.2f, XY gap %.2f' % (GAP_Z, GAP_XY)
    return out, info


def peg_frames(part, wall_y, min_height=3.0):
    """One wall-and-deck frame under every separate peg behind wall_y (cheek prints).
    A thin fin may enter the bottom of a latch slot; it peels off with the deck."""
    b = part.BoundBox
    behind = part.common(box(b.XMin-1, b.YMin-1, b.ZMin-1, b.XLength+2, wall_y-GAP_XY-b.YMin+1, b.ZLength+2))
    keep = clearance(part)
    frames, info = [], []
    for peg in behind.Solids:
        zb = peg.BoundBox
        if zb.ZMin < min_height:
            continue
        deck_top, deck_bot = zb.ZMin+HUG, zb.ZMin-GAP_Z-DECK_T
        y0, y1 = zb.YMin-0.5, wall_y-GAP_XY
        xl, xr = zb.XMin-GAP_XY-WALL_T, zb.XMax+GAP_XY+WALL_T
        frames += [box(xl, y0, 0, xr-xl, y1-y0, SLAB_T), box(xl, y0, 0, WALL_T, y1-y0, deck_bot),
                   box(xr-WALL_T, y0, 0, WALL_T, y1-y0, deck_bot), box(xl, y0, deck_bot, xr-xl, y1-y0, deck_top-deck_bot)]
        info.append(dict(peg_underside_z_mm=zb.ZMin, bridge_span_mm=xr-xl-2*WALL_T, x_mm=[xl, xr]))
    sup = carve(frames[0].multiFuse(frames[1:]), keep)
    touch = sup.common(part).Volume
    assert touch < 1e-6, f'support touches the part: {touch:.6f} mm3'
    return sup, info


def main(which):
    folder, stem = SETS[which]
    out = GALLERY/folder
    cat = json.loads((out/f'{stem}__catalog.json').read_text())
    fit = cat['coupons'][0]['files'][0]['file'].split('fit-')[-1].removesuffix('.stl')
    parts, sups, report = [], [], []
    for i, c in enumerate(cat['coupons']):
        shape = Part.read(str(out/f"{stem}__coupon-{c['coupon']}__installed__fit-{fit}.step"))
        p = print_pose(shape)
        s, info = supports(p)
        d = V((i % 5)*28, (i//5)*30, 0)
        p.translate(d); parts.append(p)
        for x in s:
            x.translate(d); sups.append(x)
        report.append(dict(coupon=c['coupon'], **info))
        print(c['label'], round(info['lower']['peg_underside_z_mm'], 2), round(info['lower']['bridge_span_mm'], 2), flush=True)
    # Mesh every body on its own and merge: meshing the whole compound left an
    # open edge on PF06 although each body is a closed, valid solid.
    plate = Mesh.Mesh()
    for body in parts+sups:
        m = MeshPart.meshFromShape(Shape=body, LinearDeflection=.005, AngularDeflection=.087, Relative=False)
        for f in ['removeDuplicatedPoints', 'removeDuplicatedFacets', 'harmonizeNormals']:
            getattr(m, f)()
        assert m.isSolid() and not m.hasNonManifolds(), 'open body mesh'
        assert abs(abs(m.Volume)-body.Volume)/body.Volume < .003
        plate.addMesh(m)
    path = out/f'{stem}__all-{len(parts)}__print-flat-top-modelled-supports__fit-{fit}.stl'
    plate.write(str(path))
    result = dict(file=path.name, bodies=len(parts)+len(sups), facets=plate.CountFacets,
                  sha256=hashlib.sha256(path.read_bytes()).hexdigest(), each_body_closed=True)
    (out/f'{stem}__modelled-supports.json').write_text(json.dumps(dict(plate=result, coupons=report), indent=2)+'\n')


def mesh_bodies(bodies, path):
    plate = Mesh.Mesh()
    for body in bodies:
        for solid in body.Solids:
            m = MeshPart.meshFromShape(Shape=solid, LinearDeflection=.005, AngularDeflection=.087, Relative=False)
            for f in ['removeDuplicatedPoints', 'removeDuplicatedFacets', 'harmonizeNormals']:
                getattr(m, f)()
            assert m.isSolid() and not m.hasNonManifolds(), 'open body mesh'
            plate.addMesh(m)
    plate.write(str(path))
    return dict(file=path.name, facets=plate.CountFacets, sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def tweezer_plate(v9_dir, pf06_stl, out_stl):
    """v9 holder on its cheek with peg frames, beside the PF06 plate (with its supports)."""
    name = 'part-solder-modules-tweezers__v9__cheek-cradle__fit-pf02c9-latch'
    holder = Part.read(str(Path(v9_dir)/f'{name}__print-right-cheek.step'))
    wall_y = min(f.BoundBox.YMin for f in holder.Faces if isinstance(f.Surface, Part.Plane)
                 and abs(f.normalAt(0, 0).y+1) < 1e-6 and f.Area > 2000)    # receiver board face
    sup, info = peg_frames(holder, wall_y)
    holder.translate(V(5, 5, 0)); sup.translate(V(5, 5, 0))
    hb = holder.BoundBox
    pf = Mesh.Mesh(str(pf06_stl)); pb = pf.BoundBox
    pf.translate(5-pb.XMin, max(hb.YMax, sup.BoundBox.YMax)+12-pb.YMin, -pb.ZMin)
    m = Mesh.Mesh(); m.addMesh(pf)
    path = Path(out_stl)
    r = mesh_bodies([holder, sup], path.with_name(path.stem+'.holder-part.stl'))
    m.addMesh(Mesh.Mesh(str(path.with_name(path.stem+'.holder-part.stl'))))
    bb = m.BoundBox
    assert bb.XMin > 3 and bb.YMin > 3 and bb.XMax < 253 and bb.YMax < 253, (bb.XMax, bb.YMax)
    m.write(str(path))
    report = dict(plate=path.name, bounds_mm=[bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMax], holder_supports=info,
                  wall_y_print_mm=wall_y)
    path.with_suffix('.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report)[:600])


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'tweezer':
        tweezer_plate(*sys.argv[2:5])
    else:
        main(sys.argv[1] if len(sys.argv) > 1 else 'pf05')
