"""Check current HX05 finished-model publication and exact evidence scope."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];B=R/'bench/reviews/hx05-finished-v1'
for name,row in json.loads((R/'publication/hx05-finished-v1.json').read_text()).items():
 p=R/name;assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],name
release=json.loads((B/'release.json').read_text());assets=json.loads((R/'publication/release-assets.json').read_text());links=json.loads((R/'publication/release-downloads.json').read_text())
assert len(release['models'])==3
for name,row in release['assets'].items():
 assert assets[name]==row and links['key-fan/finished/'+name].endswith('/'+release['release']+'/'+name)
for m in release['models']:
 ident=m['id'];draft=json.loads((B/(ident+'-draft-check.json')).read_text());mods=json.loads((B/(ident+'-modifier-check.json')).read_text());step=json.loads((B/(ident+'-step-check.json')).read_text());sliced=json.loads((B/(ident+'-slice-review.json')).read_text());paths=json.loads((B/(ident+'-toolpaths.json')).read_text())
 assert draft['passed'] and draft['tested_cutters_reused'] and draft['maximum_checked_uncut_housing_overhang_deg']<=30.0001
 assert mods['passed'] and mods['body_shape_unchanged'] and mods['print_rotation_unchanged'] and mods['modifier_count']==4
 assert mods['rotation']==draft['rotation'] and mods['translation']==draft['translation']
 assert step['passed'] and step['valid_single_solid'] and step['maximum_sample_surface_distance_mm']<1e-5
 assert step['sha256']==assets[m['step']]['sha256']
 assert sliced['exit_code']==0 and sliced['slicer_mesh_repairs']==0 and sliced['modifier_count']==4 and sliced['modifier_infill_percent']==100
 assert sliced['project_sha256']==assets[m['project']]['sha256']
 assert paths['bed_centerline_screen_passed'] and paths['socket_core_screen_passed']
assert json.loads((B/'pinch-check.json').read_text())['passed']
assert json.loads((B/'tool-access-check.json').read_text())['passed']
page=(R/'docs/gallery/key-fan/finished/index.html').read_text()
assert page.count('id="HX05')==3 and '100% infill' in page and '12% gyroid' in page
assert 'physical load' in page and 'Torx' in page and 'provisional' in page
assert sum(p.stat().st_size for p in (R/'docs').rglob('*') if p.is_file())<1024**3
print('HX05 finished: fixed pose/outside, tested cutters, native STEP, four solid modifiers, Orca and bed/socket screens, pinch access and immutable assets PASS')
