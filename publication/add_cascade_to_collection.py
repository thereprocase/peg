"""Register the reviewed CF01 v2 cassette in the Repro holder catalog."""
from pathlib import Path
import json,shutil,hashlib
R=Path(__file__).resolve().parents[1];P=R/'docs/gallery/current-pegs';D=R/'docs/gallery/cascade-funnels';B=R/'bench/reviews/cascade-funnels-v2/CF01'
r=json.loads((B/'report.json').read_text());prefix=r['prefix'];assets={}
for role in ['installed','print']:
 for suffix in ['glb','stl']:
  name=prefix+'__'+role+'.'+suffix;target=P/name
  source=D/(role+'.glb') if suffix=='glb' else B/r['assets'][role+'_stl']
  if source.exists():shutil.copyfile(source,target)
  else:assert target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()==r['files'][name]['sha256']
  assets[role+'_'+suffix]=name
 assets[role+'_png']=prefix+'__'+role+'.png'
assets.update(preview_png=assets['installed_png'],checks=prefix+'__checks.json',cad_bundle='https://github.com/thereprocase/peg/releases/download/cascade-funnels-v2-2026-10-06/cascade-funnels__v2__cad-source-and-review.zip')
shutil.copyfile(D/'checks.json',P/assets['checks'])
part=dict(id='CF01',name='Cascading tool funnels',family='solder-modules',version='v2',kind='mounted',new_design=True,fit_label='PF02 #9 / PF07 #5',pose='upright',installed_camera_orbit='0deg 75deg auto',print_bounds_mm=r['print_bounds_mm'],assets=assets,extra_downloads=[dict(label='Detailed review and tool references',url='../cascade-funnels/?v=2')],notes=dict(orientation='Print upright on the common flat bottom. Three touching funnels at 25 mm centres; the right seat is highest, with 25.4 mm steps down toward the left. Plain funnel mouths.',upper_pegs='Original PF02 #9 upper hooks retained. Front-body installation screening follows the nominal reference route.',supports='Local P1S / PolyLite ASA toolpaths reviewed. Supports remain behind the mounting face. Reslice for your printer and filament.',mount='Shared 99.6 mm backplate with PF02 #9 hooks and PF07 #5 lower hoops; hoop flex stays within the print layers.',qualification='CAD, sampled tool withdrawal, adjoining-shell overlap, print geometry and a 4 mm mesh solid-ASA stiffness screen pass. Physical print, fit, handling and support release remain pending. Tool shapes are clearance envelopes.',status='Toolpaths reviewed · physical test pending'),credit='')
p=P/'catalog.json';catalog=json.loads(p.read_text());catalog['parts']=[part]+[row for row in catalog['parts'] if row['id']!='CF01'];catalog['expected_count']=len(catalog['parts']);catalog['build_note']='Per-model CAD, print orientation and physical test status are recorded with each design.';p.write_text(json.dumps(catalog,indent=2)+'\n')
print('Registered CF01 v2 in Repro bespoke; render CF01 previews and refresh collection receipts.')
