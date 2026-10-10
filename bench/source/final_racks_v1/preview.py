"""Compact display meshes from the exact native final model; downloads remain full resolution."""
from pathlib import Path
import sys,gzip,json,hashlib
import FreeCAD as A,Part,MeshPart
import numpy as np,trimesh
import build_short as H
out=Path(sys.argv[1]);dest=Path(sys.argv[2]);dest.mkdir(parents=True,exist_ok=True)
shape=Part.Shape();shape.read(str(out/'installed.step'));lo=H.SH.Layout(H.LAYOUT['x']);keys=H.ref_tools(lo)
X=np.array([[-.001,0,0,0],[0,0,.001,0],[0,.001,0,0],[0,0,0,1]])
def mesh(s):
 m=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.3,Relative=False);p,f=m.Topology
 t=trimesh.Trimesh([[q.x,q.y,q.z] for q in p],f,process=True)
 if len(t.faces)>16000:t=t.simplify_quadric_decimation(face_count=16000)
 t.apply_transform(X);return t
holder=mesh(shape);tool=mesh(keys)
for mode in ('installed','loaded','print'):
 s=trimesh.Scene();h=holder.copy();h.visual.vertex_colors=[60,148,138,255]
 if mode=='print':
  # Conjugate exact installed-to-print matrix into the display frame.
  pose=np.array(json.loads((out/'pose.json').read_text())).reshape(4,4);h.apply_transform(X@pose@np.linalg.inv(X))
 s.add_geometry(h,node_name='holder')
 if mode=='loaded':
  t=tool.copy();t.visual.vertex_colors=[193,198,204,255];s.add_geometry(t,node_name='reference_tools')
 blob=s.export(file_type='glb');(dest/(mode+'.glb.gz')).write_bytes(gzip.compress(blob,compresslevel=9,mtime=0))
 print(mode,len(blob),len(gzip.compress(blob,mtime=0)),flush=True)
