"""Mesh print gates, GLB previews and local solid-ASA stiffness review."""
from pathlib import Path
import argparse,hashlib,json,sys
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[3]
SHARED=ROOT/'bench/source/gallery_new_designs_v1/snapshot/bench/source/solder_v12'
sys.path.insert(0,str(SHARED))
import checks

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('id');p.add_argument('--fea',action='store_true');a=p.parse_args()
    d=ROOT/'bench/reviews/canted-hex-keys-v1'/a.id;r=json.loads((d/'report.json').read_text());n=r['prefix'];assets=r['assets']
    if a.fea:
        import fea
        runtime=Path('/home/repro/cache-downloads/peg-cad/squashfs-root/usr/bin')
        fea.GMSH=runtime/'gmsh';fea.CCX=runtime/'ccx';fea.os.cpu_count=lambda:4
        fea.main(d,n)
        result=json.loads((d/(n+'__fea.json')).read_text())
        result['passed']=all(lc['deflection_at_load_mm']<=limit for case in result['cases'] for lc,limit in zip(case['loads'],[1,.5]))
        result['limits']='Linear isotropic solid ASA E=1800 MPa. Printed infill, layer bonds, board compliance, strength and fatigue require physical checks.'
        result['inputs']={k:sha(v) for k,v in {'step':d/assets['installed_step'],'spec':d/(n+'__fea-spec.json'),'solver_script':Path(fea.__file__)}.items()}
        (d/'stiffness.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return
    pr=trimesh.load(d/assets['print_stl'],force='mesh');inv=np.linalg.inv(np.array(r['pose_matrix']).reshape(4,4))
    oh=checks.overhangs(pr,inv,[]);islands=checks.islands(pr,inv)
    bed=(pr.triangles[:,:,2].max(axis=1)<.01)&(pr.face_normals[:,2]<-.9)
    result=dict(watertight=bool(pr.is_watertight),components=len(trimesh.graph.connected_components(pr.face_adjacency,min_len=1,nodes=np.arange(len(pr.faces)),engine="scipy")),positive_volume=bool(pr.volume>0),overhangs=oh,islands=islands,bed_face_mm2=float(pr.area_faces[bed].sum()),bounds_mm=pr.extents.tolist(),inputs={k:sha(d/assets[k]) for k in ['installed_stl','print_stl']})
    result['passed']=result['watertight'] and result['components']==1 and result['positive_volume'] and oh['passed'] and islands['passed'] and result['bed_face_mm2']>100 and bool(np.all(pr.extents[:2]+20<256))
    (d/'print-geometry.json').write_text(json.dumps(result,indent=2)+'\n')
    # Model-viewer uses metres, with Y up and the front of the pegboard toward +Z.
    transform=np.array([[-.001,0,0,0],[0,0,.001,0],[0,.001,0,0],[0,0,0,1]])
    for mode in ['installed','print','loaded']:
        scene=trimesh.Scene()
        m=trimesh.load(d/assets['print_stl' if mode=='print' else 'installed_stl'],force='mesh');m.apply_transform(transform);m.visual.vertex_colors=[68,151,143,255];scene.add_geometry(m,node_name='holder')
        if mode=='loaded':
            t=trimesh.load(d/'seated-keys.stl' if (d/'seated-keys.stl').exists() else d/assets['tool-reference_stl'],force='mesh');t.apply_transform(transform);t.visual.vertex_colors=[195,201,210,255];scene.add_geometry(t,node_name='reference_envelope')
        (d/(mode+'.glb')).write_bytes(scene.export(file_type='glb'))
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
