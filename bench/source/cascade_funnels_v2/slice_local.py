"""Local-only P1S/PolyLite ASA review slice; no printer communication."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys,zipfile
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[3]
PROFILES=Path('/home/repro/code/peg-bt2/print/profiles')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('id');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    d=ROOT/'bench/reviews/cascade-funnels-v2'/a.id;r=json.loads((d/'report.json').read_text());out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
    gate=json.loads((d/'print-geometry.json').read_text());assert gate['passed'],gate
    source=d/r['assets']['print_stl'];m=trimesh.load(source,force='mesh')
    # Match existing ASA preparation: compensate all geometry once before slicing.
    fil=json.loads((PROFILES/'filament-asa-polylite-calibrated.json').read_text());shrink=float(fil['filament_shrink'][0].strip('%'))/100
    scale=1/shrink;m.apply_scale(scale);shift=np.array([128,140,0])-np.array([*m.bounds.mean(axis=0)[:2],m.bounds[0,2]])
    m.apply_translation(shift);plate=out/'plate-asa-baked.stl';m.export(plate)
    fil.update(filament_settings_id=[fil['name']],filament_shrink=['100%','100%'])
    process=json.loads((PROFILES/'process.json').read_text());process.update(brim_type='outer_only',brim_width='5',post_process=[],wall_loops='2',sparse_infill_density='20%',enable_support='1',support_type='tree(auto)',support_style='organic',support_on_build_plate_only='1',support_threshold_angle='45',support_remove_small_overhang='0',wall_generator='arachne',print_sequence='by layer',curr_bed_type='Textured PEI Plate')
    for file,obj in [('filament.json',fil),('process.json',process)]: (out/file).write_text(json.dumps(obj,indent=2)+'\n')
    cmd=['flatpak','run','com.orcaslicer.OrcaSlicer','--datadir',str(out/'data'),'--load-settings',str(PROFILES/'machine.json')+';'+str(out/'process.json'),'--load-filaments',str(out/'filament.json'),'--arrange','0','--orient','0','--slice','0','--export-3mf','REVIEW-ONLY.gcode.3mf','--outputdir',str(out),str(plate)]
    run=subprocess.run(cmd,capture_output=True,text=True,timeout=900);(out/'orca.log').write_text(run.stdout+'\n'+run.stderr);assert run.returncode==0,run.stderr[-2000:]
    with zipfile.ZipFile(out/'REVIEW-ONLY.gcode.3mf') as z:code=z.read('Metadata/plate_1.gcode').decode('utf-8','replace')
    (out/'plate_1.gcode').write_text(code)
    def field(key):
        match=re.search(r'^; '+re.escape(key)+r'\s*(?:=|:)\s*(.+)$',code,re.M);return match.group(1).strip() if match else None
    record=dict(id=a.id,input_sha256=digest(source),scale=scale,translation_mm=shift.tolist(),profile_hashes={p.name:digest(p) for p in [PROFILES/'machine.json',PROFILES/'process.json',PROFILES/'filament-asa-polylite-calibrated.json']},settings={k:field(k) for k in ['layer_height','wall_loops','sparse_infill_density','support_type','support_style','brim_width','total filament used [g]','estimated printing time (normal mode)','total layer number']},local_only=True)
    (out/'summary.json').write_text(json.dumps(record,indent=2)+'\n');(d/'slice-summary.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
if __name__=='__main__':main()
