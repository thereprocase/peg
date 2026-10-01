"""Check the actual exported holder/tools and render the installed and bed poses."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

import numpy as np
import trimesh
from trimesh.collision import CollisionManager

from front import HEELS, TOOL_ROTATION, v8
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tweezers_v8'))
from review import render


def main(d):
    installed = next(d.glob('part-solder-modules-tweezers__v10*__installed.stl'))
    prefix = installed.name.removesuffix('__installed.stl')
    holder = trimesh.load(installed)
    assert holder.is_watertight and holder.is_winding_consistent and holder.is_volume
    assert holder.body_count == 1
    tools = [trimesh.load(d / f'reference-tool-{i + 1}.stl') for i in range(4)]
    all_holder = CollisionManager()
    all_holder.add_object('holder', holder)
    results = []
    for i, tool in enumerate(tools):
        other = CollisionManager()
        other.add_object('holder', holder)
        for j, neighbour in enumerate(tools):
            if i != j:
                other.add_object(f'neighbour-{j}', neighbour)
        cache = {}
        def distance(p):
            key = tuple(p)
            if key not in cache:
                q = np.eye(4)
                q[:3, 3] = p
                assert not other.in_collision_single(tool, transform=q), (i, key)
                cache[key] = float(other.min_distance_single(tool, transform=q))
            return cache[key]
        def continuous(a, b, depth=0):
            da, db = distance(a), distance(b)
            length = float(np.linalg.norm(b-a))
            assert min(da, db) > 1e-5, (i, a, b, da, db)
            if da + db > length + .08:
                return min(da, db, (da+db-length)/2)
            assert depth < 20
            mid = (a+b)/2
            return min(continuous(a, mid, depth+1), continuous(mid, b, depth+1))
        waypoints = [np.array(p, dtype=float) for p in [(0, 0, 0), (0, 0, 5), (30, 0, 5)]]
        bound = min(continuous(a, b) for a, b in zip(waypoints, waypoints[1:]))
        local = (tool.vertices - HEELS[i]) @ TOOL_ROTATION
        tip_faces = np.flatnonzero(np.all(local[tool.faces][:, :, 1] >= 108, axis=1))
        tips = tool.submesh([tip_faces], append=True)
        tip_distance = float(all_holder.min_distance_single(tips))
        assert tip_distance > 2.5, (i, tip_distance)
        body_stop = None
        for drop in np.arange(.25, 5.01, .25):
            q = np.eye(4)
            q[2, 3] = -drop
            if all_holder.in_collision_single(tool, transform=q):
                body_stop = float(drop)
                break
        assert body_stop is not None
        results.append(dict(slot=i+1, at_rest_clearance_mm=distance(np.zeros(3)),
                            tip_region_clearance_mm=tip_distance,
                            body_stop_detected_by_vertical_drop_mm=body_stop,
                            translation_waypoints_mm=[p.tolist() for p in waypoints],
                            continuous_translation_clearance_lower_bound_mm=bound,
                            distance_evaluations=len(cache), passed=True))
        print('tool', i+1, results[-1], flush=True)
    info_path = d / f'{prefix}__design-and-checks.json'
    info = json.loads(info_path.read_text())
    info['tool_checks'] = dict(
        slots=results,
        tip_direction_xyz=TOOL_ROTATION[:, 1].tolist(),
        method='Actual triangle meshes with neighbours present. Rigid translation Lipschitz distance bounds cover each entire segment; reverse path inserts. Nominal reconstructed tool only; excludes tolerance, compliance, hands and seating forces.',
    )
    info['input_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in [installed, d/'front.step', *sorted(d.glob('reference-tool-*.stl'))]}
    info_path.write_text(json.dumps(info, indent=2) + '\n')
    teal, steel = '#4ca191', '#ccd2d5'
    render([(holder, teal), *[(t, steel) for t in tools]], d/f'{prefix}__loaded.png',
           'v10 · tips down · compact right cheek', view=(18, 60),
           labels='Grasp the heel, lift 5 mm, then move left. Points remain down.')
    render([(holder, teal)], d/f'{prefix}__empty.png', 'v10 · solid right cheek · no wide support blocks', view=(23, 60))
    render([(holder, teal), *[(t, steel) for t in tools]], d/f'{prefix}__front.png',
           'Installed front view · viewer right is −X', view=(0, 90))
    render([(holder, teal)], d/f'{prefix}__rear.png', 'Unchanged v9 receiver, hooks, bearing pegs and latches', view=(15, -60))
    print_mesh = trimesh.load(d/f'{prefix}__print-right-cheek.stl')
    render([(print_mesh, teal)], d/f'{prefix}__print.png', 'Actual right cheek on the bed · −X down', view=(30, -55))
    guide = trimesh.load(d/'cradle-local.stl')
    guide.vertices = guide.vertices @ v8.R.T + HEELS[0]
    render([(guide, teal), (tools[0], steel)], d/f'{prefix}__detail.png',
           'Contoured body support · open arms · points free', view=(14, 64))
    coupon = trimesh.load(d/'single-throat-print-right-cheek.stl')
    render([(coupon, teal)], d/f'{prefix}__coupon.png', 'Single throat · right cheek on the bed', view=(30, -55))
    import math
    for name, parts in [('loaded', [holder, *tools]), ('empty', [holder]), ('print', [print_mesh])]:
        scene = trimesh.Scene()
        for i, m in enumerate(parts):
            m = m.copy()
            m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2, [1, 0, 0]))
            m.apply_scale(.001)
            m.visual.face_colors = [76, 161, 145, 255] if i == 0 else [188, 194, 200, 255]
            scene.add_geometry(m, node_name='holder' if i == 0 else f'tool-{i}')
        (d/f'{prefix}__{name}.glb').write_bytes(scene.export(file_type='glb'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=Path)
    main(parser.parse_args().directory)
