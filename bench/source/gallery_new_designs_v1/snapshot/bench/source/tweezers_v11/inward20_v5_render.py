"""Full-mesh holder-guide views and honest triangle-plane CAD-export sections."""
from pathlib import Path
import argparse,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from inward20_v3_render import stl,render,render_closeup,style,TOOL,BG,YELLOW,WEDGE

def section(tris,y):
    result=[]
    for t in tris:
        points=[]
        for a,b in zip(t,np.roll(t,-1,axis=0)):
            if (a[1]-y)*(b[1]-y)<0:points.append(a+(b-a)*(y-a[1])/(b[1]-a[1]))
        if len(points)==2:result.append(np.array(points)[:,[0,2]])
    return np.array(result)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('build',type=Path);p.add_argument('--slice',type=Path);p.add_argument('--plate-only',action='store_true');a=p.parse_args();d=a.build;c=json.loads((d/'candidate.json').read_text())['cases'][0];g=c['guide']
    if a.plate_only:
        if a.slice is None:p.error('--plate-only requires --slice')
        plan=json.loads((a.slice/'plate.json').read_text())
        render([(stl(Path(o['path'])),YELLOW if o['role']=='body' else WEDGE) for o in plan['objects']],d/'print-plate.png','V5 actual bed-coordinate plate / five objects','Calibrated XY compensation applied once; body plus four unchanged end-standing fins.',view=(65,-70))
        return
    body=stl(d/f"{c['name']}__installed.stl");fins=[stl(d/f) for f in c['wedges']];tools=[stl(d/f) for f in c['tools']]
    guide=stl(d/'guide-1.stl');installed=[(body,YELLOW)]+[(f,WEDGE) for f in fins]
    render(installed,d/'empty.png',f'Inward20 v5 — {g["count"]} curved guide(s)','Curved holder roof; exact v4 fin/floor geometry; 28 mm pitch, unchanged mount.',view=(24,35))
    render(installed+[(t,TOOL) for t in tools],d/'loaded.png','Inward20 v5 — curved holder guides','Four seats, 28 mm pitch; 20° inward / 15° lateral, A4.0 and taller fins.',view=(23,35))
    R=g['radius_mm'];cs=np.cos(np.radians(20));theta=np.radians(45);off=np.array([R*(1-np.sin(theta)),0,6.75+R*np.cos(theta)/cs])
    render_closeup(installed+[(t+off if k==0 else t,TOOL) for k,t in enumerate(tools)],d/'guide-closeup.png','Top guide — robust-arm approach','Complete meshes; camera crop only. At 45° on the guided return segment.',focus=[[-26,97,-12],[6,140,32]],view=(18,42))
    render([(body,YELLOW)],d/'empty-body.png','V5 — bare body with curved roof transitions','Full body mesh; four open guides join the receiving cheek.',view=(24,35))
    render_closeup([(body,YELLOW)],d/'guide-empty-closeup.png','Curved holder roof / open mouth','Full body mesh, camera crop only. No triangle filtering.',focus=[[-26,92,-5],[1,140,34]],view=(18,42))
    high=6.75+R/cs;direction=np.array(c['removal']['out_direction'])
    render(installed+[(t+np.array([R+2,0,high])+35*direction if k==2 else t,TOOL) for k,t in enumerate(tools)],d/'pickup.png','Tray 3 — independent pickup','Lift 6.75 mm; sweep up-left; withdraw. Other three tools stay seated.',view=(23,35))
    pr=stl(d/c['print_file']);wp=stl(d/c['wedge_print']);wy=float(pr[:,:,1].max())+20
    render([(pr,YELLOW)]+[(wp+[15+25*k,wy,0],WEDGE) for k in range(4)],d/'print-pose.png','Right-cheek print / four end-standing fins','Nominal geometry; top guide and pegs require accessible organic supports.',view=(60,-70))
    fig,axes=plt.subplots(2,2,figsize=(13,12),facecolor=BG)
    for k,ax in enumerate(axes.flat):
        style(ax);zshift=c['tray_pitch_vertical_mm']*k;y=117.
        for t,col in [(body,YELLOW)]+[(f,WEDGE) for f in fins]+[(t,TOOL) for t in tools]:
            lines=section(t,y)
            if len(lines):ax.add_collection(LineCollection(lines,colors=col,linewidths=1))
        for deg in [90,60,30,0]:
            a=np.radians(deg);offset=np.array([R*(1-np.sin(a)),0,6.75+R*np.cos(a)/cs]);lines=section(tools[k]+offset,y)
            if len(lines):ax.add_collection(LineCollection(lines,colors='#76d9f4',linewidths=.9,alpha=.8))
        ax.set_xlim(4,-26);ax.set_ylim(-9-zshift,32-zshift);ax.set_aspect('equal');ax.set_title(f'Tray {k+1}: reverse pickup / return',color='white');ax.set_xlabel('X: left + / right −');ax.set_ylabel('Z up (mm)')
    fig.suptitle('Four independent guide sections — cyan arc poses; white stored neighbors',color='white');fig.tight_layout();fig.savefig(d/'four-guide-paths.png',dpi=150,facecolor=BG);plt.close(fig)
    y=117.;fig,ax=plt.subplots(figsize=(12,10),facecolor=BG);style(ax)
    for t,col,label in [(body,YELLOW,'New holder'),(guide,'#ed6585','Curved guide'),(fins[0],WEDGE,'Taller fin'),(tools[0],TOOL,'Stored tool')]:
        lines=section(t,y)
        if len(lines):ax.add_collection(LineCollection(lines,colors=col,linewidths=2,label=label))
    for theta in np.radians([0,45,90]):
        off=np.array([R*(1-np.sin(theta)),0,6.75+R*np.cos(theta)/cs]);lines=section(tools[0]+off,y)
        if len(lines):ax.add_collection(LineCollection(lines,colors='#76d9f4',linewidths=1.3,alpha=.8))
    ax.annotate('Operator-left / above',xy=(-10,17),xytext=(2,26),color='white',arrowprops=dict(arrowstyle='->',color='white'))
    ax.annotate('Rightward / down, then free settle',xy=(-17,9),xytext=(-3,21),color='#76d9f4',arrowprops=dict(arrowstyle='->',color='#76d9f4'))
    ax.set_xlim(-26,10);ax.set_ylim(-8,32);ax.invert_xaxis();ax.set_xlabel('Global X (mm); operator-right is decreasing X');ax.set_ylabel('Global Z up (mm)')
    ax.set_title(f'Actual CAD-export section at global Y={y:g} mm',color='white');ax.legend(facecolor='#283840',labelcolor='white',loc='lower left')
    fig.text(.07,.025,'R6 / 2.4 mm roof, 0.7 mm mouth rounding. Quarter-circle ends above fin; final 6.75 mm settle is free.',color='white',fontsize=10)
    fig.tight_layout(rect=[0,.05,1,1]);fig.savefig(d/'guide-section.png',dpi=150,facecolor=BG);plt.close(fig)
if __name__=='__main__':main()
