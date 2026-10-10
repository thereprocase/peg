"""Build bounded native final racks. Requires FreeCAD 1.1; publishes nothing."""
from pathlib import Path
import json,os,subprocess,argparse,hashlib,time
from concurrent.futures import ThreadPoolExecutor
from prepare_layouts import env_for
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
NAMES={'HX04':'Owner three-tier fan','HX05A':'Bondhus 33034 Torx','HX05B':'Bondhus 13189 metric','HX05C':'Bondhus 13190 inch'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--rack',choices=NAMES,action='append');a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
 fc=os.environ.get('FREECAD_PYTHON',str(ROOT/'.local-runtime/freecad-python'))
 def run(part):
  dst=out/part;dst.mkdir(exist_ok=True);env=env_for(part)|{'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','HX_NAME':NAMES[part]};env.pop('COUPON_OUT',None)
  inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.rglob('*') if p.is_file() and p.suffix in ('.py','.json','.ttf') and '__pycache__' not in p.parts}
  start=time.monotonic()
  with (dst/'build.log').open('w') as f:subprocess.run([fc,str(HERE/'build_short.py'),'--quick',str(dst)],cwd=HERE,env=env,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=2400)
  assert all(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h for n,h in inputs.items()), 'source changed during build'
  (dst/'run.json').write_text(json.dumps({'id':part,'name':NAMES[part],'seconds':time.monotonic()-start,'build_env':{k:v for k,v in env.items() if k.startswith(('SHORT_','HX4S_')) or k=='XENV'},'source_dependencies':inputs},indent=2)+'\n')
  print(part,'native build complete',flush=True)
 with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,a.rack or list(NAMES)))
if __name__=='__main__':main()
