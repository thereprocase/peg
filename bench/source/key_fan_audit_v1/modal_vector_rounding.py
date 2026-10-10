"""Independently solve and gate the exported CCX modal pencil using SciPy/SuperLU."""
from pathlib import Path
import argparse,json,hashlib,time
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import eigsh
import scipy
p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();out=a.root/'modal/matrix-face';start=time.monotonic()
def matrix(path):
 data=np.loadtxt(path);i=data[:,0].astype(np.int64)-1;j=data[:,1].astype(np.int64)-1;v=data[:,2];n=int(max(i.max(),j.max())+1);diagonal=i==j
 A=coo_matrix((v,(i,j)),shape=(n,n)).tocsr();A=A+A.T-coo_matrix((v[diagonal],(i[diagonal],j[diagonal])),shape=(n,n)).tocsr();A.eliminate_zeros();assert np.isfinite(A.data).all();print(path.name,n,A.nnz,flush=True);return A
K=matrix(out/'matrix.sti');M=matrix(out/'matrix.mas');assert K.shape==M.shape and np.all(M.diagonal()>0)
import re
mapping=[tuple(map(int,q.split('.'))) for q in (out/'matrix.dof').read_text().splitlines()]
assert len(mapping)==K.shape[0]
node=np.array([q[0] for q in mapping]);dof=np.array([q[1]-1 for q in mapping]);text=(a.root/'modal/face/modes.dat').read_text()
blocks=re.split(r'displacements[^\n]*\n',text)[1:];assert len(blocks)==5
vectors=[];uncertainties=[]
for block in blocks:
 U=np.zeros((int(node.max())+1,3));E=np.zeros_like(U)
 for line in block.splitlines():
  q=line.split()
  if len(q)==4 and q[0].isdigit():
   index=int(q[0])
   if index<len(U):
    U[index]=[float(x) for x in q[1:]]
    for k,value in enumerate(q[1:]):
     if float(value)!=0:
      mantissa,exponent=value.upper().split('E');digits=len(mantissa.split('.')[1]);E[index,k]=.5*10**(int(exponent)-digits)
 vectors.append(U[node,dof]);uncertainties.append(E[node,dof])
V=np.array(vectors).T;reference=json.loads((a.root/'modal/face/result.json').read_text());w=np.array([q['eigenvalue'] for q in reference['modes']]);residual=[];rounding_ratios=[];KA=abs(K);MA=abs(M)
for i in range(5):
 left=K@V[:,i];right=w[i]*(M@V[:,i]);residual.append(float(np.linalg.norm(left-right)/(np.linalg.norm(left)+np.linalg.norm(right))))
 epsilon_lambda=.5*10**(np.floor(np.log10(abs(w[i])))-6)
 bound=KA@uncertainties[i]+abs(w[i])*(MA@uncertainties[i])+epsilon_lambda*np.abs(M@V[:,i])+1e-12*(KA@abs(V[:,i])+abs(w[i])*(MA@abs(V[:,i])))
 rounding_ratios.append(float(np.max(np.abs(left-right)/np.maximum(bound,1e-20))))
gram=V.T@(M@V);norm=np.sqrt(np.diag(gram));normalized=gram/np.outer(norm,norm);orthogonality=float(np.max(np.abs(normalized-np.eye(5))))
r=dict(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),matrix_export=json.loads((out/'export.json').read_text()),scipy_version=scipy.__version__,dofs=K.shape[0],normalized_eigen_residuals=residual,max_component_residual_to_print_rounding_bound=rounding_ratios,mass_orthogonality_max_error=orthogonality,printed_mode_mass_norms=norm.tolist(),seconds=time.monotonic()-start,printed_residual_original_gate_passed=bool(max(residual)<1e-3 and orthogonality<1e-4),residuals_compatible_with_print_rounding=bool(max(rounding_ratios)<=1.01),scope='Independent sparse K*u=lambda*M*u and mass orthogonality check of six-decimal printed CCX mode vectors. Output rounding limits residual precision; Retains the failed original relative-residual gate and separately bounds the effect of printed U/eigenvalue precision using absolute sparse matrices. Compatibility with rounding is not an independent eigensolution or physical validation.')
(out/'printed-vector-rounding.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2),flush=True)
