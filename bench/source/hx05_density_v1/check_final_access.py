"""Recheck represented stored tools and continuous axial release on new bodies."""
from pathlib import Path
import importlib.util,json,sys
import numpy as np,trimesh
from scipy.spatial import ConvexHull
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'.local-runtime/hx05-density-v1';B=WORK/'final-access'
source=ROOT/'bench/source/stacked_fans_v1/build.py'
sys.path.insert(0,str(source.parent));sys.argv=[sys.argv[0],str(B)]
spec=importlib.util.spec_from_file_location('hx05_native_helpers',source);h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
layout=json.loads((WORK/'layout.json').read_text());bodies=[]
for rack in layout['racks']:
 shape=h.Part.Shape();shape.read(str(WORK/rack['id']/'drafted-body.brep'));shape.translate(h.v([0,0,rack['z']]));bodies.append(shape)
sphere=trimesh.creation.icosphere(subdivisions=1,radius=1).vertices;sphere/=min(-ConvexHull(sphere).equations[:,3])
def overlap(a,b):return float(a.common(b).Volume) if a.BoundBox.intersect(b.BoundBox) else 0.
rows=[]
for rack in layout['racks']:
 for tool in rack['tools']:
  shaft,grip=h.tool_shapes(tool);shift=np.array([0,0,rack['z']]);shaft.translate(h.v(shift));grip.translate(h.v(shift))
  stored=max(overlap(shape,body) for shape in [shaft,grip] for body in bodies)
  p,u,bar,top=map(np.array,[tool['tip'],tool['axis'],tool['bar_axis'],tool['top']]);p=p+shift;top=top+shift
  length=tool['overall']-9+tool['burial']+5
  swept_shaft=h.Part.makeCylinder(tool['p2p']/2,length,h.v(p),h.v(u)) if 'p2p' in tool else h.Part.Face(h.hexwire(p,u,bar,tool['af'])).extrude(h.v(u*length))
  a=top-bar*(tool['bar']/2-9);b=top+bar*(tool['bar']/2-9);d=u*(tool['burial']+5)
  swept_grip=h.H.hull_solid((np.array([a,b,a+d,b+d])[:,None,:]+sphere[None,:,:]*9).reshape(-1,3))
  release=max(overlap(shape,body) for shape in [swept_shaft,swept_grip] for body in bodies)
  rows.append(dict(rack=rack['id'],tool=tool['name'],stored_overlap_mm3=stored,axial_release_overlap_mm3=release));print(rows[-1],flush=True)
result=dict(passed=all(max(r['stored_overlap_mm3'],r['axial_release_overlap_mm3'])<1e-5 for r in rows),rows=rows,scope='Represented catalogue tools and continuous axial release, with circumscribed grip sweep. Pinch approach checked separately. No physical fit or subsequent free-hand removal certificate.')
(B/'tool-access-check.json').write_text(json.dumps(result,indent=2)+'\n');assert result['passed']
