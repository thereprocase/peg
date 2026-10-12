"""Affine strain, rigid modes and exact wrench checks for the new formulation."""
import json,numpy as np
from model import tet_data,elasticity,wrench
from screen import stress_tensor
sample=np.array([[1.,2.,3.,4.,5.,6.]])
assert np.array_equal(stress_tensor(sample)[0],[[1,6,5],[6,2,4],[5,4,3]])
q,_=np.linalg.qr(np.array([[1.,2.,3.],[3.,2.,1.],[1.,1.,4.]]))
for tensor in [np.diag([0.,0.,10.]),np.diag([-2.,5.,0.])]:
 assert np.allclose(np.linalg.eigvalsh(q@tensor@q.T),np.linalg.eigvalsh(tensor))
X=np.array([[0.,0.,0.],[2.,0.,0.],[0.,3.,0.],[0.,0.,4.]])
_,v,B,_=tet_data(X,np.array([[0,1,2,3]]));assert abs(v[0]-4)<1e-12
A=np.array([[.02,.03,.04],[.05,.06,.07],[.08,.09,.10]])
u=X@A.T;expected=np.array([A[0,0],A[1,1],A[2,2],A[1,2]+A[2,1],A[0,2]+A[2,0],A[0,1]+A[1,0]])
assert np.max(abs(B[0]@u.ravel()-expected))<1e-12
for omega in np.eye(3):assert np.linalg.norm(B[0]@np.cross(np.broadcast_to(omega,X.shape),X).ravel())<1e-12
for translation in np.eye(3):assert np.linalg.norm(B[0]@np.tile(translation,(4,1)).ravel())<1e-12
for ratio in [.35,.65,.9]:assert np.linalg.eigvalsh(elasticity(ratio)).min()>0
weights=np.array([1.,2.,3.,4.]);force=np.array([2.,-1.,3.]);torque=np.array([.5,2.,-3.]);point=np.array([7.,8.,9.]);f=wrench(X,weights,force,torque,point)
assert np.linalg.norm(f.sum(0)-force)<1e-10;assert np.linalg.norm(np.cross(X,f).sum(0)-(torque+np.cross(point,force)))<1e-10
print(json.dumps(dict(passed=True,stress_tensor_mapping=True,principal_rotation_invariance=True,affine_strain=True,six_rigid_modes=True,positive_definite_anisotropic_material=True,exact_force_and_moment=True,scope='Formulation checks only; not a physical validation or mesh convergence result.')))
