"""Export a reusable allowed host volume, tied to one verified motion path.

The rear boundary is a conservative polygonal approximation of the exact
continuous motion envelope. Chords of its convex setback function lie on the
safe side; every exported polygon vertex also receives a continuous check.
The volume is in anchor design coordinates, ready to overlay in downstream CAD.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import cadquery as cq

from host_envelope import required_setback, max_flush_height, certify_host_polygon

ROOT = Path(__file__).resolve().parent


def export(motion=ROOT/'round_motion_results.json', output=ROOT/'cad/host-envelope',
           nominal_lip=5.0, width=100.0, minimum_height=-80.0,
           maximum_height=100.0, front_limit=60.0, height_step=1.0):
    motion, output = Path(motion), Path(output)
    data = json.loads(motion.read_text())
    if data.get('verification',{}).get('passed') is not True:
        raise ValueError('Allowed-volume export requires a passed motion record')
    if min(width,front_limit,height_step)>0 and minimum_height < nominal_lip < maximum_height:
        pass
    else:
        raise ValueError('Need positive dimensions and heights bracketing the lip')
    poses = data['removal_poses']
    seated = poses[0]
    limit = max_flush_height(poses)
    exact_height = limit['maximum_physical_height_above_upper_hole_mm']
    if exact_height is None or nominal_lip > exact_height+1e-9:
        raise ValueError('Requested nominal flush lip exceeds the input motion envelope')
    height_reserve = exact_height - nominal_lip
    heights = [minimum_height,nominal_lip]
    z = nominal_lip+height_step
    while z < maximum_height:
        heights.append(z)
        z += height_step
    heights.append(maximum_height)
    curve = []
    for h in heights:
        raw = required_setback(poses,h+height_reserve)
        y = raw['required_design_y_mm']
        if y+seated['y'] >= front_limit:
            raise ValueError('Increase front_limit to contain the requested envelope height')
        curve.append((y,h-seated['z']))
    front = front_limit-seated['y']
    polygon = curve + [(front,maximum_height-seated['z']),
                       (front,minimum_height-seated['z'])]
    certificate = certify_host_polygon(poses,polygon)
    if not certificate['passed']:
        raise ValueError('Allowed host polygon failed the continuous board-front check')
    output.mkdir(parents=True,exist_ok=True)
    part = cq.Workplane('YZ',origin=(-width/2,0,0)).polyline(polygon).close().extrude(width)
    path = output/'allowed_host_volume.step'
    cq.exporters.export(part,str(path))
    reread = cq.importers.importStep(str(path)).val()
    if not reread.isValid() or len(reread.Solids()) != 1:
        raise ValueError('Allowed host volume did not survive STEP export')
    report = {
        'schema_version':1,'source_motion_file':motion.relative_to(ROOT).as_posix() if motion.is_relative_to(ROOT) else str(motion),
        'source_motion_sha256':hashlib.sha256(motion.read_bytes()).hexdigest(),
        'source_motion_name':data.get('name'),
        'nominal_flush_lip_height_above_upper_hole_mm':nominal_lip,
        'geometric_flush_height_limit_mm':exact_height,
        'vertical_envelope_reserve_mm':height_reserve,
        'design_rule':'All added host material must be contained in this allowed volume in anchor design coordinates. The anchor itself is excluded from this containment rule.',
        'construction':'Exact continuous required-setback function evaluated at heights; its convexity makes joining chords conservative. The nominal envelope is shifted downward to place its flush limit at the requested lip height.',
        'envelope_vertices_design_yz_mm':polygon,
        'rear_boundary_design_yz_mm':curve,
        'coordinates':'Anchor design coordinates; apply the first removal pose with the complete anchor and host for installed inspection.',
        'nominal_setbacks_mm':[
            {'height_above_upper_hole_mm':h,
             'minimum_installed_setback_mm':required_setback(poses,h+height_reserve)['required_installed_setback_mm']}
            for h in [5,10,20,30,50,100] if minimum_height<=h<=maximum_height],
        'export_clip':{'x_min_mm':-width/2,'x_max_mm':width/2,
                       'minimum_installed_height_mm':minimum_height,
                       'maximum_installed_height_mm':maximum_height,
                       'maximum_installed_front_projection_mm':front_limit},
        'continuous_host_certificate':certificate,
        'step_valid':True,'step_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'limitations':[
            'This envelope applies only to the specified motion and anchor geometry; regenerate after changing either.',
            'The 100 mm width and height/front extents clip the display/export volume, not the mathematical interface; regenerate larger bounds for larger hosts.',
            'Checks board-front clearance only. Neighboring objects, rear wall, host strength, printing and hand access need separate checks.',
            'Other anchor variants cannot inherit this envelope without a corresponding passed motion record. This geometric check does not qualify a model for printing.',
        ],
        'generator_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'host_envelope.py']},
    }
    (output/'allowed_host_volume.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--motion',type=Path,default=ROOT/'round_motion_results.json')
    parser.add_argument('--output',type=Path,default=ROOT/'cad/host-envelope')
    parser.add_argument('--nominal-lip',type=float,default=5.0)
    parser.add_argument('--width',type=float,default=100.0)
    parser.add_argument('--minimum-height',type=float,default=-80.0)
    parser.add_argument('--maximum-height',type=float,default=100.0)
    parser.add_argument('--front-limit',type=float,default=60.0)
    parser.add_argument('--height-step',type=float,default=1.0)
    args=parser.parse_args()
    r=export(**vars(args))
    print(json.dumps({k:r[k] for k in ['nominal_flush_lip_height_above_upper_hole_mm','geometric_flush_height_limit_mm','vertical_envelope_reserve_mm','step_valid']},indent=2))
