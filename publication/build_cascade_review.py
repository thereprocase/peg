"""Refresh CF01 public media, evidence and page receipts after the local reviews."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[1];B=R/'bench/reviews/bespoke-tools-v1/CF01';D=R/'docs/gallery/cascade-funnels'
r=json.loads((B/'report.json').read_text());evidence={name.removesuffix('.json'):json.loads((B/name).read_text()) for name in ['report.json','junctions.json','print-geometry.json','installation-screen.json','stiffness.json','toolpaths.json','bridge-screen.json']}
assert evidence['stiffness']['inputs']['step']==r['files'][r['assets']['installed_step']]['sha256']
assert evidence['stiffness']['inputs']['spec']==hashlib.sha256((B/(r['prefix']+'__fea-spec.json')).read_bytes()).hexdigest()
assert evidence['stiffness']['passed'] and evidence['print-geometry']['passed'] and evidence['junctions']['passed']
evidence['physical_tests']='Pending'
for name in ['installed.glb','print.glb','loaded.glb','toolpaths.svg',r['assets']['print_stl']]:shutil.copyfile(B/name,D/name)
(D/'checks.json').write_text(json.dumps(evidence,indent=2)+'\n')
receipts={p.relative_to(D).as_posix():dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size) for p in D.rglob('*') if p.is_file()}
(R/'publication/cascade-funnels-v1-additions.json').write_text(json.dumps(receipts,indent=2)+'\n')
for folder,file in [('current-pegs','current-pegs-v1-additions.json'),('bespoke-tools','bespoke-tools-v1-additions.json')]:
 p=R/'publication'/file;d=json.loads(p.read_text());f=R/'docs/gallery'/folder/'index.html';d['index.html']=dict(sha256=hashlib.sha256(f.read_bytes()).hexdigest(),bytes=f.stat().st_size);p.write_text(json.dumps(d,indent=2)+'\n')
print('CF01: refreshed',len(receipts),'public assets')
