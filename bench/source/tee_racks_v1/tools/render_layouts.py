"""Front and side views of selected tool envelopes. Layout study illustration, not a CAD render."""
import hashlib,json,os
from pathlib import Path
import subprocess,sys
HERE=Path(__file__).resolve().parents[1]
if len(sys.argv)>1 and sys.argv[1]=='--worker':
    part=sys.argv[2];record=json.loads((HERE/'study'/f'{part.lower()}_stand.json').read_text())
    os.environ.update(record['build_env']);sys.path.insert(0,str(HERE/'study'));import short as S
    lo=S.Layout(record['x']);print(json.dumps([dict(name=t['name'],pts=t['pts'].tolist(),rr=t['rr'].tolist(),mouth=t['mouth'].tolist(),rail=t['rail']) for t in lo.tools]));sys.exit(0)
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,axes=plt.subplots(3,2,figsize=(10,11),layout='constrained')
colors={'tee:0':'#258880','tee:1':'#d18032'}
receipt={}
for row,(part,setid) in enumerate([('HX05A','33034'),('HX05B','13189'),('HX05C','13190')]):
    data=json.loads(subprocess.run([sys.executable,__file__,'--worker',part],capture_output=True,text=True,check=True,timeout=30).stdout)
    record=json.loads((HERE/'study'/f'{part.lower()}_stand.json').read_text());screen=json.loads((HERE/'study'/f'{part.lower()}_layout-check.json').read_text())
    for col,coords in enumerate([(0,2),(1,2)]):
        ax=axes[row,col];a,b=coords
        for t in data:
            p=np.array(t['pts']);rr=np.array(t['rr']);color=colors[t['rail']];shaft=p[rr<8];bar=p[rr>=8]
            ax.plot(shaft[:,a],shaft[:,b],color=color,lw=1.5)
            ax.plot(bar[:,a],bar[:,b],color=color,lw=6,solid_capstyle='round',alpha=.7)
            m=np.array(t['mouth']);ax.scatter(m[a],m[b],s=20,facecolors='white',edgecolors=color,zorder=3)
            if col==0:ax.annotate(t['name'],(m[a],m[b]),xytext=(0,-13),textcoords='offset points',ha='center',fontsize=7,color=color)
        ax.set_aspect('equal');ax.grid(alpha=.12);ax.spines[['top','right']].set_visible(False)
        ax.set_ylabel('Height (mm)');ax.set_xlabel('Across board (mm)' if col==0 else 'Out from board (mm)')
        if col==0:
            ax.axvline(-118,color='#858585',ls=':',lw=1);ax.axvline(118,color='#858585',ls=':',lw=1);ax.invert_xaxis();ax.set_title(f'{part} / {setid} — front, 236 mm plate',loc='left',fontsize=11)
        else:
            ax.axvline(0,color='#555555',lw=3);ax.axvline(178,color='#c64b4b',ls='--',lw=1)
            ax.set_xlim(-5,190);ax.set_title(f'Side — {screen["worst_loaded_depth_mm"]:.1f} mm loaded depth',loc='left',fontsize=11)
            ax.text(178,ax.get_ylim()[0]+10,'178 mm target',rotation=90,fontsize=8,color='#a64141',ha='right')
    receipt[part]=dict(layout_sha256=hashlib.sha256((HERE/'study'/f'{part.lower()}_stand.json').read_bytes()).hexdigest(),dense_check_sha256=hashlib.sha256((HERE/'study'/f'{part.lower()}_layout-check.json').read_bytes()).hexdigest())
fig.suptitle('HX05 staggered rows — equal 48 mm grip spacing\nTool-envelope study; native CAD build pending',fontsize=14)
fig.savefig(HERE/'layouts.png',dpi=130);fig.savefig(HERE/'layouts.svg',metadata={'Date':None});plt.close(fig)
svg=HERE/'layouts.svg';svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n',encoding='utf-8',newline='\n')
receipt['renderer_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
receipt['outputs']={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ('layouts.png','layouts.svg')}
(HERE/'layout-visuals.json').write_text(json.dumps(receipt,indent=1)+'\n',encoding='utf-8',newline='\n')
