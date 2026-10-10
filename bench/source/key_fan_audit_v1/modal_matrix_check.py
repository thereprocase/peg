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
w,V=eigsh(K,k=5,M=M,sigma=0,which='LM',tol=1e-8,maxiter=500,ncv=30);freq=np.sqrt(w)/(2*np.pi);assert np.all(w>0)
reference=json.loads((a.root/'modal/face/result.json').read_text());expected=np.array([q['frequency_Hz'] for q in reference['modes']]);relative=np.abs(freq-expected)/expected
residual=[]
for i in range(5):
 left=K@V[:,i];right=w[i]*(M@V[:,i]);residual.append(float(np.linalg.norm(left-right)/(np.linalg.norm(left)+np.linalg.norm(right))))
orthogonality=float(np.max(np.abs(V.T@(M@V)-np.eye(5))));assert max(relative)<2e-5 and max(residual)<1e-5 and orthogonality<1e-6
r=dict(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),matrix_export=json.loads((out/'export.json').read_text()),scipy_version=scipy.__version__,dofs=K.shape[0],stiffness_nonzeros=K.nnz,mass_nonzeros=M.nnz,frequency_Hz=freq.tolist(),ccx_frequency_Hz=expected.tolist(),frequency_relative_difference=relative.tolist(),normalized_eigen_residuals=residual,mass_orthogonality_max_error=orthogonality,seconds=time.monotonic()-start,passed=True,scope='Independent sparse eigensolution of the same face-clamped h7 modal matrices. Checks algebra, not physical modelling or mesh convergence. Raw matrices remain on compute box.')
(out/'check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2),flush=True)
