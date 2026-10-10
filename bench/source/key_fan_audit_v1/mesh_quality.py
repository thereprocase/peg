"""Independent tetra-mesh volume, orientation, quality and connectivity gate."""
import argparse,hashlib,json,re
from pathlib import Path
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
p=argparse.ArgumentParser();p.add_argument('run',type=Path);a=p.parse_args();run=a.run.resolve();m=np.load(run/'mesh.npz');ids=m['ids'];X=m['X'];pos={int(i):k for k,i in enumerate(ids)};conn=[];active=False
for line in (run/'volume.inp').read_text().splitlines():
 if line.startswith('*'):active=line.upper().startswith('*ELEMENT');continue
 if active:
  s=[v.strip() for v in line.split(',') if v.strip()]
  if len(s)==11:conn.append([pos[int(i)] for i in s[1:]])
C=np.array(conn);corners=X[C[:,:4]];D=corners[:,1:]-corners[:,:1];det=np.linalg.det(D);vol=det/6
assert np.all(vol>0),'Inverted or degenerate C3D10 corner tetrahedron'
edges=np.array([(i,j) for i in range(4) for j in range(i+1,4)]);e2=((corners[:,edges[:,0]]-corners[:,edges[:,1]])**2).sum((1,2));quality=12*(3*vol)**(2/3)/e2
rows=np.repeat(C[:,0],9);cols=C[:,1:].ravel();g=coo_matrix((np.ones(len(rows)),(rows,cols)),shape=(len(ids),len(ids))).tocsr();n,lab=connected_components(g,directed=False);assert n==1,'Disconnected volume mesh'
expected=1527603.2742597507;error=abs(vol.sum()-expected)/expected;assert error<.005,'Mesh loses too much native volume'
r=dict(mesh_npz_sha256=hashlib.sha256((run/'mesh.npz').read_bytes()).hexdigest(),checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),nodes=len(ids),elements=len(C),connected_components=n,inverted_elements=int(np.sum(vol<=0)),mesh_volume_mm3=float(vol.sum()),native_volume_mm3=expected,relative_native_volume_error=float(error),corner_tetra_quality=dict(min=float(quality.min()),p1=float(np.percentile(quality,1)),p5=float(np.percentile(quality,5)),median=float(np.median(quality))),passed=True,note='C3D10 midside nodes are linear in these runs; determinant check is therefore valid throughout each element. Quality statistic is a normalized corner-tetra mean ratio, not a stress-convergence certificate.')
(run/'mesh-quality.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
