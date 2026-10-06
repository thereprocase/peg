"""Check the exact CF01 source, native evidence and published preview receipts."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];D=R/'bench/reviews/cascade-funnels-v2/CF01';P=R/'docs/gallery/cascade-funnels'
def read(name):return json.loads((D/name).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=read('report.json');g=read('print-geometry.json');j=read('junctions.json');f=read('stiffness.json');i=read('installation-screen.json');t=read('toolpaths.json')
assert r['source_sha256']==j['source_sha256']==sha(R/'bench/source/cascade_funnels_v2/build.py')
assert r['version']==2 and '__v2__' in r['prefix']
assert g['passed'] and j['passed'] and f['passed'] and i['pass']
assert all(n>0 for n in j['adjacent_funnel_overlap_mm3'])
assert j['order']=='right highest, middle, left lowest'
assert r['checks']['native_valid'] and r['checks']['solids']==1 and r['checks']['unchanged_board_side_delta_mm3']<1e-6
assert all(x['max_intersection_mm3']<1e-6 for x in r['checks']['tool_routes'])
assert r['files'][r['assets']['installed_step']]['sha256']==f['inputs']['step']==i['input_sha256']
assert f['inputs']['spec']==sha(D/(r['prefix']+'__fea-spec.json'))
assert all(lc['point']==r['load_point'] for case in f['cases'] for lc in case['loads'])
assert t['input_stl_sha256']==g['inputs']['print_stl']==sha(P/r['assets']['print_stl'])
assert all(x['maximum'][1]<.15 for k,x in t['features'].items() if k in ['Support','Support interface','Overhang wall'])
for name,v in json.loads((R/'publication/cascade-funnels-v1-additions.json').read_text()).items():
 p=P/name;assert sha(p)==v['sha256'] and p.stat().st_size==v['bytes'],name
print('CF01: touching joints, right-high order, CAD, print geometry, removal, stiffness, slice and public receipts PASS; physical tests pending')
