"""Package a tested editable model; keep CAD binaries in GitHub Releases."""
from pathlib import Path
import json,hashlib,shutil,zipfile,sys
root=Path(__file__).resolve().parents[3]
work=Path(sys.argv[1]);bundle=work/'bundle';release=work/'release';release.mkdir(exist_ok=True)
review=root/'bench/reviews/hx05-parametric-v1';review.mkdir(parents=True,exist_ok=True)
for source in (work/'output/build-check.json',work/'tests/edit-check.json',work/'tests/setup-check.json'):
 shutil.copy2(source,review/source.name);shutil.copy2(source,bundle/source.name)
checks={p.stem:json.loads(p.read_text()) for p in review.glob('*.json')}
assert checks['build-check']['symmetric_difference_mm3']<.1
assert checks['edit-check']['second_process_reopen_passed']
assert checks['edit-check']['restored_generator_execute_passed']
assert checks['setup-check']['setup_macro_passed']
for name in ('hx05_parametric.py','SETUP_HX05.FCMacro','README.txt'):
 shutil.copy2(Path(__file__).parent/name,bundle/name)
source_dir=bundle/'source';source_dir.mkdir(exist_ok=True)
for name in ('create_document.py','test_document.py','test_reopen.py'):
 shutil.copy2(Path(__file__).parent/name,source_dir/name)
shutil.copy2(root/'bench/reviews/green-fan-v1/layout.json',source_dir/'approved-layout.json')
model='HX05C_13190_parametric_v1.FCStd';zipname='HX05C_13190_parametric_v1_bundle.zip'
shutil.copy2(bundle/model,release/model)
allow=[model,'hx05_parametric.py','SETUP_HX05.FCMacro','README.txt','build-check.json','edit-check.json','setup-check.json']
allow += ['source/'+n for n in ('create_document.py','test_document.py','test_reopen.py','approved-layout.json')]
with zipfile.ZipFile(release/zipname,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name in allow:z.write(bundle/name,name)
def receipt(p):return dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
tag='hx05-parametric-v1-2026-10-10'
base='https://github.com/thereprocase/peg/releases/download/'+tag+'/'
assets={name:receipt(release/name) for name in (model,zipname)}
metadata=dict(release=tag,bundle_url=base+zipname,fcstd_url=base+model,assets=assets,checks=checks,scope='Selected green Bondhus 13190 inch rack; rear mount fixed; edited geometry needs renewed clearance and print review.')
(root/'docs/gallery/key-fan/stacked/green/parametric.json').write_text(json.dumps(metadata,indent=2)+'\n')
p=root/'publication/release-assets.json';rows=json.loads(p.read_text());rows.update(assets);p.write_text(json.dumps(rows,indent=2)+'\n')
p=root/'publication/release-downloads.json';links=json.loads(p.read_text())
for name in assets:links['key-fan/stacked/green/'+name]=base+name
p.write_text(json.dumps(links,indent=2)+'\n')
p=root/'docs/gallery/release-downloads.js';before,tail=p.read_text().split('const links=',1);_,end=json.JSONDecoder().raw_decode(tail)
p.write_text(before+'const links='+json.dumps(links,separators=(',',':'))+tail[end:])
rows={}
for folder in (Path(__file__).parent,review):
 for p in sorted(folder.rglob('*')):
  if p.is_file() and '__pycache__' not in p.parts:rows[str(p.relative_to(root))]=receipt(p)
(root/'publication/hx05-parametric-v1.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(assets,indent=2))
