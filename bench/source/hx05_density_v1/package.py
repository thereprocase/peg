"""Package native modifier geometry as one Orca object with a 100%-infill modifier."""
from pathlib import Path
import json,zipfile,hashlib,sys
import xml.etree.ElementTree as E
import numpy as np,trimesh
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'.local-runtime/hx05-density-v1'

def mesh_xml(mesh,oid):
 vertices=''.join(f'<vertex x="{x:.6f}" y="{y:.6f}" z="{z:.6f}"/>' for x,y,z in mesh.vertices)
 triangles=''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in mesh.faces)
 return f'<object id="{oid}" type="model"><mesh><vertices>{vertices}</vertices><triangles>{triangles}</triangles></mesh></object>'

cap_check=json.loads((WORK/'mesh-cap-check.json').read_text());assert cap_check['passed']
results=[]
for ident in ['HX05C','HX05B','HX05A']:
 out=WORK/ident;check=json.loads((out/'check.json').read_text());assert check['passed'] and check['holder_unchanged'];structure=json.loads((out/'structure-check.json').read_text());assert structure['passed']
 meshes=[trimesh.load(out/name,force='mesh',process=True) for name in ('print-structural-body-closed.stl','print-selected-core-closed.stl','print-support-blocker.stl')]
 for mesh in meshes:
  assert mesh.is_watertight and mesh.is_volume,(ident,mesh.is_watertight,mesh.is_volume)
 body,core,blocker=meshes;
 for mesh in meshes:mesh.apply_translation([0,4,0])
 assert np.all(core.bounds[0]>=body.bounds[0]-.001) and np.all(core.bounds[1]<=body.bounds[1]+.001)
 model=('<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources>'+mesh_xml(body,1)+mesh_xml(core,2)+mesh_xml(blocker,3)+'<object id="4" type="model"><components><component objectid="1"/><component objectid="2"/><component objectid="3"/></components></object></resources><build><item objectid="4"/></build></model>')
 config=(f'<config><object id="4"><metadata key="name" value="{ident} Bondhus {check["set"]} density v1"/><metadata key="extruder" value="1"/><metadata key="sparse_infill_density" value="12%"/><metadata key="sparse_infill_pattern" value="gyroid"/><metadata key="wall_loops" value="4"/><metadata key="enable_support" value="1"/><part id="1" subtype="normal_part"><metadata key="name" value="Trimmed structural holder — 12% bulk infill"/></part><part id="2" subtype="modifier_part"><metadata key="name" value="Strategic structural core — 100% infill"/><metadata key="sparse_infill_density" value="100%"/></part><part id="3" subtype="support_blocker"><metadata key="name" value="No supports inside sockets or funnels"/></part></object></config>')
 # Validate slicer subtype and per-part density before shipping. These meshes
 # contain no G-code, printer credentials or unreviewed filament compensation.
 tree=E.fromstring(config);assert len(tree.findall('.//part[@subtype="normal_part"]'))==1
 part=tree.find('.//part[@subtype="modifier_part"]');assert part.find('metadata[@key="sparse_infill_density"]').attrib['value']=='100%'
 filename=f'{ident}_{check["set"]}_density_v1_tip_down.3mf';project=out/filename
 with zipfile.ZipFile(project,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
  z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
  z.writestr('3D/3dmodel.model',model);z.writestr('Metadata/model_settings.config',config)
 results.append(dict(id=ident,project=filename,bytes=project.stat().st_size,sha256=hashlib.sha256(project.read_bytes()).hexdigest(),body_watertight=True,modifier_watertight=True,modifier_subtype='modifier_part',modifier_density='100%',base_density='12%',baseline_construction_unchanged=True,outer_holder_trimmed=True,print_y_offset_mm=4,solid_core_percent=100*structure['selected_core_volume_mm3']/structure['structural_volume_mm3']))
print(json.dumps(results,indent=2));(WORK/'package-check.json').write_text(json.dumps(dict(passed=True,models=results,scope='Geometry-only project structure/native/mesh checks. Actual profile, support and toolpath qualification pending.'),indent=2)+'\n')
