import os
os.environ['MPLCONFIGDIR']='/tmp/peg-mpl'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json,numpy as np
from pathlib import Path
root=Path(__file__).resolve().parents[3];d=json.loads((root/'bench/reviews/hx05-tensile-v1/socket-axial-section.json').read_text());fig,ax=plt.subplots(figsize=(9,5))
force=np.linspace(25,200,120)
for r,color,label in zip(d['racks'],['#23874b','#296fa8','#d06f16'],['13190 inch / 3/32','13189 metric / 2 mm','33034 Torx / T9 shank']):
 t=min(r['tools'],key=lambda v:v['area_mm2']);a=t['area_mm2'];ax.plot(force,15*a/force,color=color,label=label);ax.fill_between(force,15*a/force,30*a/force,color=color,alpha=.12)
ax.axhline(1,color='#b33939',ls='--',lw=1);ax.axvline(100,color='#666',ls=':',lw=1);ax.set(xlim=(25,200),ylim=(0,10),xlabel='Axial tensile load on one sleeve (N)',ylabel='Nominal section tensile margin',title='Straight sleeve only · 1.2 mm solid band')
ax.grid(alpha=.2);ax.legend(loc='upper right');fig.text(.10,.015,'Solid lines: assumed 15 MPa strength. Shading up to 30 MPa reference.\nNo bending, stress concentrations, attachments or peg model; not a whole-rack safety factor.',fontsize=9);fig.tight_layout(rect=(0,.08,1,1));fig.savefig(root/'bench/reviews/hx05-tensile-v1/socket-axial-margin.png',dpi=160)
