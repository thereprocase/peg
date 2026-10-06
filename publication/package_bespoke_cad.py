"""Package reviewed native CAD and exact construction sources into a local release asset."""
from pathlib import Path
import argparse,hashlib,json,zipfile
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('output',type=Path);out=p.parse_args().output;out.mkdir(parents=True,exist_ok=True)
roots=[R/'bench/source/bespoke_tools_v1',R/'bench/source/gallery_current_mounts_v1/station_snapshot',R/'bench/reviews/bespoke-tools-v1']
paths=[]
for root in roots:
 paths.extend(p for p in root.rglob('*') if p.is_file() and p.suffix.lower() in {'.py','.md','.json','.step','.stl','.scad','.fcstd','.svg'})
for name in ['checks.py','fea.py']:paths.append(R/'bench/source/gallery_new_designs_v1/snapshot/bench/source/solder_v12'/name)
paths.append(R/'bench/source/gallery_current_mounts_v1/remount.py')
entries={p.relative_to(R).as_posix():p.read_bytes() for p in paths}
entries['README.txt']=b'Repro bespoke holders v1. Start with bench/source/bespoke_tools_v1/PRINT-DESIGN-RULES.md and each model NOTES.md. Native STEP, FreeCAD and print-oriented STL are in bench/reviews/bespoke-tools-v1/{HX01,TM01,CL01}. Physical fit and handling are pending. Rebuild from this directory using a FreeCAD 1.1 Python runtime: timeout 600 FREECAD_PYTHON bench/source/bespoke_tools_v1/build.py. Mesh review needs numpy, scipy, trimesh and rtree. FEA and slicing wrappers name the existing local Linux runtimes and owner profiles. External tool-reference CAD is linked in the audit and remains external. No machine-specific G-code is included.\n'
manifest={name:dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest()) for name,data in entries.items()};entries['MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
path=out/'repro-bespoke-tools__v1__cad-source-and-review.zip'
with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
 for name,data in sorted(entries.items()):z.writestr(name,data)
with zipfile.ZipFile(path) as z:
 assert z.testzip() is None
 for name,rec in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==rec['sha256']
print(json.dumps(dict(file=str(path),bytes=path.stat().st_size,files=len(entries),sha256=hashlib.sha256(path.read_bytes()).hexdigest()),indent=2))
