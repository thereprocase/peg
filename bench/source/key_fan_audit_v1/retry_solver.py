"""Independent newer-CalculiX cross-check of refined-mesh mount sensitivities.
Preserves the earlier failed solver output and uses the same mesh/load definitions.
"""
import argparse,json,hashlib,os
from pathlib import Path
import numpy as np
import fea_campaign as F
p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--support',choices=['hooks-only','four-corners','face'],required=True);a=p.parse_args();root=a.root.resolve();base=root/'h5';out=root/'h5-solver223';out.mkdir(exist_ok=True);gate=json.loads((base/'mesh-quality.json').read_text());assert gate['passed']
for name in ['volume.inp','mesh.npz']:
 target=out/name
 if not target.exists():target.symlink_to(base/name)
m=np.load(base/'mesh.npz');spec=json.loads((root/'loads.json').read_text());r=F.solve(out,m['ids'],m['X'],m['element_ids'],m['element_centres'],a.support,'grip-wrench',spec,6)
r.update(solver='CalculiX 2.23 from checksum-pinned FreeCAD 1.1.3 AppImage',h_requested_mm=5,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),mesh_npz_sha256=gate['mesh_npz_sha256'],parent_step_sha256=spec['installed_step_sha256'])
(out/f'{a.support}-grip-wrench/result.json').write_text(json.dumps(r,indent=2)+'\n')
