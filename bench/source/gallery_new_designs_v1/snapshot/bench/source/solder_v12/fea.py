"""Linear-static stiffness check: gmsh tetra mesh + CalculiX (both ship with FreeCAD 1.1).

    cadpy fea.py BUILD_DIR NAME          (reads NAME__fea-spec.json, writes NAME__fea.json)

The spec names the installed STEP and a list of load cases, each a force (N) spread over
the mesh nodes within `radius` of `point` (installed holder coordinates, mm). Two support
cases bracket the real mount:
- 'face': every node on or behind the rear contact face (Y <= 0.16) fixed, i.e. the plate
  pressed flat on the board; isolates cheek, arm and shelf flex.
- 'pegs': only the peg material behind the face (Y < 0.10) fixed, so the plate itself
  can bend and twist; closer to a part hanging on its pegs (no board contact assumed, so
  it overstates sway).
Material: printed ASA, E = 1800 MPa, nu = 0.35 (solid walls; infill regions are softer, so
treat results as a lower bound on deflection for thick sections).
"""
from pathlib import Path
import json
import os
import re
import subprocess
import sys

import numpy as np

FC_BIN = Path(r'C:\Program Files\FreeCAD 1.1\bin')
GMSH, CCX = FC_BIN/'gmsh.exe', FC_BIN/'ccx.exe'
E_MPA, NU = 1800.0, 0.35


def mesh(step, out, h):
    inp = out.with_suffix('.mesh.inp')
    cmd = [str(GMSH), str(step), '-3', '-order', '2', '-clmax', str(h), '-clmin', str(h/4),
           '-setnumber', 'Mesh.SecondOrderLinear', '1', '-format', 'inp', '-o', str(inp)]
    subprocess.run(cmd, check=True, capture_output=True, timeout=1800)
    text = inp.read_text()
    # Keep nodes and the C3D10 volume elements only.
    blocks = re.split(r'(?m)^(?=\*)', text)
    nodes, elems = [], []
    for b in blocks:
        head = b.split('\n', 1)[0].strip().upper()
        if head.startswith('*NODE'):
            nodes.append(b)
        elif head.startswith('*ELEMENT') and 'C3D10' in head:
            elems.append(re.sub(r'(?i)ELSET=[^,\n]*', 'ELSET=EALL', b))
    assert nodes and elems, 'gmsh produced no C3D10 elements'
    clean = out.with_suffix('.vol.inp')
    clean.write_text(''.join(nodes+elems))
    xyz = {}
    for b in nodes:
        for line in b.split('\n')[1:]:
            parts = [p for p in line.split(',') if p.strip()]
            if len(parts) == 4:
                xyz[int(parts[0])] = [float(p) for p in parts[1:]]
    ids = np.array(sorted(xyz)); X = np.array([xyz[i] for i in ids])
    ne = sum(len(re.findall(r'(?m)^\s*\d+,', b)) for b in elems)
    return clean, ids, X, ne


def nset(name, ids):
    lines = [f'*NSET,NSET={name}']
    for i in range(0, len(ids), 12):
        lines.append(', '.join(str(int(v)) for v in ids[i:i+12]))
    return '\n'.join(lines)+'\n'


def solve(spec, d, name, support):
    step = d/spec['step']
    base = d/f'{name}__fea-{support}'
    vol, ids, X, ne = mesh(step, base, spec.get('h', 2.0))
    fix = ids[X[:, 1] <= 0.16] if support == 'face' else ids[X[:, 1] < 0.10]
    assert len(fix) > 20, ('too few fixed nodes', support, len(fix))
    deck = [f'*INCLUDE,INPUT={vol.name}', nset('FIX', fix), '*MATERIAL,NAME=ASA', '*ELASTIC',
            f'{E_MPA},{NU}', '*SOLID SECTION,ELSET=EALL,MATERIAL=ASA', '*BOUNDARY', 'FIX,1,3']
    sets = {}
    for lc in spec['loads']:
        p = np.array(lc['point']); r = lc.get('radius', 3.0)
        sel = ids[np.linalg.norm(X-p, axis=1) <= r]
        assert len(sel) >= 3, ('load point not on the part', lc['id'], len(sel))
        sets[lc['id']] = sel
    for lc in spec['loads']:
        sel = sets[lc['id']]; f = np.array(lc['force'], dtype=float)/len(sel)
        deck += ['*STEP', '*STATIC', '*CLOAD,OP=NEW']
        for n in sel:
            for k in range(3):
                if f[k]:
                    deck.append(f'{int(n)},{k+1},{f[k]:.6g}')
        deck += ['*NODE PRINT,NSET=NALL', 'U', '*END STEP']
    deck_path = base.with_suffix('.inp')
    deck.insert(1, nset('NALL', ids))
    deck_path.write_text('\n'.join(deck)+'\n')
    env = dict(os.environ, OMP_NUM_THREADS=str(os.cpu_count() or 4))
    subprocess.run([str(CCX), deck_path.stem], cwd=str(d), check=True, capture_output=True, timeout=3600, env=env)
    dat = (d/(deck_path.stem+'.dat')).read_text()
    steps = re.split(r'displacements \(vx,vy,vz\) for set NALL and time', dat)[1:]
    pos = {int(i): k for k, i in enumerate(ids)}
    res = []
    for lc, blk in zip(spec['loads'], steps):
        U = np.zeros_like(X)
        for line in blk.split('\n')[1:]:
            parts = line.split()
            if len(parts) == 4 and parts[0].isdigit():
                k = pos.get(int(parts[0]))
                if k is not None:
                    U[k] = [float(v) for v in parts[1:]]
        sel = np.array([pos[int(n)] for n in sets[lc['id']]])
        fdir = np.array(lc['force'], dtype=float); F = np.linalg.norm(fdir); fdir = fdir/F
        along = float((U[sel] @ fdir).mean())
        mag = np.linalg.norm(U, axis=1); worst = int(np.argmax(mag))
        res.append(dict(id=lc['id'], force_N=lc['force'], point=lc['point'], what=lc.get('what', ''),
                        deflection_at_load_mm=round(along, 4), stiffness_N_per_mm=round(F/along, 1) if along > 0 else None,
                        max_deflection_mm=round(float(mag[worst]), 4), max_at=X[worst].round(1).tolist()))
    for p in d.glob(f'{name}__fea-{support}*'):     # mesh, deck and results run to 60+ MB; keep only the JSON
        p.unlink()
    for p in d.glob('spooles.out'):
        p.unlink()
    return dict(support=support, nodes=int(len(ids)), elements=int(ne), fixed_nodes=int(len(fix)), loads=res)


def main(d, name):
    spec = json.loads((d/f'{name}__fea-spec.json').read_text())
    out = dict(name=name, material=dict(E_MPa=E_MPA, nu=NU), h_mm=spec.get('h', 2.0), cases=[])
    for support in spec.get('supports', ['face', 'pegs']):
        out['cases'].append(solve(spec, d, name, support))
    (d/f'{name}__fea.json').write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main(Path(sys.argv[1]), sys.argv[2])
