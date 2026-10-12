"""Package the three tested density overlays and add an idempotent gallery section."""
from pathlib import Path
import json,hashlib,shutil,zipfile,sys
ROOT=Path(__file__).resolve().parents[3]
WORK=ROOT/'.local-runtime/hx05-density-v1';REV=ROOT/'bench/reviews/hx05-density-v1'
TAG='hx05-density-v1-2026-10-12';BASE='https://github.com/thereprocase/peg/releases/download/'+TAG+'/'
PAGE=ROOT/'docs/gallery/key-fan/stacked/matched/index.html'
def receipt(p):return dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def write(p,data):p.write_text(json.dumps(data,indent=2)+'\n')
def overlay():
 if not (REV/'release.json').exists():return
 data=json.loads((REV/'release.json').read_text())
 cards=[]
 for row in data['models']:
  cards.append(f'<li><strong>{row["set"]} {row["label"]}</strong>: <a href="{BASE+row["project"]}">Orca modifier project</a> · <a href="{BASE+row["native"]}">editable FCStd</a> — {row["solid_core_percent"]:.1f}% core volume.</li>')
 section='''<!-- hx05-density:start --><section id="density"><h2>Strategic solid cores — density overlay v1</h2><p>Long sleeve walls/floors, upper and lower ribs in printed XY, local peg roots/collector belts and a 3 mm tip-end foundation receive <strong>100% infill</strong>. Remaining bulk starts at <strong>12% gyroid, four walls</strong>. The outer holders, sockets, vents and mounts are unchanged. Primary gravity bending paths lie in print XY; axial pulls and torsion still cross layers.</p><p><a href="'''+BASE+'''hx05-density-layer-sections.png">View actual XY sections of all three cores</a> · <a href="'''+BASE+'''HX05_density_v1_bundle.zip">Download all native models, modifier projects, modules and checks</a></p><ul>'''+''.join(cards)+'''</ul><p>Unzip the bundle and run <code>SETUP_DENSITY_FANS.FCMacro</code> once. Edit <strong>80_Density parameters</strong>; F5 rebuilds helpers. Open each 3MF <strong>as a project</strong> and confirm the core is a Modifier at 100%. Downloads are nominal/unscaled, with no private profile or G-code. Select your actual calibrated filament and supports; compensate once.</p><p>All three pass native reopen/edit-reset checks and Orca P1S/ASA review slices with retained modifier settings. The metric holder has about 2.54 mm compensated bed-edge clearance: its brim/support footprint needs review. The included extrusion/support screens are bounded checks, not bead-volume, support-removal, physical fit or load qualification. Torx full-shank fit and small-key rotation remain provisional. Earlier FEA does not qualify these density changes.</p><p><a href="https://github.com/thereprocase/peg/tree/main/bench/reviews/hx05-density-v1">Review receipts and slice estimates</a></p></section><!-- hx05-density:end -->'''
 text=PAGE.read_text()
 if '<!-- hx05-density:start -->' in text:
  a,tail=text.split('<!-- hx05-density:start -->',1);_,b=tail.split('<!-- hx05-density:end -->',1);text=a+section+b
 else:text=text.replace('<section id="HX05B">',section+'<section id="HX05B">',1)
 PAGE.write_text(text)
 p=ROOT/'publication/matched-fans-v1.json';rows=json.loads(p.read_text())
 for path in [PAGE,ROOT/'bench/source/matched_fans_v1/publish.py']:rows[str(path.relative_to(ROOT))]=receipt(path)
 write(p,rows)
 rows={str(p.relative_to(ROOT)):receipt(p) for folder in [REV,Path(__file__).parent] for p in sorted(folder.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
 write(ROOT/'publication/hx05-density-v1.json',rows)
def main():
 REV.mkdir(exist_ok=True)
 bundle=WORK/'bundle';release=WORK/'release';bundle.mkdir(exist_ok=True);release.mkdir(exist_ok=True)
 cap=json.loads((WORK/'mesh-cap-check.json').read_text());assert cap['passed']
 package=json.loads((WORK/'package-check.json').read_text());assert package['passed']
 for name in ['mesh-cap-check.json','package-check.json']:shutil.copy2(WORK/name,REV/name)
 models=[]
 for ident,label in [('HX05C','inch'),('HX05B','metric'),('HX05A','Torx')]:
  out=WORK/ident;check=json.loads((out/'check.json').read_text());edit=json.loads((out/'edit-check.json').read_text())
  review=json.loads((out/'slice-review.json').read_text());paths=json.loads((out/'toolpaths.json').read_text())
  assert check['passed'] and check['holder_unchanged'] and edit['passed'] and review['exit_code']==0
  assert paths['bed_centerline_screen_passed'] and paths['socket_core_screen_passed']
  for name in ['check.json','edit-check.json','slice-review.json','toolpaths.json']:
   shutil.copy2(out/name,REV/(ident+'-'+name))
  native=f'{ident}_{check["set"]}_density_v1.FCStd';project=f'{ident}_{check["set"]}_density_v1_tip_down.3mf'
  for name in [native,project]:shutil.copy2(out/name,bundle/name);shutil.copy2(out/name,release/name)
  for src,suffix in [('print-body-closed.stl','holder_print.stl'),('print-solid-core-closed.stl','MODIFIER_100pct.stl')]:shutil.copy2(out/src,bundle/f'{ident}_{check["set"]}_density_v1_{suffix}')
  models.append(dict(id=ident,set=check['set'],label=label,native=native,project=project,solid_core_percent=check['solid_core_percent'],slice_review=review,toolpath_screen_passed=True))
 for p in [ROOT/'bench/source/hx05_parametric_v1/hx05_parametric.py',ROOT/'bench/source/matched_fans_v1/hx05_family.py',Path(__file__).parent/'hx05_density.py',Path(__file__).parent/'SETUP_DENSITY_FANS.FCMacro',Path(__file__).parent/'README.txt']:shutil.copy2(p,bundle/p.name)
 for p in Path(__file__).parent.iterdir():
  if p.is_file():dst=bundle/'source'/p.name;dst.parent.mkdir(exist_ok=True);shutil.copy2(p,dst)
 for p in REV.iterdir():
  if p.is_file() and p.name!='release.json':dst=bundle/'checks'/p.name;dst.parent.mkdir(exist_ok=True);shutil.copy2(p,dst)
 for name in ['hx05-density-layer-sections.png','hx05-density-layer-sections.svg']:shutil.copy2(WORK/name,bundle/name)
 shutil.copy2(WORK/'hx05-density-layer-sections.png',release/'hx05-density-layer-sections.png')
 zipname='HX05_density_v1_bundle.zip'
 with zipfile.ZipFile(release/zipname,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(bundle.rglob('*')):
   if p.is_file():z.write(p,str(p.relative_to(bundle)))
 assets={p.name:receipt(p) for p in release.iterdir() if p.is_file()}
 write(REV/'release.json',dict(release=TAG,assets=assets,models=models,scope='Unchanged native holder + independent density helpers. Reviewed slicer/support centerlines; physical manufacture and loads unqualified. No printer job submitted.'))
 p=ROOT/'publication/release-assets.json';rows=json.loads(p.read_text());rows.update(assets);write(p,rows)
 p=ROOT/'publication/release-downloads.json';links=json.loads(p.read_text())
 for name in assets:links['key-fan/stacked/matched/'+name]=BASE+name
 write(p,links)
 p=ROOT/'docs/gallery/release-downloads.js';before,tail=p.read_text().split('const links=',1);_,end=json.JSONDecoder().raw_decode(tail);p.write_text(before+'const links='+json.dumps(links,separators=(',',':'))+tail[end:])
 overlay();print(json.dumps(assets,indent=2))
if __name__=='__main__':main()
