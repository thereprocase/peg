"""Native planar sections, not an illustration of assumed wall thickness."""
from pathlib import Path
import sys,json
import FreeCAD as A,Part
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
B=Path(sys.argv[1]);data=json.loads((B/'native.json').read_text())
fig,axes=plt.subplots(1,3,figsize=(12,5.2))
for ax,r in zip(axes,data['racks']):
 for filename,color,width in [('body.brep','#333333',.65),('shafts.brep','#007f9c',1.1)]:
  shape=Part.Shape();shape.read(str(B/r['id']/filename))
  for wire in shape.slice(A.Vector(0,1,0),45.):
   for edge in wire.Edges:
    pp=edge.discretize(Deflection=.15)
    if len(pp)>1:ax.plot([p.x for p in pp],[p.z for p in pp],color=color,lw=width)
 ax.set_title(r['id']+' · '+{'HX05A':'Torx','HX05B':'metric','HX05C':'inch'}[r['id']]);ax.set_aspect('equal');ax.set_xlabel('Across board, mm');ax.grid(alpha=.15);ax.set_ylabel('Height, mm')
fig.suptitle('Native sections: 45 mm in front of the mounting face\nBlack: plastic boundaries · blue: reference steel',fontsize=12)
fig.tight_layout();fig.savefig(B.parent/'renders/sections.png',dpi=120)
