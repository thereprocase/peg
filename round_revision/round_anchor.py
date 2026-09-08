"""Prototype truly round pegboard anchor; not the released baseline.

Units mm; X across board, Y toward user, Z up. Circular upper neck and tongue
use a union of cylinders and spheres. The lower locator is a circular cylinder
with a conical nose chamfer. No flat is cut into either bearing section.

Run from this directory to export both un-supported print orientations and STEP.
Motion validation and printable support design live in separate revision files.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh
from shapely.geometry import box


ROOT = Path(__file__).resolve().parent
DEFAULTS = dict(
    board_thickness=3.94,
    hole_diameter=6.35,
    pitch=25.4,
    peg_diameter=5.0,
    diametral_clearance=None,
    locator_diameter=None,
    spine_width=6.0,
    spine_depth=4.5,
    spine_height=34.6,
    spine_top=4.2,
    spine_corner_radius=0.65,
    front_gap=0.15,
    seat_drop=0.12,
    pull_clearance=0.47,
    elbow_offset=None,
    root_y=1.4,
    tongue_run=5.0,
    tongue_rise=3.0,
    locator_depth=2.3,
    locator_root_y=0.6,
    locator_chamfer=0.5,
)


def geometry(params=None):
    """Return the resolved parameters and exact primitive geometry contract."""
    p = DEFAULTS | (params or {})
    if p['diametral_clearance'] is not None:
        if not 0 < p['diametral_clearance'] < p['hole_diameter']:
            raise ValueError('Diametral clearance must be positive and below hole diameter')
        p['peg_diameter'] = p['hole_diameter']-p['diametral_clearance']
    if p['locator_diameter'] is None:
        p['locator_diameter'] = p['peg_diameter']
    for key in ['board_thickness', 'hole_diameter', 'pitch', 'peg_diameter',
                'locator_diameter', 'spine_width', 'spine_depth', 'spine_height',
                'tongue_run', 'tongue_rise', 'locator_depth']:
        if p[key] <= 0:
            raise ValueError(f'{key} must be positive')
    if max(p['peg_diameter'], p['locator_diameter']) >= p['hole_diameter']:
        raise ValueError('Peg diameters must be below the actual hole diameter')
    if p['pitch'] <= p['hole_diameter']:
        raise ValueError('Pitch must exceed the hole diameter')
    if not 0 <= p['locator_chamfer'] < min(p['locator_depth'], p['locator_diameter']/2):
        raise ValueError('Locator chamfer must be below its projection and radius')
    radius = p['peg_diameter']/2
    slope = p['tongue_rise']/p['tongue_run']
    if p['elbow_offset'] is None:
        # Initial analytical straight-pull fitting on the symmetry plane.
        # All seated/moving interference claims require the separate study.
        p['elbow_offset'] = (p['pull_clearance'] - p['front_gap']
            - (p['hole_diameter']-radius)/slope
            + radius*math.sqrt(1+1/slope**2))
    center_z = -(p['hole_diameter']-p['peg_diameter'])/2 + p['seat_drop']
    elbow_y = -p['board_thickness']-p['elbow_offset']
    centers = [[0, p['root_y'], center_z],
               [0, elbow_y, center_z],
               [0, elbow_y-p['tongue_run'], center_z+p['tongue_rise']]]
    # Both locator and upper neck share nominal hole-row centers. When diameters
    # differ, the smaller member has radial clearance rather than false bearing.
    lower_z = center_z-p['pitch']
    return dict(
        parameters=p,
        coordinates={'units':'mm', 'x':'across board', 'y':'toward user', 'z':'up',
                     'board_front_y':0, 'board_rear_y':-p['board_thickness']},
        upper_capsule={'radius':radius, 'centers_xyz':centers,
                       'construction':'cylinders between consecutive centers plus spheres at all centers'},
        locator={'radius':p['locator_diameter']/2, 'axis':[0,1,0],
                 'center_x':0, 'center_z':lower_z,
                 'tip_y':-p['locator_depth'], 'root_y':p['locator_root_y'],
                 'chamfer_axial_length':p['locator_chamfer'],
                 'tip_radius':p['locator_diameter']/2-p['locator_chamfer']},
        spine={'x_min':-p['spine_width']/2, 'x_max':p['spine_width']/2,
               'y_min':p['front_gap'], 'y_max':p['spine_depth'],
               'z_min':p['spine_top']-p['spine_height'], 'z_max':p['spine_top'],
               'yz_corner_radius':p['spine_corner_radius']},
        seated_pose={'y':-p['front_gap'], 'z':-p['seat_drop'], 'theta_deg':0},
        section_properties={'upper_area_mm2':math.pi*radius**2,
            'upper_elastic_section_modulus_mm3':math.pi*p['peg_diameter']**3/32,
            'diametral_clearance_mm':p['hole_diameter']-p['peg_diameter'],
            'note':'Geometric section properties; no allowable load established'},
    )


def _sphere(center, radius):
    return cq.Solid.makeSphere(radius, cq.Vector(*center), angleDegrees1=-90,
                               angleDegrees2=90, angleDegrees3=360)


def _cylinder_between(a, b, radius):
    delta = np.asarray(b)-np.asarray(a)
    length = float(np.linalg.norm(delta))
    return cq.Solid.makeCylinder(radius, length, cq.Vector(*a),
                                cq.Vector(*(delta/length)))


def make_round_anchor(**params):
    g = geometry(params)
    p = g['parameters']
    c = g['upper_capsule']['centers_xyz']
    radius = g['upper_capsule']['radius']
    part = cq.Workplane(obj=_sphere(c[0], radius))
    for point in c[1:]:
        part = part.union(cq.Workplane(obj=_sphere(point, radius)))
    for a,b in zip(c[:-1],c[1:]):
        part = part.union(cq.Workplane(obj=_cylinder_between(a,b,radius)))

    s = g['spine']
    planar = box(s['y_min'],s['z_min'],s['y_max'],s['z_max'])
    if s['yz_corner_radius']:
        planar = planar.buffer(-s['yz_corner_radius'],quad_segs=12).buffer(
            s['yz_corner_radius'],quad_segs=12)
    profile = list(planar.exterior.coords[:-1])
    spine = cq.Workplane('YZ', origin=(s['x_min'],0,0)).polyline(profile).close().extrude(
        s['x_max']-s['x_min'])
    part = part.union(spine)

    loc = g['locator']
    axis = cq.Vector(0,1,0)
    cylinder_start = loc['tip_y']+loc['chamfer_axial_length']
    cylinder = cq.Solid.makeCylinder(loc['radius'],loc['root_y']-cylinder_start,
                                     cq.Vector(0,cylinder_start,loc['center_z']),axis)
    part = part.union(cq.Workplane(obj=cylinder))
    if loc['chamfer_axial_length']:
        cone = cq.Solid.makeCone(loc['tip_radius'],loc['radius'],
                                 loc['chamfer_axial_length'],
                                 cq.Vector(0,loc['tip_y'],loc['center_z']),axis)
        part = part.union(cq.Workplane(obj=cone))
    shape = part.val()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise ValueError('Round anchor is invalid or disconnected')
    return part


def print_pose(part, orientation='side'):
    if orientation == 'side':
        part = part.rotate((0,0,0),(0,1,0),-90)
    elif orientation != 'upright':
        raise ValueError('Orientation must be side or upright')
    b = part.val().BoundingBox()
    return part.translate((-b.xmin,-b.ymin,-b.zmin))


def export_candidate(params=None, name='round_candidate', output=None):
    folder = Path(output or ROOT/'cad')
    folder.mkdir(parents=True,exist_ok=True)
    g = geometry(params)
    part = make_round_anchor(**g['parameters'])
    cq.exporters.export(part,str(folder/f'{name}.step'))
    checks = []
    for orientation in ['design','side','upright']:
        suffix = 'design_reference' if orientation == 'design' else f'{orientation}_unsupported'
        filename = folder/f'{name}_{suffix}.stl'
        printable = part if orientation == 'design' else print_pose(part,orientation)
        cq.exporters.export(printable,str(filename),
                             tolerance=.008,angularTolerance=.05)
        mesh = trimesh.load(filename,force='mesh')
        # OCC can emit zero-area triangles at tangent spherical seams. Remove
        # only degenerate facets; do not fill holes or change the bearing shape.
        valid_faces = mesh.nondegenerate_faces(height=1e-10)
        removed_degenerate_faces = int((~valid_faces).sum())
        if removed_degenerate_faces:
            mesh.update_faces(valid_faces)
            mesh.remove_unreferenced_vertices()
            mesh.export(filename)
        if not mesh.is_watertight or not mesh.is_volume:
            raise ValueError(f'Invalid exported mesh: {filename.name}')
        checks.append({'file':filename.name,'watertight':bool(mesh.is_watertight),
                       'positive_volume':bool(mesh.is_volume),
                       'bounds_mm':np.round(mesh.bounds,6).tolist(),
                       'zero_area_export_facets_removed':removed_degenerate_faces,
                       'purpose':'reference geometry' if orientation == 'design' else 'support design input',
                       'supports_required':orientation != 'design'})
    (folder/f'{name}_geometry.json').write_text(json.dumps(g,indent=2)+'\n')
    report = {'candidate':name,'valid_brep':True,'solid_count':1,
              'volume_mm3':part.val().Volume(),'meshes':checks,
              'validation_scope':'Solid/mesh validity only; separate motion and print-support work required',
              'functional_sections':'Circular cylinders; no bearing flats or cosmetic-only rounding'}
    (folder/f'{name}_cad_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--diameter',type=float,default=DEFAULTS['peg_diameter'])
    parser.add_argument('--clearance',type=float,default=None,
                        help='Diametral clearance; overrides --diameter when supplied')
    parser.add_argument('--hole-diameter',type=float,default=DEFAULTS['hole_diameter'])
    parser.add_argument('--thickness',type=float,default=DEFAULTS['board_thickness'])
    parser.add_argument('--elbow-offset',type=float,default=None)
    parser.add_argument('--name',default='round_candidate')
    args = parser.parse_args()
    print(json.dumps(export_candidate({'peg_diameter':args.diameter,
                      'diametral_clearance':args.clearance,'hole_diameter':args.hole_diameter,
                      'board_thickness':args.thickness,'elbow_offset':args.elbow_offset},
                      name=args.name),indent=2))
