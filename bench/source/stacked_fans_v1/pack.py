"""One-pass downward placement of independently rotated tools.
Three distinct constraints: 1 mm shaft surface gap, 2 mm between full lead-in
openings, and a front-end grasp envelope. No common centre or candidate search.
"""
import math
import numpy as np
from scipy.spatial import cKDTree

def forbidden(p,r,q,s,margin=1.):
    near=cKDTree(p[:,:2]).sparse_distance_matrix(cKDTree(q[:,:2]),float(r.max()+s.max()+margin),output_type='ndarray')
    if not len(near):return np.empty((0,2))
    i,j=near['i'],near['j'];rr=r[i]+s[j]+margin;ok=near['v']<rr
    i,j,rr,d=i[ok],j[ok],rr[ok],near['v'][ok]
    if not len(i):return np.empty((0,2))
    dz=p[i,2]-q[j,2]; width=np.sqrt(rr*rr-d*d)
    return np.column_stack([dz-width,dz+width])

def mouth(t):
    rad=(t['p2p']+.38)/2+1.5 if 'p2p' in t else (t['af']+.38+3)/math.sqrt(3)
    return np.array([t['mouth']]),np.array([rad])

def contact_intervals(t,previous,cloud,segments,path,approach=(0,1,0)):
    """Forbidden translations along minus Z, including reciprocal access."""
    if not previous:return np.empty((0,2))
    approach=np.array(approach)
    # Fine sphere cover gives a rigorous 1 mm lower bound, with at most 0.5 mm
    # extra sampling conservatism; this is not the hand/funnel clearance.
    cp,cr=cloud(segments(t),step=.5)
    ps=[cloud(segments(q),step=.5) for q in previous]
    op=np.vstack([x[0] for x in ps]);orr=np.concatenate([x[1] for x in ps])
    intervals=[]
    def drop(*args):
        intervals.append(forbidden(*args));return 0.
    shift=drop(cp,cr,op,orr,1.)
    for q in previous:shift=max(shift,drop(*mouth(t),*mouth(q),2.))
    # Withdrawal adds material only beyond the original shaft end; the shaft
    # within the socket simply slides along its already-clear occupied line.
    p,u,c=map(np.array,(t['tip'],t['axis'],t['top']));d=u*(t['burial']+5)
    seg=segments(t);extension=cloud([(c,c+d,seg[0][2])],step=1.)
    shift=max(shift,drop(*extension,op,orr,1.))
    gp,gr=cloud(seg[1:],step=1.);hp,hr=cloud(segments(t,True),step=1.)
    coarse_p,coarse_r=cloud(seg,step=1.)
    for move in path(t,step=3.):
        shift=max(shift,drop(gp+move,gr+1.5,op,orr,1.),drop(hp+move,hr+1.5,op,orr,1.))
    for y in np.linspace(0,180,61):
        shift=max(shift,drop(hp+approach*y,hr+1.5,op,orr,1.))
    for q,(qp,qr) in zip(previous,ps):
        qu,qc=map(np.array,(q['axis'],q['top']));qd=qu*(q['burial']+5)
        qseg=segments(q);ep,er=cloud([(qc,qc+qd,qseg[0][2])],step=1.);shift=max(shift,drop(cp,cr,ep,er,1.))
        qg,qgr=cloud(qseg[1:],step=1.);qh,qhr=cloud(segments(q,True),step=1.);qcp,qcr=cloud(qseg,step=1.)
        for move in path(q,step=3.):shift=max(shift,drop(cp,cr,qg+move,qgr+1.5,1.),drop(cp,cr,qh+move,qhr+1.5,1.))
        for y in np.linspace(0,180,61):shift=max(shift,drop(cp,cr,qh+approach*y,qhr+1.5,1.))
    return np.concatenate(intervals)

def settle(t,previous,cloud,segments,path):
    # Each possible contact forbids a finite translation interval. Merge only
    # the connected interval containing zero: never force a tool past another
    # tool that is already safely above/below it. This is an analytic placement,
    # not a series of candidate layouts.
    blocked=contact_intervals(t,previous,cloud,segments,path)
    blocked=blocked[blocked[:,1]>=0]
    blocked=blocked[np.argsort(blocked[:,0])]
    shift=0.
    for low,high in blocked:
        if low>shift:break
        shift=max(shift,float(high)+1e-7)
    if shift>0:
        for k in ('tip','mouth','top'):t[k][2]-=shift
    t['downward_packing_mm']=shift
    return shift
