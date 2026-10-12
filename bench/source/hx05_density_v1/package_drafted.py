"""Geometry REVIEW projects: fixed bed pose, four separate solid-infill masks."""
from pathlib import Path
import json, zipfile, hashlib
import xml.etree.ElementTree as E
import trimesh
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'.local-runtime/hx05-density-v1'
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
E.register_namespace('',NS)
def tag(name):return '{'+NS+'}'+name
def metadata(parent,key,value):E.SubElement(parent,'metadata',key=key,value=str(value))
receipts=[]
for ident,number in [('HX05C','13190'),('HX05B','13189'),('HX05A','33034')]:
 out=WORK/ident;check=json.loads((out/'modifiers-check.json').read_text());assert check['passed'] and check['print_rotation_unchanged'] and check['body_shape_unchanged']
 names=['print-drafted-body-closed.stl']+[f'print-modifier-{role}.stl' for role in ['foundation','mounts','sockets','ribs']]+['print-drafted-support-blocker.stl']
 model=E.Element(tag('model'),unit='millimeter');resources=E.SubElement(model,tag('resources'))
 config=E.Element('config');settings=E.SubElement(config,'object',id='7')
 metadata(settings,'name',f'{ident} Bondhus {number} — finished v1')
 for key,value in [('extruder',1),('sparse_infill_density','12%'),('sparse_infill_pattern','gyroid'),('wall_loops',4),('enable_support',1)]:metadata(settings,key,value)
 if ident=='HX05C':
  metadata(settings,'support_type','normal(auto)');metadata(settings,'support_style','grid')
 for i,name in enumerate(names,1):
  mesh=trimesh.load(out/name,force='mesh',process=True);assert mesh.is_watertight and mesh.is_volume,(ident,name)
  obj=E.SubElement(resources,tag('object'),id=str(i),type='model');m=E.SubElement(obj,tag('mesh'))
  vertices=E.SubElement(m,tag('vertices'));triangles=E.SubElement(m,tag('triangles'))
  for x,y,z in mesh.vertices:E.SubElement(vertices,tag('vertex'),x=f'{x:.6f}',y=f'{y:.6f}',z=f'{z:.6f}')
  for a,b,c in mesh.faces:E.SubElement(triangles,tag('triangle'),v1=str(a),v2=str(b),v3=str(c))
  subtype='normal_part' if i==1 else ('support_blocker' if i==6 else 'modifier_part')
  part=E.SubElement(settings,'part',id=str(i),subtype=subtype);metadata(part,'name',name)
  if subtype=='modifier_part':metadata(part,'sparse_infill_density','100%')
 group=E.SubElement(resources,tag('object'),id='7',type='model');components=E.SubElement(group,tag('components'))
 for i in range(1,7):E.SubElement(components,tag('component'),objectid=str(i))
 E.SubElement(E.SubElement(model,tag('build')),tag('item'),objectid='7')
 assert len(settings.findall('part[@subtype="normal_part"]'))==1
 assert len(settings.findall('part[@subtype="modifier_part"]'))==4
 assert all(p.find('metadata[@key="sparse_infill_density"]').get('value')=='100%' for p in settings.findall('part[@subtype="modifier_part"]'))
 filename=f'{ident}_{number}_draft_review_tip_down.3mf';path=out/filename
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
  z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
  z.writestr('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))
  z.writestr('Metadata/model_settings.config',E.tostring(config,encoding='utf-8',xml_declaration=True))
  z.writestr('Metadata/REVIEW_STATUS.txt','Not print-qualified. Native CAD is the manufacturing reference. Body export has bounded rear-peg seam caps; topology passed, but surface intersections and actual-profile toolpaths still require review. Four independent modifiers set to 100% infill. Print pose is unchanged. No profile, G-code or compensation included.\n')
 receipts.append(dict(id=ident,project=filename,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),normal_parts=1,modifier_parts=4,modifier_density='100%',support_blockers=1,rotation_unchanged=True,translation_unchanged=True,print_qualified=False))
 print(ident,filename,flush=True)
(WORK/'draft-project-check.json').write_text(json.dumps(dict(passed=True,projects=receipts,scope='Project metadata/topology/pose gates only; manufacturing surface-intersection and actual-profile toolpath checks outstanding.'),indent=2)+'\n')
