"""Draw true mesh cross-sections: sparse bulk vs solid modifier, in print XY."""
from pathlib import Path
import json, numpy as np, trimesh
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'.local-runtime/hx05-density-v1'
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="820" viewBox="0 0 1500 820">', '<rect width="1500" height="820" fill="#faf8f0"/>', '<g font-family="sans-serif" fill="#26343a">', '<text x="45" y="55" font-size="30" font-weight="bold">HX05 / strategic solid cores — actual layer sections</text>', '<text x="45" y="94" font-size="20">Gray: 12% gyroid bulk · Green: 100% modifier · White: air / sockets</text>']
for i,(ident,title) in enumerate([('HX05C','13190 inch'),('HX05B','13189 metric'),('HX05A','33034 Torx')]):
 meshes=[trimesh.load(WORK/ident/(n+'-closed.stl'),force='mesh',process=True) for n in ['print-body','print-solid-core']]
 height=float(meshes[0].bounds[1,2]);cut=height*.4
 # Undo the common 45-degree print-bed yaw within this XY layer.
 rot=np.array([[2**-.5,2**-.5],[-2**-.5,2**-.5]])
 loops=[]
 for mesh in meshes:
  sec=mesh.section(plane_origin=[0,0,cut],plane_normal=[0,0,1]);assert sec is not None
  loops.append([p[:,:2]@rot.T for p in sec.discrete])
 pts=np.vstack(loops[0]);low=pts.min(0);high=pts.max(0)
 scale=min(390/(high[0]-low[0]),470/(high[1]-low[1]));centre=(low+high)/2
 def path(polygons):
  values=[]
  for poly in polygons:
   p=(poly-centre)*scale;p[:,0]+=i*490+255;p[:,1]=-p[:,1]+390
   values.append('M'+' L'.join(f'{x:.3f},{y:.3f}' for x,y in p)+' Z')
  return ' '.join(values)
 svg.append(f'<text x="{i*490+55}" y="145" font-size="24" font-weight="bold">{ident} · {title}</text>')
 svg.append(f'<path d="{path(loops[0])}" fill="#d5dbd7" fill-rule="evenodd" stroke="#677b73" stroke-width="1.2"/>')
 svg.append(f'<path d="{path(loops[1])}" fill="#197e67" fill-rule="evenodd" stroke="#105c4c" stroke-width="1.2"/>')
 check=json.loads((WORK/ident/'check.json').read_text())
 svg.append(f'<text x="{i*490+55}" y="675" font-size="19">Cut at print Z = {cut:.1f} mm</text>')
 svg.append(f'<text x="{i*490+55}" y="710" font-size="19">Solid core: {check["solid_core_percent"]:.1f}% of CAD volume</text>')
svg+=['<text x="45" y="768" font-size="19">These are XY layers, with the 45° bed yaw undone. Outer geometry is unchanged; no closed cavities were cut.</text>', '<text x="45" y="800" font-size="17">Modifier contours are real geometry. Wall paths, infill and supports require Orca review; no strength rating.</text>', '</g></svg>']
(WORK/'hx05-density-layer-sections.svg').write_text('\n'.join(svg))
print('Actual-section SVG written')
