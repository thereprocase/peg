"""Read-only checks on the exact released fan CAD and its published print STL."""
import FreeCAD as A
import Part,Mesh,hashlib,json,sys,math
from pathlib import Path
R=Path(__file__).resolve().parents[3];B=R/'bench/reviews/key-fan-audit-v1';B.mkdir(exist_ok=True)
step=R/'.local-runtime/hx04-audit/installed.step';shape=Part.read(str(step));report=json.loads((R/'bench/reviews/key-fan-v2/HX04/report.json').read_text());assert hashlib.sha256(step.read_bytes()).hexdigest()=='62a8acee8145f11967618944d6b4e0e2a54f3d96c428f3a197c91fc82f86798a'
stl=R/'docs/gallery/key-fan'/report['assets']['print.stl'];mesh=Mesh.Mesh(str(stl));assert hashlib.sha256(stl.read_bytes()).hexdigest()=='eef57613d3cc8b469d66e27c4934bcd748bda2c292b9426f16abf52a39661eef'
pegs=shape.common(Part.makeBox(600,20,800,A.Vector(-300,-19.85,-600)));solids=[s for s in pegs.Solids if s.Volume>1]
zs=sorted([s.BoundBox.Center.z for s in solids],reverse=True);groups=[]
for z in zs:
 if not groups or groups[-1][0]-z>12:groups.append([z,1])
 else:groups[-1][1]+=1
r=dict(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),step_sha256=hashlib.sha256(step.read_bytes()).hexdigest(),stl_sha256=hashlib.sha256(stl.read_bytes()).hexdigest(),native_valid=shape.isValid(),native_solids=len(shape.Solids),native_shells=len(shape.Shells),native_faces=len(shape.Faces),native_volume_mm3=shape.Volume,native_area_mm2=shape.Area,native_bbox_mm=[[shape.BoundBox.XMin,shape.BoundBox.YMin,shape.BoundBox.ZMin],[shape.BoundBox.XMax,shape.BoundBox.YMax,shape.BoundBox.ZMax]],mesh_closed=mesh.isSolid(),mesh_components=mesh.countComponents(),mesh_invalid_points=mesh.hasInvalidPoints(),mesh_invalid_neighbourhood=mesh.hasInvalidNeighbourhood(),mesh_volume_mm3=mesh.Volume,mesh_step_volume_error=abs(mesh.Volume-shape.Volume)/shape.Volume,peg_solids_behind_front_face=len(solids),peg_rows=[dict(approximate_centre_z_mm=z,count=count) for z,count in groups],freecad=A.Version(),occ=Part.OCC_VERSION)
assert r['native_valid'] and r['native_solids']==1 and r['mesh_closed'] and r['mesh_components']==1
assert len(solids)==90 and len(groups)==10 and all(count==9 for z,count in groups)
(B/'native-audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
