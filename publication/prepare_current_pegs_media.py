"""Convert checked STL exports to display GLB without changing modeled geometry."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import trimesh


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(build, selection=None):
    count = 0
    # CAD uses millimeters and Z up. GLTF uses meters and Y up.
    transform = np.array([[.001, 0, 0, 0], [0, 0, .001, 0],
                          [0, -.001, 0, 0], [0, 0, 0, 1]])
    reports = [Path(__file__).resolve().parents[1] / item['report'] for item in json.loads(selection.read_text())['products']] if selection else sorted(build.glob('*/report.json'))
    for report_file in reports:
        report = json.loads(report_file.read_text())
        if not report['checks']['pass']:
            continue
        folder = report_file.parent
        receipt_path = folder / 'presentation.json'
        old = json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
        hashes = {role: digest(folder / report['assets'][role + '_stl'])
                  for role in ['installed', 'print']}
        if old.get('input_stl_sha256') == hashes and all((folder / (r + '.glb')).is_file() for r in hashes):
            continue
        for role in ['installed', 'print']:
            input_file = folder / report['assets'][role + '_stl']
            assert hashes[role] == report['checks']['mesh'][role]['sha256']
            mesh = trimesh.load_mesh(input_file, process=False)
            mesh.apply_transform(transform)
            mesh.visual.face_colors = [72, 182, 222, 255]
            scene = trimesh.Scene(mesh)
            scene.metadata = {'part': report['id'], 'role': role,
                              'CAD_units': 'mm', 'display_units': 'm',
                              'source_STL_sha256': hashes[role]}
            target = folder / (role + '.glb')
            target.write_bytes(scene.export(file_type='glb'))
            assert digest(input_file) == hashes[role]
        receipt = {'id': report['id'], 'input_stl_sha256': hashes,
                   'display_transform': transform.tolist(),
                   'assets': {'installed_glb': 'installed.glb', 'print_glb': 'print.glb'}}
        receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
        count += 1
        print(report['id'], 'display GLBs ready', flush=True)
    print('new/rebuilt', count, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('build', type=Path)
    parser.add_argument('--selection', type=Path)
    args = parser.parse_args()
    main(args.build, args.selection)
