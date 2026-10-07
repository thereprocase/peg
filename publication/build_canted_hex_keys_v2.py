"""Publish HX02 v2 (finished, graduated organ-pipe rack) over the v1 page and catalog entry.

v1 stays available as history: its print STL remains on the page and its CAD bundle stays on the
v1 release. The page's generic media (installed/loaded/print GLB, toolpaths, checks) now show v2.
"""
from pathlib import Path
import json, hashlib, shutil, re
R = Path(__file__).resolve().parents[1]
B = R/'bench/reviews/canted-hex-keys-v2/HX02'; D = R/'docs/gallery/canted-hex-keys'; P = R/'docs/gallery/current-pegs'
TAG = 'canted-hex-keys-v2-2026-10-07'
BUNDLE = 'canted-hex-keys__v2__cad-source-and-review.zip'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def receipt(p): return dict(sha256=sha(p), bytes=p.stat().st_size)


r = json.loads((B/'report.json').read_text()); prefix = r['prefix']
evidence = {n.removesuffix('.json'): json.loads((B/n).read_text(encoding='utf-8')) for n in ['report.json', 'print-geometry.json', 'installation-screen.json', 'stiffness.json', 'toolpaths.json', 'slice-summary.json']}
f = evidence['stiffness']; t = evidence['toolpaths']; g = evidence['print-geometry']
assert f['passed'] and g['passed'] and evidence['installation-screen']['pass']
assert r['files'][r['assets']['installed_step']]['sha256'] == f['inputs']['step'] == evidence['installation-screen']['input_sha256']
assert t['input_stl_sha256'] == evidence['slice-summary']['input_sha256'] == g['inputs']['print_stl'] == sha(B/r['assets']['print_stl'])
evidence['physical_tests'] = 'Pending'
for name in ['installed.glb', 'loaded.glb', 'print.glb', 'toolpaths.svg', r['assets']['print_stl']]:
    shutil.copyfile(B/name, D/name)
(D/'checks.json').write_text(json.dumps(evidence, indent=2)+'\n', encoding='utf-8', newline='\n')

loads = f['cases'][0]['loads']; support = sum(t['features'].get(k, {}).get('grams', 0) for k in ['Support', 'Support interface'])
keys = r['tool_spec']['keys']
rows = ''.join(f'<tr><td>{k["across_flats"]:g} mm</td><td>{k["straight_length"]} mm{" · interpolated" if k["length_source"] != "owner" else ""}</td></tr>' for k in keys)
v1_stl = 'part-hx02__v1__right-cheek__fit-pf02c9-hoop5__print.stl'
html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Canted metric hex-key rack · Repro</title><link rel="stylesheet" href="../bespoke-tools/style.css"><script type="module" src="../vendor/model-viewer.min.js"></script><script defer src="../../viewer/workbench.js"></script><script defer src="review.js?v=2"></script></head>
<body><main><header><nav><a href="../../">Product groups</a><a href="../current-pegs/?family=repro">Repro collection</a></nav><h1>Canted metric hex-key rack</h1><p>Nine full-depth sockets lean 30° outward from vertical, each in its own fluted pipe sized to its key, like a rank of organ pipes. The long arms slide completely inside; the bends and short arms stay exposed, pointing toward the desk.</p><p class="status">HX02 v2 · prototype. Physical print, fit, handling and support release remain pending. The key references use the supplied straight lengths, with assumed bends and short arms.</p></header><article><model-viewer src="loaded.glb?v=2" camera-controls camera-orbit="25deg 65deg auto" interaction-prompt="none" alt="Nine metric hex keys in graduated fluted sockets angled outward from the pegboard" style="height:580px"></model-viewer><nav aria-label="Model view"><button data-mode="loaded" aria-pressed="true">With keys</button><button data-mode="installed" aria-pressed="false">Empty</button><button data-mode="print" aria-pressed="false">Print pose</button></nav><h2>What changed in v2</h2><ul><li>Graduated pipes: each socket wall is 3 mm round its bore, so the rack thins from the 10 mm pipe to the 1.5 mm pipe. {r["volume_mm3"]/1000:.0f} cm³ of solid model against 813 cm³ for v1.</li><li>A smooth falling curve under the pipes replaces the v1 staircase; the rack stands 8 mm further from the board so the curve can keep falling at the 10 mm end.</li><li>Size numerals on the top, each in a lane between V-reveals that continue the pipe valleys, and again on each pipe face below the key.</li><li>Droplet countersinks on every mouth, fillets wherever the print allows them, 50° chamfers round the bed cheek, inset V borders on both ends, and the upper opening at the left end closed by a flush plug.</li></ul><p>Every finish obeys the cheek print: no surface leans past 45° from vertical, holes keep pointed roofs, and the numerals are cut rising toward the print top so no letter has a flat ceiling.</p><p>201.2 mm wide · {r["finish"]["pipe_pitch_mm"]:.2f} mm between socket centres · two mounting columns.</p><p>Pull along the socket axis, upward and outward. The 10 mm key needs approximately 220 mm of axial travel to clear, moving 110 mm outward and 191 mm upward. Leave that path clear of nearby tools.</p><table><thead><tr><th>Key size</th><th>Straight arm / socket depth</th></tr></thead><tbody>{rows}</tbody></table><p>Sizes run from 1.5 mm on the left to 10 mm on the right when facing the board.</p><p><a href="{r["assets"]["print_stl"]}" download>Print-oriented STL (v2)</a> · <a href="https://github.com/thereprocase/peg/releases/download/{TAG}/{BUNDLE}">Native CAD, source and checks (ZIP)</a> · <a href="checks.json">Review evidence</a> · <a href="toolpaths.svg">Support layout</a></p><p class="history">v1 (blocky slab, stepped underside): <a href="{v1_stl}" download>print STL</a> · <a href="https://github.com/thereprocase/peg/releases/download/canted-hex-keys-v1-2026-10-06/canted-hex-keys__v1__cad-source-and-review.zip">v1 CAD bundle</a></p></article><footer id="review-summary"></footer></main></body></html>
'''
footer = f'<footer id="review-summary"><p>5 N solid-ASA stiffness screen: {loads[0]["deflection_at_load_mm"]:.3f} mm sideways, {loads[1]["deflection_at_load_mm"]:.3f} mm down. Nominal mesh: 5 mm. Printed strength and mesh convergence remain unqualified.</p><p>Local P1S / PolyLite ASA slice: {t["time"]}, approximately {t["extrusion_grams"]:.0f} g (v1: 345 g), including {support:.1f} g of support: peg supports behind the mounting face plus organic support the slicer sends to the engraved numerals; paint a support blocker over the numerals to avoid the latter. Reslice the print-oriented STL for your printer and filament.</p></footer>'
html = re.sub(r'<footer id="review-summary"></footer>', footer, html)
(D/'index.html').write_text(html, encoding='utf-8', newline='\n')
(D/'review.js').write_text((D/'review.js').read_text(encoding='utf-8').replace("'.glb?v=1'", "'.glb?v=2'"), encoding='utf-8', newline='\n')

assets = {}
for role in ['installed', 'print']:
    for suffix in ['glb', 'stl']:
        name = prefix+'__'+role+'.'+suffix
        shutil.copyfile(B/(role+'.glb') if suffix == 'glb' else B/r['assets'][role+'_stl'], P/name)
        assets[role+'_'+suffix] = name
    assets[role+'_png'] = prefix+'__'+role+'.png'
assets.update(preview_png=assets['installed_png'], checks=prefix+'__checks.json', cad_bundle=f'https://github.com/thereprocase/peg/releases/download/{TAG}/{BUNDLE}')
shutil.copyfile(D/'checks.json', P/assets['checks'])
part = dict(id='HX02', name='Full-depth canted metric hex-key rack', family='solder-modules', version='v2', kind='mounted', new_design=True,
            fit_label='PF02 #9 / PF07 #5', pose='right-cheek', installed_camera_orbit='25deg 65deg auto', print_bounds_mm=r['print_bounds_mm'], assets=assets,
            extra_downloads=[dict(label='Loaded view, key lengths, v2 notes and v1 history', url='../canted-hex-keys/?v=2')],
            notes=dict(orientation='Print on the broad right cheek. Graduated fluted pipes, one per key, lean 30° outward from vertical; every finish is shaped for this pose.',
                       upper_pegs='Original PF02 #9 upper hooks retained. Complete front-body installation screening follows the nominal reference route.',
                       supports='Body grows without supports: no face past 45°, pointed socket roofs, oblique-cut numerals. Peg supports are accessible behind the mounting face.',
                       mount='201.2 mm wide, eight grid cells and two mounting columns. PF07 #5 hoops are oriented for flex within the print layers.',
                       qualification=f'Nine sizes, 1.5–10 mm, with owner straight lengths (4 mm interpolated). CAD, sampled axial withdrawal, print geometry, installation, solid-ASA stiffness and local slice screens pass. Physical print, fit, handling and support release remain pending.',
                       status='Toolpaths reviewed · physical test pending'), credit='')
p = P/'catalog.json'; catalog = json.loads(p.read_text())
catalog['parts'] = [part if row['id'] == 'HX02' else row for row in catalog['parts']]
p.write_text(json.dumps(catalog, indent=2)+'\n', encoding='utf-8', newline='\n')
(R/'publication/canted-hex-keys-v2-additions.json').write_text(json.dumps({p.name: receipt(p) for p in D.iterdir() if p.is_file() and p.name != v1_stl}, indent=2)+'\n', encoding='utf-8', newline='\n')
p = R/'publication/current-pegs-v1-additions.json'; entries = json.loads(p.read_text())
for path in [P/'catalog.json']+list(P.glob(prefix+'*')):
    if path.is_file():
        entries[path.name] = receipt(path)
p.write_text(json.dumps(entries, indent=2)+'\n', encoding='utf-8', newline='\n')
print('HX02 v2 published to the page and catalog; render its previews and refresh their receipts.')
