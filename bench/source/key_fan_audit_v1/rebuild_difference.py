"""Native two-way Boolean comparison after the strict scalar rebuild check failed."""
from pathlib import Path
import FreeCAD as A,Part,json,hashlib,argparse,time
p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();root=a.root;out=root/'package-rebuild-diagnostic';start=time.monotonic();rebuilt=out/'rebuilt.brep';reference=out/'package/bench/reviews/key-fan-v2/HX04/part-hx04__v2__left-cheek__fit-pf02c9-hoop5__installed.step';x=Part.read(str(rebuilt));y=Part.read(str(reference));rows=[]
for label,left,right in [('rebuilt_minus_release',x,y),('release_minus_rebuilt',y,x)]:
 d=left.cut(right);v=0 if d.isNull() else d.Volume;rows.append(dict(operation=label,volume_mm3=v,solids=len(d.Solids),faces=len(d.Faces)));print(rows[-1],flush=True)
 if v>1e-5:d.exportBrep(str(out/(label+'.brep')))
r=dict(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),rebuilt_brep_sha256=hashlib.sha256(rebuilt.read_bytes()).hexdigest(),reference_step_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),differences=rows,seconds=time.monotonic()-start,scope='Default OpenCascade two-way solid subtraction; no added fuzzy tolerance and no relaxed strict scalar baseline gate. Native Boolean comparison has modelling tolerances and is not a bit-identical serialization proof.')
(out/'boolean-difference.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2),flush=True)
