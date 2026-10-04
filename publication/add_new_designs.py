"""Append frozen session designs to the gallery; never change modeled geometry."""
from pathlib import Path
import hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[1];B=R/'bench/reviews/gallery-new-designs-v1';PAGE=R/'docs/gallery/current-pegs';SNAP=R/'bench/source/gallery_new_designs_v1/snapshot';TAG='new-designs-v1-2026-10-04';BASE='https://github.com/thereprocase/peg/releases/download/'+TAG+'/'
def digest(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
def main(release):
 selection=json.loads((B/'SELECTED.json').read_text());catalog=json.loads((PAGE/'catalog.json').read_text());receipts=json.loads((R/'publication/current-pegs-v1-additions.json').read_text());moves=json.loads((R/'publication/release-downloads.json').read_text());native_receipts=json.loads((R/'publication/release-assets.json').read_text());release.mkdir(parents=True,exist_ok=True);new=[];release_names=[]
 def site(src,name):shutil.copy2(src,PAGE/name);receipts[name]=digest(PAGE/name);return name
 def native(src,name):

  if src.resolve()!=(release/name).resolve():shutil.copy2(src,release/name)
  native_receipts[name]=digest(release/name);receipts[name]=native_receipts[name];moves['current-pegs/'+name]=BASE+name;release_names.append(name);return BASE+name
 for p in selection['products']:
  folder=B/p['id'];prefix=p['prefix'];original=SNAP/p['origin_folder'];assets={}
  for role in ['installed_stl','print_stl','installed_glb','print_glb']:
   src=folder/p['assets'][role];suffix=('print-'+p['pose'] if role=='print_stl' else role.split('_')[0])+src.suffix;assets[role]=site(src,prefix+'__'+suffix)
  image=original/('empty.png' if (original/'empty.png').exists() else prefix+'__empty.png')
  if p['kind']=='accessory':image=original/'part-solder-drip-tray__v12__upright__fit-pf02c9-hoop5__loaded.png'
  assets['preview_png']=site(image,prefix+'__preview.png');assets['installed_png']=assets['preview_png']
  image=original/('print-pose.png' if (original/'print-pose.png').exists() else 'print.png' if (original/'print.png').exists() else prefix+'__print.png')
  if p['kind']=='accessory':image=original/'part-solder-drip-tray__v12__upright__fit-pf02c9-hoop5__loaded.png'
  assets['print_png']=site(image,prefix+'__print-preview.png')
  for role in ['installed_step','print_step']:
   if role in p['assets']:assets[role]=native(folder/p['assets'][role],p['assets'][role])
  extras=[]
  for e in p.get('extra_downloads',[]):
   f=folder/e['file'];url=native(f,f.name) if f.suffix=='.step' else site(f,f.name);extras.append({'label':e['label'],'url':url})
  if p['kind']=='accessory':
   f=original/(prefix+'__installed.step');extras.append({'label':'Filled vase template STEP · installed coordinates','url':native(f,f.name)})
  checks={'id':p['id'],'kind':p['kind'],'independent_mesh_checks':p['checks'],'native_checks':json.loads((folder/'native-checks.json').read_text()),'recorded_geometry_checks':json.loads((folder/p['geometry_checks_file']).read_text()),'source_metadata':json.loads((folder/p['origin_metadata']).read_text()),'scope':'Frozen CAD review; physical qualification and stiffness limits are separate.'}
  (folder/'public-checks.json').write_text(json.dumps(checks,indent=2)+'\n');assets['checks']=site(folder/'public-checks.json',prefix+'__gallery-checks.json')
  pose=p['pose'];notes={'orientation':'Print on the right cheek; the STL is already oriented on the bed.' if pose=='right-cheek' else 'Print upright on the flat bottom; the STL is already oriented on the bed.','upper_pegs':'Original PF02 #9 upper hooks retained. Upper body extensions are described in the matching frozen geometry checks. Nominal body screens do not certify interference-fit installation.','supports':'Inspect local peg supports and actual toolpaths with your material and printer settings.','mount':'PF02 #9 upper hooks and PF07 #5 lower hoops, with clipped roots and flex aligned within the print layers.','qualification':'Recorded CAD/mesh checks and native STEP read-back pass. Physical fit, retention and support release are unqualified.'}
  status='CAD prototype'
  if p['id']=='SPOOL-V14':
   notes['orientation']+=' Open curved-bottom storage, with an 8 mm lift then pull forward. Provisional 40–65 mm spool diameter and 8–34 mm overall width.'
   notes['qualification']='Geometry and nominal up/out paths pass. Downward stiffness target missed: 0.577 mm at 5 N against a 0.5 mm target. Unsliced prototype; physical seating, narrow-spool lean and bump retention remain untested.';status='Prototype · stiffness target missed'
  elif p['id']=='TW-GUIDED-V5':
   notes['orientation']+=' Print FOUR separate fins from the fin STL, then bond their feet into the blind seats.'
   notes['upper_pegs']='Raised top rail and open R6 roof guides; 20° inward slope, taller fins, 28 mm stack spacing and extra tip room. All four sampled pickup routes clear three stored neighbors; natural rightward return remains a physical handling test.'
   notes['qualification']='Geometry, sampled routes and stiffness checks pass. Local ASA organic-support toolpaths were reviewed; no physical curved-guide test or launch is recorded. Reslice for your setup.';status='Toolpaths reviewed · physical test pending'
  elif p['id']=='TOOL-FUNNEL-V3':
   notes['orientation']+=' One rectangular tapered through-hole holds Knipex flush cuts or Klein strippers edge-on; R2 exterior rounds and 0.6 mm rim breaks.'
   notes['supports']='Review rear-peg supports and the short 45° internal transition. Preserve the open bottom. Native installed STEP is provided; use the oriented STL for printing.'
   notes['qualification']='Nominal and +10° tool poses, 110 mm vertical pickup paths, geometry and stiffness checks pass. Unsliced; physical settling, rattle and support release remain untested.'
  elif p['id']=='BRAID-V12':
   notes['qualification']='CAD and local slicing checks pass. Owner photos show a cyan holder mounted and carrying a solder spool; physical fit force, loads and bump retention are not measured.';status='Photographed mounted · measured fit pending'
  elif p['id']=='DRIP-TRAY-V12':
   notes['orientation']+=' Deep side webs, front finger scallop and removable vase-mode liner. Liner is a separate print.'
   notes['qualification']='Tray, liner seat and lift-out CAD checks pass; local ASA slicing was reviewed. Physical tray/liner fit and load testing remain unconfirmed.';status='Toolpaths reviewed · physical fit pending'
  else:
   notes={'orientation':'SPIRAL VASE MODE REQUIRED. The print STL/STEP is intentionally a FILLED template: use one spiral perimeter, zero infill and zero top layers. The reviewed liner used 0.6 mm wall width and a 1 mm bottom. The installed 3D view is the hollow in-use model; the thumbnail shows it in its matching tray.','upper_pegs':'No pegs: this is a removable liner for the v12 drip tray.','supports':'Print separately upright, without supports, using a reviewed vase-mode setup. Ordinary solid slicing would produce a filled block.','mount':'Loose accessory. Lift the front 6.4 mm, then pull forward from the matching v12 tray.','qualification':'Hollow seat/removal and filled-template CAD checks pass; local vase-mode toolpaths were reviewed. Physical liner fit is unconfirmed.'};status='Vase-mode accessory'
  notes['status']=status
  bundle=release/(prefix+'__cad-source-and-review.zip')
  with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   for rel in p['source_paths']:z.write(SNAP/rel,rel)
   for f in folder.iterdir():
    if f.is_file():z.write(f,'gallery-review/'+f.name)
   z.writestr('README.txt',p['name']+'\n\n'+ '\n\n'.join(notes.values())+'\n\nFrozen source/input/evidence files retain their original bench/ layout. Geometry sources use FreeCAD Python and numpy. Source-side scripts and historical notes can reference private scan/render overlays or excluded machine profiles; these are not included or claimed reproducible. No raw photos/scans or printer job is included. See native CAD and exact geometry checks; review support settings and physical handling before use.\n')
  assets['cad_bundle']=native(bundle,bundle.name)
  new.append({'id':p['id'],'name':p['name'],'family':p['family'],'version':p['version'],'kind':p['kind'],'new_design':True,'fit_label':'Removable accessory · no pegs' if p['kind']=='accessory' else 'PF02 #9 / PF07 #5','pose':pose,'print_bounds_mm':p['print_bounds_mm'],'assets':assets,'extra_downloads':extras,'notes':notes,'credit':''})
 old=[p for p in catalog['parts'] if p['id'] not in {q['id'] for q in new}];catalog.update(parts=new+old,expected_count=len(new)+len(old),build_note='October 4, 2026 · Six new session designs plus 38 remounted gallery parts. Test status is stated per design.');(PAGE/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
 for p in [PAGE/'catalog.json',PAGE/'index.html',PAGE/'current-pegs.js',PAGE/'current-pegs.css']:receipts[p.name]=digest(p)
 for path,data in [('publication/current-pegs-v1-additions.json',receipts),('publication/release-downloads.json',moves),('publication/release-assets.json',native_receipts)]:(R/path).write_text(json.dumps(data,indent=2)+'\n')
 p=R/'docs/gallery/release-downloads.js';before,tail=p.read_text().split('const links=',1);_,after=tail.split(';function fix(node)',1);p.write_text(before+'const links='+json.dumps(moves,separators=(',',':'))+';function fix(node)'+after)
 (release/'release-files.json').write_text(json.dumps(release_names,indent=2)+'\n');print('Added',len(new),'designs;',len(release_names),'release assets; catalog',catalog['expected_count'])
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('release',type=Path);main(a.parse_args().release)
