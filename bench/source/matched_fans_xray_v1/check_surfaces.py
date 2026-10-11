"""Sample native face-interior/vertex points against reimported spline STEP surfaces.
A numerical screen, not an exhaustive equivalence proof.
Run from the repository root after export_steps.py.
"""
import FreeCAD as A,Part,json,time
from pathlib import Path
rows=[]
for ident,root in [('HX05A','.local-runtime/matched-fans-v1'),('HX05C','.local-runtime/green-gravity-v3')]:
 b=Part.Shape();b.read(str(Path(root)/'tight-native'/ident/'left-tip-print.brep'));s=Part.Shape();s.read(str(next(Path('.local-runtime/matched-fans-xray-v1/release').glob(ident+'*.step'))))
 points=[]
 for f in b.Faces:
  u0,u1,v0,v1=f.ParameterRange
  p=f.valueAt((u0+u1)/2,(v0+v1)/2)
  if f.distToShape(Part.Vertex(p))[0]<1e-7:points.append(p)
 points.extend(v.Point for v in b.Vertexes[::10]);points=points[::max(1,len(points)//(64 if ident=='HX05A' else 16))];dist=[]
 for i,p in enumerate(points):
  dist.append(s.distToShape(Part.Vertex(p))[0])
  if i%500==0:print(ident,i,'max',max(dist),flush=True)
 assert max(dist)<1e-5
 row=dict(id=ident,points=len(points),maximum_distance_mm=max(dist));rows.append(row);print(row,flush=True)
 Path('.local-runtime/matched-fans-xray-v1/surface-check.json').write_text(json.dumps(rows,indent=2)+'\n')
