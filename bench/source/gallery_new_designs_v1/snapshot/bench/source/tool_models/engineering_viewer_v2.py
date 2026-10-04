"""Package smooth component-coloured CAD review geometry; physics Python runtime.

Crease-aware vertex normals preserve ground planes. All CAD STL triangles remain.
Original scans are separate reference meshes and never supply model surfaces.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import numpy as np
from scipy.sparse import csr_matrix
import trimesh
from engineering_reference_v2 import source


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def smooth_crease(m):
    v=np.asarray(m.vertices);f=np.asarray(m.faces);fn=np.asarray(m.face_normals);area=np.asarray(m.area_faces)
    ids=np.repeat(np.arange(len(f)),3)
    inc=csr_matrix((np.ones(f.size),(f.ravel(),ids)),shape=(len(v),len(f)))
    maxcount=int(np.diff(inc.indptr).max());adj=np.full((len(v),maxcount),len(f),dtype=np.int32)
    for i in range(len(v)):adj[i,:inc.indptr[i+1]-inc.indptr[i]]=inc.indices[inc.indptr[i]:inc.indptr[i+1]]
    fn2=np.vstack([fn,[0,0,0]]);weighted=np.vstack([fn*area[:,None],[0,0,0]])
    ns=np.zeros((len(f),3,3))
    for start in range(0,len(f),10000):
        stop=min(start+10000,len(f));a=adj[f[start:stop]]
        good=np.einsum('fcaj,fj->fca',fn2[a],fn[start:stop])>.8
        n=(weighted[a]*good[...,None]).sum(axis=2);n/=np.maximum(np.linalg.norm(n,axis=2),1e-20)[...,None];ns[start:stop]=n
    key=np.c_[f.ravel(),np.round(ns.reshape(-1,3),6)]
    _,where,inv=np.unique(key,axis=0,return_index=True,return_inverse=True)
    return v[f.ravel()[where]],ns.reshape(-1,3)[where],inv.reshape(-1,3)


def coil_pose(parameters, coordinates, angle):
    a=np.array(parameters['coil_a'],float);b=np.array(parameters['coil_b'],float)
    theta=np.radians(parameters['opening_sign']*angle)
    rot=np.array([[np.cos(theta),-np.sin(theta),0],[np.sin(theta),np.cos(theta),0],[0,0,1]])
    original_h=np.linalg.norm(b-a);b=b@rot.T;d=b-a;h=np.linalg.norm(d);axis=d/h
    e1=np.cross([0,0,1],axis);e1/=np.linalg.norm(e1);e2=np.cross(axis,e1)
    turns=parameters['coil_turns']*2*np.pi
    radius=np.sqrt((turns*parameters['coil_radius'])**2+original_h**2-h**2)/turns
    u=coordinates[:,0];phi=coordinates[:,1];t=turns*u
    radial=np.cos(t)[:,None]*e1+np.sin(t)[:,None]*e2
    tangent=d+radius*turns*(-np.sin(t)[:,None]*e1+np.cos(t)[:,None]*e2)
    tangent/=np.linalg.norm(tangent,axis=1)[:,None];binormal=np.cross(tangent,radial)
    n=radial*np.cos(phi)[:,None]+binormal*np.sin(phi)[:,None]
    v=a+u[:,None]*d+radius*radial+parameters['wire_radius']*n
    cap=np.abs(coordinates[:,2])>.5
    v[cap]=a+u[cap,None]*d+radius*radial[cap];n[cap]=tangent[cap]*coordinates[cap,2,None]
    return v,n


def write_glb(scene,path,sign,coil_data=None):
    # Add a native glTF rotation animation to the moving-assembly node.
    blob=scene.export(file_type='glb');jlen=struct.unpack_from('<I',blob,12)[0]
    j=json.loads(blob[20:20+jlen]);offset=20+jlen
    length=struct.unpack_from('<I',blob,offset)[0];binary=bytearray(blob[offset+8:offset+8+length])
    idx=next(i for i,n in enumerate(j['nodes']) if n.get('name')=='moving-assembly')
    node=j['nodes'][idx];node.pop('matrix',None);node['rotation']=[0,0,0,1]
    def accessor(arr,typ):
        while len(binary)%4:binary.append(0)
        a=np.asarray(arr,dtype='<f4');off=len(binary);binary.extend(a.tobytes());vi=len(j['bufferViews'])
        j['bufferViews'].append(dict(buffer=0,byteOffset=off,byteLength=a.nbytes));ai=len(j['accessors'])
        item=dict(bufferView=vi,componentType=5126,count=len(a),type=typ)
        if typ=='SCALAR':item.update(min=[float(a.min())],max=[float(a.max())])
        elif typ=='VEC3':item.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
        j['accessors'].append(item);return ai
    t=accessor([0,1,2],'SCALAR');theta=np.radians(sign*20)/2
    q=accessor([[0,0,0,1],[0,0,np.sin(theta),np.cos(theta)],[0,0,0,1]],'VEC4')
    j['animations']=[dict(name='Illustrative hinge opening; released latch and geometric coil motion',samplers=[dict(input=t,output=q,interpolation='LINEAR')],channels=[dict(sampler=0,target=dict(node=idx,path='rotation'))])]
    if coil_data is not None:
        params,coords=coil_data;v0,n0=coil_pose(params,coords,0)
        coilnode=next(i for i,node in enumerate(j['nodes']) if node.get('name')=='opening_coil')
        mesh=j['meshes'][j['nodes'][coilnode]['mesh']];primitive=mesh['primitives'][0];targets=[]
        for angle in [5,10,15,20]:
            v,n=coil_pose(params,coords,angle)
            targets.append(dict(POSITION=accessor((v-v0)/1000,'VEC3'),NORMAL=accessor(n-n0,'VEC3')))
        primitive['targets']=targets;mesh['weights']=[0,0,0,0]
        tcoil=accessor(np.linspace(0,2,9),'SCALAR')
        weights=np.array([[0,0,0,0],[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1],[0,0,1,0],[0,1,0,0],[1,0,0,0],[0,0,0,0]],dtype=float)
        aw=accessor(weights.ravel(),'SCALAR');j['animations'][0]['samplers'].append(dict(input=tcoil,output=aw,interpolation='LINEAR'))
        j['animations'][0]['channels'].append(dict(sampler=1,target=dict(node=coilnode,path='weights')))
    j['buffers'][0]['byteLength']=len(binary);encoded=json.dumps(j,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4);binary+=b'\0'*((-len(binary))%4)
    total=12+8+len(encoded)+8+len(binary)
    path.write_bytes(struct.pack('<4sII',b'glTF',2,total)+struct.pack('<I4s',len(encoded),b'JSON')+encoded+struct.pack('<I4s',len(binary),b'BIN\0')+binary)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    models=[];inputs={}
    for ident in ['knipex','klein']:
        d=a.root/(ident+'-engineering-model-v2');meta=json.loads((d/'cad.json').read_text());desc=[]
        coil_data=None
        scene=trimesh.Scene();scene.graph.update(frame_to='moving-assembly',matrix=np.eye(4))
        def pack(name,v,n,f,uv,role,color,metal=False):
            file=f'{ident}-{name}.bin';buf=np.c_[v,n,uv,np.ones(len(v))].astype('<f4')
            (a.output/file).write_bytes(buf.tobytes()+np.asarray(f,dtype='<u4').tobytes())
            desc.append(dict(file=file,vertices=len(v),indices=int(np.asarray(f).size),role=role,color=color,metal=metal))
        for part in meta['parts']:
            src=d/(part['name']+'.stl');m=trimesh.load_mesh(src,process=True);inputs[str(src)]=sha(src)
            v,n,f=smooth_crease(m);role=part['role'];color=part['color'];metal='grip' not in part['name']
            if role=='coil':
                # Compact procedural round-wire helix; analytical deformation in shader.
                nu,nv=660,16
                pv=np.array([[i/nu,2*np.pi*j/nv,0] for i in range(nu+1) for j in range(nv)])
                pf=[]
                for i in range(nu):
                    for j in range(nv):
                        a0=i*nv+j;b0=i*nv+(j+1)%nv;c0=(i+1)*nv+j;d0=(i+1)*nv+(j+1)%nv
                        pf.extend([[a0,c0,b0],[b0,c0,d0]])
                start=len(pv);pv=np.vstack([pv,[0,0,-1],[1,0,1]])
                for j in range(nv):pf.extend([[start,j,(j+1)%nv],[start+1,nu*nv+(j+1)%nv,nu*nv+j]])
                pack(part['name'],pv,np.zeros_like(pv),np.array(pf),np.zeros((len(pv),2)),role,color,metal)
                coil_data=(meta['parameters'],pv)
                v,n=coil_pose(meta['parameters'],pv,0);f=np.array(pf)
            else:pack(part['name'],v,n,f,np.zeros((len(v),2)),role,color,metal)
            display=trimesh.Trimesh(v/1000,f,vertex_normals=n,process=False)
            display.visual=trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
                name=part['name'],baseColorFactor=[int(c*255) for c in color]+[255],metallicFactor=.75 if metal else 0,roughnessFactor=.3 if metal else .68))
            scene.add_geometry(display,node_name=part['name'],geom_name=part['name'],parent_node_name='moving-assembly' if role=='moving' else 'world')
        write_glb(scene,d/'articulated.glb',meta['parameters']['opening_sign'],coil_data)
        raw,faces,uv,labels,texture,registration=source(ident)
        source_mesh=trimesh.Trimesh(raw,faces,process=False);n=np.asarray(source_mesh.vertex_normals)
        pack('scan-reference',raw,n,faces,uv,'source',[1,1,1])
        shutil.copyfile(texture,a.output/(ident+'-source.jpg'))
        models.append(dict(id=ident,title=meta['title'],caliper_mm=meta['anchor_mm'],bounds=meta['overall_bounds'],
            opening_sign=meta['parameters']['opening_sign'],texture=ident+'-source.jpg',meshes=desc,
            note='Clean representative CAD. Owner caliper anchors length; profiles and hidden construction are engineering estimates. Opening is illustrative, not a measured stop.'+(' Latch is released; coil motion is illustrative.' if ident=='klein' else ''),
            cad_download=f'{ident}-editable.FCStd',glb_download=f'{ident}-articulated.glb'))
        shutil.copyfile(d/'editable.FCStd',a.output/f'{ident}-editable.FCStd');shutil.copyfile(d/'articulated.glb',a.output/f'{ident}-articulated.glb')
        for path in [d/'cad.json',Path(registration['source']),Path(registration['trace_metadata']),texture]:inputs[str(path)]=sha(path)
    (a.output/'models.json').write_text(json.dumps(models,indent=2)+'\n')
    shutil.copyfile(Path(__file__).with_suffix('.html'),a.output/'index.html')
    for path in [Path(__file__),Path(__file__).with_suffix('.html'),Path(__file__).with_name('engineering_reference_v2.py')]:inputs[str(path)]=sha(path)
    (a.output/'viewer-build.json').write_text(json.dumps(dict(inputs=inputs,geometry='CAD STL triangles with crease-aware normals; separate procedural round-wire helix in WebGL follows changing endpoints at constant centerline length. Original scan reference separate. Mobile WebGL2, no CDN.',glb='Native hinge rotation plus coil morphs at 5-degree samples; geometric deformation only, no spring-force simulation. CAD coil is a C2 helix approximation; display helix is analytical.',outputs={p.name:sha(p) for p in a.output.iterdir() if p.is_file() and p.name not in ['viewer-build.json','BUILD.json','NOTES.md']}),indent=2)+'\n')

if __name__=='__main__':main()
