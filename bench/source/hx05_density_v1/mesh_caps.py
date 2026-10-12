"""Propose only tiny planar tessellation-gap caps using existing mesh vertices.
Native face validation is required before any repaired mesh is packaged.
"""
from pathlib import Path
import sys,json,numpy as np,trimesh
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'.local-runtime/hx05-density-v1'
def cross2(a,b):return a[0]*b[1]-a[1]*b[0]
receipts=[]
for ident in ['HX05C','HX05B','HX05A']:
 for name in (['print-drafted-body'] if '--draft' in sys.argv else (['print-body','print-solid-core'] if '--baseline' in sys.argv else ['print-structural-body','print-selected-core'])):
  src=WORK/ident/(name+'-fine.stl');mesh=trimesh.load(src,force='mesh',process=True)
  keep=mesh.nondegenerate_faces(height=1e-10);removed_area=float(mesh.area_faces[~keep].sum());removed_count=int((~keep).sum());assert removed_area<1e-8
  mesh.update_faces(keep)
  mesh.remove_unreferenced_vertices()
  counts=np.bincount(mesh.edges_unique_inverse);boundary=mesh.edges_unique[counts==1];adj={}
  for a,b in boundary:adj.setdefault(int(a),[]).append(int(b));adj.setdefault(int(b),[]).append(int(a))
  assert all(len(v)==2 for v in adj.values()),(ident,name,'Non-cycle boundary')
  unused=set(adj);caps=[];loops=[]
  existing_edges={tuple(edge) for edge in mesh.edges_unique.tolist()}
  while unused:
   start=min(unused);loop=[start];previous=None;current=start
   while True:
    next_=next(v for v in adj[current] if v!=previous)
    if next_==start:break
    loop.append(next_);previous,current=current,next_
   unused-=set(loop)
   # Boundary orientation is taken from the existing face; new triangles oppose it.
   directed=mesh.edges
   if np.any(np.all(directed==[loop[0],loop[1]],axis=1)):loop=loop[::-1]
   points=mesh.vertices[loop];centroid=points.mean(axis=0);_,singular,basis=np.linalg.svd(points-centroid)
   assert singular[-1]<2e-5,(ident,name,'Non-planar boundary')
   assert np.linalg.norm(np.ptp(points,axis=0))<2.,(ident,name,'Large boundary')
   projected=(points-centroid)@basis[:2].T
   signed=sum(cross2(projected[(i+1)%len(loop)]-projected[i],projected[(i+2)%len(loop)]-projected[(i+1)%len(loop)]) for i in range(len(loop)))
   polygon_area=abs(np.sum(projected[:,0]*np.roll(projected[:,1],-1)-projected[:,1]*np.roll(projected[:,0],-1)))/2
   assert polygon_area<.02,(ident,name,'Large missing face area',polygon_area)
   # Ear-clipping in the fitted plane; no new vertices or vertex movement.
   left=list(range(len(loop)));winding=np.sign(np.sum(projected[:,0]*np.roll(projected[:,1],-1)-projected[:,1]*np.roll(projected[:,0],-1)))
   triangles=[]
   while len(left)>3:
    found=False
    for j,b in enumerate(left):
     a,c=left[j-1],left[(j+1)%len(left)];pa,pb,pc=projected[[a,b,c]]
     if cross2(pb-pa,pc-pb)*winding<=1e-12:continue
     if tuple(sorted((loop[a],loop[c]))) in existing_edges:continue
     def inside(p):
      return all(cross2(q-p_,p-p_)*winding>=-1e-12 for p_,q in [(pa,pb),(pb,pc),(pc,pa)])
     if any(inside(projected[k]) for k in left if k not in [a,b,c]):continue
     triangles.append([loop[a],loop[b],loop[c]]);left.pop(j);found=True;break
    assert found,(ident,name,'Cannot triangulate boundary')
   triangles.append([loop[k] for k in left]);caps.extend(triangles)
   loops.append(dict(vertices=len(loop),area_mm2=polygon_area,triangles_xyz=mesh.vertices[triangles].tolist()))
  old_vertices=mesh.vertices.copy();mesh.faces=np.vstack([mesh.faces,np.array(caps,dtype=int)])
  assert np.array_equal(old_vertices,mesh.vertices)
  after_counts=np.bincount(mesh.edges_unique_inverse);print(ident,name,'caps',len(caps),'edge counts',np.unique(after_counts,return_counts=True),flush=True)
  assert mesh.is_watertight and mesh.is_volume,(ident,name,'Caps failed manifold gate',mesh.is_watertight,mesh.is_winding_consistent)
  mesh.export(WORK/ident/(name+'-closed.stl'))
  receipts.append(dict(id=ident,name=name,loops=loops,patches=len(loops),new_triangles=len(caps),vertices_moved=False,watertight=True,zero_area_triangles_removed=removed_count,removed_area_mm2=removed_area))
(WORK/'mesh-cap-candidates.json').write_text(json.dumps(receipts,indent=2)+'\n')
print('Tiny planar caps proposed; native face validation REQUIRED')
