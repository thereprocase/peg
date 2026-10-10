"""Crop one actual bottom locking hoop and its surrounding plate from released CAD.
Analysis geometry only; this crop is not a standalone qualified print.
"""
import FreeCAD as A,Part,MeshPart,argparse,json,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();root=a.root;d=root/'hoop';d.mkdir(exist_ok=True);s=Part.read(str(root/'installed.step'));install=json.loads((root/'install/install-audit.json').read_text());z=install['hole_top_row_z_mm']-9*25.4
crop=s.common(Part.makeBox(12,28,20,A.Vector(-6,-20,z-10))).removeSplitter();assert crop.isValid() and len(crop.Solids)==1
crop.exportStep(str(d/'hoop-root.step'));m=MeshPart.meshFromShape(Shape=crop,LinearDeflection=.02,AngularDeflection=.1,Relative=False);m.write(str(d/'hoop-root.stl'));bb=crop.BoundBox
r=dict(parent_step_sha256=hashlib.sha256((root/'installed.step').read_bytes()).hexdigest(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),crop_step_sha256=hashlib.sha256((d/'hoop-root.step').read_bytes()).hexdigest(),hole_centre_z_mm=z,native_valid=True,native_solids=1,volume_mm3=crop.Volume,bbox_mm=[[bb.XMin,bb.YMin,bb.ZMin],[bb.XMax,bb.YMax,bb.ZMax]],scope='Exact crop of centre bottom-row hoop with plate/root; artificial fixed plate boundary in subsequent pinch study')
(d/'geometry.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
