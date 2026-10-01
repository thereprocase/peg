"""BX01: open-top box two peg columns wide that tiles on a 50.8 mm grid.

Outside 50.2 x 50.2 mm face (0.30 mm relief per edge, as geometry.integrate:
0.60 mm between tiled neighbours, horizontally and vertically). Installation
tilts only in the Y-Z plane, so side neighbours never obstruct it.

Peg fit is provisional until PF03 picks the lower ribs: PF02 coupon 9's top
(upper side ribs +0.50, clamp 0.49 on a 3.94 board) with +0.80 lower ribs and
the 7 mm lower tail. Printed top-down (inverted-top-flat) like the coupons, so
bearing faces print clean; the floor is supported inside the box.
Run with FreeCAD's Python.
"""
from pathlib import Path
import argparse, hashlib, json
import FreeCAD as A, Part
import peg_profile as P
import peg_print_variant as PV
import peg_fit_ladder_v2 as G
from peg_fit_ladder import box, label, print_pose, write_stl
from peg_interface import receive_pegs
V = A.Vector
ROOT = P.ROOT
OUT = ROOT.parent/'docs/gallery/box-2w'
NAME, VERSION = 'part-bx01-box-2w', 'v1'
GRID, RELIEF = 50.8, 0.30
DEPTH = 50.0          # outside, from the board face
WALL, FLOOR, BACK = 2.0, 2.4, 5.4
COLUMNS = [-12.7, 12.7]
FIT = dict(upper_ribs_mm=0.50, clamp_mm=0.49, lower_ribs_mm=0.80)


def build():
    path = G.fit_file(FIT['clamp_mm'])
    canonical = P.FIT_SOURCE
    P.FIT_SOURCE = PV.FIT_SOURCE = path
    try:
        fit = P.parse(path.read_bytes())
        _, vinfo = PV.build(G.PRINT_VARIANT)
        top, face = vinfo['cut_plane_z_mm'], fit['PEG_FACE_Y']
        zu, zl = fit['PEG_SEAT_DROP'], fit['PEG_SEAT_DROP']-fit['PEG_PITCH']
        w = GRID-2*RELIEF
        h = GRID-2*RELIEF
        bottom = top-h
        x0, y0 = -w/2, face
        outer = box(x0, y0, bottom, w, DEPTH, h)
        inner = box(x0+WALL, y0+BACK, bottom+FLOOR, w-2*WALL, DEPTH-BACK-WALL, h)
        host = outer.cut(inner)
        from geometry import ENVELOPE
        outside = host.cut(ENVELOPE).Volume
        assert outside < 1e-6, f'host outside allowed volume: {outside} mm3'
        shape, reports = host, []
        for x in COLUMNS:
            ref = P.load_reference(); ref.translate(V(x, 0, 0))
            shape, r = receive_pegs(ref, shape, print_variant=G.PRINT_VARIANT)
            reports.append(r)
        elbow = reports[0]['peg_profile']['elbow_center_y_mm']
        add = []
        for x in COLUMNS:
            parts = (G.side_ribs(zl, FIT['lower_ribs_mm'], face-G.BOARD-0.5, face+1.0)[0]
                     + G.side_ribs(zu, FIT['upper_ribs_mm'], max(elbow, face-G.BOARD)+0.3, face+1.0, lead=G.UPPER_LEAD)[0]
                     + G.tail(zl, face))
            for s in parts:
                s.translate(V(x, 0, 0)); add.append(s)
        shape = shape.multiFuse(add).removeSplitter()
        tag = label('BX01 L.80', 4.0, 0, bottom+h/2, face+DEPTH)
        shape = shape.multiFuse([tag]).removeSplitter()
        assert shape.isValid() and len(shape.Solids) == 1
        # Tiling: nothing but pegs may cross the 50.8 cell; host stays inside it.
        hb = host.BoundBox
        assert abs(hb.XLength-(GRID-2*RELIEF)) < 1e-6 and abs(hb.ZLength-(GRID-2*RELIEF)) < 1e-6
        sb = shape.BoundBox
        assert sb.XMax <= GRID/2-RELIEF+1e-6 and sb.XMin >= -GRID/2+RELIEF-1e-6
        # Built fit, measured per column.
        widths = {}
        for x in COLUMNS:
            lo = shape.common(box(x-10, face-2.005, zl-.005, 20, .01, .01)).BoundBox
            up = shape.common(box(x-10, face-.505, zu-.005, 20, .01, .01)).BoundBox
            widths[x] = dict(lower=lo.XLength, upper=up.XLength)
            assert abs(lo.XLength-(6.35+FIT['lower_ribs_mm'])) < 1e-4, (x, lo.XLength)
            assert abs(up.XLength-(6.35+FIT['upper_ribs_mm'])) < 1e-4, (x, up.XLength)
        info = dict(part='BX01 two-column tiling box', version=VERSION, fit=FIT,
                    fit_file=str(path.relative_to(ROOT)), fit_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                    outside_mm=dict(width=w, height=h, depth_from_board=DEPTH), grid_mm=GRID,
                    walls_mm=dict(side=WALL, floor=FLOOR, back=BACK), columns_x_mm=COLUMNS,
                    top_z_mm=top, bottom_z_mm=bottom, host_outside_envelope_mm3=outside,
                    capacity_ml=inner.common(outer).Volume/1000, measured_widths_mm=widths,
                    predicted_clamp_interference_at_3p94_mm=-reports[0]['peg_profile']['predicted_clearance_at_3p94_board_mm'],
                    scope='CAD geometry; provisional fit pending PF03. Load, print and fit untested.')
        return shape, info
    finally:
        P.FIT_SOURCE = PV.FIT_SOURCE = canonical


def main(output):
    output.mkdir(parents=True, exist_ok=True)
    fit = hashlib.sha256(P.FIT_SOURCE.read_bytes()).hexdigest()[:10]
    shape, info = build()
    stem = f'{NAME}__{VERSION}'
    shape.exportStep(str(output/f'{stem}__installed__fit-{fit}.step'))
    info['files'] = [write_stl(shape, output/f'{stem}__installed__fit-{fit}.stl'),
                     write_stl(print_pose(shape), output/f'{stem}__print-flat-top__fit-{fit}.stl')]
    (output/f'{stem}__spec.json').write_text(json.dumps(info, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: info[k] for k in ['outside_mm', 'capacity_ml', 'measured_widths_mm', 'host_outside_envelope_mm3']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUT)
    main(parser.parse_args().output)
