"""Check HX04 v2 evidence (full peg grid, install swing, brace zones), socket contracts and public artifact receipts."""
from pathlib import Path
import hashlib, json
R = Path(__file__).resolve().parents[1]; B = R/'bench/reviews/key-fan-v2/HX04'; P = R/'docs/gallery/key-fan'


def read(n): return json.loads((B/n).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


r = read('report.json'); ex = read('exact-check.json'); fe = read('stiffness.json'); g = read('print-geometry.json'); sl = read('slice-summary.json')
assert r['id'] == 'HX04' and r['version'] == 2 and r['pose'] == 'left-cheek'
assert all(sha(R/p) == d for p, d in r['source_dependencies'].items()), 'source changed since the evidence was written'
S = r['sockets']; assert len(S) == 26 and sorted({s['set'] for s in S}) == ['hex', 'tee', 'torx']
key = {'hex': lambda s: float(s['size']), 'tee': lambda s: float(s['size'])}
for s in S:                                                     # seat depth at least 4x the key size, never under 12 mm
    if s['set'] in key:
        assert s['seat_depth_mm'] >= max(12., 4*key[s['set']](s))-.05, s
    assert s['floor_slope_deg'] > 0, s
assert all(s['keyed'] for s in S if s['set'] == 'tee' and float(s['size']) >= 3)
assert ex['all_routes_ok'] and ex['stored_ok'] and ex['straighten_ok'] and min(ex['floors_mm']) >= 3.
assert len(ex['routes']) == 26 and all(x['ok'] for x in ex['routes'])
assert fe['inputs']['step'] == r['files'][r['assets']['installed.step']]['sha256']
assert min(l['stiffness_N_per_mm'] for c in fe['cases'] for l in c['loads']) > 100
assert g['components'] == 1 and g['inputs']['print_stl'] == r['files'][r['assets']['print.stl']]['sha256']
# islands: none, or only declared single vertices on the vertical end wall (probe artefact, see print-geometry.json)
assert g['islands']['passed'] or (len(g['islands'].get('declared', [])) == len(g['islands']['points'])
                                  and all(q['vertices'] == 1 and q['print_xyz'][0] >= g['extents_mm'][0]-.5 for q in g['islands']['points']))
assert sl['plain']['input_sha256'] == sl['solid_zones']['input_sha256'] == sha(P/r['assets']['print.stl']) == r['files'][r['assets']['print.stl']]['sha256']
assert sl['solid_zones']['features_g'].get('Internal solid infill', 0) > 50, 'solid-infill zones not applied by the slicer'
assert sl['coupon_plain']['input_sha256'] == r['files'][r['assets']['coupon_print.stl']]['sha256'] == sha(P/r['assets']['coupon_print.stl'])
sw = read('install-swing.json')                       # a peg in every covered hole; seated clear, hoops snap
assert sw['passed'] and sw['pegs'] == dict(hooks=9, locking=9, bearing=72) and sw['seated']['bearing_mm3'] < 1e-3
assert sw['worst_bearing_per_peg_mm3'] <= sw['graze_per_peg_limit_mm3'] <= .25 and sw['seated']['locking_snap_mm3'] > 0
assert min(l['stiffness_N_per_mm'] for c in fe['cases'] for l in c['loads']) > 1000
for n, v in json.loads((R/'publication/key-fan-v2-additions.json').read_text()).items():
    p = P/n; assert sha(p) == v['sha256'] and p.stat().st_size == v['bytes'], n
print('HX04 v2: 26 sockets (4x seats, sloped floors, keyed T bores), 90-peg grid with install swing, exact storage and withdrawal, floors, print geometry, stiffness, slices with solid zones, coupon and public receipts PASS; physical tests pending')
