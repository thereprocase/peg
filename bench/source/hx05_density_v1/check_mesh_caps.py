"""Validate tiny planar seam caps within the mesh's 0.025 mm deflection.

Curved trim boundaries are polygonal in the mesh. Cap probes therefore need
not lie exactly on the trimmed planar face, but must stay within the declared
tessellation deflection. The underlying native solid is never edited.
"""
from pathlib import Path
import json,math
import FreeCAD as A,Part
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'.local-runtime/hx05-density-v1';rows=json.loads((WORK/'mesh-cap-candidates.json').read_text())
for row in rows:
 shape=Part.Shape();shape.read(str(WORK/row['id']/(row['name']+'.brep')))
 planes=[f for f in shape.Faces if isinstance(f.Surface,Part.Plane)]
 worst=0.;samples=0
 for loop in row['loops']:
  for tri in loop['triangles_xyz']:
   pts=[A.Vector(*q) for q in tri];centre=sum(pts,A.Vector())/3
   candidates=[f for f in planes if abs(f.Surface.Axis.dot(centre-f.Surface.Position))<3e-5 and all(getattr(f.BoundBox,k+'Min')-3e-5<=getattr(centre,k.lower())<=getattr(f.BoundBox,k+'Max')+3e-5 for k in ('X','Y','Z'))]
   if not candidates:raise ValueError((row['id'],row['name'],'Patch has no native plane'))
   probes=pts+[centre]+[(pts[i]+pts[(i+1)%3])/2 for i in range(3)]
   error=min(max(f.distToShape(Part.Vertex(q))[0] for q in probes) for f in candidates)
   if error>.025:raise ValueError((row['id'],row['name'],'Patch exceeds tessellation deflection',error))
   worst=max(worst,error);samples+=len(probes)
 row['native_plane_validation_passed']=True;row['maximum_native_surface_distance_mm']=worst;row['native_surface_tolerance_mm']=.025;row['native_surface_probe_count']=samples
 print(row['id'],row['name'],'native plane cap validation',worst,flush=True)
(WORK/'mesh-cap-check.json').write_text(json.dumps(dict(passed=True,rows=rows,scope='Only zero-area triangles removed and tiny planar native-face tessellation gaps capped; no existing mesh vertices moved. No bearing redesign or generic hole repair.'),indent=2)+'\n')
