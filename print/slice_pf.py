"""Slice a PF ladder plate for the P1S, 0.4 nozzle, PETG in physical slot 1. Run with FreeCAD's Python."""
from pathlib import Path
import json, subprocess, zipfile, re, sys
import FreeCAD, Mesh
HERE = Path(__file__).resolve().parent
PLATES = {
    'pf01': ('slice', 'fit-ladder/part-pf01-peg-fit-ladder__v1', 'PF01-v1-peg-fit-ladder-PETG'),
    'pf02': ('slice-pf02', 'fit-ladder-v2/part-pf02-peg-fit-grid__v1', 'PF02-v1-peg-fit-grid-PETG'),
    'pf03': ('slice-pf03', 'fit-ladder-v3/part-pf03-peg-fit-final__v1', 'PF03-v1-peg-fit-final-PETG'),
    'pf04': ('slice-pf04', 'fit-ladder-v4/part-pf04-peg-retention-concepts__v1', 'PF04-v1-retention-concepts-PETG'),
    'pf04r2': ('slice-pf04r2', 'fit-ladder-v4/part-pf04-peg-retention-concepts__v1', 'PF04-v1-retention-concepts-PETG-r2'),
    'pf05': ('slice-pf05', 'fit-ladder-v5/part-pf05-peg-latch-grid__v1', 'PF05-v1-latch-grid-PETG'),
    'pf05m': ('slice-pf05m', 'fit-ladder-v5/part-pf05-peg-latch-grid__v1', 'PF05-v1-latch-grid-PETG-msup'),
    'pf06m': ('slice-pf06m', 'fit-ladder-v6/part-pf06-peg-latch-tune__v1', 'PF06-v1-latch-tune-PETG-msup'),
    'tw09m': ('slice-tw09m', '../../bench/reviews/v9-build/TW09-PF06-plate.stl', 'TW09-PF06-tweezer-v9-plus-latch-tune-PETG'),
    'tw09b': ('slice-tw09b', '../../bench/reviews/v9-build-gap01/TW09-PF06-plate-gap01.stl', 'TW09-PF06-tweezer-v9-plus-latch-tune-PETG-z01'),
    'pf06a': ('slice-pf06a', 'fit-ladder-v6/part-pf06-peg-latch-tune__v1__all-6__print-flat-top__fit-e586ab4ff6.stl', 'PF06-v1-latch-tune-ASA-cyan-organic'),
    'pf07a': ('slice-pf07a', 'fit-ladder-v7/part-pf07-peg-hoop-tune__v1__all-6__print-flat-top__fit-e586ab4ff6.stl', 'PF07-v1-hoop-tune-ASA-cyan-organic'),
    'pf03box': ('slice-pf03box', ['fit-ladder-v3/part-pf03-peg-fit-final__v1', 'box-2w/part-bx01-box-2w__v1'], 'PF03-BX01-v1-fit-and-box-PETG'),
}
WHICH = sys.argv[1] if len(sys.argv) > 1 else 'pf01'
folder, stem, JOB = PLATES[WHICH]
OUT = HERE/folder; OUT.mkdir(exist_ok=True)
GALLERY = HERE.parent/'docs/gallery'
# 'a' plates (user, 2026-10-02): cyan PolyLite ASA in AMS slot 4, Orca's generated organic
# supports, and every coupon its own object so Skip Objects can drop one mid-print.
ASA = WHICH.endswith('a')
MODELLED = WHICH.endswith('m') or WHICH in ('tw09b',)   # plate carries print_supports.py supports; slicer supports off
KIND = 'print-flat-top-modelled-supports' if MODELLED else 'print-flat-top'
SRCS = ([(GALLERY/stem).resolve()] if isinstance(stem, str) and stem.endswith('.stl') else   # prebuilt plate
        [max(GALLERY.glob(f'{st}__*{KIND}__fit-e586ab4ff6.stl'), key=lambda f: f.stat().st_mtime)   # newest plate
         for st in ([stem] if isinstance(stem, str) else stem)])
print('plate', [s.name for s in SRCS])
POLY = Path(r'C:\Users\repro\AppData\Roaming\OrcaSlicer\user\fecf5a7e-f2b8-486d-a7dc-191d79a5d5cb\filament\Polylite PETG.json')
NOZZLE_C = '240'   # PolyLite PETG label ceiling

m, x = Mesh.Mesh(), 0.0
for src in SRCS:   # side by side along X, 10 mm apart, all on the bed
    part = Mesh.Mesh(str(src)); b = part.BoundBox
    part.translate(x-b.XMin, -(b.YMin+b.YMax)/2, -b.ZMin); m.addMesh(part); x += b.XLength+10
b = m.BoundBox
m.translate(128-(b.XMin+b.XMax)/2, 128-(b.YMin+b.YMax)/2, -b.ZMin)
assert m.BoundBox.XMin > 5 and m.BoundBox.XMax < 251 and m.BoundBox.YMin > 5 and m.BoundBox.YMax < 251
if ASA:   # the user's calibrated preset shrinks 99.46 % in X/Y; the CLI ignores filament_shrink, so bake it
    k = 100/99.46; c = FreeCAD.Vector(128, 128, 0)
    mat = FreeCAD.Matrix(); mat.move(-c); mat.scale(k, k, 1); mat.move(c); m.transform(mat)
m.write(str(OUT/f'{JOB}.stl'))
PARTS = []
if ASA:   # one object per coupon: union-find connected components whose bounding boxes touch
    comps = m.getSeparateComponents()
    boxes = [cm.BoundBox for cm in comps]; root = list(range(len(comps)))
    def find(i):
        while root[i] != i: i = root[i]
        return i
    for i in range(len(comps)):
        for j in range(i):
            a, b2 = boxes[i], boxes[j]
            if a.XMin <= b2.XMax+1 and b2.XMin <= a.XMax+1 and a.YMin <= b2.YMax+1 and b2.YMin <= a.YMax+1:
                root[find(i)] = find(j)
    groups = {}
    for i, cm in enumerate(comps): groups.setdefault(find(i), Mesh.Mesh()).addMesh(cm)
    for n, g in enumerate(sorted(groups.values(), key=lambda g: (round(g.BoundBox.YMin), g.BoundBox.XMin)), 1):
        f = OUT/f'{JOB}__part{n}.stl'; g.write(str(f)); PARTS.append(f)
        print('part', n, [round(v, 1) for v in (g.BoundBox.XMin, g.BoundBox.YMin, g.BoundBox.XMax, g.BoundBox.YMax, g.BoundBox.ZMax)])

proc = json.loads((HERE/'profiles/process.json').read_text())
# PF04 failed at 22.2 mm (layer 189/284) when something fell: the 22-29 mm
# tree_slim trunks (2 mm branches) under the lower-peg tails are the only
# tall, thin things at that height. From PF05 on, use rigid snug grid columns.
STURDY = WHICH not in ('pf01', 'pf02', 'pf03', 'pf03box', 'pf04')
proc.update({'brim_type': 'outer_only', 'brim_width': '5', 'wall_loops': '3', 'post_process': []})
proc.update({'support_type': 'normal(auto)', 'support_style': 'snug', 'support_base_pattern': 'rectilinear',
             'support_base_pattern_spacing': '2', 'support_on_build_plate_only': '1'} if STURDY
            else {'support_type': 'tree(auto)'})
if MODELLED:
    proc.update({'enable_support': '0'})
if ASA:
    proc.update({'enable_support': '1', 'support_type': 'tree(auto)', 'support_style': 'organic',
                 'support_on_build_plate_only': '1'})
if WHICH.startswith('pf07'):   # thin hoop arms: Arachne prints 0.6-0.8 mm walls solid (classic split them)
    proc.update({'wall_generator': 'arachne'})
if STURDY:   # user, 2026-10-01: 2 walls, 20% infill, 40% exhaust fan
    proc.update({'wall_loops': '2', 'sparse_infill_density': '20%'})
(OUT/'process.json').write_text(json.dumps(proc, indent=1))
if ASA:   # resolve_filament.py: 'Repro - ASA - Polymaker PolyLite - Calibrated' over its system chain
    fil = json.loads((HERE/'profiles/filament-asa-polylite-calibrated.json').read_text())
    fil.update({'filament_settings_id': [fil['name']], 'filament_colour': ['#76D9F4'],
                'filament_shrink': ['100%', '100%']})   # shrink is baked into the mesh above
else:
    fil = json.loads((HERE/'profiles/filament.json').read_text())
    fil.update({k: v for k, v in json.loads(POLY.read_text()).items() if k not in ('inherits', 'name')})
    fil.update({'filament_settings_id': ['Polylite PETG'], 'name': 'Polylite PETG',
                'nozzle_temperature': [NOZZLE_C], 'nozzle_temperature_initial_layer': [NOZZLE_C],
                'filament_colour': ['#161616']})
if STURDY and not ASA:   # PETG plates; the ASA preset keeps its own exhaust setting
    fil['during_print_exhaust_fan_speed'] = ['40']
(OUT/'filament.json').write_text(json.dumps(fil, indent=1))
cmd = [r'C:\Program Files\OrcaSlicer\orca-slicer.exe', '--datadir', str(OUT/'data'),
       '--load-settings', str(HERE/'profiles/machine.json')+';'+str(OUT/'process.json'),
       '--load-filaments', str(OUT/'filament.json'),
       '--arrange', '0', '--orient', '0', '--slice', '0',
       '--export-3mf', f'{JOB}.gcode.3mf', '--outputdir', str(OUT),
       str(OUT/f'{JOB}.stl')]
# 0.1 mm layer bands around every modelled-support deck top, so the decks'
# 0.1 mm Z gap (PEG_SUPPORT_GAP_Z=0.1 in print_supports.py) is one real layer.
# Stock Orca: --load-assemble-list with per-object height_ranges.
BANDS = {'tw09b': [(7.8, 9.4), (27.0, 28.4), (33.2, 34.8)]}.get(WHICH)
if PARTS:   # separate objects, each STL already in bed coordinates
    plan = {'plates': [{'plate_name': JOB, 'need_arrange': False, 'objects': [
        {'path': str(f), 'count': 1, 'filaments': [1], 'pos_x': [0.0], 'pos_y': [0.0], 'pos_z': [0.0]} for f in PARTS]}]}
    (OUT/'assemble.json').write_text(json.dumps(plan, indent=1))
    cmd = [c for i, c in enumerate(cmd[:-1]) if not (c in ('--arrange', '--orient') or cmd[i-1] in ('--arrange', '--orient'))]
    cmd += ['--load-assemble-list', str(OUT/'assemble.json')]
elif BANDS:
    plan = {'plates': [{'plate_name': JOB, 'need_arrange': False, 'objects': [{
        'path': str(OUT/f'{JOB}.stl'), 'count': 1, 'filaments': [1], 'pos_x': [0.0], 'pos_y': [0.0], 'pos_z': [0.0],
        'height_ranges': [{'min_z': lo, 'max_z': hi, 'range_params': {'layer_height': '0.1'}} for lo, hi in BANDS]}]}]}
    (OUT/'assemble.json').write_text(json.dumps(plan, indent=1))
    # Orca refuses --arrange/--orient (transforms) alongside an assemble list.
    cmd = [c for i, c in enumerate(cmd[:-1]) if not (c in ('--arrange', '--orient') or cmd[i-1] in ('--arrange', '--orient'))]
    cmd += ['--load-assemble-list', str(OUT/'assemble.json')]
r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
print('orca exit', r.returncode)
print(r.stdout[-800:], r.stderr[-800:])

# Orca's CLI reads printer_model_id from resources/profiles/BBL/machine_full/,
# which the 2.4.2 install does not ship, so slice_info carries an empty id and
# the bridge's G6 gate refuses it. Write the id the GUI would: model_id of the
# printer_model named in the sliced G-code, from the installed BBL machine file.
job = OUT/f'{JOB}.gcode.3mf'
with zipfile.ZipFile(job) as z:
    members = {n: z.read(n) for n in z.namelist()}
header = members['Metadata/plate_1.gcode'][:200000].decode('utf-8', 'ignore')
model = re.search(r'^; printer_model = (.+)$', header, re.M).group(1).strip()
assert model == 'Bambu Lab P1S', model
model_id = json.loads(Path(r'C:\Program Files\OrcaSlicer\resources\profiles\BBL\machine', model+'.json').read_text())['model_id']
info = members['Metadata/slice_info.config'].decode()
assert '<metadata key="printer_model_id" value=""/>' in info
members['Metadata/slice_info.config'] = info.replace('<metadata key="printer_model_id" value=""/>',
    f'<metadata key="printer_model_id" value="{model_id}"/>').encode()
tmp = job.with_suffix('.tmp')
with zipfile.ZipFile(job) as src, zipfile.ZipFile(tmp, 'w') as dst:
    for item in src.infolist():
        dst.writestr(item, members[item.filename])
tmp.replace(job)
print('printer_model_id', model_id)
