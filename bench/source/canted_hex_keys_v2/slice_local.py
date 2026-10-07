"""Local-only P1S / PolyLite ASA (ReproCal) review slice on Windows OrcaSlicer; no printer communication.

Profiles are resolved from the local Orca install: the owner's calibrated filament preset and the
system P1S 0.4 machine and 0.20 mm Standard process, each flattened through its `inherits` chain.
"""
from pathlib import Path
import argparse, hashlib, json, os, re, subprocess, zipfile
import numpy as np
import trimesh
ROOT = Path(__file__).resolve().parents[3]
ORCA = Path(r'C:\Program Files\OrcaSlicer\orca-slicer.exe')
DATA = Path(os.environ['APPDATA'])/'OrcaSlicer'
SYSTEM = DATA/'system/BBL'
USER_FILAMENT = next((DATA/'user').glob('*/filament/PolyLite ASA - ReproCal.json'))


def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def flatten(path, kind):
    """Merge a preset over its inherits chain (system presets are found by name)."""
    j = json.loads(path.read_text(encoding='utf-8'))
    parent = j.get('inherits')
    if parent:
        hits = [q for q in (SYSTEM/kind).rglob('*.json') if q.stem == parent]
        assert len(hits) == 1, (parent, hits)
        base = flatten(hits[0], kind)
        base.update(j); j = base
    j.pop('inherits', None)
    return j


def main():
    p = argparse.ArgumentParser(); p.add_argument('id'); p.add_argument('--out', type=Path, required=True); a = p.parse_args()
    d = ROOT/'bench/reviews/canted-hex-keys-v2'/a.id; r = json.loads((d/'report.json').read_text()); out = a.out.resolve(); out.mkdir(parents=True, exist_ok=False)
    gate = json.loads((d/'print-geometry.json').read_text()); assert gate['passed'], gate
    source = d/r['assets']['print_stl']; m = trimesh.load(source, force='mesh')
    machine = flatten(SYSTEM/'machine/Bambu Lab P1S 0.4 nozzle.json', 'machine')
    process = flatten(SYSTEM/'process/0.20mm Standard @BBL X1C.json', 'process')
    fil = flatten(USER_FILAMENT, 'filament')
    # Match the v1 ASA preparation: compensate all geometry once before slicing.
    shrink = float(fil['filament_shrink'][0].strip('%'))/100
    scale = 1/shrink; m.apply_scale(scale); shift = np.array([128, 140, 0])-np.array([*m.bounds.mean(axis=0)[:2], m.bounds[0, 2]])
    m.apply_translation(shift); plate = out/'plate-asa-baked.stl'; m.export(plate)
    fil.update(filament_settings_id=[fil['name']], filament_shrink=['100%'])
    machine.update(printer_settings_id=machine['name'])
    process.update(print_settings_id=process['name'], brim_type='outer_only', brim_width='5', post_process=[], wall_loops='2', sparse_infill_density='20%',
                   enable_support='1', support_type='tree(auto)', support_style='organic', support_on_build_plate_only='1', support_threshold_angle='45',
                   support_remove_small_overhang='0', wall_generator='arachne', print_sequence='by layer', curr_bed_type='Textured PEI Plate')
    for name, obj in [('machine.json', machine), ('filament.json', fil), ('process.json', process)]:
        (out/name).write_text(json.dumps(obj, indent=2)+'\n', newline='\n')
    cmd = [str(ORCA), '--datadir', str(out/'data'), '--load-settings', str(out/'machine.json')+';'+str(out/'process.json'),
           '--load-filaments', str(out/'filament.json'), '--arrange', '0', '--orient', '0', '--slice', '0',
           '--export-3mf', 'REVIEW-ONLY.gcode.3mf', '--outputdir', str(out), str(plate)]
    run = subprocess.run(cmd, capture_output=True, text=True, timeout=1800); (out/'orca.log').write_text(run.stdout+'\n'+run.stderr)
    assert run.returncode == 0, (run.returncode, run.stderr[-2000:], run.stdout[-2000:])
    with zipfile.ZipFile(out/'REVIEW-ONLY.gcode.3mf') as z: code = z.read('Metadata/plate_1.gcode').decode('utf-8', 'replace')
    (out/'plate_1.gcode').write_text(code, newline='\n')

    def field(key):
        match = re.search(r'^; '+re.escape(key)+r'\s*(?:=|:)\s*(.+)$', code, re.M); return match.group(1).strip() if match else None
    record = dict(id=a.id, input_sha256=digest(source), scale=scale, translation_mm=shift.tolist(),
                  profiles=dict(machine='Bambu Lab P1S 0.4 nozzle (system)', process='0.20mm Standard @BBL X1C (system) + review overrides', filament='PolyLite ASA - ReproCal (owner calibrated)'),
                  profile_hashes={p.name: digest(p) for p in [out/'machine.json', out/'process.json', out/'filament.json']},
                  settings={k: field(k) for k in ['layer_height', 'wall_loops', 'sparse_infill_density', 'support_type', 'support_style', 'brim_width', 'total filament used [g]', 'estimated printing time (normal mode)', 'total layer number']},
                  local_only=True)
    (out/'summary.json').write_text(json.dumps(record, indent=2)+'\n'); (d/'slice-summary.json').write_text(json.dumps(record, indent=2)+'\n', newline='\n'); print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
