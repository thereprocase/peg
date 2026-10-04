"""Package native connector CAD separately from tessellated exchange/viewer assets."""
from pathlib import Path
import hashlib,json,shutil,sys,zipfile
import xml.etree.ElementTree as E
import numpy as np,trimesh
R=Path(__file__).resolve().parents[1];B=R/'bench/reviews/peg-connectors-v1';PAGE=R/'docs/pegs';TAG='peg-connectors-v1-2026-10-04';URL='https://github.com/thereprocase/peg/releases/download/'+TAG+'/'
def receipt(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
def three_mf(mesh,path):
 ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';E.register_namespace('',ns);model=E.Element('{'+ns+'}model',unit='millimeter',attrib={'{http://www.w3.org/XML/1998/namespace}lang':'en-US'});resources=E.SubElement(model,'{'+ns+'}resources');obj=E.SubElement(resources,'{'+ns+'}object',id='1',type='model');element=E.SubElement(obj,'{'+ns+'}mesh');vertices=E.SubElement(element,'{'+ns+'}vertices');triangles=E.SubElement(element,'{'+ns+'}triangles')
 for x,y,z in mesh.vertices:E.SubElement(vertices,'{'+ns+'}vertex',x=format(x,'.12g'),y=format(y,'.12g'),z=format(z,'.12g'))
 for a,b,c in mesh.faces:E.SubElement(triangles,'{'+ns+'}triangle',v1=str(a),v2=str(b),v3=str(c))
 build=E.SubElement(model,'{'+ns+'}build');E.SubElement(build,'{'+ns+'}item',objectid='1')
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True));z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>');z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
 with zipfile.ZipFile(path) as z:assert z.testzip() is None

def main(out):
 out.mkdir(parents=True,exist_ok=True);PAGE.mkdir(parents=True,exist_ok=True);data=json.loads((B/'BUILD.json').read_text());files=[];parts=[];formats=['step','freecad','iges','brep','stl','obj','3mf'];format_paths={f:[] for f in formats};proof=[]
 for part in data['parts']:
  mesh=trimesh.load_mesh(B/part['assets']['stl'],process=True);assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0;assert len(mesh.split(only_watertight=True))==part['solids']
  prefix=part['prefix'];(B/(prefix+'.obj')).write_text(mesh.export(file_type='obj'));three_mf(mesh,B/(prefix+'.3mf'));part['assets'].update(obj=prefix+'.obj',**{'3mf':prefix+'.3mf'});links={}
  for fmt,name in part['assets'].items():
   src=B/name;shutil.copy2(src,out/name);files.append(name);format_paths[fmt].append(out/name);links[fmt]=URL+name
  display=mesh.copy();centers=display.triangles_center;display.visual.face_colors=np.where((centers[:,1]>.15)[:,None],np.array([246,165,74,255]),np.array([84,191,219,255]));display.apply_transform(np.array([[.001,0,0,0],[0,0,.001,0],[0,-.001,0,0],[0,0,0,1]]));preview=PAGE/(part['id']+'.glb');preview.write_bytes(trimesh.Scene(display).export(file_type='glb'))
  parts.append({'id':part['id'],'name':part['name'],'links':links,'preview':preview.name,'interface':part['interface'],'solids':part['solids']});proof.append({'id':part['id'],'watertight':True,'mesh_solids':part['solids'],'native_cylindrical_faces':part['analytical_cylindrical_faces'],'native_face_types':part['analytic_face_types'],'mesh_source_sha256':receipt(B/part['assets']['stl'])['sha256']})
 text='''Current peg connectors — millimeters

PF02 #9 upper hook and PF07 #5 lower hoop, using the unchanged current-fit analytical solids and original analytical locator STEP. The demonstration handle is omitted.

Align the flat nub shoulder (Y = 0.15 mm) with the holder rear/board-facing plane. The nub extends 2 mm toward +Y into the body; give it real shared volume and Boolean Union / Combine Join / Part Fuse. Nub diameter is +20%: 6.72 mm upper (5.6 reference), 7.62 mm lower (6.35 reference). The original hole axis is Z = 0.12 mm. Individual parts share that hole axis; pre-spaced pairs place the lower peg 25.4 mm below the upper. Choose upright or cheek hoops to match the eventual print-layer flex direction.

Use STEP for Fusion/Onshape/solid CAD exchange. FCStd contains native solid features and named holder datum planes; Python source controls construction dimensions. BREP preserves OpenCascade topology. IGES exports native curved surfaces and may require sewing in the destination CAD app. STL/OBJ/3MF are tessellated geometry inputs, not editable solid source or printer jobs. GLB is display only. No proprietary F3D/Parasolid file is claimed.

Native STEP/BREP and sewn IGES round-trips passed exact solid comparisons; the holder-side nub preserves the functional board-side shapes and passes a sample one-solid host union. These checks do not establish physical fit, loads or support release. The complete holder needs its own installation clearance and printing review. The original nominal anchor motion study does not certify this interference variant.

Rebuild with FreeCAD Python and numpy:
  freecad-python bench/source/peg_connectors_v1/build.py fresh-output
'''
 (out/'README.txt').write_text(text);(PAGE/'integration.txt').write_text(text)
 for fmt in formats:
  name='pegs-current-fit__v1__nub120__'+('FCStd' if fmt=='freecad' else fmt)+'.zip'
  with zipfile.ZipFile(out/name,'w',zipfile.ZIP_DEFLATED) as z:
   for f in format_paths[fmt]:z.write(f,f.name)
   z.writestr('README.txt',text)
  files.append(name)
 bundle='pegs-current-fit__v1__nub120__all-formats-and-source.zip'
 with zipfile.ZipFile(out/bundle,'w',zipfile.ZIP_DEFLATED) as z:
  for fmt in formats:
   for f in format_paths[fmt]:z.write(f,f.name)
  z.writestr('README.txt',text);z.write(B/'BUILD.json','review/BUILD.json');z.writestr('review/MESH-CHECKS.json',json.dumps(proof,indent=2)+'\n')
  for path in data['source_hashes']:z.write(R/path,path)
 files.append(bundle)
 manifest={'units':'mm','tag':TAG,'parts':parts,'all_formats':URL+bundle,'formats':{fmt:URL+'pegs-current-fit__v1__nub120__'+('FCStd' if fmt=='freecad' else fmt)+'.zip' for fmt in formats},'validation':proof};(PAGE/'catalog.json').write_text(json.dumps(manifest,indent=2)+'\n');(B/'MESH-CHECKS.json').write_text(json.dumps(proof,indent=2)+'\n')
 assets=json.loads((R/'publication/release-assets.json').read_text());moves=json.loads((R/'publication/release-downloads.json').read_text())
 for n in files:assets[n]=receipt(out/n);moves['pegs/'+n]=URL+n
 (R/'publication/release-assets.json').write_text(json.dumps(assets,indent=2)+'\n');(R/'publication/release-downloads.json').write_text(json.dumps(moves,indent=2)+'\n');p=R/'docs/gallery/release-downloads.js';before,tail=p.read_text().split('const links=',1);_,after=tail.split(';function fix(node)',1);p.write_text(before+'const links='+json.dumps(moves,separators=(',',':'))+';function fix(node)'+after)
 receipts={str(p.relative_to(R/'docs')):receipt(p) for p in PAGE.iterdir() if p.is_file()};receipts.update({n:receipt(out/n) for n in files});(R/'publication/peg-connectors-v1-additions.json').write_text(json.dumps(receipts,indent=2)+'\n');(out/'release-files.json').write_text(json.dumps(files,indent=2)+'\n');print('Prepared 6 peg parts, 7 formats,',len(files),'release assets; native shapes retained')
if __name__=='__main__':main(Path(sys.argv[1]))
