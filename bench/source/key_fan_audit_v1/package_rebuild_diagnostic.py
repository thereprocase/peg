"""Exercise the actual flattened public ZIP's frozen native build dependencies."""
import argparse,zipfile,json,hashlib,os,sys,time
from pathlib import Path
import FreeCAD as A,Part
p=argparse.ArgumentParser();p.add_argument('archive',type=Path);p.add_argument('out',type=Path);a=p.parse_args();start=time.monotonic();a.out.mkdir(parents=True,exist_ok=True);tree=a.out/'package';tree.mkdir(exist_ok=True)
with zipfile.ZipFile(a.archive) as z:
 manifest=json.loads(z.read('MANIFEST.json'))
 for n,q in manifest.items():
  assert not Path(n).is_absolute() and '..' not in Path(n).parts
  blob=z.read(n);assert hashlib.sha256(blob).hexdigest()==q['sha256']
 z.extractall(tree)
report=json.loads((tree/'bench/reviews/key-fan-v2/HX04/report.json').read_text())
for n,expected in report['source_dependencies'].items():assert hashlib.sha256((tree/n).read_bytes()).hexdigest()==expected,n
os.environ.update(report['build_env']);sys.path.insert(0,str(tree/'bench/source/key_fan_v1'));import build_short as B
s=B.build(True)['shape'];original=Part.read(str(tree/'bench/reviews/key-fan-v2/HX04'/report['assets']['installed.step']));assert s.isValid() and len(s.Solids)==1
volume_error=abs(s.Volume-original.Volume)/original.Volume
bbox=lambda b:[b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax]
bbox_error=max(abs(x-y) for x,y in zip(bbox(s.BoundBox),bbox(original.BoundBox)))
s.exportBrep(str(a.out/'rebuilt.brep'));strict_scalar_match=volume_error<1e-7 and bbox_error<1e-5 and len(s.Faces)==len(original.Faces)
vertices=lambda shape:sorted(tuple(round(v,5) for v in [q.Point.x,q.Point.y,q.Point.z]) for q in shape.Vertexes)
vertex_match=vertices(s)==vertices(original)
r=dict(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),tested_archive_sha256=hashlib.sha256(a.archive.read_bytes()).hexdigest(),source_dependencies=report['source_dependencies'],native_valid=True,native_solids=1,native_faces=len(s.Faces),volume_mm3=s.Volume,reference_volume_mm3=original.Volume,reference_native_faces=len(original.Faces),relative_volume_difference=volume_error,max_bbox_coordinate_difference_mm=bbox_error,rounded_vertex_multiset_match=vertex_match,exact_baseline_comparison_passed=bool(strict_scalar_match and vertex_match),seconds=time.monotonic()-start,dependency_hashes_passed=True,freecad=A.Version(),occ=Part.OCC_VERSION,scope='Rebuild from flattened public package and original recorded environment; compare native validity/topology count, volume, bounds and vertex multiset to exact released STEP. An exact baseline-comparison failure is retained rather than relaxed; analyses use the included exact released STEP, not this rebuild. Not a continuous motion, physical fit or load proof.')
(a.out/'result.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2),flush=True)
