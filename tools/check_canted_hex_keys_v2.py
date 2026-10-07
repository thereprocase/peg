"""Check HX02 v2 geometry contracts, matching evidence and public artifact receipts."""
from pathlib import Path
import hashlib, json, math
R = Path(__file__).resolve().parents[1]; B = R/'bench/reviews/canted-hex-keys-v2/HX02'; P = R/'docs/gallery/canted-hex-keys'


def read(n): return json.loads((B/n).read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


r = read('report.json'); g = read('print-geometry.json'); f = read('stiffness.json'); i = read('installation-screen.json'); t = read('toolpaths.json'); sl = read('slice-summary.json')
assert r['version'] == 2 and r['source_sha256'] == sha(R/'bench/source/canted_hex_keys_v2/build.py')
assert all(sha(R/name) == digest for name, digest in r['source_dependencies'].items())
assert r['checks']['native_valid'] and r['checks']['solids'] == 1 and r['checks']['unchanged_board_side_delta_mm3'] < 1e-6
keys = r['tool_spec']['keys']; expected = [(1.5, 89), (2, 98), (2.5, 110), (3, 123), (4, 140), (5, 157), (6, 176), (8, 194), (10, 217)]
assert [(k['across_flats'], k['socket_depth_mm']) for k in keys] == expected
assert all(k['socket_depth_mm'] == k['straight_length'] for k in keys)
assert all(fl >= 2.95 for fl in r['checks']['measured_tip_floors_mm']), r['checks']['measured_tip_floors_mm']
assert r['pose'] == 'right-cheek' and r['tool_spec']['axis_angle_from_vertical_deg'] == 30
assert r['tool_spec']['short_arm_direction'][2] < 0
for k, path in zip(keys, r['checks']['tool_routes']):
    assert path['max_intersection_mm3'] < 1e-5 and path['neighbor_intersection_mm3'] < 1e-5 and path['downward_stop_intersection_mm3'] > 0
    assert math.isclose(path['outward_travel_mm']/path['axial_withdrawal_mm'], .5)
    assert math.isclose(k['axis'][2], math.sqrt(3)/2)
assert g['passed'] and f['passed'] and i['pass']
# Print gate: no undeclared overhang; declared items are engraved-numeral recesses only.
assert all(x['ok'] for x in g['overhangs']['features']) and all(x['declared'] for x in g['overhangs']['features'] if x['declared'])
assert g['islands']['passed']
assert f['inputs']['step'] == i['input_sha256'] == r['files'][r['assets']['installed_step']]['sha256']
assert f['inputs']['spec'] == sha(B/(r['prefix']+'__fea-spec.json'))
assert all(load['point'] == r['load_point'] for case in f['cases'] for load in case['loads'])
assert t['input_stl_sha256'] == sl['input_sha256'] == g['inputs']['print_stl'] == sha(P/r['assets']['print_stl'])
# Peg supports behind the mounting face, plus organic support the review slice adds at the engraved
# numerals' counters (declared in print-geometry.json); bound the body-side share.
assert t['features']['Support']['body_side_grams'] < 12, t['features']['Support']['body_side_grams']
for n, v in json.loads((R/'publication/canted-hex-keys-v2-additions.json').read_text()).items():
    p = P/n; assert sha(p) == v['sha256'] and p.stat().st_size == v['bytes'], n
print('HX02 v2: nine full-depth sockets, 30-degree axes, measured floors, withdrawal, native CAD, print, installation, stiffness, slicing and public receipts PASS; physical tests pending')
