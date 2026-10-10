"""Prescribed pinch screen on the actual bottom hoop crop. Geometrically nonlinear elastic comparison.
This is not an insertion/contact or recoverable snap-force qualification.
"""
import argparse,json,hashlib,os,subprocess,re,time
from pathlib import Path
import numpy as np
from fea_audit import mesh,nset
p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--h',type=float,default=.4);a=p.parse_args();root=a.root.resolve();out=root/'hoop'/f'nonlinear-h{a.h:g}';out.mkdir(exist_ok=True);start=time.monotonic();ids,X,eid,centres,volumes=mesh(root/'hoop/hoop-root.step',out,a.h);rear=X[:,1]<-3.5;upper=rear&(X[:,2]>X[rear,2].max()-.3);lower=rear&(X[:,2]<X[rear,2].min()+.3);fixed=X[:,1]>.5
assert upper.sum()>2 and lower.sum()>2 and not np.any(fixed&(upper|lower));deck=['*INCLUDE,INPUT=volume.inp',nset('ALL',ids),nset('ROOT',ids[fixed]),nset('UPPER',ids[upper]),nset('LOWER',ids[lower]),'*MATERIAL,NAME=ASA','*ELASTIC','1800,0.35','*SOLID SECTION,ELSET=EALL,MATERIAL=ASA'];deltas=[.1,.2,.3,.4]
for d in deltas:
 deck+=['*STEP,NLGEOM','*STATIC','0.1,1.,0.00001,0.2','*BOUNDARY,OP=NEW','ROOT,1,3',f'UPPER,3,3,{-d:.12g}',f'LOWER,3,3,{d:.12g}','*NODE PRINT,FREQUENCY=999,NSET=ALL','U','*NODE PRINT,FREQUENCY=999,NSET=UPPER','RF','*NODE PRINT,FREQUENCY=999,NSET=LOWER','RF','*NODE PRINT,FREQUENCY=999,NSET=ROOT','RF','*EL PRINT,FREQUENCY=999,ELSET=EALL','S','*END STEP']
(out/'pinch.inp').write_text('\n'.join(deck)+'\n')
with (out/'ccx.log').open('w') as f:subprocess.run(['ccx','pinch'],cwd=out,env=dict(os.environ,OMP_NUM_THREADS='4'),stdout=f,stderr=subprocess.STDOUT,timeout=3600,check=True)
text=(out/'pinch.dat').read_text();blocks=re.split(r'displacements \(vx,vy,vz\) for set ALL and time',text)[1:];assert len(blocks)==4;pos={int(i):k for k,i in enumerate(ids)};results=[]
for k,(d,block) in enumerate(zip(deltas,blocks)):
 modes=re.split(r'(?m)^\s*(?=forces \(|stresses \()',block);U=np.full_like(X,np.nan)
 for line in modes[0].splitlines()[1:]:
  v=line.split()
  if len(v)==4 and v[0].isdigit():U[pos[int(v[0])]]=[float(x) for x in v[1:]]
 assert np.isfinite(U).all();reactions={};S=[];Se=[]
 for b in modes[1:]:
  if b.lstrip().startswith('forces'):
   key=re.search(r'for set (\w+)',b).group(1);rows=[]
   for line in b.splitlines()[1:]:
    v=line.split()
    if len(v)==4 and v[0].isdigit():rows.append([float(x) for x in v[1:]])
   reactions[key]=np.array(rows).sum(0)
  else:
   for line in b.splitlines()[1:]:
    v=line.split()
    if len(v)==8 and v[0].isdigit():Se.append(int(v[0]));S.append([float(x) for x in v[2:]])
 S=np.array(S);vm=np.sqrt(.5*((S[:,0]-S[:,1])**2+(S[:,1]-S[:,2])**2+(S[:,2]-S[:,0])**2)+3*np.sum(S[:,3:]**2,1));force=.5*(abs(reactions['UPPER'][2])+abs(reactions['LOWER'][2]));balance=np.linalg.norm(sum(reactions.values()))/max(force,1e-10);assert balance<.002
 np.savez_compressed(out/f'field-{k+1:02d}.npz',X=X,U=U,stress=S,stress_element_ids=np.array(Se),element_ids=eid,element_centres=centres)
 results.append(dict(pinch_per_arm_mm=d,total_prescribed_closure_mm=2*d,upper_tip_reaction_N=reactions['UPPER'].tolist(),lower_tip_reaction_N=reactions['LOWER'].tolist(),root_reaction_N=reactions['ROOT'].tolist(),mean_force_per_arm_N=force,linear_stiffness_per_arm_N_per_mm=force/d,force_balance_relative_error=balance,max_displacement_mm=float(np.linalg.norm(U,axis=1).max()),von_mises_MPa=dict(max=float(vm.max()),p95=float(np.percentile(vm,95)),p99=float(np.percentile(vm,99))),build_normal_max_tension_MPa=float(max(0,S[:,0].max()))))
r=dict(geometric_nonlinearity=True,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),parent_step_sha256=json.loads((root/'hoop/geometry.json').read_text())['parent_step_sha256'],crop_step_sha256=hashlib.sha256((root/'hoop/hoop-root.step').read_bytes()).hexdigest(),h_mm=a.h,nodes=len(ids),elements=len(eid),fixed_root_nodes=int(fixed.sum()),upper_tip_nodes=int(upper.sum()),lower_tip_nodes=int(lower.sum()),tip_centroids_mm=dict(upper=X[upper].mean(0).tolist(),lower=X[lower].mean(0).tolist()),material=dict(E_MPa=1800,nu=.35),results=results,seconds=time.monotonic()-start,scope='Actual hoop/root crop, ideal fixed plate and distributed prescribed Z pinch at outer crest patches. Geometrically nonlinear elastic stiffness and stress only; no material yielding model. No board contact, friction, plasticity, creep, damage or support-release model; no insertion-force or recoverability rating.')
(out/'summary.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
