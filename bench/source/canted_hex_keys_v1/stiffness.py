"""Bounded HX02 solid-ASA stiffness screen using a 5 mm nominal tetrahedral mesh.

Run in an isolated scratch directory so interrupted solvers cannot mix evidence.
"""
from pathlib import Path
import sys,json,shutil,tempfile,hashlib
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'bench/source/gallery_new_designs_v1/snapshot/bench/source/solder_v12'))
import fea
D=ROOT/'bench/reviews/canted-hex-keys-v1/HX02'
r=json.loads((D/'report.json').read_text());name=r['prefix'];spec=json.loads((D/(name+'__fea-spec.json')).read_text());spec['h']=5.0
runtime=Path('/home/repro/cache-downloads/peg-cad/squashfs-root/usr/bin');fea.GMSH=runtime/'gmsh';fea.CCX=runtime/'ccx';fea.os.cpu_count=lambda:4
with tempfile.TemporaryDirectory(prefix='peg-hex-fea-') as scratch:
 out=Path(scratch);shutil.copyfile(D/r['assets']['installed_step'],out/r['assets']['installed_step']);(out/(name+'__fea-spec.json')).write_text(json.dumps(spec,indent=2)+'\n')
 fea.main(out,name)
 result=json.loads((out/(name+'__fea.json')).read_text())
 result['passed']=all(lc['deflection_at_load_mm']<=limit for case in result['cases'] for lc,limit in zip(case['loads'],[1,.5]))
 result['limits']='Screen with 5 mm nominal second-order tetrahedra and solid isotropic ASA E=1800 MPa. Mesh convergence, infill, layer bonds, board compliance and physical loads remain unqualified.'
 (D/(name+'__fea-spec.json')).write_text(json.dumps(spec,indent=2)+'\n')
 def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
 result['inputs']={k:sha(p) for k,p in {'step':D/r['assets']['installed_step'],'spec':D/(name+'__fea-spec.json'),'solver_script':Path(fea.__file__),'review_script':Path(__file__)}.items()}
 (D/(name+'__fea.json')).write_text(json.dumps(result,indent=2)+'\n');(D/'stiffness.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2));assert result['passed']
