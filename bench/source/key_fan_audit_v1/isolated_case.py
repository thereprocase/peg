"""Check whether the rejected refined-mesh case persists without load-history steps.
Same node coordinates, stiffness material, constraints and selected CLOAD entries.
"""
import argparse,json,hashlib,re,subprocess,os
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();root=a.root.resolve();old=root/'h5-deep/hooks-only-grip-wrench/case.inp';text=old.read_text();parts=text.split('*STEP\n');assert len(parts)==6;out=root/'h5-isolated/hooks-side';out.mkdir(parents=True,exist_ok=True);target=out.parent/'volume.inp'
if not target.exists():target.symlink_to(root/'h5/volume.inp')
(out/'case.inp').write_text(parts[0]+'*STEP\n'+parts[2]);
with (out/'ccx.log').open('w') as f:subprocess.run(['ccx','case'],cwd=out,env=dict(os.environ,OMP_NUM_THREADS='6'),stdout=f,stderr=subprocess.STDOUT,timeout=3600,check=True)
data=(out/'case.dat').read_text();rf=data.split('forces (fx,fy,fz) for set FIX and time')[1].split('stresses (')[0];R=np.zeros(3)
for line in rf.splitlines()[1:]:
 x=line.split()
 if len(x)==4 and x[0].isdigit():R+=np.array([float(i) for i in x[1:]])
err=float(np.linalg.norm(R+[30,0,0])/30);r=dict(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),original_multistep_deck_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),isolated_deck_sha256=hashlib.sha256((out/'case.inp').read_bytes()).hexdigest(),force_N=[30,0,0],reaction_N=R.tolist(),force_balance_relative_error=err,passed=err<.001,scope='Same failed h5 hooks-only sideways grip-wrench case, replayed as a fresh single static step. No acceptance tolerance relaxed.')
(out/'single-step-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
