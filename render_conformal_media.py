"""Render the current conformal solid and its verified motion from exported CAD.

The animation and motion sweep use an actual STEP central section. They are
illustrations of a separately certified three-dimensional path, not clearance
proofs. Every rendered file records hashes of its current geometry and evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import cadquery as cq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, Polygon as PatchPolygon, Rectangle
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, PngImagePlugin
from shapely.geometry import Polygon
from shapely.ops import unary_union
import trimesh

import render_round_common as studio
from render_conformal import (BG, BLUE, GRID, INK, MUTED, ORANGE, PALE, TAN,
                              dimension, draw_sections, section_polygons)

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def checked_inputs(geometry, step, mesh, motion, envelope):
    g = json.loads(geometry.read_text(encoding='utf-8'))
    m = json.loads(motion.read_text(encoding='utf-8'))
    h = json.loads(envelope.read_text(encoding='utf-8'))
    if m.get('verification', {}).get('passed') is not True:
        raise ValueError('Rendering requires an explicitly passed continuous motion record')
    if m.get('geometry_contract') != g:
        raise ValueError('Motion certificate does not describe the displayed geometry')
    hashes = {Path(k.replace('\\', '/')).as_posix(): v
              for k, v in m.get('source_sha256', {}).items()}
    for path in (geometry, step):
        key = path.relative_to(ROOT).as_posix()
        if hashes.get(key) != digest(path):
            raise ValueError(f'Motion certificate is stale for {key}')
    if h.get('source_motion_sha256') != digest(motion):
        raise ValueError('Host envelope does not match the displayed motion')
    if h.get('continuous_host_certificate', {}).get('passed') is not True:
        raise ValueError('Rendering requires a passed host-envelope certificate')
    if digest(envelope.with_suffix('.step')) != h.get('step_sha256'):
        raise ValueError('Host envelope STEP does not match its certificate')
    provenance = {p.relative_to(ROOT).as_posix(): digest(p)
                  for p in (geometry, step, mesh, motion, envelope, envelope.with_suffix('.step'))}
    shape = cq.importers.importStep(str(step)).val()
    side = section_polygons(shape, 'YZ', (0, 0, 0), [1, 2], (0, 0, 0))
    seat = g['seated_pose']
    shift = np.array([0, seat['y'], seat['z']])
    transverse = section_polygons(shape, 'XZ', (0, -g['parameters']['board_thickness']/2-seat['y'], 0), [0, 2], shift)
    upper = [a for a in transverse if a[:, 1].mean() > -g['parameters']['pitch']/2]
    poses = np.asarray([[q['y'], q['z'], q['theta_deg']] if isinstance(q, dict) else q
                        for q in m['removal_poses']], dtype=float)
    return g, m, h, side, upper, poses, provenance


def savefig(fig, target, provenance, svg=True):
    metadata = {'Description': json.dumps(provenance, sort_keys=True)}
    fig.savefig(target.with_suffix('.png'), dpi=160, facecolor=BG, metadata=metadata)
    if svg:
        fig.savefig(target.with_suffix('.svg'), facecolor=BG, metadata=metadata)
        path = target.with_suffix('.svg')
        path.write_text('\n'.join(line.rstrip() for line in path.read_text(encoding='utf-8').splitlines())+'\n', encoding='utf-8', newline='\n')
    plt.close(fig)


def font(size, bold=False):
    for path in [Path('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf'),
                 Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return studio.font(size, bold)


def hero(g, mesh_path, out, provenance):
    model = trimesh.load(mesh_path, force='mesh')
    p = g['parameters']
    W, H = studio.W, studio.H
    yy, xx = np.mgrid[:H, :W]
    glow = np.exp(-((xx-1470)/1100)**2-((yy-880)/660)**2)
    base = np.zeros((H, W, 3), dtype=np.float32)+[12, 21, 30]
    base += glow[:, :, None]*np.array([13, 23, 28])
    img = Image.fromarray(np.uint8(base))
    flat = model.copy()
    flat.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2, [0, 1, 0]))
    objects = []
    for obj, center in [(model, [-28.18, -4.10, 0]), (flat, [3.75, 12.90, 0])]:
        v = obj.vertices.copy()
        lo, hi = v.min(axis=0), v.max(axis=0)
        v[:, 0] -= (lo[0]+hi[0])/2
        v[:, 1] -= (lo[1]+hi[1])/2
        v[:, 2] -= lo[2]
        v += center
        objects.append((obj, v))
    mask = Image.new('L', (W, H), 0)
    md = ImageDraw.Draw(mask)
    for obj, v in objects:
        shadow = v.copy()
        shadow[:, :2] += shadow[:, 2, None]*[.40, .52]
        shadow[:, 2] = -.02
        points = studio.project(shadow)
        for face in obj.faces:
            md.polygon([tuple(q) for q in points[face, :2]], fill=120)
    img = Image.composite(Image.new('RGB', (W, H), (4, 10, 16)), img, mask.filter(ImageFilter.GaussianBlur(21)))
    rgb, depth = np.array(img), np.full((H, W), -np.inf, dtype=np.float32)
    key, fill = studio.unit([-.6, -.9, 1.3]), studio.unit([.8, .5, .7])
    half = studio.unit(key+studio.CAM)
    for obj, v in objects:
        projected = studio.project(v)
        for normal, face in zip(obj.face_normals, obj.faces):
            if np.dot(normal, studio.CAM) < -1e-8:
                continue
            diffuse = .43+.59*max(0, np.dot(normal, key))+.27*max(0, np.dot(normal, fill))
            spec = max(0, np.dot(normal, half))**38*42
            col = np.clip(np.array([32, 146, 152.])*diffuse+spec, 0, 255).astype(np.uint8)
            studio.raster_triangle(rgb, depth, projected[face, :2], projected[face, 2], col)
    img = Image.fromarray(rgb)
    draw = ImageDraw.Draw(img)
    draw.text((116, 73), 'peg.', font=font(112, True), fill='#eff4f0')
    draw.text((121, 209), '120° BEARING ARCS. A SHARP 5 MM LIP.', font=font(28, True), fill='#97b4b7')
    draw.text((1580, 102), f"Ø{p['hole_diameter']:.2f} MM BORE", font=font(28, True), fill='#d3e0df')
    draw.text((1581, 148), f"{p['board_thickness']:.2f} MM BOARD  /  {p['pitch']:.2f} MM GRID", font=font(22), fill='#739092')
    draw.line((121, 278, 2279, 278), fill='#31454e', width=2)
    draw.text((160, 954), 'CONFORMAL BEARING', font=font(28, True), fill='#dce9e5')
    draw.text((160, 1001), 'Lower curves match the bore.', font=font(23), fill='#8facb0')
    draw.text((160, 1040), 'Full board-depth lower land.', font=font(23), fill='#8facb0')
    draw.line((160, 933, 480, 933), fill='#329ca3', width=3)
    draw.text((1840, 900), 'SECOND VIEW', font=font(28, True), fill='#dce9e5')
    draw.text((1840, 947), 'Same solid, rotated.', font=font(23), fill='#8facb0')
    draw.text((1840, 985), 'Actual exported CAD.', font=font(23), fill='#8facb0')
    draw.line((1840, 879, 2225, 879), fill='#329ca3', width=3)
    draw.line((121, 1205, 2279, 1205), fill='#31454e', width=2)
    draw.text((121, 1251), 'Current conformal geometry  /  Bare solid', font=font(23, True), fill='#a8c0c0')
    draw.text((1360, 1251), 'Prototype: supports and physical fit need review.', font=font(21), fill='#779396')
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text('Description', json.dumps(provenance, sort_keys=True))
    img.save(out/'conformal-hero.png', optimize=True, pnginfo=metadata)


def bearing(g, upper, out, provenance):
    p, b = g['parameters'], g['conformal_bearing']
    R, r = p['hole_diameter']/2, p['peg_diameter']/2
    fig, ax = plt.subplots(figsize=(12, 6.5), facecolor=BG)
    fig.subplots_adjust(left=.05, right=.95, bottom=.20, top=.77)
    fig.text(.05, .91, 'The lower curve matches the hole', fontsize=25, weight='bold')
    fig.text(.05, .855, 'Actual STEP bearing section compared with a smaller circular peg', fontsize=12, color=MUTED)
    for x in [-4.5, 4.5]:
        ax.add_patch(Circle((x, 0), R, fill=False, ec=MUTED, lw=1.4, linestyle='--'))
        ax.plot(x, 0, '+', color=MUTED, ms=6)
    ax.add_patch(Circle((-4.5, -(R-r)), r, fc='#e3e8eb', ec=MUTED, lw=1.2))
    ax.plot(-4.5, -R, 'o', color=ORANGE, ms=6)
    draw_sections(ax, upper, (4.5, 0), facecolor=PALE, edgecolor=BLUE, lw=1.4)
    half = math.radians(b['angle_deg']/2)
    angles = np.linspace(-half, half, 400)
    ax.plot(4.5+R*np.sin(angles), -R*np.cos(angles), color=ORANGE, lw=4)
    for phi in [-half, half]:
        ax.plot([4.5, 4.5+R*math.sin(phi)], [0, -R*math.cos(phi)], color=ORANGE, linestyle=':', lw=1)
    ax.add_patch(Arc((4.5, 0), 2.65, 2.65, theta1=-90-b['angle_deg']/2, theta2=-90+b['angle_deg']/2, ec=ORANGE))
    ax.text(4.5, -.85, f"{b['angle_deg']:g}°", color=ORANGE, ha='center', fontsize=15, weight='bold')
    ax.text(-4.5, 3.65, f"Circular Ø{p['peg_diameter']:.2f} peg", ha='center', fontsize=13, weight='bold')
    ax.text(4.5, 3.65, f'Conformal R{R:.3f} lower arc', ha='center', fontsize=13, weight='bold')
    ax.text(-4.5, -3.85, 'Nominal tangent contact', ha='center', fontsize=11, color=MUTED)
    ax.text(4.5, -3.85, 'Zero nominal gap over 120°', ha='center', fontsize=11, color=ORANGE)
    ax.set(xlim=(-8.5, 8.5), ylim=(-4.2, 4.2), aspect='equal')
    ax.axis('off')
    fig.text(.05, .115, f"Ø{p['hole_diameter']:.2f} bore   /   {b['arc_width_mm']:.3f} mm arc chord   /   {b['arc_length_mm']:.3f} mm arc length", fontsize=12, color=MUTED)
    fig.text(.05, .065, 'Nominal CAD contact. Measured bore size, print accuracy and deformation determine physical contact.', fontsize=10.5, color=MUTED)
    savefig(fig, out/'conformal-bearing', provenance)


def transform(points, pose):
    angle = math.radians(pose[2])
    c, s = math.cos(angle), math.sin(angle)
    return points @ np.array([[c, -s], [s, c]]).T + pose[:2]


def board(ax, p, bottom=-38, top=17):
    R, t, pitch = p['hole_diameter']/2, p['board_thickness'], p['pitch']
    for lo, hi in [(bottom, -pitch-R), (-pitch+R, -R), (R, top)]:
        ax.add_patch(Rectangle((-t, lo), t, hi-lo, facecolor=TAN, edgecolor='#ab9975', lw=.8, zorder=2))
    for z in [0, -pitch]:
        ax.plot([-t-2, 6], [z, z], color=MUTED, lw=.6, linestyle='--', zorder=2)


def prepare_motion_axes(g, side, poses, title, subtitle):
    p = g['parameters']
    bounds = np.vstack([transform(points, q) for q in poses for points in side])
    fig = plt.figure(figsize=(11.4, 7.2), facecolor=BG)
    fig.text(.05, .936, title, fontsize=23, weight='bold')
    fig.text(.05, .887, subtitle, fontsize=11, color=MUTED)
    ax = fig.add_axes([.075, .18, .59, .64], facecolor=BG)
    board(ax, p)
    ax.set_xlim(min(-p['board_thickness']-10, bounds[:, 0].min()-3), bounds[:, 0].max()+3)
    ax.set_ylim(min(-38, bounds[:, 1].min()-3), max(17, bounds[:, 1].max()+2))
    ax.set_aspect('equal')
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(color=GRID, lw=.5)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=8)
    ax.set_xlabel('Away from board [mm]', fontsize=9)
    ax.set_ylabel('Height above upper hole [mm]', fontsize=9)
    return fig, ax


def animation(g, side, upper, poses, out, provenance):
    sample = studio.evenly_sample_path(poses, 95)
    fig, ax = prepare_motion_axes(g, side, sample, 'Insert, seat, remove', 'Actual STEP center section following the continuously checked path')
    patches = []
    for points in side:
        patch = PatchPolygon(transform(points, sample[-1]), fc=BLUE, ec=INK, lw=1.1, zorder=4)
        ax.add_patch(patch)
        patches.append(patch)
    phase = fig.text(.715, .765, 'INSERT', fontsize=22, weight='bold', color=BLUE)
    stats = fig.text(.715, .710, '', fontsize=12, linespacing=1.8, va='top')
    fig.text(.715, .49, '120° nominal bearing arcs\n5 mm sharp flush lip\nFull-depth lower bearing', fontsize=11, linespacing=1.8, va='top', color=MUTED)
    inset = fig.add_axes([.75, .20, .13, .20])
    R = g['parameters']['hole_diameter']/2
    inset.add_patch(Circle((0, 0), R, fc=BG, ec=MUTED, lw=1.2))
    draw_sections(inset, upper, facecolor=PALE, edgecolor=BLUE, lw=1.2)
    inset.set(xlim=(-R-1, R+1), ylim=(-R-1, R+1), aspect='equal')
    inset.axis('off')
    fig.text(.715, .17, 'Bearing section when seated', fontsize=9, color=MUTED)
    fig.text(.05, .085, 'Center cutaway illustrates the movement. Separate evidence checks the full three-dimensional geometry.', fontsize=10, color=MUTED)
    fig.text(.05, .045, 'Ideal rigid geometry; final contact is permitted. Physical insertion force and printed fit remain untested.', fontsize=10, color=MUTED)
    seq = [('INSERT', q) for q in sample[::-1]]+[('SEATED', sample[0])]+[('REMOVE', q) for q in sample]+[('REMOVED', sample[-1])]
    durations = [55]*len(seq)
    durations[len(sample)] = 1400
    durations[-1] = 950
    frames, palette = [], None
    for name, q in seq:
        for patch, points in zip(patches, side):
            patch.set_xy(transform(points, q))
        phase.set_text(name)
        stats.set_text(f'Tilt  {q[2]:.2f}°\nOut  {q[0]-poses[0, 0]:.2f} mm\nUp  {q[1]-poses[0, 1]:.2f} mm')
        fig.canvas.draw()
        frame = Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[:, :, :3])
        if palette is None:
            palette = frame.quantize(colors=128)
        frames.append(frame.quantize(palette=palette, dither=Image.Dither.NONE))
    frames[0].save(out/'conformal-motion.gif', save_all=True, append_images=frames[1:], duration=durations,
                   loop=0, optimize=True, disposal=1, comment=json.dumps(provenance, sort_keys=True).encode())
    plt.close(fig)


def motion_envelope(g, side, poses, out, provenance):
    samples = studio.evenly_sample_path(poses, 161)
    sweep = unary_union([Polygon(transform(points, q)) for q in samples for points in side])
    fig, ax = prepare_motion_axes(g, side, samples, 'The installation movement', 'Actual STEP center section along the verified insertion and removal path')
    shapes = list(sweep.geoms) if hasattr(sweep, 'geoms') else [sweep]
    for shape in shapes:
        ax.add_patch(PatchPolygon(np.asarray(shape.exterior.coords), fc='#dcebe4', ec='#a4c2b2', lw=.8, zorder=1))
    for q in poses[1:-1:max(1, len(poses)//16)]:
        for points in side:
            ax.add_patch(PatchPolygon(transform(points, q), fill=False, ec='#91b4a5', lw=.65, zorder=3))
    for points in side:
        ax.add_patch(PatchPolygon(transform(points, poses[0]), fc=BLUE, ec=INK, lw=1.1, zorder=4))
    values = [('MAXIMUM TILT', f'{poses[:, 2].max():.3f}°'),
              ('LIFT FROM SEATED', f'{poses[:, 1].max()-poses[0, 1]:.2f} mm'),
              ('NOMINAL FLUSH LIP', '5.00 mm')]
    for i, (label, value) in enumerate(values):
        y = .75-i*.16
        fig.text(.715, y, label, fontsize=10, weight='bold', color=MUTED)
        fig.text(.715, y-.062, value, fontsize=24, weight='bold', color=BLUE)
    fig.text(.715, .23, 'Pale: sampled section sweep\nBlue: seated anchor\nLines: recorded waypoints', fontsize=10, color=MUTED, linespacing=1.7, va='top')
    fig.text(.05, .085, '161 interpolated section poses illustrate the continuous certified path. Full approach distance is shown.', fontsize=10, color=MUTED)
    fig.text(.05, .045, 'This is a center-section illustration. Use the separate allowed host volume for attached-part geometry.', fontsize=10, color=MUTED)
    savefig(fig, out/'conformal-motion-envelope', provenance)


def host_envelope(g, h, side, out, provenance):
    seat = g['seated_pose']
    shift = np.array([seat['y'], seat['z']])
    boundary = np.asarray(h['rear_boundary_design_yz_mm'])+shift
    fig = plt.figure(figsize=(12, 8), facecolor=BG)
    fig.text(.05, .935, 'A 5 mm lip. Room for a taller part.', fontsize=25, weight='bold')
    fig.text(.05, .885, 'Keep every point of the attached part inside the exported allowed host volume', fontsize=12, color=MUTED)
    ax = fig.add_axes([.075, .17, .46, .64], facecolor=BG)
    board(ax, g['parameters'], bottom=-35, top=105)
    ax.fill_betweenx(boundary[:, 1], boundary[:, 0], 50, color='#e2efe7')
    ax.plot(boundary[:, 0], boundary[:, 1], color=BLUE, lw=2)
    for points in side:
        ax.add_patch(PatchPolygon(points+shift, fc=BLUE, ec=INK, lw=.9))
    ax.plot(0, 5, 'o', color=ORANGE, ms=5)
    ax.annotate('5 mm sharp lip', xy=(0, 5), xytext=(18, -7), color=ORANGE, fontsize=10,
                arrowprops=dict(arrowstyle='-', color=ORANGE, lw=.8))
    ax.text(37, 50, 'Allowed\nattached part', ha='center', color=MUTED, fontsize=10)
    ax.set(xlim=(-13, 50), ylim=(-35, 105), aspect='equal')
    ax.set_xlabel('Setback from board [mm]', fontsize=10)
    ax.set_ylabel('Height above upper hole center [mm]', fontsize=10)
    ax.grid(color=GRID, lw=.5)
    ax.set_axisbelow(True)
    ax.spines[['top', 'right']].set_visible(False)
    fig.text(.59, .76, 'HEIGHT', fontsize=11, weight='bold', color=MUTED)
    fig.text(.94, .76, 'MINIMUM SETBACK', ha='right', fontsize=11, weight='bold', color=MUTED)
    for i, row in enumerate(h['nominal_setbacks_mm']):
        y = .7-i*.054
        fig.text(.59, y, f"{row['height_above_upper_hole_mm']:g} mm", fontsize=15)
        fig.text(.94, y, f"{row['minimum_installed_setback_mm']:.2f} mm", ha='right', fontsize=15, weight='bold', color=BLUE)
    fig.text(.59, .32, 'Import allowed_host_volume.step\ninto the same design coordinates.\nIntersect your host with that volume,\nthen fuse it to the anchor.', fontsize=12, color=MUTED, linespacing=1.7, va='top')
    fig.text(.05, .092, 'The curve includes the reserve that sets the nominal flush height to 5 mm. This is not a limit on total part height.', fontsize=10, color=MUTED)
    fig.text(.05, .05, 'Board-front clearance for this motion only; regenerate for larger export bounds or changed geometry.', fontsize=10, color=MUTED)
    savefig(fig, out/'conformal-host-envelope', provenance)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geometry', type=Path, default=ROOT/'cad/conformal/conformal_120_geometry.json')
    parser.add_argument('--step', type=Path, default=ROOT/'cad/conformal/conformal_120.step')
    parser.add_argument('--mesh', type=Path, default=ROOT/'cad/conformal/conformal_120_design_unsupported.stl')
    parser.add_argument('--motion', type=Path, default=ROOT/'cad/conformal/conformal_motion_results.json')
    parser.add_argument('--envelope', type=Path, default=ROOT/'cad/conformal/host-envelope/allowed_host_volume.json')
    parser.add_argument('--output', type=Path, default=ROOT/'visuals')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'text.color': INK, 'axes.labelcolor': MUTED,
                         'xtick.color': MUTED, 'ytick.color': MUTED, 'svg.fonttype': 'none'})
    g, m, h, side, upper, poses, provenance = checked_inputs(args.geometry, args.step, args.mesh, args.motion, args.envelope)
    hero(g, args.mesh, args.output, provenance)
    bearing(g, upper, args.output, provenance)
    animation(g, side, upper, poses, args.output, provenance)
    motion_envelope(g, side, poses, args.output, provenance)
    host_envelope(g, h, side, args.output, provenance)
    (args.output/'conformal-render-inputs.json').write_text(json.dumps(provenance, indent=2, sort_keys=True)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'output': str(args.output), 'sources': provenance}, indent=2))


if __name__ == '__main__':
    main()
