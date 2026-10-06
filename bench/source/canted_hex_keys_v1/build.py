"""HX02: full-depth metric hex-key sockets, 30 degrees out from vertical.

Installed +Y points out from the board; +X is the user's left. Print on -X.
The longest socket is at the bed cheek and the bank gets shorter toward +X.
"""
from pathlib import Path
import json, math, sys, importlib.util
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'bench/source/bespoke_tools_v1'))
import build as B
K=B.K;V=A.Vector
OUT=ROOT/'bench/reviews/canted-hex-keys-v1/HX02'
INPUT=Path(__file__).with_name('key_set.json')
DATA=json.loads(INPUT.read_text())
U=V(0,.5,math.sqrt(3)/2);T=V(0,math.sqrt(3)/2,-.5)
CELLS=8;HALF=25.4*CELLS/2-1;PITCH=23.;MOUTH_Y=124.;MOUTH_Z=-12.

def socket_wire(p,r):
    # Circular clearance below, tangent 50-degree roof above in the cheek print.
    a=math.radians(50);cx=r*math.cos(a);cy=r*math.sin(a)
    q=lambda x,t:p+V(x,0,0)+T*t
    lo=q(cx,-cy);hi=q(cx,cy);apex=q(r/math.cos(a),0)
    return Part.Wire([Part.Arc(lo,q(-r,0),hi).toShape(),Part.makeLine(hi,apex),Part.makeLine(apex,lo)])

def key(af,length,short,p):
    # Given straight segment is exact. Bend radius and short arm are assumptions.
    radius=af/math.sqrt(3);bend=2*radius
    tip=p-U*(length-.06);a=tip+U*length
    b=a+U*bend+T*bend
    mid=a+U*(bend/math.sqrt(2))+T*(bend*(1-1/math.sqrt(2)))
    spine=Part.Wire([Part.makeLine(tip,a),Part.Arc(a,mid,b).toShape(),Part.makeLine(b,b+T*short)])
    points=[tip+V(radius*math.cos(i*math.pi/3),0,0)+T*(radius*math.sin(i*math.pi/3)) for i in range(6)]
    profile=Part.Wire(Part.makePolygon(points+[points[0]]).Edges)
    return spine.makePipeShell([profile],True,False)

def build():
    OUT.mkdir(parents=True,exist_ok=True)
    receiver,mount=K.receiver(CELLS,2,'right-cheek',z0=-57)
    parts=[receiver];holes=[];tools=[];seats=[]
    short_lengths=[15,18,20,23,29,33,38,44,50]
    for i,(item,short) in enumerate(zip(DATA['keys'],short_lengths)):
        af=item['across_flats'];length=item['straight_length'];x=92-i*PITCH
        p=V(x,MOUTH_Y,MOUTH_Z);radius=af/math.sqrt(3)+.35
        left=-HALF if i==8 else x-PITCH/2
        right=HALF if i==0 else x+PITCH/2
        yz=[]
        for q,t in [(-length-3,-10),(-length-3,10),(0,10),(0,-10)]:
            v=p+U*q+T*t;yz.append((v.y,v.z))
        parts.append(K.poly_prism(yz,'x',left,right))
        bore=Part.Face(socket_wire(p-U*length,radius)).extrude(U*(length-1.2))
        lead=Part.makeLoft([socket_wire(p-U*1.2,radius),socket_wire(p,radius+.8)],True,True)
        opening=Part.Face(socket_wire(p,radius+.8)).extrude(U*100)
        holes.extend([bore,lead,opening])
        tools.append(key(af,length,short,p))
        seats.append(dict(**item,x_mm=x,axis=[U.x,U.y,U.z],mouth=[p.x,p.y,p.z],socket_depth_mm=length,radial_clearance_mm=.35,lead_in_mm=1.2,tip_floor_mm=3,assumed_short_straight_mm=short,assumed_bend_radius_mm=2*af/math.sqrt(3)))
    # Continuous top tie joins every socket to the receiver. Both grow from the bed cheek.
    parts.append(K.poly_prism([(4.55,5.12),(118,-5),(118,-9),(4.55,1.12)],'x',-HALF,HALF))
    # Lower diagonal tie closes a triangulated beam behind the socket bank.
    parts.append(K.poly_prism([(4.55,-56),(117,-13),(117,-8),(4.55,-51)],'x',-HALF,HALF))
    low=V(0,MOUTH_Y,MOUTH_Z)-U*(217+3)+T*10
    parts.append(K.poly_prism([(4.55,5.12),(118,-5),(MOUTH_Y+T.y*10,MOUTH_Z+T.z*10),(low.y,low.z),(4.55,low.z)],'x',-HALF,-HALF+2))
    shape=B.union(parts).cut(B.union(holes)).removeSplitter()
    assert shape.isValid() and len(shape.Solids)==1,('native body',len(shape.Solids))
    rear=B.box(-300,-40,-400,600,40.15,800)
    a,b=shape.common(rear),receiver.common(rear);delta=a.cut(b).Volume+b.cut(a).Volume
    assert delta<1e-6,delta
    routes=[]
    for i,(tool,seat) in enumerate(zip(tools,seats)):
        assert tool.isValid() and len(tool.Solids)==1
        distance=seat['straight_length']+3
        peak=0;neighbor=0
        for k in range(math.ceil(distance/4)+1):
            travel=min(k*4,distance);moved=B.moved(tool,[0,U.y*travel,U.z*travel])
            peak=max(peak,shape.common(moved).Volume)
            for j in [i-1,i+1]:
                if 0<=j<len(tools):neighbor=max(neighbor,tools[j].common(moved).Volume)
        assert peak<1e-5 and neighbor<1e-5,(seat['across_flats'],peak,neighbor)
        # A further downward movement meets the closed socket floor.
        stop=shape.common(B.moved(tool,[0,-U.y*.2,-U.z*.2])).Volume
        assert stop>1e-5,('missing blind floor',seat['across_flats'],stop)
        routes.append(dict(af_mm=seat['across_flats'],max_intersection_mm3=peak,neighbor_intersection_mm3=neighbor,axial_withdrawal_mm=distance,outward_travel_mm=U.y*distance,upward_travel_mm=U.z*distance,downward_stop_intersection_mm3=stop,sample_step_mm=4))
    checks=dict(native_valid=True,solids=1,unchanged_board_side_delta_mm3=delta,tool_routes=routes,full_straight_legs_enclosed=True,limits='Nominal rigid tools, sampled axial withdrawal and blind-floor stop. Other tools above the rack are not modeled. Physical fit, friction, rotation, grip and bumps remain untested.')
    print('HX02 geometry, full-depth seats and withdrawal PASS',flush=True)
    pp,matrix=K.pose_transform(shape,'right-cheek');prefix='part-hx02__v1__right-cheek__fit-pf02c9-hoop5';assets={}
    for role,s in [('installed',shape),('print',pp),('tool-reference',Part.makeCompound(tools))]:
        step=OUT/(prefix+'__'+role+'.step');s.exportStep(str(step));again=Part.read(str(step))
        assert again.isValid() and len(again.Solids)==len(s.Solids)
        diff=s.cut(again).Volume+again.cut(s).Volume if role!='tool-reference' else abs(again.Volume-s.Volume)
        assert diff<(1e-4 if role!='tool-reference' else s.Volume*1e-5),(role,diff)
        stl=OUT/(prefix+'__'+role+'.stl');B.mesh(s,stl)
        assets[role+'_step']=step.name;assets[role+'_stl']=stl.name
    doc=A.newDocument('HX02v1');body=doc.addObject('PartDesign::Body','Holder');feature=body.newObject('PartDesign::Feature','HolderSolid');feature.Shape=shape
    feature.addProperty('App::PropertyString','BuildSource','Provenance');feature.BuildSource='bench/source/canted_hex_keys_v1/build.py'
    doc.recompute();assets['freecad']=prefix+'.FCStd';doc.saveAs(str(OUT/assets['freecad']));A.closeDocument(doc.Name)
    record=dict(id='HX02',name='Full-depth canted metric hex-key rack',version=1,prefix=prefix,cells=CELLS,pose='right-cheek',mount=mount,volume_mm3=shape.Volume,print_bounds_mm=B.bounds(pp),pose_matrix=K.pose_matrix(shape,'right-cheek'),assets=assets,checks=checks,tool_spec=dict(keys=seats,axis_angle_from_vertical_deg=30,short_arm_direction=[T.x,T.y,T.z],reference='Owner straight lengths; 4 mm interpolated. Short straight arms and bend radii are illustrative assumptions.'),load_point=[85,132,-18],source_sha256=B.sha(Path(__file__)),source_dependencies={str(p.relative_to(ROOT)):B.sha(p) for p in [INPUT,Path(B.__file__),Path(K.__file__)]},FreeCAD_version=A.Version(),files={p.name:dict(sha256=B.sha(p),bytes=p.stat().st_size) for p in OUT.iterdir() if p.suffix in ['.step','.stl','.FCStd']})
    (OUT/'report.json').write_text(json.dumps(record,indent=2)+'\n')
    fs=dict(step=assets['installed_step'],h=5.,supports=['pegs'],loads=[dict(id='sideways',point=record['load_point'],force=[5,0,0],radius=4),dict(id='down',point=record['load_point'],force=[0,0,-5],radius=4)])
    (OUT/(prefix+'__fea-spec.json')).write_text(json.dumps(fs,indent=2)+'\n')
    print('HX02 native exports PASS',flush=True)
if __name__=='__main__':build()
