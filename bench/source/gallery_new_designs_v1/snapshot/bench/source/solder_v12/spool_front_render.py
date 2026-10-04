"""Ordinary CAD-mesh review images; system Python with numpy/matplotlib/Pillow.

Reads binary STL directly, so this does not require installing another CAD stack.
All images are geometry renders; the side section shows the release proxy honestly.
"""
from pathlib import Path
import argparse
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.patches import Polygon as Patch
from PIL import Image, ImageDraw, ImageFont
import numpy as np

NAME = 'part-solder-spool-front__v13__right-cheek__fit-pf02c9-hoop5'
CYAN, TOOL, AMBER, BG = '#76d9f4', '#e5e7df', '#efa750', '#23303a'


def stl(path):
    dtype=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attribute','<u2')])
    with path.open('rb') as f:
        f.read(80)
        count=int.from_bytes(f.read(4),'little')
        data=np.fromfile(f,dtype=dtype,count=count)
    assert len(data)==count
    return data['vertices'].astype(float)


def style(ax):
    ax.set_facecolor(BG)
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#8295a0')
    ax.xaxis.label.set_color('white'); ax.yaxis.label.set_color('white')
    ax.grid(color='#50636d',alpha=.4)
    ax.set_aspect('equal')


def render(parts,path,title,note,view=(24,57)):
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
    xyz=np.concatenate([v.reshape(-1,3) for v,_ in parts])@matrix
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


def rings(geom):
    if geom['type']=='Polygon':
        return [geom['coordinates']]
    if geom['type']=='MultiPolygon':
        return geom['coordinates']
    return []


def diagram(d):
    p=json.loads((d/'projected-outlines.json').read_text())['projections']
    fig,axes=plt.subplots(1,2,figsize=(13,9),facecolor=BG)
    for ax in axes:
        style(ax);ax.set_xlabel('X across board (mm)');ax.set_ylabel('Z up (mm)')
        for polygon in rings(p['actual_body']):
            ax.add_patch(Patch(polygon[0],facecolor=CYAN,alpha=.25,edgecolor=CYAN,lw=2))
        ax.set_xlim(-30,30);ax.set_ylim(-76,11)
    for polygon in rings(p['continuous_largest_sweep']):
        axes[0].add_patch(Patch(polygon[0],facecolor=AMBER,alpha=.7,edgecolor=AMBER,lw=2))
    for polygon in rings(p['installed_largest_payload']):
        axes[0].add_patch(Patch(polygon[0],fill=False,edgecolor='white',lw=1.8))
    axes[0].set_title('Actual body outline + complete spool sweep',color='white')
    axes[0].text(-28,-74,'Amber: conservative full-cylinder sweep.\nWhite: detailed spool projection (invariant in Y).',color='white',fontsize=10)
    if 'previous_braid_body' in p:
        for polygon in rings(p['previous_braid_body']):
            axes[1].add_patch(Patch(polygon[0],fill=False,edgecolor='#f9faf4',lw=2,linestyle='--'))
    axes[1].set_title('New outline vs previous printed braid body',color='white')
    axes[1].annotate('',xy=(27,-70.5),xytext=(27,-37.5082),arrowprops={'arrowstyle':'<->','color':AMBER,'lw':2})
    axes[1].text(24,-54,'33.0 mm\ndownward\ngrowth',color=AMBER,ha='right')
    fig.suptitle('Front projection: X–Z outline, not a bounding-box substitute',color='white',fontsize=17)
    fig.text(.06,.035,'Cyan is the union of projected body triangles; the full backplate makes this outline filled.\nHand access is additional. This chart makes no claim that the same neighbour space remains available below.',color='white',fontsize=11)
    fig.savefig(d/'footprint.png',dpi=140,facecolor=BG);plt.close(fig)

    sections=json.loads((d/'side-sections.json').read_text())
    fig,axes=plt.subplots(1,2,figsize=(15,7),facecolor=BG)
    for ax,mode in zip(axes,['closed','released']):
        style(ax);ax.set_xlabel('Y away from board (mm)');ax.set_ylabel('Z up (mm)')
        paths=sections['closed'] if mode=='closed' else sections['frame']
        for polygon in paths:
            ax.add_patch(Patch(polygon,facecolor=CYAN,edgecolor=CYAN,lw=.8))
        if mode=='released':
            for polygon in sections['released']:
                ax.add_patch(Patch(polygon,facecolor=AMBER,edgecolor=AMBER,lw=.8))
        for shift,alpha in ([(0,.6)] if mode=='closed' else [(0,.25),(40,.3),(80,.45)]):
            for polygon in sections['payload']:
                points=np.asarray(polygon)+[shift,0]
                ax.add_patch(Patch(points,facecolor=TOOL,edgecolor='white',alpha=alpha))
        ax.set_xlim(-14,153 if mode=='released' else 88);ax.set_ylim(-77,12)
        ax.set_title('Closed: front stop + upper guide' if mode=='closed' else 'Press and hold; spool translates only +Y',color='white')
        if mode=='released':
            ax.annotate('',xy=(141,-26),xytext=(75,-26),arrowprops={'arrowstyle':'->','color':AMBER,'lw':2})
    fig.suptitle('Side sections: deliberate thumb release, no spool lift or sideways step',color='white',fontsize=17)
    fig.text(.055,.025,'Largest flange shown. Amber latch is a 7 mm-drop beam proxy, not a measured deformed shape.\nContinuous OCC clearance uses the full outer cylinder, including the empty bore and winding space.',color='white',fontsize=10)
    fig.savefig(d/'front-path.png',dpi=140,facecolor=BG);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path)
    d=parser.parse_args().output
    body=stl(d/f'{NAME}__installed.stl'); tool=stl(d/'payload__nominal-approx-55x30.stl')
    frame=stl(d/'frame__installed.stl'); opened=stl(d/'latch__released.stl')
    pr=stl(d/f'{NAME}__print-right-cheek.stl')
    render([(body,CYAN),(tool,TOOL)],d/'loaded.png','Spool front v13 — loaded candidate',
           'Approximate MAIYUM 55 × 30 mm spool. Same two mounting columns; taller body below.')
    render([(body,CYAN)],d/'empty.png','Spool front v13 — empty, latch closed',
           'Fixed rim floor and upper guide; integral spring and thumb paddle below. No axle.')
    render([(body,CYAN),(tool,TOOL)],d/'front.png','Spool front v13 — front view (+Y)',
           '48.8 mm wide. Body extends 33.0 mm below the previous braid body.',view=(0,90))
    render([(pr,CYAN)],d/'print.png','Spool front v13 — right cheek on the bed',
           'Leaf bends within Y–Z print layers. Peg supports still required; no slice produced.',view=(27,-55))
    render([(frame,CYAN),(opened,AMBER),(tool+[0,38,0],TOOL)],d/'released.png',
           'Spool front v13 — thumb held down, halfway out',
           'Spool offset: [0, 38, 0] mm. Amber is the assumed released spring shape.')
    diagram(d)


if __name__=='__main__':
    main()
