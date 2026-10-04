"""V5 exact-input full-mesh path, installation and print screens; no dynamics.

All four tools move independently through one reversible path with three neighbors.
Lift/left steps <=0.25 mm, arc 1 degree (<=0.112 mm), outward0.5 mm.
A sampled screen is not a continuous certificate or measured capture rate.
"""
from pathlib import Path
import argparse,hashlib,json,math,sys
import numpy as np
import trimesh
import manifold3d as M
from scipy.spatial import cKDTree
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'solder_v12'))
import checks as C
BASE=HERE.parents[1]/'reviews/tweezer-inward20-v4'
TOL=1e-8

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def solid(m):
    s=M.Manifold(M.Mesh64(np.asarray(m.vertices,dtype=np.float64),np.asarray(m.faces,dtype=np.uint64)))
    assert s.status()==M.Error.NoError,s.status()
    return s

def path(c):
    g=c['guide'];r=g['radius_mm'];lift=c['removal']['lift_mm'];cs=np.cos(np.radians(20));high=lift+r/cs;direction=np.array(c['removal']['out_direction'])
    return [('lift',[[0,0,float(z)] for z in np.arange(0,lift+.001,.25)]),
        ('up-left arc',[[r*(1-np.sin(t)),0,lift+r*np.cos(t)/cs] for t in np.linspace(np.pi/2,0,91)]),
        ('open-mouth clearance',[[x,0,high] for x in np.linspace(r,r+2,9)]),
        ('outward',[direction*s+[r+2,0,high] for s in np.arange(0,135.001,.5)])]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('build',type=Path);d=p.parse_args().build.resolve()
    c=json.loads((d/'candidate.json').read_text())['cases'][0];old=json.loads((BASE/'candidate.json').read_text())['cases'][0];name=c['name']
    files=[f'{name}__installed.stl',c['print_file'],c['wedge_print']]+c['tools']+c['wedges']+[f'guide-{k+1}.stl' for k in range(4)]
    meshes={f:trimesh.load(d/f,force='mesh') for f in files};ss={f:solid(m) for f,m in meshes.items()}
    body=meshes[f'{name}__installed.stl'];bs=ss[f'{name}__installed.stl'];pr=meshes[c['print_file']]
    mat=np.array(c['pose_matrix']).reshape(4,4);inv=np.linalg.inv(mat);moved=trimesh.transform_points(body.vertices,mat)
    pose_error=float(np.max(np.abs(np.array([moved.min(0),moved.max(0)])-pr.bounds)))
    board=solid(trimesh.creation.box(extents=[300,3.94,600],transform=trimesh.transformations.translation_matrix([0,.15-3.94/2,0])))
    fixed=M.Manifold.batch_boolean([bs,board]+[ss[f] for f in c['wedges']],M.OpType.Add)
    health=[dict(file=f,watertight=bool(m.is_watertight),bodies=int(m.body_count)) for f,m in meshes.items()]
    reports=[];guide_gaps=[]
    for k,f in enumerate(c['tools']):
        tool=ss[f];mesh=meshes[f];occupied=M.Manifold.batch_boolean([fixed]+[ss[t] for j,t in enumerate(c['tools']) if j!=k],M.OpType.Add)
        before=trimesh.load(BASE/old['tools'][k],force='mesh');shift=[0,0,-(c['tray_pitch_vertical_mm']-23)*k]
        translated=before.vertices+shift
        err=float(max(cKDTree(translated).query(mesh.vertices)[0].max(),cKDTree(mesh.vertices).query(translated)[0].max()))
        assert len(mesh.faces)==len(before.faces),'Translation changed face count'
        # Match vertex identities geometrically, then compare complete face incidence
        # independent of STL facet order or cyclic triangle vertex order.
        mapping=cKDTree(translated).query(mesh.vertices)[1]
        actual=np.sort(mapping[mesh.faces],axis=1);expected=np.sort(before.faces,axis=1)
        actual=actual[np.lexsort(actual.T)];expected=expected[np.lexsort(expected.T)]
        topology_equal=bool(np.array_equal(actual,expected))
        assert topology_equal,'Translation changed triangle connectivity'
        phases=[]
        for phase,offsets in path(c):
            worst=0.;at=None
            for off in offsets:
                v=abs((occupied^tool.translate(list(map(float,off)))).volume())
                if v>worst:worst=v;at=list(map(float,off))
            row=dict(phase=phase,samples=len(offsets),max_intersection_mm3=worst,worst_offset_mm=at,passed=worst<TOL);phases.append(row)
            print('Tray',k+1,phase,worst,flush=True)
        tip=tool.trim_by_plane([0,-1,0],-float(mesh.bounds[0,1]+15));tipworst=max(abs((bs^tip.translate([0,float(y),0])).volume()) for y in np.linspace(-19.05,0,40))
        tipgap=tip.min_gap(bs,100)
        reports.append(dict(tray=k+1,file=f,stored_translation_from_v4_mm=shift,translation_bidirectional_vertex_error_mm=err,translation_triangle_connectivity_equal=topology_equal,
            phases=phases,plate_tip_gap_mm=float(mesh.bounds[0,1]-5.55),tip_15mm_complete_body_gap_mm=tipgap,
            tip_extension_space_max_intersection_mm3=tipworst,tip_extension_samples=40,
            passed=bool(all(r['passed'] for r in phases) and err<2e-5 and tipworst<TOL and abs(mesh.bounds[0,1]-28.6)<2e-5)))
    # Per-station guide contact diagnostics are supplied by inward20_v5_guide_check.py.
    waypath=HERE.parents[1]/'reference/conformal_motion_results.json';way=np.array([[r['y'],r['z'],r['theta_deg']] for r in json.loads(waypath.read_text())['removal_poses']])
    front=trimesh.load(d/f'{name}__front-material.stl',force='mesh');yz=front.vertices[:,1:];rho=np.linalg.norm(yz,axis=1).max();worst=1e9;at=None;nposes=0
    for a,b in zip(way[:-1],way[1:]):
        n=max(1,math.ceil((np.linalg.norm(b[:2]-a[:2])+math.radians(abs(b[2]-a[2]))*rho)/.05))
        for f in np.linspace(0,1,n+1):
            ty,tz,theta=a+(b-a)*f;rad=math.radians(theta);gap=float(np.min(ty+yz[:,0]*math.cos(rad)-yz[:,1]*math.sin(rad)))
            if gap<worst:worst=gap;at=[ty,tz,theta]
            nposes+=1
    installation=dict(min_front_plane_clearance_mm=worst,at=at,poses=nposes,maximum_vertex_motion_mm=.05,surface_deflection_mm=.005,passed=worst>=-.006,scope='Entire new bare front body versus board plane along reference installation path. Rear peg/hoop interference unchanged; no physical fit certification.')
    overhang=C.overhangs(pr,inv,[]);islands=C.islands(pr,inv)
    # Explicit supported roof region; NOT a bridge exception or support-free pass.
    supported=[]
    for f in overhang['features']:
        lo,hi=np.array(f['installed_bbox']);ok=bool(lo[0]>=-21 and hi[0]<=-17 and lo[1]>=100 and hi[1]<=136 and lo[2]>=10 and hi[2]<=27)
        supported.append(dict(feature=f,within_top_guide_support_region=ok))
    print_screen=dict(raw_overhangs=overhang,islands=islands,pose_error_mm=pose_error,
        supported_guide_features=supported,requires_slicer_support_verification=bool(supported),
        support_plan_passed=all(r['within_top_guide_support_region'] for r in supported),scope='Organic support at pegs and the open accessible top guide. Support origin and actual extrusion coverage are separate required slicer checks.')
    wp=meshes[c['wedge_print']];wprint=dict(overhangs=C.overhangs(wp,None,[]),islands=C.islands(wp,None),bounds_mm=wp.bounds.tolist())
    immutable=[]
    for e in c['immutable_copies']:
        assert sha(e['source'])==sha(d/e['target'])==e['sha256'];immutable.append(e)
    passed=bool(all(h['watertight'] and h['bodies']==1 for h in health) and all(r['passed'] for r in reports) and installation['passed'] and pose_error<.001 and islands['passed'] and print_screen['support_plan_passed'] and wprint['overhangs']['passed'] and wprint['islands']['passed'] and c['peg_symmetric_difference_mm3']<1e-6)
    used=[d/'candidate.json',Path(__file__),Path(C.__file__),waypath,BASE/'candidate.json']+[BASE/f for f in old['tools']]+list(d.glob('*.stl'))
    out=dict(passed=passed,method=__doc__,collision_tolerance_mm3=TOL,board_included=True,health=health,tools=reports,guide_contact_report='guide-contacts.json',
        installation_front_body=installation,print_screen=print_screen,wedge_print=wprint,immutable_copies=immutable,inputs={str(p):sha(p) for p in used},
        limitations=['Reference mesh only; actual tools, fingers, guide capture and print texture unqualified','Free settle from above fin; no arm is forced laterally across fin','Supported geometry requires exact final toolpath review','Sampled nominal path, not continuous motion proof; no dynamic or friction simulation'])
    (d/'checks.json').write_text(json.dumps(out,indent=2)+'\n');print('CHECKS',passed,flush=True)
    if not passed:raise SystemExit(1)
if __name__=='__main__':main()
