"""STL -> GLB like peg's review.py (metres, Y up, board front toward +Z).

Owner, 2026-10-08: renders carry black ink on edges, its weight proportional to the angle between the two
faces that meet there. Each feature edge becomes a thin black triangular prism of radius
INK_R0 + INK_K * angle (mm, angle in degrees); edges under INK_MIN degrees (tessellation of curved
surfaces) are left bare. INK=0 turns it off.
"""
import os, sys
from pathlib import Path
import numpy as np
import trimesh

d = Path(sys.argv[1])
X = np.array([[-.001, 0, 0, 0], [0, 0, .001, 0], [0, .001, 0, 0], [0, 0, 0, 1]])
INK = os.environ.get('INK', '1') == '1'
INK_MIN, INK_R0, INK_K = float(os.environ.get('INK_MIN', 20)), .08, .55/90


def ink(m):
    ang = np.degrees(m.face_adjacency_angles)
    sel = ang > INK_MIN
    if not sel.any():
        return None
    e = m.vertices[m.face_adjacency_edges[sel]]                 # (n, 2, 3)
    r = INK_R0+INK_K*np.minimum(ang[sel], 135.)
    a, b = e[:, 0], e[:, 1]; t = b-a; L = np.linalg.norm(t, axis=1); keep = L > 1e-6
    a, b, t, r, L = a[keep], b[keep], t[keep], r[keep], L[keep]; t /= L[:, None]
    ref = np.where(np.abs(t[:, :1]) < .9, [[1., 0, 0]], [[0, 1., 0]])
    u = np.cross(t, ref); u /= np.linalg.norm(u, axis=1)[:, None]; w = np.cross(t, u)
    ring = [u, -.5*u+.866*w, -.5*u-.866*w]
    # slightly longer than the edge so neighbouring prisms overlap at corners
    a2, b2 = a-t*r[:, None]*.5, b+t*r[:, None]*.5
    V = np.stack([a2+q*r[:, None] for q in ring]+[b2+q*r[:, None] for q in ring], axis=1)   # (n, 6, 3)
    n = len(V); base = (np.arange(n)*6)[:, None]
    F = np.array([[0, 1, 4], [0, 4, 3], [1, 2, 5], [1, 5, 4], [2, 0, 3], [2, 3, 5], [0, 2, 1], [3, 4, 5]])
    return trimesh.Trimesh(V.reshape(-1, 3), (F[None]+base[:, :, None]).reshape(-1, 3), process=False)


def load(name, colour, scene, node):
    m = trimesh.load(d/name, force='mesh'); m.merge_vertices()
    k = ink(m) if INK else None
    m.apply_transform(X); m.visual.vertex_colors = colour
    scene.add_geometry(m, node_name=node)
    if k is not None:
        k.apply_transform(X); k.visual.vertex_colors = [12, 12, 12, 255]
        scene.add_geometry(k, node_name=node+'_ink')


for mode in ['installed', 'print', 'loaded']:
    s = trimesh.Scene()
    load('print.stl' if mode == 'print' else 'installed.stl', [68, 151, 143, 255], s, 'holder')
    if mode == 'loaded':
        load(os.environ.get('KEYS', 'keys.stl'), [195, 201, 210, 255], s, 'reference_envelope')
    (d/(mode+'.glb')).write_bytes(s.export(file_type='glb'))
print('glb ok', d)
