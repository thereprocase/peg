"""CF01 v3: plain-mouth, three existing funnel apertures, cascading down from the user's right.

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
        parts.append(outer)
        # Rear webs sit 0.5 mm inside each side of the 19 mm tube footprint. The former 30 mm
        # rectangular webs made the tall side fins visible beside each funnel.
        parts.append(K.box(x-9,5.4,BOTTOM,18,25,top-BOTTOM))
        holes.append(loft([(10.65625,47.125,throat-1),(22,76,top)],x))
        holes.append(loft([(14,48,BOTTOM-1),(14,48,throat-2.0),(11,48,throat)],x))
        holes.append(loft([(22,76,top),(21,74,top+2),(21,74,160)],x))
        # Closed-tool envelope, illustrative only: head, taper and separate handles.
        head=K.box(x-4,33,top-78,8,30,48)
        neck=loft([(8,30,top-31),(19,69,top+1)],x)
        handles=[K.box(x-9.5,y,top+.5,19,13,104) for y in [13.5,69.5]]
        tool=B.union([head,neck]+handles)
        tools.append(tool)
        seats.append(dict(position=label,x_mm=x,mouth_z_mm=top,throat_z_mm=throat,nominal_mouth_mm=[22,76],throat_mm=[11,48],exit_mm=[14,48]))
    void=B.union(holes)
    shape=B.union(parts).cut(void).removeSplitter()
    # Coincident faces can yield a valid OCCT solid while dropping whole funnels.
    # Verify every intended funnel shell survives the complete body boolean.
    for outer in parts[1::2]:
        shell=outer.cut(void)
        missing=shell.cut(shape).Volume
        assert missing<1e-5, ('missing funnel shell',missing)
    assert shape.Volume>230000, shape.Volume
    return shape,receiver,info,tools,dict(id=ID,name='Right-high cascading tool funnels',cells=4,pose='upright',pickup_lift_mm=82,pickup_forward_mm=100,load_point=[-25.0,83,-14],tool_spec=dict(seats=seats,reference='Existing rectangular-tool-funnel v3 apertures. Generic closed-tool clearance envelopes; photo sets arrangement, not measured tool geometry.',center_spacing_mm=25.0,step_up_toward_right_mm=25.4),description='Three edge-on funnel seats at 25.0 mm centres. Right seat highest; each seat steps down 25.4 mm toward the left. Existing v3 aperture dimensions retained on one four-column backplate.')

def main():
    shape,receiver,mount,tools,spec=cascade()
    folder=ROOT/'bench/reviews/cascade-funnels-v3/CF01';folder.mkdir(parents=True,exist_ok=True)
    prefix='part-cf01__v3__upright__fit-pf02c9-hoop5'
    checks=B.validate(shape,receiver,tools,spec)
    pp,matrix=K.pose_transform(shape,spec['pose']);assets={}
    for role,solid in [('installed',shape),('print',pp),('tool-reference',Part.makeCompound(tools))]:
        step=folder/(prefix+'__'+role+'.step');solid.exportStep(str(step));again=Part.read(str(step))
        assert again.isValid() and len(again.Solids)==len(solid.Solids)
        delta=solid.cut(again).Volume+again.cut(solid).Volume if role!='tool-reference' else abs(again.Volume-solid.Volume)
        assert delta<(1e-4 if role!='tool-reference' else solid.Volume*1e-5),(role,delta)
        stl=folder/(prefix+'__'+role+'.stl');B.mesh(solid,stl)
        assets[role+'_step']=step.name;assets[role+'_stl']=stl.name
    doc=A.newDocument('CF01v3');body=doc.addObject('PartDesign::Body','Holder');feature=body.newObject('PartDesign::Feature','HolderSolid');feature.Shape=shape
    feature.addProperty('App::PropertyString','BuildSource','Provenance');feature.BuildSource='bench/source/cascade_funnels_v3/build.py'
    doc.recompute();assets['freecad']=prefix+'.FCStd';doc.saveAs(str(folder/assets['freecad']));A.closeDocument(doc.Name)
    record={**spec,'version':3,'prefix':prefix,'mount':mount,'volume_mm3':shape.Volume,'print_bounds_mm':B.bounds(pp),'pose_matrix':K.pose_matrix(shape,spec['pose']),'assets':assets,'checks':checks,'source_sha256':B.sha(Path(__file__)),'source_dependencies':{str(p.relative_to(ROOT)):B.sha(p) for p in [Path(B.__file__),Path(K.__file__)]},'FreeCAD_version':A.Version(),'files':{p.name:dict(sha256=B.sha(p),bytes=p.stat().st_size) for p in folder.iterdir() if p.suffix in ['.step','.stl','.FCStd']},'revision':'Trimmed each rear web from 30 to 18 mm, inset 0.5 mm inside its lower tube. Removes the tall projecting side fins. Funnel apertures, touching junctions, cascade and rear mounting geometry retained.'}
    (folder/'report.json').write_text(json.dumps(record,indent=2)+'\n')
    fs=dict(step=assets['installed_step'],h=4.0,supports=['pegs'],loads=[dict(id='sideways',point=spec['load_point'],force=[5,0,0],radius=4),dict(id='down',point=spec['load_point'],force=[0,0,-5],radius=4)])
    (folder/(prefix+'__fea-spec.json')).write_text(json.dumps(fs,indent=2)+'\n')
    print('CF01 v3 native geometry and removal: PASS',flush=True)
if __name__=='__main__':main()
