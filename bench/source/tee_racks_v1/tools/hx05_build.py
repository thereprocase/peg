"""One-command Windows HX05 review pass. No printer communication or publication.
Uses the owner's existing FreeCAD 1.1 / P1S / calibrated ASA / Orca / browser setup.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parents[1]
TOOLS = HERE/'tools'
SETS = {'HX05A': ('33034', 'T9,T25,T40', 'Bondhus 33034 Torx'),
        'HX05B': ('13189', '2,4,5,10', 'Bondhus 13189 metric'),
        'HX05C': ('13190', '3/32,5/32,3/16,3/8', 'Bondhus 13190 inch')}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def environment(part):
    sid, blocks, name = SETS[part]
    layout = f'{part.lower()}_stand.json'
    record = json.loads((HERE/'study'/layout).read_text())
    for filename, expected in record['dependencies'].items():
        if digest(HERE/'study'/filename) != expected:
            raise RuntimeError(f'{layout}: stale study dependency {filename}; rerun layout verification')
    if any(float(p) > 1e-7 for p in record['pen'].values()):
        raise RuntimeError(f'{layout}: layout study contains unresolved penalties')
    screen_path=HERE/'study'/f'{part.lower()}_layout-check.json'
    screen=json.loads(screen_path.read_text())
    if not screen['passed'] or screen['layout_sha256'] != digest(HERE/'study'/layout) or screen['verifier_sha256'] != digest(HERE/'study/verify_stand.py'):
        raise RuntimeError(f'{layout}: stale or failed dense fixed-route verification')
    env = {k: v for k,v in os.environ.items() if not k.startswith(('SHORT_', 'HX4S_', 'HX_')) and k != 'XENV'}
    env.update(record['build_env'])
    env.update(HX_ID=part, HX_NAME=name, SHORT_TEE_SET=f'tee_{sid}.json', HX4S_LAYOUT=layout,
               HX4S_TBAR='flats', HX4S_GUSSET='cheek', HX4S_PEG_GRID='1', HX4S_SOLID='1',
               HX_FAMILY='tee-racks', HX4_VERSION='1', COUPON_BLOCKS=blocks,
               FEA_H='10', FEA_THREADS='4', CHECK_STEP='3', SWING_STEP='0.5', PYTHONUTF8='1')
    return env


def command(label, argv, log, env, limit, cwd=HERE):
    start=time.monotonic()
    print(f'{label}: running (timeout {limit}s)', flush=True)
    with log.open('w', encoding='utf-8', newline='\n') as f:
        proc=subprocess.run([str(x) for x in argv], cwd=cwd, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=limit)
    if proc.returncode:
        raise RuntimeError(f'{label}: exit {proc.returncode}; see {log}')
    return dict(stage=label, seconds=round(time.monotonic()-start,2), exit_code=proc.returncode)


def validate_outputs(out, coupon):
    import trimesh
    import numpy as np
    ex=json.loads((out/'checks.json').read_text())
    if not all(ex[k] for k in ('all_routes_ok','stored_ok','straighten_ok')):
        raise RuntimeError(f'exact CAD check failed: {out / "checks.json"}')
    if not ex['floors_mm'] or min(ex['floors_mm']) <= 0 or ex['depth_mm'] > 178:
        raise RuntimeError('CAD floor material or 178 mm depth check failed')
    swing=json.loads((out/'swing.json').read_text())
    if not swing['passed']:
        raise RuntimeError(f'install swing failed: {out / "swing.json"}')
    native=json.loads((out/'build-geometry.json').read_text())
    if not native['native_valid'] or native['native_solids'] != 1 or any(q['op']=='label failed' for q in native['finish']):
        raise RuntimeError('native CAD validity, solid count or label generation failed')
    # Account for the owner's actual shrink compensation and 5 mm XY brim.
    spec=__import__('importlib.util',fromlist=['spec_from_file_location'])
    sp=spec.spec_from_file_location('hx05_profiles', HERE.parent/'canted_hex_keys_v2/slice_local.py')
    sl=spec.module_from_spec(sp);sp.loader.exec_module(sl)
    fil=sl.flatten(sl.USER_FILAMENT,'filament')
    scale=1/(float(fil['filament_shrink'][0].strip('%'))/100)
    meshes={}
    for name,p in [('installed',out/'installed.stl'),('print',out/'print.stl'),('coupon',coupon/'print.stl')]:
        m=trimesh.load(p,force='mesh')
        if not m.is_watertight or not m.is_winding_consistent or m.volume<=0 or (name!='coupon' and len(m.split())!=1):
            raise RuntimeError(f'invalid mesh: {p}')
        if name!='installed' and np.any(m.extents*scale+np.array([10,10,0])>256):
            raise RuntimeError(f'{name}: compensated bounds plus brim exceed P1S 256 mm envelope')
        meshes[name]=dict(extents_mm=m.extents.tolist(),shrink_scale=scale,sha256=digest(p))
    fe=json.loads((out/'fea.json').read_text())
    loads=[q for case in fe['cases'] for q in case['loads']]
    if not loads or any(not math.isfinite(q['stiffness_N_per_mm']) or q['stiffness_N_per_mm']<=0 for q in loads):
        raise RuntimeError('FEA contains no usable stiffness results')
    return dict(meshes=meshes,exact=ex,install=swing['passed'],fea='solid ASA screen only; no physical load rating')


def preflight(fc, bin_dir):
    if not fc or not Path(fc).is_file():
        raise RuntimeError('FreeCAD build required on owner Windows machine: set FREECAD_PYTHON or --freecad-python')
    for filename in ('gmsh.exe','ccx.exe'):
        if not (bin_dir/filename).is_file():raise RuntimeError(f'missing FreeCAD solver: {bin_dir/filename}')
    if not shutil.which('node'):raise RuntimeError('Node required for review renders')
    subprocess.run([fc,'-c',"import FreeCAD, Part, numpy, scipy; v=FreeCAD.Version(); assert v[:2]==['1','1'] or tuple(v[:2])==('1','1'), v; print(v)"],check=True,timeout=60)
    subprocess.run([sys.executable,'-c', 'import numpy, scipy, trimesh, fast_simplification'],check=True,timeout=30)
    subprocess.run(['node','-e', "require('playwright-core');const fs=require('fs');if(!fs.existsSync(process.env.LOCALAPPDATA+'/ms-playwright/chromium-1208/chrome-win64/chrome.exe'))throw Error('missing review Chromium');"],cwd=TOOLS,check=True,timeout=30)
    sp=__import__('importlib.util',fromlist=['spec_from_file_location'])
    spec=sp.spec_from_file_location('hx05_preflight_profiles', HERE.parent/'canted_hex_keys_v2/slice_local.py')
    sl=sp.module_from_spec(spec);spec.loader.exec_module(sl)
    if not sl.ORCA.is_file():raise RuntimeError(f'missing OrcaSlicer: {sl.ORCA}')
    for file,kind in [(sl.USER_FILAMENT,'filament'),(sl.SYSTEM/'machine/Bambu Lab P1S 0.4 nozzle.json','machine'),(sl.SYSTEM/'process/0.20mm Standard @BBL X1C.json','process')]:
        sl.flatten(file,kind)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rack',choices=SETS,action='append');ap.add_argument('--plan',action='store_true')
    ap.add_argument('--preflight-only',action='store_true')
    ap.add_argument('--freecad-python',default=os.environ.get('FREECAD_PYTHON'))
    ap.add_argument('--freecad-bin',type=Path,default=Path(os.environ.get('FREECAD_BIN',r'C:\Program Files\FreeCAD 1.1\bin')))
    args=ap.parse_args(); racks=args.rack or list(SETS)
    envs={part:environment(part) for part in racks}
    if args.plan:
        print(json.dumps({part:dict(layout=env['HX4S_LAYOUT'],profile='owner P1S / PolyLite ASA ReproCal',stages=['build+coupon','exact check','FEA both tiers','install swing','coupon slice','mesh gate','GLB','browser renders','STL slice','solid-zone slice','validate','collect evidence']) for part,env in envs.items()},indent=2));return
    preflight(args.freecad_python,args.freecad_bin)
    if args.preflight_only:return
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    run=HERE/'runs'/f'hx05-{stamp}';run.mkdir(parents=True,exist_ok=False)
    for part,env in envs.items():
        out=run/part;coupon=run/f'{part}-coupon';out.mkdir();coupon.mkdir()
        env.update(FREECAD_PYTHON=str(args.freecad_python),FREECAD_BIN=str(args.freecad_bin),COUPON_OUT=str(coupon))
        receipts=[]
        try:
            receipts.append(command('build+coupon',[args.freecad_python,'build_short.py','--quick',out],out/'build.log',env,2400))
            tasks=[('exact check',[args.freecad_python,'check.py',out],out/'check.log',5400,HERE),
                   ('FEA',[sys.executable,'fea_run.py',out],out/'fea.log',7000,HERE),
                   ('install swing',[args.freecad_python,'swing.py',out],out/'swing.log',3600,HERE),
                   ('coupon slice',[sys.executable,'quickslice.py',coupon/'print.stl',coupon/'slice'],coupon/'slice.log',2000,TOOLS)]
            with ThreadPoolExecutor(max_workers=4) as pool:
                futures=[pool.submit(command,label,argv,log,env,limit,cwd) for label,argv,log,limit,cwd in tasks]
                for future in as_completed(futures):receipts.append(future.result())
            validation=validate_outputs(out,coupon)
            for label,argv,log,limit,cwd in [
                ('mesh gate',[sys.executable,'gate3.py',out],out/'gate.log',900,TOOLS),
                ('GLB',[sys.executable,'glb.py',out],out/'glb.log',900,TOOLS),
                ('renders',['node','shots3.cjs',out],out/'renders.log',600,TOOLS),
                ('STL slice',[sys.executable,'quickslice.py',out/'print.stl',out/'slice'],out/'slice.log',2000,TOOLS),
                ('solid-zone slice',[sys.executable,'slice3mf.py',out,out/'slice_solid'],out/'slice_solid.log',2800,TOOLS)]:
                receipts.append(command(label,argv,log,env,limit,cwd))
            (out/'pipeline-run.json').write_text(json.dumps(dict(id=part,stages=receipts,validation=validation,status='review screens complete; physical qualification pending'),indent=1)+'\n',encoding='utf-8',newline='\n')
            receipts.append(command('collect evidence',[sys.executable,TOOLS/'evidence.py',out,coupon],out/'evidence.log',env,1200))
        except Exception as e:
            (out/'FAILED.json').write_text(json.dumps(dict(id=part,error=str(e),completed_stages=receipts),indent=1)+'\n',encoding='utf-8',newline='\n')
            raise
        print(f'{part}: review pass complete; logs in {out}',flush=True)
    print('All requested racks complete. Physical fit, support release and loads remain pending; no website published.')

if __name__=='__main__':
    try:main()
    except Exception as e:print(f'HX05 STOP: {e}',file=sys.stderr);sys.exit(1)
