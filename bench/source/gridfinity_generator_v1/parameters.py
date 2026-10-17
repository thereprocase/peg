"""Shared native generator parameter validation and board-grid layout."""
import math

DEFAULTS = dict(columns=2, rows=1, clearance=0.0, web=2.4, beam=10.0, angle=0.0, mount_rows=2, backplate=True)


def validate(values):
    unknown = set(values) - set(DEFAULTS)
    if unknown:
        raise ValueError(f"Unknown parameters: {sorted(unknown)}")
    p = DEFAULTS | values
    for key in ('columns', 'rows'):
        value = p[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or int(value) != value or not 1 <= value <= 12:
            raise ValueError(f'{key} must be a whole number from 1 to 12')
        p[key] = int(value)
    if p['columns'] * p['rows'] > 64:
        raise ValueError('Use at most 64 cells per generated shelf')
    for key, lo, hi in [('clearance', -0.10, 0.20), ('web', 2.4, 6.0), ('beam', 5.0, 20.0), ('angle', -30.0, 5.0)]:
        if isinstance(p[key], bool) or not isinstance(p[key], (int, float)) or not math.isfinite(p[key]) or not lo <= p[key] <= hi:
            raise ValueError(f'{key} must be between {lo} and {hi} mm')
    if isinstance(p['mount_rows'], bool) or not isinstance(p['mount_rows'], (int,float)) or not math.isfinite(p['mount_rows']) or int(p['mount_rows']) != p['mount_rows'] or not 1 <= p['mount_rows'] <= 4:
        raise ValueError('mount_rows must be a whole number from 1 to 4')
    p['mount_rows'] = int(p['mount_rows'])
    if not isinstance(p['backplate'], bool):
        raise ValueError('backplate must be true or false')
    p['mount_z'] = [-25.4*i for i in range(p['mount_rows'])]
    p['back_bottom'] = -12.7 if p['mount_rows'] == 1 else p['mount_z'][-1]-4.28
    p['web_columns'] = [(i-p['columns']/2)*42 for i in range(p['columns']+1)]
    lanes = math.ceil((42 * p['columns'] + 6) / 25.4)
    p['frame_width'] = 42 * p['columns'] + 4
    # Keep each complete 10 mm root post inside the shelf ends.
    available = [i for i in range(lanes) if abs((i-(lanes-1)/2)*25.4)+5 <= p['frame_width']/2+1e-8]
    holes = available[::3]
    if holes[-1] != available[-1]:
        holes.append(available[-1])
    p['mount_width'] = lanes * 25.4 - 2
    p['mount_columns'] = [(i - (lanes - 1) / 2) * 25.4 for i in holes]
    p['front_y'] = 51.55 + 42 * (p['rows'] - 1)
    return p
