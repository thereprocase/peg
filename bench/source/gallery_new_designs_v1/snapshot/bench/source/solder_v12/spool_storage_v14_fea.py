"""Two fixed-cradle stiffness cases using the existing Linux solver; no spring model."""
from pathlib import Path
import argparse
import hashlib
import json

import fea

NAME='part-solder-spool-storage__v14__right-cheek__fit-pf02c9-hoop5'


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path)
    d=parser.parse_args().output.resolve()
    fea.GMSH=Path('/app/bin/gmsh');fea.CCX=Path('/app/bin/ccx');fea.os.cpu_count=lambda:4
    files=[d/f'{NAME}__installed.step',d/f'{NAME}__fea-spec.json',Path(__file__),
           Path(fea.__file__),fea.GMSH,fea.CCX]
    before={str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    fea.main(d,NAME)
    after={str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    assert before==after,'Inputs changed during solve; rerun against frozen CAD.'
    (d/'fea-provenance.json').write_text(json.dumps(dict(files=before,
        scope='Linear static fixed cradle stiffness only. No spring or release mechanism.',
        limits=['Solid isotropic ASA E1800 MPa nu.35','Peg nodes Y<.10 fixed',
                'No infill, layer, contact, strength, impact or convergence qualification']),indent=2)+'\n')


if __name__=='__main__':main()
