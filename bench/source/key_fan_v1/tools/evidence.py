"""Collect HX04 review evidence from a finished build + coupon into bench/reviews/key-fan-v1/HX04.
    python tools/evidence.py <build dir> <coupon dir>
Run from bench/source/key_fan_v1 with the build env (SHORT_*). Writes report.json, print-geometry.json,
slice-summary.json, exact-check.json, stiffness.json, coupon.json and the viewer GLBs; copies the native/print
files (STEP, STL, 3MF project) beside them (those are release assets, not tracked).
"""
import hashlib, json, os, re, shutil, subprocess, sys
from pathlib import Path
import numpy as np, trimesh
HERE = Path(__file__).resolve().parents[1]; R = HERE.parents[2]
sys.path.insert(0, str(HERE.parents[0]/'gallery_new_designs_v1/snapshot/bench/source/solder_v12')); sys.path.insert(0, str(HERE/'study'))
import checks, short as S
d, c = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
VER = int(os.environ.get('HX4_VERSION', 1))
OUT = R/f'bench/reviews/key-fan-v{VER}/HX04'; OUT.mkdir(parents=True, exist_ok=True)
PREFIX = f'part-hx04__v{VER}__left-cheek__fit-pf02c9-hoop5'


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def slice_log(p):
    t = Path(p).read_text(encoding='utf-8').splitlines()
    m = re.match(r'([\d.]+) g; (.+)', t[0]); feats = {}
    for line in t[1:]:
        q = re.match(r'(.+?)\s+([\d.]+) g$', line)
        if q:
            feats[q.group(1).strip()] = float(q.group(2))
    return dict(grams=float(m.group(1)), time=m.group(2), features_g=feats)


# --- files ---------------------------------------------------------------------------------------------------
files = {'installed.step': d/'installed.step', 'installed.stl': d/'installed.stl', 'print.stl': d/'print.stl',
         'print_solid-zones.stl': d/'print_solid.stl', 'hx04_solid-zones.3mf': d/'slice_solid/hx04_solid.3mf',
         'tool-reference.stl': d/'keys.stl', 'coupon_print.stl': c/'print.stl', 'coupon_installed.step': c/'coupon_installed.step'}
named = {}
for k, src in files.items():
    dst = OUT/(PREFIX+'__'+k); shutil.copyfile(src, dst); named[k] = dst.name
# --- viewer GLBs without the review edge ink (the gallery shader styles them) --------------------------------------
keys = trimesh.load(d/'keys.stl', force='mesh').simplify_quadric_decimation(percent=.92)   # light enough for the web viewer
keys.export(d/'keys_web.stl')
env = dict(os.environ, INK='0', KEYS='keys_web.stl')
subprocess.run([sys.executable, str(HERE/'tools/glb.py'), str(d)], check=True, env=env, capture_output=True)
for n in ('installed.glb', 'loaded.glb', 'print.glb'):
    shutil.copyfile(d/n, OUT/n)
subprocess.run([sys.executable, str(HERE/'tools/glb.py'), str(d)], check=True, capture_output=True)   # restore inked review GLBs
# --- print geometry gate --------------------------------------------------------------------------------------
pr = trimesh.load(d/'print.stl', force='mesh'); inv = np.linalg.inv(np.array(json.loads((d/'pose.json').read_text())).reshape(4, 4))
oh = checks.overhangs(pr, inv, []); isl = checks.islands(pr, inv)
geo = dict(inputs=dict(print_stl=sha(d/'print.stl')), components=len(pr.split(only_watertight=False)), extents_mm=pr.extents.round(1).tolist(),
           volume_cm3=round(pr.volume/1000, 1), overhangs=oh, islands=isl,
           note='Largest overhang patches: T10 mouth where the straight and leaned openings meet (~16 mm2 at ~44 deg) and label counters (<14 mm2). The slicer adds tree support under the peg hooks behind the mounting face.')
xmax = float(pr.extents[0])
isl['declared'] = [dict(q, reason='single vertex on the vertical end wall (print +X, the installed top trim face); the 0.2 mm probe below a wall vertex lies on the wall, not in air')
                   for q in isl['points'] if q['vertices'] == 1 and q['print_xyz'][0] >= xmax-.5]
(OUT/'print-geometry.json').write_text(json.dumps(geo, indent=1, default=float)+'\n', encoding='utf-8', newline='\n')
# --- slices, exact check, stiffness, coupon -------------------------------------------------------------------
sl = dict(profile='Local review slice only: Bambu P1S 0.4 mm, 0.20 mm layers, owner ASA filament profile, 2 walls, 20% sparse infill, tree supports on the build plate, 5 mm outer brim. No G-code is published.',
          plain=dict(slice_log(d/'slice.log'), input_sha256=sha(d/'print.stl')),
          solid_zones=dict(slice_log(d/'slice_solid.log'), input_sha256=sha(d/'print.stl'), zones_sha256=sha(d/'print_solid.stl'), zones='100% sparse infill inside the modifier part'),
          coupon_plain=dict(slice_log(c/'slice.log'), input_sha256=sha(c/'print.stl')))
(OUT/'slice-summary.json').write_text(json.dumps(sl, indent=1)+'\n', encoding='utf-8', newline='\n')
ex = json.loads((d/'checks.json').read_text()); (OUT/'exact-check.json').write_text(json.dumps(ex, indent=1)+'\n', encoding='utf-8', newline='\n')
fe = json.loads((d/'fea.json').read_text()); fe['inputs'] = dict(step=sha(d/'installed.step'))
(OUT/'stiffness.json').write_text(json.dumps(fe, indent=1)+'\n', encoding='utf-8', newline='\n')
shutil.copyfile(c/'coupon.json', OUT/'coupon.json')
if (d/'swing.json').exists():                          # install swing over the full peg grid (swing.py)
    shutil.copyfile(d/'swing.json', OUT/'install-swing.json')
# --- report ---------------------------------------------------------------------------------------------------
Lo = S.Layout(json.loads((HERE/'study'/os.environ['HX4S_LAYOUT']).read_text())['x'])
sockets = [dict(set=t['set'], size=t['name'], seat_depth_mm=round(float(t['D']), 1), axis=[round(float(a), 4) for a in t['u']],
                mouth_mm=[round(float(a), 2) for a in t['mouth']], floor_slope_deg=t['floor_deg'], pinch_ratio=round(float(t['pinch']), 2),
                keyed=bool(t['set'] == 'tee' and t['af'] >= S.TEE_KEYED_MIN),
                turn_play_deg=(round(S.tee_play_deg(t['af']), 1) if t['set'] == 'tee' else None)) for t in Lo.tools]
deps = ['bench/source/key_fan_v1/build_short.py', 'bench/source/key_fan_v1/check.py', 'bench/source/key_fan_v1/coupon.py',
        'bench/source/key_fan_v1/fea_run.py', 'bench/source/key_fan_v1/swing.py', 'bench/source/key_fan_v1/study/short.py', 'bench/source/key_fan_v1/study/sunray.py',
        'bench/source/key_fan_v1/study/comb.py', 'bench/source/key_fan_v1/study/'+os.environ['HX4S_LAYOUT'],
        'bench/source/three_set_rack_v1/key_sets.json', 'bench/source/bespoke_tools_v1/build.py',
        'bench/source/gallery_current_mounts_v1/station_snapshot/source/solder_v12/common.py']
bb = trimesh.load(d/'print.stl', force='mesh').bounds
rep = dict(id='HX04', version=VER, prefix=PREFIX, pose='left-cheek', layout=os.environ['HX4S_LAYOUT'],
           build_env={k: v for k, v in os.environ.items() if k.startswith(('SHORT_', 'HX4S_', 'XENV'))},
           source_dependencies={p: sha(R/p) for p in deps}, assets=named,
           files={n: dict(sha256=sha(OUT/n), bytes=(OUT/n).stat().st_size) for n in named.values()},
           print_bounds_mm=(bb[1]-bb[0]).round(1).tolist(), volume_mm3=round(trimesh.load(d/'installed.stl', force='mesh').volume),
           checks=dict(all_routes_ok=ex['all_routes_ok'], stored_ok=ex['stored_ok'], straighten_ok=ex['straighten_ok'], depth_mm=ex['depth_mm'],
                       min_floor_mm=min(ex['floors_mm']), stiffness_min_N_per_mm=min(l['stiffness_N_per_mm'] for cs in fe['cases'] for l in cs['loads'])),
           sockets=sockets, physical_tests='Pending')
(OUT/'report.json').write_text(json.dumps(rep, indent=1)+'\n', encoding='utf-8', newline='\n')
print(json.dumps(rep['checks']), len(named), 'files')
