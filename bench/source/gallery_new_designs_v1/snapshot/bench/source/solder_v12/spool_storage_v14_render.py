"""v14 CAD-mesh previews and explicit lift envelope, using system Python.

Reuses only the frozen ordinary triangle-depth-buffer renderer from the superseded
study. It imports no v13 design geometry or mechanism assumptions.
"""
from pathlib import Path
import argparse
import json

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch

from spool_front_render import stl,render,style,rings,CYAN,TOOL,AMBER,BG

NAME='part-solder-spool-storage__v14__right-cheek__fit-pf02c9-hoop5'


def patch(ax,geom,color,alpha=1,outline=False,offset=(0,0),lw=1.5):
    for polygon in rings(geom):
        if not polygon or not polygon[0]:continue
        ax.add_patch(Patch(np.asarray(polygon[0])+offset,fill=not outline,
            facecolor=color,edgecolor=color,alpha=alpha,lw=lw))
        if not outline:
            for hole in polygon[1:]:
                ax.add_patch(Patch(np.asarray(hole)+offset,facecolor=BG,edgecolor=color,lw=.7))


def diagrams(d):
    shapes=json.loads((d/'projected-outlines.json').read_text())
    design=json.loads((d/f'{NAME}__design.json').read_text())
    zmin=design['bounds_installed'][2]-6
    fig,axes=plt.subplots(1,2,figsize=(12,9),facecolor=BG)
    for ax,key,title in zip(axes,['nominal-55x30','large-65x34'],['Nominal 55 × 30 mm','Largest 65 × 34 mm']):
        style(ax);ax.set(xlim=(-30,30),ylim=(zmin,12),xlabel='X across board (mm)',ylabel='Z up (mm)')
        patch(ax,shapes[key]['installed_occupied_external_perimeter'],CYAN,.2)
        patch(ax,shapes['body_material_projection'],CYAN,.5)
        patch(ax,shapes[key]['conservative_up_out_sweep_projection'],TOOL,.85,True)
        patch(ax,shapes[key]['extra_lift_envelope'],AMBER,.85)
        ax.set_title(title,color='white',fontsize=15)
    axes[0].text(-28,zmin+1,'8 mm lift; sweep stays within\ninstalled occupied perimeter.',color='white',fontsize=10)
    large=next(c for c in design['payload_cases'] if c['id']=='large-65x34')
    axes[1].annotate('',xy=(23,large['lifted_top_z_mm']),xytext=(23,large['installed_top_z_mm']),arrowprops={'arrowstyle':'<->','color':AMBER,'lw':2})
    axes[1].text(20,8,'8 mm lift fits below\nthe existing plate top',color=AMBER,ha='right',fontsize=10)
    fig.suptitle('Lift stays inside the installed occupied perimeter',color='white',fontsize=17)
    fig.text(.06,.025,'Cyan: installed exterior perimeter / material. White: full-cylinder up/out projection.\nNo extra X/Z envelope for these spools. Internal windows remain open; hand access is additional.',color='white',fontsize=10)
    fig.savefig(d/'footprint-lift.png',dpi=140,facecolor=BG);plt.close(fig)

    sections=json.loads((d/'side-sections.json').read_text())
    fig,axes=plt.subplots(1,2,figsize=(15,7),facecolor=BG)
    for ax,key,title in zip(axes,['nominal','large'],['Nominal storage position','Largest spool: lift 8 mm, then out 65 mm']):
        style(ax);ax.set(xlim=(-12,145 if key=='large' else 80),ylim=(zmin,12),xlabel='Y away from board (mm)',ylabel='Z up (mm)')
        for s in sections['body']:patch(ax,s,CYAN)
        moves=[((0,0),.85)] if key=='nominal' else [((0,0),.2),((0,8),.35),((65,8),.65)]
        for move,alpha in moves:
            for s in sections[key]:patch(ax,s,TOOL,alpha,offset=move)
        ax.set_title(title,color='white',fontsize=14)
        if key=='large':
            centre=large['centre'][2]
            ax.annotate('',xy=(40,centre+8),xytext=(40,centre),arrowprops={'arrowstyle':'->','color':AMBER,'lw':2})
            ax.annotate('',xy=(105,centre+8),xytext=(40,centre+8),arrowprops={'arrowstyle':'->','color':AMBER,'lw':2})
    fig.suptitle('Open storage cradle — no lid, axle, latch or feeding mechanism',color='white',fontsize=17)
    fig.text(.055,.025,'Curved floor: radius 34 mm, front rise 6.15 mm. Small and large spools settle at the same bottom.\nConservative solid-cylinder sweeps prove the lift and outward segments clear; no spring or pinch-release step.',color='white',fontsize=10)
    fig.savefig(d/'up-out-path.png',dpi=140,facecolor=BG);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path)
    parser.add_argument('--views-only',action='store_true');args=parser.parse_args();d=args.output
    body=stl(d/f'{NAME}__installed.stl');tool=stl(d/'payload__nominal-55x30.stl')
    large=stl(d/'payload__large-65x34.stl');small=stl(d/'payload__small-40x20.stl')
    narrow=stl(d/'payload__narrow-40x8.stl')
    render([(body,CYAN),(tool,TOOL)],d/'loaded.png','Open spool storage v14 — 55 × 30 mm',
        'Simple curved tub. Lift slightly and take the spool to the bench. No feeding hardware.')
    render([(body,CYAN)],d/'empty.png','Open spool storage v14 — empty',
        '48.8 mm wide; open top and front. Curved bottom, shallow side rims and a windowed mount.')
    render([(body,CYAN),(large,TOOL)],d/'largest-loaded.png','Open storage v14 — largest envelope',
        '65 mm OD × 34 mm width. Approximate geometric coverage; actual spools require measurement.')
    render([(body,CYAN),(narrow,TOOL)],d/'narrow-loaded.png','Open storage v14 — narrow bobbin',
        '40 mm OD × 8 mm width. Same roomy cradle; narrow bobbins can lean and have less tipping margin.')
    render([(body,CYAN),(tool,TOOL)],d/'front.png','Open spool storage v14 — front (+Y)',
        'Same two mounting columns. No lid, axle or latch.',view=(0,90))
    render([(stl(d/f'{NAME}__print-right-cheek.stl'),CYAN)],d/'print.png','Open storage v14 — right cheek on bed',
        'Print geometry screen only; peg supports still required. No toolpaths or printing performed.',view=(27,-55))
    render([(body,CYAN),(large+[0,35,8],TOOL)],d/'lifted-out.png','Open storage v14 — lifted and coming out',
        'Spool offset [0, 35, 8] mm. No lateral slide, release button or required spool rotation.')
    parts=[]
    for x,t in zip([-70,0,70],[small,tool,large]):parts.extend([(body+[x,0,0],CYAN),(t+[x,0,0],TOOL)])
    render(parts,d/'range.png','One open cradle — three storage envelopes',
        '40 × 20, 55 × 30, and 65 × 34 mm. Three copies shown for comparison.',view=(18,68))
    if not args.views_only:diagrams(d)


if __name__=='__main__':main()
