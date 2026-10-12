from pathlib import Path
import math,re,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
levels=[54.2,129.6];number=r'[-+]?(?:\d*\.\d+|\d+)';colors={'wall':'#286b91','solid':'#159471','sparse':'#c8c9c1','bridge':'#d48925','support':'#a57fb1'}
def parse(path):
 out=[{} for _ in levels];pos=np.zeros(3);relative=True;epos=0.;feature='Custom';absolute=True
 for line in Path(path).open():
  if line.startswith(('; FEATURE:',';TYPE:')):feature=line.split(':',1)[1].strip();continue
  cmd=line.split(';')[0].strip();op=cmd.split(' ',1)[0]
  if op=='M82':relative=False
  if op=='M83':relative=True
  if op=='G90':absolute=True
  if op=='G91':absolute=False
  if op not in ('G0','G1','G2','G3','G92'):continue
  vals={k:float(v) for k,v in re.findall(r'\b([XYZEIJ])('+number+r')',cmd)}
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
  selected=next((i for i,z in enumerate(levels) if abs(pos[2]-z)<.01),None)
  if selected is None:continue
  group='wall' if 'wall' in feature.lower() else ('sparse' if 'Sparse' in feature else ('support' if 'upport' in feature else ('bridge' if 'Bridge' in feature else 'solid')))
  pts=np.array([old[:2],pos[:2]])
  if op in ('G2','G3'):
   c=old[:2]+[vals.get('I',0),vals.get('J',0)];r=np.linalg.norm(old[:2]-c);a=math.atan2(old[1]-c[1],old[0]-c[0]);b=math.atan2(pos[1]-c[1],pos[0]-c[0]);s=(b-a)%(2*math.pi) if op=='G3' else -((a-b)%(2*math.pi))
   if abs(s)<1e-12:s=2*math.pi*(1 if op=='G3' else -1)
   angle=np.linspace(a,a+s,max(2,math.ceil(abs(s)*r/.2)+1));pts=c+np.column_stack([np.cos(angle),np.sin(angle)])*r
  rot=np.array([[2**-.5,2**-.5],[-2**-.5,2**-.5]]);pts=((pts-128)/ (1/.9946))@rot.T
  out[selected].setdefault(group,[]).append(pts)
 return out
sets=[parse(sys.argv[1]),parse(sys.argv[2])];fig,axes=plt.subplots(2,2,figsize=(13,12));fig.patch.set_facecolor('#faf8f0')
for row,z in enumerate(levels):
 points=np.vstack([p for data in sets for group in data[row].values() for p in group]);low=points.min(0);high=points.max(0)
 for col,label in enumerate(['Published lightweight v2','Corrected attachments']):
  ax=axes[row,col];ax.set_facecolor('#faf8f0')
  for group in ['sparse','support','bridge','solid','wall']:
   paths=sets[col][row].get(group,[])
   if paths:ax.add_collection(LineCollection(paths,colors=colors[group],linewidths=.7 if group in ['wall','solid'] else .45,alpha=.85))
  ax.set_xlim(low[0]-4,high[0]+4);ax.set_ylim(low[1]-4,high[1]+4);ax.set_aspect('equal');ax.set_title(f'{label} · actual print Z {z:g} mm');ax.set_xlabel('Print XY, bed yaw undone (mm)');ax.set_ylabel('mm');ax.grid(alpha=.12)
fig.suptitle('Actual Orca extrusion paths — inch rack\nBlue walls · green solid infill · gray sparse infill · orange bridges',fontsize=15)
fig.tight_layout(rect=[0,0,1,.94]);fig.savefig(sys.argv[3],dpi=150)
print('Actual layer paths rendered')
