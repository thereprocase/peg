"""CF01: three existing funnel apertures, cascading down from the user's right.

X points left when facing the board. Negative X is therefore the high right seat.
Upright printing keeps every funnel wall rooted on one continuous bed plane.
"""
from pathlib import Path
import sys,json
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'bench/source/bespoke_tools_v1'))
import build as B
K=B.K;V=A.Vector
ID='CF01'
BOTTOM=-114.8

def rect(w,l,z,x=0):
    return Part.makePolygon([V(x+u,48+v,z) for u,v in [(-w/2,-l/2),(w/2,-l/2),(w/2,l/2),(-w/2,l/2),(-w/2,-l/2)]])
def loft(stations,x):return Part.makeLoft([rect(w,l,z,x) for w,l,z in stations],True,True)

def cascade():
    receiver,info=K.receiver(4,4,'upright',z0=BOTTOM)
    parts=[receiver];holes=[];tools=[];seats=[]
    for label,x,dz in [('right',-25.0,0.),('middle',0.,-25.4),('left',25.0,-50.8)]:
        top=-10+dz;throat=-42+dz
        outer=loft([(19,56,throat),(30,84,top)],x)
        # Extended lower tubes all meet the bed, eliminating suspended starts.
        outer=outer.fuse(K.box(x-9.5,20,BOTTOM,19,56,throat-BOTTOM)).removeSplitter()
        edges=[e for e in outer.Edges if not (e.BoundBox.ZLength<1e-6 and (abs(e.CenterOfMass.z-BOTTOM)<1e-6 or abs(e.CenterOfMass.z-top)<1e-6))]
        outer=outer.makeFillet(2,edges)
        outer=outer.makeChamfer(.6,[e for e in outer.Edges if abs(e.BoundBox.ZMin-top)<1e-6 and abs(e.BoundBox.ZMax-top)<1e-6])
        parts.append(outer)
        # The web fills the short reach from plate to tube and starts on the bed.
        parts.append(K.box(x-15,5.4,BOTTOM,30,25,top-BOTTOM))
        holes.append(loft([(10.65625,47.125,throat-1),(22,76,top)],x))
        holes.append(loft([(14,48,BOTTOM-1),(14,48,throat-2.0),(11,48,throat)],x))
        holes.append(loft([(21.79375,75.475,top-.6),(23.434375,77.4875,top+.1),(21,74,top+2),(21,74,160)],x))
        # Closed-tool envelope, illustrative only: head, taper and separate handles.
        head=K.box(x-4,33,top-78,8,30,48)
        neck=loft([(8,30,top-31),(19,69,top+1)],x)
        handles=[K.box(x-9.5,y,top+.5,19,13,104) for y in [13.5,69.5]]
        tool=B.union([head,neck]+handles)
        tools.append(tool)
        seats.append(dict(position=label,x_mm=x,mouth_z_mm=top,throat_z_mm=throat,nominal_mouth_mm=[22,76],throat_mm=[11,48],exit_mm=[14,48]))
    shape=B.union(parts).cut(B.union(holes)).removeSplitter()
    return shape,receiver,info,tools,dict(id=ID,name='Right-high cascading tool funnels',cells=4,pose='upright',pickup_lift_mm=82,pickup_forward_mm=100,load_point=[-25.0,83,-14],tool_spec=dict(seats=seats,reference='Existing rectangular-tool-funnel v3 apertures. Generic closed-tool clearance envelopes; photo sets arrangement, not measured tool geometry.',center_spacing_mm=25.0,step_up_toward_right_mm=25.4),description='Three edge-on funnel seats at 25.0 mm centres. Right seat highest; each seat steps down 25.4 mm toward the left. Existing v3 aperture dimensions retained on one four-column backplate.')

def main():
    B.hex_rack=cascade
    B.build(which='cascade')
    d=B.OUT/ID;p=d/'report.json';r=json.loads(p.read_text())
    r['source_sha256']=B.sha(Path(__file__))
    r['source_dependencies']={str(q.relative_to(ROOT)):B.sha(q) for q in [Path(B.__file__),Path(K.__file__)]}
    r['density']=dict(previous_three_modules_width_mm=146.4,new_width_mm=99.6,width_saved_mm=46.8,width_reduction_percent=31.9672131148)
    r['limits']='Prototype. Tool envelopes are illustrative, not measured Knipex/tool CAD. The original through-bores remain open; tool tips can extend below the cassette. Allow full vertical withdrawal before moving forward. Physical fit and hand access require a trial print.'
    p.write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
