"""Bounded genetic search using a native-envelope, anisotropic truss surrogate.

No physical modulus or strength is asserted. Normalized print-Z spring stiffness
is tested at 0.35 and 0.65 of XY; removed regions retain only a 0.005 numerical stiffness background.
Small features/contact/walls are unresolved. Only the selected core is CAD-built.
"""
from pathlib import Path
import json,numpy as np
from scipy.spatial import ConvexHull,cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import splu
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'.local-runtime/hx05-density-v1'
LAYOUT=json.loads((ROOT/'.local-runtime/matched-fans-v1/layout.json').read_text())
NAMES=['FoundationDepth','PegRootRadius','RootDepth','CollectorHeight','RibWidth','RootWidth','RootFanout']
BASE=np.array([3,7.5,8,10,3,9,9.])
LOW=np.array([3,7.5,8,8,3,8,6.]);HIGH=np.array([6,12,16,16,8,18,20.])
class Model:
 def __init__(self,ident):
  self.ident=ident;data=json.loads((WORK/ident/'lattice.json').read_text());self.p=np.array(data['points']);self.edges=np.array(data['edges']);self.pitch=data['pitch_mm']
  self.rack=next(r for r in LAYOUT['racks'] if r['id']==ident);self.tools=self.rack['tools']
  self.mid=self.p[self.edges].mean(1);self.vector=self.p[self.edges[:,1]]-self.p[self.edges[:,0]];self.length=np.linalg.norm(self.vector,axis=1);self.u=self.vector/self.length[:,None]
  dof=np.arange(len(self.p)*3).reshape(-1,3);self.edof=np.hstack([dof[self.edges[:,0]],dof[self.edges[:,1]]]);v=np.hstack([-self.u,self.u]);self.blocks=v[:,:,None]*v[:,None,:]/self.length[:,None,None]
  self.rows=np.repeat(self.edof,6,axis=1).ravel();self.cols=np.tile(self.edof,(1,6)).ravel();self.free=dof[self.p[:,1]>5].ravel();self.cross_weight=self.u[:,0]**2
  self.check=json.loads((WORK/ident/'check.json').read_text());tree=cKDTree(self.p)
  forces=[];labels=[]
  for t in [self.tools[0],max(self.tools,key=lambda k:k['af']),self.tools[-1]]:
   a=np.array(t['axis']);mouth=np.array(t['mouth']);rad=np.array([0.,0.,1.])-a*a[2];rad/=np.linalg.norm(rad);side=np.cross(a,rad);r=t['outer_radius'];near=[tree.query(mouth-a*3+s*rad*r)[1] for s in [-1,1]];inner=[tree.query(mouth-a*13+s*rad*r)[1] for s in [-1,1]]
   reach=max(0,t['overall']-t['burial']);lever=reach/10
   gravity=np.zeros((len(self.p),3));pull=gravity.copy();twist=gravity.copy()
   for n in near:gravity[n,2]-=(1+lever)/2;pull[n]+=a/2
   for n in inner:gravity[n,2]+=lever/2
   for sign,n in zip([-1,1],near):twist[n]+=sign*side/(2*r)
   for label,f in [('gravity',gravity),('extraction',pull),('torsion',twist)]:forces.append(f.ravel());labels.append(t['name']+':'+label)
  self.F=np.array(forces).T;self.labels=labels;self.reference={}
  for z in [.35,.65]:self.reference[z]=self.solve(np.ones(len(self.edges)),z)
 def occupancy(self,x):
  foundation,radius,depth,belt,width,root_width,reach=x;pts=self.mid;h=self.pitch
  smooth=lambda d:np.clip(.5-d/h,0,1)
  dense=smooth(pts[:,0]-(self.p[:,0].min()-h/2+foundation))
  y=pts[:,1]
  for cx in self.check['columns_mm']:
   for cz in self.check['rows_mm']:
    d=np.maximum.reduce([np.sqrt((pts[:,0]-cx)**2+(pts[:,2]-cz)**2)-radius,y-depth,-.1-y]);dense=np.maximum(dense,smooth(d))
  for cz in [max(self.check['rows_mm']),min(self.check['rows_mm'])]:dense=np.maximum(dense,smooth(np.maximum.reduce([abs(pts[:,2]-cz)-belt/2,y-depth,-.1-y])))
  for t in self.tools:
   tip=np.array(t['tip']);mouth=np.array(t['mouth']);a=np.array(t['axis']);rad=np.array([0.,0.,1.])-a*a[2];rad/=np.linalg.norm(rad);r=t['outer_radius'];floor=3.;delta=pts-tip;axial=delta@a
   d=np.maximum.reduce([np.linalg.norm(delta-axial[:,None]*a,axis=1)-r,-floor-axial,axial-t['burial']]);dense=np.maximum(dense,smooth(d))
   for sign in [-1,1]:
    vertices=[]
    for q in [tip-a*floor,mouth-a*3]:
     shell=q+rad*(sign*(r-width/3));root=np.array([shell[0],5,shell[2]+sign*reach])
     for sx in [-1,1]:
      for sz in [-1,1]:vertices.extend([shell+[sx*width/2,0,sz*width/2],root+[sx*width/2,0,sz*root_width/2]])
    planes=ConvexHull(vertices).equations;distance=np.max(pts@planes[:,:3].T+planes[:,3],axis=1);dense=np.maximum(dense,smooth(distance))
  return dense
 def solve(self,dense,z):
  E=(.005+.995*dense**2)/(1+self.cross_weight*(1/z-1))
  K=coo_matrix(((self.blocks*E[:,None,None]).ravel(),(self.rows,self.cols)),shape=(len(self.p)*3,)*2).tocsc()
  K=K[self.free][:,self.free];K=K+coo_matrix((np.full(len(self.free),1e-8),(np.arange(len(self.free)),np.arange(len(self.free)))),shape=K.shape).tocsc()
  D=np.zeros_like(self.F);D[self.free]=splu(K).solve(self.F[self.free]);compliance=np.sum(self.F*D,axis=0)
  extension=np.sum((D.reshape(len(self.p),3,-1)[self.edges[:,1]]-D.reshape(len(self.p),3,-1)[self.edges[:,0]])*self.u[:,:,None],axis=1)
  self.last_regularization_fraction=1e-8*np.sum(D[self.free]**2,axis=0)/np.maximum(compliance,1e-30)
  energy=extension**2*(E/self.length)[:,None];cross=np.sum(energy*self.cross_weight[:,None],axis=0)
  return compliance,cross
 def evaluate(self,x):
  dense=self.occupancy(x);fraction=float(dense.mean());results={}
  for z in [.35,.65]:
   c,e=self.solve(dense,z);results[z]=(c,e)
  return fraction,results
rng=np.random.default_rng(5589);report=[]
for ident in ['HX05C','HX05B','HX05A']:
 model=Model(ident);base_fraction,base_results=model.evaluate(BASE);cache={}
 def score(x):
  key=tuple(x)
  if key not in cache:
   fraction,results=model.evaluate(x)
   cs=np.concatenate([results[z][0]/base_results[z][0] for z in [.35,.65]]);es=np.concatenate([results[z][1]/base_results[z][1] for z in [.35,.65]])
   cost=.7*cs.mean()+.2*es.mean()+.25*fraction/base_fraction+15*max(0,fraction/base_fraction-1.25)**2
   cache[key]=(float(cost),fraction,results)
  return cache[key][0]
 population=[BASE.copy()]+[np.round(rng.uniform(LOW,HIGH)*2)/2 for _ in range(11)];history=[]
 for generation in range(7):
  population.sort(key=score);best=population[0];history.append(dict(generation=generation,best_score=score(best),parameters=dict(zip(NAMES,map(float,best)))))
  print(ident,generation,score(best),flush=True)
  survivors=population[:4];population=[p.copy() for p in survivors]
  while len(population)<12:
   a,b=rng.choice(4,2,replace=False);child=np.where(rng.random(7)<.5,survivors[a],survivors[b]);child+=rng.normal(0,(HIGH-LOW)*.10)* (rng.random(7)<.45);population.append(np.round(np.clip(child,LOW,HIGH)*2)/2)
 population.sort(key=score);winner=population[0];_,fraction,results=cache[tuple(winner)]
 cases=[]
 for z in [.35,.65]:
  for i,label in enumerate(model.labels):cases.append(dict(case=label,normalized_print_z_stiffness=z,compliance_relative_baseline=float(results[z][0][i]/base_results[z][0][i]),cross_layer_energy_relative_baseline=float(results[z][1][i]/base_results[z][1][i]),compliance_relative_fully_dense=float(results[z][0][i]/model.reference[z][0][i])))
 row=dict(id=ident,parameters=dict(zip(NAMES,map(float,winner))),baseline_parameters=dict(zip(NAMES,map(float,BASE))),baseline_score=score(BASE),selected_score=score(winner),coarse_dense_fraction_baseline=base_fraction,coarse_dense_fraction_selected=fraction,unique_evaluations=len(cache),history=history,cases=cases)
 report.append(row);(WORK/'genetic-check.json').write_text(json.dumps(dict(seed=5589,population=12,generations=7,models=report,scope='Coarse 10 mm native-envelope axial truss surrogate with normalized anisotropy sensitivity; no true continuum FEA, material calibration, failure stress or load rating. Optimistic fully clamped plate, unresolved walls/small bores/contact. Relative candidate ranking only.'),indent=2)+'\n')
 print(ident,'selected',row['parameters'],flush=True)
