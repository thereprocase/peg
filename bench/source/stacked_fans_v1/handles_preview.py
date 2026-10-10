"""Exact layout envelope mesh, before growing plastic. Not a print mesh."""
from pathlib import Path
import json,gzip,sys
import numpy as np,trimesh
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
rs=json.loads((out.parent/'layout.json').read_text())['racks']
M=np.array([[.001,0,0,0],[0,0,.001,0],[0,.001,0,0],[0,0,0,1]])
def rod(a,b,r,n=24):
    return trimesh.creation.cylinder(radius=r,segment=np.array([a,b]),sections=n)
def sphere(p,r):
    m=trimesh.creation.icosphere(subdivisions=2,radius=r);m.apply_translation(p);return m
stack=trimesh.Scene()
for rack in rs:
    scene=trimesh.Scene()
    for t in rack['tools']:
        p,c,b=map(np.array,(t['tip'],t['top'],t['bar_axis']));r=t.get('p2p',t['af']*2/np.sqrt(3))/2
        shafts=rod(p,c,r)
        a=c-b*(t['bar']/2-9);z=c+b*(t['bar']/2-9)
        handles=trimesh.util.concatenate([rod(a,z,9),sphere(a,9),sphere(z,9)])
        for name,mesh,color in [('shaft',shafts,[133,147,160,255]),('handle',handles,[49,74,82,255])]:
            mesh.apply_transform(M);mesh.visual.vertex_colors=color
            scene.add_geometry(mesh,node_name=t['name']+'_'+name)
            moved=mesh.copy();moved.apply_translation([0,rack['z']*.001,0]);stack.add_geometry(moved,node_name=rack['id']+t['name']+name)
    (out/(rack['id']+'.glb.gz')).write_bytes(gzip.compress(scene.export(file_type='glb'),9,mtime=0))
(out/'stack.glb.gz').write_bytes(gzip.compress(stack.export(file_type='glb'),9,mtime=0))
