"""Linear tetrahedral continuum for comparative modifier-plane studies.

Material axes stay fixed to the print: installed X is layer-normal. Normalized
moduli, sparse-bulk stiffness and layer-strength penalties are sensitivity
assumptions, not measured ASA properties. Rear peg contact is not modeled.
"""
from pathlib import Path
import json,numpy as np
from scipy.spatial import ConvexHull,cKDTree
from scipy.sparse import coo_matrix

def read_msh(path):
 nodes=[];tags=[];tri=[];tet=[]
 with open(path) as f:
  for line in f:
   if line.strip()=='$Nodes':
    for _ in range(int(next(f))):
     q=next(f).split();tags.append(int(q[0]));nodes.append(list(map(float,q[1:4])))
   elif line.strip()=='$Elements':
    for _ in range(int(next(f))):
     q=list(map(int,next(f).split()));kind=q[1];conn=q[3+q[2]:]
     if kind==2:tri.append(conn)
     elif kind==4:tet.append(conn)
 X=np.array(nodes);lookup=np.full(max(tags)+1,-1,dtype=np.int32);lookup[tags]=np.arange(len(tags))
 triangles=lookup[np.array(tri)];tets=lookup[np.array(tet)];assert len(tets)>0 and np.min(tets)>=0
 return X,triangles,tets

def elasticity(rz):
 S=np.zeros((6,6));S[:3,:3]=[[1/rz,-.25,-.25],[-.25,1,-.3],[-.25,-.3,1]]
 S[3,3]=2.6;S[4,4]=S[5,5]=2.6/rz
 D=np.linalg.inv(S)*1000.;assert np.linalg.eigvalsh(D).min()>0
 return D

def tet_data(X,tets):
 corners=X[tets];T=np.concatenate([np.ones((len(tets),4,1)),corners],axis=2)
 determinant=np.linalg.det(T);vol=np.abs(determinant)/6;assert vol.min()>1e-14
 grad=np.linalg.inv(T)[:,1:,:].transpose(0,2,1);B=np.zeros((len(tets),6,12))
 for i in range(4):
  dx,dy,dz=grad[:,i,:].T;j=3*i
  B[:,0,j]=dx;B[:,1,j+1]=dy;B[:,2,j+2]=dz
  B[:,3,j+1]=dz;B[:,3,j+2]=dy;B[:,4,j]=dz;B[:,4,j+2]=dx;B[:,5,j]=dy;B[:,5,j+1]=dx
 dof=np.arange(len(X)*3,dtype=np.int32).reshape(-1,3);edof=dof[tets].reshape(-1,12)
 return corners.mean(1),vol,B,edof

def wrench(X,weights,F,M,application):
 weights=weights/weights.sum();centre=(X*weights[:,None]).sum(0);r=X-centre
 moment=M+np.cross(application-centre,F)
 J=np.eye(3)*np.sum(weights*np.sum(r*r,axis=1))-(r*weights[:,None]).T@r
 omega=np.linalg.solve(J,moment);forces=weights[:,None]*(F+np.cross(omega,r))
 assert np.linalg.norm(forces.sum(0)-F)<1e-7
 assert np.linalg.norm(np.cross(r,forces).sum(0)-moment)<1e-6
 return forces

def load_cases(X,triangles,rack):
 pts=X[triangles];centres=pts.mean(1);areas=np.linalg.norm(np.cross(pts[:,1]-pts[:,0],pts[:,2]-pts[:,0]),axis=1)/2
 F=[];labels=[];patches=[]
 for tool in rack['tools']:
  tip=np.array(tool['tip']);u=np.array(tool['axis']);bar=np.array(tool['bar_axis']);side=np.cross(u,bar);q=centres-tip;t=q@u;rad=q-t[:,None]*u
  if rack['id']=='HX05A':
   radius=(tool['p2p']+rack['parameters']['AFClearance'])/2
   wall=abs(np.linalg.norm(rad,axis=1)-radius)<.04;inside=np.linalg.norm(rad,axis=1)<=radius+.04
  else:
   normals=np.array([bar*np.cos(k*np.pi/3)+side*np.sin(k*np.pi/3) for k in range(6)]);proj=q@normals.T;radius=(tool['af']+rack['parameters']['AFClearance'])/2
   wall=abs(proj.max(1)-radius)<.04;inside=proj.max(1)<=radius+.04
  mask=((wall&(t>1)&(t<tool['guide']-1))|((abs(t)<.04)&inside))
  selected=triangles[mask];a=areas[mask];assert len(selected)>10,(tool['name'],'No resolved bore patch')
  ids=np.unique(selected);weights=np.zeros(len(X));np.add.at(weights,selected.ravel(),np.repeat(a/3,3));weights=weights[ids]
  patches.append(dict(tool=tool['name'],nodes=len(ids),area_mm2=float(a.sum())))
  for mode,force,moment,application in [('gravity',np.array([0.,0.,-1.]),np.zeros(3),np.array(tool['top'])),('extraction',u,np.zeros(3),np.array(tool['mouth'])),('torsion',np.zeros(3),u,np.array(tool['mouth']))]:
   field=np.zeros((len(X),3));field[ids]=wrench(X[ids],weights,force,moment,application);F.append(field.ravel());labels.append(tool['name']+':'+mode)
 return np.array(F).T,labels,patches

def fixed_and_shell(X,triangles,centres,rack):
 surface=X[triangles];cloud=np.concatenate([surface.mean(1),surface[:,0],surface[:,1],surface[:,2],(surface[:,0]+surface[:,1])/2,(surface[:,1]+surface[:,2])/2,(surface[:,2]+surface[:,0])/2])
 distance=cKDTree(cloud).query(centres,workers=1)[0]
 # Conservative sampled distance approximation. Refined-mesh sensitivity is
 # required; no actual toolpath shell volume is inferred from this mask.
 fixed=distance<=1.5;fixed|=centres[:,1]<.1
 p=rack['density_parameters'];foot=rack['parameters']['FloorDepth'];lead=rack['parameters']['LeadDepth']
 fixed|=centres[:,0] <= X[:,0].min()+p['FoundationDepth']
 for x in rack['columns_mm']:
  for z in rack['rows_mm']:fixed|=((centres[:,0]-x)**2+(centres[:,2]-z)**2<=p['PegRootRadius']**2)&(centres[:,1]<=p['RootDepth'])
 for z in [max(rack['rows_mm']),min(rack['rows_mm'])]:fixed|=(abs(centres[:,2]-z)<=p['CollectorHeight']/2)&(centres[:,1]<=p['RootDepth'])
 for tool in rack['tools']:
  u=np.array(tool['axis']);q=centres-np.array(tool['tip']);t=q@u
  fixed|=(np.linalg.norm(q-t[:,None]*u,axis=1)<=tool['outer_radius']+.02)&(t>=-foot)&(t<=tool['burial']+.03)
 return fixed

def planes_mask(centres,rack,clock,width):
 p=rack['density_parameters'];mask=np.zeros(len(centres),dtype=bool);theta=np.radians(clock)
 for tool in rack['tools']:
  tip=np.array(tool['tip']);u=np.array(tool['axis']);mouth=np.array(tool['mouth']);rad=np.array([0.,0.,1.])-u*u[2];rad/=np.linalg.norm(rad)
  rad=rad*np.cos(theta)+np.cross(u,rad)*np.sin(theta)
  for sign in [-1,1]:
   vertices=[]
   for q in [tip-u*rack['parameters']['FloorDepth'],mouth-u*rack['parameters']['LeadDepth']]:
    shell=q+rad*(sign*(tool['outer_radius']-width/3));root=np.array([shell[0],5,shell[2]+sign*p['RootFanout']])
    for sx in [-1,1]:
     for sz in [-1,1]:vertices.extend([shell+[sx*width/2,0,sz*width/2],root+[sx*width/2,0,sz*p['RootWidth']/2]])
   eq=ConvexHull(vertices).equations;mask|=np.all(centres@eq[:,:3].T+eq[:,3]<=1e-7,axis=1)
 return mask

def boundary(X,rack,mode):
 back=abs(X[:,1])<1e-4
 if mode=='face':return back
 near=np.zeros(len(X),dtype=bool)
 for x in rack['columns_mm']:
  for z in rack['rows_mm']:near|=(X[:,0]-x)**2+(X[:,2]-z)**2<=3.5**2
 fix=back&near;assert fix.sum()>30,'Unresolved peg-root boundary'
 return fix
