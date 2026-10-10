"""Independent global force/moment balance check on completed static solver runs."""
import argparse,json,re,hashlib
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('run',type=Path);a=p.parse_args();run=a.run.resolve();mesh=np.load(run.parent/'mesh.npz');ids=mesh['ids'];X=mesh['X'];xyz={int(i):v for i,v in zip(ids,X)};loads=[];rows=[];active=False
for line in (run/'case.inp').read_text().splitlines():
 if line.startswith('*CLOAD'):active=True;rows=[]
 elif line.startswith('*'):
  if active:loads.append(rows);active=False
 elif active:
  s=line.split(',');f=np.zeros(3);f[int(s[1])-1]=float(s[2]);rows.append((int(s[0]),f))
text=(run/'case.dat').read_text();blocks=re.split(r'forces \(fx,fy,fz\) for set FIX and time',text)[1:];assert len(blocks)==len(loads)
results=[]
for i,(block,force_rows) in enumerate(zip(blocks,loads)):
 reactions=[]
 for line in block.split('stresses (')[0].splitlines()[1:]:
  s=line.split()
  if len(s)==4 and s[0].isdigit():reactions.append((int(s[0]),np.array([float(v) for v in s[1:]])))
 F=sum((f for n,f in force_rows),np.zeros(3));M=sum((np.cross(xyz[n],f) for n,f in force_rows),np.zeros(3));R=sum((f for n,f in reactions),np.zeros(3));RM=sum((np.cross(xyz[n],f) for n,f in reactions),np.zeros(3));ferror=float(np.linalg.norm(F+R)/max(np.linalg.norm(F),1e-12));merror=float(np.linalg.norm(M+RM)/max(np.linalg.norm(M),1e-12));results.append(dict(case=i+1,applied_force_N=F.tolist(),applied_moment_about_global_origin_Nmm=M.tolist(),force_balance_relative_error=ferror,moment_balance_relative_error=merror,passed=ferror<.001 and merror<.001))
r=dict(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),deck_sha256=hashlib.sha256((run/'case.inp').read_bytes()).hexdigest(),results=results,passed=all(q['passed'] for q in results));(run/'reaction-audit.json').write_text(json.dumps(r,indent=2)+'\n');print(run,r['passed'],[(q['force_balance_relative_error'],q['moment_balance_relative_error']) for q in results]);assert r['passed']
