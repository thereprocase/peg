"""Plot the actual analytic helper sections and idealized beam stress field."""
from pathlib import Path
import os,json
os.environ.setdefault('MPLCONFIGDIR','/tmp/peg-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
import numpy as np
from rib_section_screen import hulls,section

root=Path(__file__).resolve().parents[3];cfg=json.loads((root/'bench/source/hx05_anisotropy_v1/config.json').read_text());data=json.loads((root/'bench/reviews/hx05-tensile-v1/rib-bending-sections.json').read_text())
fig,axes=plt.subplots(1,3,figsize=(11,8),layout='constrained')
for ax,rack,record in zip(axes,cfg['racks'],data['racks']):
    w=max(record['cases'],key=lambda c:c['nominal_peak_normal_tension_MPa']);tool=next(t for t in rack['tools'] if t['name']==w['tool']);polys=[section(p,w['plane_y_mm']) for p in hulls(tool,rack)]
    pts=np.vstack(polys);cent=np.array(w['centroid_xz_mm']);xmin,zmin=pts.min(0)-3;xmax,zmax=pts.max(0)+3
    x=np.linspace(xmin,xmax,240);z=np.linspace(zmin,zmax,600);X,Z=np.meshgrid(x,z);cloud=np.column_stack([X.ravel(),Z.ravel()]);inside=np.zeros(len(cloud),bool)
    for p in polys:inside|=MPath(p).contains_points(cloud)
    sigma=((cloud-cent)@np.array(w['normal_tension_gradient_xz_MPa_per_mm'])+w['normal_mean_stress_MPa']).reshape(X.shape);sigma=np.ma.masked_where(~inside.reshape(X.shape),sigma)
    im=ax.pcolormesh(X,Z,sigma,cmap='RdBu_r',vmin=-17,vmax=17,shading='auto')
    for p in polys:q=np.vstack([p,p[0]]);ax.plot(q[:,0],q[:,1],color='#333',lw=.7)
    ax.scatter(*cent,color='#333',s=12);ax.set_aspect('equal');ax.set_xlim(xmin,xmax);ax.set_ylim(zmin,zmax);ax.set_xlabel('Installed X · layer normal (mm)');ax.set_ylabel('Installed Z · height (mm)');ax.grid(alpha=.12)
    ax.set_title(f"{rack['id']} / {tool['name']}\nTwo root ribs at Y={w['plane_y_mm']:g} mm\nPeak tension {w['nominal_peak_normal_tension_MPa']:.1f} MPa",fontsize=11)
fig.suptitle('Bending screen · 20 N across layers + 5 N downward\nOnly each key’s two dense ribs credited',fontsize=15)
fig.colorbar(im,ax=axes,label='Nominal in-plane normal stress σYY (MPa); red = tension',shrink=.7)
fig.supxlabel('Idealized beam sections, not a whole-rack FOS. Surrounding walls omitted; torsion, local contact and pegs unassessed.',fontsize=10)
fig.savefig(root/'bench/reviews/hx05-tensile-v1/rib-root-bending-screen.png',dpi=160)
