import FreeCAD,Mesh,json,struct,math
from pathlib import Path
root=Path(__file__).resolve().parents[1];src=root/'bench/reviews/tee-fit-v4-guide40/HX05-fit-v4__left-end__print.stl';mesh=Mesh.Mesh(str(src));points,faces=mesh.Topology
vertices=[];normals=[]
for a,b,c in faces:
 p=[[points[i].x*.001,points[i].z*.001,-points[i].y*.001] for i in (a,b,c)];u=[p[1][i]-p[0][i] for i in range(3)];v=[p[2][i]-p[0][i] for i in range(3)];n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];length=math.sqrt(sum(x*x for x in n));n=[x/length for x in n]
 for q in p:vertices.extend(q);normals.extend(n)
pos=struct.pack('<'+'f'*len(vertices),*vertices);normal=struct.pack('<'+'f'*len(normals),*normals);binary=pos+normal;count=len(vertices)//3
j={'asset':{'version':'2.0','generator':'FreeCAD coupon mesh, geometry-only preview'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'mesh':0,'name':'40 mm minimum shaft guide coupon'}],'meshes':[{'primitives':[{'attributes':{'POSITION':0,'NORMAL':1},'material':0,'mode':4}]}],'materials':[{'pbrMetallicRoughness':{'baseColorFactor':[.12,.55,.50,1],'metallicFactor':0,'roughnessFactor':.7},'doubleSided':False}],'buffers':[{'byteLength':len(binary)}],'bufferViews':[{'buffer':0,'byteOffset':0,'byteLength':len(pos),'target':34962},{'buffer':0,'byteOffset':len(pos),'byteLength':len(normal),'target':34962}],'accessors':[{'bufferView':0,'componentType':5126,'count':count,'type':'VEC3','min':[min(vertices[i::3]) for i in range(3)],'max':[max(vertices[i::3]) for i in range(3)]},{'bufferView':1,'componentType':5126,'count':count,'type':'VEC3'}]}
encoded=json.dumps(j,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4);binary+=b'\0'*((-len(binary))%4)
data=struct.pack('<III',0x46546c67,2,12+8+len(encoded)+8+len(binary))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(binary),0x004e4942)+binary
(root/'docs/gallery/key-fan/fit-v4/coupon.glb').write_bytes(data);print('coupon GLB',len(data),'bytes',count//3,'triangles')
