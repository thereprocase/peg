"""Ordinary mesh renders and four-station path/clearance projections; no image editing."""
from pathlib import Path
import argparse,json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Rectangle
from matplotlib.colors import to_rgb
from PIL import Image,ImageDraw,ImageFont
from itertools import product
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'solder_v12'))
from spool_front_render import stl,render,style,TOOL,BG
YELLOW='#fff144';WEDGE='#e79c46'
def project(ax,t,color,alpha=1):
    ax.add_collection(PolyCollection(t[:,:,[1,2]],facecolors=color,edgecolors='none',alpha=alpha))
def render_closeup(parts,path,title,note,focus,view=(24,35)):
    # Orthographic software z-buffer: matplotlib's per-collection painter order
    # can hide an installed spool behind a large rear-plate triangle.
    width,height=1430,1170
    canvas=np.empty((height,width,3),dtype=np.uint8);canvas[:]=np.array(to_rgb(BG))*255
    depth=np.full((height,width),-np.inf)
    el,az=np.deg2rad(view)
    direction=np.array([np.cos(el)*np.cos(az),np.cos(el)*np.sin(az),np.sin(el)])
    right=np.cross([0,0,1],direction);right/=np.linalg.norm(right)
    up=np.cross(direction,right)
    matrix=np.array([right,up,direction]).T
    # Frame the camera on a world-space box; rasterize EVERY body triangle.
    # No triangle filtering, cut surfaces, mesh changes or image repair.
    xyz=np.array(list(product(*zip(focus[0],focus[1]))))@matrix
    low=xyz.min(0);high=xyz.max(0);centre=(low+high)/2
    scale=min((width-170)/(high[0]-low[0]),(height-300)/(high[1]-low[1]))
    for vertices,color in parts:
        normals=np.cross(vertices[:,1]-vertices[:,0],vertices[:,2]-vertices[:,0])
        normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-12)
        light=direction+np.array([0,0,.8]); light/=np.linalg.norm(light)
        shade=.45+.55*np.maximum(0,normals@light)
        colors=np.array(to_rgb(color))[None,:]*shade[:,None]
        if color==TOOL:
            middle=np.abs(vertices[:,:,0]).max(1)<13
            colors[middle]=np.array(to_rgb('#aab3b8'))*shade[middle,None]
        projected=vertices@matrix
        projected[:,:,0]=(projected[:,:,0]-centre[0])*scale+width/2
        projected[:,:,1]=-(projected[:,:,1]-centre[1])*scale+height/2
        for tri,rgb in zip(projected,colors):
            xmin=max(0,int(np.floor(tri[:,0].min())));xmax=min(width-1,int(np.ceil(tri[:,0].max())))
            ymin=max(0,int(np.floor(tri[:,1].min())));ymax=min(height-1,int(np.ceil(tri[:,1].max())))
            if xmin>xmax or ymin>ymax: continue
            a,b,c=tri
            den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            if abs(den)<1e-9:continue
            xx,yy=np.meshgrid(np.arange(xmin,xmax+1)+.5,np.arange(ymin,ymax+1)+.5)
            u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
            v=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den
            w=1-u-v;z=u*a[2]+v*b[2]+w*c[2]
            old=depth[ymin:ymax+1,xmin:xmax+1]
            keep=(u>=-1e-7)&(v>=-1e-7)&(w>=-1e-7)&(z>old)
            old[keep]=z[keep]
            canvas[ymin:ymax+1,xmin:xmax+1][keep]=(np.clip(rgb,0,1)*255).astype(np.uint8)
    im=Image.fromarray(canvas);draw=ImageDraw.Draw(im)
    fonts=Path(matplotlib.get_data_path())/'fonts'/'ttf'
    draw.text((55,42),title,fill='white',font=ImageFont.truetype(str(fonts/'DejaVuSans.ttf'),35))
    draw.text((55,height-75),note,fill='#d6e1e5',font=ImageFont.truetype(str(fonts/'DejaVuSans.ttf'),20))
    im.save(path)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('build',type=Path);p.add_argument('--slice',type=Path)
    args=p.parse_args();d=args.build;c=json.loads((d/'candidate.json').read_text())['cases'][0]
    body=stl(d/f"{c['name']}__installed.stl");wedges=[stl(d/f) for f in c['wedges']];tools=[stl(d/f) for f in c['tools']]
    assert len(tools)==len(wedges)==4
    installed=[(body,YELLOW)]+[(w,WEDGE) for w in wedges];loaded=installed+[(t,TOOL) for t in tools]
    render(loaded,d/'loaded.png','Inward20 v3 — four vertical trays','20° inward slope, 15° lateral seating, A/4.0; retained 23.05 mm plate-tip gap.',view=(23,35))
    render(installed,d/'empty.png','Four-stack — continuous rounded frame','Shared row-4 mount with row-2 locators. Four ordinary wedges shown orange.',view=(24,35))
    render([(body,YELLOW)],d/'empty-body.png','Bare body — continuous frame junctions','No wedges or tools hide the receiving pockets or rail/root transitions.',view=(24,35))
    render(loaded,d/'mounted-side.png','Four-stack — mounted side','Top two seats unchanged; two more below at 23 mm vertical pitch.',view=(0,0))
    lift=np.array([0,0,c['removal']['lift_mm']]);direction=np.array(c['removal']['out_direction'])
    render(installed+[(t+(lift+35*direction if k==2 else 0),TOOL) for k,t in enumerate(tools)],d/'lift-out.png','Tray 3 — independent withdrawal','Other three tools remain seated. Lift 6.5 mm, then travel outward/uphill.',view=(18,32))
    for name,focus,title in [
        ('junction-upper.png',[[-25,0,-30],[25,82,12]],'Upper root / continuous rail junction'),
        ('junction-lower.png',[[-25,0,-115],[25,95,-73]],'Lower root / continuous rail junction')]:
        render_closeup([(body,YELLOW)],d/name,title,
                       'Complete body mesh; close camera framing, no removed triangles.',focus=focus)
    pr=stl(d/c['print_file']);wp=stl(d/c['wedge_print']);wy=float(pr[:,:,1].max())+20
    render([(pr,YELLOW)]+[(wp+[15+25*k,wy,0],WEDGE) for k in range(4)],d/'print-pose.png','Right-cheek print — body plus four wedges','Nominal pose; peg supports appear in actual sliced toolpaths.',view=(60,-70))
    for kind in ['headroom-path','tip-clearance']:
        fig,axes=plt.subplots(2,2,figsize=(15,12),facecolor=BG)
        for k,ax in enumerate(axes.flat):
            style(ax);ax.set_xlabel('Y away from board (mm)');ax.set_ylabel('Z up (mm)')
            project(ax,body,YELLOW,.55)
            for w in wedges:project(ax,w,WEDGE)
            for j,t in enumerate(tools):project(ax,t,TOOL,1 if j==k else .45)
            low=float(tools[k][:,:,2].min())
            if kind=='headroom-path':
                for distance,alpha in [(0,.25),(35,.4),(80,.65)]:project(ax,tools[k]+lift+distance*direction,'#76d9f4',alpha)
                ax.set_xlim(-6,238);ax.set_ylim(low-10,low+91)
                ax.text(5,low-5,'6.5 mm up, then 20° outward/uphill; no rotation.',color='white',fontsize=9)
            else:
                ax.set_xlim(-6,70);ax.set_ylim(low-15,low+23)
                ax.annotate('',xy=(28.6,low-3),xytext=(5.55,low-3),arrowprops=dict(arrowstyle='<->',color='white'))
                ax.text(6,low-9,'23.05 mm to plate plane',color='white',fontsize=10)
            ax.add_patch(Rectangle((-3.79,low-20),3.94,130,facecolor='#947b59'))
            ax.set_title(f'Tray {k+1} (top to bottom)',color='white')
        fig.suptitle('Four independent loaded-neighbor paths' if kind=='headroom-path' else 'Four retained tip spaces — actual Y–Z projections',color='white',fontsize=17)
        fig.text(.06,.015,'Reference tools only. Hand space is additional; actual 3D clearances and sampled headroom are in checks.json.',color='white',fontsize=10)
        fig.tight_layout(rect=[0,.04,1,.95]);fig.savefig(d/f'{kind}.png',dpi=145,facecolor=BG);plt.close(fig)
    if args.slice:
        layout=json.loads((args.slice/'plate.json').read_text());assert layout['object_count']==5
        render([(stl(Path(o['path'])),YELLOW if o['role']=='body' else WEDGE) for o in layout['objects']],d/'print-plate.png','Five separate objects — one body, four wedges','Calibrated ASA XY shrink applied once. Preview omits generated supports.',view=(65,-70))
if __name__=='__main__':main()
