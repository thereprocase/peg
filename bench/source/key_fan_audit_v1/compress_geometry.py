"""Losslessly compress display geometry; preserve decoded hashes and captured scene."""
from pathlib import Path
import argparse,json,gzip,hashlib
p=argparse.ArgumentParser();p.add_argument('data',type=Path);a=p.parse_args();data=a.data;j=json.loads((data/'scene.json').read_text());raw=data.parent/'raw-display-geometry';raw.mkdir(exist_ok=True)
def pack(desc):
 path=data/desc['file']
 if path.suffix=='.gz':return
 blob=path.read_bytes();assert hashlib.sha256(blob).hexdigest()==desc['sha256'];(raw/path.name).write_bytes(blob);name=path.name+'.gz';(data/name).write_bytes(gzip.compress(blob,9,mtime=0));desc.update(file=name,decoded_sha256=desc['sha256'],sha256=hashlib.sha256((data/name).read_bytes()).hexdigest(),encoding='gzip, lossless float32/uint32 geometry');path.unlink()
for desc in [j['holder'],j['fem'],j['board']]+[q['display_mesh'] for q in j['tools']]+[q['display_mesh'] for q in j['fields'] if q.get('display_mesh')]:pack(desc)
(data/'scene.json').write_text(json.dumps(j,indent=2)+'\n');print('Compressed display bytes',sum(q.stat().st_size for q in data.iterdir() if q.is_file()))
