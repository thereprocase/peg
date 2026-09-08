"""Portable rendering helpers for the round anchor; no baseline-file dependency."""
from pathlib import Path
import numpy as np
from PIL import ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
W,H=2400,1400
SCALE=20.0
BG='#f7f5ef'
INK='#243b3b'
TEAL='#177e80'
TEAL_DARK='#07565c'
BOARD='#d9c8a7'
BOARD_DARK='#8d7858'
MUTED='#677b7a'
GRID='#dddeda'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':INK,'axes.labelcolor':INK,'axes.edgecolor':GRID,'xtick.color':MUTED,'ytick.color':MUTED,'savefig.facecolor':BG})

def unit(v):
    v=np.asarray(v,dtype=float);return v/np.linalg.norm(v)
CAM=unit([.72,-.92,.65]);RIGHT=unit(np.cross([0,0,1],CAM));UP=np.cross(CAM,RIGHT)


def project(v):
    a=np.asarray(v)
    return np.column_stack([1230+SCALE*(a@RIGHT),1130-SCALE*(a@UP),a@CAM])

def font(size,bold=False):
    candidates=[Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
        Path('/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf')]
    for p in candidates:
        if p.exists():return ImageFont.truetype(str(p),size)
    return ImageFont.load_default(size=size)

def raster_triangle(rgb,depth,xy,d,col):
    lo=np.maximum(np.floor(xy.min(axis=0)).astype(int),[0,0]);hi=np.minimum(np.ceil(xy.max(axis=0)).astype(int),[W-1,H-1])
    if np.any(lo>hi):return
    a,b,c=xy
    den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
    if abs(den)<1e-8:return
    yy,xx=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1];xx=xx+.5;yy=yy+.5
    u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
    v=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den
    w=1-u-v
    zz=u*d[0]+v*d[1]+w*d[2]
    old=depth[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
    use=(u>=-1e-7)&(v>=-1e-7)&(w>=-1e-7)&(zz>old)
    old[use]=zz[use]
    rgb[lo[1]:hi[1]+1,lo[0]:hi[0]+1][use]=col

def dimension(ax, a, b, label, text_offset=(0,0), rotate=0):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="|-|", mutation_scale=4,
                                linewidth=.8, color=MUTED, zorder=5))
    mid=(np.asarray(a)+np.asarray(b))/2 + text_offset
    ax.text(*mid, label, fontsize=9, ha="center", va="center", rotation=rotate,
            color=MUTED, bbox=dict(facecolor=BG, edgecolor="none", pad=2))

def evenly_sample_path(poses,n=100):
    # Euclidean path length uses degrees as 0.55 mm for stable visible motion.
    dist=np.linalg.norm(np.diff(poses,axis=0)*[1,1,.55],axis=1)
    cumulative=np.r_[0,np.cumsum(dist)]
    if cumulative[-1]==0:
        return poses[:1]
    values=np.linspace(0,cumulative[-1],n)
    return np.column_stack([np.interp(values,cumulative,poses[:,i]) for i in range(3)])
