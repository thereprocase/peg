"""Place the measured tips-down cradles next to the actual right (-X) cheek.

Run with the v8 CadQuery requirements: python front.py BUILD_DIR
The tool moves relative to the unchanged peg grid. A proper 180-degree roll
about its heel-to-point axis swaps its arms while keeping its points down.
The guide's width profile follows that rolled tool. Its existing floor reaches
the cheek; no broad blocks or additional lateral extensions are required.
"""
from pathlib import Path
import json
import sys

import cadquery as cq
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tweezers_v8'))
import holder as v8

CHEEK_X = -24.4
CHEEK_T = 3.0
HEELS = [np.array([-11.5, 93.0, 49.0 - 42.0 * i]) for i in range(4)]
TOOL_ROTATION = v8.R @ np.diag([-1.0, 1.0, -1.0])


def print_pose(shape):
    """Negative-X face on the bed, following the repository's right cheek rule."""
    s = shape.rotate((0, 0, 0), (0, 1, 0), -90)
    b = s.BoundingBox()
    return s.translate((-b.xmin, -b.ymin, -b.zmin))


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    assert abs(np.linalg.det(TOOL_ROTATION) - 1.0) < 1e-12
    guide = v8.cradle().mirror('YZ')
    front = cq.Compound.makeCompound([v8.installed(guide, heel) for heel in HEELS])
    assert front.isValid() and len(front.Solids()) == 4
    cq.exporters.export(front, str(out / 'front.step'))
    local_bed_wall = v8.box(-12.9, 5, -2, 3, 60, 12)
    coupon = guide.fuse(local_bed_wall).clean()
    assert coupon.isValid() and len(coupon.Solids()) == 1
    cq.exporters.export(coupon, str(out / 'single-throat-installed-local.step'))
    cq.exporters.export(print_pose(coupon), str(out / 'single-throat-print-right-cheek.step'))
    v8.mesh(print_pose(coupon)).export(out / 'single-throat-print-right-cheek.stl')
    v8.mesh(guide).export(out / 'cradle-local.stl')
    for i, heel in enumerate(HEELS):
        tool = v8.tool.make_mesh('open_rest')
        tool.vertices = tool.vertices @ TOOL_ROTATION.T + heel
        tool.export(out / f'reference-tool-{i + 1}.stl')
    floor_end = HEELS[0][0] - 12.3
    report = dict(
        cheek_side='Right when facing the installed holder: negative X',
        cheek_outer_x_mm=CHEEK_X, cheek_thickness_mm=CHEEK_T,
        heel_positions_xyz_mm=[h.tolist() for h in HEELS],
        tool_to_installed_rotation=TOOL_ROTATION.tolist(),
        points_down_axis_xyz=TOOL_ROTATION[:, 1].tolist(),
        floor_to_cheek_overlap_mm=(CHEEK_X + CHEEK_T) - floor_end,
        new_support_webs=0,
        throat_source='v8 contoured guide, width profile turned for the rolled tool',
        tool_motion='Lift 5 mm, then +X 30 mm (left when facing the board); reverse to insert',
    )
    (out / 'front.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main(Path(sys.argv[1]))
