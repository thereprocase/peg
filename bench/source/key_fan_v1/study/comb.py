"""Compact sunburst, part 1: the comb (Torx tubes + hex pipes alternating in one row near the board).

Installed frame: x = user's left, y = out from the board, z = up, mm.
Every L-key stands vertical with its short arm straight out (+y). Torx mouths are the top of the
rack (z = 0); hex mouths are HEX_DROP lower, so each hex key withdraws straight up through the slot
between two Torx tubes. Spacing: every hex key column must clear the neighbouring Torx tube (tube =
bore + TUBE_WALL) by SWEEP_CLEAR.
"""
import json, math
from pathlib import Path
import numpy as np

DATA = json.loads((Path(__file__).parents[2]/'three_set_rack_v1/key_sets.json').read_text())
HEX, TORX, TEES = DATA['hex'], DATA['torx'], DATA['tee']
CLEAR = .35          # bore over the key (radius)
TUBE_WALL = 2.0      # Torx tube wall where it stands proud of the hex mouths
SWEEP_CLEAR = 2.0    # hex key column to Torx tube
FLOOR = 3.
END_WALL = 3.


def hex_key_r(i): return HEX[i]['across_flats']/math.sqrt(3)            # corner radius of the key
def hex_bore(i): return hex_key_r(i)+CLEAR
def torx_key_r(k): return TORX[k]['point_to_point']/2
def torx_bore(k): return torx_key_r(k)+CLEAR
def torx_tube(k): return torx_bore(k)+TUBE_WALL


def layout(extra=0.):
    """x of every pipe from the user's left: hex0, T0, hex1, T1, ... hex8, T8. extra = added gap per pair."""
    xs, kind = [], []
    x = 0.
    for i in range(9):
        if i > 0:
            x -= torx_tube(i-1)+hex_key_r(i)+SWEEP_CLEAR+extra
        xs.append(x); kind.append(('hex', i))
        x -= hex_key_r(i)+torx_tube(i)+SWEEP_CLEAR+extra
        xs.append(x); kind.append(('torx', i))
    left = xs[0]+hex_bore(0)+END_WALL+1.5
    right = xs[-1]-torx_tube(8)-1.
    shift = -(left+right)/2
    return [v+shift for v in xs], kind, (left+shift, right+shift)


if __name__ == '__main__':
    for extra in (0., 1., 2.):
        xs, kind, (l, r) = layout(extra)
        print('extra %.1f  width %.1f  (%.1f .. %.1f)' % (extra, l-r, l, r))
    xs, kind, _ = layout(0.)
    for v, k in zip(xs, kind):
        print(k, round(v, 2))
