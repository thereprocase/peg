"""Standard geometry-only 3MF with both print orientations. No machine G-code."""
from pathlib import Path
import zipfile,xml.etree.ElementTree as ET
import trimesh,json
root=Path(__file__).resolve().parent
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('',NS)
def el(tag,*a,**k):return ET.Element('{'+NS+'}'+tag,*a,**k)
def sub(parent,tag,attrs=None):return ET.SubElement(parent,'{'+NS+'}'+tag,attrs or {})
model=el('model',{'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'en-US'})
sub(model,'metadata',{'name':'Title'}).text='Round pegboard anchor — two print orientations'
sub(model,'metadata',{'name':'Description'}).text='Geometry only. Side anchor with removable cradles, or upright anchor with cradles on cut-away webs. Keep each model and its cradles in their supplied relative positions. Select your printer and filament before slicing. No machine-specific settings or G-code.'
resources=sub(model,'resources');build=sub(model,'build')
for oid,name,path,shift in [(1,'SIDE_remove_cradles',root/'cad/round_side_supported.stl',(15,15,0)),(2,'UPRIGHT_cut_webs_remove_cradles',root/'cad/round_upright_supported.stl',(65,15,0))]:
    mesh=trimesh.load(path,force='mesh');assert mesh.is_watertight
    ob=sub(resources,'object',{'id':str(oid),'type':'model','name':name});me=sub(ob,'mesh');vs=sub(me,'vertices');fs=sub(me,'triangles')
    for x,y,z in mesh.vertices:sub(vs,'vertex',{'x':f'{x:.6f}','y':f'{y:.6f}','z':f'{z:.6f}'})
    for a,b,c in mesh.faces:sub(fs,'triangle',{'v1':str(a),'v2':str(b),'v3':str(c)})
    tx,ty,tz=shift;sub(build,'item',{'objectid':str(oid),'transform':f'1 0 0 0 1 0 0 0 1 {tx} {ty} {tz}'})
# OPC package content types and root relationship.
ct=b'''<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'''
rels=b'''<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'''
out=root/'Round_Print_Options.3mf'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml',ct);z.writestr('_rels/.rels',rels);z.writestr('3D/3dmodel.model',ET.tostring(model,encoding='utf-8',xml_declaration=True))
with zipfile.ZipFile(out) as z:ET.fromstring(z.read('3D/3dmodel.model'))
scene=trimesh.load(out)
report={'file':out.name,'geometry_objects':len(scene.geometry),
        'all_watertight':all(m.is_watertight for m in scene.geometry.values()),
        'all_positive_volume':all(m.is_volume for m in scene.geometry.values()),
        'units':'millimeter','geometry_only':True,'machine_profile_included':False,
        'keep_support_positions':True}
assert report['geometry_objects']==2 and report['all_watertight'] and report['all_positive_volume']
(root/'round_3mf_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
