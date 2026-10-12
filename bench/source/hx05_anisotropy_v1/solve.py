"""One continuum solve for a fixed outer body and equal-volume density planes."""
from pathlib import Path
import argparse,json,time,resource
import numpy as np
from scipy.sparse import coo_matrix,triu
from pypardiso import PyPardisoSolver
from model import read_msh,tet_data,elasticity,load_cases,fixed_and_shell,planes_mask,boundary

def weighted_q(x,weight,q=.99):
 order=np.argsort(x);v=x[order];w=weight[order];return float(v[np.searchsorted(np.cumsum(w),q*w.sum())])

def main(folder,clock,rz,bulk,support='roots'):
 folder=Path(folder);ident=folder.name;rack=next(r for r in json.loads((folder.parent/'config.json').read_text())['racks'] if r['id']==ident)
 start=time.monotonic();X,tri,tets=read_msh(folder/'front-4mm.msh');centres,vol,B,edof=tet_data(X,tets)
 F,labels,patches=load_cases(X,tri,rack);fix_nodes=boundary(X,rack,support);fixed=fixed_and_shell(X,tri,centres,rack)
 base=planes_mask(centres,rack,0,rack['density_parameters']['RibWidth']);target=float(vol[base&~fixed].sum())
 # Normalize only added rib material, avoiding a mass advantage for a clock.
 low,high=1.5,12.;width=rack['density_parameters']['RibWidth']
 if clock:
  for _ in range(12):
   width=(low+high)/2;trial=planes_mask(centres,rack,clock,width)
   if vol[trial&~fixed].sum()<target:low=width
   else:high=width
 ribs=planes_mask(centres,rack,clock,width);dense=fixed|ribs;rho=np.where(dense,1.,bulk);D=elasticity(rz)
 print(ident,clock,rz,bulk,'assemble',len(X),len(tets),flush=True)
 local=np.einsum('eai,ab,ebj,e->eij',B,D,B,vol*rho,optimize=True)
 rows=np.repeat(edof,12,axis=1).ravel();cols=np.tile(edof,(1,12)).ravel()
 K=coo_matrix((local.ravel(),(rows,cols)),shape=(len(X)*3,)*2).tocsr();K.sum_duplicates();del local,rows,cols
 fix=np.repeat(fix_nodes,3);free=np.flatnonzero(~fix);Kf=K[free][:,free].tocsr();A=triu(Kf,format='csr');A.sort_indices()
 print(ident,clock,'factor',len(free),Kf.nnz,flush=True)
 solver=PyPardisoSolver(mtype=2);Uf=solver.solve(A,np.asfortranarray(F[free]));U=np.zeros_like(F);U[free]=Uf
 residual=Kf@Uf-F[free];error=np.linalg.norm(residual,axis=0)/np.maximum(np.linalg.norm(F[free],axis=0),1e-20);assert error.max()<1e-6,('Residual gate',error.max())
 reaction=K@U-F;results=[]
 for j,label in enumerate(labels):
  f=F[:,j].reshape(-1,3);r=reaction[:,j].reshape(-1,3);force=f.sum(0);moment=np.cross(X,f).sum(0);rf=r[fix_nodes].sum(0);rm=np.cross(X[fix_nodes],r[fix_nodes]).sum(0)
  assert np.linalg.norm(rf+force)<1e-5 and np.linalg.norm(rm+moment)<1e-3,(label,'Equilibrium failed')
  strain=np.einsum('eai,ei->ea',B,U[edof,j]);stress=(strain@D.T)*rho[:,None]
  normal=np.maximum(stress[:,0],0);shear=np.hypot(stress[:,4],stress[:,5])
  away=(centres[:,1]>7)&(np.linalg.norm(centres-np.array(rack['tools'][int(j//3)]['mouth']),axis=1)>5)
  layer=np.hypot(normal/rz,shear/rz)
  results.append(dict(case=label,compliance=float(F[:,j]@U[:,j]),layer_normal_tension_p99=weighted_q(normal[away],vol[away]),layer_shear_p99=weighted_q(shear[away],vol[away]),normalized_layer_index_p99=weighted_q(layer[away],vol[away]),residual_relative=float(error[j]),force_balance_error=float(np.linalg.norm(rf+force)),moment_balance_error=float(np.linalg.norm(rm+moment))))
 result=dict(id=ident,clock_deg=clock,layer_stiffness_ratio=rz,bulk_stiffness_ratio=bulk,support=support,rib_width_mm=width,added_rib_volume_mm3=float(vol[ribs&~fixed].sum()),target_added_rib_volume_mm3=target,budget_error_fraction=float(abs(vol[ribs&~fixed].sum()-target)/max(target,1)),dense_volume_fraction=float(vol[dense].sum()/vol.sum()),nodes=len(X),tetrahedra=len(tets),tet_volume_mm3=float(vol.sum()),minimum_tet_volume_mm3=float(vol.min()),load_patches=patches,loads=results,seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='Linear C3D4 continuum, unit force/torque wrenches on resolved bore patches. Normalized anisotropic and bulk stiffness assumptions; strength index is comparative. Front-domain peg-root clamp idealization; no contact, nonlinear failure or load rating.')
 dest=folder/'results';dest.mkdir(exist_ok=True);name=f'clock-{clock:g}-rz-{rz:g}-bulk-{bulk:g}-{support}.json';(dest/name).write_text(json.dumps(result,indent=2)+'\n');print(ident,name,'DONE',result['seconds'],flush=True)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('folder');p.add_argument('--clock',type=float,default=0);p.add_argument('--rz',type=float,default=.65);p.add_argument('--bulk',type=float,default=.04);p.add_argument('--support',choices=['roots','face'],default='roots');a=p.parse_args();main(a.folder,a.clock,a.rz,a.bulk,a.support)
