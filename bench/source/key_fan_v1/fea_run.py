"""HX04 stiffness screen (gmsh + CalculiX from FreeCAD 1.1, peg's fea.py): loads at the mouths that hang
furthest from the board. Solid ASA E = 1800 MPa; infill, layer bonds and board compliance not modelled.
    python fea_run.py <build dir>          (env as for the build: SHORT_*, HX4S_LAYOUT)
"""
import json, os, shutil, sys, tempfile
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]/'source/gallery_new_designs_v1/snapshot/bench/source/solder_v12'))
sys.path.insert(0, str(HERE/'study'))
import fea, short as S
FCB = Path(os.environ['FREECAD_BIN'])                  # FreeCAD 1.1 bin folder (gmsh.exe, ccx.exe)
fea.GMSH, fea.CCX = FCB/'gmsh.exe', FCB/'ccx.exe'
if os.environ.get('FEA_THREADS'):                     # several racks at once: cap CalculiX's threads
    os.cpu_count = lambda: int(os.environ['FEA_THREADS'])
d = Path(sys.argv[1]).resolve()
Lo = S.Layout(json.loads((HERE/'study'/os.environ['HX4S_LAYOUT']).read_text())['x'])
CASES = [(('tee', '10'), [0, 0, -50], 'T-handle 10 down 50 N', 'someone leans on the biggest handle'),
         (('tee', '10'), [30, 0, 0], 'T-handle 10 sideways 30 N', 'prying the biggest handle sideways'),
         (('hex', '10'), [0, 0, -50], 'hex 10 down 50 N', 'leaning on the biggest L-key'),
         (('torx', 'T50'), [0, 30, 0], 'Torx T50 out 30 N', 'yanking a stuck key straight off the board'),
         (('tee', '2'), [0, 0, -50], 'T-handle 2 down 50 N', 'the furthest-out corner of the T rail')]
if S.TONLY:                                            # HX05: one T rail, biggest and smallest handles
    big, small = S.TEE_NAMES[-1], S.TEE_NAMES[0]
    CASES = [(('tee', big), [0, 0, -50], 'T-handle %s down 50 N' % big, 'someone leans on the biggest handle'),
             (('tee', big), [30, 0, 0], 'T-handle %s sideways 30 N' % big, 'prying the biggest handle sideways'),
             (('tee', big), [0, 30, 0], 'T-handle %s out 30 N' % big, 'yanking the biggest handle off the board'),
             (('tee', small), [0, 0, -50], 'T-handle %s down 50 N' % small, 'the smallest handle')]
loads = []
for key, f, name, what in CASES:
    t = next(t for t in Lo.tools if (t['set'], t['name']) == key)
    loads.append(dict(id=name, point=[round(float(c), 3) for c in t['mouth']], force=f, radius=float(t['bore'])+2.5, what=what))
spec = dict(step='installed.step', h=float(os.environ.get('FEA_H', 7.)), supports=os.environ.get('FEA_SUPPORTS', 'pegs').split(','), loads=loads)
with tempfile.TemporaryDirectory(prefix='hx04-fea-', dir=os.environ.get('TEMP')) as sc:
    sc = Path(sc); shutil.copyfile(d/'installed.step', sc/'installed.step')
    (sc/'hx04__fea-spec.json').write_text(json.dumps(spec, indent=1))
    fea.main(sc, 'hx04')
    res = json.loads((sc/'hx04__fea.json').read_text())
(d/'fea.json').write_text(json.dumps(res, indent=1), encoding='utf-8', newline='\n')
for case in res['cases']:
    print('support', case['support'], 'nodes', case['nodes'])
    for lc in case['loads']:
        print('  %-28s %7.3f mm  (%s N/mm)' % (lc['id'], lc['deflection_at_load_mm'], lc['stiffness_N_per_mm']))
