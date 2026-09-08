"""Conservative three-dimensional round-peg motion study.

Upper hook: union of spheres swept along a planar centerline. For centers on
X=0, the nearest material in a board with coaxial cylindrical holes lies in
that plane. A circumscribed 2D capsule polygon therefore bounds exact 3D
collision. Lower locator: union of conservative constant-section X slabs;
each slab bounds the round cylinder, ignores its beneficial nose chamfer,
and uses the most restrictive circular-bore section over that slab.
Spine stays wholly in front of the board. Rotation about X preserves slabs.
"""
import math,json,heapq,time
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon,LineString,box
from shapely.ops import unary_union
from shapely.affinity import affine_transform
from round_anchor import geometry as cad_geometry

DEFAULTS=dict(board_thickness=3.94,hole_diameter=6.35,peg_diameter=5.6,
 tongue_diameter=4.8,spine_width=6.,spine_depth=4.5,spine_height=34.6,pitch=25.4,front_gap=.15,
 seat_drop=.12,pull_clearance=.47,tongue_run=5.,tongue_rise=3.,elbow_offset=None,
 locator_depth=2.3,locator_root_y=.6,locator_chamfer=.5,clearance=.10)

def parameters(overrides=None):
 p=cad_geometry(DEFAULTS|(overrides or {}))['parameters']
 p['neck_z']=-(p['hole_diameter']-p['peg_diameter'])/2+p['seat_drop']
 return p

def tf(poly,q):
 a=math.radians(q[2]);c=math.cos(a);s=math.sin(a)
 return affine_transform(poly,[c,-s,s,c,q[0],q[1]])

def pose_dict(q,stage='threading'):return dict(y=float(q[0]),z=float(q[1]),theta_deg=float(q[2]),stage=stage)

class RoundStudy:
 def __init__(self,p=None,slabs=96):
  self.p=parameters(p);p=self.p;r=p['peg_diameter']/2;z=p['neck_z'];t=p['board_thickness']
  self.centers=[(p['root_y'],z),(-t-p['elbow_offset'],z),(-t-p['elbow_offset']-p['tongue_run'],z+p['tongue_rise'])]
  self.centerline=LineString(self.centers)
  # Buffer's chordal arcs contain the exact circular cross-section.
  self.quad_segs=32;self.bound_radius=r/math.cos(math.pi/(4*self.quad_segs))
  self.tongue_bound_radius=(p['tongue_diameter']/2)/math.cos(math.pi/(4*self.quad_segs))
  self.upper=unary_union([LineString(self.centers[:2]).buffer(self.bound_radius,quad_segs=self.quad_segs),LineString(self.centers[1:]).buffer(self.tongue_bound_radius,quad_segs=self.quad_segs)])
  cr=p['spine_corner_radius'];self.spine=box(p['front_gap'],p['spine_top']-p['spine_height'],p['spine_depth'],p['spine_top'])
  if cr:self.spine=self.spine.buffer(-cr,quad_segs=12).buffer(cr,quad_segs=12)
  self.spinepts=np.asarray(self.spine.exterior.coords)
  self.radius=max(np.linalg.norm(np.asarray(self.upper.exterior.coords),axis=1).max(),np.linalg.norm(self.spinepts,axis=1).max(),p['pitch']+abs(z)+p['locator_diameter']/2+p['locator_depth'])
  lr=p['locator_diameter']/2;self.slab_edges=np.linspace(0,lr,slabs+1);self.ri=np.sqrt(np.maximum(0,lr*lr-self.slab_edges[:-1]**2))
  zl=z-p['pitch'];yl=-p['locator_depth'];yh=p['locator_root_y']
  self.locator_points=np.stack([np.column_stack([np.full(slabs,yl),zl-self.ri]),np.column_stack([np.full(slabs,yh),zl-self.ri]),np.column_stack([np.full(slabs,yh),zl+self.ri]),np.column_stack([np.full(slabs,yl),zl+self.ri])],axis=1)
  self.obstacles={False:self.make_obstacles(p['hole_diameter']/2-p['clearance']),True:self.make_obstacles(p['hole_diameter']/2)}
  self.cache={}
 def make_obstacles(self,R):
  p=self.p;t=p['board_thickness'];pitch=p['pitch']
  return unary_union([box(-t,-100,0,-pitch-R),box(-t,-pitch+R,0,-R),box(-t,R,0,100)])
 def lower_clip(self,q,real=False):
  p=self.p;t=p['board_thickness'];a=math.radians(q[2]);c=math.cos(a);s=math.sin(a)
  pts=self.locator_points
  yy=c*pts[:,:,0]-s*pts[:,:,1]+q[0];zz=s*pts[:,:,0]+c*pts[:,:,1]+q[1]
  valid=(yy>=-t)&(yy<=0);zs=[np.where(valid,zz,np.nan)]
  yn=np.roll(yy,-1,axis=1);zn=np.roll(zz,-1,axis=1);dy=yn-yy
  for boundary in [-t,0]:
   with np.errstate(divide='ignore',invalid='ignore'):u=(boundary-yy)/dy
   zs.append(np.where((u>=0)&(u<=1),zz+u*(zn-zz),np.nan))
  cand=np.concatenate(zs,axis=1)
  lo=np.min(np.where(np.isnan(cand),np.inf,cand),axis=1);hi=np.max(np.where(np.isnan(cand),-np.inf,cand),axis=1)
  R=p['hole_diameter']/2-(0 if real else p['clearance']);h=np.sqrt(np.maximum(0,R*R-self.slab_edges[1:]**2))
  coll=(lo<-p['pitch']-h-1e-10)|(hi>-p['pitch']+h+1e-10)
  return bool(np.any(coll & np.isfinite(lo)))
 def collision(self,q,real=False):
  p=self.p;a=math.radians(q[2]);c=math.cos(a);s=math.sin(a)
  sy=c*self.spinepts[:,0]-s*self.spinepts[:,1]+q[0]
  if sy.min()<-1e-9 and sy.max()>-p['board_thickness']:return True
  if tf(self.upper,q).distance(self.obstacles[real])<1e-7:return True
  return self.lower_clip(q,real)
 def clear_distance(self,q,real=False):
  p=self.p;t=p['board_thickness'];upper=tf(self.upper,q).distance(self.obstacles[real]);spine=tf(self.spine,q)
  dist=min(upper,max(0,spine.bounds[0]))
  R=p['hole_diameter']/2-(0 if real else p['clearance'])
  # Every X slab is bounded by this rectangle and the outer-edge bore section.
  h=np.sqrt(np.maximum(0,R*R-self.slab_edges[1:]**2))
  a=math.radians(q[2]);c=math.cos(a);ss=math.sin(a)
  xy=np.empty_like(self.locator_points)
  xy[:,:,0]=c*self.locator_points[:,:,0]-ss*self.locator_points[:,:,1]+q[0]
  xy[:,:,1]=ss*self.locator_points[:,:,0]+c*self.locator_points[:,:,1]+q[1]
  lo=-p['pitch']-h;hi=-p['pitch']+h
  dy=np.maximum.reduce([-t-xy[:,:,0],xy[:,:,0],np.zeros_like(xy[:,:,0])])
  dl=np.maximum(xy[:,:,1]-lo[:,None],0);du=np.maximum(hi[:,None]-xy[:,:,1],0)
  vd=np.sqrt(np.min(np.minimum(dy*dy+dl*dl,dy*dy+du*du)))
  corners=np.stack([np.column_stack([np.full(len(h),-t),lo]),np.column_stack([np.zeros(len(h)),lo]),np.column_stack([np.full(len(h),-t),hi]),np.column_stack([np.zeros(len(h)),hi])],axis=1)
  edges=np.roll(xy,-1,axis=1)-xy
  delta=corners[:,:,None,:]-xy[:,None,:,:]
  fac=np.sum(delta*edges[:,None,:,:],axis=3)/np.sum(edges*edges,axis=2)[:,None,:]
  fac=np.clip(fac,0,1)
  dd=delta-fac[:,:,:,None]*edges[:,None,:,:]
  cd=np.sqrt(np.min(np.sum(dd*dd,axis=3)))
  if self.lower_clip(q,real):return 0.
  dist=min(dist,float(vd),float(cd))
  return dist
 def search(self,step=.05,da=.25,max_seconds=12):
  started=time.time();p=self.p;base=(-p['front_gap']+.03,0,0);start=(0,0,0);q=[(0,0,start)];best={start:0};prev={start:None};self.cache={}
  def pose(n):return (n[0]*step+base[0],n[1]*step,n[2]*da)
  def valid(n):
   if not(-10<=n[0]<=int(35/step) and -int(2/step)<=n[1]<=int(12/step) and 0<=n[2]<=int(60/da)):return False
   if n not in self.cache:self.cache[n]=not self.collision(pose(n))
   return self.cache[n]
  if not valid(start):return None
  moves=[(y,z,a) for y in[-1,0,1] for z in[-1,0,1] for a in[-1,0,1] if(y,z,a)!=(0,0,0)]
  while q:
   if time.time()-started>max_seconds:self.search_timeout=True;return None
   _,cost,n=heapq.heappop(q)
   if cost!=best[n]:continue
   if tf(self.upper,pose(n)).bounds[0]>1:
    out=[]
    while n is not None:out.append(pose(n));n=prev[n]
    return out[::-1]
   for d in moves:
    nn=tuple(n[i]+d[i] for i in range(3))
    if not valid(nn):continue
    nc=cost+math.sqrt(d[0]**2+d[1]**2+(.5*d[2])**2)
    if nc<best.get(nn,1e100):
     best[nn]=nc;prev[nn]=n
     heapq.heappush(q,(nc+max(0,14/step-nn[0]),nc,nn))
  return None
 def sampled_clear(self,a,b,maxtravel=.08):
  a=np.array(a);b=np.array(b);travel=np.linalg.norm(b[:2]-a[:2])+self.radius*math.radians(abs(b[2]-a[2]));n=max(1,math.ceil(travel/maxtravel))
  return all(not self.collision(a+(b-a)*u/n) for u in range(n+1))
 def simplify(self,path):
  out=[path[0]];i=0
  while i<len(path)-1:
   j=len(path)-1
   while j>i+1 and not self.sampled_clear(path[i],path[j]):j-=1
   out.append(path[j]);i=j
  return out
 def certify(self,a,b,depth=0):
  a=np.asarray(a);b=np.asarray(b);m=(a+b)/2
  bound=np.linalg.norm(b[:2]-a[:2])/2+2*self.radius*math.sin(math.radians(abs(b[2]-a[2]))/4)
  dist=self.clear_distance(m)
  if dist>bound+1e-8:return dict(passed=True,leaves=1,residual_mm=dist-bound)
  if depth>=18 or self.collision(m):return dict(passed=False,depth=depth,pose=m.tolist(),distance=dist,bound=bound)
  l=self.certify(a,m,depth+1);r=self.certify(m,b,depth+1)
  if not l['passed'] or not r['passed']:return dict(passed=False,left=l,right=r)
  return dict(passed=True,leaves=l['leaves']+r['leaves'],residual_mm=min(l['residual_mm'],r['residual_mm']))


def exact_upper_margin(study,q):
 p=study.p;rr=[p['peg_diameter']/2,p['tongue_diameter']/2]
 return min(tf(LineString(study.centers[i:i+2]),q).distance(study.obstacles[True])-rr[i] for i in[0,1])

def contact_certificate(study,contact,release):
 """Exact circular primitives, allowing deliberate final tangency."""
 p=study.p;radii=[p['peg_diameter']/2,p['tongue_diameter']/2];upper=[]
 for i,r in enumerate(radii):
  a=tf(LineString(study.centers[i:i+2]),contact);b=tf(LineString(study.centers[i:i+2]),release)
  swept=unary_union([a,b]).convex_hull
  distance=swept.distance(study.obstacles[True]);upper.append(dict(radius_mm=r,minimum_center_sweep_distance_mm=distance,passed=distance>=r-1e-9))
 R=p['hole_diameter']/2;lr=p['locator_diameter']/2
 c0=p['neck_z']+contact[1];c1=p['neck_z']+release[1]
 maxradial=lr+max(abs(c0),abs(c1))
 spine_min_y=p['front_gap']+min(contact[0],release[0])
 passed=all(a['passed'] for a in upper) and maxradial<=R+1e-9 and spine_min_y>=-1e-9
 return dict(passed=passed,upper_capsules=upper,lower_maximum_radial_extent_mm=maxradial,physical_bore_radius_mm=R,minimum_spine_front_y_mm=spine_min_y,
  method='Exact centerline translation sweep distance for each circular capsule; full-circle containment for locator, chamfer ignored conservatively; monotonic opening of spine contact. Final zero-clearance tangency allowed.')

def first_upper_stop(study,fn,maxq=10,step=.01):
 prev=0.
 for q in np.arange(step,maxq+step/2,step):
  if exact_upper_margin(study,fn(float(q))) < -1e-9:
   lo=prev;hi=float(q)
   for _ in range(36):
    mid=(lo+hi)/2
    if exact_upper_margin(study,fn(mid)) < -1e-9:hi=mid
    else:lo=mid
   return (lo+hi)/2
  prev=float(q)
 return None

def build_result(name,trial_path,outfile=None):
 data=trial_path if isinstance(trial_path,dict) else json.loads(Path(trial_path).read_text());s=RoundStudy(data['parameters']);p=s.p
 raw=data['path'];path=s.simplify(raw)
 contact=(-p['front_gap'],-p['seat_drop'],0);release=path[0]
 stage=(max(28,path[-1][0]+12),path[-1][1],path[-1][2]);front=(stage[0],stage[1],0)
 free=path+[stage,front]
 certs=[];certified=[free[0]]
 raw_ext=[tuple(q) for q in raw]+[tuple(stage),tuple(front)]
 raw_indices={tuple(q):i for i,q in enumerate(raw_ext)}
 def refine(a,b):
  cert=s.certify(a,b)
  if cert['passed']:return [b],[cert]
  ia=raw_indices[tuple(a)];ib=raw_indices[tuple(b)]
  if ib-ia<=1:raise RuntimeError(f'{name}: adjacent search edge failed continuous proof')
  mid=raw_ext[(ia+ib)//2]
  lp,lc=refine(a,mid);rp,rc=refine(mid,b)
  return lp+rp,lc+rc
 for a,b in zip(free[:-1],free[1:]):
  pts,cs=refine(a,b);certified.extend(pts);certs.extend(cs)
 free=certified
 contact_cert=contact_certificate(s,contact,release)
 if not contact_cert['passed']:raise RuntimeError(f'{name}: contact segment failed')
 removal=[contact]+free
 frames=[]
 for a,b in zip(removal[:-1],removal[1:]):
  a=np.asarray(a,float);b=np.asarray(b,float);travel=np.linalg.norm(b[:2]-a[:2])+s.radius*math.radians(abs(b[2]-a[2]));n=max(1,math.ceil(travel/.025))
  frames.extend((a+(b-a)*k/n).tolist() for k in range(n))
 frames.append(list(removal[-1]))
 # Dense free-motion checks supplement the continuous proof; contact uses exact primitives.
 free_collisions=sum(s.collision(q) for q in frames if not(q[2]==0 and q[0]<=release[0]+1e-9 and q[1]<=release[1]+1e-9))
 pull=first_upper_stop(s,lambda u:(contact[0]+u,contact[1],0),5)
 lift=first_upper_stop(s,lambda u:(contact[0],contact[1]+u,0),3)
 pivot=np.array([p['front_gap'],p['spine_top']-p['spine_height']+p['spine_corner_radius']])
 def rocking(u):
  a=-math.radians(u);c=math.cos(a);ss=math.sin(a);rp=np.array([c*pivot[0]-ss*pivot[1],ss*pivot[0]+c*pivot[1]])
  tr=np.array(contact[:2])+pivot-rp;return(tr[0],tr[1],-u)
 rock=first_upper_stop(s,rocking,5,.005)
 rear=max(0,-p['board_thickness']-min(tf(s.upper,q).bounds[0] for q in frames))
 poses=[]
 for i,q in enumerate(removal):
  label='seated' if i==0 else 'release bearing contact' if i==1 else 'tip and lift' if i<len(removal)-3 else 'withdraw tongue' if i==len(removal)-3 else 'clear approach' if i==len(removal)-2 else 'free in front'
  poses.append(pose_dict(q,label))
 install=[]
 for i,q in enumerate(poses[::-1]):
  q=dict(q);q['stage']='free in front' if i==0 else 'set insertion angle' if i==1 else 'thread upper tongue' if i==2 else 'rotate and engage round locator' if i<len(poses)-2 else 'align' if i==len(poses)-2 else 'seat round pegs';install.append(q)
 result=dict(name=name,parameters=p,install_poses=install,removal_poses=poses,
  summary=dict(maximum_install_tilt_deg=max(q[2] for q in removal),maximum_lift_mm=max(q[1] for q in removal)-contact[1],rear_wall_clearance_required_mm=rear,
    straight_outward_travel_until_stop_mm=pull,straight_lift_until_stop_mm=lift,outward_rock_to_rear_shoulder_deg=rock,rocking_pivot_yz=pivot.tolist(),rocking_stop_pose=pose_dict(rocking(rock)) if rock else None,
    diametral_clearance_mm=p['hole_diameter']-p['peg_diameter'],upper_section_area_mm2=math.pi*p['peg_diameter']**2/4,upper_section_modulus_mm3=math.pi*p['peg_diameter']**3/32,
    tongue_section_area_mm2=math.pi*p['tongue_diameter']**2/4,tongue_section_modulus_mm3=math.pi*p['tongue_diameter']**3/32,
    retaining_overlap_above_centerplane_bore_mm=p['peg_diameter']/2+p['tongue_diameter']/2+p['tongue_rise']-p['hole_diameter']),
  verification=dict(passed=free_collisions==0,continuous_free_motion_certificates=certs,contact_segment_certificate=contact_cert,dense_verification_frames=len(frames),dense_colliding_free_frames=free_collisions,
    dense_maximum_point_travel_mm=.025,radial_bore_clearance_reserved_mm=p['clearance'],lower_x_slabs_per_half=len(s.ri),lower_locator_chamfer_ignored_conservatively=True,
    upper_capsule_polygon_is_circumscribed=True,maximum_upper_radius_overbound_mm=max(s.bound_radius-p['peg_diameter']/2,s.tongue_bound_radius-p['tongue_diameter']/2),
    spine_profile_matches_cad_quad_segs=12,raw_search_waypoints=len(raw),simplified_waypoints=len(removal),
    assumptions=['Rigid ideal geometry and circular cylindrical bores.','Motion preserves X: translation in Y/Z and rotation about X only.','Upper uses exact center-plane reduction of planar sphere-swept primitives, then circumscribed bounds.','Lower uses conservative full-cylinder bounds over 96 X slabs per half; removing the nose chamfer from the check enlarges the solid.','Spine stays in front of the full board slab and matches the CAD polygon.','Free motion reserves 0.10 mm radial bore clearance; exact final seating closes the intended contacts.','No physical force, fatigue, creep, FDM adhesion, or board-breakout test.','Full attached holders and print scaffolds require separate checks; scaffolds must be removed.']))
 if outfile:Path(outfile).write_text(json.dumps(result,indent=2))
 print(name,json.dumps(result['summary']),result['verification']['passed'],flush=True)
 return result

PRESETS=[
 ('round_default_3p94',{}),
 ('round_stock_4p19',{'board_thickness':4.19}),
 ('round_nominal_3_16',{'board_thickness':4.7625,'peg_diameter':5.4}),
 ('round_true_1_4',{'board_thickness':6.35,'peg_diameter':5.2}),
 ('round_9_32_holes',{'hole_diameter':7.14375}),
]

def regenerate(outdir=None,default_only=False,custom=None):
 """Rebuild the study without exploratory files or cached paths."""
 out=Path(outdir or Path(__file__).parent);out.mkdir(exist_ok=True,parents=True)
 presets=[('round_custom',custom)] if custom is not None else PRESETS[:1] if default_only else PRESETS
 results=[]
 for name,overrides in presets:
  study=RoundStudy(overrides);path=study.search(step=.025,da=.125,max_seconds=20)
  if path is None:
   reason='bounded search timed out' if getattr(study,'search_timeout',False) else 'no path found in the explored grid'
   raise RuntimeError(f'{name}: {reason}; this does not prove every possible installation motion impossible')
  target=out/'round_motion_results.json' if name=='round_default_3p94' else None
  result=build_result(name,{'parameters':study.p,'path':path},target);results.append(result)
 if len(results)>1:(out/'round_motion_presets.json').write_text(json.dumps({'passed':all(r['verification']['passed'] for r in results),'variants':results},indent=2))
 elif custom is not None:(out/'round_custom_motion.json').write_text(json.dumps(results[0],indent=2))
 return results

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--default-only',action='store_true')
 ap.add_argument('--output-dir')
 ap.add_argument('--thickness',type=float)
 ap.add_argument('--hole-diameter',type=float)
 ap.add_argument('--peg-diameter',type=float)
 ap.add_argument('--tongue-diameter',type=float)
 args=ap.parse_args();custom={}
 for arg,key in [('thickness','board_thickness'),('hole_diameter','hole_diameter'),('peg_diameter','peg_diameter'),('tongue_diameter','tongue_diameter')]:
  value=getattr(args,arg)
  if value is not None:custom[key]=value
 regenerate(args.output_dir,args.default_only,custom or None)
