"""Verify final model receipts, exact source/STEP references and compressed browser previews."""
from pathlib import Path
import gzip,json,hashlib,struct
R=Path(__file__).resolve().parents[1];D=R/'docs/gallery/key-fan/final';B=R/'bench/reviews/final-racks-v1';S=R/'bench/source/final_racks_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
models=json.loads((D/'models.json').read_text());assert [q['id'] for q in models]==['HX04','HX05A','HX05B','HX05C']
for q in models:
 check=q['native_check'];assert check['passed'] and check['native_valid'] and check['native_solids']==1
 assert all(m['closed'] and m['volume_relative_error']<.005 for m in check['meshes'].values())
 assert q['tool_count']==len(check['sockets']) and q['loaded_depth_mm']<=178
 assert check==json.loads((B/q['id']/'native-check.json').read_text())
 policy=q['geometry']['socket_policy'];assert {k:v for k,v in policy.items() if k!='vent_outlet'}==dict(total_af_clearance_mm=.38,guide_minimum_mm=40,guide_size_ratio=8,lead_axial_mm=3,lead_width_per_flat_mm=1.5,vent_diameter_mm=1)
 if q['id']=='HX04':
  refinement=json.loads((B/'HX04/owner-refinement.json').read_text());full=json.loads((B/'HX04/full-guide-refinement.json').read_text());assert full['base_step_sha256']==refinement['step_sha256'] and full['step_sha256']==check['step_sha256']
  assert full['source_sha256']==sha(S/'complete_guide_walls.py') and refinement['source_sha256']==sha(S/'refine_owner.py') and check['refinement_rear_delta_mm3']<1e-6
  assert all(r['added_material_overlap_mm3']<1e-3 for proof in (refinement,full) for r in proof['added_material_withdrawal_screen'])
  doc=json.loads((B/'HX04/document-roundtrip.json').read_text());assert doc['valid'] and doc['topology_counts_equal'] and doc['max_vertex_difference_mm']<1e-6 and doc['step_sha256']==check['step_sha256']
 assert not any(r['op']=='label failed' for r in q['geometry']['finish'])
 assert any(r['op']=='board-side delta' and r['mm3']<1e-6 for r in q['geometry']['finish'])
 step=next(h for n,h in q['files'].items() if n.endswith('installed.step'));assert step['sha256']==check['step_sha256']
 for pose in ('installed','loaded','print'):
  data=gzip.decompress((D/q['id']/(pose+'.glb.gz')).read_bytes());magic,ver,n=struct.unpack_from('<III',data);assert magic==0x46546c67 and ver==2 and n==len(data)
  assert (D/q['id']/({'loaded':'hero','installed':'empty','print':'print'}[pose]+'.jpg')).stat().st_size>5000
 for name,h in json.loads((B/q['id']/'run.json').read_text())['source_dependencies'].items():assert sha(R/name)==h,(q['id'],name)
for name,q in json.loads((R/'publication/final-racks-v1-additions.json').read_text()).items():assert sha(R/name)==q['sha256'] and (R/name).stat().st_size==q['bytes']
assert not any('__pycache__' in Path(name).parts for name in json.loads((R/'publication/final-racks-v1-additions.json').read_text()))
assert '3C / 5C' in (D/'index.html').read_text()
assert sum(p.stat().st_size for p in (R/'docs').rglob('*') if p.is_file())<1024**3
print('Final four models: native/source receipts, socket/vent policy, previews, rendered poses and site budget PASS')
