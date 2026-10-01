"""Create smooth, connected tweezers meshes from measured/scanned references.

Run: python build_models.py
Edit parameters.json to adjust any estimated dimensions. Coordinates and mesh
exports are millimetres; GLB files are explicitly converted to metres.
"""
import base64
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.collections import PolyCollection
from scipy.interpolate import CubicSpline, PchipInterpolator

ROOT = Path(__file__).resolve().parent
P = json.loads((ROOT / 'parameters.json').read_text())
LENGTH = P['length_mm']
JOIN = P['joined_rear_length_mm']

def interpolator(key, cubic=False):
    points = np.asarray(P[key], dtype=float)
    if cubic:
        return CubicSpline(points[:, 0], points[:, 1], bc_type='natural')
    return PchipInterpolator(points[:, 0], points[:, 1])

WIDTH = interpolator('width_profile_mm')
CENTER = interpolator('face_centerline_mm', cubic=True)
THICKNESS = interpolator('single_arm_thickness_mm')
OPEN_GAP = interpolator('open_gap_profile_mm')

def section_shape(y, gap=0.0, inner_bevel=True):
    """CCW rounded cross-section of the upper arm in the X/Z plane."""
    radius = P['rear_rounding_radius_mm']
    width = float(WIDTH(max(y, radius)))
    if y < radius:
        width = 2 * np.sqrt(max(radius ** 2 - (y - radius) ** 2, 0))
    # An imperceptibly narrow flat closes the rounded rear without collapsed
    # triangles. The finite sharp tip is similarly capped as a valid solid.
    width = max(width, .02)
    half_width = width / 2
    thickness = float(THICKNESS(y))
    outer_bevel = min(P['edge_radius_mm'], thickness * .22, width * .22)
    blend = np.clip((y - JOIN) / 3.0, 0, 1)
    blend = blend * blend * (3 - 2 * blend)
    bottom_bevel = outer_bevel * blend if inner_bevel else 0.0
    z0, z1 = gap / 2, gap / 2 + thickness
    corners = [
        (half_width - bottom_bevel, z0 + bottom_bevel, bottom_bevel, -90),
        (half_width - outer_bevel, z1 - outer_bevel, outer_bevel, 0),
        (-half_width + outer_bevel, z1 - outer_bevel, outer_bevel, 90),
        (-half_width + bottom_bevel, z0 + bottom_bevel, bottom_bevel, 180),
    ]
    points = []
    for x, z, bevel, angle in corners:
        theta = np.deg2rad(np.linspace(angle, angle + 90, 9))
        points.extend(np.column_stack([x + bevel * np.cos(theta),
                                       z + bevel * np.sin(theta)]))
    points = np.asarray(points)
    points[:, 0] += float(CENTER(y))
    return points

def gap_at(y, pose):
    if y <= JOIN:
        return 0.0
    if pose == 'open_rest':
        return float(OPEN_GAP(y))
    fraction = (y - JOIN) / (LENGTH - JOIN)
    return float(.9 * np.sin(np.pi * fraction) ** 2
                 + P['closed_tip_clearance_mm'] * fraction ** 2)

def make_mesh(pose):
    vertices, faces = [], []
    def add_ring(section, y):
        start = len(vertices)
        vertices.extend(np.column_stack([section[:, 0], np.full(len(section), y), section[:, 1]]))
        return np.arange(start, start + len(section))
    def connect(previous, following):
        for i in range(len(previous)):
            j = (i + 1) % len(previous)
            faces.extend([[previous[i], following[i], previous[j]],
                          [previous[j], following[i], following[j]]])
    def cap(ring, end):
        center = len(vertices)
        vertices.append(np.asarray(vertices)[ring].mean(axis=0))
        for i in range(len(ring)):
            j = (i + 1) % len(ring)
            faces.append([center, ring[j], ring[i]] if end else [center, ring[i], ring[j]])
    # The rear perimeter is the outside of the TWO fused half sections. No
    # interior cap or overlapping rear block remains in the final mesh.
    previous = None
    rear_stations = np.unique(np.concatenate([
        np.linspace(0, JOIN, 120), np.linspace(0, .5, 24),
        np.array([10.0, P['rear_rounding_radius_mm']])]))
    for y in rear_stations:
        upper = section_shape(float(y), inner_bevel=False)[[0] + list(range(9, 27)) + [27]]
        lower = upper.copy(); lower[:, 1] *= -1
        rear = np.concatenate([upper, lower[-2:0:-1]])
        ring = add_ring(rear, float(y))
        if previous is None:
            cap(ring, False)
        else:
            connect(previous, ring)
        previous = ring
    stations = np.unique(np.concatenate([
        np.linspace(JOIN, LENGTH, 500),
        np.asarray(P['single_arm_thickness_mm'])[:, 0],
        np.asarray(P['width_profile_mm'])[:, 0],
        np.asarray(P['face_centerline_mm'])[:, 0],
        np.asarray(P['open_gap_profile_mm'])[:, 0],
    ]))
    stations = stations[(stations >= JOIN) & (stations <= LENGTH)]
    for sign in [1, -1]:
        previous = None
        for y in stations:
            section = section_shape(float(y), gap_at(float(y), pose))
            if sign < 0:
                section[:, 1] *= -1
                section = section[::-1]
            ring = add_ring(section, float(y))
            if previous is not None:
                connect(previous, ring)
            previous = ring
        cap(previous, True)
    mesh = trimesh.Trimesh(vertices=np.asarray(vertices), faces=np.asarray(faces), process=False)
    mesh.process(validate=True)
    mesh.fix_normals()
    mesh.metadata.update({'units': 'mm', 'pose': pose, 'length_mm': LENGTH})
    if not mesh.is_watertight or not mesh.is_winding_consistent or not mesh.is_volume:
        raise RuntimeError(f'{pose}: invalid solid after meshing')
    if mesh.body_count != 1:
        raise RuntimeError(f'{pose}: expected one joined solid, got {mesh.body_count}')
    return mesh

def export_mesh(mesh, pose):
    (ROOT / f'tweezers_{pose}.obj').write_text(
        '# Smooth reconstructed tweezers; coordinates in millimetres.\n'
        + trimesh.exchange.obj.export_obj(mesh, include_normals=True,
                                          include_color=False, include_texture=False))
    mesh.export(ROOT / f'tweezers_{pose}.stl')
    glb_mesh = mesh.copy()
    glb_mesh.apply_scale(.001)
    glb_mesh.metadata['units'] = 'm'
    glb_mesh.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
        name='Brushed steel', baseColorFactor=[157, 166, 179, 255],
        metallicFactor=.85, roughnessFactor=.32))
    glb_scene = trimesh.Scene()
    glb_scene.add_geometry(glb_mesh, node_name=pose, geom_name='Tweezers')
    glb_scene.export(ROOT / f'tweezers_{pose}.glb', include_normals=True)
    return {
        'pose': pose, 'vertices': len(mesh.vertices), 'triangles': len(mesh.faces),
        'watertight': bool(mesh.is_watertight), 'consistent_winding': bool(mesh.is_winding_consistent),
        'positive_volume': bool(mesh.is_volume), 'connected_bodies': mesh.body_count,
        'bounds_mm': mesh.bounds.tolist(), 'dimensions_mm': mesh.extents.tolist(),
        'volume_mm3': float(mesh.volume), 'closed_tip_clearance_mm':
            P['closed_tip_clearance_mm'] if pose == 'closed_pinched' else None,
    }

def make_preview(meshes):
    fig, axes = plt.subplots(2, 2, figsize=(16, 7), facecolor='#f4f6f8',
                             gridspec_kw={'width_ratios': [1.35, 1]})
    light = np.array([-.25, -.5, .829]); light /= np.linalg.norm(light)
    view = np.array([.20, -.60, .77]); view /= np.linalg.norm(view)
    right = np.cross([0, 0, 1], view); right /= np.linalg.norm(right)
    up = np.cross(view, right)
    for row, (pose, mesh) in enumerate(meshes.items()):
        triangles = mesh.triangles[:, :, [1, 0, 2]]
        normals = mesh.vertex_normals[mesh.faces].mean(axis=1)[:, [1, 0, 2]]
        normals /= np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-12)
        brightness = .40 + .44 * np.maximum(normals @ light, 0) + .08 * np.abs(normals[:, 2])
        colors = np.column_stack([brightness * .87, brightness * .94, brightness, np.ones(len(brightness))])
        projected = np.stack([triangles @ right, triangles @ up], axis=2)
        order = np.argsort(triangles.mean(axis=1) @ view)
        ax = axes[row, 0]
        ax.add_collection(PolyCollection(projected[order], facecolors=colors[order], edgecolors='none'))
        low, high = projected.min(axis=(0, 1)), projected.max(axis=(0, 1))
        ax.set_xlim(low[0] - 3, high[0] + 3)
        ax.set_ylim(low[1] - 4, high[1] + 4)
        ax.set_aspect('equal'); ax.set_facecolor('#f4f6f8'); ax.set_axis_off()
        ax.set_title('Open at rest' if pose == 'open_rest' else 'Pinched closed', fontsize=17, pad=18)
        ax = axes[row, 1]
        order = np.argsort(mesh.triangles_center[:, 0])
        ax.add_collection(PolyCollection(mesh.triangles[order][:, :, [1, 2]],
                                         facecolors=colors[order], edgecolors='none'))
        ax.set_xlim(-2, LENGTH + 2); ax.set_ylim(-11, 8); ax.set_aspect('equal')
        ax.set_facecolor('#f4f6f8'); ax.set_axis_off()
        ax.set_title('Side view — arm separation', fontsize=13)
        ax.plot([0, LENGTH], [-6.6, -6.6], color='#8995a3', lw=1)
        ax.text(LENGTH / 2, -8, '122.76 mm overall', ha='center', va='top', color='#435163', fontsize=11)
    fig.suptitle('Smooth reconstructed tweezers', fontsize=21, y=.95)
    fig.text(.5, .065, 'Fused aft end: 1.17 mm → 1.31 mm     |     Forward single arm: 1.47 mm\n'
             'Open separation and unmeasured transitions fitted from the scans.',
             ha='center', va='center', fontsize=11, color='#435163')
    fig.subplots_adjust(left=.025, right=.975, bottom=.17, top=.82, hspace=.25, wspace=.10)
    fig.savefig(ROOT / 'preview.png', dpi=150)
    plt.close(fig)

def make_viewer(meshes):
    encoded = {}
    for pose, mesh in meshes.items():
        positions = mesh.vertices[:, [1, 2, 0]].copy()
        positions[:, 0] -= LENGTH / 2
        positions[:, 2] -= 1.0
        normals = mesh.vertex_normals[:, [1, 2, 0]]
        def pack(array, dtype):
            return base64.b64encode(np.asarray(array, dtype=dtype).tobytes()).decode('ascii')
        encoded[pose] = {'positions': pack(positions, '<f4'), 'normals': pack(normals, '<f4'),
                         'indices': pack(mesh.faces, '<u4'), 'count': int(mesh.faces.size)}
    template = (ROOT / 'viewer_template.html').read_text()
    (ROOT / 'viewer.html').write_text(template.replace('__MODEL_DATA__', json.dumps(encoded)))

def verify_exports(meshes, report):
    for pose, original in meshes.items():
        for suffix in ['stl', 'obj']:
            loaded = trimesh.load(ROOT / f'tweezers_{pose}.{suffix}', force='mesh', process=True)
            assert loaded.is_watertight and loaded.is_volume and loaded.body_count == 1
            assert abs(loaded.extents[1] - LENGTH) < .001
        glb = trimesh.load(ROOT / f'tweezers_{pose}.glb', force='mesh', process=True)
        assert glb.is_watertight and glb.is_volume
        assert abs(glb.extents[1] * 1000 - LENGTH) < .001
        rear_vertices = original.vertices[np.isclose(original.vertices[:, 1], 0)]
        rear_thickness = float(np.ptp(rear_vertices[:, 2]))
        aft = original.section(plane_normal=[0, 1, 0], plane_origin=[0, 10, 0])
        aft_thickness = float(np.ptp(aft.vertices[:, 2]))
        arm = original.section(plane_normal=[0, 1, 0], plane_origin=[0, 86, 0])
        arm_thicknesses = [float(np.ptp(loop[:, 2])) for loop in arm.discrete]
        tip_vertices = original.vertices[np.isclose(original.vertices[:, 1], LENGTH)]
        tip_gap = float(2 * np.min(np.abs(tip_vertices[:, 2])))
        assert abs(rear_thickness - 1.17) < .001
        assert abs(aft_thickness - 1.31) < .001
        assert len(arm_thicknesses) == 2 and all(abs(t - 1.47) < .001 for t in arm_thicknesses)
        expected_gap = P['open_tip_gap_mm'] if pose == 'open_rest' else P['closed_tip_clearance_mm']
        assert abs(tip_gap - expected_gap) < .001
        next(r for r in report if r['pose'] == pose)['measured_section_checks_mm'] = {
            'fused_rear_total': rear_thickness, 'aft_total_at_interpolated_station_10': aft_thickness,
            'individual_arms_at_interpolated_station_86': arm_thicknesses, 'tip_clear_gap': tip_gap}
    (ROOT / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')

if __name__ == '__main__':
    meshes, report = {}, []
    for pose in ['open_rest', 'closed_pinched']:
        mesh = make_mesh(pose)
        meshes[pose] = mesh
        report.append(export_mesh(mesh, pose))
        print(f'{pose}: exported {len(mesh.faces):,} faces, one watertight solid', flush=True)
    verify_exports(meshes, report)
    make_preview(meshes)
    make_viewer(meshes)
    print('Both models, preview, viewer and validation complete.', flush=True)
