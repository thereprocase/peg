"""One-command final native build, owner guide-wall refinement and exported checks."""
from pathlib import Path
import os,sys,subprocess,argparse
from build_all import NAMES,ROOT,HERE
from prepare_layouts import env_for

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--rack',choices=NAMES,action='append');a=ap.parse_args();out=a.out.resolve();assert not out.exists() or not any(out.iterdir()), 'use a fresh output directory';parts=a.rack or list(NAMES)
 args=[sys.executable,str(HERE/'build_all.py'),'--out',str(out)]
 for p in parts:args+=['--rack',p]
 subprocess.run(args,check=True,timeout=5200)
 fc=os.environ.get('FREECAD_PYTHON',str(ROOT/'.local-runtime/freecad-python'))
 for part in parts:
  env=env_for(part)|{'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'};dst=out/part
  if part=='HX04':
   subprocess.run([fc,str(HERE/'refine_owner.py'),str(dst)],env=env,check=True,timeout=900)
   subprocess.run([fc,str(HERE/'complete_guide_walls.py'),str(dst)],env=env,check=True,timeout=900)
   subprocess.run([fc,str(HERE/'normalize_document.py'),str(dst)],env=env,check=True,timeout=120)
  checker='check_full_model.py'
  subprocess.run([fc,str(HERE/checker),str(dst)],env=env,check=True,timeout=1200)
  import json
  assert json.loads((dst/'native-check.json').read_text())['passed'],part
if __name__=='__main__':main()
