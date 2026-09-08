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

DEFAULTS=dict(board_thickness=3.94,hole_diameter=6.35,peg_diameter=5.0,
 spine_width=6.,spine_depth=4.5,spine_height=34.6,pitch=25.4,front_gap=.15,
 seat_drop=.12,pull_clearance=.47,tongue_run=5.,tongue_rise=3.,elbow_offset=None,
 locator_depth=2.3,locator_front=.6,locator_chamfer=.5,clearance=.10)

def parameters(overrides=None):
 p=DEFAULTS|(overrides or {});R=p['hole_diameter']/2;r=p['peg_diameter']/2;m=p['tongue_rise']/p['tongue_run']
 if p['elbow_offset'] is None:p['elbow_offset']=p['pull_clearance']-p['front_gap']-(2*R-r)/m+r*math.sqrt(1+1/m**2)
 p['neck_z']=-(R-r)+p['seat_drop'];return p

def tf(poly,q):
 a=math.radians(q[2]);c=math.cos(a);s=math.sin(a)
 return affine_transform(poly,[c,-s,s,c,q[0],q[1]])

def pose_dict(q,stage='threading'):return dict(y=float(q[0]),z=float(q[1]),theta_deg=float(q[2]),stage=stage)

class RoundStudy:
 def __init__(self,p=None,slabs=96):
  self.p=parameters(p);p=self.p;r=p['peg_diameter']/2;z=p['neck_z'];t=p['board_thickness']
  self.centers=[(1.4,z),(-t-p['elbow_offset'],z),(-t-p['elbow_offset']-p['tongue_run'],z+p['tongue_rise'])]
  self.centerline=LineString(self.centers)
  # Buffer's chordal arcs contain the exact circular cross-section.
  self.quad_segs=32;self.bound_radius=r/math.cos(math.pi/(4*self.quad_segs))
  self.upper=self.centerline.buffer(self.bound_radius,quad_segs=self.quad_segs,cap_style=1,join_style=1)
  self.spine=box(p['front_gap'],4.2-p['spine_height'],p['spine_depth'],4.2).buffer(-.65,quad_segs=8).buffer(.65,quad_segs=8)
  self.spinepts=np.asarray(self.spine.exterior.coords)
  self.radius=max(np.linalg.norm(np.asarray(self.upper.exterior.coords),axis=1).max(),np.linalg.norm(self.spinepts,axis=1).max(),p['pitch']+abs(z)+r+p['locator_depth'])
  self.slab_edges=np.linspace(0,r,slabs+1);self.ri=np.sqrt(np.maximum(0,r*r-self.slab_edges[:-1]**2))
  zl=z-p['pitch'];yl=-p['locator_depth'];yh=p['locator_front']
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
 def search(self,step=.05,da=.25):
  p=self.p;base=(-p['front_gap']+.03,0,0);start=(0,0,0);q=[(0,0,start)];best={start:0};prev={start:None};self.cache={}
  def pose(n):return (n[0]*step+base[0],n[1]*step,n[2]*da)
  def valid(n):
   if not(-10<=n[0]<=600 and -40<=n[1]<=240 and 0<=n[2]<=240):return False
   if n not in self.cache:self.cache[n]=not self.collision(pose(n))
   return self.cache[n]
  if not valid(start):return None
  moves=[(y,z,a) for y in[-1,0,1] for z in[-1,0,1] for a in[-1,0,1] if(y,z,a)!=(0,0,0)]
  while q:
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

if __name__=='__main__':
 import sys
 d=float(sys.argv[1]) if len(sys.argv)>1 else 5.
 s=RoundStudy({'peg_diameter':d});start=time.time();path=s.search();print('diameter',d,'offset',s.p['elbow_offset'],'states',len(s.cache),'seconds',time.time()-start,'path',len(path) if path else None,'angle',max(q[2] for q in path) if path else None,flush=True)
 if path:Path(__file__).with_name('trial_round_'+str(d)+'.json').write_text(json.dumps({'parameters':s.p,'path':path}))
