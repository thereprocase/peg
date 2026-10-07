"""Classify actual review extrusion in installed coordinates; relative-E Orca jobs."""
from pathlib import Path
import argparse,hashlib,json,math,re
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser();p.add_argument('id');p.add_argument('slice',type=Path);a=p.parse_args()
d=ROOT/'bench/reviews/canted-hex-keys-v2'/a.id;r=json.loads((d/'report.json').read_text());sr=json.loads((a.slice/'summary.json').read_text());code=(a.slice/'plate_1.gcode').read_text();inv=np.linalg.inv(np.array(r['pose_matrix']).reshape(4,4));shift=np.array(sr['translation_mm']);scale=sr['scale']
assert 'M83' in code
number=r'[-+]?(?:\d*\.\d+|\d+)';feat='Custom';pos=np.zeros(3);data={};relative=True;plot={}
for line in code.splitlines():
 if line.startswith(('; FEATURE:',';TYPE:')):feat=line.split(':',1)[1].strip();continue
 if line.startswith('M82'):relative=False
 if line.startswith('M83'):relative=True
 if not line.startswith(('G1 ','G2 ','G3 ')):continue
 vals={k:float(v) for k,v in re.findall(r'\b([XYZEIJ])('+number+r')',line.split(';')[0])};old=pos.copy()
 for i,k in enumerate('XYZ'):
  if k in vals:pos[i]=vals[k]
 if vals.get('E',0)<=0 or not any(k in vals for k in ['X','Y']) or feat=='Custom':continue
 assert relative,'Absolute E requires a separate extrusion parser'
 pts=[old.copy(),pos.copy()]
 if line.startswith(('G2 ','G3 ')) and ('I' in vals or 'J' in vals):
  # Follow the commanded arc sweep; a shallow arc may have a very large radius.
  center=old[:2]+[vals.get('I',0),vals.get('J',0)];rad=np.linalg.norm(old[:2]-center)
  start=math.atan2(old[1]-center[1],old[0]-center[0]);end=math.atan2(pos[1]-center[1],pos[0]-center[0]);sweep=(end-start)%(2*math.pi) if line.startswith('G3 ') else -((start-end)%(2*math.pi))
  pts += [np.array([center[0]+rad*math.cos(t),center[1]+rad*math.sin(t),pos[2]]) for t in np.linspace(start,start+sweep,max(3,min(2048,math.ceil(abs(sweep)*rad/.2))))]
 q=(np.array(pts)-shift)/scale;q=np.c_[q,np.ones(len(q))]@inv.T;q=q[:,:3]
 if feat in ['Outer wall','Support','Support interface','Bridge','Overhang wall']:
  coords=(np.array(pts[:2])-shift)/scale
  plot.setdefault(feat,[]).append(coords.tolist())
 item=data.setdefault(feat,dict(extruded_filament_mm=0,minimum=[1e9]*3,maximum=[-1e9]*3,moves=0,body_side_filament_mm=0,body_moves=0,body_max_move_mm=0))
 item['extruded_filament_mm']+=vals['E'];item['minimum']=np.minimum(item['minimum'],q.min(0)).tolist();item['maximum']=np.maximum(item['maximum'],q.max(0)).tolist();item['moves']+=1
 if q[:,1].max()>.4:
  item['body_side_filament_mm']+=vals['E'];item['body_moves']+=1
  length=abs(sweep)*rad if line.startswith(('G2 ','G3 ')) and ('I' in vals or 'J' in vals) else float(np.linalg.norm(pos-old))
  item['body_max_move_mm']=max(item['body_max_move_mm'],length/scale)
dens=float(re.search(r'; filament_density: ([\d.]+)',code).group(1));factor=math.pi*(1.75/2)**2*dens/1000
for v in data.values():v['grams']=round(v['extruded_filament_mm']*factor,3);v['body_side_grams']=round(v['body_side_filament_mm']*factor,4)
t=re.search(r'total estimated time: ([^\n]+)',code)
result=dict(id=a.id,gcode_sha256=hashlib.sha256(code.encode()).hexdigest(),input_stl_sha256=sr['input_sha256'],time=t.group(1),density_g_cm3=dens,extrusion_grams=round(sum(v['grams'] for v in data.values()),2),features=data,limits='Feature classification and deposited centerline bounds, with commanded arc sweeps sampled at <=0.2 mm where below the 2048-point cap. Supports may flare at the bed; support contact and removal need visual review.')
(d/'toolpaths.json').write_text(json.dumps(result,indent=2)+'\n', newline='\n');print(json.dumps({k:v for k,v in result.items() if k!='features'},indent=2));print(json.dumps({k:v for k,v in data.items() if 'upport' in k or 'ridge' in k or 'Overhang' in k},indent=2))

# Orthographic plots of the actual extrusion endpoints in print coordinates.
# Small arc curvature is omitted in this visualization; numerical bounds above use sweeps.
from html import escape
width,depth,height=r['print_bounds_mm'];extent=max(width,depth,height)+35;plot_height=max(depth,height)+35
panels=[]
colours={'Outer wall':'#748780','Support':'#d57c20','Support interface':'#873cb0','Bridge':'#e63243','Overhang wall':'#246ba0'}
for panel,axes,label in [(0,(0,1),'Top: print X / Y'),(1,(1,2),'Side: print Y / Z')]:
 paths=[]
 for feature in colours:
  segments=plot.get(feature,[])
  commands=[]
  for seg in segments:
   a,b=np.array(seg)
   commands.append(f'M{a[axes[0]]+17:.3f},{plot_height-a[axes[1]]-17:.3f}L{b[axes[0]]+17:.3f},{plot_height-b[axes[1]]-17:.3f}')
  paths.append(f'<path d="{" ".join(commands)}" fill="none" stroke="{colours[feature]}" stroke-width=".13" opacity=".65"/>')
 panels.append(f'<g transform="translate({panel*extent},15)"><text x="12" y="8" font-size="5">{label}</text>{"".join(paths)}</g>')
svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-40 0 {2*extent+40} {plot_height+32}"><rect x="-40" width="100%" height="100%" fill="#fff"/><text x="12" y="9" font-family="sans-serif" font-size="6">{result['id']}: actual extrusion paths</text>{"".join(panels)}<text x="12" y="{plot_height+25}" font-size="3.2" font-family="sans-serif">Gray: body walls · Orange/purple: supports · Red: bridge · Blue: overhang wall</text></svg>'
(d/'toolpaths.svg').write_text(svg, encoding='utf-8', newline='\n')
