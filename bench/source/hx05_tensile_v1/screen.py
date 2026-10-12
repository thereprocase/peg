"""Provisional tensile screen of connected-v3 masks; not a load qualification.

Installed X is the print layer normal. Coarse front-domain tetrahedra and
homogenized bulk cannot resolve every bead/interface; report raw maxima and
sampling errors, never substitute a percentile for the minimum safety factor.
"""
from pathlib import Path
import argparse, json, time, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import trimesh
from scipy.sparse import coo_matrix, triu
from pypardiso import PyPardisoSolver
from model import read_msh, tet_data, elasticity, load_cases, boundary

def stress_tensor(s):
    T=np.zeros((len(s),3,3)); T[:,0,0]=s[:,0]; T[:,1,1]=s[:,1]; T[:,2,2]=s[:,2]
    T[:,1,2]=T[:,2,1]=s[:,3]; T[:,0,2]=T[:,2,0]=s[:,4]; T[:,0,1]=T[:,1,0]=s[:,5]
    return T

def load_surface(path):
    global query_body
    query_body=trimesh.load(path,force='mesh')

def surface_distance(points):
    return trimesh.proximity.closest_point(query_body,points)[1]

def prepare(folder, source, mesh_name=None, jobs=1):
    folder=Path(folder); source=Path(source)
    mesh=folder/mesh_name if mesh_name else folder/('front-delaunay.msh' if folder.name=='HX05A' else 'front-4mm.msh')
    X,tri,tets=read_msh(mesh); centres,vol,_,_=tet_data(X,tets)
    pose=json.loads((source/'draft-check.json').read_text()); R=np.array(pose['rotation']); t=np.array(pose['translation'])
    p=centres@R.T+t
    body=trimesh.load(source/'print-drafted-body-closed.stl',force='mesh')
    # Exact nearest-triangle distance, chunked to bound query memory.
    distances=[]
    with ProcessPoolExecutor(max_workers=jobs,initializer=load_surface,initargs=(str(source/'print-drafted-body-closed.stl'),)) as pool:
        for i,d in enumerate(pool.map(surface_distance,(p[i:i+1000] for i in range(0,len(p),1000)))):
            distances.extend(d)
            if i%100==0: print(folder.name,'surface distance',i*1000,len(p),flush=True)
    distances=np.asarray(distances)
    # Nominal 3 x 0.42 mm walls, 5 x 0.2 mm top/bottom assumption.
    skin=(distances<=1.26)|(p[:,2]<=1.)|(p[:,2]>=body.bounds[1,2]-1.)
    dense=skin.copy(); checks=[]
    for role in ['foundation','mounts','sockets','ribs']:
        m=trimesh.load(source/f'print-modifier-{role}.stl',force='mesh')
        assert m.is_watertight,(folder.name,role,'not watertight')
        inside=m.contains(p); dense|=inside
        checks.append(dict(role=role,centroid_volume_mm3=float(vol[inside].sum()),raw_mesh_volume_mm3=float(m.volume)))
    tag=mesh.stem if mesh_name else 'connected'
    np.savez_compressed(folder/f'{tag}-mask.npz',dense=dense,skin=skin,distances=distances)
    out=dict(id=folder.name,tetrahedra=len(tets),nodes=len(X),domain_volume_mm3=float(vol.sum()),minimum_tet_volume_mm3=float(vol.min()),dense_sampled_volume_mm3=float(vol[dense].sum()),skin_volume_mm3=float(vol[skin].sum()),modifiers=checks,assumed_perimeter_thickness_mm=1.26,assumed_top_bottom_thickness_mm=1.,scope='Centroid sampling, not resolved bead geometry; raw modifier volume includes material outside body.')
    (folder/f'{tag}-mask-check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out),flush=True)

def solve(folder, rz, bulk, support, mesh_name=None,bending=False):
    folder=Path(folder); rack=next(r for r in json.loads((folder.parent/'config.json').read_text())['racks'] if r['id']==folder.name)
    mesh=folder/mesh_name if mesh_name else folder/('front-delaunay.msh' if folder.name=='HX05A' else 'front-4mm.msh')
    X,tri,tets=read_msh(mesh); centres,vol,B,edof=tet_data(X,tets)
    tag=mesh.stem if mesh_name else 'connected'
    dense=np.load(folder/f'{tag}-mask.npz')['dense']; rho=np.where(dense,1.,bulk)
    edges=np.array([np.linalg.norm(X[tets[:,a]]-X[tets[:,b]],axis=1) for a,b in [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]])
    quality=12*(3*vol)**(2/3)/(edges**2).sum(0)
    D=elasticity(rz); F,labels,patches=load_cases(X,tri,rack,bending=bending)
    # Conservative service assumption: 5 N per key, applied at grip center,
    # plus 5.1 N uniformly distributed holder weight (actual inch ~0.520 kg).
    service=sum((5*F[:,j] for j in range(0,len(labels),3)),np.zeros(len(X)*3))
    for k in range(4): np.add.at(service,edof[:,3*k+2],-5.1*vol/vol.sum()/4)
    cases=[service]; names=['all_keys_5N_each_and_holder_5.1N']
    for j in range(0,len(labels),3):
        modes=[('pull100N',100*F[:,j+1]),('twist1Nm',1000*F[:,j+2]),('down20N',20*F[:,j])]
        if bending:modes=[('down20N',20*F[:,j]),('across_layers20N',20*F[:,j+1]),('outboard20N',20*F[:,j+2])]
        for mode,vector in modes:
            cases.append(service+vector); names.append(labels[j].split(':')[0]+':'+mode)
    F=np.asarray(cases).T
    fixed_nodes=boundary(X,rack,support); free=np.flatnonzero(~np.repeat(fixed_nodes,3))
    local=np.einsum('eai,ab,ebj,e->eij',B,D,B,vol*rho,optimize=True)
    rows=np.repeat(edof,12,axis=1).ravel(); cols=np.tile(edof,(1,12)).ravel()
    K=coo_matrix((local.ravel(),(rows,cols)),shape=(len(X)*3,)*2).tocsr(); K.sum_duplicates(); del local,rows,cols
    Kf=K[free][:,free].tocsr(); A=triu(Kf,format='csr'); A.sort_indices()
    solver=PyPardisoSolver(mtype=2); Uf=solver.solve(A,np.asfortranarray(F[free])); U=np.zeros_like(F); U[free]=Uf
    err=np.linalg.norm(Kf@Uf-F[free],axis=0)/np.maximum(np.linalg.norm(F[free],axis=0),1e-20)
    reaction=K@U-F; results=[]
    for j,name in enumerate(names):
        strain=np.einsum('eai,ei->ea',B,U[edof,j]); s=strain@D.T
        # Dense-region stress is actual continuum solid stress. Sparse phase:
        # nominal stress / 5% solid fraction, an unvalidated gyroid estimate.
        s*=np.where(dense,1.,bulk/.05)[:,None]
        T=stress_tensor(s); principal=np.maximum(np.linalg.eigvalsh(T)[:,-1],0)
        layer=np.maximum(s[:,0],0)
        # Separate in-plane tensile eigenvalue and layer-normal tensile stress.
        inplane=np.maximum(np.linalg.eigvalsh(T[:,1:,1:])[:,-1],0)
        index=np.maximum.reduce([principal/30.,layer/30.,inplane/38.6])
        idx=int(np.argmax(index)); didx=int(np.argmax(np.where(dense,index,-1)))
        f=F[:,j].reshape(-1,3); r=reaction[:,j].reshape(-1,3)
        force_error=np.linalg.norm(f.sum(0)+r[fixed_nodes].sum(0))
        moment_error=np.linalg.norm(np.cross(X,f).sum(0)+np.cross(X[fixed_nodes],r[fixed_nodes]).sum(0))
        regular=(quality>=.01)&(vol>=1e-6); ri=int(np.argmax(np.where(regular,index,-1)))
        results.append(dict(case=name,raw_strength_to_peak_stress_ratio=float(1/index[idx]),peak_principal_MPa=float(principal[idx]),peak_layer_normal_MPa=float(layer.max()),peak_interlayer_shear_MPa=float(np.hypot(s[:,4],s[:,5]).max()),critical_position_mm=centres[idx].tolist(),critical_is_dense=bool(dense[idx]),critical_tet_volume_mm3=float(vol[idx]),critical_tet_mean_ratio=float(quality[idx]),regular_element_peak_MPa=float(principal[ri]),regular_element_position_mm=centres[ri].tolist(),dense_only_factor=float(1/index[didx]),dense_critical_position_mm=centres[didx].tolist(),residual=float(err[j]),force_error_N=float(force_error),moment_error_Nmm=float(moment_error)))
    out=dict(accepted_for_fracture_factor=False,id=folder.name,mesh=mesh.name,rz=rz,bulk_stiffness_ratio=bulk,support=support,passed_equilibrium=bool(err.max()<1e-6 and max(x['force_error_N'] for x in results)<1e-5 and max(x['moment_error_Nmm'] for x in results)<1e-3),nodes=len(X),tetrahedra=len(tets),minimum_mean_ratio=float(quality.min()),regular_elements=int(regular.sum()),loads=results,scope='Unconverged preliminary tensile-only screen, not a whole-holder safety factor. Rear pegs and contact omitted, centroid mask sampling, assumed wall thickness and bulk homogenization. Regular-element peak is diagnostic, not a replacement minimum factor. Shear, creep, impact, buckling and joint failures not qualified.')
    suffix='-'+mesh.stem if mesh_name else ''
    if bending:suffix+='-bending'
    dest=folder/f'tensile-rz{rz}-bulk{bulk}-{support}{suffix}.json'; dest.write_text(json.dumps(out,indent=2)+'\n'); print(dest, 'DONE',out['passed_equilibrium'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('folder'); p.add_argument('--prepare'); p.add_argument('--mesh'); p.add_argument('--bending',action='store_true'); p.add_argument('--jobs',type=int,default=1); p.add_argument('--rz',type=float,default=.9); p.add_argument('--bulk',type=float,default=.025); p.add_argument('--support',choices=['roots','face'],default='roots'); a=p.parse_args()
    if a.prepare: prepare(a.folder,a.prepare,a.mesh,a.jobs)
    else: solve(a.folder,a.rz,a.bulk,a.support,a.mesh,a.bending)
