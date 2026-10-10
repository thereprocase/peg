"""Publish HX04 v2 (three-tier key fan, full peg grid, brace-type solid zones) over the v1 page and catalog entry.

v1 stays available as history: its print STL remains on the page and its CAD bundle stays on the v1 release.

Inputs: bench/reviews/key-fan-v1/HX04 (written by bench/source/key_fan_v1/tools/evidence.py). Native CAD, the
solid-zone 3MF project and the source bundle are release assets (package_key_fan.py, tag below).
"""
from pathlib import Path
import json, hashlib, shutil, html as H
R = Path(__file__).resolve().parents[1]
B = R/'bench/reviews/key-fan-v2/HX04'; D = R/'docs/gallery/key-fan'; P = R/'docs/gallery/current-pegs'
TAG = 'key-fan-v2-2026-10-08'
BUNDLE = 'key-fan__v2__cad-source-and-review.zip'
V1_STL = 'part-hx04__v1__left-cheek__fit-pf02c9-hoop5__print.stl'
V1_BUNDLE = 'https://github.com/thereprocase/peg/releases/download/key-fan-v1-2026-10-08/key-fan__v1__cad-source-and-review.zip'
REL = f'https://github.com/thereprocase/peg/releases/download/{TAG}/'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def receipt(p): return dict(sha256=sha(p), bytes=p.stat().st_size)


r = json.loads((B/'report.json').read_text()); prefix = r['prefix']; A = r['assets']
ev = {n.removesuffix('.json'): json.loads((B/n).read_text(encoding='utf-8')) for n in
      ['report.json', 'exact-check.json', 'stiffness.json', 'print-geometry.json', 'slice-summary.json', 'coupon.json', 'install-swing.json']}
ex, fe, sl = ev['exact-check'], ev['stiffness'], ev['slice-summary']
assert ex['all_routes_ok'] and ex['stored_ok'] and ex['straighten_ok'] and min(ex['floors_mm']) >= 3
sw = ev['install-swing']; assert sw['passed'] and sw['pegs'] == dict(hooks=9, locking=9, bearing=72)
assert fe['inputs']['step'] == r['files'][A['installed.step']]['sha256']
assert sl['plain']['input_sha256'] == sl['solid_zones']['input_sha256'] == r['files'][A['print.stl']]['sha256']
ev['physical_tests'] = 'Pending'
D.mkdir(parents=True, exist_ok=True)
for q in D.glob('part-hx04__v1__*coupon*'):          # v1's coupon is superseded (its peg column changed)
    q.unlink()
for name in ['installed.glb', 'loaded.glb', 'print.glb', A['print.stl'], A['coupon_print.stl']]:
    shutil.copyfile(B/name, D/name)
(D/'checks.json').write_text(json.dumps(ev, indent=1)+'\n', encoding='utf-8', newline='\n')
(D/'review.js').write_text("""const viewer=document.querySelector('model-viewer');
document.querySelectorAll('[data-mode]').forEach(button=>button.addEventListener('click',()=>{
  viewer.src=button.dataset.mode+'.glb?v=2';
  document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
}));
viewer.addEventListener('load',async()=>{
  await viewer.updateFraming();
  viewer.cameraTarget='auto auto auto';
  viewer.cameraOrbit=viewer.getAttribute('src').startsWith('print.glb')?'35deg 60deg 115%':'30deg 70deg 115%';
  viewer.jumpCameraToGoal();
});
""", encoding='utf-8', newline='\n')

SET = {'hex': 'Hex L-key', 'torx': 'Torx L-key', 'tee': 'T-handle'}
order = {'hex': 0, 'torx': 1, 'tee': 2}
rows = ''.join(
    f"<tr><td>{SET[s['set']]}</td><td>{H.escape(s['size'])}{'' if s['set'] == 'torx' else ' mm'}</td><td>{s['seat_depth_mm']:.0f} mm</td>"
    f"<td>{('hex-keyed, ±%g°' % s['turn_play_deg']) if s['keyed'] else ('set by eye' if s['set'] == 'tee' else 'gravity')}</td></tr>"
    for s in sorted(r['sockets'], key=lambda s: order[s['set']]))
loads = {l['id']: l for cs in fe['cases'] for l in cs['loads']}
weak = min(loads.values(), key=lambda l: l['stiffness_N_per_mm'])
html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Three-tier key fan · Repro</title><link rel="stylesheet" href="../bespoke-tools/style.css"><script type="module" src="../vendor/model-viewer.min.js"></script><script defer src="../../viewer/workbench.js"></script><script defer src="review.js?v=2"></script></head>
<body><main><header><nav><a href="../../">Product groups</a><a href="../current-pegs/?family=repro">Repro collection</a></nav><h1>Three-tier key fan</h1><p>One pegboard rack for three sets, stadium style. Metric hex L-keys 1.5–10 mm stand at the back, seated deeper toward the long keys so the tall ones sit low. Husky Torx T10–T50 make the middle row. Bondhus T-handles 2–10 mm fan out in front, their grips evenly spaced about 39 mm apart, with the two smallest sunk below the hex keys’ short arms.</p><p class="status">HX04 v2 · prototype. Physical print, peg fit, install, tool fit and seating under knocks remain pending. Print the fit coupon first.</p></header><article><model-viewer src="loaded.glb?v=2" camera-controls camera-orbit="30deg 70deg auto" interaction-prompt="none" alt="Pegboard rack with hex keys at the back, Torx keys in the middle and a fan of T-handles in front" style="height:600px"></model-viewer><nav aria-label="Model view"><button data-mode="loaded" aria-pressed="true">With tools</button><button data-mode="installed" aria-pressed="false">Empty</button><button data-mode="print" aria-pressed="false">Print pose</button></nav>
<h2>What changed in v2</h2><ul><li>A peg in every hole the plate covers: hook pegs every inch across the top row, locking hoops across the bottom row, and gravity-load pegs in the 72 holes between (9 columns × 10 rows). The reviewed peg profiles are unchanged; the back is now their 5.4 mm wall throughout. Hook the top row in, then swing the bottom onto the board until the hoops click.</li><li>The solid-infill helpers are braces: a solid web through each row of sockets, a short bulkhead at every socket and a disc round every peg root, instead of padded sleeves.</li></ul><h2>How the sockets hold the tools</h2><ul><li>Every seat is at least four times the key size. Long hex keys and the smallest T-handles get deeper seats so they sit lower.</li><li>Each L-key’s short arm points straight downhill, so a key dropped in at any turn swings to rest. T-handles have no preferred turn, so T3 and up sit in hex-keyed bores clocked to their grip turn.</li><li>Jiggling tools walk in, not out. Every bore has a short straight neck, then widens slightly toward a floor sloped 30° low on the side the tool’s own weight tips toward, so a tool pinched by its weight slides deeper instead of hanging.</li><li>To take a tool, straighten it, lift it out of its seat, then pull it forward. Every route clears the other tools and a 3″-deep shelf 2″ above.</li></ul>
<p>236 mm wide, on the nine-cell peg pattern (columns at ±101.6 mm) · {r["checks"]["depth_mm"]:.0f} mm from the board to the furthest tool · {r["print_bounds_mm"][2]:.0f} mm tall in the print, on its left end.</p>
<table><thead><tr><th>Tool</th><th>Size</th><th>Seat</th><th>Turn held by</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Printing</h2><ol><li><strong>Print the fit coupon first</strong> (<a href="{A["coupon_print.stl"]}" download>coupon STL</a>, plain 20%, about {sl["coupon_plain"]["grams"]:.0f} g / {sl["coupon_plain"]["time"]}). It is cut from the final model and prints the same way. The end slice hangs on the board from the top of the left peg column and holds Torx T10/T15, hex 1.5/2 and T-handles T2, T2.5 and T3; drop the tools in, knock the board, pull them out. The PEGS strip is the rest of that column down to the locking hoop, so you can feel the gravity-load pegs and the hoop snap. Blocks <em>T5 C</em> and <em>T5 F</em> key the T5 shaft to its corners and to its flats: the one that holds the bar at the right turn tells you how your handles are made. The full part assumes corners.</li><li><strong>Full part:</strong> open the <a href="{REL}{A["hx04_solid-zones.3mf"]}">Bambu Studio / OrcaSlicer project with solid-infill zones</a>. It is the body plus brace zones at 100% infill (socket row webs, socket bulkheads, peg roots), about {sl["solid_zones"]["grams"]:.0f} g / {sl["solid_zones"]["time"]}. A lighter alternative is the <a href="{A["print.stl"]}" download>print-oriented STL</a> at plain 20% infill, about {sl["plain"]["grams"]:.0f} g / {sl["plain"]["time"]}. Print it on its left end as oriented, with tree supports on the build plate only (they land under the peg hooks behind the mounting face).</li><li>ASA: use an enclosure and a 5 mm brim. Then paint the debossed size labels.</li></ol>
<p><a href="{REL}{BUNDLE}">Native CAD, source and checks (ZIP)</a> · <a href="checks.json">Review evidence</a></p><p class="history">v1 (two peg columns, padded solid sleeves): <a href="{V1_STL}" download>print STL</a> · <a href="{V1_BUNDLE}">v1 CAD bundle</a></p></article><footer id="review-summary"><p>Exact OCC check: all 26 tools store clear and come out clear in their resting lean; floors at least {min(ex["floors_mm"]):.1f} mm. Install swing over all 90 pegs: seated clear, hoops snap, bearing pegs graze the hole edges by at most {sw["worst_bearing_per_peg_mm3"]:.2f} mm³ each in the last degrees. Solid-ASA stiffness on the pegs alone: weakest case {H.escape(weak["id"])}, {weak["deflection_at_load_mm"]:.3f} mm ({weak["stiffness_N_per_mm"]:.0f} N/mm). Local P1S / ASA review slices only, no G-code; reslice for your printer and filament. Tool lengths are catalogue values, not measurements.</p></footer></main></body></html>
'''
(D/'index.html').write_text(html, encoding='utf-8', newline='\n')

assets = {}
for role in ['installed', 'print']:
    for suffix in ['glb', 'stl']:
        name = prefix+'__'+role+'.'+suffix
        shutil.copyfile(B/(role+'.glb') if suffix == 'glb' else B/A[role+'.stl'], P/name)
        assets[role+'_'+suffix] = name
    assets[role+'_png'] = prefix+'__'+role+'.png'
assets.update(preview_png=assets['installed_png'], checks=prefix+'__checks.json', cad_bundle=REL+BUNDLE)
shutil.copyfile(D/'checks.json', P/assets['checks'])
part = dict(id='HX04', name='Three-tier key fan: hex, Torx and T-handles', family='solder-modules', version='v2', kind='mounted', new_design=True,
            fit_label='PF02 #9 / PF07 #5', pose='left-cheek', installed_camera_orbit='30deg 70deg auto', print_bounds_mm=r['print_bounds_mm'], assets=assets,
            extra_downloads=[dict(label='Loaded view, fit coupon, brace-zone project, printing notes and v1 history', url='../key-fan/?v=2')],
            notes=dict(orientation="Print on the user's left end. Rails, webs and plate follow chamfer-in-Z, fillet-in-XY; socket roofs are pointed and floors print as walls or floors.",
                       upper_pegs='A peg in every covered hole: 9 PF02 #9 hooks across the top row, 9 PF07 #5 locking hoops across the bottom row, 72 gravity-load bearing pegs between; reviewed profiles mirrored for the left-end print (fit assumed equal). Sampled install swing passes.',
                       supports='Tree supports on the build plate only, mostly under the 90 pegs behind the mounting face; small label counters.',
                       mount='236 mm wide (ten cells shaved 8 mm a side); 9 peg columns at 25.4 mm pitch (±101.6 mm) by 10 rows.',
                       qualification=f'26 tools: hex 1.5–10, Torx T10–T50, Bondhus T-handles 2–10. Exact storage and withdrawal, install swing, floors, print geometry, solid-ASA stiffness and local slices pass. Physical print, fit, install and seating remain pending; print the fit coupon first.',
                       status='CAD checks pass · physical test pending'), credit='')
p = P/'catalog.json'; catalog = json.loads(p.read_text())
if not any(row['id'] == 'HX04' for row in catalog['parts']):
    catalog['expected_count'] += 1                      # a new entry, not a replacement
catalog['parts'] = [row for row in catalog['parts'] if row['id'] != 'HX04']+[part]
p.write_text(json.dumps(catalog, indent=2)+'\n', encoding='utf-8', newline='\n')
(R/'publication/key-fan-v2-additions.json').write_text(json.dumps({q.name: receipt(q) for q in sorted(D.iterdir()) if q.is_file() and q.name != V1_STL}, indent=2)+'\n', encoding='utf-8', newline='\n')
p = R/'publication/current-pegs-v1-additions.json'; entries = json.loads(p.read_text())
for path in [P/'catalog.json']+sorted(P.glob(prefix+'*')):
    if path.is_file():
        entries[path.name] = receipt(path)
p.write_text(json.dumps(entries, indent=2)+'\n', encoding='utf-8', newline='\n')
print('HX04 v2 published to its page and the catalog; render previews with PEG_PREVIEW_IDS=HX04 and refresh the receipts.')

# Keep the owner-tested fit revision prominent after regenerating this historical rack page.
from update_key_fan_fit_spectrum_v6 import apply as apply_fit_revision
apply_fit_revision(R/'.local-runtime/tee-fit-v6-release')
