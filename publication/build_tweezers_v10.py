"""Package reviewed v10 CAD and publish only its scoped gallery additions.

python publication/build_tweezers_v10.py BUILD_DIR RELEASE_DIR --baseline-v9 V9_STEP
Uploads and git publication are separate steps. No G-code is packaged.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'part-solder-modules-tweezers__v10__compact-right-cheek__fit-9328ccc5d4'
COUPON = 'part-solder-modules-tweezers__v10__single-throat__print-right-cheek'
TAG = 'tweezers-v10-dev-2026-10-01'
BASE_URL = f'https://github.com/thereprocase/peg/releases/download/{TAG}/'


def digest(p):
    return dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(), size=p.stat().st_size)


def main(build, release, baseline):
    page_dir = ROOT/'docs/gallery/tweezers'
    source = ROOT/'bench/source/tweezers_v10'
    release.mkdir(parents=True, exist_ok=True)
    info_path = build/f'{PREFIX}__design-and-checks.json'
    info = json.loads(info_path.read_text())
    assert info['valid_single_solid']
    assert info['v9_receiver_and_peg_difference_mm3'] < 1e-6
    assert all(s['passed'] for s in info['tool_checks']['slots'])
    fit_snapshot = source/'fit-pf02-clamp-0.49.scad'
    assert digest(fit_snapshot)['sha256'] == info['fit_scalar_source_sha256']
    info['source_sha256'] = {p.relative_to(ROOT).as_posix(): digest(p)['sha256']
                             for p in [*sorted(source.glob('*.py')), source/'README.txt', fit_snapshot]}
    info['source_sha256'].update({n: digest(ROOT/n)['sha256'] for n in [
        'bench/source/tweezers_v8/holder.py', 'bench/source/tweezers_v8/build_models.py',
        'bench/source/tweezers_v8/parameters.json', 'bench/source/geometry.py',
        'bench/reference/host_envelope.py', 'bench/reference/conformal_motion_results.json']})
    info_path.write_text(json.dumps(info, indent=2)+'\n')
    public = []
    for role in ['loaded', 'empty', 'front', 'rear', 'print', 'detail', 'coupon']:
        public.append(build/f'{PREFIX}__{role}.png')
    for role in ['loaded', 'empty', 'print']:
        public.append(build/f'{PREFIX}__{role}.glb')
    public += [build/f'{PREFIX}__print-right-cheek.stl', info_path]
    additions = {}
    for p in public:
        shutil.copy2(p, page_dir/p.name)
        additions[p.name] = digest(p)
    shutil.copy2(source/'README.txt', page_dir/f'{PREFIX}__README.txt')
    additions[f'{PREFIX}__README.txt'] = digest(source/'README.txt')
    shutil.copy2(build/'front.json', page_dir/f'{PREFIX}__layout.json')
    additions[f'{PREFIX}__layout.json'] = digest(build/'front.json')
    coupon_stl = page_dir/f'{COUPON}.stl'
    shutil.copy2(build/'single-throat-print-right-cheek.stl', coupon_stl)
    additions[coupon_stl.name] = digest(coupon_stl)

    release_files = []
    for role in ['installed', 'print-right-cheek']:
        p = release/f'{PREFIX}__{role}.step'
        shutil.copy2(build/p.name, p)
        release_files.append(p)
    coupon_step = release/f'{COUPON}.step'
    shutil.copy2(build/'single-throat-print-right-cheek.step', coupon_step)
    release_files.append(coupon_step)
    assert digest(baseline)['sha256'] == info['baseline_v9_step_sha256']
    baseline_name = 'part-solder-modules-tweezers__v9__cheek-cradle__fit-pf02c9-latch__installed.step'
    bundle = release/'part-solder-modules-tweezers__v10__cad-source-and-review.zip'
    dependencies = [
        'bench/source/geometry.py', 'bench/source/peg_interface.py',
        'bench/source/peg_profile.py', 'bench/source/peg_print_variant.py',
        'bench/reference/host_envelope.py', 'bench/reference/conformal_motion_results.json',
        'bench/reference/conformal_120_geometry.json', 'bench/reference/conformal_120.step',
        'bench/reference/peg-fit.scad', 'bench/reference/peg-print-variants.json',
        'bench/source/tweezers_v10/fit-pf02-clamp-0.49.scad',
    ]
    dependencies += ['bench/source/tweezers_v8/'+n for n in
                     ['holder.py', 'build_models.py', 'parameters.json', 'requirements.txt', 'review.py']]
    with zipfile.ZipFile(bundle, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        z.writestr('README.txt',
                   'Tweezers v10: compact right cheek, tips down\n\n'
                   'Read bench/source/tweezers_v10/README.txt for fit, printing and checks.\n'
                   'Printable STLs, STEP files and previews are in exports/.\n'
                   'The small single-throat STL is the first fit trial.\n\n'
                   'Rebuild from this extracted directory with the two documented runtimes:\n'
                   '  cadpy bench/source/tweezers_v10/front.py rebuilt\n'
                   '  freecad-python bench/source/tweezers_v10/holder.py rebuilt inputs/'+baseline_name+'\n'
                   '  cadpy bench/source/tweezers_v10/review.py rebuilt\n')
        for p in [*sorted(source.glob('*.py')), source/'README.txt']:
            z.write(p, p.relative_to(ROOT).as_posix())
        for name in dependencies:
            z.write(ROOT/name, name)
        z.write(baseline, 'inputs/'+baseline_name)
        for p in release_files:
            z.write(p, 'exports/'+p.name)
        for p in public:
            z.write(p, 'exports/'+p.name)
        z.write(coupon_stl, 'exports/'+coupon_stl.name)
        for p in [build/'front.json', *sorted(build.glob('reference-tool-*.stl'))]:
            z.write(p, 'review/'+p.name)
    with zipfile.ZipFile(bundle) as z:
        assert z.testzip() is None
        assert hashlib.sha256(z.read('inputs/'+baseline_name)).hexdigest() == info['baseline_v9_step_sha256']
    release_files.append(bundle)
    moves_path = ROOT/'publication/release-downloads.json'
    assets_path = ROOT/'publication/release-assets.json'
    moves, assets = json.loads(moves_path.read_text()), json.loads(assets_path.read_text())
    for p in release_files:
        moves['tweezers/'+p.name] = BASE_URL+p.name
        assets[p.name] = digest(p)
        additions[p.name] = digest(p)
    moves_path.write_text(json.dumps(moves, indent=2)+'\n')
    assets_path.write_text(json.dumps(assets, indent=2)+'\n')
    js = ROOT/'docs/gallery/release-downloads.js'
    text = js.read_text()
    start = text.index('const links=')+len('const links=')
    end = text.index(';', start)
    text = text[:start]+json.dumps(moves, separators=(',', ':'))+text[end:]
    js.write_text(text)
    (ROOT/'publication/tweezers-v10-additions.json').write_text(json.dumps(additions, indent=2)+'\n')

    reduction = 100*info['cad_volume_reduction_fraction']
    tip = min(s['tip_region_clearance_mm'] for s in info['tool_checks']['slots'])
    bounds = ' × '.join(f'{v:.2f}'.rstrip('0').rstrip('.') for v in info['print_bounds_mm'])
    html = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tweezers v10 · compact right cheek</title><script type="module" src="vendor/model-viewer.min.js"></script>
<style>*{box-sizing:border-box}body{margin:0;background:#253139;color:#e7eeeb;font:16px/1.6 system-ui}main{max-width:1120px;margin:auto;padding:24px}a{color:#9bdfd1;overflow-wrap:anywhere}h1{font-size:clamp(30px,5vw,48px);line-height:1.15}h2{line-height:1.3}img{width:100%;height:auto;border-radius:10px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,330px),1fr));gap:20px}.downloads{display:flex;flex-wrap:wrap;gap:10px}.download,button{padding:12px 16px;background:#31554f;border:1px solid #739f93;color:white;border-radius:6px;text-decoration:none;min-height:44px}button{font:inherit;cursor:pointer}button[aria-pressed=true]{background:#417d6e}model-viewer{display:block;width:100%;height:580px;background:#253139;border-radius:12px}.notice{padding:16px;border-left:4px solid #dbb562;background:#3b403b}.lineup-nav{display:flex;flex-wrap:wrap;gap:12px 22px;padding:18px 22px;background:#20282d;font-weight:600}.lineup-nav a{min-height:36px;display:flex;align-items:center;text-decoration:none}table{border-collapse:collapse;width:100%}th,td{border-bottom:1px solid #516068;padding:10px;text-align:left}section{margin:30px 0}.tag{color:#b1d9d0}</style><script defer src="../../viewer/workbench.js"></script></head><body>
<nav class="lineup-nav" aria-label="Collection"><a href="../index.html">The lineup</a><a href="../solder-modules/index.html">Solder WIP</a><a href="index.html">Tweezers versions</a></nav>
<main><p class="tag">v10 · development build · four slots · solid right cheek</p>
<h1>Tips down. A closer, lighter layout.</h1>
<p>The cradles sit beside the right cheek, so their floors join directly into it. The broad support blocks are gone. The cheek stays solid and flat for printing, while the long body guides support the lower arm and leave the upper arm free.</p>
<p><strong>Grasp the heel, lift 5 mm, then move left 30 mm.</strong> Reverse that path to insert. The points stay down throughout.</p>
<img src="__PREFIX____loaded.png" alt="Four open bent tweezers stored tips down beside a continuous right cheek">
<section><h2>Print the single throat first</h2><p>Hold the coupon at the station’s 40° incline and check seating, lateral play and the lift-and-left motion with your actual tweezer.</p>
<div class="downloads"><a class="download" download href="__COUPON__.stl">Single-throat test STL</a><a class="download" download href="__PREFIX____print-right-cheek.stl">Four-slot station STL</a><a class="download" href="__BASE____PREFIX____installed.step">Installed STEP</a><a class="download" href="__BASE__part-solder-modules-tweezers__v10__cad-source-and-review.zip">CAD + editable source bundle</a></div>
<p class="notice"><strong>Prototype fit; not yet physically tested.</strong> All four slots repeat the supplied 122.76 mm bent tweezer. The close side allowance is 0.08 mm per edge; the aft and lower-face allowances are 0.35 mm. Clear supports and burrs before trying the real tool.</p></section>
<section><h2>Rotate the actual model</h2><div class="downloads" role="group" aria-label="Model view"><button type="button" data-view="loaded" aria-pressed="true">With tweezers</button><button type="button" data-view="empty" aria-pressed="false">Empty</button><button type="button" data-view="print" aria-pressed="false">On the print bed</button></div>
<model-viewer id="cad" src="__PREFIX____loaded.glb" poster="__PREFIX____loaded.png" camera-orbit="150deg 72deg auto" camera-controls touch-action="pan-y" alt="Compact tweezer holder with tips down and a solid right cheek"></model-viewer>
<div class="grid"><div><img loading="lazy" src="__PREFIX____front.png" alt="Installed front view showing the solid cheek on the viewer’s right"><p>The right cheek is on your right when facing the mounted station.</p></div><div><img loading="lazy" src="__PREFIX____print.png" alt="Actual right cheek lying flat on the print bed"><p>The print STL already lies on that solid cheek. The projecting pegs need local supports.</p></div><div><img loading="lazy" src="__PREFIX____detail.png" alt="Broad body support with open arms and working points extending free"><p>Body support and rounded low rails; the points have no floor or stop beneath them.</p></div><div><img loading="lazy" src="__PREFIX____rear.png" alt="The retained v9 mounting receiver, hooks, bearing pegs and latches"><p>The v9 mounting interface is retained.</p></div></div></section>
<section><h2>What changed from v9</h2><table><tbody>
<tr><th>Solid model volume</th><td>379.1 → 102.8 cm³ · __REDUCTION__% reduction</td></tr>
<tr><th>Cradle placement</th><td>Beside the right cheek · heels 12 mm closer to the board and 6 mm lower</td></tr>
<tr><th>Print bounds</th><td>__BOUNDS__ mm · right cheek on the bed</td></tr>
<tr><th>Cheek and throat</th><td>3 mm continuous cheek · 58 mm contoured support · 19 mm closer side guidance</td></tr>
<tr><th>Tool spacing and tilt</th><td>42 mm between slots · 40° incline</td></tr>
<tr><th>Mounting interface</th><td>Same v9 receiver and pegs · 48.8 mm width · two mounting columns</td></tr>
</tbody></table><p>The reduction compares CAD volume. Sliced filament savings depend on infill and supports. These exports are print-preparation inputs; inspect toolpaths with your intended printer and filament settings.</p>
<p>CAD and closed-mesh checks pass. All four nominal insertion/removal paths clear the holder and neighboring tools; the point region has at least __TIP__ mm clearance at rest. These geometry checks do not establish printed fit, spring behavior or wear.</p>
<p><a href="__PREFIX____design-and-checks.json">Dimensions and checks</a> · <a href="__PREFIX____README.txt">Build and fit notes</a> · <a href="v9.html">Previous v9 development build</a> · <a href="https://github.com/thereprocase/peg/tree/main/bench/source/tweezers_v10">Editable source</a></p></section></main>
<script>const prefix='__PREFIX____';const cad=document.getElementById('cad');document.querySelectorAll('[data-view]').forEach(button=>button.addEventListener('click',async()=>{await customElements.whenDefined('model-viewer');cad.src=prefix+button.dataset.view+'.glb';cad.poster=prefix+button.dataset.view+'.png';cad.cameraOrbit=button.dataset.view==='print'?'35deg 55deg auto':'150deg 72deg auto';document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));}));</script><script defer src="../clear-download-names.js"></script><script defer src="../release-downloads.js"></script></body></html>
'''
    for token, value in {'__PREFIX__':PREFIX, '__COUPON__':COUPON, '__BASE__':BASE_URL,
                         '__REDUCTION__':f'{reduction:.1f}', '__BOUNDS__':bounds, '__TIP__':f'{tip:.2f}'}.items():
        html = html.replace(token, value)
    assert '__PREFIX__' not in html
    (page_dir/'v10.html').write_text(html)
    index = page_dir/'index.html'
    text = index.read_text()
    notice = '<p class="notice"><a href="v10.html">New development build: v10 · compact layout and a solid right cheek</a></p>'
    if 'href="v10.html"' not in text:
        text = text.replace('<main>', '<main>'+notice, 1)
        index.write_text(text)
    print(json.dumps(dict(cad_reduction_percent=reduction, additions=len(additions),
                          release_files=[p.name for p in release_files]), indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('build', type=Path)
    parser.add_argument('release', type=Path)
    parser.add_argument('--baseline-v9', type=Path, required=True)
    args = parser.parse_args()
    main(args.build, args.release, args.baseline_v9)
