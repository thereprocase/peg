"""Reproducible HX04 published-STEP FEA audit. Linux gmsh/ccx, numpy required.
Retains meshes/decks/solver logs on compute box; exports compact receipts.
"""
import argparse,hashlib,json,math,os,re,subprocess,time
from pathlib import Path
import numpy as np

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(argv,log,limit):
 with log.open('w') as f:subprocess.run([str(x) for x in argv],stdout=f,stderr=subprocess.STDOUT,timeout=limit,check=True)
def mesh(step,out,h,algorithm=1):
 raw=out/'mesh.inp';run(['gmsh',step,'-3','-order','2','-clmax',h,'-clmin',h/4,'-setnumber','Mesh.SecondOrderLinear','1','-setnumber','Mesh.Algorithm3D',algorithm,'-nt','4','-format','inp','-o',raw],out/'gmsh.log',1800)
 blocks=re.split(r'(?m)^(?=\*)',raw.read_text());nodes=[];elements=[];xyz={};conn={}
 for block in blocks:
  header=block.split('\n',1)[0].strip().upper()
  if header.startswith('*NODE'):
   nodes.append(block)
   for line in block.splitlines()[1:]:
    a=[x.strip() for x in line.split(',')]
    if len(a)==4:xyz[int(a[0])]=[float(x) for x in a[1:]]
  elif header.startswith('*ELEMENT') and 'C3D10' in header:
   elements.append(re.sub(r'(?i)ELSET=[^,\n]*','ELSET=EALL',block))
   for line in block.splitlines()[1:]:
    a=[x.strip() for x in line.split(',') if x.strip()]
    if len(a)==11:conn[int(a[0])]=[int(x) for x in a[1:]]
 assert xyz and conn
 ids=np.array(sorted(xyz));X=np.array([xyz[int(i)] for i in ids]);ei=np.array(sorted(conn));ec=np.array([conn[int(i)] for i in ei]);positions={int(i):k for k,i in enumerate(ids)};corners=X[np.array([[positions[int(i)] for i in c[:4]] for c in ec])]
 volumes=np.abs(np.linalg.det(corners[:,1:]-corners[:,:1]))/6;assert np.all(volumes>1e-14)
 np.savez(out/'mesh.npz',ids=ids,X=X,element_ids=ei,element_centres=corners.mean(1),volumes=volumes)
 (out/'volume.inp').write_text(''.join(nodes+elements));return ids,X,ei,corners.mean(1),volumes

def nset(name,ids):return '*NSET,NSET='+name+'\n'+'\n'.join(','.join(str(int(i)) for i in ids[k:k+12]) for k in range(0,len(ids),12))+'\n'
def wrench(X,force,application):
 """Minimum-norm nodal force distribution with exact force and moment resultants."""
 centre=X.mean(0);r=X-centre;F=np.asarray(force,float);moment=np.cross(np.asarray(application)-centre,F)
 J=np.eye(3)*np.sum(r*r)-r.T@r;omega=np.linalg.solve(J,moment);f=F/len(X)+np.cross(np.broadcast_to(omega,r.shape),r)
 assert np.linalg.norm(f.sum(0)-F)<1e-8 and np.linalg.norm(np.cross(r,f).sum(0)-moment)<1e-6
 return f,moment,centre

def parse_dat(path,ids,X,elem_ids,centres,loads,fix):
 pos={int(i):k for k,i in enumerate(ids)};epos={int(i):k for k,i in enumerate(elem_ids)};steps=[];current=None;mode=None;stress=[];stress_e=[];U=None;RF=[]
 def finish():
  if current is None:return
  assert U is not None and np.isfinite(U).all();sv=np.array(stress);assert len(sv)>0
  force=np.array(current['force']);direction=force/np.linalg.norm(force);sel=np.array([pos[int(i)] for i in current['load_node_ids']]);along=float((U[sel]@direction).mean());maxidx=int(np.argmax(np.linalg.norm(U,axis=1)))
  vm=np.sqrt(.5*((sv[:,0]-sv[:,1])**2+(sv[:,1]-sv[:,2])**2+(sv[:,2]-sv[:,0])**2)+3*(sv[:,3]**2+sv[:,4]**2+sv[:,5]**2));where=int(np.argmax(vm));reaction=np.array(RF).sum(0)
  assert np.linalg.norm(reaction+force)/np.linalg.norm(force)<.001,(reaction,force)
  nodeforces=np.array(current['nodal_forces']);compliance=float(np.sum(nodeforces*U[sel]));assert compliance>0
  steps.append(dict(id=current['id'],force_N=force.tolist(),force_point_mm=current['force_point'],load_nodes=len(sel),applied_moment_at_node_centroid_Nmm=current['moment'],load_centroid_mm=current['centroid'],load_force_sum_N=nodeforces.sum(0).tolist(),max_nodal_force_N=float(np.linalg.norm(nodeforces,axis=1).max()),mean_load_patch_deflection_along_force_mm=along,work_equivalent_deflection_mm=compliance/np.linalg.norm(force),compliance_Nmm=compliance,max_deflection_mm=float(np.linalg.norm(U[maxidx])),max_deflection_at_mm=X[maxidx].tolist(),reaction_N=reaction.tolist(),force_balance_relative_error=float(np.linalg.norm(reaction+force)/np.linalg.norm(force)),build_normal_max_tension_MPa=float(max(0,sv[:,0].max())),build_normal_max_compression_MPa=float(max(0,-sv[:,0].min())),von_mises_MPa=dict(max=float(vm.max()),p95=float(np.percentile(vm,95)),p99=float(np.percentile(vm,99)),max_element_centroid_mm=centres[epos[stress_e[where]]].tolist()),stress_integration_points=len(vm)))
  # Preserve nodal displacements and integration stress samples for plots/review, without rounding.
  np.savez_compressed(path.parent/(f'field-{len(steps):02d}.npz'),X=X,U=U,stress=sv,stress_element_ids=np.array(stress_e),element_ids=elem_ids,element_centres=centres)
 with path.open() as f:
  for line in f:
   low=line.strip().lower()
   if low.startswith('displacements ('):
    finish();current=loads[len(steps)];U=np.full_like(X,np.nan);mode='U';stress=[];stress_e=[];RF=[];continue
   if low.startswith('forces ('):mode='RF';continue
   if low.startswith('stresses ('):mode='S';continue
   a=line.split()
   if not a or not a[0].isdigit():continue
   if mode=='U' and len(a)==4:U[pos[int(a[0])]]=[float(x) for x in a[1:]]
   elif mode=='RF' and len(a)==4:RF.append([float(x) for x in a[1:]])
   elif mode=='S' and len(a)==8:stress_e.append(int(a[0]));stress.append([float(x) for x in a[2:]])
 finish();assert len(steps)==len(loads), (len(steps),len(loads));return steps

def solve(out,ids,X,ei,centres,support,force_mode,spec,threads,material="iso1800"):
 dest=out/f'{support}-{force_mode}';dest.mkdir(exist_ok=True)
 behind=X[:,1]<.10;top=X[behind,2].max();bottom=X[behind,2].min()
 if support=='all-pegs':mask=behind
 elif support=='face':mask=X[:,1]<=.16
 elif support=='hooks-only':mask=behind&(X[:,2]>top-14)
 elif support=='four-corners':mask=behind&((X[:,2]>top-14)|(X[:,2]<bottom+14))&(np.abs(X[:,0])>95)
 else:raise ValueError(support)
 fix=ids[mask];assert len(fix)>20;deck=['*INCLUDE,INPUT=../volume.inp',nset('NALL',ids),nset('FIX',fix),'*MATERIAL,NAME=ASA',('*ELASTIC\n1800,0.35' if material=='iso1800' else '*ELASTIC,TYPE=ENGINEERING CONSTANTS\n1965,2379,2379,0.30,0.30,0.35,815.9,815.9\n881.111111'),'*SOLID SECTION,ELSET=EALL,MATERIAL=ASA','*BOUNDARY','FIX,1,3'];loads=[]
 for q in spec['loads']:
  idx=np.flatnonzero(np.linalg.norm(X-np.array(q['point']),axis=1)<=q['radius']);assert len(idx)>=3
  assert not np.any(mask[idx]),'load overlaps fixed region'
  point=q['point'] if force_mode=='mouth' else q['physical_grip_point_mm']
  if force_mode=='mouth':f=np.tile(np.array(q['force'],float)/len(idx),(len(idx),1));centroid=X[idx].mean(0);moment=np.cross(X[idx]-centroid,f).sum(0)
  else:f,moment,centroid=wrench(X[idx],q['force'],point)
  loads.append(dict(q,force_point=point,load_node_ids=ids[idx].tolist(),nodal_forces=f.tolist(),moment=moment.tolist(),centroid=centroid.tolist()))
  deck+=['*STEP','*STATIC','*CLOAD,OP=NEW']
  for node,forces in zip(ids[idx],f):
   for dim,value in enumerate(forces):
    if value:deck.append(f'{int(node)},{dim+1},{value:.12g}')
  deck+=['*NODE PRINT,NSET=NALL','U','*NODE PRINT,NSET=FIX','RF','*EL PRINT,ELSET=EALL','S','*END STEP']
 (dest/'case.inp').write_text('\n'.join(deck)+'\n');start=time.monotonic()
 with (dest/'ccx.log').open('w') as log:subprocess.run(['ccx','case'],cwd=dest,env=dict(os.environ,OMP_NUM_THREADS=str(threads)),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=5400)
 steps=parse_dat(dest/'case.dat',ids,X,ei,centres,loads,fix)
 r=dict(support=support,force_mode=force_mode,nodes=len(ids),elements=len(ei),fixed_nodes=len(fix),fixed_node_bbox_mm=[X[mask].min(0).tolist(),X[mask].max(0).tolist()],material=(dict(E_MPa=1800,nu=.35) if material=='iso1800' else dict(E_installed_x_MPa=1965,E_installed_yz_MPa=2379,nu_xy_xz=.30,nu_yz=.35,G_xy_xz_MPa=815.9,G_yz_MPa=881.111111,reference='Polymaker ASA TDS modulus values; Poisson/shear values assumed; full-solid orthotropic sensitivity, not a measured print model')),seconds=time.monotonic()-start,loads=steps,input_deck_sha256=sha(dest/'case.inp'),solver_log_sha256=sha(dest/'ccx.log'))
 (dest/'result.json').write_text(json.dumps(r,indent=2)+'\n');print(support,force_mode,'done',round(r['seconds'],1),flush=True);return r

def main():
 p=argparse.ArgumentParser();p.add_argument('--step',type=Path,required=True);p.add_argument('--loads',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--h',type=float,required=True);p.add_argument('--algorithm',type=int,choices=[1,10],default=10);p.add_argument('--threads',type=int,default=8);p.add_argument('--suite',choices=['baseline','deep','transfer'],default='baseline');p.add_argument('--reuse',type=Path);p.add_argument('--material',choices=['iso1800','ortho-reference'],default='iso1800');p.add_argument('--radius-multiplier',type=float,default=1.);a=p.parse_args();a.step=a.step.resolve();a.out=a.out.resolve();a.out.mkdir(parents=True,exist_ok=True);spec=json.loads(a.loads.read_text());assert sha(a.step)==spec['installed_step_sha256']
 start=time.monotonic()
 if a.reuse:
  base=a.reuse.resolve();gate=json.loads((base/'mesh-quality.json').read_text());assert gate['passed'] and gate['inverted_elements']==0 and gate['connected_components']==1
  data=np.load(base/'mesh.npz');ids,X,ei,centres,volumes=[data[k] for k in ['ids','X','element_ids','element_centres','volumes']]
  assert sha(base/'mesh.npz')==gate['mesh_npz_sha256']
  for name in ['volume.inp','mesh.npz']:
   target=a.out/name
   if not target.exists():target.symlink_to(base/name)
 else:ids,X,ei,centres,volumes=mesh(a.step,a.out,a.h,a.algorithm)
 for q in spec['loads']:q['radius']*=a.radius_multiplier
 jobs=[('all-pegs','mouth')]
 if a.suite=='transfer':jobs += [('all-pegs','grip-wrench')]
 if a.suite=='deep':jobs += [('all-pegs','grip-wrench'),('hooks-only','grip-wrench'),('four-corners','grip-wrench'),('face','grip-wrench')]
 results=[solve(a.out,ids,X,ei,centres,sup,mode,spec,a.threads,a.material) for sup,mode in jobs]
 r=dict(step_sha256=sha(a.step),source_sha256=sha(__file__),loads_sha256=sha(a.loads),h_requested_mm=a.h,mesh_algorithm=a.algorithm,nodes=len(ids),elements=len(ei),linear_tetra_mesh_volume_mm3=float(volumes.sum()),minimum_element_volume_mm3=float(volumes.min()),gmsh_version=subprocess.check_output(['gmsh','-version'],stderr=subprocess.STDOUT,text=True).strip(),ccx_version=subprocess.run(['ccx','-v'],capture_output=True,text=True,check=False,timeout=30).stdout.strip(),suite=a.suite,material_scenario=a.material,load_radius_multiplier=a.radius_multiplier,mesh_reused_from=str(a.reuse) if a.reuse else None,seconds=time.monotonic()-start,results=results,limitations=['Solid isotropic ASA; infill and layer interfaces absent','Clamps are ideal boundary sensitivities, not contact with elastic pegboard','Grip wrench is an equivalent resultant on a mouth patch, not verified tool/socket contact','Stress maxima may be singular at sharp edges and ideal clamps; do not infer a load rating','Stress percentiles are unweighted integration-point percentiles'])
 (a.out/'summary.json').write_text(json.dumps(r,indent=2)+'\n');print('COMPLETE',a.out,flush=True)
if __name__=='__main__':main()
