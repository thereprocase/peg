from pathlib import Path
import json,hashlib
import numpy as np, trimesh,manifold3d as M
R=Path('/home/repro/code/peg-gallery-current-mounts');S=R/'bench/source/gallery_current_mounts_v1';D=R/'bench/reviews/gallery-current-mounts-v1/inputs'
for id in ['P01','P02']:
 p=S/(id+'.json');spec=json.loads(p.read_text());src=R/f'docs/gallery/pegstr/{id}/model.stl';m=trimesh.load(src,force='mesh');a=M.Manifold(M.Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)));assert a.status()==M.Error.NoError
 b=a.trim_by_plane([0,1,0],.151);v=b.to_mesh();q=trimesh.Trimesh(v.vert_properties[:,:3],v.tri_verts,process=True);assert q.is_watertight
 out=D/(id+'-body-y0151.stl');q.export(out);spec.update(original_step=spec['input'],original_step_sha256=spec['input_sha256'],original_mesh=str(src),original_mesh_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),input=str(out),input_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),preparation='Historical faceted STEP Boolean returns empty at Y=.15 and invalid solid at .151. Exact published installed STL clipped by manifold at .151; one micron of full back wall restored by the receiver. No seat remeshing or smoothing.',preparation_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest());p.write_text(json.dumps(spec,indent=2)+'\n');print(id,q.volume,flush=True)
