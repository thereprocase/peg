"""Gallery assets for tweezers v9 (development): renders and GLBs with v8's own renderer.

Run with the v8 CadQuery env (cadpy) from the repo root:
  cadpy bench/source/tweezers_v9/gallery_assets.py <v9-build-dir> <out-dir>
"""
import sys, math
from pathlib import Path
import numpy as np, trimesh
ROOT = Path(__file__).resolve().parents[3]   # repo root; needs bench/source/tweezers_v8 from main
sys.path.insert(0, str(ROOT/'bench/source/tweezers_v8'))
import build_models as tool          # noqa: E402
from holder import HEELS, R          # noqa: E402
from review import render            # noqa: E402

build, out = Path(sys.argv[1]), Path(sys.argv[2])
NAME = 'part-solder-modules-tweezers__v9__cheek-cradle__fit-pf02c9-latch'
holder = trimesh.load(build/f'{NAME}__installed.stl')
printmesh = trimesh.load(build/f'{NAME}__print-right-cheek.stl')
tools = []
for heel in HEELS:
    m = tool.make_mesh('open_rest'); m.vertices = m.vertices@R.T+heel; tools.append(m)
teal, steel = '#4ca191', '#ccd2d5'
render([(holder, teal), *[(m, steel) for m in tools]], out/f'{NAME}__loaded.png',
       'v9 (development) · v8 cradles on a flat cheek',
       labels='Same throats, tilt and lift-then-left path as v8. The right side is now a solid print face.')
render([(holder, teal)], out/f'{NAME}__rear.png', 'Hooks on top, bearing pegs, latch at the bottom', view=(12, -65),
       labels='PF02 #9 hooks (row 0), loose bearing pegs (rows 2, 4), one spring latch per column (row 6).')
render([(printmesh, teal)], out/f'{NAME}__print.png', 'Right cheek on the bed', view=(30, -55),
       labels='Peg undersides need support; the cradles stand as walls.')
for name, parts in [('loaded', [holder, *tools]), ('empty', [holder]), ('print', [printmesh])]:
    scene = trimesh.Scene()
    for i, m in enumerate(parts):
        m = m.copy(); m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2, [1, 0, 0]))
        m.apply_scale(.001); m.visual.face_colors = [76, 161, 145, 255] if i == 0 else [188, 194, 200, 255]
        scene.add_geometry(m, node_name='holder' if i == 0 else f'tool-{i}')
    (out/f'{NAME}__{name}.glb').write_bytes(scene.export(file_type='glb'))
print('ok')
