"""Re-export the unchanged print BREP bodies; rational STEP surfaces avoid vent seam defects."""
from pathlib import Path
import sys,json,hashlib
import FreeCAD as A,Part
ROOT=Path(__file__).resolve().parents[3]
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True);rows=[]
for ident,root,name in [('HX05C','green-gravity-v3','HX05C_13190_green_v3_left_tip_print.step'),('HX05B','matched-fans-v1','HX05B_13189_matched_v1_left_tip_print.step'),('HX05A','matched-fans-v1','HX05A_33034_matched_v1_left_tip_print.step')]:
 p=ROOT/'.local-runtime'/root/'tight-native'/ident/'left-tip-print.brep'
 native=Part.Shape();native.read(str(p));assert native.isValid() and len(native.Solids)==1
 converted=native.toNurbs() if ident!='HX05B' else native
 converted.exportStep(str(out/name))
 restored=Part.Shape();restored.read(str(out/name));assert restored.isValid() and len(restored.Solids)==1
 a=native.optimalBoundingBox();b=restored.optimalBoundingBox()
 bounds_error=max(abs(getattr(a,k)-getattr(b,k)) for k in ('XMin','XMax','YMin','YMax','ZMin','ZMax'))
 assert bounds_error<.01 and abs(restored.Volume/native.Volume-1)<.0001
 rows.append(dict(id=ident,native_brep_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),rational_surface_conversion=ident!='HX05B',maximum_bound_delta_mm=bounds_error,native_volume_mm3=native.Volume,step_volume_mm3=restored.Volume))
 print(ident,'valid STEP',flush=True)
(out.parent/'export-check.json').write_text(json.dumps(dict(models=rows,scope='Same native print bodies. Inch and Torx surfaces are converted to rational B-splines for STEP interoperability. Reported volume differences include surface-integration differences; STEP reload validity and bounds are checked.'),indent=2)+'\n')
