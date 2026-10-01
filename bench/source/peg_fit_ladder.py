"""PF01 lower-locator fit ladder: ten single-column coupons, stock to tight.

The hooked mount's lower locator is 5.55 mm wide at hole-centre height in a
6.35 mm hole, so nothing resists the bottom of a holder swinging off the board.
Each rung adds two crush ribs at 3 and 9 o'clock. Insertion rotates the holder
about X, so lateral (X) interference does not fight the swing-in arc; it only
adds squeeze against the hole's side walls. Rung 0 is the unchanged stock mount.

Run with FreeCAD's Python. Upper hook, print variant and fit authority are the
current canonical ones; only the ribs vary. Force and wear are unmeasured.
"""
from pathlib import Path
import argparse, hashlib, json
import FreeCAD as A, Part, Mesh, MeshPart
import peg_profile as P
from peg_interface import receive_pegs
V = A.Vector
ROOT = P.ROOT
OUT = ROOT.parent/'docs/gallery/fit-ladder'
FONT = r'C:\Windows\Fonts\arialbd.ttf'
NAME = 'part-pf01-peg-fit-ladder'
VERSION = 'v1'
PRINT_VARIANT = 'inverted-top-flat-v1'

# Diametral interference across the ribs, mm; None = stock locator, no ribs.
RUNGS = [None, 0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.65, 0.80, 1.00]

WIDTH = 20.0          # coupon width across X
WALL = 5.4            # receiving wall, as the demonstrated holder receiver
BELOW_LOWER = 7.0     # plate below the lower hole centre
RIB_BASE_X = 2.2      # rib root, buried inside the locator core
RIB_ROOT_HALF = 1.6   # rib half-height at its root, about hole centre
RIB_CREST_HALF = 0.4  # flat crest half-height
LEAD_START_X = 2.5    # crest half-width at the locator tip
LEAD_LENGTH = 1.5     # axial ramp from tip to full crest
EMBOSS = 0.6


def box(x, y, z, w, d, h): return Part.makeBox(w, d, h, V(x, y, z))


def rungs():
    out = []
    for n, value in enumerate(RUNGS):
        label = 'STOCK' if value is None else ('0.00' if value == 0 else f'+{value:.2f}')
        out.append(dict(rung=n, diametral_interference_mm=value, label=label))
    return out


def ribs(cfg, value):
    """Two X-facing crush ribs on the lower locator, in anchor design coordinates."""
    R = cfg['PEG_HOLE_DIAMETER']/2
    zc = cfg['PEG_SEAT_DROP']-cfg['PEG_PITCH']        # lower hole centre when seated
    face = cfg['PEG_FACE_Y']
    tip = face-3.94-0.5                               # baseline locator: 3.94 board + 0.5 nose
    crest = R+value/2
    assert crest > LEAD_START_X and RIB_BASE_X < 2.3
    profile = [(RIB_BASE_X, zc-RIB_ROOT_HALF), (crest, zc-RIB_CREST_HALF),
               (crest, zc+RIB_CREST_HALF), (RIB_BASE_X, zc+RIB_ROOT_HALF)]
    front = face+1.0                                  # buried in the receiving wall
    shapes = []
    for sign in (1, -1):
        vs = [V(sign*x, tip, z) for x, z in profile]
        prism = Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(0, front-tip, 0))
        # Axial lead-in: crest ramps from LEAD_START_X at the tip to full height.
        plan = [(0, tip), (LEAD_START_X, tip), (crest+.01, tip+LEAD_LENGTH),
                (crest+.01, front+1), (0, front+1)]
        ps = [V(sign*x, y, zc-5) for x, y in plan]
        lead = Part.Face(Part.makePolygon(ps+[ps[0]])).extrude(V(0, 0, 10))
        shapes.append(prism.common(lead))
    return shapes, dict(crest_half_width_mm=crest, hole_centre_design_z_mm=zc,
                        tip_y_mm=tip, full_crest_from_y_mm=tip+LEAD_LENGTH,
                        crest_height_mm=2*RIB_CREST_HALF, root_height_mm=2*RIB_ROOT_HALF)


def label(text, size, x_centre, z_centre, y_face):
    """Raised text reading upright from the front (viewer's right is -X)."""
    wires = Part.makeWireString(text, FONT, size)
    faces = []
    for char in wires:
        if char:
            faces.append(Part.Face(char, 'Part::FaceMakerBullseye'))
    shape = Part.makeCompound(faces)
    b = shape.BoundBox
    shape.translate(V(-(b.XMin+b.XMax)/2, -(b.YMin+b.YMax)/2, 0))
    shape.rotate(V(), V(1, 0, 0), 90)      # text up -> +Z
    shape.rotate(V(), V(0, 0, 1), 180)     # text right -> -X
    solids = [f.extrude(V(0, EMBOSS+.3, 0)) for f in shape.Faces]
    text = solids[0].multiFuse(solids[1:]) if len(solids) > 1 else solids[0]
    text.translate(V(x_centre, y_face-.3, z_centre))
    return text


def coupon(entry, cfg):
    reference = P.load_reference()
    zc = cfg['PEG_SEAT_DROP']-cfg['PEG_PITCH']
    from peg_print_variant import build as variant_build
    _, vinfo = variant_build(PRINT_VARIANT)
    top = vinfo['cut_plane_z_mm']
    bottom = zc-BELOW_LOWER
    face = cfg['PEG_FACE_Y']
    host = box(-WIDTH/2, face, bottom, WIDTH, WALL, top-bottom)
    shape, report = receive_pegs(reference, host, print_variant=PRINT_VARIANT)
    stock = shape
    rib_info = None
    if entry['diametral_interference_mm'] is not None:
        rib_shapes, rib_info = ribs(cfg, entry['diametral_interference_mm'])
        shape = shape.multiFuse(rib_shapes).removeSplitter()
    y_front = face+WALL
    text = [label(str(entry['rung']), 11, 0, top-8.5, y_front),
            label(entry['label'], 3.6, 0, zc+10.5, y_front)]
    shape = shape.multiFuse(text).removeSplitter()
    stock_labelled = stock.multiFuse(text).removeSplitter()
    assert shape.isValid() and len(shape.Solids) == 1, entry
    added = shape.cut(stock_labelled).Volume
    removed = stock_labelled.cut(shape).Volume
    assert removed < 1e-6, 'ribs may only add material'
    if rib_info is None:
        assert added < 1e-6
    measured = None
    if rib_info:
        probe = shape.common(box(-10, face-2.0, zc-.005, 20, .01, .01)).BoundBox
        measured = dict(xmin=probe.XMin, xmax=probe.XMax)
        want = rib_info['crest_half_width_mm']
        assert abs(probe.XMax-want) < 1e-4 and abs(-probe.XMin-want) < 1e-4, (probe, want)
        rib_info['measured_width_across_ribs_mm'] = probe.XMax-probe.XMin
    else:
        probe = shape.common(box(-10, face-2.0, zc-.005, 20, .01, .01)).BoundBox
        measured = dict(xmin=probe.XMin, xmax=probe.XMax)
    wires = [w for w in shape.slice(V(0, 1, 0), face-2.0) if w.BoundBox.ZMax < zc+5]
    assert len(wires) == 1 and wires[0].isClosed()
    section = [[round(p.x, 4), round(p.z-zc, 4)] for p in wires[0].discretize(Deflection=.005)]
    return shape, dict(entry, ribs=rib_info, locator_section_xz_about_hole_centre_at_y_minus_1p85=section, rib_volume_mm3=added,
                       locator_width_at_hole_centre_mm=measured['xmax']-measured['xmin'],
                       hole_diameter_mm=cfg['PEG_HOLE_DIAMETER'],
                       side_gap_each_mm=(cfg['PEG_HOLE_DIAMETER']-(measured['xmax']-measured['xmin']))/2,
                       host=dict(width=WIDTH, wall=WALL, top_z=top, bottom_z=bottom),
                       peg_profile=report['peg_profile'])


def print_pose(shape):
    """Flat top on the bed, as the inverted-top-flat print variant intends."""
    s = shape.copy()
    s.rotate(V(), V(0, 1, 0), 180)
    b = s.BoundBox
    s.translate(V(-b.XMin, -b.YMin, -b.ZMin))
    return s


def write_stl(shape, path):
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=.005, AngularDeflection=.087, Relative=False)
    for method in ['removeDuplicatedPoints', 'removeDuplicatedFacets', 'harmonizeNormals']:
        getattr(mesh, method)()
    mesh.write(str(path))
    mesh = Mesh.Mesh(str(path))
    assert mesh.isSolid() and not mesh.hasNonManifolds(), f'Open mesh {path}'
    error = abs(abs(mesh.Volume)-shape.Volume)/shape.Volume
    assert error < .003, (path, error)
    return dict(file=path.name, facets=mesh.CountFacets, closed=True, volume_error_fraction=error,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main(output):
    output.mkdir(parents=True, exist_ok=True)
    raw = P.FIT_SOURCE.read_bytes()
    cfg = P.parse(raw)
    fit = hashlib.sha256(raw).hexdigest()[:10]
    catalog = dict(part='PF01 peg fit ladder', version=VERSION, fit_sha256=hashlib.sha256(raw).hexdigest(),
                   print_variant=PRINT_VARIANT, source='bench/source/peg_fit_ladder.py',
                   varied='Lower-locator diametral interference across two X-facing crush ribs at hole-centre height',
                   fixed='Upper hook, tongue clamp, locator core and print variant are the current canonical fit',
                   scope='CAD geometry only. Ribs deliberately exceed the nominal bore; the baseline motion certificate does not cover them. Retention force, board wear and repeated-use behaviour are unmeasured.',
                   coupons=[])
    installed, printed = [], []
    for i, entry in enumerate(rungs()):
        shape, info = coupon(entry, cfg)
        stem = f"{NAME}__{VERSION}__rung-{entry['rung']}"
        info['files'] = [write_stl(shape, output/f'{stem}__installed__fit-{fit}.stl'),
                         write_stl(print_pose(shape), output/f'{stem}__print-flat-top__fit-{fit}.stl')]
        catalog['coupons'].append(info)
        s = shape.copy(); s.translate(V(-(WIDTH+5.4)*i, 0, 0)); installed.append(s)
        p = print_pose(shape); p.translate(V((i % 5)*(WIDTH+8), (i//5)*24, 0)); printed.append(p)
        print(entry['label'], round(info['locator_width_at_hole_centre_mm'], 4), flush=True)
    lineup = Part.makeCompound(installed)
    plate = Part.makeCompound(printed)
    lineup.exportStep(str(output/f'{NAME}__{VERSION}__lineup-installed.step'))
    catalog['lineup'] = [write_stl(lineup, output/f'{NAME}__{VERSION}__all-10__installed__fit-{fit}.stl'),
                         write_stl(plate, output/f'{NAME}__{VERSION}__all-10__print-flat-top__fit-{fit}.stl')]
    (output/f'{NAME}__{VERSION}__catalog.json').write_text(json.dumps(catalog, indent=2)+'\n', encoding='utf-8', newline='\n')
    return catalog


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUT)
    main(parser.parse_args().output)
