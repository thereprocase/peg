"""Review actual Orca extrusion; keep machine G-code private.

Samples support paths at <=0.2 mm, including IJ arcs, in nominal CAD space.
The socket-core screen excludes 0.30 mm near walls and 0.50 mm near ends.
It is a screen for trapped supports, not a full bead/contact certificate.
"""
from pathlib import Path
import sys,json,re,math,hashlib
import numpy as np
B=Path(sys.argv[1]);gcode=Path(sys.argv[2]);out=Path(sys.argv[3])
pose=json.loads((B/'tight-native/print-check.json').read_text());layout=json.loads((B/'layout.json').read_text())
rot=np.array(pose['rotation']);shift=np.array(pose['translation']);scale=1/.9946
sockets=[]
for t in layout['racks'][0]['tools']:
 u,b,p=map(np.array,(t['axis'],t['bar_axis'],t['tip']));side=np.cross(u,b)
 normals=np.array([b*math.cos(k*math.pi/3)+side*math.sin(k*math.pi/3) for k in range(6)])
 sockets.append((t,p,u,normals))
feature='Custom';pos=[0.,0.,0.];relative=True;epos=0.;absolute=True;data={};hits={t['name']:0 for t,_,_,_ in sockets}
number=r'[-+]?(?:\d*\.\d+|\d+)';arcs=0;bounds=[[float('inf')]*3,[-float('inf')]*3]
for line in gcode.open():
 if line.startswith(('; FEATURE:',';TYPE:')):feature=line.split(':',1)[1].strip();continue
 cmd=line.split(';')[0].strip();op=cmd.split(' ',1)[0]
 if op=='M82':relative=False
 if op=='M83':relative=True
 if op=='G90':absolute=True
 if op=='G91':absolute=False
 if op not in ('G0','G1','G2','G3','G92'):continue
 vals={k:float(v) for k,v in re.findall(r'\b([XYZEIJR])('+number+r')',cmd)}
 if op=='G92':
  if 'E' in vals:epos=vals['E']
  for i,k in enumerate('XYZ'):
   if k in vals:pos[i]=vals[k]
  continue
 old=pos.copy()
 for i,k in enumerate('XYZ'):
  if k in vals:pos[i]=vals[k] if absolute else pos[i]+vals[k]
 extrusion=vals.get('E',0) if relative else vals.get('E',epos)-epos
 if 'E' in vals:epos=epos+vals['E'] if relative else vals['E']
 if extrusion<=0 or feature=='Custom' or not any(k in vals for k in ('X','Y')):continue
 pts=[old,pos];length=math.dist(old,pos)
 if op in ('G2','G3'):
  assert 'R' not in vals,'R-format arc needs a separate parser'
  center=[old[0]+vals.get('I',0),old[1]+vals.get('J',0)];rad=math.dist(old[:2],center)
  a=math.atan2(old[1]-center[1],old[0]-center[0]);e=math.atan2(pos[1]-center[1],pos[0]-center[0]);sweep=(e-a)%(2*math.pi) if op=='G3' else -((a-e)%(2*math.pi))
  if abs(sweep)<1e-12:sweep=2*math.pi*(1 if op=='G3' else -1)
  length=math.hypot(abs(sweep)*rad,pos[2]-old[2])
  if 'upport' in feature:
   n=max(2,math.ceil(length/.2)+1);fractions=np.linspace(0,1,n);angles=a+fractions*sweep
   pts=np.column_stack([center[0]+rad*np.cos(angles),center[1]+rad*np.sin(angles),old[2]+fractions*(pos[2]-old[2])])
  else:
   # Arc extrema provide exact bounds without sampling infill centerlines.
   for angle in (0,math.pi/2,math.pi,3*math.pi/2):
    distance=(angle-a)%(2*math.pi) if sweep>0 else (a-angle)%(2*math.pi)
    if distance<=abs(sweep):pts.append([center[0]+rad*math.cos(angle),center[1]+rad*math.sin(angle),old[2]+distance/abs(sweep)*(pos[2]-old[2])])
  arcs+=1
 elif 'upport' in feature:pts=np.linspace(old,pos,max(2,math.ceil(length/.2)+1))
 if 'upport' in feature:
  low=pts.min(0);high=pts.max(0)
  for i in range(3):bounds[0][i]=min(bounds[0][i],float(low[i]));bounds[1][i]=max(bounds[1][i],float(high[i]))
 else:
  for pt in pts:
   for i in range(3):
    if pt[i]<bounds[0][i]:bounds[0][i]=pt[i]
    if pt[i]>bounds[1][i]:bounds[1][i]=pt[i]
 row=data.setdefault(feature,dict(moves=0,filament_mm=0.,maximum_path_length_mm=0.));row['moves']+=1;row['filament_mm']+=extrusion;row['maximum_path_length_mm']=max(row['maximum_path_length_mm'],length)
 if 'upport' in feature:
  nominal=pts.copy();nominal[:,:2]=(nominal[:,:2]-128)/scale+128;nominal[:,2]/=scale
  q=(nominal-shift)@rot
  for t,p,u,normals in sockets:
   delta=q-p;depth=delta@u;mask=(depth>.5)&(depth<t['guide']-.5)
   if mask.any():hits[t['name']]+=int(np.any(np.all(delta[mask]@normals.T<((t['af']+.38)/2-.3),axis=1)))
result=dict(gcode_sha256=hashlib.sha256(gcode.read_bytes()).hexdigest(),features=data,parsed_arc_moves=arcs,extrusion_centerline_bounds_mm=bounds,support_moves_entering_socket_core=hits,socket_core_screen_passed=not any(hits.values()),scope='Actual extrusion centerlines. Support IJ arcs and lines sampled at <=0.2 mm; other arc bounds include analytical axis extrema. Socket core excludes 0.30 mm at walls and 0.50 mm at guide ends; lead-ins and vents excluded. No bead-volume, contact, support removal or physical print certification.')
out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
