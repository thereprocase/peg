"""Fixed-peg linear static prototype stiffness; no strength/printed-infill claim."""
import argparse,json,hashlib,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'solder_v12'))
import fea

def main():
 p=argparse.ArgumentParser();p.add_argument('directory',type=Path);d=p.parse_args().directory.resolve();c=json.loads((d/'candidate.json').read_text());name=c['name']
 fea.GMSH=Path('/app/bin/gmsh');fea.CCX=Path('/app/bin/ccx');fea.os.cpu_count=lambda:4
 inputs=[d/(name+'__installed.step'),d/(name+'__fea-spec.json'),Path(__file__),Path(fea.__file__),fea.GMSH,fea.CCX]
 before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs};fea.main(d,name)
 result=json.loads((d/(name+'__fea.json')).read_text());limits=[1,.5]
 passed=all(r['deflection_at_load_mm']<=limit for case in result['cases'] for r,limit in zip(case['loads'],limits))
 out=dict(inputs=before,passed=passed,scope='5N lateral and down at front taper wall; fixed peg nodes, solid isotropic ASA E1800MPa nu.35. No infill/layer/board/contact/strength/fatigue qualification.')
 (d/'fea-provenance.json').write_text(json.dumps(out,indent=2)+'\n');print('FEA targets',passed)
 if not passed:raise SystemExit(1)
if __name__=='__main__':main()
