"""Left/tip-face bed pose and native contact/vent checks; no slicing claim."""
from pathlib import Path
import sys,json,math,importlib.util
import numpy as np
source=Path(__file__).resolve().parent.parent/'stacked_fans_v1'/'build.py'
sys.path.insert(0,str(source.parent))
spec=importlib.util.spec_from_file_location('hx05_native_helpers',source);h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
B=Path(sys.argv[1]);r=json.loads((B.parent/'layout.json').read_text())['racks'][0]
body=h.Part.Shape();body.read(str(B/'HX05C/body.brep'))
body_bounds=body.optimalBoundingBox()
contact=sum(f.Area for f in body.Faces if f.BoundBox.XLength<1e-6 and abs(f.BoundBox.XMin-body_bounds.XMin)<1e-5)
assert contact>5000.,('Insufficient flat bed contact',contact)
reference=h.Part.Shape();reference.read(sys.argv[2])
back=h.Part.makeBox(2000,1000.15,2000,h.V(-1000,-1000,-1000))
new_back=body.common(back);old_back=reference.common(back)
back_difference=new_back.cut(old_back).Volume+old_back.cut(new_back).Volume
assert back_difference<1e-6,('Board-side geometry changed',back_difference)
checks=[]
for t in r['tools']:
 p,u,b,m=map(np.array,(t['tip'],t['axis'],t['bar_axis'],t['mouth']));elbow=p-u*1.5
 direction=np.array([0.,1.,0.])-u*u[1];direction/=np.linalg.norm(direction)
 axial=h.Part.makeCylinder(.45,1.56,h.v(p+u*.03),h.v(-u));exit=h.Part.makeCylinder(.45,500.,h.v(elbow),h.v(direction))
 vent=max(body.common(axial).Volume,body.common(exit).Volume)
 entry=h.Part.Face(h.hexwire(m,u,b,t['af']+3.36)).extrude(h.v(u*10.))
 entry_overlap=body.common(entry).Volume
 checks.append(dict(tool=t['name'],vent_probe_overlap_mm3=vent,entrance_clearance_probe_overlap_mm3=entry_overlap))
 assert max(vent,entry_overlap)<1e-5,checks[-1]
# Installed X increases upward during printing. Installed Y/Z form the bed.
base=np.array([[0.,1.,0.],[0.,0.,1.],[1.,0.,0.]])
a=math.radians(45);yaw=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1.]])
rot=yaw@base;matrix=h.A.Matrix()
for i in range(3):
 for j in range(3):setattr(matrix,f'A{i+1}{j+1}',float(rot[i,j]))
posed=body.copy();posed.transformShape(matrix);bb=posed.optimalBoundingBox()
translation=h.V(128-(bb.XMin+bb.XMax)/2,128-(bb.YMin+bb.YMax)/2,-bb.ZMin)
posed.translate(translation);bb=posed.optimalBoundingBox()
assert posed.isValid() and abs(posed.Volume-body.Volume)<1e-4
assert min(bb.XMin,bb.YMin)>=3 and max(bb.XMax,bb.YMax)<=253 and abs(bb.ZMin)<1e-5 and bb.ZMax<256
posed.exportStep(str(B/'HX05C/left-tip-print.step'))
posed.exportBrep(str(B/'HX05C/left-tip-print.brep'))
h.MeshPart.meshFromShape(Shape=posed,LinearDeflection=.1,AngularDeflection=.25,Relative=False).write(str(B/'HX05C/left-tip-print.stl'))
scene=h.trimesh.Scene();h.add(scene,posed,[50,146,133,255],'holder');h.add(scene,h.Part.makeBox(256,256,1,h.V(0,0,-1)),[203,207,203,255],'256 mm bed');h.write(scene,'HX05C-print')
result=dict(passed=True,board_side_symmetric_difference_mm3=back_difference,reference_body_sha256=__import__('hashlib').sha256(Path(sys.argv[2]).read_bytes()).hexdigest(),bed_plane_design_x_mm=body_bounds.XMin,bed_contact_area_mm2=contact,bed_contact_area_cm2=contact/100,bed_yaw_degrees=45,bed_size_mm=[256,256],print_bounds_mm=[bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax],print_dimensions_mm=[bb.XLength,bb.YLength,bb.ZLength],available_edge_margin_mm=min(bb.XMin,bb.YMin,256-bb.XMax,256-bb.YMax),rotation=rot.tolist(),translation=list(translation),cavity_checks=checks,scope='Native bed contact, pose, envelope, open entry and vent probes. Not a sliced or physically qualified print; peg undersides and bore bridges need toolpath review.')
(B/'print-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
