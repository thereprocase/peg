"""Verify bespoke review assets against the matching CAD, FEA and slice evidence."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];D=R/'docs/gallery/bespoke-tools';B=R/'bench/reviews/bespoke-tools-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
receipts=json.loads((R/'publication/bespoke-tools-v1-additions.json').read_text())
for name,record in receipts.items():
 p=D/name;assert p.is_file(),name;assert sha(p)==record['sha256'],name;assert p.stat().st_size==record['bytes'],name
for id in ['HX01','TM01','CL01']:
 d=B/id;r=json.loads((d/'report.json').read_text());g=json.loads((d/'print-geometry.json').read_text());f=json.loads((d/'stiffness.json').read_text());t=json.loads((d/'toolpaths.json').read_text());i=json.loads((d/'installation-screen.json').read_text())
 assert r['source_sha256']==sha(R/'bench/source/bespoke_tools_v1/build.py'),id
 assert r['checks']['native_valid'] and r['checks']['solids']==1 and r['checks']['unchanged_board_side_delta_mm3']<1e-6,id
 assert g['passed'] and f['passed'] and i['pass'],id
 assert t['input_stl_sha256']==g['inputs']['print_stl']==sha(D/id/r['assets']['print_stl']),id
 assert f['inputs']['step']==i['input_sha256']==r['files'][r['assets']['installed_step']]['sha256'],id
 if (d/r['assets']['installed_step']).exists():assert sha(d/r['assets']['installed_step'])==f['inputs']['step'],id
 assert all(v['maximum'][1]<.15 for k,v in t['features'].items() if k in ['Support','Support interface','Overhang wall']),id
 assert max(r['print_bounds_mm'])<256,id
 if (d/r['assets']['print_stl']).exists():assert sha(D/id/r['assets']['print_stl'])==sha(d/r['assets']['print_stl']),id
 assert (D/id/'checks.json').is_file() and (D/id/'toolpaths.svg').is_file(),id
 for role in ['installed','loaded','print']:
  if (d/(role+'.glb')).exists():assert sha(D/id/(role+'.glb'))==sha(d/(role+'.glb')),(id,role)
 assert r['checks']['tool_routes'] and all(v['max_intersection_mm3']<1e-6 for v in r['checks']['tool_routes']),id
for name in ['key-seating.json','external-key-fit.json']:assert json.loads((B/'HX01'/name).read_text())['passed'],name
print(json.dumps(dict(bespoke_parts=3,verified_public_assets=len(receipts),geometry_stiffness_and_slice_provenance='pass',physical_tests='pending'),indent=2))
