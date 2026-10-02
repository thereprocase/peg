"""Resolve an Orca user filament preset (a diff over a system preset) into one full JSON for the CLI.

Usage: python3 resolve_filament.py "<user preset .json>" <out.json>
Follows `inherits` through resources/profiles/BBL/filament/** by each file's "name", parent first.
"""
import json, sys
from pathlib import Path

RES = Path('/mnt/c/Program Files/OrcaSlicer/resources/profiles/BBL/filament')
by_name = {}
for f in RES.rglob('*.json'):
    try:
        d = json.loads(f.read_text(encoding='utf-8'))
    except (ValueError, UnicodeDecodeError):
        continue
    if isinstance(d, dict) and 'name' in d:
        by_name.setdefault(d['name'], d)

def resolve(d):
    parent = d.get('inherits')
    base = resolve(by_name[parent]) if parent else {}
    out = dict(base)
    out.update({k: v for k, v in d.items() if k != 'inherits'})
    return out

user = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
full = resolve(user)
full.pop('inherits', None)
full['from'] = 'User'
Path(sys.argv[2]).write_text(json.dumps(full, indent=1))
chain, n = [], user.get('inherits')
while n:
    chain.append(n); n = by_name[n].get('inherits')
print('chain:', ' -> '.join([user.get('name', '?')] + chain))
print({k: full.get(k) for k in ('name', 'filament_type', 'nozzle_temperature', 'nozzle_temperature_initial_layer',
       'nozzle_temperature_range_high', 'hot_plate_temp', 'textured_plate_temp', 'filament_flow_ratio',
       'pressure_advance', 'filament_shrink', 'filament_max_volumetric_speed', 'during_print_exhaust_fan_speed',
       'fan_max_speed', 'compatible_printers')})
