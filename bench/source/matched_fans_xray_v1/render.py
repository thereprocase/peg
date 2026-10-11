from pathlib import Path
import os,json,math,sys
os.environ['MPLCONFIGDIR']='/tmp/hx05-matplotlib'
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch,Polygon
from scipy.spatial import ConvexHull
import trimesh
root=Path(sys.argv[1]);(root/'xray').mkdir(exist_ok=True);data=json.loads((root/'layout.json').read_text())
colors=['#258779','#3d6fb1','#bc702f']
fig,axes=plt.subplots(1,3,figsize=(18,8.7),dpi=150)
fig.patch.set_facecolor('#fbfaf6')
for ax,rack,color in zip(axes,data['racks'],colors):
 ax.set_facecolor('#fbfaf6')
 mesh=trimesh.load(root/'tight-native'/rack['id']/'installed.stl',force='mesh',process=False)
 triangles=np.asarray(mesh.triangles)[:,:,[0,2]].copy()
 a=triangles[:,1]-triangles[:,0];b=triangles[:,2]-triangles[:,0];area=a[:,0]*b[:,1]-a[:,1]*b[:,0]
 triangles=triangles[np.abs(area)>1e-7];area=area[np.abs(area)>1e-7]
 triangles[area<0]=triangles[area<0][:,[0,2,1]]
 # Positive winding produces one solid projection; no triangulation edges.
 ax.add_patch(PathPatch(MPath.make_compound_path_from_polys(triangles),facecolor=color,edgecolor='none',alpha=.19,zorder=1))
 palette=plt.get_cmap('tab10').colors
 ordered=sorted(rack['tools'],key=lambda t:t.get('p2p',t['af']))
 for i,t in enumerate(ordered):
  p,u,b,c=map(np.array,(t['tip'],t['axis'],t['bar_axis'],t['top']));side=np.cross(u,b)
  if 'p2p' in t:
   theta=np.linspace(0,2*math.pi,64,endpoint=False);rr=t['p2p']/2
  else:theta=math.pi/6+np.arange(6)*math.pi/3;rr=t['af']/math.sqrt(3)
  ring=rr*(np.cos(theta)[:,None]*b+np.sin(theta)[:,None]*side)
  vertices=np.vstack([p+ring,c+ring])[:,[0,2]];poly=vertices[ConvexHull(vertices).vertices]
  col=palette[i]
  ax.add_patch(Polygon(poly,closed=True,facecolor=col,edgecolor=col,lw=.6,zorder=3))
  # Exact orthographic capsule projection: endpoint discs swept along the bar.
  ends=np.array([c-b*(t['bar']/2-9),c+b*(t['bar']/2-9)])[:,[0,2]]
  theta=np.linspace(0,2*math.pi,64,endpoint=False)
  circles=ends[:,None,:]+9*np.array([np.cos(theta),np.sin(theta)]).T[None,:,:]
  verts=circles.reshape(-1,2);hull=verts[ConvexHull(verts).vertices]
  ax.add_patch(Polygon(hull,closed=True,facecolor=col,edgecolor='white',lw=.8,alpha=.88,zorder=4))
  # Mark the seated tip and sleeve entrance without hiding shaft geometry.
  tip=p[[0,2]];mouth=np.array(t['mouth'])[[0,2]]
  ax.plot(*tip,'o',ms=3,color=col,zorder=5)
  ax.plot(*mouth,'o',ms=3.5,mfc='#fbfaf6',mec=col,mew=1,zorder=5)
  upper=ends[np.argmax(ends[:,1])]
  ax.annotate(t['name'],xy=upper,xytext=(4,10),textcoords='offset points',fontsize=10,fontweight='bold',color=col,zorder=6)
 ax.set_xlim(-125,235);ax.set_ylim(-278,145);ax.set_aspect('equal');ax.axis('off')
 ax.set_title(rack['set']+' · '+rack['name'].capitalize(),fontsize=18,fontweight='bold',pad=14,color=color)
 ax.plot([-100,-50],[-263,-263],color='#41464a',lw=2)
 ax.text(-75,-254,'50 mm',ha='center',fontsize=10,color='#41464a')
fig.suptitle('FRONT-ON X-RAY  ·  SHAFTS THROUGH THE HOLDERS',fontsize=21,fontweight='bold',y=.985,color='#252d31')
fig.text(.5,.035,'Same scale · orthographic view toward the pegboard · filled dot = seated tip · open dot = sleeve entrance',ha='center',fontsize=12,color='#41464a')
fig.text(.5,.008,'Projected crossings can be separated in depth. Handle orientations shown are the modeled positions.',ha='center',fontsize=11,color='#61696b')
fig.subplots_adjust(left=.025,right=.975,top=.9,bottom=.085,wspace=.07)
fig.savefig(root/'xray/front-xray.png',dpi=150,facecolor=fig.get_facecolor())
fig.savefig(root/'xray/front-xray.webp',dpi=110,facecolor=fig.get_facecolor(),pil_kwargs={'quality':70,'method':6})
print(root/'xray/front-xray.png')
