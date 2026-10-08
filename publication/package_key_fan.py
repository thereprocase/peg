"""Package HX04 (HX4_VERSION, default 1): native CAD, exact sources and review evidence (bundle), plus the solid-zone 3MF project.
    python publication/package_key_fan.py RELEASE_DIR
"""
from pathlib import Path
import argparse, hashlib, json, shutil, zipfile
R = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser(); ap.add_argument('output', type=Path); out = ap.parse_args().output; out.mkdir(parents=True, exist_ok=True)
VER = int(__import__('os').environ.get('HX4_VERSION', 1))
B = R/f'bench/reviews/key-fan-v{VER}/HX04'; S = R/'bench/source/key_fan_v1'
rep = json.loads((B/'report.json').read_text())
src = [S/n for n in ['README.md', 'build_short.py', 'check.py', 'coupon.py', 'fea_run.py', 'swing.py']]
src += [S/'study'/n for n in ['short.py', 'sunray.py', 'comb.py', 'nudge_rows.py', rep['layout']]]
src += [S/'tools'/n for n in ['glb.py', 'gate3.py', 'quickslice.py', 'slice3mf.py', 'evidence.py', 'run_candidate.sh', 'shots3.cjs', 'package.json']]
src += [S/'fonts'/n for n in ['Fillaprint-Regular.ttf', 'OFL.txt']]
src += [R/'bench/source/three_set_rack_v1/key_sets.json', R/'bench/source/bespoke_tools_v1/build.py',
        R/'bench/source/gallery_current_mounts_v1/station_snapshot/source/solder_v12/common.py',
        R/'bench/source/canted_hex_keys_v2/slice_local.py']
src += [R/'bench/source/gallery_new_designs_v1/snapshot/bench/source/solder_v12'/n for n in ['checks.py', 'fea.py']]
ev = [p for p in B.iterdir() if p.is_file() and p.suffix.lower() in {'.json', '.md', '.step', '.stl', '.3mf'} and 'tool-reference' not in p.name]
entries = {p.relative_to(R).as_posix(): p.read_bytes() for p in src+ev}
entries['README.txt'] = (f'HX04 v{VER}: three-tier pegboard key fan (hex L-keys 1.5-10 back, Torx T10-T50 middle, Bondhus T-handles 2-10 front). '
                         f'Read bench/reviews/key-fan-v{VER}/HX04/NOTES.md first, then print the fit coupon. Rebuild with a FreeCAD 1.1 Python (numpy + scipy) '
                         'and the build env in report.json: FREECAD_PYTHON bench/source/key_fan_v1/build_short.py --quick OUT. The print STL and the '
                         'solid-zone 3MF are in left-end print orientation. Physical print, fit and seating are untested. No machine G-code is included.' + chr(10)).encode()
manifest = {n: dict(bytes=len(b), sha256=hashlib.sha256(b).hexdigest()) for n, b in entries.items()}
entries['MANIFEST.json'] = (json.dumps(manifest, indent=2)+'\n').encode()
path = out/f'key-fan__v{VER}__cad-source-and-review.zip'
with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
    for n, b in sorted(entries.items()):
        z.writestr(n, b)
with zipfile.ZipFile(path) as z:
    assert z.testzip() is None
    for n, m in manifest.items():
        assert hashlib.sha256(z.read(n)).hexdigest() == m['sha256']
proj = out/rep['assets']['hx04_solid-zones.3mf']; shutil.copyfile(B/proj.name, proj)
for p in (path, proj):
    print(json.dumps(dict(path=p.name, bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest())))
