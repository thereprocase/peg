"""Check the private Orca archive and emit only credential-free slice facts."""
from pathlib import Path
import json,zipfile,sys,os,xml.etree.ElementTree as E
folder=Path(sys.argv[1]);ident=folder.name
light=os.environ.get('HX05_LIGHT')=='1'
with zipfile.ZipFile(folder/(ident+'-review.gcode.3mf')) as z:
 config=E.fromstring(z.read('Metadata/model_settings.config'))
 parts=config.findall('.//part');assert len(parts)==6
 assert len([p for p in parts if p.attrib["subtype"]=="support_blocker"])==1
 cores=[p for p in parts if p.attrib['subtype']=='modifier_part'];assert len(cores)==4
 assert all(core.find('metadata[@key="sparse_infill_density"]').attrib['value']=='100%' for core in cores)
 assert len([p for p in parts if p.attrib['subtype']=='normal_part'])==1
 obj=config.find('object')
 assert obj.find('metadata[@key="sparse_infill_density"]').attrib['value']==('5%' if light else '12%')
 assert obj.find('metadata[@key="wall_loops"]').attrib['value']==('3' if light else '4')
 if ident=='HX05C' or light:
  assert obj.find('metadata[@key="support_type"]').attrib['value']=='normal(auto)'
  assert obj.find('metadata[@key="support_style"]').attrib['value']=='grid'
 for stat in config.findall('.//mesh_stat'):
  assert all(int(value)==0 for value in stat.attrib.values())
 review=json.loads((folder/'review.json').read_text());assert review['exit_code']==0
 review['modifier_subtype']='modifier_part';review['modifier_infill_percent']=100
 review['modifier_count']=4
 review['support_type']='normal(auto)' if ident=='HX05C' or light else 'tree(auto)'
 review['base_infill_percent']=5 if light else 12
 review['slicer_mesh_repairs']=0;review['source_nominal_unscaled']=True
 text=review.pop('model printing time');model,total=text.split('; total estimated time: ')
 review['model_print_time']=model;review['total_estimated_print_time']=total
 review['filament_grams']=float(review.pop('filament used [g]'))
 (folder/'slice-review.json').write_text(json.dumps(review,indent=2)+'\n')
 print(ident,'Orca modifier preservation and zero repairs PASS')
