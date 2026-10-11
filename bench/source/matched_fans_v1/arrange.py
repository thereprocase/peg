"""Transfer the approved green fan frame to the metric and Torx sets.
One analytic contact placement, no CAD candidate search.
"""
from pathlib import Path
import copy,json,math,sys
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'stacked_fans_v1'))
from layout import cloud,segments,path
from pack import settle
from densify import nearest_vertical_gap,compress
ROOT=HERE.parents[2]
data=json.loads((ROOT/'bench/reviews/green-fan-v1/layout.json').read_text())
green=data['racks'][0]; main=green['tools'][:-3];deck=green['tools'][-3:]
def interpolate(f,key):
 i=min(int(f),len(main)-2);a=f-i
 return (1-a)*np.array(main[i][key])+a*np.array(main[i+1][key])
for rack in data['racks'][1:]:
 ts=rack['tools'];scale=max(t['overall'] for t in ts)/300.
 for i,t in enumerate(ts):
  size=t.get('p2p',t['af']);t['guide']=max(60.,12*size);t['burial']=t['guide']+3
  if i<len(ts)-3:
   f=i*(len(main)-1)/(len(ts)-4)
   u=interpolate(f,'axis');u/=np.linalg.norm(u)
   b=interpolate(f,'bar_axis');b-=u*np.dot(b,u);b/=np.linalg.norm(b)
   p=interpolate(f,'tip');p[[0,2]]*=scale;p[1]=60-40*i/(len(ts)-4)
  else:
   ref=deck[i-(len(ts)-3)];u=np.array(ref['axis']);b=np.array(ref['bar_axis'])
   top=np.array(ref['top']);top[[0,2]]*=scale
   p=top-u*(t['overall']-9)
  # Frontmost grip end drives the existing conservative approach model.
  if b[1]<0:b=-b
  t.update(axis=u.tolist(),bar_axis=b.tolist(),tip=p.tolist(),top=(p+u*(t['overall']-9)).tolist(),mouth=(p+u*t['burial']).tolist(),elevation=math.degrees(math.asin(u[2])))
 # Match the green fan's ordering while resolving set-specific handle lengths.
 for i,t in enumerate(ts[:-3]):settle(t,ts[:i],cloud,segments,path)
 for i in range(len(ts)-3,len(ts)):
  if rack['id']=='HX05A' and i==len(ts)-1:
   items=copy.deepcopy([ts[i]]+ts[:i])
   for q in items:
    for key in ('tip','mouth','top','axis','bar_axis'):q[key]=[q[key][2],q[key][1],q[key][0]]
   dx=nearest_vertical_gap(items[0],items[1:])
   for key in ('tip','mouth','top'):ts[i][key][0]-=dx
  else:nearest_vertical_gap(ts[i],ts[:i])
 # Tuck the upper deck toward the fan only until first reciprocal access contact.
 for direction in ((-1,0,0),(0,0,-1)):
  for t in ts[-3:]:compress(t,[q for q in ts if q is not t],direction,35.)
 low=min(t['tip'][0]-t['outer_radius'] for t in ts);high=max(t['mouth'][0]+t['outer_radius'] for t in ts)
 shift=np.array([-(low+high)/2,0,-max(t['mouth'][2]+t['outer_radius'] for t in ts)])
 for t in ts:
  for key in ('tip','mouth','top'):t[key]=(np.array(t[key])+shift).tolist()
 rack['revision']='matched-green-v1';rack['offset']=shift.tolist()
 print(rack['id'],'tools',len(ts),'guide range',min(t['guide'] for t in ts),max(t['guide'] for t in ts),'height',-min(t['tip'][2]-t['outer_radius']-6 for t in ts),flush=True)
data['revision']='matched-green-v1';data['minimum_upward_elevation_degrees']=10.
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
(out/'layout.json').write_text(json.dumps(data,indent=2)+'\n')
