"""Export the exact reference pegboard used by the full-host install screen."""
import FreeCAD as A,Part,MeshPart,json,argparse,hashlib
from pathlib import Path
V=A.Vector
p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();root=a.root;d=json.loads((root/'install/install-audit.json').read_text());lo,hi=d['body_bbox_mm'];face=d['board_front_mm'];th=d['board_thickness_mm'];pitch=d['pitch_mm'];radius=d['hole_radius_mm'];top=d['hole_top_row_z_mm']
board=Part.makeBox(hi[0]-lo[0]+60,th,hi[2]-lo[2]+80,V(lo[0]-30,face-th,lo[2]-60));holes=[Part.makeCylinder(radius,th+2,V(i*pitch,face-th-1,top-k*pitch),V(0,1,0)) for i in range(-12,13) for k in range(-1,14)];board=board.cut(Part.makeCompound(holes));assert board.isValid()
mesh=MeshPart.meshFromShape(Shape=board,LinearDeflection=.1,AngularDeflection=.18,Relative=False);mesh.write(str(root/'install/nominal-board.stl'))
print('Exact reference board display mesh exported',mesh.CountFacets)
