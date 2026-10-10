"""Complete the strong refined-mesh fixtures independently of the rejected weak run."""
import argparse,json,os,hashlib
from pathlib import Path
import numpy as np
import fea_campaign as F
p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--support',choices=['four-corners','face'],required=True);a=p.parse_args();root=a.root.resolve();out=root/'h5-remaining';out.mkdir(exist_ok=True);base=root/'h5'
for name in ['mesh.npz','volume.inp']:
 if not (out/name).exists():(out/name).symlink_to(base/name)
m=np.load(base/'mesh.npz');spec=json.loads((root/'loads.json').read_text());r=F.solve(out,m['ids'],m['X'],m['element_ids'],m['element_centres'],a.support,'grip-wrench',spec,8)
r.update(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),mesh_npz_sha256=hashlib.sha256((base/'mesh.npz').read_bytes()).hexdigest(),h_requested_mm=5,parent_step_sha256=spec['installed_step_sha256'],solver='CalculiX 2.21')
(out/f'{a.support}-grip-wrench/result.json').write_text(json.dumps(r,indent=2)+'\n')
