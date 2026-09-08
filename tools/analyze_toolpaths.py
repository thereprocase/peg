#!/usr/bin/env python3
"""Reproduce deposited-envelope and bridge-path evidence from generic Cura GCode.

Adapted from the September 2026 scratch scripts analyze_gcode.py and
final_review.py. Preserves their line-envelope method and default inspection
layers; exposes every machine-specific assumption through CLI options.
This analyzes files only and never contacts a printer.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import statistics

from shapely.geometry import LineString
from shapely.ops import unary_union


def parse(path, layer_height=.2, filament_diameter=1.75, xy_offset=128):
    xyz = [0., 0., 0.]
    extrusion = 0.
    layer = -1
    feature = ''
    layers = {}
    for raw in Path(path).read_text().splitlines():
        if raw.startswith(';LAYER:'):
            layer = int(raw.split(':')[1])
            layers[layer] = []
        if raw.startswith(';TYPE:'):
            feature = raw.split(':')[1]
        line = raw.split(';')[0].strip()
        if line in ('M83', 'G91'):
            raise ValueError('This review requires absolute extrusion and XYZ coordinates.')
        if line.startswith('G92 E'):
            extrusion = float(line[5:].split()[0])
        if not re.match(r'G[01] ', line):
            continue
        values = {k: float(v) for k, v in re.findall(r'([XYZEF])([-+\d\.]+)', line)}
        old = xyz.copy()
        next_extrusion = values.get('E', extrusion)
        xyz = [values.get(k, xyz[i]) for i, k in enumerate('XYZ')]
        length = math.hypot(xyz[0] - old[0], xyz[1] - old[1])
        delta = next_extrusion - extrusion
        extrusion = next_extrusion
        if layer >= 0 and delta > 0 and length > 1e-5:
            width = delta * math.pi * (filament_diameter / 2) ** 2 / length / layer_height
            layers[layer].append(dict(p=[v - xy_offset for v in old[:2]],
                                      q=[v - xy_offset for v in xyz[:2]],
                                      z=xyz[2], type=feature, width=width, length=length))
    return layers


def deposition_check(layers, reach=.2):
    """Catch whole components detached from the prior layer, not all overhangs."""
    previous = None
    floaters = []
    first_components = None
    for index, segments in layers.items():
        beads = [LineString([s['p'], s['q']]).buffer(s['width'] / 2, cap_style=1)
                 for s in segments if s['type'] != 'SKIRT' and .1 < s['width'] < 1]
        shape = unary_union(beads).buffer(.01).buffer(-.01)
        components = list(shape.geoms) if hasattr(shape, 'geoms') else [shape]
        if first_components is None:
            first_components = len(components)
        if previous is not None and not shape.is_empty:
            prior = previous.buffer(reach)
            for component in components:
                if component.area > .01 and not component.intersects(prior):
                    floaters.append(dict(layer=index, area_mm2=component.area))
        previous = shape
    return dict(layers=len(layers), first_layer_components=first_components,
                wholly_detached_components=floaters)


def web_samples(layers):
    # These bands and inspection layers refer to the shipped default geometry.
    records = []
    for index in [8, 10, 12, 115, 120, 125, 130]:
        segments = layers.get(index, [])
        paths = [s for s in segments
                 if abs(s['p'][0] - s['q'][0]) < .03
                 and abs(s['p'][1] - s['q'][1]) > .15
                 and (s['p'][0] < .75 or s['p'][0] > 3.25)
                 and min(s['p'][1], s['q'][1]) < 9.4]
        records.append(dict(layer=index, z=segments[0]['z'] if segments else None,
                            web_paths=paths))
    return records


def roof_samples(layers):
    result = []
    for index in [15, 140]:
        segments = layers.get(index, [])
        skin = [s for s in segments if s['type'] == 'SKIN']
        result.append(dict(layer=index, z=segments[0]['z'] if segments else None,
                           skin_paths=skin,
                           all_skin_along_x=bool(skin) and all(abs(s['p'][1] - s['q'][1]) < .01 for s in skin)))
    return result


def render(layers, filename):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 4, figsize=(13, 7), layout='constrained')
    for ax, index, label in zip(axes, [8, 15, 120, 140],
                               ['Lower webs', 'Lower first roof', 'Upper webs', 'Upper first roof']):
        segments = layers.get(index, [])
        for s in segments:
            if s['type'] == 'SKIRT':
                continue
            color = {'WALL-OUTER': '#087f8c', 'WALL-INNER': '#999fa4',
                     'SKIN': '#e95a20', 'FILL': '#c6ced3'}.get(s['type'], 'gray')
            ax.plot(*zip(s['p'], s['q']), color=color, lw=max(1, 4 * s['width']), solid_capstyle='round')
        height = segments[0]['z'] if segments else float('nan')
        ax.set_title(f'{label}\nZ {height:.1f} mm', fontsize=12)
        ax.set_aspect('equal')
        ax.set_xlim(-.4, 4.4)
        ax.set_ylim(-.4, 14.4)
        ax.set_xlabel('X, mm')
        ax.grid(alpha=.15)
    axes[0].set_ylabel('Y, mm, STL coordinates')
    fig.suptitle('Generic Cura toolpath review · web and roof inspection layers', fontsize=13)
    fig.savefig(filename, dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--side', type=Path, required=True)
    parser.add_argument('--upright', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--layer-height', type=float, default=.2)
    parser.add_argument('--filament-diameter', type=float, default=1.75)
    parser.add_argument('--xy-offset', type=float, default=128.)
    parser.add_argument('--reach', type=float, default=.2)
    parser.add_argument('--no-plot', action='store_true')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    parsed = {name: parse(path, args.layer_height, args.filament_diameter, args.xy_offset)
              for name, path in [('side', args.side), ('upright', args.upright)]}
    samples = web_samples(parsed['upright'])
    widths = [p['width'] for s in samples for p in s['web_paths']]
    result = dict(parameters={k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()},
                  inputs={name: hashlib.sha256(path.read_bytes()).hexdigest()
                          for name, path in [('side_gcode_sha256', args.side), ('upright_gcode_sha256', args.upright)]},
                  deposition={k: deposition_check(v, args.reach) for k, v in parsed.items()},
                  web_samples=samples, web_sample_median_width_mm=statistics.median(widths) if widths else None,
                  roof_samples=roof_samples(parsed['upright']),
                  physical_print_tested=False,
                  scope='Whole-component overlap only; does not establish support for every connected path segment, bridge sag, bond strength, machine suitability, or load rating.')
    (args.output / 'toolpath_reconstructed.json').write_text(json.dumps(result, indent=2))
    if not args.no_plot:
        render(parsed['upright'], args.output / 'upright_actual_toolpaths.png')
    print(json.dumps(dict(deposition=result['deposition'], web_sample_median_width_mm=result['web_sample_median_width_mm']), indent=2))


if __name__ == '__main__':
    main()
