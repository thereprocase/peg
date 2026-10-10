"""Repackage the exact unscaled v2 body and brace meshes as an Orca/Bambu project.
Geometry and modifier positions unchanged. Filament compensation applies once in the owner's slicer.
No machine/filament preset, credentials or G-code are embedded.
"""
import argparse,json,zipfile,hashlib,struct,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np

def stl(data):
 n=struct.unpack_from('<I',data,80)[0];assert len(data)==84+50*n;record=np.ndarray((n,),dtype=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]),buffer=data,offset=84);V,F=np.unique(record['v'].reshape(-1,3),axis=0,return_inverse=True);return V,F.reshape(-1,3)
def xml_mesh(V,F,oid):
 vertices=''.join(f'<vertex x="{v[0]:.9g}" y="{v[1]:.9g}" z="{v[2]:.9g}"/>' for v in V);triangles=''.join(f'<triangle v1="{f[0]}" v2="{f[1]}" v3="{f[2]}"/>' for f in F);return f'<object id="{oid}" type="model"><mesh><vertices>{vertices}</vertices><triangles>{triangles}</triangles></mesh></object>'
def main():
 p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(a.bundle) as z:
  report=json.loads(z.read('bench/reviews/key-fan-v2/HX04/report.json'));names=[report['assets']['print.stl'],report['assets']['print_solid-zones.stl']];entries=[z.read('bench/reviews/key-fan-v2/HX04/'+n) for n in names]
 expected=['eef57613d3cc8b469d66e27c4934bcd748bda2c292b9426f16abf52a39661eef','0475c37a1483699071c73778a80f517153a0b3f90e60fb4dea8c31aa864cbc55'];meshes=[]
 for name,data,h in zip(names,entries,expected):assert hashlib.sha256(data).hexdigest()==h;meshes.append(stl(data))
 body,zone=meshes;model='<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources>'+xml_mesh(*body,1)+xml_mesh(*zone,2)+'<object id="3" type="model"><components><component objectid="1"/><component objectid="2"/></components></object></resources><build><item objectid="3"/></build></model>'
 config='<?xml version="1.0" encoding="UTF-8"?><config><object id="3"><metadata key="name" value="HX04 v2 — uncompensated geometry; apply your filament compensation once"/><metadata key="extruder" value="1"/><part id="1" subtype="normal_part"><metadata key="name" value="exact v2 body"/></part><part id="2" subtype="modifier_part"><metadata key="name" value="brace zones at 100 percent"/><metadata key="sparse_infill_density" value="100%"/></part></object></config>'
 ctypes='<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
 rels='<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
 path=a.out/'HX04-v2__uncompensated-brace-project__reslice.3mf'
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  for name,data in [('[Content_Types].xml',ctypes),('_rels/.rels',rels),('3D/3dmodel.model',model),('Metadata/model_settings.config',config)]:z.writestr(name,data)
 # Verify positions and modifier semantics in the delivered archive, independently of the source arrays.
 with zipfile.ZipFile(path) as z:
  root=ET.fromstring(z.read('3D/3dmodel.model'));ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
  for obj,(V,F) in zip(root.findall('m:resources/m:object',ns)[:2],meshes):
   read=np.array([[float(v.attrib[k]) for k in 'xyz'] for v in obj.findall('m:mesh/m:vertices/m:vertex',ns)]);assert np.allclose(read,V,atol=5e-7,rtol=0)
  conf=ET.fromstring(z.read('Metadata/model_settings.config'));part=conf.find("object/part[@id='2']");assert part.attrib['subtype']=='modifier_part' and part.find("metadata[@key='sparse_infill_density']").attrib['value']=='100%'
  assert not any('gcode' in n or 'project_settings' in n for n in z.namelist())
 r=dict(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),project_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),input_meshes=dict(zip(names,expected)),geometry_scale=1.,original_print_pose_preserved=True,modifier_alignment_preserved=True,modifier_sparse_infill='100%',embedded_machine_or_filament_profiles=False,gcode_included=False,body_extents_mm=np.ptp(body[0],axis=0).tolist(),scope='Repack of archived v2 geometry, not a new fit-qualified rack. Existing owner compensation must be applied once. Supports, compensated bed/brim fit and physical installation need new owner-profile review.')
 (a.out/'uncompensated-project-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
