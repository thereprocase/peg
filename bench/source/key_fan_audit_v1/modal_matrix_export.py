"""Export the same modal pencil for an independent SciPy eigenvalue check."""
from pathlib import Path
import argparse,subprocess,os,json,hashlib,time
p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();root=a.root;out=root/'modal/matrix-face';out.mkdir(exist_ok=True);base=root/'modal/face';text=(base/'modes.inp').read_text().replace('*FREQUENCY\n','*FREQUENCY,SOLVER=MATRIXSTORAGE\n');(out/'matrix.inp').write_text(text)
if not (out/'volume.inp').exists():(out/'volume.inp').symlink_to(root/'h7/volume.inp')
start=time.monotonic()
with (out/'solver.log').open('w') as f:subprocess.run(['ccx','matrix'],cwd=out,env=dict(os.environ,OMP_NUM_THREADS='4'),stdout=f,stderr=subprocess.STDOUT,timeout=1000,check=True)
r=dict(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),deck_sha256=hashlib.sha256(text.encode()).hexdigest(),seconds=time.monotonic()-start,files={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in out.iterdir() if p.is_file() and p.name not in ['volume.inp','export.json']})
(out/'export.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2),flush=True)
