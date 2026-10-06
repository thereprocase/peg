"""Publish HX02's reviewed artifacts and register it in the Repro catalog."""
from pathlib import Path
import json,hashlib,shutil,re
R=Path(__file__).resolve().parents[1];B=R/'bench/reviews/canted-hex-keys-v1/HX02';D=R/'docs/gallery/canted-hex-keys';P=R/'docs/gallery/current-pegs'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def receipt(p):return dict(sha256=sha(p),bytes=p.stat().st_size)
r=json.loads((B/'report.json').read_text());prefix=r['prefix']
evidence={name.removesuffix('.json'):json.loads((B/name).read_text()) for name in ['report.json','print-geometry.json','installation-screen.json','stiffness.json','toolpaths.json']}
f=evidence['stiffness'];t=evidence['toolpaths'];g=evidence['print-geometry']
assert f['passed'] and g['passed'] and evidence['installation-screen']['pass']
assert r['files'][r['assets']['installed_step']]['sha256']==f['inputs']['step']==evidence['installation-screen']['input_sha256']
assert f['inputs']['spec']==sha(B/(prefix+'__fea-spec.json'))
assert t['input_stl_sha256']==g['inputs']['print_stl']==sha(B/r['assets']['print_stl'])
assert all(v['maximum'][1]<.15 for k,v in t['features'].items() if k in ['Support','Support interface'])
# Four sub-0.02 mm mouth transitions are classified as overhang wall by Orca.
# Native face-angle screening passes; bound these explicitly in the sliced evidence.
assert t['features'].get('Overhang wall',{}).get('body_max_move_mm',0)<.02
assert t['features'].get('Overhang wall',{}).get('body_side_filament_mm',0)<.002
evidence['physical_tests']='Pending'
for name in ['installed.glb','loaded.glb','print.glb','toolpaths.svg',r['assets']['print_stl']]:shutil.copyfile(B/name,D/name)
(D/'checks.json').write_text(json.dumps(evidence,indent=2)+'\n')
loads=f['cases'][0]['loads'];support=sum(t['features'].get(k,{}).get('grams',0) for k in ['Support','Support interface'])
footer=f'<footer id="review-summary"><p>5 N solid-ASA stiffness screen: {loads[0]["deflection_at_load_mm"]:.3f} mm sideways, {loads[1]["deflection_at_load_mm"]:.3f} mm down. Nominal mesh: 5 mm. Printed strength and mesh convergence remain unqualified.</p><p>Local P1S / PolyLite ASA slice: {t["time"]}, approximately {t["extrusion_grams"]:.0f} g, including {support:.2f} g of peg supports. Supports remain behind the mounting face. Reslice the print-oriented STL for your printer and filament.</p></footer>'
p=D/'index.html';p.write_text(re.sub(r'<footer id="review-summary">.*?</footer>',footer,p.read_text(),flags=re.S))
assets={}
for role in ['installed','print']:
 for suffix in ['glb','stl']:
  name=prefix+'__'+role+'.'+suffix
  shutil.copyfile(B/(role+'.glb') if suffix=='glb' else B/r['assets'][role+'_stl'],P/name)
  assets[role+'_'+suffix]=name
 assets[role+'_png']=prefix+'__'+role+'.png'
assets.update(preview_png=assets['installed_png'],checks=prefix+'__checks.json',cad_bundle='https://github.com/thereprocase/peg/releases/download/canted-hex-keys-v1-2026-10-06/canted-hex-keys__v1__cad-source-and-review.zip')
shutil.copyfile(D/'checks.json',P/assets['checks'])
part=dict(id='HX02',name='Full-depth canted metric hex-key rack',family='solder-modules',version='v1',kind='mounted',new_design=True,fit_label='PF02 #9 / PF07 #5',pose='right-cheek',installed_camera_orbit='25deg 65deg auto',print_bounds_mm=r['print_bounds_mm'],assets=assets,extra_downloads=[dict(label='Loaded view, key lengths and review',url='../canted-hex-keys/?v=1')],notes=dict(orientation='Print on the broad right cheek. Full-depth blind sockets lean 30° outward from vertical. The bends and short arms remain exposed and slope toward the desk.',upper_pegs='Original PF02 #9 upper hooks retained. Complete front-body installation screening follows the nominal reference route.',supports='Local P1S / PolyLite ASA toolpaths reviewed. Pointed socket roofs grow in the cheek print; peg supports are accessible behind the mounting face.',mount='201.2 mm wide, eight grid cells and two mounting columns. PF07 #5 hoops are oriented for flex within the print layers.',qualification='Nine sizes: 1.5, 2, 2.5, 3, 4, 5, 6, 8 and 10 mm. Owner straight lengths; 4 mm interpolated to 140 mm. CAD, sampled axial withdrawal, print geometry, installation and solid-ASA stiffness screens pass. Physical print, fit, handling and support release remain pending.',status='Toolpaths reviewed · physical test pending'),credit='')
p=P/'catalog.json';catalog=json.loads(p.read_text());catalog['parts']=[part]+[row for row in catalog['parts'] if row['id']!='HX02'];catalog['expected_count']=len(catalog['parts']);p.write_text(json.dumps(catalog,indent=2)+'\n')
p=P/'index.html';p.write_text(p.read_text().replace('45 holders and accessories','46 holders and accessories'))
(R/'publication/canted-hex-keys-v1-additions.json').write_text(json.dumps({p.name:receipt(p) for p in D.iterdir() if p.is_file()},indent=2)+'\n')
# Collection PNG receipts are refreshed after the browser preview render.
p=R/'publication/current-pegs-v1-additions.json';entries=json.loads(p.read_text())
for path in [P/'index.html',P/'catalog.json']+list(P.glob(prefix+'*')):entries[path.name]=receipt(path)
p.write_text(json.dumps(entries,indent=2)+'\n')
print('HX02 registered in Repro; render its previews and refresh their receipts.')
