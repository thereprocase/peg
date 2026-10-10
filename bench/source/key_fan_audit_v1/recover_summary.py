"""Recover completed FEA results after ccx -v's documented 201 exit code.
Does not execute the solver or alter numerical results/decks.
"""
import argparse,json,hashlib,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('run',type=Path);p.add_argument('--h',type=float,required=True);p.add_argument('--suite',default='baseline');a=p.parse_args();run=a.run.resolve();root=run.parent
results=[]
for support,mode in [('all-pegs','mouth')]+([('all-pegs','grip-wrench'),('hooks-only','grip-wrench'),('four-corners','grip-wrench'),('face','grip-wrench')] if a.suite=='deep' else []):
 path=run/f'{support}-{mode}'/'result.json';r=json.loads(path.read_text());assert len(r['loads'])==5 and all(q['force_balance_relative_error']<.001 for q in r['loads']);results.append(r)
import numpy as np
mesh=np.load(run/'mesh.npz');version=subprocess.run(['ccx','-v'],capture_output=True,text=True,check=False,timeout=30)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=dict(step_sha256=sha(root/'installed.step'),source_sha256=sha(root/'fea_audit.py'),loads_sha256=sha(root/'loads.json'),h_requested_mm=a.h,nodes=len(mesh['ids']),elements=len(mesh['element_ids']),linear_tetra_mesh_volume_mm3=float(mesh['volumes'].sum()),minimum_element_volume_mm3=float(mesh['volumes'].min()),gmsh_version=subprocess.run(['gmsh','-version'],capture_output=True,text=True,check=False,timeout=30).stderr.strip(),ccx_version=version.stdout.strip(),ccx_version_exit_code=version.returncode,suite=a.suite,results=results,receipt_recovery=dict(reason='All solves and numerical parsing completed; ccx -v returns 201 on this build and original check_output treated version query as failure',recovery_source_sha256=sha(__file__)),limitations=['Solid isotropic ASA, not actual infill','Ideal clamps, no elastic pegboard/contact','Equivalent grip resultants on mouth patch, not verified tool/socket contact','Sharp-edge/clamp stress maxima may be singular','Stress percentiles unweighted by volume'])
(run/'summary.json').write_text(json.dumps(r,indent=2)+'\n');print('Recovered',run,'without rerunning solver')
