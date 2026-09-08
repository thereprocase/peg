"""Sample the current conformal STEP against the actual cylindrical board.

Independent finite-pose solid intersections supplement the separate continuous
motion certificate, including the exact seated pose and final seating motion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time

import cadquery as cq

from round_verify_cad import sample_poses

ROOT = Path(__file__).resolve().parent
DEFAULT_OUT = ROOT / 'cad' / 'conformal'


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(step=None, geometry=None, output=None, max_seconds=600,
           candidate_motion=None, candidate_poses=400):
    step = Path(step or DEFAULT_OUT / 'conformal_120.step')
    geometry = Path(geometry or step.with_name(step.stem + '_geometry.json'))
    candidate_motion = Path(candidate_motion or DEFAULT_OUT / 'conformal_motion_results.json')
    output = Path(output or DEFAULT_OUT / 'conformal_motion_check.json')
    if candidate_poses < 2 or max_seconds <= 0:
        raise ValueError('Use at least two samples and a positive time budget')
    output.parent.mkdir(parents=True, exist_ok=True)
    g = json.loads(geometry.read_text(encoding='utf-8'))
    motion = json.loads(candidate_motion.read_text(encoding='utf-8'))
    p = g['parameters']
    if motion['parameters'] != p or motion['geometry_contract'] != g:
        raise ValueError('Motion evidence and current geometry contract differ')
    if not motion['verification']['passed'] or not motion['verification']['complete']:
        raise ValueError('Current motion must pass its continuous check first')
    for path in [step, geometry, ROOT/'conformal_anchor.py', ROOT/'conformal_motion.py']:
        if motion['source_sha256'].get(path.relative_to(ROOT).as_posix()) != _sha(path):
            raise ValueError(f'Stale continuous evidence for {path.name}')
    original = cq.importers.importStep(str(step)).val()
    if not original.isValid() or len(original.Solids()) != 1:
        raise ValueError('Candidate STEP must contain one valid solid')
    t, pitch, R = p['board_thickness'], p['pitch'], p['hole_diameter'] / 2
    board = cq.Workplane('XY').box(80, t, 120).translate((0, -t / 2, -pitch / 2))
    for z in [0, -pitch]:
        bore = cq.Solid.makeCylinder(R, t + 2, cq.Vector(0, -t - 1, z), cq.Vector(0, 1, 0))
        board = board.cut(cq.Workplane(obj=bore))
    board = board.val()
    plans = {'candidate_removal_path': sample_poses(motion['removal_poses'], candidate_poses)}
    source_paths = [step, geometry, candidate_motion, Path(__file__), ROOT / 'conformal_anchor.py',
                    ROOT / 'round_anchor.py', ROOT / 'round_verify_cad.py']
    threshold = 1e-6
    report = {
        'check': 'Sampled OpenCascade Boolean intersections of actual conformal STEP and cylindrical-hole board',
        'parameters': p,
        'source_sha256': {path.relative_to(ROOT).as_posix(): _sha(path)
                          for path in source_paths if path.is_relative_to(ROOT)},
        'intersection_volume_threshold_mm3': threshold,
        'continuous_source_certified': True,
        'complete': False, 'all_sampled_poses_clear': False, 'checks': {},
        'scope': [
            'Finite samples supplement the separate continuous certificate and do not prove clearance between samples.',
            'Upper/lower saddles, full-depth locator, normal nose chamfer and sharp spine are all included.',
            'Intended zero-volume contact is allowed. No force, friction, deformation, strength or printing test.',
        ],
    }
    started = time.monotonic()
    for label, poses in plans.items():
        check = {'planned_poses': len(poses), 'checked_poses': 0, 'complete': False,
                 'passed': False, 'maximum_intersection_volume_mm3': 0.0,
                 'colliding_poses': [], 'samples': []}
        report['checks'][label] = check
        for i, (y, z, angle) in enumerate(poses):
            if time.monotonic() - started > max_seconds:
                report['time_budget_exceeded'] = True
                output.write_text(json.dumps(report, indent=2) + '\n',encoding='utf-8',newline='\n')
                raise TimeoutError(f'Candidate CAD check exceeded {max_seconds}s; partial results saved')
            placed = original.rotate((0, 0, 0), (1, 0, 0), float(angle)).translate((0, float(y), float(z)))
            volume = float(placed.intersect(board).Volume())
            sample = {'index': i, 'y': float(y), 'z': float(z), 'theta_deg': float(angle),
                      'intersection_volume_mm3': volume}
            check['samples'].append(sample)
            check['checked_poses'] = i + 1
            check['maximum_intersection_volume_mm3'] = max(check['maximum_intersection_volume_mm3'], volume)
            if volume > threshold:
                check['colliding_poses'].append(sample)
            report['elapsed_seconds'] = round(time.monotonic() - started, 3)
            if i % 10 == 0:
                output.write_text(json.dumps(report, indent=2) + '\n',encoding='utf-8',newline='\n')
                print(f'{label}: {i + 1}/{len(poses)}; max overlap {check["maximum_intersection_volume_mm3"]:.9g} mm3', flush=True)
        check['complete'] = True
        check['passed'] = not check['colliding_poses']
    report['complete'] = True
    report['all_sampled_poses_clear'] = all(c['passed'] for c in report['checks'].values())
    report['candidate_sampled_path_passed'] = report['all_sampled_poses_clear']
    output.write_text(json.dumps(report, indent=2) + '\n',encoding='utf-8',newline='\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--step', type=Path)
    parser.add_argument('--geometry', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--max-seconds', type=float, default=600)
    parser.add_argument('--candidate-motion', type=Path)
    parser.add_argument('--candidate-poses', type=int, default=400)
    result = verify(**vars(parser.parse_args()))
    print(json.dumps({name: {key: c[key] for key in ['passed', 'checked_poses', 'maximum_intersection_volume_mm3']}
                      for name, c in result['checks'].items()}, indent=2))
    if not result['all_sampled_poses_clear']:
        raise SystemExit(1)
