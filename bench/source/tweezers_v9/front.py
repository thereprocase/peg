"""v9 front body: v8's exact tool cradles, floors and webs carried to the right cheek.

v8 (12e4d15) printed on its right cheek touched the bed only along the receiver
plate's edge. v9 keeps every tool-facing surface of v8's cradle (floor under the
lower arm, both guide rails, all clearances, heel positions, 40 deg tilt and the
lift-then-left departure) and only lengthens each cradle floor and right-side web
in +X, away from the tool and its exit path, so they meet a flat cheek at
X = +24.4 mm. Run with the v8 CadQuery environment (cadpy):
  cadpy front.py <output-dir>
"""
from pathlib import Path
import sys, json
import numpy as np
import cadquery as cq
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tweezers_v8'))
import holder as v8          # noqa: E402  (v8 source, unchanged)

CHEEK_X = 24.4


def cradle_to_cheek(side_clearance=.08):
    """v8.cradle() with only the floor's +X end moved from 12.3 to the cheek."""
    floors, left, right = [], [], []
    for y in np.unique(np.r_[np.arange(6, 65, 2), 14, 16, 20, 28, 36, 38, 42, 50, 55, 60, 61, 64]):
        c, w, h, top, cl = v8.values(float(y), side_clearance)
        xl, xr = c-w/2-cl, c+w/2+cl
        bottom = h+.35+v8.T
        floors.append(v8.wire(y, [(xl-v8.T, h+.35), (CHEEK_X, h+.35), (CHEEK_X, bottom), (xl-v8.T, bottom)]))
        left.append(v8.wire(y, v8.rail_outline(xl-v8.T, xl, top, bottom)))
        right.append(v8.wire(y, v8.rail_outline(xr, xr+v8.T, top, bottom)))
    result = v8.loft(floors).fuse(v8.loft(left), v8.loft(right)).clean()
    assert result.isValid() and len(result.Solids()) == 1
    return result


def web_to_cheek(heel):
    """v8.web() widened from X 0.5..2.9 to X 0.5..24.4."""
    y0, z0 = heel[1], heel[2]
    return v8.prism_yz(.5, CHEEK_X-.5, [(5.15, z0-63), (5.15, min(z0-10, 4.5)), (y0+2, z0-3), (y0-37, z0-56)])


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    old_cradle, new_cradle = v8.cradle(), cradle_to_cheek()
    # Tool-side proof: the new cradle equals v8's wherever X <= 12.3 (v8's floor end).
    keep = v8.box(-60, -60, -60, 72.3, 200, 200)
    a, b = old_cradle.intersect(keep), new_cradle.intersect(keep)
    delta = a.cut(b).Volume()+b.cut(a).Volume()
    assert delta < 1e-6, delta
    front = None
    for heel in v8.HEELS:
        part = v8.installed(new_cradle, heel).fuse(web_to_cheek(heel))
        front = part if front is None else front.fuse(part)
    front = front.clean()
    assert front.isValid()
    cq.exporters.export(front, str(out/'front-to-cheek.step'))
    report = dict(source='bench/source/tweezers_v8/holder.py (12e4d15), unchanged', cheek_x_mm=CHEEK_X,
                  cradle_difference_mm3_where_x_le_12p3=delta, solids=len(front.Solids()),
                  changed='cradle floor +X end 12.3 -> 24.4; web X 0.5..2.9 -> 0.5..24.4; nothing on the tool side')
    (out/'front-to-cheek.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main(Path(sys.argv[1]))
