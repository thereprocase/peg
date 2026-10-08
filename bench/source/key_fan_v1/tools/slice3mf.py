"""Slice the print-pose body with its solid-infill zones (modifier part at 100% infill) on the review profiles
(Bambu P1S 0.4, 0.20 mm, user ASA; same settings as quickslice.py). Writes <out>/hx04_solid.3mf (the project the
owner can open in Bambu Studio / Orca) and the sliced gcode 3MF, and prints weight, time and per-feature grams.
    python slice3mf.py <build dir> <out dir>
"""
import sys, json, re, subprocess, zipfile, importlib.util, os
from pathlib import Path
import numpy as np, trimesh
sp = importlib.util.spec_from_file_location('sl', Path(__file__).resolve().parents[2]/'canted_hex_keys_v2/slice_local.py')
S = importlib.util.module_from_spec(sp); sp.loader.exec_module(S)
d, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
body = trimesh.load(d/'print.stl', force='mesh'); zone = trimesh.load(d/'print_solid.stl', force='mesh')
machine = S.flatten(S.SYSTEM/'machine/Bambu Lab P1S 0.4 nozzle.json', 'machine')
process = S.flatten(S.SYSTEM/'process/0.20mm Standard @BBL X1C.json', 'process')
fil = S.flatten(S.USER_FILAMENT, 'filament')
scale = 1/(float(fil['filament_shrink'][0].strip('%'))/100)
shift = np.array([128, 140, 0])-np.array([*(body.bounds.mean(axis=0)[:2]*scale), body.bounds[0, 2]*scale])
for m in (body, zone):
    m.apply_scale(scale); m.apply_translation(shift)


def mesh_xml(m, oid):
    v = '\n'.join(f'<vertex x="{a:.5f}" y="{b:.5f}" z="{c:.5f}"/>' for a, b, c in m.vertices)
    t = '\n'.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in m.faces)
    return f'<object id="{oid}" type="model"><mesh><vertices>\n{v}\n</vertices><triangles>\n{t}\n</triangles></mesh></object>'


model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
         'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources>'
         + mesh_xml(body, 1)+mesh_xml(zone, 2)
         + '<object id="3" type="model"><components><component objectid="1"/><component objectid="2"/></components></object>'
         '</resources><build><item objectid="3"/></build></model>')
config = ('<?xml version="1.0" encoding="UTF-8"?>\n<config><object id="3"><metadata key="name" value="HX04 key fan"/>'
          '<metadata key="extruder" value="1"/>'
          '<part id="1" subtype="normal_part"><metadata key="name" value="body"/></part>'
          '<part id="2" subtype="modifier_part"><metadata key="name" value="solid zones (sockets, peg receiver)"/>'
          '<metadata key="sparse_infill_density" value="100%"/></part></object></config>')
ctypes = ('<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
rels = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
proj = out/'hx04_solid.3mf'
with zipfile.ZipFile(proj, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', ctypes); z.writestr('_rels/.rels', rels)
    z.writestr('3D/3dmodel.model', model); z.writestr('Metadata/model_settings.config', config)
fil.update(filament_settings_id=[fil['name']], filament_shrink=['100%']); machine.update(printer_settings_id=machine['name'])
process.update(print_settings_id=process['name'], brim_type='outer_only', brim_width='5', post_process=[], wall_loops='2', sparse_infill_density='20%',
               enable_support='1', support_type='tree(auto)', support_style='organic', support_on_build_plate_only='1', support_threshold_angle='45',
               support_remove_small_overhang='0', wall_generator='arachne', print_sequence='by layer', curr_bed_type='Textured PEI Plate')
for n, o in [('machine.json', machine), ('filament.json', fil), ('process.json', process)]:
    (out/n).write_text(json.dumps(o, indent=2))
r = subprocess.run([str(S.ORCA), '--datadir', str(out/'data'), '--load-settings', str(out/'machine.json')+';'+str(out/'process.json'),
                    '--load-filaments', str(out/'filament.json'), '--arrange', '0', '--orient', '0', '--slice', '0',
                    '--export-3mf', 'q.gcode.3mf', '--outputdir', str(out), str(proj)], capture_output=True, text=True, timeout=2400)
assert r.returncode == 0, r.stderr[-1500:]
with zipfile.ZipFile(out/'q.gcode.3mf') as z:
    code = z.read('Metadata/plate_1.gcode').decode('utf-8', 'replace')
g = {}; feat = 'x'
for line in code.splitlines():
    if line.startswith(';TYPE:') or line.startswith('; FEATURE:'):
        feat = line.split(':', 1)[1].strip(); continue
    if line.startswith(('G1', 'G2', 'G3')) and ' E' in line and ('X' in line or 'Y' in line):
        e = float(re.search(r' E([-\d.]+)', line).group(1))
        if e > 0:
            g[feat] = g.get(feat, 0)+e
dens = float(re.search(r'; filament_density: ([\d.]+)', code).group(1)); k = np.pi*(1.75/2)**2*dens/1000
print(re.search(r'; filament used \[g\] = (.+)', code).group(1), 'g;', re.search(r'total estimated time: ([^\n]+)', code).group(1))
for f, e in sorted(g.items(), key=lambda kv: -kv[1]):
    print(f'{f:26s}{e*k:7.1f} g')
