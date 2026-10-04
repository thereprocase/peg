import json,hashlib
from pathlib import Path
import numpy as np,trimesh,manifold3d as M
R=Path('/home/repro/code/peg-gallery-current-mounts');D=R/'bench/reviews/gallery-current-mounts-flat-top-v2/P09-36';p=D/'installed.stl';m=trimesh.load(p);a=M.Manifold(M.Mesh(np.float32(m.vertices),np.uint32(m.faces)));sections=[]
for z in [-2.4,-4.4,-9.4]:
 polygons=a.slice(z).to_polygons();areas=[float(np.sum(q[:,0]*np.roll(q[:,1],-1)-q[:,1]*np.roll(q[:,0],-1))/2) for q in polygons];holes=[q for q,v in zip(polygons,areas) if v<0];sections.append({'z_mm':z,'openings':len(holes),'opening_xy_spans_mm':[np.ptp(q,axis=0).tolist() for q in holes]})
d={'pass':all(s['openings']==36 for s in sections),'input_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sections':sections,'scope':'Three horizontal mesh sections through the seating bank have 36 clear openings. Original body preservation is additionally established by exact CAD checks; no claim that every hole has uniform depth.'};(D/'seat-checks.json').write_text(json.dumps(d,indent=2)+'\n');print(d['pass'])
