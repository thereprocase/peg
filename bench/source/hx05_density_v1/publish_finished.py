"""Publish the owner-selected finished shapes and fixed-pose infill modifiers."""
from pathlib import Path
import hashlib,json,shutil,zipfile,os,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];LIGHT=os.environ.get('HX05_LIGHT')=='1'
WORK=ROOT/('.local-runtime/hx05-light-v2' if LIGHT else '.local-runtime/hx05-density-v1')
REV=ROOT/('bench/reviews/hx05-light-v2' if LIGHT else 'bench/reviews/hx05-finished-v1');PAGE=ROOT/'docs/gallery/key-fan/finished/index.html'
TAG='hx05-light-v2-2026-10-12' if LIGHT else 'hx05-finished-v1-2026-10-12';BASE='https://github.com/thereprocase/peg/releases/download/'+TAG+'/'
def receipt(p):return dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def refresh_scoped(changed):
 for p in (ROOT/'publication').glob('*.json'):
  data=json.loads(p.read_text());dirty=False
  if not isinstance(data,dict):continue
  for name in changed:
   if name in data and isinstance(data[name],dict) and 'sha256' in data[name]:data[name]=receipt(ROOT/name);dirty=True
  if p.name=='key-fan-v2-additions.json' and 'docs/gallery/key-fan/index.html' in changed:
   data['index.html']=receipt(ROOT/'docs/gallery/key-fan/index.html');dirty=True
  if dirty:write(p,data)
def overlay():
 if not PAGE.exists():return
 changed=['bench/source/matched_fans_v1/publish.py',str(PAGE.relative_to(ROOT))]+[str(p.relative_to(ROOT)) for p in Path(__file__).parent.iterdir() if p.is_file()]
 for relative in ['docs/gallery/key-fan/index.html','docs/gallery/key-fan/stacked/matched/index.html','docs/gallery/key-fan/stacked/green/index.html','docs/gallery/key-fan/final/index.html']:
  p=ROOT/relative;text=p.read_text()
  banner='<p class="note" data-hx05-finished><strong>Updated finished models:</strong> <a href="/peg/gallery/key-fan/finished/">All three Bondhus fans, native FreeCAD, print STEP and 100% infill modifier projects</a>. The earlier revision below is preserved as history.</p>'
  if 'data-hx05-finished' not in text:
   end=text.index('</h1>')+len('</h1>');text=text[:end]+banner+text[end:];p.write_text(text)
  changed.append(relative)
 refresh_scoped(changed)

def main():
 REV.mkdir(exist_ok=True);PAGE.parent.mkdir(parents=True,exist_ok=True)
 release=WORK/'finished-release';bundle=WORK/'finished-bundle';release.mkdir(exist_ok=True);bundle.mkdir(exist_ok=True)
 mask=json.loads((WORK/'raw-mask-mesh-check.json').read_text());assert mask['passed']
 shutil.copy2(WORK/'raw-mask-mesh-check.json',REV/'modifier-mesh-check.json')
 pinch=json.loads((WORK/'final-access/pinch-check.json').read_text());assert pinch['passed'] and len(pinch['rows'])==26
 shutil.copy2(WORK/'final-access/pinch-check.json',REV/'pinch-check.json')
 access=json.loads((WORK/'final-access/tool-access-check.json').read_text());assert access['passed'] and len(access['rows'])==26
 shutil.copy2(WORK/'final-access/tool-access-check.json',REV/'tool-access-check.json')
 shutil.copy2(WORK/'mesh-cap-check.json',REV/'mesh-cap-check.json')
 models=[]
 for ident,number,label in [('HX05C','13190','Inch'),('HX05B','13189','Metric'),('HX05A','33034','Torx')]:
  out=WORK/ident;draft=json.loads((out/'draft-check.json').read_text());mods=json.loads((out/'modifiers-check.json').read_text());step=json.loads((out/'finished-step-check.json').read_text());sliced=json.loads((out/'finished-slice-review.json').read_text());paths=json.loads((out/'finished-toolpaths.json').read_text())
  assert all(d['passed'] for d in [draft,mods,step]) and sliced['exit_code']==0 and sliced['slicer_mesh_repairs']==0 and sliced['modifier_count']==4
  assert paths['bed_centerline_screen_passed'] and paths['socket_core_screen_passed']
  if LIGHT:
   proof=json.loads((out/'unchanged-print-mesh.json').read_text());assert proof['passed'] and proof['body_mesh_byte_identity']
   for key in ['light-parameters','unchanged-print-mesh']:shutil.copy2(out/(key+'.json'),REV/f'{ident}-{key}.json')
  for name,data in [('draft-check',draft),('modifier-check',mods),('step-check',step),('slice-review',sliced),('toolpaths',paths)]:write(REV/f'{ident}-{name}.json',data)
  stem=f'{ident}_{number}_'+('light_v2' if LIGHT else 'finished_v1');native=stem+'.FCStd';project=stem+'_tip_down.3mf';original_step=step['filename'];stepname=stem+'_tip_down.step'
  step['filename']=stepname;write(REV/f'{ident}-step-check.json',step)
  shutil.copy2(next(out.glob('*_density_v1.FCStd')),release/native)
  shutil.copy2(out/original_step,release/stepname)
  # Rename the reviewed geometry-only archive without touching its bytes.
  source=out/f'{ident}_{number}_draft_review_tip_down.3mf'
  assert receipt(source)['sha256']==sliced['project_sha256']
  shutil.copy2(source,release/project)
  for name in [native,project,stepname]:shutil.copy2(release/name,bundle/name)
  for role in ['foundation','mounts','sockets','ribs']:
   shutil.copy2(out/f'print-modifier-{role}.stl',bundle/f'{stem}_MODIFIER_{role}_100pct.stl')
  for pose in ['hero','front','plan','print-hero']:
   name=f'{ident}-'+('light-v2-' if LIGHT else 'finished-')+f'{pose}.jpg';shutil.copy2((ROOT/'.local-runtime/hx05-density-v1/renders' if LIGHT else WORK/'renders')/f'{ident}-{pose}.jpg',release/name)
  models.append(dict(id=ident,set=number,label=label,native=native,project=project,step=stepname,print_dimensions_mm=draft['print_dimensions_mm'],nominal_edge_margin_mm=draft['available_edge_margin_mm'],maximum_uncut_housing_overhang_deg=draft['maximum_checked_uncut_housing_overhang_deg'],modifier_count=4,modifier_infill_percent=100,total_estimated_print_time=sliced['total_estimated_print_time'],filament_grams=sliced['filament_grams']))
 for p in [Path(__file__).parent/'hx05_density.py',Path(__file__).parent/'SETUP_DENSITY_FANS.FCMacro',Path(__file__).parent/'README.txt',ROOT/'bench/source/hx05_parametric_v1/hx05_parametric.py',ROOT/'bench/source/matched_fans_v1/hx05_family.py']:shutil.copy2(p,bundle/p.name)
 if LIGHT:shutil.copy2(Path(__file__).parent/'README_LIGHT.txt',bundle/'README.txt')
 for p in Path(__file__).parent.iterdir():
  if p.is_file():dst=bundle/'source'/p.name;dst.parent.mkdir(exist_ok=True);shutil.copy2(p,dst)
 (bundle/'checks/release.json').unlink(missing_ok=True)
 for p in REV.glob('*.json'):
  if p.name=='release.json':continue  # A ZIP cannot contain its own final hash.
  dst=bundle/'checks'/p.name;dst.parent.mkdir(exist_ok=True);shutil.copy2(p,dst)
 for p in [WORK/'fixed-pose-modifier-sections.png',WORK/'fixed-pose-modifier-sections.svg',Path(__file__).parent/'style-guide.html']:
  name=('HX05_light_v2_'+p.name if LIGHT else p.name)
  shutil.copy2(p,release/name);shutil.copy2(p,bundle/name)
 zipname='HX05_light_v2_native_STEP_Orca_bundle.zip' if LIGHT else 'HX05_finished_v1_native_STEP_Orca_bundle.zip'
 with zipfile.ZipFile(release/zipname,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(bundle.rglob('*')):
   if p.is_file():z.write(p,str(p.relative_to(bundle)))
 assets={p.name:receipt(p) for p in release.iterdir() if p.is_file()}
 write(REV/'release.json',dict(release=TAG,assets=assets,models=models,scope='Owner-selected finished outside geometry, unchanged tested cutters and fixed bed pose. Four independent 100% infill modifiers. STEP round trips and owner-profile Orca slices/screens; physical fits, support removal and loads remain separate.'))
 rows=json.loads((ROOT/'publication/release-assets.json').read_text());rows.update(assets);write(ROOT/'publication/release-assets.json',rows)
 links=json.loads((ROOT/'publication/release-downloads.json').read_text())
 for name in assets:links['key-fan/finished/'+name]=BASE+name
 write(ROOT/'publication/release-downloads.json',links)
 p=ROOT/'docs/gallery/release-downloads.js';before,tail=p.read_text().split('const links=',1);_,end=json.JSONDecoder().raw_decode(tail);p.write_text(before+'const links='+json.dumps(links,separators=(',',':'))+tail[end:])
 cards=[]
 for m in models:
  ident=m['id'];dims=' × '.join(f'{v:.1f}' for v in m['print_dimensions_mm'])
  cards.append(f'''<section id="{ident}"><h2>{m['set']} {m['label']} fan</h2><img src="{BASE}{ident}-finished-hero.jpg" width="1000" height="710" alt="Finished {m['label'].lower()} holder outside geometry"><p><a href="{BASE}{m['project']}">Orca project: four 100% infill modifiers</a> · <a href="{BASE}{m['step']}">Print-pose STEP</a> · <a href="{BASE}{m['native']}">Editable FreeCAD</a></p><p>Nominal print envelope: {dims} mm. Minimum bed-edge margin: {m['nominal_edge_margin_mm']:.1f} mm. Recorded P1S/ASA slice: {m['total_estimated_print_time']}, {m['filament_grams']:.0f} g.</p><details><summary>Front, plan and chosen bed face</summary><img loading="lazy" src="{BASE}{ident}-finished-front.jpg" width="1000" height="585" alt="{m['label']} front view"><img loading="lazy" src="{BASE}{ident}-finished-plan.jpg" width="1000" height="500" alt="{m['label']} plan view"><img loading="lazy" src="{BASE}{ident}-finished-print-hero.jpg" width="1000" height="710" alt="{m['label']} holder on the fixed tip-end bed face"></details></section>''')
 PAGE.write_text('''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Finished Bondhus fan racks</title><style>body{margin:0;background:#f5f3ec;color:#222;font:18px/1.55 system-ui,sans-serif}main{max-width:1000px;margin:auto;padding:24px}a,summary{color:#126657}h1,h2{line-height:1.15}img{display:block;width:100%;height:auto;border-radius:14px;background:#ece9df;margin:18px 0}section{margin:38px 0}.note{border-left:5px solid #247b6d;padding:16px;background:#e0eee7}summary{cursor:pointer}code{overflow-wrap:anywhere}</style></head><body><main><nav><a href="../">Key fans</a> · <a href="../stacked/matched/">Earlier matched models</a></nav><h1>Finished Bondhus fan racks</h1><p>Three single-set racks: 13190 inch, 13189 metric and 33034 Torx. Compact swept handles, long straight sleeves, integrated print-plane gussets and restrained outside tapers. The chosen tip-end bed face is fixed. Tested socket fits remain unchanged.</p><p class="note"><a href="'''+BASE+zipname+'''">Download all three: native FreeCAD, STEP, Orca projects and construction sources</a></p><p>Outside housing growth is limited to 30° from print Z; contraction is unrestricted. The original pegs and internal bore bridges are separate support cases. Four nonphysical modifiers make the bed-face foundation, peg roots/collector belts, sleeves/floors and sleeve-to-back load paths <strong>100% infill</strong>. Bulk starts at <strong>12% gyroid, four walls</strong>.</p>'''+''.join(cards)+'''<section id="density"><h2>Where the solid material goes</h2><a href="'''+BASE+'''fixed-pose-modifier-sections.png"><img src="'''+BASE+'''fixed-pose-modifier-sections.png" width="1440" height="1060" alt="Actual XY layer sections: green solid modifiers, gray bulk, white sockets"></a><p>Actual XY sections; bed yaw is undone for readability only. Reinforcement directions are independent of the fixed print orientation. Masks may extend through air as selection handles; Orca intersects them with the physical holder. Never fuse them into an ordinary print part.</p></section><section id="downloads"><h2>Edit and print preparation</h2><p>Extract the bundle and run <code>SETUP_DENSITY_FANS.FCMacro</code> once in FreeCAD. Open the matching FCStd. <strong>86 DraftedHolder</strong> is the current physical part; older bodies and clipped cores are hidden construction history. Toggle <strong>DensityHelpers</strong> to inspect the four zones. Install the supplied modules before recomputing.</p><p>Open 3MF files <strong>as projects</strong>. Confirm four Modifier parts, each at 100%, and one socket support blocker. Downloads are nominal/unscaled, with no private printer profile or G-code. The inch project requests normal/grid supports to keep its footprint on the bed; metric and Torx were reviewed with organic tree supports. Select your actual calibrated filament profile, compensate once and review supports. The recorded slices used the owner's captured P1S 0.4 mm / 0.20 mm / calibrated ASA profiles; estimates depend on those settings.</p><p>All three STEP files reload as valid single solids with bounded volume/bounds and native surface checks. All four modifiers survive Orca slicing; repair counts are zero, extrusion centerlines stay on the bed, and the bounded socket-core screen finds no trapped support paths. Rear-peg mesh seams use the recorded bounded tessellation adapter; native CAD is the manufacturing reference.</p><p><strong>Fit scope:</strong> +0.38 mm total across flats follows the winning 3C/5C coupons. Other sizes and long sleeves still need physical fit confirmation. The 2 mm key may rotate. Torx circular seats use catalogue tip envelopes; full-shank fit and handle rotation remain provisional. These files have no physical load or support-removal rating. The 30° check covers uncut outside housing facets, not every internal cut or peg underside.</p><p><a href="https://github.com/thereprocase/peg/tree/main/bench/reviews/hx05-finished-v1">Checks and exact download hashes</a> · <a href="https://github.com/thereprocase/peg/tree/main/bench/source/hx05_density_v1">Construction source</a> · <a href="'''+BASE+'''style-guide.html">Workshop design guide (HTML download)</a></p></section></main></body></html>''')
 if LIGHT:
  baseline=json.loads((ROOT/'bench/reviews/hx05-finished-v1/release.json').read_text());old={m['id']:m['filament_grams'] for m in baseline['models']}
  current={m['id']:m['filament_grams'] for m in models};assert current['HX05C']<=old['HX05C']*.55
  text=PAGE.read_text().replace('12% gyroid, four walls','5% gyroid, three walls').replace('fixed-pose-modifier-sections.png','HX05_light_v2_fixed-pose-modifier-sections.png').replace('-finished-','-light-v2-').replace('style-guide.html','HX05_light_v2_style-guide.html')
  summary='<section id="lightweight"><h2>Lightweight density revision</h2><p>The outside part, tested sockets and print orientation are unchanged. Narrow 100% infill zones replace the previous broad solid cores. Bulk is 5% gyroid with three continuous walls; all three use normal/grid supports in the recorded review slices.</p><ul>'+''.join(f'<li>{m["set"]} {m["label"]}: <strong>{m["filament_grams"]:.0f} g</strong>, down from {old[m["id"]]:.0f} g ({100*(1-m["filament_grams"]/old[m["id"]]):.0f}% less).</li>' for m in models)+'</ul><p>Solid zones: 1.6 mm bed-face foundation, 1.2 mm socket bands and load-path plates, 2.5 mm root widths, local 5.5 mm radius peg-root discs. Density-only parameters are separate from the outside construction. Strength changes with the material reduction; physical load qualification remains separate.</p><p><a href="https://github.com/thereprocase/peg/releases/tag/hx05-finished-v1-2026-10-12">Previous v1 — 12% gyroid, four walls and broad solid cores</a></p></section>'
  text=text.replace('<h1>Finished Bondhus fan racks</h1>','<h1>Finished Bondhus fan racks</h1>'+summary).replace('metric and Torx were reviewed with organic tree supports','all three were reviewed with normal/grid supports')
  PAGE.write_text(text)
  for ident in current:
   shutil.copy2(WORK/ident/'light-parameters.json',REV/f'{ident}-light-parameters.json');shutil.copy2(WORK/ident/'unchanged-print-mesh.json',REV/f'{ident}-unchanged-print-mesh.json')
 overlay()
 rows={str(p.relative_to(ROOT)):receipt(p) for folder in [REV,Path(__file__).parent] for p in sorted(folder.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
 rows[str(PAGE.relative_to(ROOT))]=receipt(PAGE);rows['tools/check_hx05_density.py']=receipt(ROOT/'tools/check_hx05_density.py')
 if LIGHT:rows['tools/check_hx05_light.py']=receipt(ROOT/'tools/check_hx05_light.py')
 write(ROOT/('publication/hx05-light-v2.json' if LIGHT else 'publication/hx05-finished-v1.json'),rows)
 print(json.dumps(dict(assets=len(assets),release=str(release),site_bytes=sum(p.stat().st_size for p in (ROOT/'docs').rglob('*') if p.is_file())),indent=2))
if __name__=='__main__':main()
