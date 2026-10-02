"""Fast pre-print checks for v11: overhangs outside the pegs, tool/holder interference.

Run with cadpy: python quick_checks.py BUILD_DIR
"""
from pathlib import Path
import json
import sys

import numpy as np
import trimesh

NAME = 'part-solder-modules-tweezers__v11p1__edge-trays-right-cheek__fit-pf02c9-hoop5'


def main(d):
    holder = trimesh.load(d/f'{NAME}__installed.stl')
    pr = trimesh.load(d/f'{NAME}__print-right-cheek.stl')
    # print_pose: rotate -90 about Y, then shift to the origin; holder Y is print Y.
    y_shift = holder.bounds[0][1]
    peg_y = 0.15-y_shift                       # print y below this = pegs behind the board face
    n, c, a = pr.face_normals, pr.triangles_center, pr.area_faces
    down = (n[:, 2] < -0.7071) & (c[:, 2] > 0.3)          # steeper than 45 deg, not on the bed
    pegs = c[:, 1] < peg_y
    report = dict(overhang_area_pegs_mm2=float(a[down & pegs].sum()),
                  overhang_area_elsewhere_mm2=float(a[down & ~pegs].sum()))
    others = c[down & ~pegs]
    if len(others):
        report['overhang_elsewhere_bbox'] = [others.min(0).round(1).tolist(), others.max(0).round(1).tolist()]
        report['overhang_elsewhere_largest_faces'] = sorted(a[down & ~pegs].round(2).tolist())[-5:]
    # Tool vs holder (and glued wedges): sampled tool vertices inside either.
    solids = [holder]+[trimesh.load(d/f'{NAME}__wedge-{k}__installed.stl') for k in range(1, 5)]
    inside = []
    for k in range(1, 5):
        tool = trimesh.load(d/f'{NAME}__tool-{k}.stl')
        v = tool.vertices[::25]
        hits = sum(int(s.contains(v).sum()) for s in solids)
        inside.append(dict(tool=k, sampled=len(v), inside_holder_or_wedges=hits))
    report['tool_interference'] = inside
    print(json.dumps(report, indent=1))
    (d/'quick-checks.json').write_text(json.dumps(report, indent=1))


if __name__ == '__main__':
    main(Path(sys.argv[1]))
