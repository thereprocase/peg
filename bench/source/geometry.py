from pathlib import Path
import sys, json, math
import FreeCAD as A
import Part, Mesh, MeshPart
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'reference'))
from host_envelope import required_setback,max_flush_height,certify_host_polygon
from peg_interface import receive_pegs
V=A.Vector
P=25.4

def box(x,y,z,w,d,h): return Part.makeBox(w,d,h,V(x,y,z))
def cyl(x,y,z,r,h,axis=(0,0,1)): return Part.makeCylinder(r,h,V(x,y,z),V(*axis))
def cone(x,y,z,r1,r2,h): return Part.makeCone(r1,r2,h,V(x,y,z))
def union(shapes):
    shapes=[s for s in shapes if s and not s.isNull()]
    return shapes[0].multiFuse(shapes[1:]).removeSplitter() if len(shapes)>1 else shapes[0]
def cut(s,holes): return s.cut(Part.makeCompound(holes)).removeSplitter() if holes else s
def prism_yz(x,w,points):
    vs=[V(x,y,z) for y,z in points];return Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(w,0,0))
def prism_xy(z,h,points):
    vs=[V(x,y,z) for x,y in points];return Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(0,0,h))
def rounded(x,y,z,w,d,h,r=3):
    r=min(r,w/2-.01,d/2-.01)
    return union([box(x+r,y,z,w-2*r,d,h),box(x,y+r,z,w,d-2*r,h)]+[cyl(xx,yy,z,r,h) for xx in (x+r,x+w-r) for yy in (y+r,y+d-r)])
def prism_xz(y,d,points):
    vs=[V(x,y,z) for x,z in points];return Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(0,d,0))
def tube(x,y,z,ri,h,t=2.4): return cyl(x,y,z,ri+t,h).cut(cyl(x,y,z+2.4,ri,h+1))
def channel(x,y,z,w,d,h,t=2.4):
    return rounded(x,y,z,w,d,h).cut(rounded(x+t,y+t,z+t,w-2*t,d-2*t,h+1,1))
def beam(p,q,r):
    p,q=V(*p),V(*q);d=q-p
    return union([Part.makeCylinder(r,d.Length,p,d),Part.makeSphere(r,p),Part.makeSphere(r,q)])
def hoop(x,y,z,outer,inner,h): return cyl(x,y,z,outer,h).cut(cyl(x,y,z-.1,inner,h+.2))
def rot(s,axis,angle,center=(0,0,0)):
    s=s.copy();s.rotate(V(*center),V(*axis),angle);return s
def translated(s,x=0,y=0,z=0):
    s=s.copy();s.translate(V(x,y,z));return s

def make_envelope():
    data=json.loads((ROOT/'reference/conformal_motion_results.json').read_text())
    poses=data['removal_poses'];reserve=max_flush_height(poses)['maximum_physical_height_above_upper_hole_mm']-5
    curve=[(required_setback(poses,h+reserve)['required_design_y_mm'],h+.12) for h in [-240,5]+list(range(10,201,5))]
    poly=curve+[(220.15,200.12),(220.15,-239.88)]
    cert=certify_host_polygon(poses,poly);assert cert['passed']
    report={'vertices_yz':poly,'certificate':cert,'bounds':{'width':480,'front':220,'bottom':-240,'top':200},'source':'conformal_motion_results.json','nominal_flush_lip':5,'scope':'Continuous board-front clearance only'}
    (ROOT/'reviews').mkdir(parents=True,exist_ok=True)
    (ROOT/'reviews/expanded-envelope.json').write_text(json.dumps(report,indent=2))
    return prism_yz(-240,480,poly)

ENVELOPE=make_envelope()
from peg_profile import load_reference


def back(w,bottom=-32,top=5.12,thickness=5.4,windows=False):
    s=box(-w/2,.15,bottom,w,thickness,top-bottom)
    if windows and w>65:
        # Structural receiver columns are left solid; this is a host wall,
        # not a copy of the removed reference handle.
        opening=2*abs(mounts_for(w)[0])-16
        n=max(1,int(opening//23));cell=opening/n
        voids=[]
        for i in range(n):
            x0=-opening/2+i*cell+2;x1=x0+cell-4;mid=(x0+x1)/2
            lo=bottom+7;peak=top-10;shoulder=max(lo+2,peak-(x1-x0)/2)
            voids.append(prism_xz(0,7,[(x0,lo),(x1,lo),(x1,shoulder),(mid,peak),(x0,shoulder)]))
        s=cut(s,voids)
    return s
def rib(x,depth,z=0,bottom=-32,t=3):
    bottom=min(bottom,z-5)
    return prism_yz(x-t/2,t,[(.15,bottom),(6,bottom),(depth,z),(depth,z+2),(.15,z+2)])
def deck(w,d,z=-2,t=4,bottom=-32):
    return union([back(w,bottom),rounded(-w/2,.15,z,w,d,t),rib(-w/2+3,d,z,bottom),rib(w/2-3,d,z,bottom)])
def mounts_for(w):
    # Each original pair has upper retention and a lower antirotation locator.
    if w < 35.0:return [0.]
    pitch=max(1,int((w-9.6)//P))*P
    return [-pitch/2,pitch/2]

def integrate(host,w):
    # 0.30 mm relief on each module edge leaves 0.60 mm between tiled hosts.
    host=host.common(ENVELOPE).common(box(-w/2+.3,.15,-240,w-.6,220,440)).removeSplitter()
    assert host.isValid(), 'Invalid host'
    outside=host.cut(ENVELOPE).Volume
    result=host
    checks=[]
    for x in mounts_for(w):
        source=translated(load_reference(),x=x)
        result,report=receive_pegs(source,result)
        checks.append(report)
    assert result.isValid() and len(result.Solids)==1, f'Solids: {len(result.Solids)}'
    return result,host,{'host_outside_envelope_mm3':outside,'mount_columns_x':mounts_for(w),'peg_checks':checks,'reference_handle_removed':True,'single_valid_solid':True}

def export_mesh(shape,path):
    mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.07,AngularDeflection=.15,Relative=False)
    mesh.write(str(path));mesh=Mesh.Mesh(str(path))
    for method in ['removeDuplicatedPoints','removeDuplicatedFacets','harmonizeNormals']:
        getattr(mesh,method)()
    repaired=False
    if not mesh.isSolid():
        repaired=True;mesh.removeNonManifolds();mesh.removeNonManifoldPoints();mesh.fillupHoles(1000);mesh.harmonizeNormals()
    mesh.write(str(path));mesh=Mesh.Mesh(str(path))
    assert mesh.isSolid(), f'Open mesh {path}'
    error=abs(abs(mesh.Volume)-shape.Volume)/shape.Volume
    assert error<.006,(path,error)
    return mesh,{'closed':True,'facets':mesh.CountFacets,'volume_error_fraction':error,'tessellation_cleanup':repaired}

def save(spec,host):
    from access import assign
    from catalog_rules import apply
    apply(spec)
    assign(spec)
    out=ROOT/'dist/models'/spec['id'];out.mkdir(parents=True,exist_ok=True)
    shape,host,checks=integrate(host,spec['w'])
    shape.exportStep(str(out/'model.step'))
    read=Part.read(str(out/'model.step'));assert read.isValid() and len(read.Solids)==1
    mesh,mcheck=export_mesh(shape,out/'model.stl')
    if spec['id'] in ('01','18','47'):
        # Actual Boolean cut for junction/section review; never a drawing of a seam.
        xx=mounts_for(spec['w'])[0]
        section=shape.common(box(xx, -30,-240,240-xx,260,440))
        export_mesh(section,out/'section.stl')
    orientations={'upright':((1,0,0),0),'left-side':((0,1,0),90),'front-face':((1,0,0),90)}
    for name,(axis,angle) in orientations.items():
        m=mesh.copy();matrix=A.Matrix();matrix.rotateY(math.radians(angle)) if axis[1] else matrix.rotateX(math.radians(angle));m.transform(matrix)
        bb=m.BoundBox;m.translate(-bb.XMin,-bb.YMin,-bb.ZMin);m.write(str(out/(name+'.stl')))
    bb=shape.BoundBox
    spec.update(cad=checks,mesh=mcheck,volume_cm3=shape.Volume/1000,
                bounds_mm=[bb.XLength,bb.YLength,bb.ZLength],status='CAD checked; slice pending')
    (out/'spec.json').write_text(json.dumps(spec,indent=2)+'\n')
    print('BUILT',spec['id'],spec['name'],round(shape.Volume/1000,1),'cm3',flush=True)
