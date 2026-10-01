"""Keep v9's receiver/pegs and build a compact, continuous right cheek.

Run with FreeCAD Python: python holder.py BUILD_DIR V9_INSTALLED_STEP
First run front.py with CadQuery. Regenerate v9 with its own unchanged source.
The exact v9 CAD behind Y=5.55 is retained, including PF02 #9 upper hooks,
the loose bearing rows and the rotated PF06-style bottom latches.
"""
from pathlib import Path
import hashlib
import json
import sys

import FreeCAD as A
import Part
import Mesh
import MeshPart

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from geometry import ENVELOPE

V = A.Vector
CHEEK_X, CHEEK_T = -24.4, 3.0
FIT_SHA = '9328ccc5d4bfd4ef7f5c88efb68cc4714da8b0017cd2c2d0a85e52ddc1669f3a'
BASELINE_SHA = '1eeac53c57cf450ca49767528618f02bf2da23386e01036c388ec1131728b213'
NAME = 'part-solder-modules-tweezers__v10__compact-right-cheek__fit-' + FIT_SHA[:10]


def box(x, y, z, w, d, h):
    return Part.makeBox(w, d, h, V(x, y, z))


def write_stl(shape, path):
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=.005,
                                 AngularDeflection=.087, Relative=False)
    for method in ['removeDuplicatedPoints', 'removeDuplicatedFacets', 'harmonizeNormals']:
        getattr(mesh, method)()
    mesh.write(str(path))
    read = Mesh.Mesh(str(path))
    assert read.isSolid() and not read.hasNonManifolds()
    error = abs(abs(read.Volume)-shape.Volume)/shape.Volume
    assert error < .003
    return dict(file=path.name, facets=read.CountFacets, closed=True,
                volume_error_fraction=error, sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def hull(points):
    pts = sorted(set((round(y, 6), round(z, 6)) for y, z in points))
    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    low, high = [], []
    for p in pts:
        while len(low) >= 2 and cross(low[-2], low[-1], p) <= 0:
            low.pop()
        low.append(p)
    for p in reversed(pts):
        while len(high) >= 2 and cross(high[-2], high[-1], p) <= 0:
            high.pop()
        high.append(p)
    return low[:-1] + high[:-1]


def print_pose(shape):
    s = shape.copy()
    s.rotate(V(), V(0, 1, 0), -90)
    b = s.BoundBox
    s.translate(V(-b.XMin, -b.YMin, -b.ZMin))
    return s


def main(out, baseline):
    assert hashlib.sha256(baseline.read_bytes()).hexdigest() == BASELINE_SHA, 'Use the exact v9 release STEP supplied with this bundle'
    source = Part.read(str(baseline))
    region = box(-100, -100, -300, 200, 105.55, 600)
    retained = source.common(region).removeSplitter()
    front = Part.read(str(out / 'front.step'))
    plate = box(-24.4, .15, -175, 48.8, 5.4, 180.12)
    # Leave a 0.5 mm border around the projected cradles. Their bottom faces
    # then overlap the cheek's interior rather than coinciding with its rim.
    outline = hull([(v.Y+dy, v.Z+dz) for s in [plate, front] for v in s.Vertexes
                    for dy in [-.5, .5] for dz in [-.5, .5]])
    verts = [V(CHEEK_X, y, z) for y, z in outline]
    cheek = Part.Face(Part.makePolygon(verts + [verts[0]])).extrude(V(CHEEK_T, 0, 0)).common(ENVELOPE)
    shape = retained.multiFuse([front, cheek]).removeSplitter()
    assert shape.isValid() and len(shape.Solids) == 1, (shape.isValid(), len(shape.Solids))
    # Compare the entire region behind the receiver face, plus the full plate.
    # New cheek material above the plate is allowed to change with the layout.
    fit_region = box(-100, -100, -300, 200, 100.15, 600).fuse(plate)
    old_fit, kept = source.common(fit_region), shape.common(fit_region)
    delta = old_fit.cut(kept).Volume + kept.cut(old_fit).Volume
    # The new right cheek meets the board receiver, preserving all fit surfaces.
    assert delta < 1e-6, delta
    new_host = shape.cut(retained)
    outside = new_host.cut(ENVELOPE).Volume
    assert outside < 1e-6, outside
    shape.exportStep(str(out / f'{NAME}__installed.step'))
    reread = Part.read(str(out / f'{NAME}__installed.step'))
    assert reread.isValid() and len(reread.Solids) == 1
    p = print_pose(shape)
    p.exportStep(str(out / f'{NAME}__print-right-cheek.step'))
    bed = [f for f in p.Faces if isinstance(f.Surface, Part.Plane)
           and abs(f.BoundBox.ZMin) < 1e-6 and abs(f.BoundBox.ZMax) < 1e-6]
    info = dict(
        baseline_v9_step_sha256=hashlib.sha256(baseline.read_bytes()).hexdigest(),
        fit_scalar_source_sha256=FIT_SHA, peg_variant='v9 PF02 #9 hooks / loose bearings / PF06-style latch',
        v9_receiver_and_peg_difference_mm3=delta,
        new_host_outside_allowed_volume_mm3=outside,
        cheek_side='negative-X, viewer right', cheek_thickness_mm=CHEEK_T,
        print_rotation_y_degrees=-90, bed_contact_area_mm2=sum(f.Area for f in bed),
        v9_volume_mm3=source.Volume, v10_volume_mm3=shape.Volume,
        cad_volume_reduction_fraction=1-shape.Volume/source.Volume,
        print_bounds_mm=[p.BoundBox.XLength, p.BoundBox.YLength, p.BoundBox.ZLength],
        installed_bounds_mm=[shape.BoundBox.XLength, shape.BoundBox.YLength, shape.BoundBox.ZLength],
        step_roundtrip_volume_difference_mm3=abs(reread.Volume-shape.Volume),
        valid_single_solid=True,
        files=[write_stl(shape, out / f'{NAME}__installed.stl'),
               write_stl(p, out / f'{NAME}__print-right-cheek.stl')],
        scope='CAD prototype. Unchanged v9 interfering peg fit; no inherited rigid peg motion, physical fit, strength or slicing qualification.',
        runtime=dict(freecad=A.Version()),
    )
    (out / f'{NAME}__design-and-checks.json').write_text(json.dumps(info, indent=2) + '\n')
    print(json.dumps(info), flush=True)


if __name__ == '__main__':
    main(Path(sys.argv[1]), Path(sys.argv[2]))
