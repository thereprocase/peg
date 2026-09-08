#!/usr/bin/env python3
"""Recreate generic Cura geometry reviews; never send output to a printer."""
import argparse
import json
import os
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', type=Path, required=True)
    parser.add_argument('--definitions', type=Path, required=True)
    parser.add_argument('--package', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True, help='Scratch directory outside this package')
    parser.add_argument('--include-five-wall-trial', action='store_true')
    args = parser.parse_args()
    if args.output.resolve().is_relative_to(args.package.resolve()):
        parser.error('Use a scratch output directory outside the package; review GCode is not a printer profile.')
    args.output.mkdir(parents=True, exist_ok=True)
    report = json.loads((args.package / 'slicer_check.json').read_text())
    env = os.environ.copy()
    env['CURA_ENGINE_SEARCH_PATH'] = str(args.definitions.resolve())
    variants = [('side', 'anchor_default_3p94mm.stl', 'settings_flat_complete'),
                ('upright', 'anchor_upright_supported.stl', 'settings_upright_complete')]
    if args.include_five_wall_trial:
        variants.append(('upright_five_wall_trial', 'anchor_upright_supported.stl', 'settings_flat_complete'))
    for name, filename, settings_key in variants:
        command = [str(args.engine.resolve()), 'slice', '-m2', '-j', str(args.definitions / 'fdmprinter.def.json')]
        for key, value in report[settings_key].items():
            value = str(value).lower() if isinstance(value, bool) else str(value)
            command.extend(['-s', f'{key}={value}'])
        command.extend(['-e0', '-j', str(args.definitions / 'fdmextruder.def.json'),
                        '-s', 'machine_nozzle_size=0.4', '-s', 'material_diameter=1.75',
                        '-l', str(args.package / 'cad' / filename),
                        '-o', str(args.output / f'{name}_REVIEW_ONLY.gcode')])
        (args.output / f'{name}_command.json').write_text(json.dumps(command, indent=2))
        result = subprocess.run(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        (args.output / f'{name}.log').write_text(result.stdout)
        result.check_returncode()
        print(f'{name}: review written to {args.output}')


if __name__ == '__main__':
    main()
