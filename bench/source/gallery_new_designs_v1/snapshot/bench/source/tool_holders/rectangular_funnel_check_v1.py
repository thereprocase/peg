"""Nominal edge-on placement and sampled vertical pickup, without fit optimization."""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
import trimesh
import manifold3d as M
from scipy.spatial.transform import Rotation
B=np.array([[0,0,1],[0,-1,0],[1,0,0]])
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def solid(m):
 s=M.Manifold(M.Mesh64(np.asarray(m.vertices,dtype=float),np.asarray(m.faces,dtype=np.uint64)))
 assert s.status()==M.Error.NoError
 return s
def hardware(n):return any(x in n for x in ['latch','coil','spring','rivet','pin','limiter'])
def main():
 p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args();d=a.directory;c=json.loads((d/'candidate.json').read_text());bodymesh=trimesh.load_mesh(d/(c['name']+'__installed.stl'));body=solid(bodymesh);poses=[];results=[];inputs=[Path(__file__),d/'candidate.json',d/(c['name']+'__installed.stl')]
 for ident in ['knipex','klein']:
  td=Path('bench/reviews')/(ident+'-engineering-model-v2');meta=json.loads((td/'cad.json').read_text());inputs.append(td/'cad.json')
  for angle in [0,10]:
   turn=Rotation.from_euler('z',meta['parameters']['opening_sign']*angle,degrees=True).as_matrix()
   basis=B@Rotation.from_euler('z',-meta['parameters']['opening_sign']*angle/2,degrees=True).as_matrix();parts=[]
   for part in meta['parts']:
    path=td/(f'coil-open-{angle}.stl' if part['role']=='coil' and angle else part['name']+'.stl');inputs.append(path)
    m=trimesh.load_mesh(path);m.vertices=np.asarray(m.vertices)@(basis@(turn if part['role']=='moving' else np.eye(3))).T
    parts.append((part,m,solid(m)))
   allv=np.vstack([m.vertices for _,m,_ in parts]);offset=np.array([-(allv[:,0].min()+allv[:,0].max())/2,48.,0.])
   union=M.Manifold.batch_boolean([s for _,_,s in parts],M.OpType.Add)
   def hit(z):return abs((body^union.translate((offset+[0,0,z]).tolist())).volume())
   hi=150.
   for z in np.arange(148,-150,-2.):
    if hit(z)>1e-6:lo=float(z);break
    hi=float(z)
   else:raise RuntimeError('No seating contact')
   for _ in range(23):
    mid=(lo+hi)/2
    if hit(mid)>1e-6:lo=mid
    else:hi=mid
   offset[2]=hi+.03;vertices=allv+offset;minimum_lift=math.ceil(-10-vertices[:,2].min()+3);lift=max(110,minimum_lift)
   row=dict(id=f'{ident}-open{angle}',tool=ident,opening_deg=angle,basis=basis.tolist(),translation=offset.tolist(),bounds=[vertices.min(0).tolist(),vertices.max(0).tolist()],lift_mm=lift,minimum_lift_mm=minimum_lift)
   contacts=[];hw=[]
   for part,m,s in parts:
    q=s.translate(offset.tolist());gap=q.min_gap(body,10);deeper=abs((body^s.translate((offset-[0,0,.08]).tolist())).volume())
    if deeper>1e-5:contacts.append(dict(component=part['name'],penetration_after_008mm_lowering_mm3=deeper,gap_mm=gap))
    if hardware(part['name']):hw.append(dict(component=part['name'],gap_mm=gap,intersection_mm3=abs((q^body).volume())))
   path=[]
   for dz in np.linspace(0,lift,math.ceil(lift/2)+1):path.append(abs((body^union.translate((offset+[0,0,dz]).tolist())).volume()))
   seated=union.translate(offset.tolist());tip=seated.trim_by_plane([0,0,-1],-float(vertices[:,2].min()+12));tipgap=tip.min_gap(body,100)
   grips=bool(contacts) and all('grip' in r['component'] for r in contacts)
   result=dict(id=row['id'],contacts=contacts,hardware=hw,board_gap_mm=float(vertices[:,1].min()-.15),bottom_12mm_tip_gap_mm=tipgap,vertical_pickup=dict(lift_mm=lift,minimum_lift_mm=minimum_lift,samples=len(path),max_intersection_mm3=max(path),final_tip_above_rim_mm=float(vertices[:,2].min()+lift+10)),passed=bool(grips and min(h['gap_mm'] for h in hw)>1 and max(path)<1e-6 and tipgap>1 and vertices[:,1].min()>.15))
   poses.append(row);results.append(result);print(json.dumps(result),flush=True)
   (d/'poses.json').write_text(json.dumps(poses,indent=2)+'\n');(d/'tool-checks.json').write_text(json.dumps(results,indent=2)+'\n')
 pr=trimesh.load_mesh(d/c['print_file']);mat=np.asarray(c['pose_matrix']).reshape(4,4);v=trimesh.transform_points(bodymesh.vertices,mat);error=float(np.max(np.abs(np.array([v.min(0),v.max(0)])-pr.bounds)))
 waypath=Path('bench/reference/conformal_motion_results.json');way=np.array([[r['y'],r['z'],r['theta_deg']] for r in json.loads(waypath.read_text())['removal_poses']]);fm=d/'front-material.stl';yz=trimesh.load_mesh(fm).vertices[:,1:];rho=np.linalg.norm(yz,axis=1).max();worst=1e9;count=0
 for aa,bb in zip(way[:-1],way[1:]):
  n=max(1,math.ceil((np.linalg.norm(bb[:2]-aa[:2])+math.radians(abs(bb[2]-aa[2]))*rho)/.05))
  for t in np.linspace(0,1,n+1):
   ty,tz,theta=aa+(bb-aa)*t;rad=math.radians(theta);worst=min(worst,float(np.min(ty+yz[:,0]*math.cos(rad)-yz[:,1]*math.sin(rad))));count+=1
 toolgap=50.8+min(r['bounds'][0][0] for r in poses if r['tool']=='klein')-max(r['bounds'][1][0] for r in poses if r['tool']=='knipex')
 inputs += [fm,waypath,d/c['print_file']]
 out=dict(passed=bool(all(r['passed'] for r in results) and bodymesh.is_watertight and bodymesh.body_count==1 and pr.is_watertight and error<.001 and worst>=-.006),tools=results,body=dict(watertight=bool(bodymesh.is_watertight),connected_bodies=int(bodymesh.body_count),volume_mm3=float(bodymesh.volume)),printing=dict(watertight=bool(pr.is_watertight),pose_bounds_error_mm=error,supports='Accessible local cavity/web supports likely; unsliced and no toolpath qualification'),installation=dict(min_board_plane_gap_mm=worst,samples=count,mesh_deflection_mm=.005,scope='Bare front body sampled against board plane; unchanged interface checked separately'),neighbors=dict(spacing_mm=50.8,body_gap_mm=2.,tool_X_gap_mm=toolgap,grasp='About 33 mm tool-to-tool gap; fingers extend beyond each tool. Physical grasp test pending.'),scope='Nominal reference and illustrative +10 opening; grip-bearing witnesses, unloaded hardware/tips, sampled vertical route. No dynamic capture, exact resting equilibrium or physical fit certification.',inputs={str(p):sha(p) for p in set(inputs)})
 (d/'checks.json').write_text(json.dumps(out,indent=2)+'\n');print('CHECKS',out['passed'])
 if not out['passed']:raise SystemExit(1)
if __name__=='__main__':main()
