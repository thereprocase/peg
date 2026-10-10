"""Handles first: independently rotated, staggered fans inspired by HX04.
X right across board; Y toward user; Z up, mm. No optimiser/search.
Tool handle centres define the layout; shaft ends and guides follow from lengths.
"""
from pack import settle
from functools import lru_cache
from pathlib import Path
import json, math, copy
import numpy as np
HERE=Path(__file__).resolve().parent
DATA=HERE.parent/'final_racks_v1/study'
PITCH=254.
SETS=[('HX05C','13190','inch',0),('HX05B','13189','metric',1),('HX05A','33034','Torx',2)]

@lru_cache(maxsize=1)
def layout():
    racks=[]
    for ident,number,name,tier in SETS:
        ts=json.loads((DATA/f'tee_{number}.json').read_text()); tools=[]
        last_L=ts[-1]['overall']-9.
        big_dx=math.sqrt(last_L**2-105.**2-(.4*last_L)**2)
        # Three short keys curl onto an upper-right deck. Long shafts occupy
        # the lower band underneath it, each with its own angle and floor.
        ordered=list(enumerate(ts[3:],3))+list(enumerate(ts[:3]))
        for i,t in ordered:
            L=t['overall']-9.
            if i>=3:
                f=(i-3)/(len(ts)-4)
                dx=25.+(big_dx-25.)*f;dy=65.+40*f
                dz=math.sqrt(L*L-dx*dx-dy*dy)
                # Translate every longer shaft left AND down beneath the last.
                # The earlier clustered-floor construction wasted handle width.
                j=i-3
                top=np.array([-130.-6.*j+dx,125.,-200.-5.*j+dz])
            else:
                deck_z={'13190':-100.,'13189':-30.,'33034':-65.}[number]
                top=np.array([40.+55.*i,70.,deck_z])
                # Parallel small-key deck: withdrawal must not converge into
                # the neighboring grip. The long-tool run supplies the fan.
                dx=L*.7;dy=L*.2
            dz=math.sqrt(L*L-dx*dx-dy*dy)
            u=np.array([dx,dy,dz])/L
            # Keep the grip in the Y/Z plane, tipping its front end downward.
            # This preserves front-end access without pulling each larger
            # handle sideways into its smaller neighbor's grasp space.
            b=np.array([0.,u[2],-u[1]]);b/=np.linalg.norm(b)
            tip=top-u*L
            size=t.get('p2p',t['af']);guide=max(40.,8*size);D=guide+3
            outer=(t['af']+.38+3)/math.sqrt(3)+3.
            tools.append(dict(t,axis=u.tolist(),tip=tip.tolist(),mouth=(tip+u*D).tolist(),top=top.tolist(),bar_axis=b.tolist(),guide=guide,burial=D,outer_radius=outer,elevation=math.degrees(math.asin(u[2]))))
        for i,t in enumerate(tools[:len(ts)-3]):settle(t,tools[:i],cloud,segments,path)
        # Apply the same constructive clearance calculation upward for the
        # small-key deck, using a reflected coordinate frame.
        for i in range(len(ts)-3,len(ts)):
            reflected=copy.deepcopy(tools[:i+1])
            for q in reflected:
                for key in ('tip','mouth','top','axis','bar_axis'):q[key][2]*=-1
            lift=settle(reflected[-1],reflected[:-1],cloud,segments,path)
            for key in ('tip','mouth','top'):tools[i][key][2]+=lift
            tools[i]['upward_packing_mm']=lift
        # Common 1-inch grid datum; the handle arrangement stays unchanged.
        # Centre each support footprint, retaining the same spiral handedness.
        low=min(t['tip'][0]-t['outer_radius'] for t in tools)
        high=max(t['mouth'][0]+t['outer_radius'] for t in tools)
        xshift=-(low+high)/2
        # Top hook row is the common grid datum. Avoid adding a whole board
        # row of blank plate merely to round the socket height upward.
        zshift=-max(t['mouth'][2]+t['outer_radius'] for t in tools)
        for t in tools:
            for key in ('tip','mouth','top'):t[key]=(np.array(t[key])+[xshift,0,zshift]).tolist()
        racks.append(dict(id=ident,set=number,name=name,tier=tier,z=tier*PITCH,tools=tools,offset=[xshift,0,zshift]))
    return racks

def segments(t,hand=False):
    p,u,c,b=map(np.array,(t['tip'],t['axis'],t['top'],t['bar_axis']))
    if hand:return [(c+b*(t['bar']/2-18),c+b*(t['bar']/2-3),25.)]
    return [(p,c,t.get('p2p',t['af']*2/math.sqrt(3))/2),(c-b*(t['bar']/2-9),c+b*(t['bar']/2-9),9.)]

def cloud(segs,step=2.):
    points=[];r=[]
    for a,b,rad in segs:
        n=max(2,math.ceil(np.linalg.norm(b-a)/step)+1)
        points.extend(np.linspace(a,b,n));r.extend([rad+step/2]*n)
    return np.array(points),np.array(r)

def path(t,step=2.):
    u=np.array(t['axis']);d=t['burial']+5.
    return np.linspace(np.zeros(3),u*d,math.ceil(d/step)+1)
if __name__=='__main__':print(json.dumps(dict(pitch=PITCH,racks=layout()),indent=2))
