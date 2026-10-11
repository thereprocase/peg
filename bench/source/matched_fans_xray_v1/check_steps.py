from pathlib import Path
import sys,json,hashlib
import FreeCAD as A,Part
folder=Path(sys.argv[1]);rows=[]
for p in sorted(folder.glob('*.step')):
 s=Part.Shape();s.read(str(p));b=s.optimalBoundingBox()
 assert s.isValid() and len(s.Solids)==1,p.name
 assert abs(b.ZMin)<1e-5 and min(b.XMin,b.YMin)>0 and max(b.XMax,b.YMax,b.ZMax)<256
 rows.append(dict(filename=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size,valid_single_solid=True,volume_mm3=s.Volume,print_dimensions_mm=[b.XLength,b.YLength,b.ZLength],bed_clearance_mm=min(b.XMin,b.YMin,256-b.XMax,256-b.YMax),bottom_z_mm=b.ZMin))
assert len(rows)==3
result=dict(passed=True,models=rows,scope='Reloaded print-oriented STEP solids, nominal unscaled 256 mm bed coordinates. No slice, brim, compensation, support or physical qualification.',freecad='.'.join(A.Version()[:3]))
(folder.parent/'step-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
