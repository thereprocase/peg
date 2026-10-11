"""Export native model evidence and previews from saved parametric documents."""
from pathlib import Path
import sys,json,hashlib,importlib.util
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'bench/source/green_fan_v1'))
spec=importlib.util.spec_from_file_location('green_native',ROOT/'bench/source/green_fan_v1/build.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
B=Path(sys.argv[1]);data=json.loads((B.parent/'layout.json').read_text());records=[];stack=h.trimesh.Scene()
colors=[[50,146,133,255],[67,111,175,255],[170,103,61,255]]
for rack,color in zip(data['racks'],colors):
 ident=rack['id'];dst=B/ident
 body=h.Part.Shape();body.read(str(dst/'body.brep'))
 shafts=[];grips=[];cavities=[]
 for t in rack['tools']:
  sh,gr=h.tool_shapes(t);shafts.append(sh);grips.append(gr)
  p,u,b,m=map(np.array,(t['tip'],t['axis'],t['bar_axis'],t['mouth']))
  if 'p2p' in t:probe=h.Part.makeCylinder((t['p2p']+.36)/2,t['guide']-.02,h.v(p+u*.01),h.v(u))
  else:probe=h.Part.Face(h.hexwire(p+u*.01,u,b,t['af']+.36)).extrude(h.v(u*(t['guide']-.02)))
  assert body.common(probe).Volume<1e-5,(ident,t['name'],'blocked guide')
  cavities.append(probe)
 tool=h.Part.makeCompound(shafts+grips);stored=body.common(tool).Volume
 assert body.isValid() and len(body.Solids)==1 and stored<1e-5,(ident,stored)
 gaps=[]
 for i,a in enumerate(cavities):
  for j,b in enumerate(cavities[:i]):
   vol=a.common(b).Volume;assert vol<1e-5
   gaps.append(dict(a=rack['tools'][i]['name'],b=rack['tools'][j]['name'],gap_mm=a.distToShape(b)[0],overlap_mm3=vol))
 h.Part.makeCompound(shafts).exportBrep(str(dst/'shafts.brep'));h.Part.makeCompound(grips).exportBrep(str(dst/'grips.brep'))
 h.MeshPart.meshFromShape(Shape=body,LinearDeflection=.1,AngularDeflection=.25,Relative=False).write(str(dst/'installed.stl'))
 bb=body.optimalBoundingBox()
 record=dict(id=ident,set=rack['set'],valid=True,solids=1,volume=body.Volume,stored_overlap_mm3=stored,bounds=[bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax],tools=rack['tools'],cavity_gaps=gaps,layout_sha256=hashlib.sha256((B.parent/'layout.json').read_bytes()).hexdigest(),body_recipe='approved-green-v3' if ident=='HX05C' else 'matched-green-v1')
 (dst/'native.json').write_text(json.dumps(record,indent=2)+'\n');records.append(record)
 scene=h.trimesh.Scene();h.add(scene,body,color,'holder');h.add(scene,h.Part.makeCompound(shafts),[130,142,153,255],'shafts');h.add(scene,h.Part.makeCompound(grips),[61,67,75,255],'grips');h.write(scene,ident)
 scene=h.trimesh.Scene();h.add(scene,body,color,'holder');h.write(scene,ident+'-empty')
 h.add(stack,body,color,ident+'_holder',rack['z']);h.add(stack,h.Part.makeCompound(shafts),[130,142,153,255],ident+'_shafts',rack['z']);h.add(stack,h.Part.makeCompound(grips),[61,67,75,255],ident+'_grips',rack['z'])
 print(ident,'native evidence and meshes',flush=True)
h.write(stack,'stack');(B/'native.json').write_text(json.dumps(dict(racks=records,pitches_mm=data['pitches_mm']),indent=2)+'\n')
