"""Open curved holder lead-in, four seats at 28 mm pitch; exact v4 fins and mount.

FreeCAD Python: inward20_v5.py NEW_EMPTY_OUTPUT [--guide-count 1]
Facing board: +X is left; rightward return is -X. No printer commands.
"""
from pathlib import Path
import argparse,copy,hashlib,json,math,shutil,sys
import FreeCAD as A
import Part,Mesh
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import inward20_v5_frame as F
H,K=F.H,F.K;V=A.Vector
BASE=HERE.parents[1]/'reviews/tweezer-inward20-v4'
NAME='part-tweezers__inward20-v5-A4p0-guideR6-p28__right-cheek__fit-pf02c9-hoop5'
RADIUS=6.;THICKNESS=2.4;PITCH=28.;U0=104.;CS=math.cos(math.radians(20));SN=math.sin(math.radians(20));LIFT=6.75+RADIUS/CS

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def uv(p):return [p.x,CS*p.y+SN*p.z,-SN*p.y+CS*p.z]
def xyz(x,u,v):return V(x,CS*u-SN*v,SN*u+CS*v)
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path);parser.add_argument('--guide-count',type=int,choices=[1,4],default=4)
    a=parser.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    if any(out.iterdir()):parser.error('Use a fresh empty output; preserve earlier evidence.')
    old=json.loads((BASE/'candidate.json').read_text())['cases'][0];frame=F.make_frame();bare=frame['body']
    # Align each lower guide end exactly with the preceding floor front plane.
    U1=max(uv(v.Point)[1] for v in frame['floors'][0].Vertexes)+SN*PITCH
    points=[uv(V(p.x,p.y,p.z)) for p in Mesh.Mesh(str(BASE/old['tools'][0])).Points]
    patch=[p for p in points if U0<p[1]<U1];vtop=max(p[2] for p in patch);high=[p for p in patch if p[2]>vtop-.05]
    xc=min(p[0] for p in high);centre_x=xc+RADIUS;centre_v=vtop+CS*LIFT-RADIUS+.1
    def pt(rad,deg):
        theta=math.radians(deg);return xyz(centre_x-rad*math.sin(theta),U0,centre_v+rad*math.cos(theta))
    # Open quarter-round underside stops at80deg, before a vertical hook.
    # Broad root blends the round roof into the cheek/upper rail.
    i0,i40,i80=pt(RADIUS,0),pt(RADIUS,40),pt(RADIUS,80)
    o0,o32,o65=pt(RADIUS+THICKNESS,0),pt(RADIUS+THICKNESS,32.5),pt(RADIUS+THICKNESS,65)
    rootlow=xyz(H.INNER-.1,U0,centre_v+RADIUS*math.cos(math.radians(80)))
    roothigh=xyz(H.INNER-.1,U0,centre_v+(RADIUS+THICKNESS)*math.cos(math.radians(65)))
    edges=[Part.Arc(i0,i40,i80).toShape(),Part.makeLine(i80,rootlow),Part.makeLine(rootlow,roothigh),Part.makeLine(roothigh,o65),Part.Arc(o65,o32,o0).toShape(),Part.makeLine(o0,i0)]
    guide=Part.Face(Part.Wire(edges)).extrude(V(0,CS*(U1-U0),SN*(U1-U0)))
    # Round fore/aft cut edges and the exposed open mouth, not peg/contact geometry.
    fillet_edges=[e for e in guide.Edges if len(e.Vertexes)==2 and abs(e.Length-(U1-U0))<1e-6 and abs(e.CenterOfMass.x-centre_x)<1e-6]
    guide=guide.makeFillet(.7,fillet_edges)
    assert guide.isValid() and len(guide.Solids)==1
    guides=[]
    for k in range(a.guide_count):
        g=guide.copy();g.translate(V(0,0,-PITCH*k));guides.append(g)
    body=bare.multiFuse(guides).cut(frame['slots']).removeSplitter();guides=[g.common(body) for g in guides];assert body.isValid() and len(body.Solids)==1
    rear=K.box(-60,-40,-180,120,40.15,300);oldbody=Part.read(str(BASE/f"{old['name']}__installed.step"))
    peg_delta=F.difference(body.common(rear),oldbody.common(rear));assert peg_delta<1e-6
    added=body.cut(bare);protected=[]
    for k in range(4):
        t=A.Placement(frame['pitch']);t.move(V(0,0,-PITCH*k))
        floor_delta=F.difference(F.moved(frame['floors'][k],t.inverse()),frame['reference'][0][0]);pocket_delta=F.difference(F.moved(frame['slots'][k],t.inverse()),frame['reference'][1])
        intrusion=added.common(frame['slots'][k]).Volume
        # Existing floor solid is preserved; new roof may join its underside,
        # but may not cover its receiving face (0.3mm sheet above floor plane).
        n=frame['pitch'].Rotation.multVec(V(-math.sin(H.CANT),0,math.cos(H.CANT)))
        face_region=frame['floors'][k].copy();face_region.translate(n*.3)
        contact_intrusion=added.common(face_region.cut(frame['floors'][k])).Volume
        r=dict(tray=k+1,translation_from_v4_mm=[0,0,-(PITCH-23)*k],floor_inverse_translation_difference_mm3=floor_delta,pocket_inverse_translation_difference_mm3=pocket_delta,new_roof_in_pocket_mm3=intrusion,new_roof_in_floor_contact_skin_mm3=contact_intrusion)
        protected.append(r);assert max(floor_delta,pocket_delta,intrusion,contact_intrusion)<1e-6,r
    record=K.export(body,out,NAME,'right-cheek',dict(receiver=frame['receiver']))
    K.write(body.common(K.box(-100,.15,-180,200,250,360)),out/f'{NAME}__front-material.stl')
    tools=[];fins=[];comparisons=[];copies=[]
    for k in range(4):
        oldfin=Part.read(str(BASE/f"{old['name']}__wedge-{k+1}__installed.step"));fin=oldfin.copy();fin.translate(V(0,0,-(PITCH-23)*k));hit=body.common(fin).Volume;assert hit<1e-6,hit
        name=f'{NAME}__wedge-{k+1}__installed';fin.exportStep(str(out/f'{name}.step'));K.write(fin,out/f'{name}.stl');fins.append(f'{name}.stl')
        back=fin.copy();back.translate(V(0,0,(PITCH-23)*k));comparisons.append(dict(tray=k+1,fin_inverse_translation_difference_mm3=F.difference(back,oldfin),fin_body_intersection_mm3=hit))
        m=Mesh.Mesh(str(BASE/old['tools'][k]));m.translate(0,0,-(PITCH-23)*k);tf=f'{NAME}__tool-{k+1}.stl';m.write(str(out/tf));tools.append(tf)
    def inherit(f):
        target=f.replace(old['name'],NAME);shutil.copyfile(BASE/f,out/target);assert sha(BASE/f)==sha(out/target)
        copies.append(dict(source=str(BASE/f),target=target,sha256=sha(BASE/f)));return target
    wp=inherit(old['wedge_print']);inherit(old['wedge_print'].replace('.stl','.step'))
    for f in ['fin-v3__tool-frame.stl','fin-v4__tool-frame.stl','fin-comparison.json']:inherit(f)
    for k,g in enumerate(guides):g.exportStep(str(out/f'guide-{k+1}.step'));K.write(g,out/f'guide-{k+1}.stl')
    K.write(added,out/'guide-addition.stl')
    record.update(id='inward20-v5-A4p0-guideR6-p28',fore_aft_pitch_deg=20,lateral_cant_in_receiving_frame_deg=15,lean_mm=4,added_tip_clearance_global_y_mm=19.05,tray_pitch_vertical_mm=PITCH,
        tools=tools,wedges=fins,wedge_print=wp,wedge_count=4,wedge_volume_mm3=old['wedge_volume_mm3'],wedge_print_pose_matrix=old['wedge_print_pose_matrix'],fin=old['fin'],immutable_copies=copies,
        receiving_transform=old['receiving_transform'],tool_pose=old['tool_pose'],baseline_v4_removal=old['removal'],removal=dict(lift_mm=6.75,arc_radius_mm=RADIUS,arc_end_lift_mm=LIFT,left_clearance_extension_mm=2,out_direction=old['removal']['out_direction'],out_distance_mm=135,sequence='Free lift; continuous up-left quarter arc; 2 mm further left; outward along 20 degree axis. Return is exact reverse with final free downward settle.'),receiving_equivalence=protected,fin_equivalence=comparisons,
        peg_symmetric_difference_mm3=peg_delta,guide=dict(count=a.guide_count,radius_mm=RADIUS,thickness_mm=THICKNESS,lip_fillet_mm=.7,U_band_mm=[U0,U1],centre_XV_mm=[centre_x,centre_v],end_angle_deg=80,
            coordinates='Facing board: +X left, -X right; Z up. U=(0,cos20,sin20), V=(0,-sin20,cos20).',
            return_path=dict(radius_mm=RADIUS,high_lift_mm=LIFT,lateral_start_mm=RADIUS+2,final_free_lift_mm=6.75,formula='X=6(1-sin(theta)), Z=6.75+6*cos(theta)/cos20, theta0..90; Y0; then free vertical settle.',out_direction=old['removal']['out_direction'],out_distance_mm=135),extra_roof_mm3=added.Volume),
        frame=dict(outline_yz_mm=frame['outline'],windows_yz_mm=frame['windows'],top_rail_rise_from_v4_mm=6,bottom_growth_nominal_mm=15),
        sources={str(p):sha(p) for p in [Path(__file__).resolve(),Path(F.__file__),HERE/'holder.py',K.HERE/'common.py',BASE/'candidate.json',BASE/f"{old['name']}__installed.step",H.TOOL]},
        v4_comparison=dict(candidate=str(BASE/'candidate.json'),sha256=sha(BASE/'candidate.json'),translations_mm=[[0,0,-(PITCH-23)*k] for k in range(4)],notes='Pitch increase expressly authorized; floor/pocket/fin geometry and orientations unchanged, translated only. Peg surfaces unchanged.'))
    load_x=frame['reference'][3]['xmax']-2.5;load=frame['pitch'].multVec(V(load_x,frame['reference'][3]['y_front']-4,H.floor_top(load_x,0)-1));loads=[]
    for k in range(4):
        for axis,force,target in [('side',[5,0,0],1.),('down',[0,0,-5],.5)]:loads.append(dict(id=f'tray-{k+1}-{axis}-5N',point=list(load+V(0,0,-PITCH*k)),radius=3,force=force,target_load_point_mm=target,what=f'Tray {k+1} {axis} handling'))
    (out/f'{NAME}__fea-spec.json').write_text(json.dumps(dict(step=f'{NAME}__installed.step',h=2.,supports=['pegs'],loads=loads),indent=2)+'\n')
    K.save_design(out,NAME,record);(out/'candidate.json').write_text(json.dumps(dict(cases=[record],runtime=dict(FreeCAD=A.Version(),OpenCascade=Part.OCC_VERSION)),indent=2)+'\n')
    print(json.dumps(dict(guide=record['guide'],protected=protected,peg_difference=peg_delta,volume_cm3=body.Volume/1000,bounds=record['bounds_installed']),indent=2))
if __name__=='__main__':main()
