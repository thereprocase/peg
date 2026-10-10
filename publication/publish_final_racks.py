"""Publish the owner fan and three single-set final straight-socket models. No printer artifacts."""
from pathlib import Path
import json,hashlib,shutil,zipfile,argparse,re,html
R=Path(__file__).resolve().parents[1];S=R/'bench/source/final_racks_v1';B=R/'bench/reviews/final-racks-v1';D=R/'docs/gallery/key-fan/final'
TAG='final-racks-v1-2026-10-10';REL=f'https://github.com/thereprocase/peg/releases/download/{TAG}/'
NAMES={'HX04':'Your three-tier fan','HX05A':'Bondhus 33034 · Torx','HX05B':'Bondhus 13189 · metric','HX05C':'Bondhus 13190 · inch'}
def receipt(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
def apply():
 p=R/'docs/gallery/key-fan/index.html';s=p.read_text();s=re.sub(r'<section id="final-models">.*?</section>','',s,flags=re.S)
 banner='<section id="final-models"><h2>Final straight-socket models</h2><p><strong><a href="final/">Your complete fan and the three Bondhus single-set racks</a></strong> — rendered native models, STEP, FreeCAD and print meshes. Owner selected <strong>3C / 5C</strong>: +0.38 mm total across-flats clearance. New sockets have at least 40 mm straight engagement, separate 3 mm / 1.5 mm lead-ins, square stops and vents. Other sizes use this allowance provisionally; full-rack print and installation remain unqualified.</p></section>'
 s=s.replace('</header>','</header>'+banner,1)
 s=s.replace('No new physical fit or winning letters are established.','The owner subsequently completed the fit trial and selected 3C and 5C.').replace('3 mm = _, 5 mm = _','3 mm = C, 5 mm = C')
 p.write_text(s)
 p=R/'BENCH_HOLDERS.md';s=p.read_text().replace('revised 3/5 mm guide spectra await physical selection.','the owner selected 3C / 5C (+0.38 mm total AF clearance). [Final straight-socket models](https://thereprocase.github.io/peg/gallery/key-fan/final/) now include the revised full fan and three Bondhus single-set racks. Other sizes and complete-rack printing remain unqualified.');p.write_text(s)
 p=R/'docs/gallery/current-pegs/catalog.json';j=json.loads(p.read_text());q=next(q for q in j['parts'] if q['id']=='HX04');q['notes']['status']='Final straight-socket models available · 3C/5C fit selected';q['notes']['qualification']='The owner physically selected 3C/5C guide coupons. Full-rack physical printing, installation and loads remain unqualified. The final page provides new straight-socket native models and scoped CAD checks. This catalog viewer and the extended audit retain archived v2 geometry; its FEA/install results do not qualify the revised models.'
 q['extra_downloads']=[{'label':'Final fan and three Bondhus racks','url':'../key-fan/final/'},{'label':'Archived v2 engineering lab','url':'../key-fan/studies/'}];p.write_text(json.dumps(j,indent=2)+'\n')
 p=R/'publication/current-pegs-v1-additions.json';j=json.loads(p.read_text());j['catalog.json']=receipt(R/'docs/gallery/current-pegs/catalog.json');p.write_text(json.dumps(j,indent=2)+'\n')
 folder=R/'docs/gallery/key-fan';(R/'publication/key-fan-v2-additions.json').write_text(json.dumps({q.name:receipt(q) for q in folder.iterdir() if q.is_file() and q.name!='part-hx04__v1__left-cheek__fit-pf02c9-hoop5__print.stl'},indent=2)+'\n')

def prepare(build,out):
 out.mkdir(parents=True,exist_ok=True);B.mkdir(parents=True,exist_ok=True);models=[]
 source=[p for p in S.rglob('*') if p.is_file() and p.suffix in ('.py','.json','.ttf','.md','.txt') and '__pycache__' not in p.parts]
 source += [R/'bench/source/three_set_rack_v1/key_sets.json',R/'bench/source/bespoke_tools_v1/build.py',R/'bench/reviews/key-fan-v2/HX04/report.json']
 snap=R/'bench/source/gallery_current_mounts_v1/station_snapshot';source+=list((snap/'source').glob('*.py'))+[snap/'source/solder_v12/common.py']+[p for p in (snap/'reference').iterdir() if p.is_file()]
 for part,title in NAMES.items():
  src=build/part;dst=B/part;dst.mkdir(exist_ok=True)
  check=json.loads((src/'native-check.json').read_text());assert check['passed'],part
  geom=json.loads((src/'build-geometry.json').read_text());assert not any(q['op']=='label failed' for q in geom['finish'])
  for name in ('native-check.json','build-geometry.json','run.json','pose.json')+ (('owner-refinement.json','full-guide-refinement.json','document-roundtrip.json','base-native-check.json') if part=='HX04' else ()):shutil.copyfile(src/name,dst/name)
  prefix=f'{part}__final-v1__straight-C38__pf02c9-hoop5';downloads={};assets=[]
  for name,role in [('installed.step','STEP'),('model.FCStd','FreeCAD'),('print.stl','Print STL'),('print_solid.stl','Brace modifier STL')]:
   filename=prefix+'__'+name;shutil.copyfile(src/name,out/filename);assets.append(out/filename);downloads[role]=REL+filename
  entries={p.relative_to(R).as_posix():p.read_bytes() for p in source}
  for name in ('installed.step','model.FCStd','installed.stl','print.stl','print_solid.stl','installed_solid.stl','keys.stl','native-check.json','build-geometry.json','run.json','pose.json'):entries[f'bench/reviews/final-racks-v1/{part}/{name}']=(src/name).read_bytes()
  if part=='HX04':
   entries['bench/reviews/final-racks-v1/HX04/base-installed.step']=(src/'base-installed.step').read_bytes()
   entries['bench/reviews/final-racks-v1/HX04/owner-refinement.json']=(src/'owner-refinement.json').read_bytes()
   entries['bench/reviews/final-racks-v1/HX04/base-native-check.json']=(src/'base-native-check.json').read_bytes()
   for extra in ('guide-base.step','full-guide-refinement.json','document-roundtrip.json'):entries['bench/reviews/final-racks-v1/HX04/'+extra]=(src/extra).read_bytes()
  entries['README.txt']=(f'{title}. Rebuild from the repository-root layout using FreeCAD 1.1 Python with numpy/scipy:\nFREECAD_PYTHON=/path/to/freecad-python python bench/source/final_racks_v1/build_final.py --rack {part} --out OUTPUT\nThe saved final layout is the geometry authority; do not regenerate its search to reproduce this selection. Read source README and native-check.json. Print STL is unscaled, left-end orientation. Brace STL is a modifier, not a separate physical part. Apply your filament compensation exactly once. No profiles, supports or G-code are included. 3C/5C coupons selected; other sizes and full-rack installation/loads remain unqualified.\n').encode()
  manifest={n:{'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)} for n,b in entries.items()};entries['MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
  bundle=out/(prefix+'__CAD-source-review.zip')
  with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
   for n,b in sorted(entries.items()):z.writestr(n,b)
  with zipfile.ZipFile(bundle) as z:
   assert z.testzip() is None
   for n,q in manifest.items():assert hashlib.sha256(z.read(n)).hexdigest()==q['sha256']
  assets.append(bundle);downloads['CAD + source ZIP']=REL+bundle.name
  bb=geom['installed_bounds_mm'];depth=json.loads((S/'study'/f'{part.lower()}_final.json').read_text())['depth']
  models.append(dict(id=part,title=title,tool_count=len(check['sockets']),plate_width_mm=bb[1]-bb[0],body_bounds_mm=[bb[1]-bb[0],bb[3]-bb[2],bb[5]-bb[4]],loaded_depth_mm=depth,downloads=downloads,native_check=check,geometry=geom,files={p.name:receipt(p) for p in assets}))
 (D/'models.json').write_text(json.dumps(models,indent=2)+'\n');(B/'models.json').write_text(json.dumps(models,indent=2)+'\n')
 assets=json.loads((R/'publication/release-assets.json').read_text());mapping=json.loads((R/'publication/release-downloads.json').read_text())
 for p in out.iterdir():
  if p.is_file():assets[p.name]=receipt(p);mapping['key-fan/final/'+p.name]=REL+p.name
 (R/'publication/release-assets.json').write_text(json.dumps(assets,indent=2)+'\n');(R/'publication/release-downloads.json').write_text(json.dumps(mapping,indent=2)+'\n')
 p=R/'docs/gallery/release-downloads.js';before,tail=p.read_text().split('const links=',1);_,end=json.JSONDecoder().raw_decode(tail);p.write_text(before+'const links='+json.dumps(mapping,separators=(',',':'))+tail[end:])
 apply();refresh();print('Prepared final models:',len(models),'release assets:',len(list(out.iterdir())))
def refresh():
 (R/'publication/final-racks-v1-additions.json').write_text(json.dumps({p.relative_to(R).as_posix():receipt(p) for folder in (D,B,S,R/'docs/final') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts},indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--build',type=Path);p.add_argument('--out',type=Path);p.add_argument('--refresh',action='store_true');a=p.parse_args()
 if a.build:prepare(a.build,a.out)
 elif a.refresh:refresh()
 else:apply()
