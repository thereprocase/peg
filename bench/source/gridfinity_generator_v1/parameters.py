"""Shared native generator parameter validation and board-grid layout."""
import math

DEFAULTS = dict(columns=2, rows=1, clearance=0.0, web=2.4, beam=10.0, angle=0.0)


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
    lanes = math.ceil((42 * p['columns'] + 6) / 25.4)
    holes = list(range(0, lanes, 3))
    if holes[-1] != lanes - 1:
        holes.append(lanes - 1)
    p['mount_width'] = lanes * 25.4 - 2
    p['mount_columns'] = [(i - (lanes - 1) / 2) * 25.4 for i in holes]
    p['front_y'] = 51.55 + 42 * (p['rows'] - 1)
    return p
