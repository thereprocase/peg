"""Integrity and scope gates for the extended engineering publication."""
from pathlib import Path
import gzip,hashlib,json,struct,zipfile
R=Path(__file__).resolve().parents[1];B=R/'bench/reviews/key-fan-audit-v1';D=R/'docs/gallery/key-fan/studies'
def load(p):return json.loads(p.read_text())
def sha(data):return hashlib.sha256(data).hexdigest()
scene=load(D/'data/scene.json');assert scene['installed_step_sha256']=='62a8acee8145f11967618944d6b4e0e2a54f3d96c428f3a197c91fc82f86798a'
assert len(scene['tools'])==26 and len(scene['fields'])==26
geometries=[scene['holder'],scene['fem'],scene['board']]+[q['display_mesh'] for q in scene['tools']]
for field in scene['fields']:
 if 'display_mesh' in field:geometries.append(field['display_mesh'])
for q in geometries:
 data=(D/'data'/q['file']).read_bytes();assert sha(data)==q['sha256'],q['file']
 decoded=gzip.decompress(data) if data[:2]==b'\x1f\x8b' else data
 if 'decoded_sha256' in q:assert sha(decoded)==q['decoded_sha256']
for q in scene['fields']:
 data=(D/'data'/q['file']).read_bytes();assert sha(data)==q['sha256'];raw=gzip.decompress(data);assert len(raw)==q['vertices']*8
 assert q['max_stress_quant_error_MPa']<.02
 assert max(q['max_component_displacement_quant_error_mm'])<.001
films=load(D/'films.json');assert len(films)==60 and len({q['id'] for q in films})==60
for q in films:
 assert q['frames']>1 and q['fps']>0
 assert (D/q['poster']).is_file();p=D/q['video'];assert sha(p.read_bytes())==q['provenance']['files'][p.name.removeprefix('HX04-')]['sha256']
source_hashes={sha(p.read_bytes()) for p in (R/'bench/source/key_fan_audit_v1').iterdir() if p.is_file()}
for p in B.glob('*.json'):
 q=load(p)
 if isinstance(q,dict) and q.get('source_sha256'):assert q['source_sha256'] in source_hashes,p.name
scene_hashes={sha((B/name).read_bytes()) for name in ['scene-capture-v1.json','scene-capture-extra.json']}
for q in films:
 provenance=q['provenance'];assert provenance['recorder_sha256'] in source_hashes
 assert provenance['source_scene_sha256'] in scene_hashes
 if provenance.get('viewer_js_sha256'):assert provenance['viewer_js_sha256'] in source_hashes
for name in ['modal-all-pegs.json','modal-four-corners.json','modal-face.json','modal-h5-all-pegs.json','modal-h5-four-corners.json','modal-h5-face.json']:
 q=load(B/name);assert len(q['modes'])==5 and all(m['frequency_Hz']>0 and m['imaginary_frequency_Hz']==0 for m in q['modes'])
for q in load(B/'hoop-nonlinear-h04.json')['results']:assert q['force_balance_relative_error']<.002
assert load(B/'reaction-force-moment.json')['passed']
fits=load(B/'requested-fits-check.json');assert fits['sizes_mm']==[3,5] and fits['closed_mesh'] and fits['step_solids']==2
page=(R/'docs/gallery/key-fan/index.html').read_text();assert 'fit-requested-3-5/' in page and 'studies/' in page
report=(D/'report.html').read_text();assert '15%' in report and 'not a physically qualified' in report and 'front-host' in report
for q in ['sequence','relief','loadField','DecompressionStream']:assert q in (D/'study.js').read_text()
for p in D.rglob('*'):
 if p.is_file():assert p.suffix not in ['.pyc','.gcode'] and 'private' not in p.name and '__pycache__' not in p.parts
assert sum(p.stat().st_size for p in (R/'docs').rglob('*') if p.is_file())<1024**3
print('Extended HX04: 26 fields/tools, 60 films, hashes, force/moment, paired fits, scope and site budget PASS')

archive=R/'.local-runtime/hx04-audit/completed-films.zip'
if archive.exists():
 from PIL import Image
 import io
 with zipfile.ZipFile(archive) as z:
  for q in films:
   name=next(n for n in z.namelist() if n.endswith('/'+q['id']+'.gif'))
   image=Image.open(io.BytesIO(z.read(name)));assert image.n_frames>1
   image.seek(0);first=sha(image.convert('RGB').tobytes());image.seek(image.n_frames//2);assert sha(image.convert('RGB').tobytes())!=first,q['id']
 print('All 60 downloaded GIF payloads contain differing animation frames PASS')

assert load(B/'campaign-timing.json')['wall_seconds']>=14400
assert load(B/'campaign-timing.json')['minimum_met']
