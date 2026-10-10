"""Ideal solid-body vibration reference; excludes infill, tools and elastic board.
Density is an explicit assumption, not a measured specimen property.
"""
import argparse,json,hashlib,os,re,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--support',choices=['all-pegs','four-corners','face'],required=True);a=p.parse_args();start=time.monotonic();root=a.root;out=root/'modal/h5'/a.support;out.mkdir(parents=True,exist_ok=True)
base=root/('h5-deep' if a.support=='all-pegs' else 'h5-remaining')/f'{a.support}-grip-wrench';original=(base/'case.inp').read_text();pre=original.split('*STEP')[0].replace('INPUT=../volume.inp','INPUT=volume.inp');assert '*MATERIAL' in pre and '*BOUNDARY' in pre
pre=pre.replace('*SOLID SECTION','*DENSITY\n1.07e-9\n*SOLID SECTION');(out/'volume.inp').symlink_to(root/'h5/volume.inp') if not (out/'volume.inp').exists() else None
# Keep the original fixture constraints, remove all applied load history.
text=pre+'*STEP\n*FREQUENCY\n5\n*NODE PRINT,NSET=NALL\nU\n*END STEP\n';(out/'modes.inp').write_text(text)
with (out/'solver.log').open('w') as f:subprocess.run(['ccx','modes'],cwd=out,env=dict(os.environ,OMP_NUM_THREADS='4'),stdout=f,stderr=subprocess.STDOUT,check=True,timeout=2200)
dat=(out/'modes.dat').read_text();rows=[]
for line in dat.splitlines():
 v=line.split()
 if len(v)==5 and v[0].isdigit():
  try:n=int(v[0]);numbers=[float(q.replace('D','E')) for q in v[1:]]
  except ValueError:continue
  if 1<=n<=5:rows.append(dict(mode=n,eigenvalue=numbers[0],angular_frequency_rad_s=numbers[1],frequency_Hz=numbers[2],imaginary_frequency_Hz=numbers[3]))
assert len(rows)==5,dat[:4000];assert all(q['frequency_Hz']>0 and q['imaginary_frequency_Hz']==0 for q in rows)
r=dict(h_requested_mm=5,mesh_sha256=hashlib.sha256((root/'h5/mesh.npz').read_bytes()).hexdigest(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),deck_sha256=hashlib.sha256(text.encode()).hexdigest(),dat_sha256=hashlib.sha256(dat.encode()).hexdigest(),support=a.support,density_tonne_mm3=1.07e-9,material_E_MPa=1800,nu=.35,modes=rows,seconds=time.monotonic()-start,scope='Five undamped eigenmodes of archived rack as homogeneous solid ASA, E=1800 MPa, nu=.35, assumed density1070 kg/m3. Ideal original clamps; no tools, elastic board, print infill, layering, damping or validation. Mode-vector magnitude is arbitrary, not a vibration response.')
(out/'result.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2),flush=True)
