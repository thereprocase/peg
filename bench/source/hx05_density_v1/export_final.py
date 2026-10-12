"""Final print-pose STEP round trips with the recorded rational export workaround."""
from pathlib import Path
import json, sys, hashlib
import FreeCAD as A, Part, MeshPart
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'.local-runtime/hx05-density-v1'
ident=sys.argv[1];out=WORK/ident;native=Part.Shape()
native.read(str(out/'print-drafted-body.brep'))
assert native.isValid() and len(native.Solids)==1
converted=native.toNurbs() if ident!='HX05B' else native
name=f'{ident}_{dict(HX05C="13190",HX05B="13189",HX05A="33034")[ident]}_finished_v1_tip_down.step'
converted.exportStep(str(out/name))
restored=Part.Shape();restored.read(str(out/name));assert restored.isValid() and len(restored.Solids)==1
a=native.optimalBoundingBox();b=restored.optimalBoundingBox()
delta=max(abs(getattr(a,k)-getattr(b,k)) for k in ['XMin','XMax','YMin','YMax','ZMin','ZMax'])
print(ident,'STEP deltas',delta,'native/converted/STEP volumes',native.Volume,converted.Volume,restored.Volume,flush=True)
volume_delta=abs(restored.Volume/native.Volume-1)
# Rational surfaces change OCC's numerical volume integration slightly. Keep
# a bounded volume gate and additionally check native surface samples against
# the reloaded STEP; do not accept the volume comparison on its own.
assert delta<.01 and volume_delta<.0005
points=[]
for face in native.Faces:
 u0,u1,v0,v1=face.ParameterRange
 p=face.valueAt((u0+u1)/2,(v0+v1)/2)
 if face.distToShape(Part.Vertex(p))[0]<1e-7:points.append(p)
points.extend(v.Point for v in native.Vertexes[::10])
points=points[::max(1,len(points)//32)]
distances=[restored.distToShape(Part.Vertex(p))[0] for p in points]
assert max(distances)<1e-5
# Tessellate the rational conversion of the native solid, not a repaired mesh.
mesh=MeshPart.meshFromShape(Shape=converted,LinearDeflection=.025,AngularDeflection=.1,Relative=False)
mesh.write(str(out/'print-finished-body.stl'))
result=dict(id=ident,passed=True,valid_single_solid=True,filename=name,sha256=hashlib.sha256((out/name).read_bytes()).hexdigest(),native_volume_mm3=native.Volume,step_volume_mm3=restored.Volume,relative_volume_integration_delta=volume_delta,maximum_bound_delta_mm=delta,surface_samples=len(points),maximum_sample_surface_distance_mm=max(distances),rational_surface_conversion=ident!='HX05B',print_rotation_unchanged=True,scope='STEP reload validity, bounded numerical volume-integration difference, bounds and native surface samples. Fresh native rational-surface tessellation; mesh topology and intersection checks separate.')
(out/'finished-step-check.json').write_text(json.dumps(result,indent=2)+'\n');print(ident,'STEP and fresh mesh exported',flush=True)
