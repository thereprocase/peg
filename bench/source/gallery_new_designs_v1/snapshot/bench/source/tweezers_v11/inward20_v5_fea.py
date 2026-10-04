"""Eight fixed-holder stiffness cases using the existing Linux solver; no spring model."""
from pathlib import Path
import argparse
import hashlib
import json

import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"solder_v12"))
import fea




def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path)
    d=parser.parse_args().output.resolve();NAME=json.loads((d/'candidate.json').read_text())['cases'][0]['name']
    fea.GMSH=Path('/app/bin/gmsh');fea.CCX=Path('/app/bin/ccx');fea.os.cpu_count=lambda:4
    files=[d/f'{NAME}__installed.step',d/f'{NAME}__fea-spec.json',Path(__file__),
           Path(fea.__file__),fea.GMSH,fea.CCX]
    before={str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    fea.main(d,NAME)
    result=json.loads((d/f'{NAME}__fea.json').read_text())
    spec=json.loads((d/f'{NAME}__fea-spec.json').read_text())
    assert len(result['cases'])==1 and len(result['cases'][0]['loads'])==len(spec['loads'])==8
    result['load_point_targets_passed']=all(r['deflection_at_load_mm']<=s['target_load_point_mm'] for r,s in zip(result['cases'][0]['loads'],spec['loads']))
    (d/f'{NAME}__fea.json').write_text(json.dumps(result,indent=2)+'\n')
    after={str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    assert before==after,'Inputs changed during solve; rerun against frozen CAD.'
    (d/'fea-provenance.json').write_text(json.dumps(dict(files=before,
        scope='Fresh v5 whole-body solve: eight 5 N tray cases. Guide contact loading and capture are not simulated.',
        limits=['Solid isotropic ASA E1800 MPa nu.35','Peg nodes Y<.10 fixed',
                'No infill, layer, contact, strength, impact or convergence qualification']),indent=2)+'\n')


if __name__=='__main__':main()
