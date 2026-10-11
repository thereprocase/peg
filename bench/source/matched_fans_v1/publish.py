"""Versioned matched-fan package and scoped gallery publication."""
from pathlib import Path
import json,hashlib,shutil,zipfile,sys
ROOT=Path(__file__).resolve().parents[3]
TAG='hx05-matched-fans-v1-2026-10-11'
BASE='https://github.com/thereprocase/peg/releases/download/'+TAG+'/'
def receipt(p):return dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def write(p,data):p.write_text(json.dumps(data,indent=2)+'\n')
def install_navigation(root=ROOT):
 root=Path(root)
 if not (root/'docs/gallery/key-fan/stacked/matched/index.html').exists():return
 for relative,href,record in [('docs/gallery/key-fan/stacked/green/index.html','../matched/','green-fan-v1-review'),('docs/gallery/key-fan/stacked/index.html','matched/','stacked-fans-v1-review')]:
  p=root/relative;s=p.read_text();link=f'<a href="{href}">Matched metric + Torx fans</a> · '
  if link not in s:s=s.replace('<nav>','<nav>'+link,1);p.write_text(s)
  rp=root/'publication'/f'{record}.json';rows=json.loads(rp.read_text());rows[relative]=receipt(p);write(rp,rows)
def main(work):
 work=Path(work);native=work/'tight-native';bundle=work/'bundle';release=work/'release';release.mkdir(exist_ok=True)
 dst=ROOT/'docs/gallery/key-fan/stacked/matched';dst.mkdir(parents=True,exist_ok=True)
 rev=ROOT/'bench/reviews/matched-fans-v1';rev.mkdir(parents=True,exist_ok=True)
 setup=json.loads((work/'setup-check.json').read_text());assert setup['passed']
 for name in ('layout.json','access.json','spacing.json','setup-check.json'):shutil.copy2(work/name,rev/name)
 for name in ('native.json','sweep-check.json','pinch-check.json'):shutil.copy2(native/name,rev/name)
 assert all(json.loads((rev/n).read_text())['passed'] for n in ('access.json','sweep-check.json','pinch-check.json'))
 models=[];native_data=json.loads((native/'native.json').read_text())
 for ident,number,label in [('HX05B','13189','Metric'),('HX05A','33034','Torx')]:
  n=next(x for x in native_data['racks'] if x['id']==ident);r=rev/ident;r.mkdir(exist_ok=True)
  for name in ('build-check.json','print-check.json'):shutil.copy2(native/ident/name,r/name)
  edit=json.loads((work/'tests'/ident/'edit-check.json').read_text());assert edit['fresh_process_reopen_and_execute_passed']
  write(r/'edit-check.json',edit)
  model=f'{ident}_{number}_matched_v1.FCStd'
  gui=next(x for x in setup['models'] if x['filename']==model)
  assert abs(gui['volume_mm3']-n['volume'])<1e-4
  shutil.copy2(bundle/model,release/model)
  bounds=n['bounds'];dims=[bounds[i+1]-bounds[i] for i in (0,2,4)]
  print_check=json.loads((r/'print-check.json').read_text());assert print_check['passed']
  models.append(dict(id=ident,set=number,label=label,filename=model,dimensions_mm=dims,volume_mm3=n['volume'],guide_range_mm=[min(t['guide'] for t in n['tools']),max(t['guide'] for t in n['tools'])],print_check=print_check,edit_check=edit))
  for file in ('installed.step','installed.stl','left-tip-print.step','left-tip-print.stl'):
   target=bundle/'exports'/ident/file;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(native/ident/file,target)
 for name in ('hx05_family.py','SETUP_MATCHED_FANS.FCMacro','README.txt'):shutil.copy2(Path(__file__).parent/name,bundle/name)
 shutil.copytree(rev,bundle/'validation',dirs_exist_ok=True)
 src=bundle/'source';src.mkdir(exist_ok=True)
 for p in Path(__file__).parent.iterdir():
  if p.is_file():shutil.copy2(p,src/p.name)
 zipname='HX05AB_matched_fans_v1_bundle.zip'
 allow=[p for p in bundle.rglob('*') if p.is_file() and (p.parent==bundle and (p.suffix in ('.FCStd','.py','.FCMacro','.txt')) or p.relative_to(bundle).parts[0] in ('exports','validation','source')) and '__pycache__' not in p.parts]
 with zipfile.ZipFile(release/zipname,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(allow):z.write(p,str(p.relative_to(bundle)))
 assets={name:receipt(release/name) for name in [zipname]+[r['filename'] for r in models]}
 metadata=dict(release=TAG,bundle_url=BASE+zipname,models=models,assets=assets,tool_access_passed=True,native_release_checks=26,pinch_checks=26,pitches_mm=native_data['pitches_mm'],green_reference='8478fc8425a6028588baebe45d4bf56435b6547d',scope='Matched metric and Torx review geometry; unchanged green inch body. Torx round sockets use provisional tip diameters and do not lock handle rotation. Unsliced; physical fit, whole-holder installation and loads unqualified.')
 write(dst/'review.json',metadata)
 image_names=['stack-hero.jpg']+[ident+suffix for ident in ('HX05A','HX05B') for suffix in ('-hero.jpg','-front.jpg','-plan.jpg','-empty-hero.jpg','-print-hero.jpg')]
 for name in image_names:shutil.copy2(work/'renders'/name,dst/name)
 cards=[]
 for r in models:
  ident=r['id'];pc=r['print_check'];dims=' × '.join(f'{x:.1f}' for x in r['dimensions_mm']);pd=' × '.join(f'{x:.1f}' for x in pc['print_dimensions_mm'])
  extra='<p class="note"><strong>Torx fit is provisional.</strong> The circular sockets use catalogue tip envelopes, not measured full shanks. They do not lock handle rotation. The renders show intended handle placement. Measure the actual shanks and test fit before manufacturing this holder.</p>' if ident=='HX05A' else '<p>The hex flats follow the T-handle axis. +0.38 mm total across-flats clearance comes from the selected 3C/5C coupon fit; other sizes and long guides still need a physical test. A nominal 2 mm hex can rotate inside the 2.38 mm AF socket, so its shown handle clocking is also provisional.</p>'
  cards.append(f'''<section id="{ident}"><h2>{r['set']} {r['label']} — eight tools</h2><img src="{ident}-hero.jpg" width="1000" height="710" alt="{r['label']} fan with handles arranged like the selected green rack">{extra}<p>Holder: <strong>{dims} mm</strong> (width × depth × height, including pegs). Straight guides: {r['guide_range_mm'][0]:.0f}–{r['guide_range_mm'][1]:.1f} mm, plus the 3 mm lead-in.</p><details><summary>Front, plan and empty-holder views</summary><img loading="lazy" src="{ident}-front.jpg" width="1000" height="585" alt="{r['label']} fan front view"><img loading="lazy" src="{ident}-plan.jpg" width="1000" height="500" alt="{r['label']} fan plan view"><img loading="lazy" src="{ident}-empty-hero.jpg" width="1000" height="710" alt="{r['label']} holder with tools hidden"></details><details><summary>Tip-end print pose</summary><img loading="lazy" src="{ident}-print-hero.jpg" width="1000" height="710" alt="{r['label']} native holder resting on its tip end on a 256 mm bed"><p>Nominal, unscaled envelope: {pd} mm, at 45° bed yaw. Flat native bed contact: {pc['bed_contact_area_cm2']:.1f} cm². Minimum nominal edge margin: {pc['available_edge_margin_mm']:.2f} mm. Compensation, brim and supports require a new slice; the metric rack is particularly close to the bed edge.</p></details><p><a href="{BASE+r['filename']}">Native FCStd only</a> — install the module from the bundle first.</p></section>''')
 page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Matched Bondhus metric and Torx fans</title><style>body{margin:0;background:#f5f3ec;color:#222;font:18px/1.55 system-ui,sans-serif}main{max-width:1000px;margin:auto;padding:24px}a,summary{color:#126657}h1,h2{line-height:1.15}img{display:block;width:100%;height:auto;border-radius:14px;background:#ece9df;margin:18px 0}section{margin:38px 0}summary{cursor:pointer}.note{border-left:5px solid #247b6d;padding:16px;background:#e0eee7}.stack{max-width:520px;margin:auto}code{overflow-wrap:anywhere}</style></head><body><main><nav><a href="../green/">Approved green inch fan</a> · <a href="../">Earlier stack</a></nav><h1>The green fan, adapted to metric and Torx</h1><p>The Bondhus 13189 and 33034 sets now use the green rack’s swept handle arrangement, flatter T-bars, long straight sleeves, filled tip base and broad print-plane gussets. Each is sized for its own tools; these are separate holders.</p>'''
 page+=f'<p class="note"><a href="{BASE+zipname}"><strong>Download both editable FreeCAD models and exports</strong></a><br>Unzip and run <code>SETUP_MATCHED_FANS.FCMacro</code> once in FreeCAD. Edit yellow cells in <strong>01_GlobalParameters</strong> and <strong>02_KeyLayout</strong>; press F5. The included module is required for custom-feature rebuilds. Full recomputes can take several minutes.</p>'
 page+=''.join(cards)
 page+=f'''<section><h2>One matching family</h2><img class="stack" src="stack-hero.jpg" width="650" height="1055" alt="Orange Torx and blue metric fans stacked above the unchanged green inch fan"><p>The green inch holder is unchanged. The new stack has {' then '.join(f'{p:.1f} mm' for p in native_data['pitches_mm'])} between top-hook datums, from bottom to top, on the 25.4 mm peg grid. The smaller tools tuck above and behind the main fan; the staggered shaft tips have independent centres.</p><p>Every shaft rises at least 10° toward its handle. Each new holder has 60 mm minimum engagement, growing with shaft size, a 3 mm axial lead-in widened 1.5 mm per side, below-floor 1 mm vents, 8 mm base rounds and tapered gussets broadened 12 mm per side and 16 mm toward the tip-end bed face.</p></section><section><h2>Checks and limits</h2><p>All three bodies are valid single solids. All 26 represented tools pass stored-tool and continuous axial socket-release checks against the native holders; all 26 two-finger pinch approaches clear the represented neighboring tools and holders. New entrance and vent probes are clear. Board-side geometry matches each new rack’s generated receiver. Parameter edits, save/reopen and live feature restoration pass in FreeCAD 1.1.3.</p><p>Reference tools use catalogue lengths and an assumed 18 mm grip diameter. The Torx shaft dimensions and clocking remain provisional. These checks do not qualify subsequent free-hand removal, whole-rack installation, printed fits, supports or loads. The new models have not been sliced. The native bed poses are unscaled; no previous slice estimate or FEA result transfers.</p><p><a href="review.json">Numerical review and download hashes</a> · <a href="https://github.com/thereprocase/peg/tree/main/bench/source/matched_fans_v1">Construction source</a></p></section></main></body></html>'''
 (dst/'index.html').write_text(page,encoding='utf-8')
 p=ROOT/'publication/release-assets.json';rows=json.loads(p.read_text());rows.update(assets);write(p,rows)
 p=ROOT/'publication/release-downloads.json';links=json.loads(p.read_text())
 for name in assets:links['key-fan/stacked/matched/'+name]=BASE+name
 write(p,links)
 p=ROOT/'docs/gallery/release-downloads.js';before,tail=p.read_text().split('const links=',1);_,end=json.JSONDecoder().raw_decode(tail);p.write_text(before+'const links='+json.dumps(links,separators=(',',':'))+tail[end:])
 install_navigation()
 rows={str(p.relative_to(ROOT)):receipt(p) for folder in (dst,rev,Path(__file__).parent) for p in sorted(folder.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
 write(ROOT/'publication/matched-fans-v1.json',rows)
 __import__('runpy').run_path(str(ROOT/'bench/source/matched_fans_xray_v1/publish.py'))['overlay']()
 print(json.dumps(assets,indent=2));print('Matched page bytes',sum(p.stat().st_size for p in dst.iterdir()))
if __name__=='__main__':main(sys.argv[1])
