"""Independent envelope screen. Fine static covers preserve the 1 mm tip rule.
During axial withdrawal only the new shaft extension and the moving grip need a
new check: the remaining shaft stays on its already checked occupied centreline.
"""
from pathlib import Path
import sys,json
import numpy as np
from scipy.spatial import cKDTree
from layout import *

def clearance(tree, rr, p, rad):
    near=cKDTree(p).sparse_distance_matrix(tree,float(rad.max()+rr.max()+20),output_type='ndarray')
    if len(near)==0:return 20.
    return float(np.min(near['v']-rad[near['i']]-rr[near['j']]))

def main():
    dst=Path(sys.argv[1]);dst.mkdir(parents=True,exist_ok=True)
    racks=json.loads((dst/'layout.json').read_text())['racks'] if '--saved' in sys.argv else layout()
    alltools=[]
    for rack in racks:
        for t in rack['tools']:
            offset=np.array([0,0,rack['z']]);p,r=cloud(segments(t),step=.5);alltools.append((rack,t,offset,p+offset,r))
    records=[]
    for i,(rack,t,offset,p,r) in enumerate(alltools):
        other=[x for j,x in enumerate(alltools) if j!=i];op=np.vstack([x[3] for x in other]);orr=np.concatenate([x[4] for x in other]);tree=cKDTree(op)
        hp,hr=cloud(segments(t,True),step=.5);hp+=offset
        gp,gr=cloud(segments(t)[1:],step=.5);gp+=offset
        c,u=np.array(t['top']),np.array(t['axis']);d=u*(t['burial']+5)
        ep,er=cloud([(c,c+d,segments(t)[0][2])],step=.5);ep+=offset
        stored=clearance(tree,orr,p,r);toolmin=clearance(tree,orr,ep,er);handmin=20.
        for move in path(t):
            toolmin=min(toolmin,clearance(tree,orr,gp+move,gr+1.))
            handmin=min(handmin,clearance(tree,orr,hp+move,hr+1.))
        for y in np.linspace(0,180,91):
            handmin=min(handmin,clearance(tree,orr,hp+[0,y,0],hr+1.))
        records.append(dict(rack=rack['id'],tool=t['name'],stored_bound=stored,withdrawal_bound=toolmin,hand_bound=handmin))
    pitch=racks[1]['z']-racks[0]['z']
    out=dict(scope='Stored tools, axial stroke of burial plus 5 mm, and front-end grasp approach. Subsequent free-hand removal is not modelled.',pitch=pitch,hand_proxy='50 mm diameter, 15 mm centre segment around the front end of the grip; 65 mm overall length',records=records,passed=all(min(r['stored_bound'],r['withdrawal_bound'],r['hand_bound'])>0 for r in records))
    (dst/'layout.json').write_text(json.dumps(dict(pitch=pitch,racks=racks),indent=2)+'\n');(dst/'access.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
