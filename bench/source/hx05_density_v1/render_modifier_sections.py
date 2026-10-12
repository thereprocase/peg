"""Actual fixed-pose XY sections, showing the four independent modifier masks."""
from pathlib import Path
import numpy as np, trimesh
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'.local-runtime/hx05-density-v1'
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1060" viewBox="0 0 1440 1060">','<rect width="1440" height="1060" fill="#faf8f0"/>','<g font-family="sans-serif" fill="#26343a">','<text x="35" y="45" font-size="28" font-weight="bold">Fixed bed face · strategic 100% infill masks</text>','<text x="35" y="78" font-size="19">Actual print XY sections. Gray: holder bulk · Green: modifier intersection · White: air</text>']
for col,(ident,title) in enumerate([('HX05C','13190 inch'),('HX05B','13189 metric'),('HX05A','33034 Torx')]):
 body=trimesh.load(WORK/ident/'print-drafted-body-closed.stl',force='mesh',process=True)
 masks=[trimesh.load(WORK/ident/f'print-modifier-{role}.stl',force='mesh',process=True) for role in ['foundation','mounts','sockets','ribs']]
 svg.append(f'<text x="{col*475+35}" y="120" font-size="23" font-weight="bold">{ident} · {title}</text>')
 rot=np.array([[2**-.5,2**-.5],[-2**-.5,2**-.5]])
 for row,fraction in enumerate([.25,.60]):
  height=float(body.bounds[1,2])*fraction
  sec=body.section(plane_origin=[0,0,height],plane_normal=[0,0,1]);assert sec is not None
  loops=[p[:,:2]@rot.T for p in sec.discrete];pts=np.vstack(loops);low=pts.min(0);high=pts.max(0);centre=(low+high)/2;scale=min(415/(high[0]-low[0]),340/(high[1]-low[1]))
  def path(polygons):
   values=[]
   for poly in polygons:
    p=(poly-centre)*scale;p[:,0]+=col*475+240;p[:,1]=-p[:,1]+row*420+325
    values.append('M'+' L'.join(f'{x:.3f},{y:.3f}' for x,y in p)+' Z')
   return ' '.join(values)
  d=path(loops);clip=f'clip-{col}-{row}'
  svg.append(f'<defs><clipPath id="{clip}"><path d="{d}" clip-rule="evenodd"/></clipPath></defs>')
  svg.append(f'<path d="{d}" fill="#d5dbd7" fill-rule="evenodd" stroke="#677b73" stroke-width="1.2"/>')
  svg.append(f'<g clip-path="url(#{clip})">')
  for mask in masks:
   section=mask.section(plane_origin=[0,0,height],plane_normal=[0,0,1])
   if section is not None:
    svg.append(f'<path d="{path([p[:,:2]@rot.T for p in section.discrete])}" fill="#197e67" fill-rule="evenodd"/>')
  svg.append('</g>')
  svg.append(f'<text x="{col*475+35}" y="{row*420+522}" font-size="18">Print Z = {height:.1f} mm</text>')
svg+=['<text x="35" y="995" font-size="19">Bed yaw is undone for readability only. Part orientation, tested fits and outside shape are unchanged.</text>','<text x="35" y="1028" font-size="18">Density regions are real masks, not toolpaths. Actual-profile slicing and print qualification remain pending.</text>','</g></svg>']
(WORK/'fixed-pose-modifier-sections.svg').write_text('\n'.join(svg)+'\n')
print('Fixed-pose modifier sections written')
