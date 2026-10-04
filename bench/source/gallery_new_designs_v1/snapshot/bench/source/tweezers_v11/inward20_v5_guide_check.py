"""Per-station guide gaps/contact locations on actual clipped guide meshes.

Mesh/mesh minima are separate from closest sampled robust-arm vertex locations.
These are nominal CAD diagnostics, not a validated printed fit or capture test.
"""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
import trimesh
from inward20_v5_check import solid

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('build',type=Path);d=p.parse_args().build.resolve();c=json.loads((d/'candidate.json').read_text())['cases'][0]
    files=[d/'candidate.json',Path(__file__),Path(__file__).with_name('inward20_v5_check.py')]+[d/f for f in c['tools']]+[d/f'guide-{k+1}.stl' for k in range(4)]
    before={str(f):sha(f) for f in files};rows=[];cs=np.cos(np.radians(20));sn=np.sin(np.radians(20))
    for k,f in enumerate(c['tools']):
        tm=trimesh.load(d/f,force='mesh');gm=trimesh.load(d/f'guide-{k+1}.stl',force='mesh');ts=solid(tm);gs=solid(gm)
        pts=tm.vertices;local=pts+[0,0,c['tray_pitch_vertical_mm']*k];vv=-sn*local[:,1]+cs*local[:,2]
        mask=(pts[:,1]>=90)&(pts[:,1]<=138)&(pts[:,0]<-13)&(vv>=vv.max()-3)
        arm=pts[mask];assert len(arm)>0
        # Deterministic bounded sample retains the robust upper edge near contact.
        arm=arm[::max(1,len(arm)//1200)];samples=[]
        for deg in [0,15,30,45,60,75,90]:
            a=np.radians(deg);r=c['guide']['radius_mm'];off=np.array([r*(1-np.sin(a)),0,6.75+r*np.cos(a)/cs])
            q,dist,face=trimesh.proximity.closest_point(gm,arm+off);i=int(np.argmin(dist))
            row=dict(arc_degrees=deg,offset_mm=off.tolist(),mesh_min_gap_mm=ts.translate(off).min_gap(gs,10),
                nearest_sampled_arm_vertex_before_motion_mm=arm[i].tolist(),nearest_sampled_arm_vertex_moved_mm=(arm[i]+off).tolist(),nearest_guide_point_mm=q[i].tolist(),sampled_vertex_gap_mm=float(dist[i]),
                vertex_distance_from_tip_Y_mm=float(arm[i,1]-tm.bounds[0,1]),mesh_intersection_mm3=abs((ts.translate(off)^gs).volume()))
            samples.append(row)
        rows.append(dict(tray=k+1,guide_file=f'guide-{k+1}.stl',sampled_arm_vertices=len(arm),samples=samples))
        print('Guide',k+1,[(s['arc_degrees'],round(s['mesh_min_gap_mm'],4)) for s in samples],flush=True)
    assert before=={str(f):sha(f) for f in files},'Changed diagnostic inputs'
    report=dict(passed=all(s['mesh_intersection_mm3']<1e-8 for r in rows for s in r['samples']),method=__doc__,
        subset='Stored Y90..138 mm; X<-13 mm; normal-to-20-degree-slope V within3 mm of tool maximum; at most approximately1200 deterministic vertices. Fragile tip is excluded.',
        stations=rows,inputs=before,limits=['Nearest sampled vertex is not necessarily the exact mesh/mesh nearest point','Mesh minima may occur between vertices; use separate min-gap field','Open underside relieves before final6.75 mm downward settle','A constrained clear route does not prove passive self-guiding or user success'])
    (d/'guide-contacts.json').write_text(json.dumps(report,indent=2)+'\n')
    if not report['passed']:raise SystemExit(1)
if __name__=='__main__':main()
