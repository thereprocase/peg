"""Package the HX02 v2 native model with exact sources and review evidence."""
from pathlib import Path
import argparse,hashlib,json,zipfile
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('output',type=Path);out=p.parse_args().output;out.mkdir(parents=True,exist_ok=True)
roots=[R/'bench/source/canted_hex_keys_v2',R/'bench/source/bespoke_tools_v1',R/'bench/source/gallery_current_mounts_v1/station_snapshot',R/'bench/reviews/canted-hex-keys-v2/HX02']
paths=[p for root in roots for p in root.rglob('*') if p.is_file() and p.suffix.lower() in {'.py','.md','.json','.step','.stl','.scad','.fcstd','.svg'}]
paths += [R/'bench/source/gallery_current_mounts_v1/remount.py']
paths += [R/'bench/source/gallery_new_designs_v1/snapshot/bench/source/solder_v12'/name for name in ['checks.py','fea.py']]
entries={p.relative_to(R).as_posix():p.read_bytes() for p in paths}
entries['README.txt']=b'HX02 v2: graduated organ-pipe metric hex-key rack; full-depth sockets 30 degrees outward from vertical. Read bench/reviews/canted-hex-keys-v2/HX02/NOTES.md. Rebuild with a FreeCAD 1.1 Python runtime (numpy + scipy): FREECAD_PYTHON bench/source/canted_hex_keys_v2/build.py. Print, hand access and tool fit need physical checks. The STL is in right-cheek print orientation. No machine G-code is included.\n'
manifest={name:dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest()) for name,data in entries.items()}
entries['MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
path=out/'canted-hex-keys__v2__cad-source-and-review.zip'
with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
 for name,data in sorted(entries.items()):z.writestr(name,data)
with zipfile.ZipFile(path) as z:
 assert z.testzip() is None
 for name,r in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==r['sha256']
print(json.dumps(dict(path=str(path),files=len(entries),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()),indent=2))
