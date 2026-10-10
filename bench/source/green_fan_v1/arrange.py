"""Selected green fan: longer guides and T-bars clocked toward the board plane.
Geometric changes are constructed before any native CAD is generated.
"""
from pathlib import Path
import copy,json,math,sys
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'stacked_fans_v1'))
from densify import nearest_vertical_gap

def arrange():
 data=json.loads((HERE/'reference-layout.json').read_text())
 rack=next(r for r in data['racks'] if r['id']=='HX05C');ts=rack['tools']
 for i,t in enumerate(ts):
  t['guide']*=1.5;t['burial']=t['guide']+3
  u,b=np.array(t['axis']),np.array(t['bar_axis'])
  # A bar lying in the X/Z board plane is perpendicular to this shaft.
  # Rotate toward that bar, not toward a gravity-level horizontal bar.
  flat=np.array([u[2],0.,-u[0]]);flat/=np.linalg.norm(flat)
  angle=math.acos(np.clip(np.dot(b,flat),-1,1));turn=min(math.radians(30),angle)
  b=(b*math.sin(angle-turn)+flat*math.sin(turn))/math.sin(angle)
  fan_turn=2.5*i if i<len(ts)-3 else 0.
  a=math.radians(fan_turn);c,s=math.cos(a),math.sin(a)
  rotate=np.array([[c,0,s],[0,1,0],[-s,0,c]])
  u=rotate@u;b=rotate@b
  t.update(axis=u.tolist(),bar_axis=b.tolist(),elevation=math.degrees(math.asin(u[2])),bar_twist_toward_board_deg=math.degrees(turn),additional_fan_rotation_deg=fan_turn)
  for key,length in [('top',t['overall']-9),('mouth',t['burial'])]:t[key]=(np.array(t['tip'])+u*length).tolist()
 # The symmetric 3/32 grip is accessed at its opposite end. Reversing the bar
 # vector selects that grasp proxy; it does not change the physical T-bar.
 t=ts[-3];t['bar_axis']=(-np.array(t['bar_axis'])).tolist();t['grasp_end']='opposite end'
 # The 1/8 key moves sideways to the nearest safe gap around the 5/16
 # release path. Swap X/Z to reuse the analytic translation calculation;
 # the front approach remains +Y in this frame.
 reflected=copy.deepcopy(ts)
 for t in reflected:
  for key in ('tip','mouth','top','axis','bar_axis'):t[key]=[t[key][2],t[key][1],t[key][0]]
 correction=nearest_vertical_gap(reflected[-1],reflected[:-1])
 for key in ('tip','mouth','top'):ts[-1][key][0]-=correction
 ts[-1]['sideways_clearance_adjustment_mm']=-correction
 low=min(t['tip'][0]-t['outer_radius'] for t in ts);high=max(t['mouth'][0]+t['outer_radius'] for t in ts)
 shift=np.array([-(low+high)/2,0.,-max(t['mouth'][2]+t['outer_radius'] for t in ts)])
 for t in ts:
  for key in ('tip','mouth','top'):t[key]=(np.array(t[key])+shift).tolist()
 rack['offset']=(np.array(rack['offset'])+shift).tolist();rack['revision']='green-long-sleeves-v1'
 data['revision']='green-long-sleeves-v1'
 return data

if __name__=='__main__':
 out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
 data=arrange();(out/'layout.json').write_text(json.dumps(data,indent=2)+'\n')
 print('Green fan: 1.5x sleeves, 30-degree clock toward board, 0–15-degree added fan spread.')
