"""P06 export adapter: bounded 0.00001 mm mesh weld; native geometry unchanged.
Historical faceted body leaves two zero-area triangles after top planing. The
shared mesh exporter rejects it. Round/weld and remove only degenerate/duplicate
triangles, assert closed manifold; do not alter the frozen flat-top generator.
"""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
import FreeCAD as A
import Mesh,MeshPart
import flat_top as F

def write(shape,path,lin=.005):
 mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=lin,AngularDeflection=.087,Relative=False);vv,ff=mesh.Topology;v=np.array([[p.x,p.y,p.z] for p in vv]);f=np.array(ff);q=np.round(v,5);maximum=float(np.linalg.norm(q-v,axis=1).max());verts,idx=np.unique(q,axis=0,return_inverse=True);faces=idx[f];keep=(faces[:,0]!=faces[:,1])&(faces[:,0]!=faces[:,2])&(faces[:,1]!=faces[:,2]);faces=faces[keep];_,unique=np.unique(np.sort(faces,axis=1),axis=0,return_index=True);faces=faces[np.sort(unique)];tri=verts[faces];mesh=Mesh.Mesh([[F.V(*p) for p in t] for t in tri]);mesh.harmonizeNormals();mesh.write(str(path));read=Mesh.Mesh(str(path));assert read.isSolid() and not read.hasNonManifolds()
 return dict(file=path.name,facets=read.CountFacets,volume_error_fraction=abs(abs(read.Volume)-shape.Volume)/shape.Volume,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bounded_export_weld=dict(grid_mm=.00001,max_pre_serialization_vertex_displacement_mm=maximum,removed_degenerate_or_duplicate_triangles=len(f)-len(faces),native_shape_unchanged=True))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('spec');p.add_argument('out');a=p.parse_args();F.K.write=write;F.build(json.loads(Path(a.spec).read_text()),Path(a.out));r=Path(a.out)/'report.json';d=json.loads(r.read_text());d['input_hashes'][str(Path(__file__).resolve())]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();r.write_text(json.dumps(d,indent=2)+'\n')
