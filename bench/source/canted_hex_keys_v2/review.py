"""HX02 v2 mesh print gates and GLB previews.

Same gates as v1 (watertight single body, face-angle overhang screen, starting islands, bed
contact, envelope) with one declared exception class: the engraved size numerals. They are cut
obliquely (rising toward the print top), so they add no flagged faces, but the counters of
0, 4, 6 and 8 still begin each as a sub-millimetre island in the layer where they start; the local
Orca review slice puts organic support there (recorded in toolpaths.json). Only starting points
inside a numeral's recorded box are accepted, and they are listed.
"""
from pathlib import Path
import argparse, hashlib, json, sys
import numpy as np
import trimesh
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'bench/source/gallery_new_designs_v1/snapshot/bench/source/solder_v12'))
import checks

LABEL_SPAN_MM = 2.0


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def inside(lo, hi, box):
    return bool((np.array(lo) >= np.array(box[0])).all() and (np.array(hi) <= np.array(box[1])).all())


def main():
    p = argparse.ArgumentParser(); p.add_argument('id'); a = p.parse_args()
    d = ROOT/'bench/reviews/canted-hex-keys-v2'/a.id; r = json.loads((d/'report.json').read_text()); assets = r['assets']
    boxes = r['finish']['labels']['installed_boxes']
    pr = trimesh.load(d/assets['print_stl'], force='mesh'); inv = np.linalg.inv(np.array(r['pose_matrix']).reshape(4, 4))
    oh = checks.overhangs(pr, inv, [])
    for f in oh['features']:
        lo, hi = f['installed_bbox']
        if not f['ok'] and f['short_span_mm'] < LABEL_SPAN_MM and any(inside(lo, hi, b) for b in boxes):
            f['declared'] = 'engraved size numeral: 1 mm recess stroke ceiling'; f['ok'] = True
    oh['passed'] = all(f['ok'] for f in oh['features'])
    oh['label_ceiling_area_mm2'] = round(sum(f['area_mm2'] for f in oh['features'] if f['declared']), 2)
    isl = checks.islands(pr, inv)
    for g in isl['points']:
        g['declared'] = any(inside(g['installed_xyz'], g['installed_xyz'], b) for b in boxes)
    isl['passed'] = all(g['declared'] for g in isl['points'])
    bed = (pr.triangles[:, :, 2].max(axis=1) < .01) & (pr.face_normals[:, 2] < -.9)
    components = len(trimesh.graph.connected_components(pr.face_adjacency, min_len=1, nodes=np.arange(len(pr.faces)), engine='scipy'))
    result = dict(watertight=bool(pr.is_watertight), components=components, positive_volume=bool(pr.volume > 0), overhangs=oh, islands=isl,
                  bed_face_mm2=float(pr.area_faces[bed].sum()), bounds_mm=pr.extents.tolist(),
                  declared_exceptions=f'Engraved numerals only: starting points (digit counters) inside a numeral box; flagged faces inside a numeral box with span < {LABEL_SPAN_MM} mm (none in v2). The review slice supports these counters; a support blocker over the numerals avoids that.',
                  inputs={k: sha(d/assets[k]) for k in ['installed_stl', 'print_stl']})
    result['passed'] = result['watertight'] and components == 1 and result['positive_volume'] and oh['passed'] and isl['passed'] and result['bed_face_mm2'] > 100 and bool(np.all(pr.extents[:2]+20 < 256))
    (d/'print-geometry.json').write_text(json.dumps(result, indent=2)+'\n', newline='\n')
    # Model-viewer uses metres, with Y up and the front of the pegboard toward +Z.
    transform = np.array([[-.001, 0, 0, 0], [0, 0, .001, 0], [0, .001, 0, 0], [0, 0, 0, 1]])
    for mode in ['installed', 'print', 'loaded']:
        scene = trimesh.Scene()
        m = trimesh.load(d/assets['print_stl' if mode == 'print' else 'installed_stl'], force='mesh'); m.apply_transform(transform); m.visual.vertex_colors = [68, 151, 143, 255]; scene.add_geometry(m, node_name='holder')
        if mode == 'loaded':
            t = trimesh.load(d/assets['tool-reference_stl'], force='mesh'); t.apply_transform(transform); t.visual.vertex_colors = [195, 201, 210, 255]; scene.add_geometry(t, node_name='reference_envelope')
        (d/(mode+'.glb')).write_bytes(scene.export(file_type='glb'))
    print(json.dumps({k: v for k, v in result.items() if k not in ['overhangs', 'islands']}, indent=2))
    print('overhangs passed', oh['passed'], 'features', len(oh['features']), 'label ceilings mm2', oh['label_ceiling_area_mm2'], 'islands passed', isl['passed'], len(isl['points']))
    assert result['passed']


if __name__ == '__main__':
    main()
