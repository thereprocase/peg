"""Three native FreeCAD holders; run with FreeCAD's Python and this repository.

Tool reference shapes are dimensioned design envelopes. Exact manufacturer surfaces,
physical fit, slicing and load ratings require further evidence.
"""
from pathlib import Path
import hashlib,json,math,sys,argparse
import FreeCAD as A
import Part,MeshPart
ROOT=Path(__file__).resolve().parents[3]
SNAP=ROOT/'bench/source/gallery_current_mounts_v1/station_snapshot'
sys.path.insert(0,str(SNAP/'source/solder_v12'))
import common as K
V=A.Vector
OUT=ROOT/'bench/reviews/bespoke-tools-v1'
FONT='/usr/share/fonts/TTF/DejaVuSans.ttf'

def box(x,y,z,w,d,h):return Part.makeBox(w,d,h,V(x,y,z))
def cylinder(r,h,x,y,z,axis=V(0,0,1)):return Part.makeCylinder(r,h,V(x,y,z),axis)
def union(shapes):return shapes[0].multiFuse(shapes[1:]).removeSplitter()
def moved(s,v):
    t=s.copy();t.translate(V(*v));return t

def text_shape(text,x,y,z,size=3.5):
    faces=[Part.Face(w,'Part::FaceMakerBullseye') for w in Part.makeWireString(text,FONT,size) if w]
    s=Part.makeCompound(faces);b=s.BoundBox;s.translate(V(-(b.XMin+b.XMax)/2,-(b.YMin+b.YMax)/2,0))
    s.rotate(V(),V(1,0,0),90);s.rotate(V(),V(0,0,1),180)
    s=Part.makeCompound([f.extrude(V(0,.65,0)) for f in s.Faces]);s.translate(V(x,y-.15,z));return s

def mesh(shape,path):
    return K.write(shape,path,lin=.005)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bounds(s):
    b=s.optimalBoundingBox();return [b.XLength,b.YLength,b.ZLength]

def hex_prism(af,points,axis,length):
    r=af/math.sqrt(3);vs=[]
    for i in range(6):
        a=math.radians(30+60*i)
        # Cross-section in XY for the vertical leg, XZ for the horizontal arm.
        vs.append(V(points[0]+r*math.cos(a),points[1]+(r*math.sin(a) if axis=='z' else 0),points[2]+(r*math.sin(a) if axis=='y' else 0)))
    return Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(0,0,length) if axis=='z' else V(0,length,0))

def hex_reference(af,L,short,x,y,top):
    # Sweep one hex section around a tangent quarter-circle. Arm dimensions follow
    # the cited long-key table; bend radius remains an explicit design assumption.
    r=af/math.sqrt(3);R=2*r
    start=V(0,0,L);bend=V(0,0,R);end=V(0,R,0)
    arc=Part.Arc(bend,V(0,R-R/math.sqrt(2),R-R/math.sqrt(2)),end).toShape()
    spine=Part.Wire([Part.makeLine(start,bend),arc,Part.makeLine(end,V(0,short-r,0))])
    pts=[V(r*math.cos(math.radians(30+60*i)),r*math.sin(math.radians(30+60*i)),L) for i in range(6)]
    profile=Part.Wire(Part.makePolygon(pts+[pts[0]]).Edges)
    s=spine.makePipeShell([profile],True,False)
    s.rotate(V(),V(0,1,0),180);s.translate(V(x,y,top))
    return s

def hex_rack():
    cells=7;receiver,info=K.receiver(cells,2,'upright',z0=-57)
    hw=K.half_width(cells);floor=-53.8
    parts=[receiver,box(-hw,4.55,-57,2*hw,61.45,3.2)]
    # Low partitions retain the feet; tall rear guides locate the upright long legs.
    sizes=[1.5,2,2.5,3,4,5,6,8,10]
    lengths=[65,75,85,95,105,120,140,160,180];shorts=[15,18,20,23,29,33,38,44,50]
    tools=[];seats=[]
    for i,(af,L,short) in enumerate(zip(sizes,lengths,shorts)):
        x=72-i*18;r=af/math.sqrt(3);y=12
        # A conservative elbow plus exact hexagonal straight sections. The horizontal
        # foot sits on its lowest hex corner. Long leg faces upward for a short pickup.
        t=hex_reference(af,L,short,0,0,0)
        t.rotate(V(),V(0,1,0),180)
        t.translate(V(x,y,floor+r+.06))
        tools.append(t)
        half=r+1.2
        for side in [-1,1]:
            xx=x+half if side==1 else x-half-2
            parts.append(K.poly_prism([(4.55,-57),(4.55,-16),(14,-16),(23,-40),(23,-53.8)],'x',xx,xx+2))
        seats.append(dict(af_mm=af,x_mm=x,long_arm_mm=L,short_arm_mm=short,guide_clearance_mm=1.2))
    # Full-width lip and side webs make a stiff shallow tray. All start on the bed.
    parts.append(K.poly_prism([(62,-53.8),(62,-48),(64,-46),(66,-46),(66,-57),(62,-57)],'x',-hw,hw))
    for x in [-hw,hw-3]:parts.append(K.poly_prism([(4.55,-57),(4.55,-12),(66,-46),(66,-57)],'x',x,x+3))
    shape=union(parts)
    return shape,receiver,info,tools,dict(id='HX01',name='Open-front metric hex-key rack',cells=cells,pose='upright',pickup_lift_mm=9,pickup_forward_mm=70,load_point=[0,62,-52],tool_spec=dict(sizes=seats,reference='EGA Master long-pattern dimensions; swept hex sections; bend radius is an explicit assumption'),description='Nine upright L-keys, 1.5–10 mm. Short arms rest on the floor. Lift 9 mm and pull forward through the open guides.')

def tape_dock():
    cells=4;receiver,info=K.receiver(cells,2,'upright',z0=-57);hw=K.half_width(cells)
    parts=[receiver,box(-hw,4.55,-57,2*hw,55.45,3.2)]
    for x in [-hw,47]:
        parts.append(K.poly_prism([(4.55,-57),(4.55,-10),(17,-10),(60,-44),(60,-57)],'x',x,x+(hw-47)))
    parts.append(K.poly_prism([(56,-57),(56,-47),(58,-45),(60,-45),(60,-57)],'x',-hw,hw))
    shape=union(parts)
    shape=shape.cut(K.pointed_window(-22,22,-42,-6,'+Z',55)).removeSplitter()
    # Largest rectangular envelope covers the case plus belt clip. Smaller examples
    # are sampled independently, since these represent alternatives in one dock.
    tool=box(-46,7.55,-53.74,92,48,95)
    return shape,receiver,info,[tool],dict(id='TM01',name='Tape-measure dock',cells=cells,pose='upright',pickup_lift_mm=10,pickup_forward_mm=65,load_point=[0,55,-55],tool_spec=dict(case_width_max_mm=92,depth_including_clip_max_mm=48,reference='Conservative case-plus-clip envelope; product listings often describe retail packaging, so no exact brand fit is asserted',pocket_width_mm=94,pocket_depth_mm=50.45),description='A shallow open dock for a tape measure up to 92 mm across and 48 mm deep including its clip. Lift 10 mm and pull forward.')

def cable_hanger():
    cells=2;receiver,info=K.receiver(cells,2,'right-cheek');hw=K.half_width(cells)
    # Every body section is present on the bed cheek and grows continuously across X.
    # Rounded upper saddle supports a coiled lead bundle; the nose supplies retention.
    yz=[(4.55,-45),(4.55,-18),(12,-12),(20,-7),(26,-5),(32,-5),(39,-9),(44,-15),(48,-7),(51,-5),(54,-5),(54,-23),(16,-45)]
    shape=union([receiver,K.poly_prism(yz,'x',-hw,hw)])
    # Rounded rectangular coil envelope: 8 mm bundle, 80 mm overall coil width.
    outer=box(-40,22,-139,80,8,143)
    inner=box(-32,21,-131,64,10,127)
    # Top bearing is at z=-4, 1 mm above the saddle; settle model down .94 mm.
    outer=outer.makeFillet(12,[e for e in outer.Edges if e.BoundBox.YLength>7.9 and e.BoundBox.XLength<.01 and e.BoundBox.ZLength<.01])
    inner=inner.makeFillet(4,[e for e in inner.Edges if e.BoundBox.YLength>9.9 and e.BoundBox.XLength<.01 and e.BoundBox.ZLength<.01])
    tool=outer.cut(inner);tool.translate(V(0,0,-.94))
    return shape,receiver,info,[tool],dict(id='CL01',name='Coiled test-lead hanger',cells=cells,pose='right-cheek',pickup_lift_mm=13,pickup_forward_mm=65,load_point=[0,42,-15],tool_spec=dict(bundle_thickness_mm=8,coil_width_mm=80,coil_height_mm=143,reference='Coil clearance envelope; cable bundle shape is user-arranged',seat_clearance_mm=.06),description='A broad saddle and raised nose hold coiled test leads or USB cables. Lift the coil over the nose and pull forward.')

def validate(shape,receiver,tools,spec):
    assert shape.isValid() and len(shape.Solids)==1,(spec['id'],shape.isValid(),len(shape.Solids))
    rear=box(-300,-40,-400,600,40.15,800)
    a,b=shape.common(rear),receiver.common(rear)
    delta=a.cut(b).Volume+b.cut(a).Volume
    assert delta<1e-6,delta
    checks={'native_valid':True,'solids':1,'unchanged_board_side_delta_mm3':delta,'tool_routes':[],'tool_neighbor_clearances_mm':[]}
    for i,t in enumerate(tools):
        assert t.isValid()
        vol=shape.common(t).Volume;assert vol<1e-6,(spec['id'],i,'seated',vol)
        distance=shape.distToShape(t)[0]
        poses=[]
        for k in range(21):poses.append((0,0,spec['pickup_lift_mm']*k/20))
        for k in range(1,21):poses.append((0,spec['pickup_forward_mm']*k/20,spec['pickup_lift_mm']))
        peak=0
        for v in poses:
            moving=moved(t,v);peak=max(peak,shape.common(moving).Volume)
            for j,other in enumerate(tools):
                if i!=j:peak=max(peak,other.common(moving).Volume)
        assert peak<1e-6,(spec['id'],i,'route',peak)
        checks['tool_routes'].append({'tool_index':i,'seated_clearance_mm':distance,'sampled_poses':len(poses),'max_intersection_mm3':peak,'lift_mm':spec['pickup_lift_mm'],'forward_mm':spec['pickup_forward_mm']})
        for other in tools[i+1:]:checks['tool_neighbor_clearances_mm'].append(t.distToShape(other)[0])
    checks['limits']='Sampled rigid tool-envelope pickup checks. Physical fit, support removal, stiffness, loads, and complete holder installation require testing. Tool shape assumptions are in reference metadata.'
    return checks

def build(which=None):
    OUT.mkdir(parents=True,exist_ok=True);summaries=[]
    for make in [hex_rack,tape_dock,cable_hanger]:
        if which and make.__name__!=which:continue
        print('Building',make.__name__,flush=True)
        shape,receiver,mount,tools,spec=make();folder=OUT/spec['id'];folder.mkdir(exist_ok=True)
        prefix='part-'+spec['id'].lower()+'__v1__'+spec['pose']+'__fit-pf02c9-hoop5'
        checks=validate(shape,receiver,tools,spec);print('Geometry and pickup PASS',spec['id'],flush=True)
        pp,matrix=K.pose_transform(shape,spec['pose']);assets={}
        for role,s in [('installed',shape),('print',pp),('tool-reference',Part.makeCompound(tools))]:
            step=folder/(prefix+'__'+role+'.step');s.exportStep(str(step));r=Part.read(str(step))
            diff=s.cut(r).Volume+r.cut(s).Volume if role!='tool-reference' else abs(s.Volume-r.Volume)
            limit=1e-4 if role!='tool-reference' else s.Volume*1e-5
            assert r.isValid() and len(r.Solids)==len(s.Solids) and diff<limit,(role,diff,len(s.Solids),len(r.Solids))
            stl=folder/(prefix+'__'+role+'.stl');mesh(s,stl)
            assets[role+'_step']=step.name;assets[role+'_stl']=stl.name
        doc=A.newDocument(spec['id']);body=doc.addObject('PartDesign::Body','Holder');feature=body.newObject('PartDesign::Feature','HolderSolid');feature.Shape=shape
        for name,value in [('Cells',spec['cells']),('GridPitch',25.4),('RearPlane',.15)]:feature.addProperty('App::PropertyFloat',name,'Dimensions');setattr(feature,name,value)
        feature.addProperty('App::PropertyString','BuildSource','Provenance');feature.BuildSource='bench/source/bespoke_tools_v1/build.py'
        doc.recompute();doc.saveAs(str(folder/(prefix+'.FCStd')));A.closeDocument(doc.Name);assets['freecad']=prefix+'.FCStd'
        record={**spec,'prefix':prefix,'mount':mount,'volume_mm3':shape.Volume,'print_bounds_mm':bounds(pp),'pose_matrix':K.pose_matrix(shape,spec['pose']),'assets':assets,'checks':checks,'source_sha256':sha(Path(__file__)),'FreeCAD_version':A.Version(),'files':{f.name:{'sha256':sha(f),'bytes':f.stat().st_size} for f in folder.iterdir() if f.suffix in ['.step','.stl','.FCStd']}}
        fea_spec=dict(step=assets['installed_step'],h=2.5,supports=['pegs'],loads=[dict(id='sideways',point=spec['load_point'],force=[5,0,0],radius=4),dict(id='down',point=spec['load_point'],force=[0,0,-5],radius=4)])
        (folder/(prefix+'__fea-spec.json')).write_text(json.dumps(fea_spec,indent=2)+'\n')
        (folder/'report.json').write_text(json.dumps(record,indent=2)+'\n');summaries.append(record)
    print('Complete:',[r['id'] for r in summaries],flush=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--only');build(parser.parse_args().only)
