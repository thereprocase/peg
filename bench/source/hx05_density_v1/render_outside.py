"""Convert the selected exact native-export meshes for private workbench renders."""
from pathlib import Path
import json,gzip,sys,numpy as np,trimesh
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'.local-runtime/hx05-density-v1';out=WORK/'view';out.mkdir(exist_ok=True)
for ident,color in [('HX05C',[50,146,133,255]),('HX05B',[67,111,175,255]),('HX05A',[170,103,61,255])]:
 if len(sys.argv)>1 and ident!=sys.argv[1]:continue
 draft=(WORK/ident/'print-drafted-body-fine.stl').exists()
 mesh=trimesh.load(WORK/ident/('print-drafted-body-fine.stl' if draft else 'print-structural-body-fine.stl'),force='mesh',process=True)
 pc=json.loads((WORK/ident/('draft-check.json' if draft else 'check.json')).read_text());pc=pc if draft else pc['print_pose'];world=(mesh.vertices-np.array(pc['translation']))@np.array(pc['rotation'])
 mesh.vertices=world
 transform=np.array([[.001,0,0,0],[0,0,.001,0],[0,.001,0,0],[0,0,0,1]])
 mesh.apply_transform(transform)
 mesh.unmerge_vertices()
 mesh.visual.vertex_colors=color;scene=trimesh.Scene(mesh)
 (out/(ident+'.glb.gz')).write_bytes(gzip.compress(scene.export(file_type='glb')))
 if draft:
  pose=trimesh.load(WORK/ident/'print-drafted-body-fine.stl',force='mesh',process=True)
  pose.apply_translation([-128,-128,0]);pose.apply_transform(transform);pose.unmerge_vertices();pose.visual.vertex_colors=color
  (out/(ident+'-print.glb.gz')).write_bytes(gzip.compress(trimesh.Scene(pose).export(file_type='glb')))
 print(ident,'current outside + print GLB',flush=True)
