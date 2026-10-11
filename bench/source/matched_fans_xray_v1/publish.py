"""Publish the matched-fan front projection and independently checked STEP downloads."""
from pathlib import Path
import json,hashlib,shutil,sys
ROOT=Path(__file__).resolve().parents[3]
TAG='hx05-print-step-v1-2026-10-11'
BASE='https://github.com/thereprocase/peg/releases/download/'+TAG+'/'
DST=ROOT/'docs/gallery/key-fan/stacked/matched'
REV=ROOT/'bench/reviews/matched-fans-xray-v1'
def receipt(p):return dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def overlay():
 if not (REV/'step-check.json').exists():return
 check=json.loads((REV/'step-check.json').read_text());assert check['passed']
 links=[]
 for ident,label in [('HX05C','13190 inch — green'),('HX05B','13189 metric — blue'),('HX05A','33034 Torx — orange')]:
  row=next(r for r in check['models'] if r['filename'].startswith(ident))
  links.append(f'<li><a href="{BASE+row["filename"]}">{label}: print STEP</a></li>')
 section='''<!-- matched-xray:start --><section id="front-xray"><h2>Front-on shaft X-ray and print STEP files</h2><a href="'''+BASE+'''HX05_front_xray_v1.png"><img src="front-xray.webp" width="1980" height="957" alt="Front-on X-ray of inch, metric and Torx fans, showing individual shafts inside translucent holders at the same scale"></a><p>Orthographic front view, all three at the same scale. Filled dots mark seated tips; open dots mark sleeve entrances. Projected crossings can be separated in depth. Tap the image for full resolution.</p><ul>'''+''.join(links)+'''</ul><p>Holder only, in the checked tip-end-down print pose, millimetres, nominal and unscaled. Each STEP reloads as one valid solid. Use the STEP downloads here in preference to the earlier bundle exports. Supports, filament compensation and brim still need slicer review; the metric rack has only 3.22 mm nominal bed-edge clearance. Torx full-shank fit remains provisional.</p></section><!-- matched-xray:end -->'''
 p=DST/'index.html';s=p.read_text()
 if '<!-- matched-xray:start -->' in s:
  a,tail=s.split('<!-- matched-xray:start -->',1);_,b=tail.split('<!-- matched-xray:end -->',1);s=a+section+b
 else:s=s.replace('<section id="HX05B">',section+'<section id="HX05B">',1)
 p.write_text(s)
 rp=ROOT/'publication/matched-fans-v1.json';rows=json.loads(rp.read_text())
 for p in [DST/'index.html',DST/'front-xray.webp',ROOT/'bench/source/matched_fans_v1/publish.py']:rows[str(p.relative_to(ROOT))]=receipt(p)
 write(rp,rows)
 rows={str(p.relative_to(ROOT)):receipt(p) for folder in [REV,Path(__file__).parent] for p in sorted(folder.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
 rows[str((DST/'front-xray.webp').relative_to(ROOT))]=receipt(DST/'front-xray.webp')
 write(ROOT/'publication/matched-fans-xray-v1.json',rows)
def main(work,render):
 work=Path(work);render=Path(render);REV.mkdir(exist_ok=True)
 check=json.loads((work/'step-check.json').read_text());assert check['passed']
 for name in ('step-check.json','export-check.json','surface-check.json'):
  shutil.copy2(work/name,REV/name)
 shutil.copy2(render/'front-xray.webp',DST/'front-xray.webp')
 shutil.copy2(render/'front-xray.png',work/'release/HX05_front_xray_v1.png')
 assets={p.name:receipt(p) for p in (work/'release').iterdir() if p.suffix in ('.step','.png')}
 write(REV/'assets.json',dict(release=TAG,assets=assets))
 p=ROOT/'publication/release-assets.json';rows=json.loads(p.read_text());rows.update(assets);write(p,rows)
 p=ROOT/'publication/release-downloads.json';links=json.loads(p.read_text())
 for name in assets:links['key-fan/stacked/matched/'+name]=BASE+name
 write(p,links)
 p=ROOT/'docs/gallery/release-downloads.js';before,tail=p.read_text().split('const links=',1);_,end=json.JSONDecoder().raw_decode(tail);p.write_text(before+'const links='+json.dumps(links,separators=(',',':'))+tail[end:])
 overlay()
if __name__=='__main__':main(*sys.argv[1:])
