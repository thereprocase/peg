"""Package and register the completed extended HX04 fan audit and its films.
Explicit public allowlists only; never printer files, credentials, runtime binaries or caches.
"""
from pathlib import Path
import argparse,json,hashlib,zipfile,shutil,io,re,tarfile
from PIL import Image
R=Path(__file__).resolve().parents[1];B=R/'bench/reviews/key-fan-audit-v1';D=R/'docs/gallery/key-fan/studies';TAG='key-fan-engineering-v1-2026-10-10';REL=f'https://github.com/thereprocase/peg/releases/download/{TAG}/'
def receipt(p):return dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def prepare(out):
 out.mkdir(parents=True,exist_ok=True);media=D/'media';media.mkdir(exist_ok=True);films=[]
 with zipfile.ZipFile(R/'.local-runtime/hx04-audit/completed-films.zip') as z:
  names=[n for n in z.namelist() if n.endswith('/receipt.json')];assert len(names)==60,names
  for name in sorted(names):
   q=json.loads(z.read(name));folder=name.rsplit('/',1)[0]
   assert re.fullmatch(r'[a-zA-Z0-9_.-]+',q['id'])
   for file,h in q['files'].items():
    blob=z.read(folder+'/'+file);assert hashlib.sha256(blob).hexdigest()==h['sha256'] and len(blob)==h['bytes']
    if file.endswith(('.gif','.webm')):(out/('HX04-'+file)).write_bytes(blob)
   webm='HX04-'+q['id']+'.webm';shutil.copyfile(out/webm,media/webm)
   image=Image.open(io.BytesIO(z.read(folder+'/poster.png'))).convert('RGB');poster=q['id']+'.jpg';image.save(media/poster,quality=83,optimize=True)
   films.append(dict(id=q['id'],title=q['title'],caption=q['caption'],mode=q['mode'],video='media/'+webm,poster='media/'+poster,gif=REL+'HX04-'+q['id']+'.gif',amplification=q['amplification'],frames=q['frames'],fps=q['fps'],provenance=q))
 (D/'films.json').write_text(json.dumps(films,indent=2)+'\n');(B/'film-manifest.json').write_text(json.dumps(films,indent=2)+'\n')
 # Preserve full original source/CAD bundle and supply its missing frozen mount dependencies.
 source=R/'bench/source/key_fan_audit_v1';paths=[p for p in source.iterdir() if p.is_file() and p.suffix in ['.py','.cjs','.js','.md','.json']]+[p for p in B.iterdir() if p.is_file() and p.name!='public-package-check.json' and p.suffix in ['.json','.svg','.md','.3mf','.step','.stl']]+[p for p in D.rglob('*') if p.is_file() and ('media' not in p.parts or p.suffix=='.jpg')]
 snapshot=R/'bench/source/gallery_current_mounts_v1/station_snapshot';paths += list((snapshot/'source').glob('*.py'))+list((snapshot/'reference').glob('*'))
 for p in paths:assert '__pycache__' not in p.parts and p.suffix not in ['.pyc','.gcode'] and 'private' not in p.name
 entries={p.relative_to(R).as_posix():p.read_bytes() for p in paths}
 bundled_films=[dict(q,video=REL+Path(q['video']).name) for q in films]
 entries['docs/gallery/key-fan/studies/films.json']=(json.dumps(bundled_films,indent=2)+'\n').encode()
 with zipfile.ZipFile(R/'.local-runtime/hx04-audit/release.zip') as original:
  for name in original.namelist():
   if name.startswith('bench/'):
    blob=original.read(name)
    if name in entries:assert entries[name]==blob, name
    else:entries[name]=blob
 manifest={n:dict(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)) for n,data in entries.items()};entries['MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
 bundle='HX04-engineering-v1__sources-fields-and-review.zip'
 with zipfile.ZipFile(out/bundle,'w',zipfile.ZIP_DEFLATED) as z:
  for name,data in sorted(entries.items()):z.writestr(name,data)
 project='HX04-v2__uncompensated-brace-project__reslice.3mf';shutil.copyfile(B/project,out/project)
 for suffix in ['.stl','.step']:
  name='HX04-fit-v6__3mm-5mm__fan-angle__print'+suffix;shutil.copyfile(B/name,out/name)
 (B/'public-package-check.json').write_text(json.dumps(dict(bundle=bundle,asset_count=len(list(out.iterdir())),film_count=len(films),native_geometry_unchanged=True,private_printer_artifacts_included=False,files={p.name:receipt(p) for p in sorted(out.iterdir()) if p.is_file()}),indent=2)+'\n')
 assets=json.loads((R/'publication/release-assets.json').read_text());downloads=json.loads((R/'publication/release-downloads.json').read_text())
 for p in out.iterdir():
  if p.is_file():assets[p.name]=receipt(p);downloads['key-fan/studies/'+p.name]=REL+p.name
 (R/'publication/release-assets.json').write_text(json.dumps(assets,indent=2)+'\n');(R/'publication/release-downloads.json').write_text(json.dumps(downloads,indent=2)+'\n')
 js=R/'docs/gallery/release-downloads.js';before,tail=js.read_text().split('const links=',1);_,end=json.JSONDecoder().raw_decode(tail);js.write_text(before+'const links='+json.dumps(downloads,separators=(',',':'))+tail[end:])
 apply()
 print('Prepared',len(films),'GIF/WebM pairs and public review package')
def apply():
 p=R/'docs/gallery/key-fan/index.html';text=p.read_text();banner='<section id="engineering-review"><h2>Extended engineering studies</h2><p><strong><a href="studies/">Open the interactive motion and FEA lab</a></strong> · <a href="studies/report.html">Full numerical report</a></p><p>All 26 tool paths, 25 initial load/fixture cases, exaggerated computed flexure, stress maps, full-rack loading/unloading and locking-hoop pinch. The deeper review finds front-host collision on the old assumed swing and shows why mouth forces do not represent loads at the handles. These are prototype studies, not a printed load rating.</p><p><a href="'+REL+'HX04-engineering-v1__sources-fields-and-review.zip">Sources, native CAD, display fields and review ZIP</a> · <a href="'+REL+'HX04-v2__uncompensated-brace-project__reslice.3mf">Corrected unscaled v2 brace project—reslice with compensation once</a></p></section>'
 text=re.sub(r'<section id="engineering-review">.*?</section>','',text,flags=re.S);text=text.replace('</header>','</header>'+banner,1)
 # Keep the actual 3/5 mm trials active; 7 mm is not part of the owner's set.
 text=text.replace('Three sizes, five lettered fits per size','Two sizes, five lettered fits per size');text=text.replace('3, 5 and 7 mm hexes','3 and 5 mm hexes').replace('Three connected coupons','Two requested test sizes').replace('Download all three spectra on one plate','Historical three-size plate (includes unused 7 mm trial)')
 text=text.replace(' · <a href="fit-v6/HX05-fit-v6-7mm__fan-angle__print.stl" download>7 mm coupon STL</a>','')
 text=text.replace('<th>7 mm bore AF</th>','').replace('<td>7.20 mm</td>','').replace('<td>7.30 mm</td>','').replace('<td>7.38 mm</td>','').replace('<td>7.46 mm</td>','').replace('<td>7.56 mm</td>','')
 text=text.replace('3 mm = _, 5 mm = _, 7 mm = _','3 mm = _, 5 mm = _').replace('Length','Length').replace('</p></p>','</p>')
 text=text.replace('https://github.com/thereprocase/peg/releases/download/key-fan-v2-2026-10-08/part-hx04__v2__left-cheek__fit-pf02c9-hoop5__hx04_solid-zones.3mf',REL+'HX04-v2__uncompensated-brace-project__reslice.3mf')
 text=text.replace('fit-v6/HX05-fit-v6__three-spectra__print.stl','fit-requested-3-5/HX04-fit-v6__3mm-5mm__fan-angle__print.stl').replace('Historical three-size plate (includes unused 7 mm trial)','Download the 3/5 mm spectra on one plate').replace('src="fit-v6/coupon.glb"','src="fit-requested-3-5/coupon.glb"').replace('Three connected coupons with five lettered hex slots each','Two fan-angle coupons with five lettered hex slots each')
 text=re.sub(r'The <strong>7 mm trial.*?layout\.', '',text)
 text=text.replace('and 56 mm for 7 mm, ','').replace('40 mm for 3 and 5 mm, ','40 mm for 3 and 5 mm, ')
 text=text.replace('Slicing and physical fit remain pending; no overnight job has been submitted from this box, which has no configured printer connector or local owner-profile slicer.', 'The supported 3/5 mm Orca job was submitted through the Bambu bridge on physical AMS slot 3, then paused before layer 1 on a filament-feed error. No new physical fit or winning letters are established.')
 text=text.replace('Install swing over all 90 pegs:', 'Historical rear-peg-only install swing over all 90 pegs (the new whole-host check finds collision):')
 text=text.replace('seated clear, hoops snap,', 'nominal seated bearings clear, intentional hoop overlap modeled,')
 text=text.replace('swing the bottom onto the board until the hoops click.', 'the intended final motion swings the bottom toward the board. Whole-rack clearance and physical hoop recovery remain unqualified; see the installation audit.')
 p.write_text(text,encoding='utf-8',newline='\n')
 p=R/'docs/gallery/current-pegs/catalog.json';catalog=json.loads(p.read_text());q=next(q for q in catalog['parts'] if q['id']=='HX04');q['notes']['upper_pegs']=q['notes']['upper_pegs'].replace('Sampled install swing passes.','Historical rear-peg-only swing screen passes; the whole-host audit finds collision on that assumed pivot.');q['notes']['status']='Engineering review · physical fit revision pending';q['notes']['qualification']='Extended FEA and motion studies of archived v2. Whole-host collision found on assumed install pivot; revised 3/5 mm fit trials remain pending. Physical loads and snap recovery remain unqualified. Simulations are not a printed load or snap rating.';q['extra_downloads']=[dict(label='Interactive engineering lab and full report',url='../key-fan/studies/'),dict(label='3/5 mm fit spectra',url='../key-fan/?v=6#fit-coupon-v6')];p.write_text(json.dumps(catalog,indent=2)+'\n')
 p=R/'publication/current-pegs-v1-additions.json';d=json.loads(p.read_text());d['catalog.json']=receipt(R/'docs/gallery/current-pegs/catalog.json');p.write_text(json.dumps(d,indent=2)+'\n')
 folder=R/'docs/gallery/key-fan';(R/'publication/key-fan-v2-additions.json').write_text(json.dumps({q.name:receipt(q) for q in folder.iterdir() if q.is_file() and q.name!='part-hx04__v1__left-cheek__fit-pf02c9-hoop5__print.stl'},indent=2)+'\n')
 (R/'publication/key-fan-engineering-v1-additions.json').write_text(json.dumps({q.relative_to(R).as_posix():receipt(q) for folder in [D,R/'docs/gallery/key-fan/fit-requested-3-5'] for q in folder.rglob('*') if q.is_file()},indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path);a=p.parse_args();prepare(a.out) if a.out else apply()
