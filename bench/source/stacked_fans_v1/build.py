"""Native review solids grown around the selected handles. No layout search."""
from pathlib import Path
import sys,os,json,math,gzip,time,hashlib
import numpy as np
import FreeCAD as A,Part,MeshPart
import trimesh
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'final_racks_v1'))
os.environ['HX4S_LAYOUT']='hx04_final.json'
import build_short as H
from layout import layout,PITCH
V=A.Vector
OUT=Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=True)

def v(p):return V(*map(float,p))
def fuse(parts):return parts[0].multiFuse(parts[1:]).removeSplitter() if len(parts)>1 else parts[0]
def hexwire(p,u,b,af):
    side=np.cross(u,b);r=af/math.sqrt(3)
    pts=[v(p+r*(b*math.cos(math.pi/6+k*math.pi/3)+side*math.sin(math.pi/6+k*math.pi/3))) for k in range(6)]
    return Part.makePolygon(pts+[pts[0]])
def capsule(a,b,r):
    d=np.array(b)-a
    return fuse([Part.makeCylinder(r,float(np.linalg.norm(d)),v(a),v(d)),Part.makeSphere(r,v(a)),Part.makeSphere(r,v(b))])
def tool_shapes(t):
    p,u,b,top=map(np.array,(t['tip'],t['axis'],t['bar_axis'],t['top']))
    shaft=Part.makeCylinder(t['p2p']/2,t['overall']-9,v(p),v(u)) if 'p2p' in t else Part.Face(hexwire(p,u,b,t['af'])).extrude(v(top-p))
    grip=capsule(top-b*(t['bar']/2-9),top+b*(t['bar']/2-9),9.)
    return shaft,grip

def ring(p,u,r,n=20):return H.ring(p,u,r,n)

def build(rack):
    ident=rack['id'];dst=OUT/ident;dst.mkdir(exist_ok=True);ts=rack['tools'];print(ident,'start',flush=True)
    top_z=0.
    bottom_z=min(t['tip'][2]-t['outer_radius']-3 for t in ts)-3.
    half=math.ceil(max(abs(t[k][0])+t['outer_radius']+6 for t in ts for k in ('tip','mouth')))
    receiver,info=H.receiver_grid(-half,half,bottom_z)
    receiver=receiver.mirror(V(0,0,0),V(1,0,0));receiver.translate(V(0,0,top_z))
    bodies=[receiver];cutters=[];guide_probes=[];cavities=[]
    shafts=[];grips=[]
    for t in ts:
        p,u,b,m=map(np.array,(t['tip'],t['axis'],t['bar_axis'],t['mouth']));R=t['outer_radius'];D=t['burial']
        # Circular wall + a direct full-length web to the rear plate.
        ends=np.vstack([ring(p-u*3,u,R),ring(m,u,R)])
        rear=ends.copy();rear[:,1]=5.0
        support=H.hull_solid(np.vstack([ends,rear]));bodies.append(support)
        if 'p2p' in t:
            radius=(t['p2p']+.38)/2
            bore=Part.makeCylinder(radius,t['overall']+D,v(p),v(u))
            lead=Part.makeCone(radius,radius+1.5,3.,v(m-u*3),v(u))
            gp=Part.makeCylinder(radius-.01,t['guide']-.02,v(p+u*.01),v(u))
        else:
            bore=Part.Face(hexwire(p,u,b,t['af']+.38)).extrude(v(u*(t['overall']+D)))
            lead=Part.makeLoft([hexwire(m-u*3,u,b,t['af']+.38),hexwire(m,u,b,t['af']+.38+3)],True,True)
            gp=Part.Face(hexwire(p+u*.01,u,b,t['af']+.36)).extrude(v(u*(t['guide']-.02)))
        # All vent material removal stays below the square seating plane.
        elbow=p-u*1.5
        vent1=Part.makeCylinder(.5,1.56,v(p+u*.03),v(-u))
        vent2=Part.makeCylinder(.5,R+8,v(elbow),v(b))
        cutters.extend([bore,lead,vent1,vent2]);guide_probes.append(gp)
        cavities.append(bore.fuse(lead))
        shaft,grip=tool_shapes(t);shafts.append(shaft);grips.append(grip)
    cavity_gaps=[]
    for i,a in enumerate(cavities):
        for j,bore_b in enumerate(cavities[:i]):
            cavity_gaps.append(dict(a=ts[i]['name'],b=ts[j]['name'],gap_mm=a.distToShape(bore_b)[0],overlap_mm3=a.common(bore_b).Volume))
    body=fuse(bodies);print(ident,'support union',body.isValid(),flush=True)
    for i in range(0,len(cutters),4):
        raw=body.cut(fuse(cutters[i:i+4]))
        if not raw.isValid():
            raw=body
            for cutter in cutters[i:i+4]:raw=raw.cut(cutter)
        if not raw.isValid():raw=body.cut(fuse(cutters[i:i+4]),1e-6)
        if not raw.isValid():raw.fix(1e-7,1e-7,1e-6)
        reduced=raw.removeSplitter()
        body=reduced if reduced.isValid() else raw
        print(ident,'bore',i//4,'valid',body.isValid(),'solids',len(body.Solids),flush=True)
    assert body.isValid() and len(body.Solids)==1,(ident,'native body')
    assert all(body.common(g).Volume<1e-6 for g in guide_probes),(ident,'guide blocked')
    tool=Part.makeCompound(shafts+grips)
    stored=body.common(tool).Volume
    print(ident,'stored overlap',stored,flush=True)
    assert stored<1e-5,(ident,'stored tool/body overlap',stored)
    body.exportStep(str(dst/'installed.step'))
    doc=A.newDocument(ident);feat=doc.addObject('PartDesign::Feature','Holder');feat.Label='Spiral fan render study';feat.Shape=body;doc.recompute();doc.saveAs(str(dst/'holder.FCStd'));A.closeDocument(doc.Name)
    body.exportBrep(str(dst/'body.brep'));Part.makeCompound(shafts).exportBrep(str(dst/'shafts.brep'));Part.makeCompound(grips).exportBrep(str(dst/'grips.brep'))
    mesh=MeshPart.meshFromShape(Shape=body,LinearDeflection=.10,AngularDeflection=.25,Relative=False)
    mesh.write(str(dst/'installed.stl'))
    record=dict(layout_sha256=hashlib.sha256((OUT.parent/'layout.json').read_bytes()).hexdigest(),id=ident,valid=body.isValid(),solids=len(body.Solids),volume=body.Volume,stored_overlap_mm3=stored,mount=info,peg_top_z=top_z,bounds=[body.BoundBox.XMin,body.BoundBox.XMax,body.BoundBox.YMin,body.BoundBox.YMax,body.BoundBox.ZMin,body.BoundBox.ZMax],tools=ts,cavity_gaps=cavity_gaps)
    (dst/'native.json').write_text(json.dumps(record,indent=2)+'\n')
    return body,shafts,grips,record

# X right / Z up / Y toward viewer -> glTF X right / Y up / Z front.
M=np.array([[.001,0,0,0],[0,0,.001,0],[0,.001,0,0],[0,0,0,1]])
def mesh(s):
    q=MeshPart.meshFromShape(Shape=s,LinearDeflection=.13,AngularDeflection=.32,Relative=False);p,f=q.Topology
    m=trimesh.Trimesh([[v.x,v.y,v.z] for v in p],f,process=True)
    if len(m.faces)>16000:m=m.simplify_quadric_decimation(face_count=16000)
    m.apply_transform(M);return m

def add(scene,shape,color,name,z=0):
    m=mesh(shape);m.apply_translation([0,z*.001,0]);m.visual.vertex_colors=color;scene.add_geometry(m,node_name=name)

def write(scene,name):
    blob=scene.export(file_type='glb');(OUT/(name+'.glb.gz')).write_bytes(gzip.compress(blob,9,mtime=0))

if __name__=='__main__':
    data=json.loads((OUT.parent/'layout.json').read_text()); racks=data['racks']; stack=trimesh.Scene();empty=trimesh.Scene();records=[]
    colors=[[50,146,133,255],[67,111,175,255],[170,103,61,255]]
    for rack,color in zip(racks,colors):
        dst=OUT/rack['id']
        if (dst/'native.json').exists():
            record=json.loads((dst/'native.json').read_text());assert record['layout_sha256']==hashlib.sha256((OUT.parent/'layout.json').read_bytes()).hexdigest(), 'Stale native layout';body=Part.Shape();body.read(str(dst/'body.brep'))
            sh=Part.Shape();sh.read(str(dst/'shafts.brep'));shafts=[sh]
            gr=Part.Shape();gr.read(str(dst/'grips.brep'));grips=[gr]
        else:body,shafts,grips,record=build(rack)
        records.append(record)
        scene=trimesh.Scene();add(scene,body,color,'holder');add(scene,Part.makeCompound(shafts),[130,142,153,255],'shafts');add(scene,Part.makeCompound(grips),[61,67,75,255],'grips');write(scene,rack['id'])
        add(stack,body,color,rack['id']+'_holder',rack['z']);add(stack,Part.makeCompound(shafts),[130,142,153,255],rack['id']+'_shafts',rack['z']);add(stack,Part.makeCompound(grips),[61,67,75,255],rack['id']+'_grips',rack['z']);add(empty,body,color,rack['id'],rack['z'])
    write(stack,'stack');write(empty,'empty-stack')
    (OUT/'native.json').write_text(json.dumps(dict(racks=records,pitch=data['pitch']),indent=2)+'\n')
    print('DONE',flush=True)
