"""Check the published fit-trial page, downloads and exact prototype geometry receipts."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];D=R/'docs/gallery/key-fan';B=R/'bench/reviews/tee-fit-v4-guide40'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
j=json.loads((D/'fit-v4/checks.json').read_text());r=j['geometry'];ex=j['exports']
assert r['version']==4 and r['handle_axis']=='flat-to-flat along design Y'
assert r['source_sha256']==sha(R/'bench/source/tee_racks_v1/fit_coupon_v4.py')
assert r['policy_sha256']==sha(R/'bench/source/tee_racks_v1/study/socket_policy.py')
assert ex['closed_mesh'] and ex['mesh_components']==4 and ex['step_solids']==4
expected={'L2':(2.38,40),'T2.5':(2.88,40),'T5':(5.38,40),'T10':(10.38,80)}
for q in r['pieces']:
 af,g=expected[q['tool']];assert q['bore_af_mm']==af and abs(q['straight_guide_mm']-g)<1e-8 and q['clearance_per_flat_mm']==.19 and q['vent_diameter_mm']==1
mesh='HX05-fit-v4__left-end__print.stl';assert sha(D/'fit-v4'/mesh)==sha(B/mesh)==ex['files'][mesh]
for p,h in json.loads((R/'publication/tee-fit-v4-page-additions.json').read_text()).items():assert sha(R/p)==h['sha256'] and (R/p).stat().st_size==h['bytes']
text=(D/'index.html').read_text()
if 'id="fit-coupon-v6"' not in text and 'id="fit-coupon-v5"' not in text: assert 'id="fit-coupon-v4"' in text and 'id="hx04-v2-archive"' in text and '5.38 mm AF bore' in text and '40.0 mm' in text and '80.0 mm' in text
if 'id="fit-coupon-v6"' not in text and 'id="fit-coupon-v5"' not in text: assert text.index('Download the new coupon STL')<text.index('Archived HX04 v2 rack')
assert "querySelector('#rack-viewer')" in (D/'review.js').read_text()
js=(R/'docs/gallery/release-downloads.js').read_text();assert 'MutationObserver' in js;links,_=json.JSONDecoder().raw_decode(js.split('const links=',1)[1]);assert links==json.loads((R/'publication/release-downloads.json').read_text())
print('Fit v4: 40/80 mm guides, increased clearance and floor vents, flats, native/export hashes and page links PASS; physical fit and slicing pending')
