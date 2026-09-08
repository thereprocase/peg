"""Sample the released round STEP against actual 3D cylindrical pegboard holes.

This independently supplements the continuous conservative motion certificate.
It is a sampled CAD interference check, not a strength or print-quality test.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import time

import cadquery as cq
import numpy as np


ROOT = Path(__file__).resolve().parent


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sample_poses(waypoints, count):
    path = np.array([[p['y'],p['z'],p['theta_deg']] for p in waypoints],dtype=float)
    if len(path)<2:
        raise ValueError('Need at least two waypoints')
    count = max(count,len(path))
    weights = np.linalg.norm(np.diff(path[:,:2],axis=0),axis=1)+40*np.radians(
        np.abs(np.diff(path[:,2])))
    weights = weights/weights.sum() if weights.sum() else np.full(len(weights),1/len(weights))
    fractional = weights*(count-len(path))
    counts = np.floor(fractional).astype(int)+1
    extras = count-1-int(counts.sum())
    order = np.argsort(-(fractional-np.floor(fractional)))
    counts[order[:extras]] += 1
    result = [path[0].tolist()]
    for a,b,n in zip(path[:-1],path[1:],counts):
        result.extend((a+(b-a)*i/n).tolist() for i in range(1,n+1))
    return result


def verify(motion_path=None, step_path=None, output=None, pose_count=80, columns=1):
    motion_path = Path(motion_path or ROOT/'round_motion_results.json')
    step_path = Path(step_path or ROOT/'cad/round.step')
    output = Path(output or ROOT/'round_occ_motion_check.json')
    motion = json.loads(motion_path.read_text())
    parameters = motion['parameters']
    contract_stem = step_path.stem.removesuffix('_two_column_example')
    contract_path = step_path.with_name(contract_stem+'_geometry.json')
    contract = json.loads(contract_path.read_text())
    mismatches = {}
    for key,expected in contract['parameters'].items():
        if key in parameters and parameters[key] != expected:
            mismatches[key] = {'step_contract':expected,'motion':parameters[key]}
    if mismatches:
        raise ValueError(f'CAD and motion parameters disagree: {mismatches}')
    original = cq.importers.importStep(str(step_path)).val()
    if not original.isValid() or len(original.Solids()) != 1:
        raise ValueError('STEP does not contain one valid functional solid')
    t = parameters['board_thickness']
    pitch = parameters['pitch']
    board = cq.Workplane('XY').box(max(80,(columns-1)*pitch+40),t,120).translate(
        ((columns-1)*pitch/2,-t/2,-pitch/2))
    for x in [i*pitch for i in range(columns)]:
        for z in [0,-pitch]:
            bore = cq.Solid.makeCylinder(parameters['hole_diameter']/2,t+2,
                                         cq.Vector(x,-t-1,z),cq.Vector(0,1,0))
            board = board.cut(cq.Workplane(obj=bore))
    board = board.val()
    poses = sample_poses(motion['removal_poses'],pose_count)
    threshold = 1e-6
    report = dict(
        check='Sampled OpenCascade boolean intersection of the actual round STEP and circular-hole board',
        parameters=contract['parameters'],
        source_files={step_path.name:_sha(step_path),motion_path.name:_sha(motion_path),
                      contract_path.name:_sha(contract_path)},
        anchor_columns=columns,requested_poses=pose_count,checked_poses=0,total_planned_poses=len(poses),
        intersection_volume_threshold_mm3=threshold,
        maximum_intersection_volume_mm3=0.,colliding_poses=[],samples=[],passed=False,
        scope=['Actual cylindrical holes; upper and lower round pegs, nose chamfer, and spine included.',
               'Planar installation/removal about X; intended bearing contact permitted.',
               'Finite samples supplement the separate continuous certificate.',
               'No material, deformation, insertion-force, strength, or printer simulation.'])
    start = time.monotonic()
    for index,(y,z,angle) in enumerate(poses):
        placed = original.rotate((0,0,0),(1,0,0),angle).translate((0,y,z))
        volume = float(placed.intersect(board).Volume())
        sample = dict(index=index,y=y,z=z,theta_deg=angle,intersection_volume_mm3=volume)
        report['samples'].append(sample)
        report['checked_poses'] = index+1
        report['maximum_intersection_volume_mm3'] = max(report['maximum_intersection_volume_mm3'],volume)
        if volume>threshold:
            report['colliding_poses'].append(sample)
        report['elapsed_seconds'] = round(time.monotonic()-start,3)
        output.write_text(json.dumps(report,indent=2)+'\n')
        if index%10==0:
            print(f'Checked {index+1}/{len(poses)} poses; maximum overlap {report["maximum_intersection_volume_mm3"]:.9g} mm3',flush=True)
    report['passed'] = not report['colliding_poses']
    summary = motion.get('summary',{})
    if 'rocking_stop_pose' in summary and 'rocking_pivot_yz' in summary:
        pivot = np.asarray(summary['rocking_pivot_yz'],dtype=float)
        contact = np.array([-parameters['front_gap'],-parameters['seat_drop']])
        stop_angle = abs(summary['rocking_stop_pose']['theta_deg'])
        transitions = []
        for label,delta in [('before_stop',-.05),('at_stop',0),('beyond_stop',.05)]:
            angle = -(stop_angle+delta)
            c,s = math.cos(math.radians(angle)),math.sin(math.radians(angle))
            moved_pivot = np.array([c*pivot[0]-s*pivot[1],s*pivot[0]+c*pivot[1]])
            y,z = contact+pivot-moved_pivot
            placed = original.rotate((0,0,0),(1,0,0),angle).translate((0,float(y),float(z)))
            volume = float(placed.intersect(board).Volume())
            transitions.append({'position':label,'theta_deg':angle,'y':float(y),'z':float(z),
                                'intersection_volume_mm3':volume})
        report['rocking_contact_transition'] = {
            'passed':transitions[0]['intersection_volume_mm3']<=threshold
                     and transitions[1]['intersection_volume_mm3']<=threshold
                     and transitions[2]['intersection_volume_mm3']>threshold,
            'samples':transitions,
            'scope':'Confirms a change from separation/contact to overlap around the predicted rear-shoulder stop; beyond-stop overlap is intentional in this check.'}
        report['passed'] = report['passed'] and report['rocking_contact_transition']['passed']
    output.write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--motion',type=Path,default=ROOT/'round_motion_results.json')
    parser.add_argument('--step',type=Path,default=ROOT/'cad/round.step')
    parser.add_argument('--output',type=Path,default=ROOT/'round_occ_motion_check.json')
    parser.add_argument('--poses',type=int,default=80)
    parser.add_argument('--columns',type=int,default=1)
    args = parser.parse_args()
    result = verify(args.motion,args.step,args.output,args.poses,args.columns)
    print(json.dumps({k:result[k] for k in ['passed','checked_poses','maximum_intersection_volume_mm3','elapsed_seconds']},indent=2))
