"""Verify published five-slot spectra and exact native/export receipts."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];B=R/'bench/reviews/tee-fit-v6-fan';D=R/'docs/gallery/key-fan';r=json.loads((B/'fit-v6-check.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert r['source_sha256']==sha(R/'bench/source/tee_racks_v1/fit_spectrum_v6.py')
assert [q['size_mm'] for q in r['coupons']]==[3,5,7]
for q in r['coupons']:
 assert q['native_valid'] and q['native_solids']==1 and q['mesh_closed'] and q['mesh_components']==1
 assert q['guide_mm']==max(40,8*q['size_mm']) and q['vent_diameter_mm']==1
 assert [s['letter'] for s in q['slots']]==list('ABCDE')
 assert [s['clearance_per_flat_mm'] for s in q['slots']]==[.10,.15,.19,.23,.28]
 for s in q['slots']:assert abs(s['bore_af_mm']-q['size_mm']-s['total_af_clearance_mm'])<1e-8
ex=json.loads((B/'export-check.json').read_text());assert ex['freecad_document_matches_combined_step'] and all(q['closed_mesh'] for q in ex['native_and_mesh_exports'])
assert ex['checker_sha256']==sha(R/'bench/source/tee_racks_v1/tools/check_fit_spectrum_v6.py')
for name,h in r['files'].items():assert sha(B/name)==h['sha256']
for p,h in json.loads((R/'publication/tee-fit-v6-page-additions.json').read_text()).items():assert sha(R/p)==h['sha256']
assert json.loads((D/'fit-v6/checks.json').read_text())==r
assert all(q['fan_frame_match'] for q in r['coupons'])
assert abs(r['coupons'][0]['elevation_deg']-25.09821582313435)<1e-8
assert abs(r['coupons'][1]['elevation_deg']-38.527906505600775)<1e-8
text=(D/'index.html').read_text();assert 'id="fit-coupon-v6"' in text and '3 mm = _, 5 mm = _, 7 mm = _' in text
for size in [3,5,7]:
 name=f'HX05-fit-v6-{size}mm__fan-angle__print.stl';assert sha(D/'fit-v6'/name)==sha(B/name)
print('Fit v6: three connected five-slot spectra, rack angles, vents and native/export hashes PASS; slicing and physical selection pending')

# Independent check against the original fan study, not the coupon frame alone.
import os,sys,numpy as np
frame=json.loads((R/'bench/source/tee_racks_v1/fan_orientation_v6.json').read_text())
assert sha(R/frame['source_layout'])==frame['source_layout_sha256']
assert sha(R/'bench/source/key_fan_v1/study/short.py')==frame['source_study_sha256']
os.environ.update(frame['build_env']);sys.path.insert(0,str(R/'bench/source/key_fan_v1/study'))
import short
lo=short.Layout(json.loads((R/frame['source_layout']).read_text())['x']);tools={t['name']:t for t in lo.tools if t['set']=='tee'};rotation=np.array(frame['print_rotation'])
for q in frame['coupons']:
 size=q['size_mm']
 if size!=7:u=tools[str(size)]['u'];bar=tools[str(size)]['bar']
 else:
  u=tools['6']['u']+tools['8']['u'];u/=np.linalg.norm(u)
  bar=tools['6']['bar']+tools['8']['bar'];bar-=u*np.dot(bar,u);bar/=np.linalg.norm(bar)
 assert np.allclose(rotation@u,q['shaft_print'],atol=1e-12,rtol=0)
 assert np.allclose(rotation@bar,q['bar_print'],atol=1e-12,rtol=0)
print('Independent HX04 fan shaft/hex-flat print-frame comparison PASS')
