"""Rigid-key two-bearing static load demands, not holder bending capacity.

Key upper bearing is at the straight-wall shoulder, not the funnel opening.
Idealized lower bearing is at the tip. The grip force acts at the modeled
grip center. These reactions follow force/moment equilibrium independently
of holder stiffness; real distributed contact and steel deflection differ.
"""
from pathlib import Path
import json, numpy as np

def couple(axis, tip, shoulder, grip, force):
    u=np.asarray(axis); p=np.asarray(tip); s=np.asarray(shoulder); g=np.asarray(grip); f=np.asarray(force)
    L=float((s-p)@u); T=float((g-p)@u); transverse=f-u*(f@u)
    upper=transverse*T/L; lower=transverse-upper
    # Loads key applies to holder. Axial force remains separately transmitted.
    assert np.linalg.norm(upper+lower-transverse)<1e-10
    assert np.linalg.norm(np.cross(s-p,upper)-np.cross(g-p,transverse))<1e-8
    return dict(bearing_spacing_mm=L,exposed_grip_lever_mm=T-L,transverse_force_N=float(np.linalg.norm(transverse)),axial_force_N=float(f@u),upper_bearing_force_N=float(np.linalg.norm(upper)),lower_bearing_force_N=float(np.linalg.norm(lower)),upper_bearing_vector_N=upper.tolist(),lower_bearing_vector_N=lower.tolist(),grip_moment_at_shoulder_Nmm=np.cross(g-s,f).tolist(),moment_magnitude_at_shoulder_Nm=float(np.linalg.norm(np.cross(g-s,f))/1000),print_layer_normal_upper_force_N=float(upper[0]))

def main():
    root=Path(__file__).resolve().parents[3]; cfg=json.loads((root/'bench/source/hx05_anisotropy_v1/config.json').read_text()); racks=[]
    for r in cfg['racks']:
        tools=[]
        for t in r['tools']:
            u=np.array(t['axis']);tip=np.array(t['tip']);shoulder=tip+u*t['guide'];grip=np.array(t['top'])
            perpendicular=np.cross(u,[0,0,1.]);perpendicular/=np.linalg.norm(perpendicular)
            cases={name:couple(u,tip,shoulder,grip,force) for name,force in [('transverse20N',20*perpendicular),('down20N',[0,0,-20]),('across_layers20N',[20,0,0]),('outboard20N',[0,20,0])]}
            tools.append(dict(tool=t['name'],axis=u.tolist(),tip=tip.tolist(),straight_shoulder=shoulder.tolist(),grip_center=grip.tolist(),cases=cases))
        racks.append(dict(id=r['id'],tools=tools))
    out=dict(scope='Static load demands only. Two point bearings, rigid straight key and modeled grip centers. Not stresses or safety factors. Actual holder has distributed contact, walls, dense ribs and roots; rear peg contact remains unresolved.',force_N=20,print_layer_normal_installed_axis='X',racks=racks)
    dest=root/'bench/reviews/hx05-tensile-v1/bending-demands.json';dest.write_text(json.dumps(out,indent=2)+'\n')
    for r in racks:
        tools=r['tools']; w=max(tools,key=lambda x:x['cases']['transverse20N']['moment_magnitude_at_shoulder_Nm']); c=w['cases']['transverse20N']
        print(r['id'],w['tool'],'moment',round(c['moment_magnitude_at_shoulder_Nm'],3),'Nm','upper bearing maximum',round(max(t['cases']['transverse20N']['upper_bearing_force_N'] for t in tools),1),'N')

if __name__=='__main__':
    q=couple([1.,0,0],[0,0,0],[60,0,0],[240,0,0],[0,20,0])
    assert abs(q['upper_bearing_force_N']-80)<1e-10
    assert abs(q['lower_bearing_force_N']-60)<1e-10
    assert abs(q['moment_magnitude_at_shoulder_Nm']-3.6)<1e-10
    main()
