"""Open curved-bottom storage cradle v14: no lid, axle, latch or feed function.

FreeCAD Python entrypoint; only writes this new version's requested build directory.
The unchanged right-cheek two-column receiver carries a shallow gravity trough.
Removal is an explicit 8 mm lift followed by 65 mm outward travel, with no X motion.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

import FreeCAD as A
import Part

sys.path.insert(0,str(Path(__file__).resolve().parent))
import common as K

V=A.Vector
NAME='part-solder-spool-storage__v14__right-cheek__fit-pf02c9-hoop5'
HW=24.4
YC,CZ=40.0,-34.0
RADIUS,WALL,ANGLE=34.0,3.6,35.0
FLOOR=CZ-RADIUS
LIFT,OUT=8.0,65.0


def fuse(parts):
    return parts[0].multiFuse(parts[1:]).removeSplitter()


def sector():
    a=math.radians(ANGLE)
    return K.poly_prism([(YC,CZ),(YC-100*math.sin(a),CZ-100*math.cos(a)),
                        (YC+100*math.sin(a),CZ-100*math.cos(a))],'x',-25,25)


def ring(x,length,inner):
    return Part.makeCylinder(RADIUS+WALL,length,V(x,YC,CZ),V(1,0,0)).cut(
        Part.makeCylinder(inner,length+2,V(x-1,YC,CZ),V(1,0,0))).common(sector())


def build():
    receiver,info=K.receiver(2,1,'right-cheek')
    shell=ring(-HW,2*HW,RADIUS)
    left_rim=ring(-HW,6.2,28.5)
    right_rim=Part.makeCylinder(RADIUS+WALL,6.6,V(17.8,YC,CZ),V(1,0,0)).cut(
        Part.makeCone(RADIUS,28.5,6.6,V(17.8,YC,CZ),V(1,0,0))).common(sector())
    rear_web=K.band((5.4,-48),(21,-63),(0,-1),5.0,-HW,HW,extend=.2)
    cheek=K.poly_prism([(5.4,-28),(61.6,-57.5),(61.6,-64.8),
                        (40,-71.6),(18.4,-64.8),(5.4,-51)],'x',-HW,-22)
    # Deep side flanges carry the tub below the hoop row without filling the
    # lower window. The far flange grows at <45 degrees in the cheek print pose.
    side_flange=K.box(-HW,5.4,-51,3,7.6,30)
    far_flange=K.poly_prism([(17.8,5.4),(24.4,5.4),(24.4,11)],'z',-51,-21)
    body=fuse([receiver,K.box(-HW,.15,-51,48.8,5.4,19.73),
               shell,left_rim,right_rim,rear_web,cheek,side_flange,far_flange])
    for xa,xb,za,zb in [(-8,21,-20,-5),(-18,16,-45,-33)]:
        window=K.pointed_window(xa,xb,za,zb,'+X').cut(K.peg_keepout(2,1))
        body=body.cut(window).removeSplitter()
    assert body.isValid() and len(body.Solids)==1
    rear=K.box(-50,-30,-100,100,30.15,130)
    old,new=receiver.common(rear),body.common(rear)
    delta=old.cut(new).Volume+new.cut(old).Volume
    assert delta<1e-6,delta
    return body,info,delta


def cylinder(od,width):
    return Part.makeCylinder(od/2,width,V(-width/2,YC,FLOOR+od/2),V(1,0,0))


def payload(od,width):
    z=FLOOR+od/2; flange=1.0 if width<=12 else 2.0
    bore=8.0 if width<=12 else 20.0
    parts=[Part.makeCylinder(od/2,flange,V(-width/2,YC,z),V(1,0,0)),
           Part.makeCylinder(od/2,flange,V(width/2-flange,YC,z),V(1,0,0)),
           Part.makeCylinder(min(20,od/2-4),width-2*flange,
                             V(-width/2+flange,YC,z),V(1,0,0))]
    return fuse(parts).cut(Part.makeCylinder(bore/2,width+2,
                             V(-width/2-1,YC,z),V(1,0,0))).removeSplitter()


def sweeps(od,width):
    c=cylinder(od,width); raised=c.translated(V(0,0,LIFT))
    lift=fuse([c,raised,K.box(-width/2,YC-od/2,FLOOR+od/2,width,od,LIFT)])
    outward=fuse([raised,raised.translated(V(0,OUT,0)),
                 K.box(-width/2,YC,FLOOR+LIFT,width,OUT,od)])
    return lift,outward


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path)
    out=parser.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=True)
    body,receiver,peg_delta=build()
    design=K.export(body,out,NAME,'right-cheek',dict(receiver=receiver))
    cases=[];tools=[]
    for ident,od,width in [('narrow-40x8',40,8),('narrow-40x12',40,12),
                          ('small-40x20',40,20),('nominal-55x30',55,30),('large-65x34',65,34)]:
        tool=payload(od,width);full=cylinder(od,width);up,forward=sweeps(od,width)
        filename=f'payload__{ident}.stl';K.write(tool,out/filename)
        overlaps=dict(rest_full_cylinder_mm3=full.common(body).Volume,
                      lift_sweep_mm3=up.common(body).Volume,
                      outward_sweep_mm3=forward.common(body).Volume)
        assert max(overlaps.values())<1e-5,(ident,overlaps)
        # A direct outward slide without the allowed lift must meet the curved rim.
        closed_path=fuse([full,full.translated(V(0,OUT,0)),
                         K.box(-width/2,YC,FLOOR,width,OUT,od)])
        no_lift_overlap=closed_path.common(body).Volume
        assert no_lift_overlap>1, (ident,no_lift_overlap)
        cases.append(dict(id=ident,od_mm=od,width_mm=width,
            centre=[0,YC,FLOOR+od/2],installed_top_z_mm=FLOOR+od,
            lifted_top_z_mm=FLOOR+od+LIFT,overlaps=overlaps,
            direct_outward_without_lift_overlap_mm3=no_lift_overlap,
            gravity_local_minimum=RADIUS>od/2))
        tools.append(dict(id=ident,stl=filename,seat=dict(gravity=True),
                          removal=[[0,0,LIFT],[0,OUT,0]],samples=1500))
        if ident=='large-65x34':
            K.write(full,out/'envelope__largest-installed.stl')
            K.write(fuse([up,forward]),out/'envelope__largest-up-out-sweep.stl')
    spec=dict(title='Open spool storage v14',pose='right-cheek',
        installed=f'{NAME}__installed.stl',print=design['print_file'],
        pose_matrix=design['pose_matrix'],overhang_exceptions=[],tools=tools)
    (out/f'{NAME}__checks-spec.json').write_text(json.dumps(spec,indent=2)+'\n')
    fea=dict(step=f'{NAME}__installed.step',h=2.0,supports=['pegs'],loads=[
        dict(id='front-rim-side-5N',point=[16,59.6,-63],radius=3,force=[5,0,0],
             what='front outer trough rim, lateral'),
        dict(id='front-rim-down-5N',point=[16,59.6,-63],radius=3,force=[0,0,-5],
             what='front outer trough rim, downward')])
    (out/f'{NAME}__fea-spec.json').write_text(json.dumps(fea,indent=2)+'\n')
    sources=[Path(__file__),K.HERE/'common.py']
    sources += [K.HERE.parent/n for n in ['peg_profile.py','peg_print_variant.py',
        'peg_fit_ladder.py','peg_fit_ladder_v2.py','peg_fit_ladder_v4.py','peg_interface.py']]
    design.update(role='Open storage cradle; supersedes gated v13 mechanism study',
        coverage=dict(od_mm=[40,65],overall_width_mm=[8,34],measured=False,
                      note='Narrow bobbins have a smaller tipping margin and can lean; no fitted narrow-spool guides.'),
        trough=dict(inner_radius_mm=RADIUS,shell_mm=WALL,half_angle_deg=ANGLE,
                    bottom_z_mm=FLOOR,front_rise_mm=RADIUS*(1-math.cos(math.radians(ANGLE)))),
        removal=[[0,0,LIFT],[0,OUT,0]],peg_symmetric_difference_mm3=peg_delta,
        payload_cases=cases,sources=[dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sources],
        runtime=dict(FreeCAD=A.Version(),OpenCascade=getattr(Part,'OCC_VERSION','unknown')),
        limits=['Unmeasured spool dimensions','Passive gravity engagement, no dynamic bump rating',
                'Lift clearance and hand access required','No slicing or physical fit qualification'])
    K.save_design(out,NAME,design)
    print(json.dumps(dict(volume_cm3=body.Volume/1000,bounds=design['bounds_installed'],
                         print_bounds=design['print_bounds'],cases=cases),indent=2))


if __name__=='__main__':
    main()
