"""Render a dimensioned engineering review from the conformal STEP and contract.

This creates a technical drawing, not a motion qualification. Host setbacks
come from the separately identified path in host_envelope.json.
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
from matplotlib.patches import Arc, Circle, Polygon, Rectangle
import numpy as np

from host_envelope import required_setback


ROOT = Path(__file__).resolve().parent
INK = '#17333e'
MUTED = '#576b73'
BLUE = '#147792'
PALE = '#d5eaf0'
ORANGE = '#bd6020'
TAN = '#e5d8bd'
GRID = '#dce4e7'
BG = '#fbfcfc'


def section_polygons(shape, plane, origin, axes, shift):
    section = cq.Workplane(plane, origin=origin).newObject([shape]).section().val()
    paths = []
    for face in section.Faces():
        points, _ = face.outerWire().sample(0.001)
        xyz = np.array([p.toTuple() for p in points]) + np.asarray(shift)
        paths.append(xyz[:, axes])
    return paths


def draw_sections(ax, paths, offset=(0, 0), **kwargs):
    for points in paths:
        ax.add_patch(Polygon(points + np.asarray(offset), closed=True, **kwargs))


def dimension(ax, a, b, text, offset=(0, 0), rotation=0, size=10):
    ax.annotate('', xy=a, xytext=b,
                arrowprops=dict(arrowstyle='|-|', color=MUTED, lw=0.9))
    mid = (np.array(a)+np.array(b))/2 + np.array(offset)
    ax.text(*mid, text, ha='center', va='center', rotation=rotation,
            fontsize=size, color=MUTED,
            bbox=dict(facecolor=BG, edgecolor='none', pad=1.7))


def clean(ax):
    ax.set_aspect('equal')
    ax.axis('off')


def panel_title(fig, x, y, number, title, subtitle):
    fig.text(x, y, number, color=BLUE, fontsize=13, weight='bold')
    fig.text(x+0.025, y, title, fontsize=15, weight='bold')
    fig.text(x+0.025, y-0.023, subtitle, fontsize=10, color=MUTED)


def render(geometry_file, step_file, envelope_file, output, allowed_envelope=None):
    geometry_file, step_file, envelope_file, output = map(Path, (geometry_file, step_file, envelope_file, output))
    g = json.loads(geometry_file.read_text())
    h = json.loads(envelope_file.read_text())
    p, bearing = g['parameters'], g['conformal_bearing']
    seated = g['seated_pose']
    shift = np.array([0, seated['y'], seated['z']])
    R, r, t = p['hole_diameter']/2, p['peg_diameter']/2, p['board_thickness']
    shape = cq.importers.importStep(str(step_file)).val()
    section_y = -t/2-seated['y']
    transverse = section_polygons(shape, 'XZ', (0, section_y, 0), [0, 2], shift)
    upper = [points for points in transverse if points[:, 1].mean() > -p['pitch']/2]
    side = section_polygons(shape, 'YZ', (0, 0, 0), [1, 2], shift)
    motion_file = ROOT/h['motion_input']['file']
    if not motion_file.exists():
        candidates = list(ROOT.glob('cad/**/'+h['motion_input']['file']))
        if len(candidates) != 1:
            raise ValueError('Cannot resolve the host envelope motion input')
        motion_file = candidates[0]
    motion_raw = motion_file.read_bytes()
    if hashlib.sha256(motion_raw).hexdigest() != h['motion_input']['sha256']:
        raise ValueError('Host envelope report no longer matches its motion input')
    motion = json.loads(motion_raw)
    poses = motion['removal_poses']
    source_hashes = {Path(k.replace('\\', '/')).as_posix(): v
                     for k, v in motion.get('source_sha256', {}).items()}
    for source in (geometry_file, step_file):
        if source_hashes.get(source.resolve().relative_to(ROOT).as_posix()) != hashlib.sha256(source.read_bytes()).hexdigest():
            raise ValueError(f'Motion certificate is stale for {source.name}')
    motion_checked = (motion.get('verification', {}).get('passed') is True
                      and motion.get('geometry_contract') == g)
    allowed = None
    if allowed_envelope is not None:
        allowed_envelope = Path(allowed_envelope)
        allowed = json.loads(allowed_envelope.read_text())
        if allowed.get('source_motion_sha256') != hashlib.sha256(motion_raw).hexdigest():
            raise ValueError('Allowed volume no longer matches the displayed motion input')
        if allowed.get('continuous_host_certificate', {}).get('passed') is not True:
            raise ValueError('Allowed volume requires a passed continuous host certificate')

    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'text.color': INK, 'axes.labelcolor': MUTED,
                         'xtick.color': MUTED, 'ytick.color': MUTED,
                         'svg.fonttype': 'none'})
    fig = plt.figure(figsize=(16, 11.6), facecolor=BG)
    fig.text(.04, .957, f"{bearing['angle_deg']:g}° conformal peg — engineering review", fontsize=25, weight='bold')
    fig.text(.04, .928, 'Actual STEP sections and dimensioned geometry  •  All dimensions in millimeters', fontsize=12, color=MUTED)
    fig.text(.96, .955, 'PROTOTYPE', ha='right', fontsize=12, weight='bold', color=ORANGE)
    fig.text(.96, .933, 'Motion continuously checked' if motion_checked else 'Motion not qualified',
             ha='right', fontsize=11, color=BLUE if motion_checked else ORANGE)
    fig.add_artist(plt.Line2D([.04, .96], [.91, .91], transform=fig.transFigure, color=GRID))

    panel_title(fig, .04, .88, '01', 'Match the lower bore curve', 'Transverse section through the bearing land; seated position')
    ax = fig.add_axes([.06, .574, .40, .275])
    old_x, new_x = -4.4, 4.4
    for x in [old_x, new_x]:
        ax.add_patch(Circle((x, 0), R, fill=False, ec=MUTED, lw=1.3, linestyle=(0, (3, 3))))
        ax.plot(x, 0, '+', color=MUTED, ms=7, mew=.8)
    ax.add_patch(Circle((old_x, -(R-r)), r, facecolor='#e3e8eb', edgecolor=MUTED, lw=1.2))
    ax.plot(old_x, -R, 'o', color=ORANGE, ms=5)
    draw_sections(ax, upper, (new_x, 0), facecolor=PALE, edgecolor=BLUE, lw=1.2)
    half = math.radians(bearing['angle_deg']/2)
    angles = np.linspace(-half, half, 401)
    arc_x, arc_z = R*np.sin(angles), -R*np.cos(angles)
    ax.plot(new_x+arc_x, arc_z, color=ORANGE, lw=3.4, solid_capstyle='round')
    for phi in [-half, half]:
        ax.plot([new_x, new_x+R*math.sin(phi)], [0, -R*math.cos(phi)], color=ORANGE, lw=.8, linestyle=':')
    ax.add_patch(Arc((new_x, 0), 2.65, 2.65, theta1=-90-bearing['angle_deg']/2,
                     theta2=-90+bearing['angle_deg']/2, edgecolor=ORANGE, lw=1.0))
    ax.text(new_x, -.89, f"{bearing['angle_deg']:g}°", color=ORANGE, ha='center', fontsize=13, weight='bold')
    ax.text(old_x, R+.48, f"Circular Ø{p['peg_diameter']:.2f}", ha='center', weight='bold', fontsize=12)
    ax.text(new_x, R+.48, f"Conformal R{R:.3f} bearing arc", ha='center', weight='bold', fontsize=12)
    ax.text(old_x, -R-.63, 'Nominal tangent contact', ha='center', fontsize=10, color=MUTED)
    ax.text(new_x, -R-.63, 'Nominal zero gap across the arc', ha='center', fontsize=10, color=ORANGE)
    dimension(ax, (new_x+arc_x[0], -R-1.07), (new_x+arc_x[-1], -R-1.07),
              f"{bearing['arc_width_mm']:.3f} chord width")
    ax.set_xlim(-8.35, 8.35); ax.set_ylim(-4.65, 4.35); clean(ax)
    fig.text(.065, .555, f"Hole Ø{p['hole_diameter']:.2f}  •  Round upper core retained  •  Tongue Ø{p['tongue_diameter']:.2f}", color=MUTED, fontsize=10)

    panel_title(fig, .53, .88, '02', 'Lower peg reaches the full board thickness', 'Center section from the STEP; board front at Y = 0')
    ax = fig.add_axes([.55, .593, .40, .255])
    zc = -p['pitch']
    ax.add_patch(Rectangle((-t, zc-5), t, 5-R, facecolor=TAN, edgecolor='#b6a781', hatch='///', lw=.6))
    ax.add_patch(Rectangle((-t, zc+R), t, 2, facecolor=TAN, edgecolor='#b6a781', hatch='///', lw=.6))
    draw_sections(ax, side, facecolor=PALE, edgecolor=BLUE, lw=1.3)
    ax.plot([-t, 0], [zc-R, zc-R], color=ORANGE, lw=3)
    for yy in [-t, 0]:
        ax.plot([yy, yy], [zc-R-.08, zc-R-1.05], color=MUTED, lw=.65)
    dimension(ax, (-t, zc-R-.83), (0, zc-R-.83), f"{t:.2f} full bearing land")
    lead = p['locator_chamfer']
    dimension(ax, (-t-lead, zc+R+.48), (-t, zc+R+.48), f"{lead:.2f}", offset=(-.28, .34), size=10)
    ax.annotate('Rear lead-in', xy=(-t-lead*.52, zc-R+lead*.52), xytext=(-t-1.1, zc-.8),
                ha='right', color=MUTED, fontsize=10, arrowprops=dict(arrowstyle='-', color=MUTED, lw=.8))
    ax.annotate('Board-facing\nflat', xy=(0, zc+2.7), xytext=(1.25, zc+4.4),
                ha='center', color=MUTED, fontsize=10, arrowprops=dict(arrowstyle='-', color=MUTED, lw=.8))
    ax.text(-t/2, zc+R+.36, 'BOARD', fontsize=10, weight='bold', ha='center', color=MUTED)
    ax.text(-t-1.4, zc+1.7, 'rear', fontsize=10, color=MUTED)
    ax.text(2.4, zc+1.7, 'front', fontsize=10, color=MUTED)
    ax.set_xlim(-t-2.6, 4.1); ax.set_ylim(zc-4.35, zc+5.15); clean(ax)
    fig.text(.555, .555, f"Full curve to the rear face, then a {lead:.2f} lead-in beyond the board.", color=MUTED, fontsize=10)

    fig.add_artist(plt.Line2D([.04, .96], [.53, .53], transform=fig.transFigure, color=GRID))
    panel_title(fig, .04, .495, '03', 'A sharp 5 mm lip against the board',
                'Actual STEP center section; taller attached parts follow the envelope')
    ax = fig.add_axes([.068, .18, .365, .26])
    lip = g['host_interface']['nominal_flush_lip_height_above_upper_hole_mm']
    ax.add_patch(Rectangle((-t, R), t, 14-R, facecolor=TAN,
                           edgecolor='#b6a781', hatch='///', lw=.7))
    if allowed:
        boundary = np.asarray(allowed['rear_boundary_design_yz_mm'], dtype=float) + seated['y'] * np.array([1, 0]) + seated['z'] * np.array([0, 1])
        ax.fill_betweenx(boundary[:, 1], boundary[:, 0], 10, color='#edf5f1')
        ax.plot(boundary[:, 0], boundary[:, 1], color='#77a18c', lw=1.2)
    draw_sections(ax, side, facecolor=PALE, edgecolor=BLUE, lw=1.4)
    ax.plot([-t-1, 8.5], [0, 0], color=MUTED, lw=.6, linestyle='--')
    dimension(ax, (6.5, 0), (6.5, lip), f'{lip:.2f} nominal lip',
              offset=(1.05, 0), rotation=90, size=10)
    ax.plot([0, 0, .8], [lip-.8, lip, lip], color=ORANGE, lw=2.6)
    ax.annotate('Sharp corner', xy=(0, lip), xytext=(-t-.7, 8.7),
                color=ORANGE, fontsize=10, ha='left',
                arrowprops=dict(arrowstyle='-', color=ORANGE, lw=.8))
    ax.text(5.6, 12, 'Allowable\nattached part', ha='center', fontsize=10, color=MUTED)
    ax.text(-t/2, 11.9, 'BOARD', ha='center', fontsize=9, color=MUTED, rotation=90)
    ax.text(1, -.9, 'Upper hole center', fontsize=9, color=MUTED)
    ax.set_xlim(-t-2.2, 9.5); ax.set_ylim(-1.5, 14); clean(ax)
    fig.text(.065, .133, 'Flat board contact to 5 mm above the upper hole center.', fontsize=10, color=MUTED)
    fig.text(.065, .113, 'Zero corner radius in CAD; higher material stays within the envelope.', fontsize=10, color=MUTED)

    envelope_caption = ('Conformal motion; exported nominal envelope' if allowed else
                        'Conformal motion; exact geometric boundary') if motion_checked else (
                        'Supplied motion envelope; candidate compatibility unverified')
    panel_title(fig, .53, .495, '04', 'Fill the allowable envelope with the attached part', envelope_caption)
    ax = fig.add_axes([.575, .20, .225, .24])
    if allowed:
        rear_boundary = np.asarray(allowed['rear_boundary_design_yz_mm'], dtype=float)
        heights = rear_boundary[:, 1] + seated['z']
        setbacks = rear_boundary[:, 0] + seated['y']
        graph_height = min(105, allowed['export_clip']['maximum_installed_height_mm'])
    else:
        heights = np.linspace(0, 105, 421)
        setbacks = [max(0, required_setback(poses, v)['required_installed_setback_mm']) for v in heights]
        graph_height = 105
    ax.fill_betweenx(heights, setbacks, 42, color='#edf5f1')
    ax.plot(setbacks, heights, color=BLUE, lw=2.1)
    ax.axvline(0, color=MUTED, lw=1.2)
    ax.set_xlim(-1, 40); ax.set_ylim(0, graph_height)
    ax.set_xlabel('Setback from board', fontsize=10, labelpad=7)
    ax.set_ylabel('Height above upper hole', fontsize=10, labelpad=7)
    ax.set_xticks([0, 10, 20, 30, 40]); ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.tick_params(labelsize=9, length=3)
    ax.grid(color=GRID, lw=.6); ax.set_axisbelow(True)
    for spine in ax.spines.values(): spine.set_color(GRID)
    ax.text(26, 45, 'fill with host\ngeometry', ha='center', fontsize=10, color=MUTED)
    cap = (allowed['nominal_flush_lip_height_above_upper_hole_mm'] if allowed else
           h['flush_front_height_limit']['maximum_physical_height_above_upper_hole_mm'])
    ax.plot(0, cap, 'o', color=ORANGE, ms=4)
    cap_label = 'Nominal lip' if allowed else 'Flush limit'
    ax.annotate(f'{cap_label} {cap:.2f}', xy=(0, cap), xytext=(11, 15), fontsize=9, color=ORANGE,
                arrowprops=dict(arrowstyle='-', lw=.8, color=ORANGE))
    rows = ([{'physical_height_above_upper_hole_mm': row['height_above_upper_hole_mm'],
              'required_installed_setback_mm': row['minimum_installed_setback_mm']}
             for row in allowed['nominal_setbacks_mm']] if allowed else h['example_setbacks'])
    tx = .825
    fig.text(tx, .425, 'Height', fontsize=10, color=MUTED)
    fig.text(.942, .425, 'Setback', fontsize=10, color=MUTED, ha='right')
    for i, row in enumerate(rows):
        ytext = .390-(.031 if len(rows) > 5 else .037)*i
        fig.text(tx, ytext, f"{row['physical_height_above_upper_hole_mm']:g}", fontsize=12)
        fig.text(.942, ytext, f"{row['required_installed_setback_mm']:.2f}", fontsize=12, ha='right', weight='bold')
    fig.text(.824, .18, 'Exported nominal\nenvelope; includes\nheight reserve.' if allowed else
             'Continuous path\nminimums; equality\npermits contact.', fontsize=9, color=MUTED, linespacing=1.5)
    lip_height = (allowed['nominal_flush_lip_height_above_upper_hole_mm'] if allowed else
                  h['proposed_sharp_host']['top_physical_height_above_upper_hole_mm'])
    fig.text(.555, .133, f'A {lip_height:.2f} nominal lip above the hole; keep all higher material in the envelope.', fontsize=10, color=MUTED)
    fig.text(.555, .113, 'Keep added material inside the CAD envelope for this motion.' if motion_checked else
             "These limits do not establish the modified anchor's installation path.",
             fontsize=10, color=MUTED if motion_checked else ORANGE)

    fig.add_artist(plt.Line2D([.04, .96], [.086, .086], transform=fig.transFigure, color=GRID))
    fig.text(.04, .063, 'Prototype CAD review. Nominal arc contact depends on the measured bore and printed surface.', fontsize=10, color=MUTED)
    fig.text(.04, .043, 'Printing, support removal, physical fit and load capacity remain untested.' if motion_checked else
             'Continuous motion, printing, support removal and physical fit checks remain necessary.',
             fontsize=10, color=MUTED)
    fig.text(.96, .057, f"STEP {hashlib.sha256(step_file.read_bytes()).hexdigest()[:12]}\nHost path {h['motion_input']['name']}", ha='right', fontsize=8.5, color=MUTED)
    output.parent.mkdir(parents=True, exist_ok=True)
    sources = [geometry_file, step_file, envelope_file, motion_file]
    if allowed_envelope is not None:
        sources.append(allowed_envelope)
    provenance = json.dumps({f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sources})
    fig.savefig(output.with_suffix('.png'), dpi=190, facecolor=BG, metadata={'Description': provenance})
    fig.savefig(output.with_suffix('.svg'), facecolor=BG, metadata={'Description': provenance})
    svg_path=output.with_suffix('.svg')
    svg_path.write_text('\n'.join(line.rstrip() for line in svg_path.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8', newline='\n')
    plt.close(fig)
    return {'png': str(output.with_suffix('.png')), 'svg': str(output.with_suffix('.svg'))}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geometry', type=Path, default=ROOT/'cad/conformal/conformal_120_geometry.json')
    parser.add_argument('--step', type=Path, default=ROOT/'cad/conformal/conformal_120.step')
    parser.add_argument('--envelope', type=Path, default=ROOT/'cad/conformal/host_envelope.json')
    parser.add_argument('--allowed-envelope', type=Path,
                        default=ROOT/'cad/conformal/host-envelope/allowed_host_volume.json',
                        help='Optional allowed_host_volume.json; plot its exported nominal boundary and table')
    parser.add_argument('--output', type=Path, default=ROOT/'visuals/conformal-design-review')
    args = parser.parse_args()
    print(json.dumps(render(args.geometry, args.step, args.envelope, args.output,
                            args.allowed_envelope), indent=2))
