"""Quick review slice of an arbitrary print-pose STL with the same profiles as slice_local.py."""
import sys, json, re, subprocess, zipfile, importlib.util
from pathlib import Path
import numpy as np, trimesh
sp = importlib.util.spec_from_file_location('sl', Path(__file__).resolve().parents[2]/'canted_hex_keys_v2/slice_local.py')
S = importlib.util.module_from_spec(sp); sp.loader.exec_module(S)
src, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
m = trimesh.load(src, force='mesh')
machine = S.flatten(S.SYSTEM/'machine/Bambu Lab P1S 0.4 nozzle.json', 'machine')
process = S.flatten(S.SYSTEM/'process/0.20mm Standard @BBL X1C.json', 'process')
fil = S.flatten(S.USER_FILAMENT, 'filament')
scale = 1/(float(fil['filament_shrink'][0].strip('%'))/100); m.apply_scale(scale)
m.apply_translation(np.array([128, 140, 0])-np.array([*m.bounds.mean(axis=0)[:2], m.bounds[0, 2]])); m.export(out/'plate.stl')
fil.update(filament_settings_id=[fil['name']], filament_shrink=['100%']); machine.update(printer_settings_id=machine['name'])
process.update(print_settings_id=process['name'], brim_type='outer_only', brim_width='5', post_process=[], wall_loops='2', sparse_infill_density='20%',
               enable_support='1', support_type='tree(auto)', support_style='organic', support_on_build_plate_only='1', support_threshold_angle=__import__('os').environ.get('STA','45'),
               support_remove_small_overhang=__import__('os').environ.get('RSO','0'), wall_generator='arachne', print_sequence='by layer', curr_bed_type='Textured PEI Plate')
for n, o in [('machine.json', machine), ('filament.json', fil), ('process.json', process)]:
    (out/n).write_text(json.dumps(o, indent=2))
r = subprocess.run([str(S.ORCA), '--datadir', str(out/'data'), '--load-settings', str(out/'machine.json')+';'+str(out/'process.json'),
                    '--load-filaments', str(out/'filament.json'), '--arrange', '0', '--orient', '0', '--slice', '0',
                    '--export-3mf', 'q.gcode.3mf', '--outputdir', str(out), str(out/'plate.stl')], capture_output=True, text=True, timeout=1800)
assert r.returncode == 0, r.stderr[-1500:]
with zipfile.ZipFile(out/'q.gcode.3mf') as z: code = z.read('Metadata/plate_1.gcode').decode('utf-8', 'replace')
g = {}; feat = 'x'; E = 0.
for line in code.splitlines():
    if line.startswith(';TYPE:') or line.startswith('; FEATURE:'): feat = line.split(':', 1)[1].strip(); continue
    if line.startswith(('G1','G2','G3')) and ' E' in line and ('X' in line or 'Y' in line):
        e = float(re.search(r' E([-\d.]+)', line).group(1))
        if e > 0: g[feat] = g.get(feat, 0)+e
dens = float(re.search(r'; filament_density: ([\d.]+)', code).group(1)); k = np.pi*(1.75/2)**2*dens/1000
print(re.search(r'; filament used \[g\] = (.+)', code).group(1), 'g;', re.search(r'total estimated time: ([^\n]+)', code).group(1))
for f, e in sorted(g.items(), key=lambda kv: -kv[1]): print(f'{f:26s}{e*k:7.1f} g')
