"""Render actual circular-peg CAD and certified motion; preserve the baseline.

The hero reads an STL in design coordinates. The animation draws the exact
central-axis section from the exported primitive contract, along recorded,
verified rigid-body poses. A center cutaway illustrates the geometry; it does
not substitute for the full three-dimensional clearance check.
"""
from __future__ import annotations
import argparse,json,math,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
import trimesh
from shapely.geometry import LineString,Polygon,box
from shapely.ops import unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PatchPolygon,Rectangle,Circle

ROOT=Path(__file__).resolve().parent
import render_round_common as studio
from render_round_common import BG,INK,TEAL,TEAL_DARK,BOARD,BOARD_DARK,MUTED,GRID,evenly_sample_path,dimension


def read_contract(path):
    data=json.loads(Path(path).read_text())
    if 'upper_capsule' not in data:raise ValueError('Need round_anchor.geometry() export contract')
    return data


def central_profile(g):
    cap=g['upper_capsule'];yz=np.asarray(cap['centers_xyz'])[:,1:]
    radii=cap.get('segment_radii',[cap.get('radius')]*(len(yz)-1))
    upper=unary_union([LineString([a,b]).buffer(r,quad_segs=96,cap_style=1,join_style=1) for a,b,r in zip(yz[:-1],yz[1:],radii)])
    s=g['spine'];rr=s['yz_corner_radius']
    spine=box(s['y_min'],s['z_min'],s['y_max'],s['z_max'])
    if rr:spine=spine.buffer(-rr,quad_segs=12).buffer(rr,quad_segs=12)
    loc=g['locator'];y=loc['tip_y'];z=loc['center_z'];rl=loc['radius'];rt=loc['tip_radius'];ch=loc['chamfer_axial_length']
    lower=Polygon([(y,z-rt),(y+ch,z-rl),(loc['root_y'],z-rl),
                   (loc['root_y'],z+rl),(y+ch,z+rl),(y,z+rt)])
    return unary_union([upper,spine,lower])


def transform(poly,pose):
    a=np.deg2rad(pose[2]);c=np.cos(a);s=np.sin(a)
    return np.asarray(poly.exterior.coords)@np.array([[c,-s],[s,c]]).T+pose[:2]


def hero(g,mesh_path,out):
    m=trimesh.load(mesh_path,force='mesh');p=g['parameters']
    W,H=studio.W,studio.H;yy,xx=np.mgrid[:H,:W]
    glow=np.exp(-((xx-1470)/1100)**2-((yy-880)/660)**2)
    base=np.zeros((H,W,3),dtype=np.float32)+[12,21,30]
    base+=glow[:,:,None]*np.array([13,23,28]);img=Image.fromarray(np.uint8(base))
    flat=m.copy();flat.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[0,1,0]))
    objects=[]
    for model,center in [(m,[-28.18,-4.10,0]),(flat,[3.75,12.90,0])]:
        v=model.vertices.copy();lo=v.min(axis=0);hi=v.max(axis=0)
        v[:,0]-=(lo[0]+hi[0])/2;v[:,1]-=(lo[1]+hi[1])/2;v[:,2]-=lo[2];v+=center
        objects.append((model,v))
    mask=Image.new('L',(W,H),0);md=ImageDraw.Draw(mask)
    for model,v in objects:
        shadow=v.copy();shadow[:,:2]+=shadow[:,2,None]*[.40,.52];shadow[:,2]=-.02
        points=studio.project(shadow)
        for face in model.faces:md.polygon([tuple(q) for q in points[face,:2]],fill=120)
    img=Image.composite(Image.new('RGB',(W,H),(4,10,16)),img,mask.filter(ImageFilter.GaussianBlur(21)))
    rgb=np.array(img);depth=np.full((H,W),-np.inf,dtype=np.float32)
    key=studio.unit([-.6,-.9,1.3]);fill=studio.unit([.8,.5,.7]);half=studio.unit(key+studio.CAM)
    for model,v in objects:
        projected=studio.project(v)
        normals=model.face_normals.copy()
        for i,face in enumerate(model.faces):
            normal=normals[i]
            if np.dot(normal,studio.CAM)<-1e-8:continue
            diffuse=.43+.59*max(0,np.dot(normal,key))+.27*max(0,np.dot(normal,fill))
            spec=max(0,np.dot(normal,half))**38*42
            col=np.clip(np.array([32,146,152.])*diffuse+spec,0,255).astype(np.uint8)
            studio.raster_triangle(rgb,depth,projected[face,:2],projected[face,2],col)
    img=Image.fromarray(rgb);draw=ImageDraw.Draw(img)
    draw.text((116,73),'round.',font=studio.font(112,True),fill='#eff4f0')
    draw.text((121,209),'CIRCULAR PEGS. CIRCULAR BEARING SURFACES.',font=studio.font(26,True),fill='#97b4b7')
    draw.text((1570,102),f"Ø{p['peg_diameter']:.2f} MM PEG",font=studio.font(28,True),fill='#d3e0df')
    draw.text((1571,148),f"Ø{p['hole_diameter']:.2f} MM BORE  ·  {p['board_thickness']:.2f} MM BOARD",font=studio.font(19),fill='#739092')
    draw.line((121,278,2279,278),fill='#31454e',width=2)
    draw.text((194,942),'ROUND NECK',font=studio.font(28,True),fill='#dce9e5')
    draw.text((194,989),'Cylinders and spherical blends.',font=studio.font(22),fill='#8facb0')
    draw.text((194,1027),'Circular lower locator.',font=studio.font(22),fill='#8facb0')
    draw.line((193,921,439,921),fill='#329ca3',width=3)
    draw.text((1850,900),'SIDE VIEW',font=studio.font(28,True),fill='#dce9e5')
    draw.text((1850,947),'The same exact solid,',font=studio.font(22),fill='#8facb0')
    draw.text((1850,985),'rotated onto its side.',font=studio.font(22),fill='#8facb0')
    draw.line((1850,879,2225,879),fill='#329ca3',width=3)
    draw.line((121,1205,2279,1205),fill='#31454e',width=2)
    draw.text((121,1251),'Actual CAD geometry · circular load-bearing sections',font=studio.font(21,True),fill='#a8c0c0')
    draw.text((1310,1251),'Bare solid shown; see the separate print preparation.',font=studio.font(19),fill='#779396')
    img.save(out/'round-hero.png',optimize=True)


def read_motion(path,g):
    d=json.loads(Path(path).read_text())
    if 'variants' in d:
        vv=d['variants'];vv=list(vv.values()) if isinstance(vv,dict) else vv
        p=g['parameters'];d=min(vv,key=lambda v:abs(v['parameters']['peg_diameter']-p['peg_diameter'])+abs(v['parameters']['board_thickness']-p['board_thickness']))
    valid=d.get('passed') or d.get('verification',{}).get('passed')
    if valid is not True:raise ValueError('Animation requires explicitly passed verification')
    p=d.get('parameters',{})
    for key in ['peg_diameter','tongue_diameter','hole_diameter','board_thickness','tongue_run','tongue_rise','pull_clearance','elbow_offset']:
        if key in p and key in g['parameters'] and p[key] is not None and g['parameters'][key] is not None and abs(p[key]-g['parameters'][key])>1e-6:raise ValueError(f'Study/geometry mismatch: {key}')
    values=d.get('removal_poses',d.get('removal_path'))
    if values is None:raise ValueError('Expected verified removal_poses; trial paths are not rendered')
    poses=np.asarray([[q['y'],q['z'],q['theta_deg']] if isinstance(q,dict) else q for q in values],dtype=float)
    return d,poses


def animation(g,study,out):
    data,poses=read_motion(study,g);p=g['parameters'];poly=central_profile(g)
    sample=evenly_sample_path(poses,95);bound=np.vstack([transform(poly,q) for q in sample])
    xmin=min(-p['board_thickness']-10,bound[:,0].min()-3);xmax=bound[:,0].max()+3
    fig=plt.figure(figsize=(11.4,7.2),facecolor=BG)
    fig.text(.05,.937,'ROUND PEGS  /  INSERT · SEAT · REMOVE',fontsize=22,fontweight='bold')
    fig.text(.05,.89,'Recorded rigid-body motion of the circular-peg CAD geometry',fontsize=11,color=MUTED)
    ax=fig.add_axes([.075,.18,.60,.66]);ax.set_facecolor(BG);ax.set_axisbelow(True)
    half=p['hole_diameter']/2;t=p['board_thickness'];pitch=p['pitch']
    for lo,hi in [(-38,-pitch-half),(-pitch+half,-half),(half,12)]:
        ax.add_patch(Rectangle((-t,lo),t,hi-lo,facecolor=BOARD,edgecolor=BOARD_DARK,lw=1))
    for z in [0,-pitch]:ax.plot([-t-2,5],[z,z],color=BOARD_DARK,lw=.5,linestyle=(0,(4,4)))
    patch=PatchPolygon(transform(poly,sample[-1]),facecolor=TEAL,edgecolor=TEAL_DARK,lw=1.25)
    ax.add_patch(patch);ax.set_xlim(xmin,xmax);ax.set_ylim(-38,14);ax.set_aspect('equal')
    ax.spines[['top','right']].set_visible(False);ax.grid(color=GRID,lw=.5);ax.tick_params(labelsize=8)
    ax.set_xlabel('Front / away from board  →  [mm]',fontsize=9);ax.set_ylabel('Height [mm]',fontsize=9)
    phase=fig.text(.72,.755,'INSERT',fontsize=20,fontweight='bold',color=TEAL)
    stats=fig.text(.72,.697,'',fontsize=12,linespacing=1.6,va='top')
    fig.text(.72,.49,f"Round peg  Ø{p['peg_diameter']:.2f} mm\nBoard bore  Ø{p['hole_diameter']:.2f} mm",fontsize=10.5,linespacing=1.7,va='top',color=MUTED)
    bore=fig.add_axes([.737,.20,.12,.20]);bore.set_aspect('equal');bore.axis('off')
    R=p['hole_diameter']/2;r=p['peg_diameter']/2
    bore.add_patch(Circle((0,0),R,facecolor=BOARD,edgecolor=BOARD_DARK,lw=1))
    bore.add_patch(Circle((0,0),R-.035,facecolor=BG,edgecolor='none'))
    bore.add_patch(Circle((0,-(R-r)),r,facecolor=TEAL,edgecolor=TEAL_DARK,lw=1))
    bore.set_xlim(-R-1,R+1);bore.set_ylim(-R-1,R+1)
    fig.text(.72,.173,'Circular bearing section\nat the seated position',fontsize=9,color=MUTED)
    fig.text(.05,.080,'Central-axis cutaway shown. The numerical study checks the full three-dimensional circular geometry.',fontsize=10,color=MUTED)
    fig.text(.05,.037,'Movement follows the verified poses; removal reverses the insertion path. Final seating permits bearing contact.',fontsize=9.5,color=MUTED)
    seq=[('INSERT',q) for q in sample[::-1]]+[('SEATED',sample[0])]*24+[('REMOVE',q) for q in sample]+[('REMOVED',sample[-1])]*16
    frames=[]
    for name,q in seq:
        patch.set_xy(transform(poly,q));phase.set_text(name)
        stats.set_text(f'Tilt  {q[2]:.2f}°\nOut  {q[0]-poses[0,0]:.2f} mm\nUp  {q[1]-poses[0,1]:.2f} mm')
        fig.canvas.draw();frames.append(Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[:,:,:3]).convert('P',palette=Image.Palette.ADAPTIVE,colors=128))
    frames[0].save(out/'round-insertion-removal.gif',save_all=True,append_images=frames[1:],duration=55,loop=0,optimize=True,disposal=2)
    plt.close(fig)



def drawing(g,out):
    p=g['parameters'];poly=central_profile(g);seat=g['seated_pose']
    pose=np.array([seat['y'],seat['z'],seat['theta_deg']]);q=transform(poly,pose)
    fig=plt.figure(figsize=(13,8.5),facecolor=BG)
    fig.text(.05,.93,'ROUND PEG ANCHOR  /  GEOMETRY',fontsize=23,fontweight='bold')
    fig.text(.05,.882,'Parametric dimensions in millimetres. Circular bearing sections remain circular.',fontsize=11,color=MUTED)
    ax=fig.add_axes([.07,.16,.47,.68]);t=p['board_thickness'];R=p['hole_diameter']/2;pitch=p['pitch']
    for lo,hi in [(-37,-pitch-R),(-pitch+R,-R),(R,12)]:
        ax.add_patch(Rectangle((-t,lo),t,hi-lo,facecolor=BOARD,edgecolor=BOARD_DARK,lw=.8))
    ax.add_patch(PatchPolygon(q,facecolor=TEAL,edgecolor=TEAL_DARK,lw=1.3))
    for z in [0,-pitch]:ax.plot([-t-2,6],[z,z],color=BOARD_DARK,lw=.5,linestyle=(0,(4,4)))
    dimension(ax,(-16,0),(-16,-pitch),f'{pitch:.2f}',(-1.5,0),90)
    dimension(ax,(-t,10),(0,10),f't = {t:.2f}',(0,1.6))
    dimension(ax,(q[:,0].min(),-35),(q[:,0].max(),-35),f'{np.ptp(q[:,0]):.2f} total depth',(0,-1.6))
    dimension(ax,(10,q[:,1].min()),(10,q[:,1].max()),f'{np.ptp(q[:,1]):.2f} overall',(1.7,0),90)
    ax.set_xlim(min(-21,q[:,0].min()-3),15);ax.set_ylim(-39,15);ax.set_aspect('equal');ax.axis('off')
    bore=fig.add_axes([.65,.48,.21,.31]);bore.set_aspect('equal');bore.axis('off');r=p['peg_diameter']/2
    bore.add_patch(Circle((0,0),R,facecolor=BG,edgecolor=BOARD_DARK,lw=2))
    bore.add_patch(Circle((0,-(R-r)),r,facecolor=TEAL,edgecolor=TEAL_DARK,lw=1.2))
    bore.plot([-R-1,R+1],[0,0],color=MUTED,lw=.5,linestyle=(0,(4,4)))
    bore.plot([0,0],[-R-1,R+1],color=MUTED,lw=.5,linestyle=(0,(4,4)))
    bore.set_xlim(-R-1,R+1);bore.set_ylim(-R-1,R+1)
    fig.text(.605,.81,'TRUE CIRCULAR BEARING SECTION',fontsize=11,fontweight='bold')
    rows=[('Upper peg diameter',f"Ø{p['peg_diameter']:.2f}"),('Rear tongue diameter',f"Ø{g['upper_capsule'].get('segment_radii',[p['peg_diameter']/2])[-1]*2:.2f}"),('Board bore diameter',f"Ø{p['hole_diameter']:.2f}"),
          ('Diametral clearance',f"{p['hole_diameter']-p['peg_diameter']:.2f}"),('Lower locator diameter',f"Ø{g['locator']['radius']*2:.2f}"),
          ('Spine width',f"{p['spine_width']:.2f}"),('Tongue run / rise',f"{p['tongue_run']:.2f} / {p['tongue_rise']:.2f}")]
    for i,(name,val) in enumerate(rows):
        fig.text(.595,.418-i*.04,name,fontsize=11,color=MUTED)
        fig.text(.918,.418-i*.04,val,fontsize=11,ha='right')
    fig.text(.05,.065,'Reference geometry only. Print preparation and the verified installation path are documented separately.',fontsize=10,color=MUTED)
    fig.savefig(out/'round-drawing.png',dpi=170);fig.savefig(out/'round-drawing.svg');plt.close(fig)


def envelope(g,study,out):
    data,poses=read_motion(study,g);p=g['parameters'];poly=central_profile(g)
    samples=evenly_sample_path(poses,161);shapes=[Polygon(transform(poly,q)) for q in samples]
    sweep=unary_union(shapes);bounds=sweep.bounds;t=p['board_thickness'];R=p['hole_diameter']/2;pitch=p['pitch']
    fig=plt.figure(figsize=(13,8.5),facecolor=BG)
    fig.text(.05,.936,'ROUND PEG ANCHOR  /  INSTALLATION ENVELOPE',fontsize=22,fontweight='bold')
    fig.text(.05,.888,'Side projection of the recorded path: insertion, seating and reverse removal.',fontsize=11,color=MUTED)
    ax=fig.add_axes([.07,.16,.62,.68]);ax.set_facecolor(BG);ax.set_axisbelow(True)
    polygons=list(sweep.geoms) if hasattr(sweep,'geoms') else [sweep]
    for sh in polygons:ax.add_patch(PatchPolygon(np.asarray(sh.exterior.coords),facecolor='#d5e5df',edgecolor='#8dbbb2',lw=1,zorder=1))
    for lo,hi in [(-38,-pitch-R),(-pitch+R,-R),(R,14)]:
        ax.add_patch(Rectangle((-t,lo),t,hi-lo,facecolor=BOARD,edgecolor=BOARD_DARK,lw=.8,zorder=2))
    for q in poses[1:-1]:
        ax.add_patch(PatchPolygon(transform(poly,q),fill=False,edgecolor='#7aa39e',lw=.8,alpha=.65,zorder=3))
    ax.add_patch(PatchPolygon(transform(poly,poses[0]),facecolor=TEAL,edgecolor=TEAL_DARK,lw=1.2,zorder=4))
    ax.set_xlim(bounds[0]-3,bounds[2]+3);ax.set_ylim(min(-38,bounds[1]-3),max(14,bounds[3]+3));ax.set_aspect('equal')
    ax.spines[['top','right']].set_visible(False);ax.grid(color=GRID,lw=.5,zorder=0);ax.tick_params(labelsize=8)
    ax.set_xlabel('Front / away from board  →  [mm]',fontsize=9);ax.set_ylabel('Height [mm]',fontsize=9)
    summary=data.get('summary',{});rear=summary.get('rear_wall_clearance_required_mm',max(0,-t-bounds[0]))
    values=[('MAXIMUM TILT',f'{poses[:,2].max():.2f}°'),('LIFT FROM SEATED',f'{poses[:,1].max()-poses[0,1]:.2f} mm'),('REAR SWEEP',f'{rear:.2f} mm')]
    for i,(label,value) in enumerate(values):
        y=.735-i*.158;fig.text(.743,y,label,fontsize=10,fontweight='bold',color=MUTED)
        fig.text(.743,y-.064,value,fontsize=24,fontweight='bold',color=TEAL_DARK)
    fig.text(.743,.238,'Pale area: sampled sweep\nTeal: seated geometry\nLines: recorded waypoints',fontsize=10,color=MUTED,linespacing=1.6,va='top')
    fig.text(.05,.065,'Envelope uses 161 interpolated poses on the verified path. Full approach distance is included; this is not a minimum-space optimization.',fontsize=9.5,color=MUTED)
    fig.text(.05,.035,'Bare anchor only. Check the attached host, neighboring objects and wall battens separately.',fontsize=9.5,color=MUTED)
    fig.savefig(out/'round-motion-envelope.png',dpi=170);plt.close(fig)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--geometry',default=str(ROOT/'cad'/'round_geometry.json'))
    ap.add_argument('--mesh',default=str(ROOT/'cad'/'round_design_reference.stl'))
    ap.add_argument('--study',default=str(ROOT/'round_motion_results.json'))
    ap.add_argument('--hero-only',action='store_true')
    ap.add_argument('--animation-only',action='store_true')
    args=ap.parse_args();g=read_contract(args.geometry);out=ROOT/'visuals';out.mkdir(exist_ok=True)
    if not args.animation_only:
        hero(g,args.mesh,out)
        drawing(g,out)
    if not args.hero_only:
        animation(g,args.study,out)
        envelope(g,args.study,out)
    print(out)

if __name__=='__main__':main()
