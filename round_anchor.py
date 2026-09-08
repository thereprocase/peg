"""Canonical geometry for the truly round pegboard anchor revision.

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
    peg_diameter=5.6,
    diametral_clearance=None,
    tongue_diameter=4.8,
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

# These diameter/thickness combinations have separate continuous motion records
# in round_motion_presets.json. Changed geometry still needs renewed validation.
PRESETS = {
    'round_default_3p94': dict(board_thickness=3.94,hole_diameter=6.35,
        peg_diameter=5.6,locator_diameter=5.6,tongue_diameter=4.8),
    'round_stock_4p19': dict(board_thickness=4.19,hole_diameter=6.35,
        peg_diameter=5.6,locator_diameter=5.6,tongue_diameter=4.8),
    'round_nominal_3_16': dict(board_thickness=4.7625,hole_diameter=6.35,
        peg_diameter=5.4,locator_diameter=5.4,tongue_diameter=4.8),
    'round_true_1_4': dict(board_thickness=6.35,hole_diameter=6.35,
        peg_diameter=5.2,locator_diameter=5.2,tongue_diameter=4.8),
    'round_9_32_holes': dict(board_thickness=3.94,hole_diameter=7.14375,
        peg_diameter=5.6,locator_diameter=5.6,tongue_diameter=4.8),
}


def geometry(params=None):
    """Return the resolved parameters and exact primitive geometry contract."""
    p = DEFAULTS | (params or {})
    if p['diametral_clearance'] is not None:
        if not 0 < p['diametral_clearance'] < p['hole_diameter']:
            raise ValueError('Diametral clearance must be positive and below hole diameter')
        p['peg_diameter'] = p['hole_diameter']-p['diametral_clearance']
    if p['locator_diameter'] is None:
        p['locator_diameter'] = p['peg_diameter']
    if p['tongue_diameter'] is None:
        p['tongue_diameter'] = p['peg_diameter']
    for key in ['board_thickness', 'hole_diameter', 'pitch', 'peg_diameter',
                'locator_diameter', 'tongue_diameter', 'spine_width', 'spine_depth', 'spine_height',
                'tongue_run', 'tongue_rise', 'locator_depth']:
        if p[key] <= 0:
            raise ValueError(f'{key} must be positive')
    if max(p['peg_diameter'], p['locator_diameter']) >= p['hole_diameter']:
        raise ValueError('Peg diameters must be below the actual hole diameter')
    if p['tongue_diameter'] > p['peg_diameter']:
        raise ValueError('Tongue diameter must not exceed the through-neck diameter')
    if p['pitch'] <= p['hole_diameter']:
        raise ValueError('Pitch must exceed the hole diameter')
    if not 0 <= p['locator_chamfer'] < min(p['locator_depth'], p['locator_diameter']/2):
        raise ValueError('Locator chamfer must be below its projection and radius')
    radius = p['peg_diameter']/2
    tongue_radius = p['tongue_diameter']/2
    slope = p['tongue_rise']/p['tongue_run']
    if p['elbow_offset'] is None:
        # Initial analytical straight-pull fitting on the symmetry plane.
        # All seated/moving interference claims require the separate study.
        p['elbow_offset'] = (p['pull_clearance'] - p['front_gap']
            - (p['hole_diameter']-radius)/slope
            + tongue_radius*math.sqrt(1+1/slope**2))
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
                       'segment_radii':[radius,tongue_radius],
                       'ball_radii_at_centers':[radius,radius,tongue_radius],
                       'construction':'Capsule A-B uses neck radius; capsule B-C uses tongue radius; their union retains the large spherical junction at B'},
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
            'tongue_area_mm2':math.pi*tongue_radius**2,
            'tongue_elastic_section_modulus_mm3':math.pi*p['tongue_diameter']**3/32,
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
    segment_radii = g['upper_capsule']['segment_radii']
    ball_radii = g['upper_capsule']['ball_radii_at_centers']
    part = cq.Workplane(obj=_sphere(c[0],ball_radii[0]))
    for point,radius in zip(c[1:],ball_radii[1:]):
        part = part.union(cq.Workplane(obj=_sphere(point,radius)))
    for a,b,radius in zip(c[:-1],c[1:],segment_radii):
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


def round_pair(columns=2, **params):
    """Replicate round anchors on the hole grid with a small front bridge.

    This is an integration example. Its source geometry controls neither a
    complete holder's print orientation nor its installation envelope.
    """
    if not isinstance(columns,int) or columns < 1:
        raise ValueError('columns must be a positive integer')
    p = geometry(params)['parameters']
    anchor = make_round_anchor(**p)
    part = anchor
    for i in range(1,columns):
        part = part.union(anchor.translate((i*p['pitch'],0,0)))
    if columns > 1:
        bridge_front = p['spine_depth']-.3
        bridge = cq.Workplane('XY').box(
            (columns-1)*p['pitch']+p['spine_width'],3.0,6.0).translate(
                ((columns-1)*p['pitch']/2,bridge_front+1.5,-p['pitch']/2))
        part = part.union(bridge)
    if not part.val().isValid() or len(part.val().Solids()) != 1:
        raise ValueError('Column example is not one valid solid')
    return part


def export_pair(params=None, name='round_two_column_example', output=None):
    folder = Path(output or ROOT/'cad')
    folder.mkdir(parents=True,exist_ok=True)
    part = round_pair(**(params or {}))
    cq.exporters.export(part,str(folder/f'{name}.step'))
    return {'file':f'{name}.step','valid_brep':True,'solid_count':1,
            'columns':2,'volume_mm3':part.val().Volume(),
            'purpose':'CAD integration example; complete host needs its own print and motion checks'}


def export_candidate(params=None, name='round', output=None):
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


def export_presets(skip_default=False):
    records = []
    for preset,params in PRESETS.items():
        name = 'round' if preset == 'round_default_3p94' else preset
        if skip_default and preset == 'round_default_3p94':
            result = json.loads((ROOT/'cad/round_cad_validation.json').read_text())
        else:
            result = export_candidate(params,name=name)
        records.append({'preset':preset,**result})
        print(f'{preset}: valid solid and watertight exports',flush=True)
    report = {'passed':all(r['valid_brep'] and all(m['watertight'] for m in r['meshes']) for r in records),
              'variants':records,'motion_evidence':'round_motion_presets.json'}
    (ROOT/'round_cad_presets_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--diameter',type=float,default=DEFAULTS['peg_diameter'])
    parser.add_argument('--clearance',type=float,default=None,
                        help='Diametral clearance; overrides --diameter when supplied')
    parser.add_argument('--tongue-diameter',type=float,default=DEFAULTS['tongue_diameter'],
                        help='Optional smaller circular retaining-tongue diameter')
    parser.add_argument('--hole-diameter',type=float,default=DEFAULTS['hole_diameter'])
    parser.add_argument('--thickness',type=float,default=DEFAULTS['board_thickness'])
    parser.add_argument('--elbow-offset',type=float,default=None)
    parser.add_argument('--name',default='round')
    parser.add_argument('--all-presets',action='store_true',
                        help='Rebuild all five motion-checked diameter/thickness combinations')
    args = parser.parse_args()
    if args.all_presets:
        report = export_presets()
        report['two_column_example'] = export_pair()
        print(json.dumps({'passed':report['passed'],'variants':len(report['variants']),
                          'two_column_example':report['two_column_example']},indent=2))
        raise SystemExit(0)
    params = {'peg_diameter':args.diameter,
                      'diametral_clearance':args.clearance,'hole_diameter':args.hole_diameter,
                      'tongue_diameter':args.tongue_diameter,
                      'board_thickness':args.thickness,'elbow_offset':args.elbow_offset}
    print(json.dumps({'anchor':export_candidate(params,name=args.name),
                      'two_column_example':export_pair(params,name=args.name+'_two_column_example')},indent=2))
