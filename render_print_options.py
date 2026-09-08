"""Exact profile/extrusion comparison of flat and sacrificial-web upright printing."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PatchPolygon, Rectangle, FancyArrowPatch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shapely.geometry import Polygon
from shapely.ops import triangulate
from motion_design import get_parts
from upright_supports_design import support_data
from render_study import BG, INK, TEAL, TEAL_DARK, ORANGE, MUTED, GRID, add_part_3d

ROOT=Path(__file__).resolve().parent


def extrude_band(poly,lo,hi):
    caps=[];sides=[]
    for triangle in triangulate(poly):
        if poly.covers(triangle.representative_point()):
            yz=np.asarray(triangle.exterior.coords)[:3]
            for x in [lo,hi]:caps.append(np.column_stack([np.full(3,x),yz]))
    ring=np.asarray(poly.exterior.coords)
    for a,b in zip(ring[:-1],ring[1:]):
        sides.append([[lo,*a],[hi,*a],[hi,*b],[lo,*b]])
    return caps+sides


def lines(ax,geom,**kwargs):
    if geom.is_empty:return
    if geom.geom_type in ['LineString','LinearRing']:
        q=np.asarray(geom.coords);ax.plot(q[:,0],q[:,1],**kwargs)
    elif hasattr(geom,'geoms'):
        for g in geom.geoms:lines(ax,g,**kwargs)


def leader(ax,xy,xytext,text):
    ax.annotate(text,xy=xy,xytext=xytext,ha='left',va='center',fontsize=9.5,color=INK,
        arrowprops=dict(arrowstyle='-',color=MUTED,lw=.8,
                        connectionstyle='angle,angleA=0,angleB=90,rad=3'))


def main():
    d=support_data();p,parts,z0=get_parts(d['parameters']);poly=parts['complete']
    webs={k:Polygon(v) for k,v in d['profiles_yz'].items()}
    fig=plt.figure(figsize=(16,10),facecolor=BG)
    fig.text(.045,.94,'TWO PRINT ORIENTATIONS. ONE FUNCTIONAL ANCHOR.',fontsize=22,fontweight='bold',color=INK)
    fig.text(.045,.897,'Print flat for a continuous filament path through the hook, or add cutaway webs when the host must print upright.',fontsize=12,color=MUTED)
    fig.add_artist(plt.Line2D([.045,.955],[.866,.866],transform=fig.transFigure,color=GRID,lw=1))
    headers=[('01  PRINT ON ITS SIDE',.045),('02  PRINT UPRIGHT',.355),('03  FOUR CUTAWAY WEBS',.665)]
    for text,x in headers:fig.text(x,.825,text,fontsize=12,fontweight='bold')

    # Panel one uses the identical functional polygon, only rotated onto a side.
    ax=fig.add_axes([.045,.39,.27,.37]);yz=np.asarray(poly.exterior.coords)
    xy=np.column_stack([yz[:,1],-yz[:,0]])
    ax.add_patch(PatchPolygon(xy,facecolor=TEAL,edgecolor=TEAL_DARK,lw=1.5))
    ax.text(-13,-p['spine_depth']-2,'Bed top view · build out of the page',ha='center',fontsize=9.5,color=MUTED)
    ax.set_aspect('equal');ax.set_xlim(-34,8);ax.set_ylim(-12,12);ax.axis('off')
    fig.text(.045,.737,'No sacrificial webs.',fontsize=12,color=INK)
    fig.text(.045,.686,'Build through the 4.0 mm width.\nThe tongue and neck follow\nthe same layer plane.',fontsize=11,color=MUTED,linespacing=1.65,va='top')

    # Panel two is an exact side section through an actual sacrificial web.
    ax=fig.add_axes([.352,.36,.278,.405])
    for web in webs.values():
        ax.add_patch(PatchPolygon(np.asarray(web.exterior.coords),facecolor=ORANGE,edgecolor='#a04c24',lw=1.1))
    ax.add_patch(PatchPolygon(yz,facecolor=TEAL,edgecolor=TEAL_DARK,lw=1.25))
    for web in webs.values():
        lines(ax,poly.boundary.intersection(web),color='#823d1d',lw=1.2,linestyle=(0,(3,2)))
    ymin=poly.bounds[0];zmin=poly.bounds[1]
    ax.plot([-11,8],[zmin-.15]*2,color=MUTED,lw=1)
    ax.annotate('BUILD UP',xy=(8,-9),xytext=(8,-25),ha='center',va='center',rotation=90,fontsize=8.5,color=MUTED,
        arrowprops=dict(arrowstyle='->',color=MUTED,lw=1))
    leader(ax,(-3.9,-4.4),(-17,-7.0),'45° ramps\ngrow from the spine')
    leader(ax,(-1.2,-27.4),(-17,-23.7),'Lower locator\ngets its own webs')
    ax.set_aspect('equal');ax.set_xlim(-18,11);ax.set_ylim(-34,8);ax.axis('off')
    fig.text(.355,.737,'Temporary webs support both projections.',fontsize=11,color=INK)

    # Panel three contains the same four prisms in their true X positions.
    ax3=fig.add_axes([.67,.35,.28,.415],projection='3d')
    add_part_3d(ax3,poly,p['width'])
    for name,web in webs.items():
        for lo,hi in d['web_x_bands']:
            # Explicit exploded translation only; individual prisms retain exact dimensions.
            dx=3 if lo>0 else -3
            faces=extrude_band(web,lo+dx,hi+dx)
            ax3.add_collection3d(Poly3DCollection(faces,facecolors=ORANGE,shade=True,
                lightsource=matplotlib.colors.LightSource(310,45)))
    ax3.set_xlim(-7,7);ax3.set_ylim(-12,8);ax3.set_zlim(-34,8)
    ax3.set_box_aspect([14,20,42]);ax3.set_proj_type('ortho');ax3.view_init(elev=21,azim=-48)
    ax3.set_facecolor(BG);ax3.axis('off')
    fig.text(.665,.737,'Two 0.50 mm webs under each overhang.',fontsize=11,color=INK)
    fig.text(.70,.357,'Exploded view: webs spread apart for clarity.',fontsize=9.5,color=MUTED)

    # A small exact X section makes the two-web spacing unambiguous.
    axb=fig.add_axes([.71,.235,.205,.095]);w=p['width'];
    axb.add_patch(Rectangle((-w/2,1.2),w,.5,facecolor=TEAL,edgecolor=TEAL_DARK,lw=.8))
    for lo,hi in d['web_x_bands']:
        axb.add_patch(Rectangle((lo,-.05),hi-lo,1.25,facecolor=ORANGE,edgecolor='#a04c24',lw=.7))
    inner=d['bridge_span_x_mm']/2
    axb.add_patch(FancyArrowPatch((-inner,.58),(inner,.58),arrowstyle='<->',mutation_scale=7,color=MUTED,lw=.8))
    axb.text(0,.06,f"{d['bridge_span_x_mm']:.1f} mm bridge",ha='center',va='center',fontsize=9,color=INK)
    axb.set_xlim(-2.6,2.6);axb.set_ylim(-.5,2);axb.axis('off')
    fig.text(.71,.233,'Section across the 4.0 mm width',fontsize=9,color=MUTED)

    fig.add_artist(plt.Line2D([.045,.955],[.208,.208],transform=fig.transFigure,color=GRID,lw=1))
    fig.text(.045,.308,'BLUE  ·  KEEP',fontsize=12,fontweight='bold',color=TEAL_DARK)
    fig.text(.355,.308,'ORANGE  ·  CUT AWAY',fontsize=12,fontweight='bold',color=ORANGE)
    fig.text(.045,.265,'The final anchor geometry stays the same.',fontsize=10.5,color=MUTED)
    fig.text(.355,.263,'Snip each roof and root flush.\nNever twist the tail to break off a web.',fontsize=10.5,color=MUTED,linespacing=1.5,va='top')
    fig.text(.045,.151,'One filament. Colors identify permanent and sacrificial geometry in this drawing.',fontsize=11,color=INK)
    fig.text(.045,.106,'Upright setup: use the host base or a brim; preview the 0.50 mm web toolpaths and bridge lines across the 2.70 mm gap.',fontsize=10.5,color=MUTED)
    fig.text(.045,.066,'After cutting: clear every remnant from the tongue, neck, locator and spine; test board fit. Qualify upright prints separately for the intended load.',fontsize=10.5,color=MUTED)
    out=ROOT/'visuals';out.mkdir(exist_ok=True)
    for ext in ['png','svg']:fig.savefig(out/f'print-options.{ext}',dpi=170)
    plt.close(fig)
    print(out/'print-options.png');print(out/'print-options.svg')


if __name__=='__main__':main()
