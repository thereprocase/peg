"""Experimental 120-degree conformal bearing; independent of round release.

Exact lower circular segments are added to the existing round core. The lower
locator's cylindrical land reaches the board rear, with its lead-in beyond it.
No current round motion or slicer certificate applies to these exports.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import importlib.metadata

import cadquery as cq
import numpy as np
import trimesh

from round_anchor import geometry, make_round_anchor, print_pose

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'cad' / 'conformal'


def contract(overrides=None, bearing_angle=120.0, land_through_board=True,
             upper_land_through_board=False):
    if not 0 < bearing_angle < 180:
        raise ValueError('Bearing angle must lie between 0 and 180 degrees')
    overrides = dict(overrides or {})
    p = geometry(overrides)['parameters']
    # Preserve the lower spine height while changing its top independently.
    top = overrides.get('spine_top', 5.0 + p['seat_drop'])
    p.update(spine_corner_radius=0.0, spine_top=top,
             spine_height=top + 30.4)
    if land_through_board:
        p['locator_depth'] = p['board_thickness'] - p['front_gap'] + p['locator_chamfer']
    g = geometry(p)
    p = g['parameters']
    g['host_interface'] = {
        'nominal_flush_lip_height_above_upper_hole_mm': top-p['seat_drop'],
        'board_facing_corner_radius_mm': 0.0,
        'rule': 'All attached host material must lie within the allowed envelope of the same verified motion. The nominal lip is not a limit on total host height.',
    }
    R = p['hole_diameter'] / 2
    half = math.radians(bearing_angle / 2)
    front = p['front_gap']
    rear = front - p['board_thickness']
    upper_rear = rear if upper_land_through_board else g['upper_capsule']['centers_xyz'][1][1]
    lower_rear = -p['locator_depth'] + p['locator_chamfer']
    g['conformal_bearing'] = {
        'angle_deg': bearing_angle, 'radius_mm': R,
        'arc_width_mm': 2 * R * math.sin(half),
        'arc_length_mm': R * 2 * half,
        'chord_z_relative_to_hole_mm': -R * math.cos(half),
        'construction': 'Exact lower circular segment fused to the round core; upper core and 4.8 mm tongue retained.',
        'upper_land_through_board': upper_land_through_board,
        'lower_land_through_board': land_through_board,
        'lands': [
            {'name': 'upper', 'center_z': p['seat_drop'], 'rear_y': upper_rear,
             'front_y': p['root_y'], 'axial_bearing_length_mm': front - upper_rear},
            {'name': 'lower', 'center_z': p['seat_drop'] - p['pitch'],
             'rear_y': lower_rear, 'front_y': p['locator_root_y'],
             'axial_bearing_length_mm': min(p['board_thickness'], front - lower_rear)},
        ],
        'nominal_contact_area_per_full_land_mm2': R * 2 * half * p['board_thickness'],
        'fit': 'Zero nominal radial gap over the arc. Physical full-arc contact depends on measured bore, print accuracy and deformation.',
    }
    for land in g['conformal_bearing']['lands']:
        land['nominal_contact_area_mm2'] = R * 2 * half * land['axial_bearing_length_mm']
    g['status'] = 'Experimental candidate; requires its own motion, support and physical checks.'
    return g


def saddle_segment(g, land, chamfer=False):
    b = g['conformal_bearing']
    R = b['radius_mm']
    z = land['center_z']
    ch = g['parameters']['locator_chamfer'] if chamfer else 0.0
    if ch:
        solid = cq.Solid.makeCone(R-ch, R, ch,
            cq.Vector(0,land['rear_y']-ch,z), cq.Vector(0,1,0))
        start, length = land['rear_y']-ch, ch
    else:
        start = land['rear_y']
        length = land['front_y'] - start
        solid = cq.Solid.makeCylinder(R, length,
            cq.Vector(0,start,z), cq.Vector(0,1,0))
    cutoff = z + b['chord_z_relative_to_hole_mm']
    clip = cq.Solid.makeBox(2*R+2, length+2, cutoff-(z-R-1),
                            cq.Vector(-R-1,start-1,z-R-1))
    return solid.intersect(clip)


def make_conformal_anchor(overrides=None, bearing_angle=120.0, land_through_board=True,
                         upper_land_through_board=False):
    g = contract(overrides, bearing_angle, land_through_board, upper_land_through_board)
    part = make_round_anchor(**g['parameters'])
    for land in g['conformal_bearing']['lands']:
        part = part.union(cq.Workplane(obj=saddle_segment(g,land)))
        if land['name'] == 'lower' and g['parameters']['locator_chamfer']:
            part = part.union(cq.Workplane(obj=saddle_segment(g,land,True)))
    if not part.val().isValid() or len(part.val().Solids()) != 1:
        raise ValueError('Conformal candidate must be one valid solid')
    return part, g


def export(overrides=None, bearing_angle=120.0, output=OUT, name='conformal_120',
           upper_land_through_board=False):
    output = Path(output)
    output.mkdir(parents=True,exist_ok=True)
    part, g = make_conformal_anchor(overrides,bearing_angle,
                                   upper_land_through_board=upper_land_through_board)
    step = output / f'{name}.step'
    cq.exporters.export(part,str(step))
    imported = cq.importers.importStep(str(step)).val()
    checks = []
    for pose in ['design','side','upright']:
        shape = part if pose == 'design' else print_pose(part,pose)
        path = output / f'{name}_{pose}_unsupported.stl'
        cq.exporters.export(shape,str(path),tolerance=.008,angularTolerance=.05)
        mesh = trimesh.load(path,force='mesh')
        keep = mesh.nondegenerate_faces(height=1e-10)
        mesh.update_faces(keep)
        mesh.remove_unreferenced_vertices()
        mesh.export(path)
        checks.append({'file':path.name,'watertight':bool(mesh.is_watertight),
                       'positive_volume':bool(mesh.is_volume)})
    report = {'valid_brep':imported.isValid(),'solid_count':len(imported.Solids()),
              'volume_mm3':imported.Volume(),'meshes':checks,
              'passed':imported.isValid() and len(imported.Solids())==1 and all(c['watertight'] and c['positive_volume'] for c in checks),
              'scope':'Solid and mesh validity. No motion or print qualification implied.',
              'runtime':{'python':sys.version,'packages':{n:importlib.metadata.version(n) for n in ['cadquery','numpy','shapely','trimesh']}},
              'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'round_anchor.py',step]}}
    (output/f'{name}_geometry.json').write_text(json.dumps(g,indent=2)+'\n', encoding='utf-8', newline='\n')
    (output/f'{name}_cad_validation.json').write_text(json.dumps(report,indent=2)+'\n', encoding='utf-8', newline='\n')
    if not report['passed']:
        raise ValueError('Exported CAD/mesh validity check failed')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=OUT)
    parser.add_argument('--name',default='conformal_120')
    parser.add_argument('--full-upper-land',action='store_true',
                        help='Reproduce the longer upper saddle experiment, which obstructed the historical path')
    args = parser.parse_args()
    print(json.dumps(export(output=args.output,name=args.name,
                            upper_land_through_board=args.full_upper_land),indent=2))
