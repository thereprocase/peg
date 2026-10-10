"""Audit full host material as well as rear pegs along the published assumed install pivot.
Intersections are geometric volumes, not penetration distances or installation forces.
"""
import argparse,json,hashlib,time,math
from pathlib import Path
import FreeCAD as A,Part,MeshPart
V=A.Vector;PITCH=25.4;FACE=.15;BOARD=3.94;HOLE_R=3.175
p=argparse.ArgumentParser();p.add_argument('--step',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);start=time.monotonic();shape=Part.read(str(a.step));assert shape.isValid() and len(shape.Solids)==1
pegs=shape.common(Part.makeBox(600,20,800,V(-300,FACE-20,-600)));sol=[q for q in pegs.Solids if q.Volume>1];zc=sorted({round(q.BoundBox.Center.z/5)*5 for q in sol},reverse=True);clusters=[]
for z in zc:
 if not clusters or clusters[-1]-z>12:clusters.append(z)
groups={}
for q in sol:
 k=min(range(len(clusters)),key=lambda i:abs(clusters[i]-q.BoundBox.Center.z));groups.setdefault(k,[]).append(q)
assert len(groups)==10 and all(len(q)==9 for q in groups.values());zs=min(q.BoundBox.ZMin for q in groups[1])+HOLE_R-(.12-PITCH)
bb=shape.BoundBox
front=shape.common(Part.makeBox(600,400,800,V(-300,FACE,-600)));pivot=V(0,FACE-BOARD/2,.12+zs+HOLE_R)
def board(thickness=BOARD,hole_radius=HOLE_R,pitch=PITCH):
 s=Part.makeBox(bb.XLength+60,thickness,bb.ZLength+80,V(bb.XMin-30,FACE-thickness,bb.ZMin-60));holes=[]
 for i in range(-12,13):
  for k in range(-1,14):holes.append(Part.makeCylinder(hole_radius,thickness+2,V(i*pitch,FACE-thickness-1,.12-k*pitch+zs),V(0,1,0)))
 return s.cut(Part.makeCompound(holes))
b=board();steps=[];worst=None
for angle in [25-i*.5 for i in range(51)]:
 m=front.copy();m.rotate(pivot,V(1,0,0),angle);contact=m.common(b) if m.BoundBox.intersect(b.BoundBox) else Part.Shape();volume=contact.Volume if not contact.isNull() else 0.;step=dict(angle_deg=angle,front_host_intersection_mm3=volume)
 if worst is None or volume>worst[0]:worst=(volume,angle,contact)
 steps.append(step);print('host',angle,volume,flush=True)
if worst[0]>1e-7:
 mesh=MeshPart.meshFromShape(Shape=worst[2],LinearDeflection=.06,AngularDeflection=.16,Relative=False);mesh.write(str(a.out/'worst-front-host-contact.stl'))
variations=[]
centre=V(0,FACE,.12+zs-9*PITCH/2)
for thickness,radius,pitch,residual in [(3.8,HOLE_R,PITCH,1.),(3.94,HOLE_R,PITCH,1.),(4.1,HOLE_R,PITCH,1.),(BOARD,3.125,PITCH,1.),(BOARD,3.225,PITCH,1.),(BOARD,HOLE_R,25.375,1.),(BOARD,HOLE_R,25.425,1.),(BOARD,HOLE_R,PITCH,.999),(BOARD,HOLE_R,PITCH,1.001),(BOARD,HOLE_R,PITCH,1.0054293183189222)]:
 target=board(thickness,radius,pitch);volumes=[]
 for k in range(1,9):
  for peg in groups[k]:
   q=peg.copy()
   if residual!=1:q.translate(-centre);q.scale(residual);q.translate(centre)
   volume=q.common(target).Volume if q.BoundBox.intersect(target.BoundBox) else 0.;volumes.append(volume)
 variations.append(dict(board_thickness_mm=thickness,hole_diameter_mm=2*radius,pitch_mm=pitch,residual_part_scale=residual,max_seated_bearing_intersection_mm3=max(volumes),total_seated_bearing_intersection_mm3=sum(volumes),bearing_pegs_with_intersection_gt_1e_4=sum(x>1e-4 for x in volumes)))
 print('variation',variations[-1],flush=True)
r=dict(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),step_sha256=hashlib.sha256(a.step.read_bytes()).hexdigest(),pivot_installed_mm=[pivot.x,pivot.y,pivot.z],board_front_mm=FACE,board_thickness_mm=BOARD,hole_radius_mm=HOLE_R,pitch_mm=PITCH,hole_top_row_z_mm=.12+zs,body_bbox_mm=[[bb.XMin,bb.YMin,bb.ZMin],[bb.XMax,bb.YMax,bb.ZMax]],steps=steps,worst_front_host_intersection_mm3=worst[0],worst_front_host_angle_deg=worst[1],front_host_seated_intersection_mm3=steps[-1]['front_host_intersection_mm3'],seated_bearing_sensitivities=variations,seconds=time.monotonic()-start,scope='Same assumed fixed pivot as published swing screen; checks front host omitted from the rear-peg screen. Sensitivity ranges are illustrative, not measured board tolerances. Positive volume is neither force nor maximum penetration; compliant hooks/hoops and alternative install trajectories are not simulated.')
(a.out/'install-audit.json').write_text(json.dumps(r,indent=2)+'\n');print('COMPLETE',r['seconds'],flush=True)
