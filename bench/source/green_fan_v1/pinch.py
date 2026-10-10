"""Continuous two-fingertip pinch sweeps for the selected green fan.
Two ellipsoidal pads: 24 mm along the bar, 18 mm front/back, 10 mm thick.
Their centres are 14 mm either side of an 18 mm grip: 38 mm total span.
These are assumed fingertips, not a measured hand or full removal proof.
"""
from pathlib import Path
import sys,json,importlib.util
import numpy as np
import trimesh
from scipy.spatial import ConvexHull
source=Path(__file__).resolve().parent.parent/'stacked_fans_v1'/'build.py'
sys.path.insert(0,str(source.parent))
spec=importlib.util.spec_from_file_location('hx05_native_helpers',source)
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
B=Path(sys.argv[1]);data=json.loads((B.parent/'layout.json').read_text())
sphere=trimesh.creation.icosphere(subdivisions=1,radius=1).vertices
sphere/=min(-ConvexHull(sphere).equations[:,3])
bodies=[];tools=[]
for rack in data['racks']:
 body=h.Part.Shape();body.read(str(B/rack['id']/'body.brep'));body.translate(h.v([0,0,rack['z']]));bodies.append(body)
 for t in rack['tools']:
  shape=h.Part.makeCompound(h.tool_shapes(t));shape.translate(h.v([0,0,rack['z']]))
  tools.append((rack['id'],t['name'],shape))
def overlap(a,b):
 return float(a.common(b).Volume) if a.BoundBox.intersect(b.BoundBox) else 0.
rows=[]
for rack in data['racks']:
 if rack['id']!='HX05C':continue
 for t in rack['tools']:
  b,u,c=map(np.array,(t['bar_axis'],t['axis'],t['top']));c=c+np.array([0,0,rack['z']])
  # Pinch the end nearer the user, including the smallest key.
  if b[1]<0:b=-b
  n=np.cross(b,[0,1,0]);n/=np.linalg.norm(n);front=np.cross(n,b)
  mid=c+b*(t['bar']/2-10.5)
  ellipsoid=sphere@np.array([12*b,5*n,9*front])
  body_max=other_max=0.;containment_max=0.
  for sign in (-1,1):
   vertices=mid+sign*14*n+ellipsoid
   # Report the pad extent about this chosen grasp segment.
   a=c+b*(t['bar']/2-18);z=c+b*(t['bar']/2-3)
   f=np.clip(((vertices-a)@(z-a))/np.dot(z-a,z-a),0,1)
   containment_max=max(containment_max,float(np.linalg.norm(vertices-(a+f[:,None]*(z-a)),axis=1).max()))
   for d in (np.array([0.,180.,0.]),u*(t['burial']+5)):
    sweep=h.H.hull_solid(np.vstack([vertices,vertices+d]))
    body_max=max(body_max,max(overlap(sweep,body) for body in bodies))
    other_max=max(other_max,max(overlap(sweep,q) for ident,name,q in tools if (ident,name)!=(rack['id'],t['name'])))
  row=dict(tool=t['name'],grasp_end='frontmost',body_overlap_mm3=body_max,other_tool_overlap_mm3=other_max,maximum_distance_from_grasp_segment_mm=containment_max)
  rows.append(row);print(row,flush=True)
result=dict(passed=all(max(r['body_overlap_mm3'],r['other_tool_overlap_mm3'])<1e-5 and r['maximum_distance_from_grasp_segment_mm']<=25 for r in rows),scope='Two assumed fingertips during front approach and axial socket release; not a fist, full hand or subsequent free-hand removal.',pad_full_axes_mm=[24,10,18],pad_centre_offsets_mm=[-14,14],grip_diameter_mm=18,total_pinch_span_mm=38,rows=rows)
(B/'pinch-check.json').write_text(json.dumps(result,indent=2)+'\n');assert result['passed']
