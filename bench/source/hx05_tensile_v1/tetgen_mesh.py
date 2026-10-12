"""Bounded alternative analysis meshing; never changes manufacturing assets."""
from pathlib import Path
import argparse,json,time
import numpy as np,trimesh,tetgen
from concurrent.futures import ProcessPoolExecutor

def init_surface(vertices,faces):
    global distance_surface
    distance_surface=trimesh.Trimesh(vertices,faces,process=False)

def distances(points):
    return trimesh.proximity.closest_point(distance_surface,points)[1]

def sampled_distance(a,b):
    samples=np.vstack([a.vertices,a.triangles.mean(1)])
    with ProcessPoolExecutor(max_workers=12,initializer=init_surface,initargs=(b.vertices,b.faces)) as pool:
        return max(float(v.max()) for v in pool.map(distances,(samples[i:i+1000] for i in range(0,len(samples),1000))))

def main(folder,maxvolume,faces):
    folder=Path(folder); surface=trimesh.load(folder/'surface-tensile.stl',force='mesh'); original=surface.copy()
    if faces>0: surface=surface.simplify_quadric_decimation(face_count=faces,aggression=5)
    elif faces==-1:
        import pyfqmr
        reducer=pyfqmr.Simplify();reducer.setMesh(surface.vertices,surface.faces)
        reducer.simplify_mesh_lossless(verbose=False,epsilon=1e-6,max_iterations=1000)
        vertices,triangles,_=reducer.getMesh();surface=trimesh.Trimesh(vertices,triangles,process=True)
    assert surface.is_watertight and surface.is_winding_consistent
    approximation=dict(relative_surface_volume_error=float(abs(surface.volume-original.volume)/original.volume),sampled_original_to_analysis_mm=sampled_distance(original,surface) if faces else 0.,sampled_analysis_to_original_mm=sampled_distance(surface,original) if faces else 0.)
    print('Surface approximation',json.dumps(approximation),flush=True)
    assert approximation['relative_surface_volume_error']<.001
    assert max(approximation['sampled_original_to_analysis_mm'],approximation['sampled_analysis_to_original_mm'])<.05,'Excessive analysis-surface deviation'
    tag=f'tetgen-v{maxvolume:g}'+(f'-f{faces}' if faces else '')
    start=time.monotonic(); mesher=tetgen.TetGen(np.array(surface.vertices),np.asarray(surface.faces,dtype=np.int32))
    X,tets,_,_=mesher.tetrahedralize(quality=True,minratio=2,mindihedral=0,maxvolume=maxvolume,fixedvolume=True,steinerleft=300000,facesout=True,docheck=True,quiet=False)
    groups=tets[:,[[0,1,2],[0,3,1],[0,2,3],[1,3,2]]].reshape(-1,3)
    _,idx,count=np.unique(np.sort(groups,axis=1),axis=0,return_index=True,return_counts=True)
    tri=groups[idx[count==1]]
    corners=X[tets];volume=np.abs(np.linalg.det(corners[:,1:]-corners[:,:1]))/6
    edges=np.array([np.linalg.norm(corners[:,a]-corners[:,b],axis=1) for a,b in [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]])
    quality=12*(3*volume)**(2/3)/(edges**2).sum(0)
    out=dict(nodes=len(X),tets=len(tets),minimum_volume_mm3=float(volume.min()),minimum_mean_ratio=float(quality.min()),volume_mm3=float(volume.sum()),surface_volume_mm3=float(surface.volume),volume_error_fraction=float(abs(volume.sum()-surface.volume)/surface.volume),seconds=time.monotonic()-start,maxvolume_mm3=maxvolume,simplified_surface_faces=faces,approximation=approximation,accepted_for_analysis=False)
    dest=folder/f'{tag}.msh'
    with dest.open('w') as f:
        f.write('$MeshFormat\n2.2 0 8\n$EndMeshFormat\n$Nodes\n'+str(len(X))+'\n')
        for j,p in enumerate(X):f.write(f'{j+1} {p[0]:.17g} {p[1]:.17g} {p[2]:.17g}\n')
        f.write('$EndNodes\n$Elements\n'+str(len(tri)+len(tets))+'\n')
        for j,p in enumerate(tri):f.write(f'{j+1} 2 0 '+' '.join(str(k+1) for k in p)+'\n')
        for j,p in enumerate(tets):f.write(f'{len(tri)+j+1} 4 0 '+' '.join(str(k+1) for k in p)+'\n')
        f.write('$EndElements\n')
    (folder/f'{tag}-check.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder');p.add_argument('--maxvolume',type=float,default=8);p.add_argument('--faces',type=int,default=0);a=p.parse_args();main(a.folder,a.maxvolume,a.faces)
