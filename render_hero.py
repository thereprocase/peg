"""Portable CPU studio render of the actual released STL meshes.

Requires numpy, Pillow, trimesh and shapely (repository requirements). The
upright STL remains the rendered geometry; triangle centroids outside the
functional profile receive the diagram's sacrificial-material accent.
No OpenGL, Blender, external textures, or generated concept imagery is used.
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import trimesh
from shapely.geometry import Point
from motion_design import get_parts

ROOT=Path(__file__).resolve().parent
W,H=2400,1400
SCALE=20.0

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

def mesh(name,center):
    m=trimesh.load(ROOT/'cad'/name,force='mesh')
    v=m.vertices.copy();lo=v.min(axis=0);hi=v.max(axis=0)
    v[:,0]-=(lo[0]+hi[0])/2;v[:,1]-=(lo[1]+hi[1])/2;v[:,2]-=lo[2]
    v+=center
    return m,v

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

def main():
    # A subdued floor spotlight keeps the model silhouettes legible.
    yy,xx=np.mgrid[:H,:W]
    glow=np.exp(-((xx-1470)/1100)**2-((yy-880)/660)**2)
    base=np.zeros((H,W,3),dtype=np.float32)+[12,21,30]
    base+=glow[:,:,None]*np.array([13,23,28])
    img=Image.fromarray(np.uint8(base))
    p,parts,_=get_parts();profile=parts['complete'];bounds=profile.bounds
    upright,uv=mesh('anchor_upright_supported.stl',[-28.18,-4.10,0])
    flat,fv=mesh('anchor_default_3p94mm.stl',[3.75,12.90,0])
    objects=[(upright,uv,True),(flat,fv,False)]
    # Shadows project the real triangles onto the same Z=0 studio floor.
    mask=Image.new('L',(W,H),0);md=ImageDraw.Draw(mask)
    for m,vertices,isup in objects:
        shadow=vertices.copy();shadow[:,:2]+=shadow[:,2,None]*[.40,.52];shadow[:,2]=-.02
        points=project(shadow)
        for face in m.faces:md.polygon([tuple(q) for q in points[face,:2]],fill=120)
    mask=mask.filter(ImageFilter.GaussianBlur(21))
    img=Image.composite(Image.new('RGB',(W,H),(4,10,16)),img,mask)
    # Exact triangle rasterization with a depth buffer, diffuse and specular light.
    rgb=np.array(img);depth=np.full((H,W),-np.inf,dtype=np.float32)
    key=unit([-.6,-.9,1.3]);fill=unit([.8,.5,.7]);half=unit(key+CAM)
    for m,vertices,isup in objects:
        projected=project(vertices)
        for fi,face in enumerate(m.faces):
            normal=m.face_normals[fi]
            if np.dot(normal,CAM)<-1e-8:continue
            color=np.array([32,146,152.],dtype=float)
            if isup:
                center=m.triangles_center[fi]
                design_y=center[1]+bounds[0]
                design_z=center[2]+bounds[1]
                if profile.distance(Point(design_y,design_z))>0.002:
                    color=np.array([235,123,58.],dtype=float)
            diffuse=.43+.59*max(0,np.dot(normal,key))+.27*max(0,np.dot(normal,fill))
            spec=max(0,np.dot(normal,half))**38*42
            col=np.clip(color*diffuse+spec,0,255).astype(np.uint8)
            raster_triangle(rgb,depth,projected[face,:2],projected[face,2],col)
    img=Image.fromarray(rgb)
    draw=ImageDraw.Draw(img)
    draw.text((116,73),'peg.',font=font(112,True),fill='#eff4f0')
    draw.text((121,209),'ONE INTERFACE. TWO WAYS TO PRINT.',font=font(26,True),fill='#97b4b7')
    draw.text((1600,102),'¼ IN HOLES  /  1 IN GRID',font=font(28,True),fill='#d3e0df')
    draw.text((1601,148),'PARAMETRIC  ·  MODULAR  ·  FDM',font=font(19),fill='#739092')
    draw.line((121,278,2279,278),fill='#31454e',width=2)
    # Deliberately place labels outside the rendered silhouettes.
    draw.text((194,942),'UPRIGHT',font=font(28,True),fill='#dce9e5')
    draw.text((194,989),'Four thin cutaway webs.',font=font(24),fill='#8facb0')
    draw.text((194,1027),'Snip flush after printing.',font=font(24),fill='#8facb0')
    draw.line((193,921,439,921),fill='#e88446',width=3)
    draw.text((1850,900),'SIDE PRINT',font=font(28,True),fill='#dce9e5')
    draw.text((1850,947),'Full profile in each layer.',font=font(24),fill='#8facb0')
    draw.text((1850,985),'No sacrificial webs.',font=font(24),fill='#8facb0')
    draw.line((1850,879,2225,879),fill='#329ca3',width=3)
    draw.line((121,1205,2279,1205),fill='#31454e',width=2)
    draw.rectangle((122,1257,138,1273),fill='#2b969d')
    draw.text((155,1249),'KEEP THE ANCHOR',font=font(20,True),fill='#a8c0c0')
    draw.rectangle((609,1257,625,1273),fill='#e88446')
    draw.text((642,1249),'CUT THE WEBS',font=font(20,True),fill='#a8c0c0')
    draw.text((1240,1251),'Actual released CAD · colors identify material to remove',font=font(19),fill='#779396')
    out=ROOT/'visuals'/'anchor-hero.png';out.parent.mkdir(exist_ok=True)
    img.save(out,optimize=True)
    print(out)

if __name__=='__main__':main()
