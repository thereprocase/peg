"""Bounded local native build with the pinned Linux FreeCAD runtime. No slicing/printing/publication."""
import argparse,json,os,subprocess,sys,time,hashlib
from pathlib import Path
from datetime import datetime,timezone
from hx05_build import environment,SETS
HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parents[2]


def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--rack',choices=SETS,action='append');ap.add_argument('--check',action='store_true');ap.add_argument('--out',type=Path);a=ap.parse_args()
 fc=Path(os.environ.get('FREECAD_PYTHON',str(ROOT/'.local-runtime/freecad-python')))
 if not fc.is_file():raise RuntimeError('run tools/setup_freecad_linux.sh or set FREECAD_PYTHON')
 out=a.out or HERE/'runs'/('guide40-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S'))
 out=out.resolve()
 out.mkdir(parents=True,exist_ok=False)
 for part in a.rack or list(SETS):
  env=environment(part);env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
  env.pop('COUPON_OUT',None)
  dst=out/part;dst.mkdir();start=time.monotonic()
  inputs=[HERE/'build_short.py',HERE/'study/short.py',HERE/'study/socket_policy.py',HERE/'study'/env['HX4S_LAYOUT'],HERE/'study'/env['SHORT_TEE_SET'],HERE/'fonts/Fillaprint-Regular.ttf']
  hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
  with (dst/'build.log').open('w',encoding='utf-8') as f:
   subprocess.run([str(fc),str(HERE/'build_short.py'),'--quick',str(dst)],cwd=HERE,env=env,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=2400)
  assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items()), 'source changed during native build'
  report=json.loads((dst/'build-geometry.json').read_text());assert report['native_valid'] and report['native_solids']==1
  assert not any(q['op']=='label failed' for q in report['finish']),report['finish']
  (dst/'cad-run.json').write_text(json.dumps(dict(part=part,source_dependencies=hashes,build_seconds=time.monotonic()-start,build_env={k:v for k,v in env.items() if k.startswith(('SHORT_','HX4S_'))},status='native build; exact check pending' if not a.check else 'native build complete'),indent=2)+'\n')
  if a.check:
   with (dst/'check.log').open('w',encoding='utf-8') as f:
    subprocess.run([str(fc),str(HERE/'check.py'),str(dst)],cwd=HERE,env=env,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=5400)
   check=json.loads((dst/'checks.json').read_text());assert all(check[k] for k in ('stored_ok','straighten_ok','all_routes_ok')),check
  print(part,dst,'native build complete',flush=True)

if __name__=='__main__':main()
