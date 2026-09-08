"""CPU studio view of actual retained CAD and removable cradle CAD.

Run from the repository or this directory. Tessellation comes directly from
round_print_supports.support_parts(); both sets retain their actual 0.20 mm
interfaces. Colors identify material roles, not a multi-material print.
"""
from pathlib import Path
import sys,math
import numpy as np
import trimesh
from PIL import Image,ImageDraw,ImageFilter
ROOT=Path(__file__).resolve().parent
import render_round_common as studio
from round_print_supports import support_parts


def tessellate(part):
    vertices,faces=part.val().tessellate(.02,.12)
    v=np.array([[a.x,a.y,a.z] for a in vertices])
    return trimesh.Trimesh(vertices=v,faces=np.asarray(faces),process=False)


def main():
    groups=[]
    for orientation,center in [('upright',[-28.18,-4.10,0]),('side',[3.75,12.90,0])]:
        clean,parts,g,s=support_parts(orientation=orientation)
        meshes=[(tessellate(clean),False)]+[(tessellate(part),True) for name,part in parts]
        if orientation=='side':
            rot=trimesh.transformations.rotation_matrix(-math.pi/2,[0,1,0])
            for mesh,_ in meshes:mesh.apply_transform(rot)
        lo=meshes[0][0].vertices.min(axis=0);hi=meshes[0][0].vertices.max(axis=0)
        bed_z=min(model.vertices[:,2].min() for model,_ in meshes)
        shift=np.array(center)-[(lo[0]+hi[0])/2,(lo[1]+hi[1])/2,bed_z]
        for model,is_support in meshes:groups.append((model,model.vertices+shift,is_support))
    W,H=studio.W,studio.H;yy,xx=np.mgrid[:H,:W]
    glow=np.exp(-((xx-1470)/1100)**2-((yy-880)/660)**2)
    base=np.zeros((H,W,3),dtype=np.float32)+[12,21,30]
    base+=glow[:,:,None]*np.array([13,23,28]);img=Image.fromarray(np.uint8(base))
    mask=Image.new('L',(W,H),0);md=ImageDraw.Draw(mask)
    for model,v,is_support in groups:
        shadow=v.copy();shadow[:,:2]+=shadow[:,2,None]*[.4,.52];shadow[:,2]=-.02
        points=studio.project(shadow)
        for face in model.faces:md.polygon([tuple(q) for q in points[face,:2]],fill=120)
    img=Image.composite(Image.new('RGB',(W,H),(4,10,16)),img,mask.filter(ImageFilter.GaussianBlur(21)))
    rgb=np.array(img);depth=np.full((H,W),-np.inf,dtype=np.float32)
    key=studio.unit([-.6,-.9,1.3]);fill=studio.unit([.8,.5,.7]);half=studio.unit(key+studio.CAM)
    for model,v,is_support in groups:
        points=studio.project(v);normals=model.face_normals.copy()
        for i,face in enumerate(model.faces):
            normal=normals[i]
            if np.dot(normal,studio.CAM)<-1e-8:continue
            base=np.array([235,123,58.] if is_support else [32,146,152.])
            diffuse=.43+.59*max(0,np.dot(normal,key))+.27*max(0,np.dot(normal,fill))
            spec=max(0,np.dot(normal,half))**38*42
            color=np.clip(base*diffuse+spec,0,255).astype(np.uint8)
            studio.raster_triangle(rgb,depth,points[face,:2],points[face,2],color)
    img=Image.fromarray(rgb);draw=ImageDraw.Draw(img)
    draw.text((116,73),'round.',font=studio.font(112,True),fill='#eff4f0')
    draw.text((121,209),'REMOVABLE CRADLES FOR CIRCULAR BEARING SURFACES',font=studio.font(26,True),fill='#97b4b7')
    draw.text((1580,102),f"{s['interface_gap']:.2f} MM INTERFACES",font=studio.font(28,True),fill='#d3e0df')
    draw.text((1581,148),'ACTUAL CAD  ·  SUPPORTS SHOWN IN ORANGE',font=studio.font(18),fill='#739092')
    draw.line((121,278,2279,278),fill='#31454e',width=2)
    draw.text((194,942),'UPRIGHT SUPPORTS',font=studio.font(26,True),fill='#dce9e5')
    draw.text((194,989),'Cut the spine roots.',font=studio.font(22),fill='#8facb0')
    draw.text((194,1027),'Lift off the curved cradles.',font=studio.font(22),fill='#8facb0')
    draw.line((193,921,490,921),fill='#e88446',width=3)
    draw.text((1850,900),'SIDE CRADLES',font=studio.font(26,True),fill='#dce9e5')
    draw.text((1850,947),'Lift off cradles and pad.',font=studio.font(22),fill='#8facb0')
    draw.text((1850,985),'Preserve round bearings.',font=studio.font(22),fill='#8facb0')
    draw.line((1850,879,2225,879),fill='#e88446',width=3)
    draw.line((121,1205,2279,1205),fill='#31454e',width=2)
    draw.rectangle((122,1257,138,1273),fill='#2b969d');draw.text((155,1249),'KEEP',font=studio.font(20,True),fill='#a8c0c0')
    draw.rectangle((360,1257,376,1273),fill='#e88446');draw.text((393,1249),'REMOVE',font=studio.font(20,True),fill='#a8c0c0')
    draw.text((720,1251),'One filament; colors explain removal. Inspect the interface in your slicer and test the print.',font=studio.font(19),fill='#779396')
    out=ROOT/'visuals'/'round-print-options.png';img.save(out,optimize=True);print(out)

if __name__=='__main__':main()
