"""Complete-mesh upright view, actual bed triangles, and dimensioned section."""
import argparse,json,struct
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Polygon
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def triangles(path):
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,80)[0];dt=np.dtype([('normal','<f4',(3,)),('v','<f4',(3,3)),('attr','<u2')]);return np.frombuffer(raw,dtype=dt,count=n,offset=84)['v'].astype(float)
def main():
 p=argparse.ArgumentParser();p.add_argument('directory',type=Path);d=p.parse_args().directory;c=json.loads((d/'candidate.json').read_text());t=triangles(d/c['print_file']);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1),1e-12)[:,None];light=np.clip(.65+.35*n@np.array([-.4,-.5,.75]),.2,1);colors=light[:,None]*np.array([.78,.59,.26])
 fig=plt.figure(figsize=(9,8));a=fig.add_subplot(111,projection='3d');a.add_collection3d(Poly3DCollection(t,facecolors=colors,edgecolors='none',linewidths=0,antialiaseds=False));a.add_collection3d(Poly3DCollection([[(0,0,0),(55,0,0),(55,106,0),(0,106,0)]],facecolors=[(.65,.74,.79,.20)],edgecolors='#637a85',linewidths=.5));a.set(xlim=(-5,55),ylim=(-5,108),zlim=(0,74),xlabel='Print X / mm',ylabel='Print Y / mm',zlabel='Print Z / mm');a.set_box_aspect((60,113,74));a.view_init(24,-48);a.set_title('Upright print pose • common flat bottom at Z=0\nPegs still require support planning; no slice performed');fig.savefig(d/'print-pose.png',dpi=170);plt.close(fig)
 b=triangles(d/'bed-contact.stl');fig,a=plt.subplots(figsize=(8,8),layout='constrained');a.add_collection(PolyCollection(b[:,:,:2],facecolors='#bf984f',edgecolors='none',antialiaseds=False));a.autoscale();a.set_aspect('equal');a.grid(alpha=.2);a.set(xlabel='Installed X / mm',ylabel='Installed Y / mm');a.set_title(f'Actual CAD bed face • {c["bed_contact"]["cad_face_area_mm2"]:.2f} mm²\nSingle connected contact, 14 × 48 mm open hole');a.text(0,48,'OPEN\n14 × 48',ha='center',va='center');fig.savefig(d/'bed-contact.png',dpi=170);plt.close(fig)
 sections=json.loads((d/'sections.json').read_text());fig,aa=plt.subplots(1,2,figsize=(10,7),layout='constrained')
 for a,(label,lines) in zip(aa,sections.items()):
  for line in lines:
   q=np.array(line);a.plot(q[:,0],q[:,1],color='#926b24',linewidth=1.6)
  a.set_aspect('equal');a.grid(alpha=.2);a.set_title(label+' complete mesh section');a.set_ylabel('Installed Z / mm');a.margins(.1);a.set_ylim(-75,12)
 aa[0].text(0,-6,'23.2 mm entry',ha='center');aa[0].text(0,-70,'14 mm open',ha='center');aa[1].text(48,-6,'77.2 mm entry',ha='center');aa[1].text(48,-70,'48 mm open',ha='center');fig.suptitle('R2 exterior/web/root rounds • 0.6 mm rim breaks\nUpper taper, 11 × 48 throat, lower passage and flat bed retained')
 fig.savefig(d/'dimensions.png',dpi=170);plt.close(fig)
if __name__=='__main__':main()
