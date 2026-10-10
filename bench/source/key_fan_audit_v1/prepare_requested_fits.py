"""Repack only the requested 3/5 mm fan-angle spectra, without machine compensation."""
import FreeCAD as A,Part,MeshPart,Mesh,json,hashlib,struct,math
from pathlib import Path
R=Path(__file__).resolve().parents[3];src=R/'bench/reviews/tee-fit-v6-fan';out=R/'bench/reviews/key-fan-audit-v1';web=R/'docs/gallery/key-fan/fit-requested-3-5';web.mkdir(exist_ok=True);pieces=[];y=0;inputs={}
for size in [3,5]:
 p=src/f'HX05-fit-v6-{size}mm__fan-angle__print.step';s=Part.read(str(p));assert s.isValid() and len(s.Solids)==1;b=s.BoundBox;s.translate(A.Vector(-b.XMin,y-b.YMin,-b.ZMin));y+=b.YLength+8;pieces.append(s);inputs[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
shape=Part.makeCompound(pieces);name='HX04-fit-v6__3mm-5mm__fan-angle__print';shape.exportStep(str(out/(name+'.step')));m=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.03,AngularDeflection=.12,Relative=False);assert m.isSolid() and m.countComponents()==2;m.write(str(web/(name+'.stl')));m.write(str(out/(name+'.stl')))
# Geometry-only preview, using the original gallery world conversion.
points,faces=m.Topology;v=[];n=[]
for a,b,c in faces:
 p=[[points[i].x*.001,points[i].z*.001,-points[i].y*.001] for i in [a,b,c]];u=[p[1][i]-p[0][i] for i in range(3)];w=[p[2][i]-p[0][i] for i in range(3)];q=[u[1]*w[2]-u[2]*w[1],u[2]*w[0]-u[0]*w[2],u[0]*w[1]-u[1]*w[0]];length=math.sqrt(sum(x*x for x in q));q=[x/length for x in q]
 for row in p:v.extend(row);n.extend(q)
pos=struct.pack('<'+'f'*len(v),*v);norm=struct.pack('<'+'f'*len(n),*n);binary=pos+norm;count=len(v)//3
j=dict(asset={'version':'2.0'},scene=0,scenes=[{'nodes':[0]}],nodes=[{'mesh':0}],meshes=[{'primitives':[{'attributes':{'POSITION':0,'NORMAL':1},'material':0}]}],materials=[{'pbrMetallicRoughness':{'baseColorFactor':[.12,.55,.5,1],'metallicFactor':0,'roughnessFactor':.7}}],buffers=[{'byteLength':len(binary)}],bufferViews=[{'buffer':0,'byteOffset':0,'byteLength':len(pos)},{'buffer':0,'byteOffset':len(pos),'byteLength':len(norm)}],accessors=[{'bufferView':0,'componentType':5126,'count':count,'type':'VEC3','min':[min(v[i::3]) for i in range(3)],'max':[max(v[i::3]) for i in range(3)]},{'bufferView':1,'componentType':5126,'count':count,'type':'VEC3'}]);encoded=json.dumps(j,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4);binary+=b'\0'*((-len(binary))%4);(web/'coupon.glb').write_bytes(struct.pack('<III',0x46546c67,2,28+len(encoded)+len(binary))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(binary),0x004e4942)+binary)
r=dict(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),sizes_mm=[3,5],inputs=inputs,geometry_compensation_scale=1,closed_mesh=True,mesh_components=2,step_solids=2,print_extents_mm=[shape.BoundBox.XLength,shape.BoundBox.YLength,shape.BoundBox.ZLength],files={p.name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in web.iterdir()},scope='Unchanged v6 native 3/5 mm coupons, re-laid on one plate;7 mm excluded; supports and owner compensation still required when slicing')
(out/'requested-fits-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
