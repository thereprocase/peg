"""Verify published five-slot spectra and exact native/export receipts."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];B=R/'bench/reviews/tee-fit-v5-spectra';D=R/'docs/gallery/key-fan';r=json.loads((B/'fit-v5-check.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert r['source_sha256']==sha(R/'bench/source/tee_racks_v1/fit_spectrum_v5.py')
assert [q['size_mm'] for q in r['coupons']]==[3,5,7]
for q in r['coupons']:
 assert q['native_valid'] and q['native_solids']==1 and q['mesh_closed'] and q['mesh_components']==1
 assert q['guide_mm']==max(40,8*q['size_mm']) and q['vent_diameter_mm']==1
 assert [s['letter'] for s in q['slots']]==list('ABCDE')
 assert [s['clearance_per_flat_mm'] for s in q['slots']]==[.10,.15,.19,.23,.28]
 for s in q['slots']:assert abs(s['bore_af_mm']-q['size_mm']-s['total_af_clearance_mm'])<1e-8
ex=json.loads((B/'export-check.json').read_text());assert ex['freecad_document_matches_combined_step'] and all(q['closed_mesh'] for q in ex['native_and_mesh_exports'])
assert ex['checker_sha256']==sha(R/'bench/source/tee_racks_v1/tools/check_fit_spectrum.py')
for name,h in r['files'].items():assert sha(B/name)==h['sha256']
for p,h in json.loads((R/'publication/tee-fit-v5-page-additions.json').read_text()).items():assert sha(R/p)==h['sha256']
assert json.loads((D/'fit-v5/checks.json').read_text())==r
text=(D/'index.html').read_text();assert 'id="fit-coupon-v5"' in text and '3 mm = _, 5 mm = _, 7 mm = _' in text
for size in [3,5,7]:
 name=f'HX05-fit-v5-{size}mm__rack-angle__print.stl';assert sha(D/'fit-v5'/name)==sha(B/name)
print('Fit v5: three connected five-slot spectra, rack angles, vents and native/export hashes PASS; slicing and physical selection pending')
