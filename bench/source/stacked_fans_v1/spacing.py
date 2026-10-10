"""Derive vertical separation directly from capsule XY overlaps, no trial layouts.
For each possible XY contact, put the upper point above the lower by the positive
sphere separation sqrt((r1+r2+margin)^2-dx^2-dy^2), then round up to a board row.
Conservative capsules bound tool, hand and individual guide/web solids.
"""
import json,math
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from layout import *

def body_cloud(rack):
    segs=[]
    for t in rack['tools']:
        p,u,m=map(np.array,(t['tip'],t['axis'],t['mouth']));R=t['outer_radius']
        for f in np.linspace(0,1,12):
            a=p-3*u;b=m.copy();a[1]=5.55+(a[1]-5.55)*f;b[1]=5.55+(b[1]-5.55)*f
            segs.append((a,b,R+1.5)) # covers web interpolation, intentionally overbounds at board
    return cloud(segs,3.)

def need(lower,upper):
    p,r=lower;q,s=upper
    near=cKDTree(p[:,:2]).sparse_distance_matrix(cKDTree(q[:,:2]),float(r.max()+s.max()+4),output_type='ndarray')
    if not len(near):return -1000.
    i,j=near['i'],near['j'];rr=r[i]+s[j]+4.;mask=near['v']<rr;i,j,rr,d=i[mask],j[mask],rr[mask],near['v'][mask]
    return float(np.max(p[i,2]-q[j,2]+np.sqrt(rr**2-d**2))) if len(i) else -1000.

def main():
    dst=Path(__import__('sys').argv[1]); data=json.loads((dst/'layout.json').read_text()); rs=data['racks'];maxneed=0.;limiter=None
    for lo,hi in zip(rs,rs[1:]):
        lowerclouds=[cloud(segments(t)) for t in lo['tools']]+[body_cloud(lo)]
        upperclouds=[cloud(segments(t)) for t in hi['tools']]+[body_cloud(hi)]
        lower=tuple(np.concatenate([x[k] for x in lowerclouds]) for k in (0,1));upper=tuple(np.concatenate([x[k] for x in upperclouds]) for k in (0,1))
        for rack,other,is_lower in ((lo,upper,True),(hi,lower,False)):
            for t in rack['tools']:
                for hand in (False,True):
                    p,r=cloud(segments(t,hand));moves=path(t,step=3.)
                    if hand:moves=np.vstack([moves,np.linspace([0,180,0],[0,0,0],61)])
                    for d in moves:
                        moving=(p+d,r+1.5)
                        n=need(moving,other) if is_lower else need(other,moving)
                        if n>maxneed:maxneed=n;limiter=dict(lower=lo['id'],upper=hi['id'],moving=rack['id'],tool=t['name'],hand=hand,translation=d.tolist())
    result=dict(required_mm=maxneed,pitch_mm=25.4*math.ceil(maxneed/25.4),margin_mm=4.,limiter=limiter)
    pitch=result['pitch_mm']
    for i,rack in enumerate(rs):rack['z']=i*pitch
    data['pitch']=pitch
    (dst/'layout.json').write_text(json.dumps(data,indent=2)+'\n')
    (dst/'spacing.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
if __name__=='__main__':main()
