"""Sample a native-export mesh once for a coarse truss surrogate."""
from pathlib import Path
import json,itertools,numpy as np,trimesh
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'.local-runtime/hx05-density-v1';pitch=10.
for ident in ['HX05C','HX05B','HX05A']:
 mesh=trimesh.load(WORK/ident/'print-body-closed.stl',force='mesh',process=True);assert mesh.is_volume
 pc=json.loads((WORK/ident/'check.json').read_text())['print_pose'];mesh.vertices=(mesh.vertices-np.array(pc['translation']))@np.array(pc['rotation'])
 low,high=mesh.bounds;origins=np.array([low[0]+pitch/2,2.5,low[2]+pitch/2]);counts=np.ceil((high-origins)/pitch).astype(int)+1
 indices=np.array(list(itertools.product(*(range(n) for n in counts))));points=indices*pitch+origins
 def inside(p):
  return np.concatenate([mesh.contains(chunk) for chunk in np.array_split(p,max(1,len(p)//200+1))])
 mask=inside(points);points=points[mask];indices=indices[mask]
 lookup={tuple(q):n for n,q in enumerate(indices)};edges=[]
 offsets=[q for q in itertools.product([-1,0,1],repeat=3) if q>(0,0,0)]
 for n,q in enumerate(indices):
  for d in offsets:
   m=lookup.get(tuple(q+np.array(d)))
   if m is not None:edges.append([n,m])
 edges=np.array(edges);midpoints=points[edges].mean(1);edges=edges[inside(midpoints)]
 path=WORK/ident/'lattice.json';path.write_text(json.dumps(dict(id=ident,pitch_mm=pitch,points=points.tolist(),edges=edges.tolist(),scope='10 mm truss lattice sampled from the validated native-export mesh (0.025 mm deflection). Small bores/vents, print walls and contact details unresolved. Fully clamped plate-front nodes are optimistic. Comparative surrogate only.'))+'\n')
 print(ident,len(points),'nodes',len(edges),'edges',flush=True)
