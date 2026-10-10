"""Replay load cases as independent static solves, preserving the original decks.
Used to diagnose load-history residuals rather than relaxing equilibrium checks.
"""
import argparse,json,os,re,hashlib,subprocess,time
from pathlib import Path
import numpy as np
from fea_campaign import parse_dat
p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--base',default='h5');p.add_argument('--deck-run',default='h5-deep');p.add_argument('--support',default='hooks-only');p.add_argument('--mode',default='grip-wrench');p.add_argument('--cases',default='0,1,2,3,4');p.add_argument('--out',required=True);a=p.parse_args();root=a.root.resolve();mesh=np.load(root/a.base/'mesh.npz');ids,X,ei,centres=[mesh[k] for k in ['ids','X','element_ids','element_centres']];source=root/a.deck_run/f'{a.support}-{a.mode}'/'case.inp';text=source.read_text();parts=text.split('*STEP\n');assert len(parts)==6;spec=json.loads((root/'loads.json').read_text());out=root/a.out;out.mkdir(exist_ok=True);link=out/'volume.inp'
if not link.exists():link.symlink_to(root/a.base/'volume.inp')
fixtext=parts[0].split('*NSET,NSET=FIX\n')[1].split('*',1)[0];fixed=np.array([int(v) for v in re.findall(r'\d+',fixtext)]);pos={int(i):k for k,i in enumerate(ids)};results=[];start=time.monotonic()
for case in [int(i) for i in a.cases.split(',')]:
 dest=out/f'case-{case+1:02d}';dest.mkdir(exist_ok=True);deck=parts[0]+'*STEP\n'+parts[case+1];(dest/'case.inp').write_text(deck);frows={};active=False
 for line in parts[case+1].splitlines():
  if line.startswith('*CLOAD'):active=True
  elif line.startswith('*'):active=False
  elif active:
   s=line.split(',');node=int(s[0]);vec=frows.setdefault(node,np.zeros(3));vec[int(s[1])-1]=float(s[2])
 nodes=np.array(sorted(frows));forces=np.array([frows[int(n)] for n in nodes]);patch=X[[pos[int(n)] for n in nodes]];centre=patch.mean(0);q=dict(spec['loads'][case],force_point=(spec['loads'][case]['physical_grip_point_mm'] if a.mode=='grip-wrench' else spec['loads'][case]['point']),load_node_ids=nodes.tolist(),nodal_forces=forces.tolist(),centroid=centre.tolist(),moment=np.cross(patch-centre,forces).sum(0).tolist())
 with (dest/'ccx.log').open('w') as f:subprocess.run(['ccx','case'],cwd=dest,env=dict(os.environ,OMP_NUM_THREADS='3'),stdout=f,stderr=subprocess.STDOUT,check=True,timeout=3600)
 row=parse_dat(dest/'case.dat',ids,X,ei,centres,[q],fixed)[0];row.update(case_index=case,independent_single_step=True,source_deck_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),fresh_deck_sha256=hashlib.sha256((dest/'case.inp').read_bytes()).hexdigest());(dest/'result.json').write_text(json.dumps(row,indent=2)+'\n');results.append(row);print('FRESH PASS',a.base,a.support,case,row['force_balance_relative_error'],flush=True)
r=dict(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),step_sha256=spec['installed_step_sha256'],base_mesh=a.base,support=a.support,force_mode=a.mode,results=results,seconds=time.monotonic()-start,scope='Same stiffness/constraints/CLOAD entries as prior deck, one fresh static step per load. No load-history states reused; acceptance tolerance unchanged.')
(out/'summary.json').write_text(json.dumps(r,indent=2)+'\n')
