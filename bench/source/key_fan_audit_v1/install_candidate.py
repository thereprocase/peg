"""Screen translated swing candidates on the same released fan and nominal board.
A front-clear trajectory is not a qualified installation; hooks and hoops require compliance.
"""
import FreeCAD as A,Part,argparse,json,hashlib,time,math
from pathlib import Path
V=A.Vector
p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();root=a.root;out=root/'install';d=json.loads((out/'install-audit.json').read_text());s=Part.read(str(root/'installed.step'));lo,hi=d['body_bbox_mm'];face=d['board_front_mm'];th=d['board_thickness_mm'];pitch=d['pitch_mm'];radius=d['hole_radius_mm'];top=d['hole_top_row_z_mm'];pivot=V(*d['pivot_installed_mm']);start=time.monotonic()
b=Part.makeBox(hi[0]-lo[0]+60,th,hi[2]-lo[2]+80,V(lo[0]-30,face-th,lo[2]-60));holes=[Part.makeCylinder(radius,th+2,V(i*pitch,face-th-1,top-k*pitch),V(0,1,0)) for i in range(-12,13) for k in range(-1,14)];b=b.cut(Part.makeCompound(holes));front=s.common(Part.makeBox(600,400,800,V(-300,face,-600)));rear=s.common(Part.makeBox(600,20,800,V(-300,face-20,-600)));pegs=[q for q in rear.Solids if q.Volume>1];centres=sorted([q.BoundBox.Center.z for q in pegs],reverse=True);ztop=centres[0];zbottom=centres[-1];classes={'hooks':[q for q in pegs if q.BoundBox.Center.z>ztop-12],'locking':[q for q in pegs if q.BoundBox.Center.z<zbottom+12],'bearing':[q for q in pegs if zbottom+12<=q.BoundBox.Center.z<=ztop-12]};assert len(classes['hooks'])==len(classes['locking'])==9 and len(classes['bearing'])==72
rows=[]
for clearance in [1.,1.5,2.]:
 steps=[]
 for ang in [25-i*.5 for i in range(51)]:
  shift=clearance*math.sin(math.radians(ang))/math.sin(math.radians(25));m=front.copy();m.rotate(pivot,V(1,0,0),ang);m.translate(V(0,shift,0));volume=m.common(b).Volume if m.BoundBox.intersect(b.BoundBox) else 0.;q=dict(angle_deg=ang,outward_translation_mm=shift,front_host_intersection_mm3=volume)
  if ang in [25,10,5,3,2.5,2,1,.5,0]:
   for kind,objects in classes.items():
    values=[]
    for obj in objects:
     moved=obj.copy();moved.rotate(pivot,V(1,0,0),ang);moved.translate(V(0,shift,0));values.append(moved.common(b).Volume if moved.BoundBox.intersect(b.BoundBox) else 0.)
    q[kind+'_total_intersection_mm3']=sum(values);q[kind+'_max_per_peg_intersection_mm3']=max(values)
  steps.append(q)
 row=dict(outward_clearance_at_25deg_mm=clearance,formula='dy = clearance * sin(angle) / sin(25deg)',steps=steps,max_front_host_intersection_mm3=max(q['front_host_intersection_mm3'] for q in steps),front_host_clear_at_sampled_angles=all(q['front_host_intersection_mm3']<1e-5 for q in steps));rows.append(row);print('CANDIDATE',clearance,'host max',row['max_front_host_intersection_mm3'],flush=True)
r=dict(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),parent_step_sha256=hashlib.sha256((root/'installed.step').read_bytes()).hexdigest(),candidates=rows,seconds=time.monotonic()-start,scope='Prescribed rigid rotation plus outward translation, 0.5 degree samples. Tests front-host clearance and selected rear-peg intersections on nominal board. Does not establish hook engagement, contact force, snap recovery, hand motion or a continuous collision certificate.')
(out/'install-candidates.json').write_text(json.dumps(r,indent=2)+'\n')
