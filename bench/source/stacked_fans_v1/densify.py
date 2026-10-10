"""Contact-limited compression of the checked reference fan.
Keep the existing tool angles, fit and access envelopes. Translate each small
key toward the main fan only as far as the first analytic contact permits.
"""
from pathlib import Path
import json,copy,math,sys
import numpy as np
from layout import cloud,segments,path
from pack import contact_intervals
HERE=Path(__file__).resolve().parent

def nearest_vertical_gap(t,others):
 blocked=contact_intervals(t,others,cloud,segments,path)
 merged=[]
 for low,high in blocked[np.argsort(blocked[:,0])]:
  if merged and low<=merged[-1][1]:merged[-1][1]=max(merged[-1][1],float(high))
  else:merged.append([float(low),float(high)])
 hit=[(low,high) for low,high in merged if low<=0<=high]
 travel=min((hit[0][0]-.02,hit[0][1]+.02),key=abs) if hit else 0.
 for key in ('tip','mouth','top'):t[key][2]-=travel
 return travel

def compress(t,others,direction,limit):
 direction=np.array(direction,dtype=float);direction/=np.linalg.norm(direction)
 # In this orthogonal frame, the requested travel is minus Z.
 z=-direction;seed=np.eye(3)[np.argmin(abs(z))]
 x=np.cross(seed,z);x/=np.linalg.norm(x);y=np.cross(z,x)
 frame=np.array([x,y,z]);items=copy.deepcopy([t]+others)
 for q in items:
  for key in ('tip','mouth','top','axis','bar_axis'):q[key]=(frame@q[key]).tolist()
 blocked=contact_intervals(items[0],items[1:],cloud,segments,path,frame@np.array([0,1,0]))
 blocked=blocked[blocked[:,1]>1e-5]
 travel=max(0.,min(limit,float(blocked[:,0].min())-.02)) if len(blocked) else limit
 for key in ('tip','mouth','top'):t[key]=(np.array(t[key])+direction*travel).tolist()
 return travel

def densify():
 data=json.loads((HERE/'reference-layout.json').read_text());comparisons=[]
 for rack in data['racks']:
  tools=rack['tools'];moves=[]
  if rack['id']=='HX05B':
   # The middle small key already occupies a low access pocket. Tuck the
   # two higher keys first; nearest safe vertical gaps preserve that pocket.
   for t in (tools[-3],tools[-1]):
    for key in ('tip','mouth','top'):t[key][0]-=60.
    dz=nearest_vertical_gap(t,[q for q in tools if q is not t])
    moves.append(dict(tool=t['name'],direction=(-1,0,0),travel_mm=60.,vertical_correction_mm=-dz))
  for direction in ((-1,0,0),(0,0,-1),(-1,0,0)):
   for t in tools[-3:]:
    travel=compress(t,[q for q in tools if q is not t],direction,100.)
    moves.append(dict(tool=t['name'],direction=direction,travel_mm=travel))
  low=min(t['tip'][0]-t['outer_radius'] for t in tools)
  high=max(t['mouth'][0]+t['outer_radius'] for t in tools)
  shift=np.array([-(low+high)/2,0,-max(t['mouth'][2]+t['outer_radius'] for t in tools)])
  for t in tools:
   for key in ('tip','mouth','top'):t[key]=(np.array(t[key])+shift).tolist()
  rack['offset']=(np.array(rack['offset'])+shift).tolist();rack['density_revision']=2
  width=2*math.ceil(max(abs(t[k][0])+t['outer_radius']+6 for t in tools for k in ('tip','mouth')))
  height=5.445-min(t['tip'][2]-t['outer_radius']-6 for t in tools)
  comparisons.append(dict(id=rack['id'],width_mm=width,height_mm=height,moves=moves))
 return data,comparisons
if __name__=='__main__':
 dst=Path(sys.argv[1]);dst.mkdir(parents=True,exist_ok=True);data,comparison=densify()
 (dst/'layout.json').write_text(json.dumps(data,indent=2)+'\n')
 (dst/'density.json').write_text(json.dumps(comparison,indent=2)+'\n');print(json.dumps(comparison,indent=2))
