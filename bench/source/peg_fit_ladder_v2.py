"""PF02 upper-fit grid on a longer, ribbed lower locator.

PF01 feedback (2026-09-30): lower rungs +0.50 and +0.80 held well; the board
stands on 3/4 in shims, so the lower peg may run past the board; the top was a
hair loose (rocks away, wiggles sideways, lifts).

Every PF02 coupon has +0.65 lower ribs and a 4.8 mm tail running 7 mm past the
board's rear face (a sampled sweep of the baseline removal path cleared 8 mm).
The top varies on a 3x3 grid:
  S = diametral interference of two side ribs on the upper neck (0, .25, .50)
  C = tongue clamp interference on a 3.94 mm board (.19 current, .34, .49)
Coupon 0 is PF01 rung 7 (same lower ribs, stock length, current top) for
comparison. Run with FreeCAD's Python. Force and wear are unmeasured.
"""
from pathlib import Path
import argparse, hashlib, json, re
import FreeCAD as A, Part
import peg_profile as P
import peg_print_variant as PV
from peg_interface import receive_pegs
from peg_fit_ladder import box, label, print_pose, write_stl, RIB_BASE_X, RIB_ROOT_HALF, RIB_CREST_HALF
V = A.Vector
ROOT = P.ROOT
OUT = ROOT.parent/'docs/gallery/fit-ladder-v2'
FITS = ROOT/'reviews/pf02-fits'
NAME, VERSION = 'part-pf02-peg-fit-grid', 'v1'
PRINT_VARIANT = 'inverted-top-flat-v1'
BOARD = 3.94
LOWER_RIBS = 0.65
TAIL = dict(beyond_rear_mm=7.0, diameter_mm=4.8, raise_mm=0.4, chamfer_mm=0.8)
UPPER_RIBS = [0.0, 0.25, 0.50]
CLAMP_AT_BOARD = [0.19, 0.34, 0.49]
WIDTH, WALL, BELOW_LOWER = 20.0, 5.4, 7.0
LEAD_START_X, LEAD_LENGTH = 2.5, 1.5
UPPER_LEAD = 0.8   # upper neck land is only ~2.4 mm between face and bend


def coupons():
    out = [dict(coupon=0, label='PF01-7', upper_ribs_mm=0.0, clamp_mm=0.19, tail=False)]
    for s in UPPER_RIBS:
        for c in CLAMP_AT_BOARD:
            out.append(dict(coupon=len(out), label=f"S{s:.2f}C{c:.2f}".replace('0.', '.'),
                            upper_ribs_mm=s, clamp_mm=c, tail=True))
    return out


def fit_file(clamp):
    """Canonical fit bytes with only the pull clearance (clamp) changed."""
    raw = P.FIT_SOURCE.read_bytes().decode()
    cfg = P.parse(raw.encode())
    pull = round(-(clamp-(BOARD-cfg['PEG_BOARD_GRIP'])), 4)
    raw, n = re.subn(r'^PEG_PULL_CLEARANCE = [^;]+;', f'PEG_PULL_CLEARANCE = {pull};', raw, flags=re.M)
    assert n == 1
    raw = re.sub(r'^PEG_FIT_REVISION = "[^"]*";', f'PEG_FIT_REVISION = "pf02-clamp-{clamp:.2f}";', raw, flags=re.M)
    FITS.mkdir(parents=True, exist_ok=True)
    path = FITS/f'peg-fit-clamp-{clamp:.2f}.scad'
    path.write_text(raw, encoding='utf-8', newline='\n')
    return path


def side_ribs(zc, value, rear_y, front_y, lead=LEAD_LENGTH):
    """Two X-facing crush ribs about a hole centre at zc, leading end at rear_y."""
    crest = 6.35/2+value/2
    profile = [(RIB_BASE_X, zc-RIB_ROOT_HALF), (crest, zc-RIB_CREST_HALF),
               (crest, zc+RIB_CREST_HALF), (RIB_BASE_X, zc+RIB_ROOT_HALF)]
    shapes = []
    for sign in (1, -1):
        vs = [V(sign*x, rear_y, z) for x, z in profile]
        prism = Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(0, front_y-rear_y, 0))
        plan = [(0, rear_y), (LEAD_START_X, rear_y), (crest+.01, rear_y+lead),
                (crest+.01, front_y+1), (0, front_y+1)]
        ps = [V(sign*x, y, zc-5) for x, y in plan]
        shapes.append(prism.common(Part.Face(Part.makePolygon(ps+[ps[0]])).extrude(V(0, 0, 10))))
    return shapes, crest


def tail(zc, face):
    rear = face-BOARD
    r, ch, L = TAIL['diameter_mm']/2, TAIL['chamfer_mm'], TAIL['beyond_rear_mm']
    z = zc+TAIL['raise_mm']
    body = Part.makeCylinder(r, L-ch+1.2, V(0, rear-(L-ch), z), V(0, 1, 0))
    nose = Part.makeCone(r-ch, r, ch, V(0, rear-L, z), V(0, 1, 0))
    return [body, nose]


def width_at(shape, y, z):
    b = shape.common(box(-10, y-.005, z-.005, 20, .01, .01)).BoundBox
    return b.XMin, b.XMax


def coupon(entry, cfg):
    path = fit_file(entry['clamp_mm'])
    P.FIT_SOURCE = PV.FIT_SOURCE = path          # both modules reread this fit
    fit = P.parse(path.read_bytes())
    _, vinfo = PV.build(PRINT_VARIANT)
    top, face = vinfo['cut_plane_z_mm'], fit['PEG_FACE_Y']
    zu, zl = fit['PEG_SEAT_DROP'], fit['PEG_SEAT_DROP']-fit['PEG_PITCH']
    host = box(-WIDTH/2, face, zl-BELOW_LOWER, WIDTH, WALL, top-(zl-BELOW_LOWER))
    shape, report = receive_pegs(P.load_reference(), host, print_variant=PRINT_VARIANT)
    elbow = report['peg_profile']['elbow_center_y_mm']
    base = shape
    lower, crest_l = side_ribs(zl, entry.get('lower_ribs_mm', LOWER_RIBS), face-BOARD-0.5, face+1.0)
    add = list(lower)
    upper_rear = max(elbow, face-BOARD)+0.3
    crest_u = None
    if entry['upper_ribs_mm']:
        upper, crest_u = side_ribs(zu, entry['upper_ribs_mm'], upper_rear, face+1.0, lead=UPPER_LEAD)
        add += upper
    if entry['tail']:
        add += tail(zl, face)
    shape = shape.multiFuse(add).removeSplitter()
    y_front = face+WALL
    text = [label(str(entry['coupon']), 11, 0, top-8.5, y_front),
            label(entry['label'], 3.2, 0, zl+10.5, y_front)]
    shape = shape.multiFuse(text).removeSplitter()
    assert shape.isValid() and len(shape.Solids) == 1, entry
    assert base.multiFuse(text).removeSplitter().cut(shape).Volume < 1e-6, 'additions only'
    # Measure what was built, not what was asked for.
    lx = width_at(shape, face-2.0, zl)
    assert abs(lx[1]-crest_l) < 1e-4 and abs(-lx[0]-crest_l) < 1e-4, lx
    ux = width_at(shape, face-0.5, zu)
    if crest_u:
        assert abs(ux[1]-crest_u) < 1e-4 and abs(-ux[0]-crest_u) < 1e-4, ux
    else:
        assert ux[1] < 2.81, ux
    tip = shape.common(box(-3, -30, zl-4, 6, 30+face-BOARD, 8)).BoundBox.YMin if entry['tail'] else None
    if entry['tail']:
        assert abs(tip-(face-BOARD-TAIL['beyond_rear_mm'])) < 1e-4, tip
    return shape, dict(entry, fit_file=str(path.relative_to(ROOT)), fit_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                       pull_clearance_at_3p80_grip_mm=fit['PEG_PULL_CLEARANCE'],
                       predicted_clamp_interference_at_3p94_mm=-report['peg_profile']['predicted_clearance_at_3p94_board_mm'],
                       elbow_center_y_mm=elbow, upper_rib_rear_y_mm=upper_rear if crest_u else None,
                       measured_upper_width_mm=ux[1]-ux[0], measured_lower_width_mm=lx[1]-lx[0],
                       lower_tip_y_mm=tip, tail=TAIL if entry['tail'] else None,
                       host=dict(width=WIDTH, wall=WALL, top_z=top), print_variant=vinfo['print_variant'])


def main(output, entries=None, name=NAME, part='PF02 peg fit grid'):
    output.mkdir(parents=True, exist_ok=True)
    canonical = P.FIT_SOURCE
    cfg = P.parse(canonical.read_bytes())
    fit = hashlib.sha256(canonical.read_bytes()).hexdigest()[:10]
    catalog = dict(part=part, version=VERSION, base_fit_sha256=hashlib.sha256(canonical.read_bytes()).hexdigest(),
                   lower_ribs_diametral_mm=LOWER_RIBS, tail=TAIL, board_mm=BOARD,
                   scope='CAD geometry only. Ribs and clamp deliberately exceed the nominal board and bore. The 7 mm tail cleared a sampled sweep of the baseline removal path (no motion certificate). Force, wear and repeat use unmeasured.',
                   coupons=[])
    printed = []
    try:
        for i, entry in enumerate(entries or coupons()):
            shape, info = coupon(entry, cfg)
            stem = f"{name}__{VERSION}__coupon-{entry['coupon']}"
            info['files'] = [write_stl(shape, output/f'{stem}__installed__fit-{fit}.stl')]
            shape.exportStep(str(output/f'{stem}__installed__fit-{fit}.step'))
            catalog['coupons'].append(info)
            p = print_pose(shape); p.translate(V((i % 5)*(WIDTH+8), (i//5)*30, 0)); printed.append(p)
            print(entry['label'], round(info['measured_upper_width_mm'], 3), round(info['predicted_clamp_interference_at_3p94_mm'], 3), flush=True)
    finally:
        P.FIT_SOURCE = PV.FIT_SOURCE = canonical
    catalog['plate'] = write_stl(Part.makeCompound(printed), output/f'{name}__{VERSION}__all-{len(printed)}__print-flat-top__fit-{fit}.stl')
    (output/f'{name}__{VERSION}__catalog.json').write_text(json.dumps(catalog, indent=2)+'\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUT)
    main(parser.parse_args().output)
