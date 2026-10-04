"""Analytical current-fit pegs with holder-side +20% joining nubs; FreeCAD Python."""
from pathlib import Path
import argparse,hashlib,json,sys
import FreeCAD as A
import Part,MeshPart
R=Path(__file__).resolve().parents[3]
SNAP=R/'bench/source/gallery_current_mounts_v1/station_snapshot'
sys.path.insert(0,str(SNAP/'source/solder_v12'))
import common as K
V=A.Vector
FACE=.15;EMBED=2.;SCALE=1.2

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def region(z0,z1,y1=FACE):return Part.makeBox(100,y1+60,z1-z0,V(-50,-60,z0))
def difference(a,b):return a.cut(b).Volume+b.cut(a).Volume

def with_nub(functional,diameter):
    nub=Part.makeCylinder(diameter*SCALE/2,EMBED,V(0,FACE,.12),V(0,1,0))
    shape=functional.fuse(nub).removeSplitter()
    assert shape.isValid() and len(shape.Solids)==1
    delta=difference(shape.common(region(-50,50)),functional)
    assert delta<1e-7,delta
    # Real volumetric union with a flush holder blank, not a surface-only butt joint.
    blank=Part.makeBox(20,5,20,V(-10,FACE,-10))
    assert shape.common(blank).Volume>1
    joined=shape.fuse(blank).removeSplitter();assert joined.isValid() and len(joined.Solids)==1
    return shape,{'shaft_reference_diameter_mm':diameter,'nub_diameter_mm':diameter*SCALE,'diameter_scale':SCALE,'holder_plane_y_mm':FACE,'embed_mm':EMBED,'hole_axis_z_mm':.12,'board_side_symmetric_difference_mm3':delta,'sample_holder_overlap_mm3':shape.common(blank).Volume,'sample_union_one_solid':True}

def native_doc(name,shapes,out):
    doc=A.newDocument(name.replace('-','_'));features=[]
    for i,shape in enumerate(shapes):
        body=doc.addObject('PartDesign::Body','Peg'+str(i+1));f=body.newObject('PartDesign::Feature','AnalyticalPeg'+str(i+1));f.Label='Current peg + joining nub';f.Shape=shape
        datum=body.newObject('PartDesign::Plane','HolderRearPlane'+str(i+1));datum.Label='Holder rear plane · Y = 0.15 mm';datum.Placement=A.Placement(V(0,FACE,.12),A.Rotation(V(0,0,1),V(0,1,0)));body.Tip=f
        f.addProperty('App::PropertyLength','JoiningDepth','Interface').JoiningDepth=EMBED
        features.append(f)
    doc.recompute();doc.saveAs(str(out/(name+'.FCStd')));A.closeDocument(doc.Name)
    loaded=A.openDocument(str(out/(name+'.FCStd')))
    assert all(f.Shape.isValid() for f in loaded.Objects if f.TypeId=='PartDesign::Feature')
    A.closeDocument(loaded.Name)

def build(out):
    out.mkdir(parents=True,exist_ok=True);upright,_=K.receiver(1,1,'upright');cheek,_=K.receiver(1,1,'right-cheek')
    top=upright.common(region(-10,15));lo=upright.common(region(-40,-10));lc=cheek.common(region(-40,-10));lo.translate(V(0,0,25.4));lc.translate(V(0,0,25.4))
    old=K.P.FIT_SOURCE;K.P.FIT_SOURCE=K.G.fit_file(.49)
    ref=K.P.load_reference();K.P.FIT_SOURCE=old
    locator=next(s for s in ref.Solids if s.BoundBox.ZMax<-9.9).common(region(-40,-10));locator.translate(V(0,0,25.4))
    components=[]
    for name,label,source,diam in [('upper-hook','PF02 #9 upper hook',top,5.6),('lower-hoop-upright','PF07 #5 lower hoop · upright',lo,6.35),('lower-hoop-cheek','PF07 #5 lower hoop · cheek',lc,6.35),('bearing-locator','120° intermediate bearing locator',locator,6.35)]:
        shape,info=with_nub(source,diam);components.append((name,label,[shape],info))
    for pose,index in [('upright',1),('cheek',2)]:
        upper=components[0][2][0].copy();lower=components[index][2][0].copy();lower.translate(V(0,0,-25.4))
        components.append(('pair-'+pose,'Pre-spaced hook + hoop pair · '+pose,[upper,lower],{'pitch_mm':25.4,'separate_solids':2,'holder_plane_y_mm':FACE,'embed_mm':EMBED,'component_ids':['upper-hook',components[index][0]]}))
    records=[]
    for short,label,shapes,info in components:
        name='peg-'+short+'__v1__pf02c9-hoop5__nub120';shape=shapes[0] if len(shapes)==1 else Part.makeCompound(shapes)
        paths={}
        for ext,method in [('step','exportStep'),('iges','exportIges'),('brep','exportBrep')]:
            p=out/(name+'.'+ext);getattr(shape,method)(str(p));reread=Part.read(str(p))
            if ext=='iges':
                reread.sewShape()
                solids=[Part.makeSolid(shell) for shell in reread.Shells if shell.isClosed()]
                reread=Part.makeCompound(solids)
            assert reread.isValid();assert len(reread.Solids)==len(shapes),(short,ext,len(reread.Solids))
            delta=difference(shape,reread);assert delta<1e-5,(short,ext,delta);paths[ext]=p.name
        native_doc(name,shapes,out);paths['freecad']=name+'.FCStd'
        mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.005,AngularDeflection=.05,Relative=False);mesh.write(str(out/(name+'.stl')));paths['stl']=name+'.stl'
        cylinders=sum(type(f.Surface).__name__=='Cylinder' for f in shape.Faces);assert cylinders>0
        record={'id':short,'name':label,'prefix':name,'assets':paths,'interface':info,'analytical_cylindrical_faces':cylinders,'analytic_face_types':sorted(set(type(f.Surface).__name__ for f in shape.Faces)),'solids':len(shapes),'volume_mm3':shape.Volume,'hashes':{k:sha(out/v) for k,v in paths.items()}};records.append(record)
        print(short,'native solids/arcs and 20% nub PASS',flush=True)
    source_paths=[Path(__file__)]+[p for p in SNAP.rglob('*') if p.is_file()]
    data={'version':'peg-connectors-v1','units':'mm','holder_plane_y_mm':FACE,'nub_depth_mm':EMBED,'diameter_scale':SCALE,'fit':'PF02 #9 / PF07 #5 clipped roots','mesh_tessellation':{'linear_deflection_mm':.005,'angular_deflection_rad':.05,'native_solid_source':True,'mesh_repairs':False},'geometry_source':'Analytical FreeCAD/OpenCascade solids. No STL-to-solid conversion. Existing lower locator imported from its original analytic STEP.','parts':records,'source_hashes':{str(p.relative_to(R)):sha(p) for p in source_paths},'limits':'Geometry integration exports, not a new physical fit or load rating. Completed holder installation and print/support strategy need checking. Nominal anchor-study certificates do not cover this interference fit.'};(out/'BUILD.json').write_text(json.dumps(data,indent=2)+'\n')
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('output',type=Path);build(a.parse_args().output)
