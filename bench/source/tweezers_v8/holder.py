"""Tip-down, open-arm troughs on the unchanged v7 fourteen-point receiver.

Python 3.12 + the repository requirements.txt. Run:
  python holder.py --baseline /path/to/v7-installed.step --output /path/to/output
The source bundle includes that SHA256-pinned baseline and the measured model.
Coordinates: tool X=broad-face width, Y=heel toward point, Z=arm opening.
The trough is open upward; its low left rail clears after a vertical lift.
"""
from pathlib import Path
import argparse, hashlib, json, math
import cadquery as cq
import numpy as np
import trimesh
from scipy.interpolate import PchipInterpolator, CubicSpline
import build_models as tool

ROOT = Path(__file__).resolve().parent
PREFIX = 'part-solder-modules-tweezers__v8__long-body-cradle__fit-e586ab4ff6'
BASELINE_NAME = 'part-solder-modules-tweezers__v7__4-tweezer-stack-14-mount-points__fit-e586ab4ff6__installed.step'
BASELINE_SHA = '2abdd83699589dac57290c444aeb298cfc429a8d2d4eb9effbe83d5bf0c20f37'
SIN, COS = math.sin(math.radians(40)), math.cos(math.radians(40))
R = np.array([[1,0,0],[0,-SIN,COS],[0,-COS,-SIN]])
HEELS = [np.array([-9.4,105.,55.-42*i]) for i in range(4)]
T = 2.4

def box(x,y,z,w,d,h):
    return cq.Solid.makeBox(w,d,h,cq.Vector(x,y,z))

def wire(y, points):
    return cq.Wire.makePolygon([cq.Vector(x,y,z) for x,z in points],close=True)

def loft(sections):
    return cq.Solid.makeLoft(sections,ruled=True)

def values(y, side_clearance):
    c,w,t,g = float(tool.CENTER(y)),float(tool.WIDTH(y)),float(tool.THICKNESS(y)),tool.gap_at(y,'open_rest')
    # The aft dimension is the TOTAL fused thickness. Only one half is below
    # the centreline. Above the split, support just the lower arm's outside.
    outer = g/2+t
    blend = float(np.clip((y-14)/6,0,1)); blend=blend*blend*(3-2*blend)
    top = (1-blend)*(-t-.30)+blend*(g/2-.30)
    clearance = float(np.interp(y,[6,36,42,61,64],[.35,.35,side_clearance,side_clearance,.45]))
    return c,w,outer,top,clearance

def rail_outline(x0,x1,top,bottom):
    # Rounded upper corners: no sharp guide lip against the steel.
    rad=.6
    p=[(x0,bottom),(x1,bottom),(x1,top+rad)]
    for a in np.linspace(0,-90,7)[1:]:
        p.append((x1-rad+rad*math.cos(math.radians(a)),top+rad+rad*math.sin(math.radians(a))))
    p.append((x0+rad,top))
    for a in np.linspace(-90,-180,7)[1:]:
        p.append((x0+rad+rad*math.cos(math.radians(a)),top+rad+rad*math.sin(math.radians(a))))
    return p

def cradle(side_clearance=.08):
    floors,left,right=[],[],[]
    for y in np.unique(np.r_[np.arange(6,65,2),14,16,20,28,36,38,42,50,55,60,61,64]):
        c,w,h,top,cl=values(float(y),side_clearance)
        xl,xr=c-w/2-cl,c+w/2+cl
        bottom=h+.35+T
        floors.append(wire(y,[(xl-T,h+.35),(12.3,h+.35),(12.3,bottom),(xl-T,bottom)]))
        left.append(wire(y,rail_outline(xl-T,xl,top,bottom)))
        right.append(wire(y,rail_outline(xr,xr+T,top,bottom)))
    result=loft(floors).fuse(loft(left),loft(right)).clean()
    assert result.isValid() and len(result.Solids())==1
    return result

def installed(shape, heel):
    # A rigid rotation, not a general affine transform, preserves analytic CAD.
    return shape.rotate((0,0,0),(1,0,0),-130).translate(tuple(heel))

def mesh(shape):
    v,f=shape.tessellate(.055,.13)
    m=trimesh.Trimesh(vertices=[p.toTuple() for p in v],faces=f,process=True)
    m.merge_vertices(digits_vertex=5)
    m.update_faces(m.unique_faces())
    m.update_faces(m.nondegenerate_faces())
    m.remove_unreferenced_vertices()
    m.fix_normals()
    assert m.is_watertight and m.is_winding_consistent and m.volume>0
    return m

def print_pose(shape):
    q=shape.rotate((0,0,0),(0,1,0),90)
    b=q.BoundingBox()
    return q.translate((-b.xmin,-b.ymin,-b.zmin))

def prism_yz(x,width,points):
    w=cq.Wire.makePolygon([cq.Vector(x,y,z) for y,z in points],close=True)
    return cq.Solid.extrudeLinear(w,[],cq.Vector(width,0,0))

def web(heel):
    # A right-side rib leaves the entire left departure corridor open.
    # Its inner X face lies beyond the right edge of the stored broad body.
    y0,z0=heel[1],heel[2]
    return prism_yz(.5,2.4,[(5.15,z0-63),(5.15,min(z0-10,4.5)),
                              (y0+2,z0-3),(y0-37,z0-56)])

def save(shape,path):
    cq.exporters.export(shape,str(path.with_suffix('.step')))
    m=mesh(shape);m.export(path.with_suffix('.stl'))
    reread=cq.importers.importStep(str(path.with_suffix('.step'))).val()
    assert reread.isValid() and len(reread.Solids())==1
    return m,{'valid_single_solid':True,'volume_mm3':shape.Volume(),
              'mesh_watertight':True,'mesh_triangles':len(m.faces),
              'mesh_volume_error_fraction':abs(m.volume-shape.Volume())/shape.Volume(),
              'step_roundtrip_volume_error_mm3':abs(reread.Volume()-shape.Volume()),
              'bounds_mm':m.extents.tolist()}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--baseline',type=Path,default=ROOT/BASELINE_NAME)
    parser.add_argument('--output',type=Path,default=ROOT/'output');args=parser.parse_args()
    assert hashlib.sha256(args.baseline.read_bytes()).hexdigest()==BASELINE_SHA
    out=args.output;out.mkdir(parents=True,exist_ok=True)
    old=cq.importers.importStep(str(args.baseline)).val()
    retained=old.intersect(box(-50,-30,-220,100,35.55,300)).clean()
    guide=cradle();new=retained
    for heel in HEELS:
        new=new.fuse(installed(guide,heel),web(heel)).clean()
    assert new.isValid() and len(new.Solids())==1, (new.isValid(),len(new.Solids()))
    keep=box(-50,-30,-220,100,35.15,300)
    a,b=old.intersect(keep),new.intersect(keep)
    delta=a.cut(b).Volume()+b.cut(a).Volume();assert delta<1e-6,delta
    holder,checks=save(new,out/(PREFIX+'__installed'))
    pm,pcheck=save(print_pose(new),out/(PREFIX+'__print-right-cheek'))
    coupon,coupon_check=save(print_pose(guide),out/(PREFIX+'__single-throat-test__print-right-cheek'))
    mesh(guide).export(out/'cradle-local.stl')
    tools=[]
    for i,heel in enumerate(HEELS):
        m=tool.make_mesh('open_rest');m.vertices=m.vertices@R.T+heel;tools.append(m)
        m.export(out/f'{PREFIX}__reference-tool-{i+1}.stl')
    for pose in ['open_rest','closed_pinched']:
        tool.make_mesh(pose).export(out/f'tweezers_{pose}.stl')
    for name,parts in [('loaded',[holder,*tools]),('empty',[holder]),('print',[pm]),('test-piece',[coupon])]:
        scene=trimesh.Scene()
        for i,m in enumerate(parts):
            m=m.copy();m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]));m.apply_scale(.001);m.visual.face_colors=[76,161,145,255] if i==0 else [188,194,200,255]
            scene.add_geometry(m,node_name='holder' if i==0 else f'tool-{i}')
        (out/f'{PREFIX}__{name}.glb').write_bytes(scene.export(file_type='glb'))
    report={'version':8,'orientation':'Tips down for storage, insertion and removal; grasp the heel.',
      'baseline_sha256':BASELINE_SHA,'canonical_peg_fit_sha256':'e586ab4ff6173c76e10c960ca707da94b01c615a629480d4bceeae71c80e2438',
      'mount_and_receiver_difference_mm3_below_y_5p15':delta,'mount_points':14,
      'tool_heel_positions_xyz_mm':[h.tolist() for h in HEELS],
      'tool_to_installed_rotation':R.tolist(),'cradle_body_station_range_from_heel_mm':[6,64],
      'closer_lateral_bearing_range_mm':[42,61],'lateral_clearance_per_edge_mm':.08,
      'aft_lateral_clearance_per_edge_mm':.35,'lower_face_clearance_mm':.35,
      'wall_mm':T,'tip_region_from_heel_mm':[108,122.76],
      'storage_tool':'The measured/scanned 122.76 mm bent tweezer, repeated in all four slots. Other tools not fitted.',
      'holder':checks,'print':pcheck,'test_piece':coupon_check,
      'qualification':'Prototype; no physical fit, wear, load or printer-profile qualification. No inherited v6/v7 slicing claim.'}
    (out/f'{PREFIX}__design-and-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__': main()
