"""Fresh-process restore and representative two-sheet parameter edits."""
from pathlib import Path
import sys,json,math,types
import FreeCAD as A,Part
bundle=Path(sys.argv[1]);sys.path.insert(0,str(bundle))
import hx05_parametric as H
out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
doc=A.openDocument(str(bundle/'HX05C_13190_parametric_v1.FCStd'))
custom=[o for o in doc.Objects if hasattr(o,'Kind')]
assert len(custom)==61,len(custom)
assert all(isinstance(o.Proxy,H.Generator) for o in custom),'Missing restored feature proxies'
assert doc.FinalHolder.Shape.isValid() and len(doc.FinalHolder.Shape.Solids)==1
original=doc.FinalHolder.Shape.copy();volume=original.Volume;mouth=doc.Key_3_32.Mouth;bar=doc.Key_3_8.BarAxis
old_cavity=doc.Cavity_3_8.Shape.Volume
# Verify the gravity guard without invalidating the delivered document.
invalid=types.SimpleNamespace(Parameters=doc.Parameters,UpAngle=9.,OutOfPlane=doc.Key_3_8.OutOfPlane,Label='invalid test')
try:
 H.frame(invalid)
except ValueError:
 rejected=True
else:
 raise AssertionError('9-degree upward angle was accepted')
doc.GlobalParameters.set('B2','=0.48 mm')
doc.GlobalParameters.set('B8','=13 mm')
doc.GlobalParameters.set('B6','=1.2 mm')
doc.KeyLayout.set('B2','=65 mm')
doc.KeyLayout.set('C11','=11.5 deg')
doc.KeyLayout.set('E11','=%0.15g deg' % (doc.Key_3_8.HandleRoll.Value+5))
print('Recomputing edited portable copy',flush=True)
doc.recompute()
errors=[(o.Name,o.getStatusString(),getattr(o,'LastError','')) for o in doc.Objects if 'Invalid' in o.State or getattr(o,'LastError','')]
assert not errors,errors
shape=doc.FinalHolder.Shape
assert shape.isValid() and len(shape.Solids)==1
assert abs(shape.Volume-volume)>1
assert abs(doc.Parameters.AFClearance.Value-.48)<1e-9
assert abs(doc.Parameters.GussetSpread.Value-13)<1e-9
assert abs(doc.Parameters.VentDiameter.Value-1.2)<1e-9
assert abs(doc.Key_3_32.GuideLength.Value-65)<1e-9
assert abs((doc.Key_3_32.Mouth-mouth).Length-5)<1e-7
assert abs(math.degrees(math.asin(doc.Key_3_8.Axis.z))-11.5)<1e-9
assert (doc.Key_3_8.BarAxis-bar).Length>.01
assert doc.Cavity_3_8.Shape.Volume>old_cavity
back=Part.makeBox(2000,1000.15,2000,A.Vector(-1000,-1000,-1000))
a=original.common(back);b=shape.common(back);difference=a.cut(b).Volume+b.cut(a).Volume
assert difference<1e-6,difference
file=out/'EDIT_TEST.FCStd';doc.saveAs(str(file));A.closeDocument(doc.Name)
r=dict(restored_custom_features=len(custom),default_volume_mm3=volume,edited_volume_mm3=shape.Volume,edited_valid_single_solid=True,clearance_mm=.48,gusset_spread_mm=13,vent_diameter_mm=1.2,smallest_guide_mm=65,largest_up_degrees=11.5,handle_roll_increment_degrees=5,sub_ten_degree_angle_rejected=rejected,board_side_symmetric_difference_mm3=difference,freecad_version='.'.join(A.Version()[:3]),dependencies='FreeCAD + Python standard library only',edited_file=file.name)
(out/'edit-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2),flush=True)
