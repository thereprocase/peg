"""Render the computed pegboard geometry and its checked rigid-body motion.

No rendered pose is invented: animation samples are piecewise-linear samples of
the removal path recorded in motion_results.json. Run after motion_design.py.
"""
from __future__ import annotations

import argparse
import io
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PatchPolygon, Rectangle, FancyArrowPatch, Circle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from PIL import Image
from shapely.geometry import Polygon, Point, box
from shapely.ops import triangulate

ROOT = Path(__file__).resolve().parent
BG = "#f7f5ef"
INK = "#243b3b"
TEAL = "#177e80"
TEAL_DARK = "#07565c"
ORANGE = "#db713b"
BOARD = "#d9c8a7"
BOARD_DARK = "#8d7858"
MUTED = "#677b7a"
GRID = "#dddeda"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "text.color": INK, "axes.labelcolor": INK,
    "axes.edgecolor": GRID, "xtick.color": MUTED,
    "ytick.color": MUTED, "savefig.facecolor": BG,
})


def _first(mapping, keys, default=None):
    for key in keys:
        if key in mapping:
            return mapping[key]
    return default


def load_study(path):
    data = json.loads(Path(path).read_text())
    if isinstance(data, list):
        data = data[0]
    if "default" in data and isinstance(data["default"], dict):
        data = data["default"]
    if "variants" in data:
        variants = data["variants"]
        if isinstance(variants, dict):
            variants = list(variants.values())
        data = min(variants, key=lambda v: abs(_first(v,["parameters","params"])["board_thickness"]-3.94))
    p = _first(data, ["params", "parameters"])
    if p is None and (ROOT / "geometry.json").exists():
        gd = json.loads((ROOT / "geometry.json").read_text())
        p = _first(gd, ["params", "parameters"])
    path = _first(data, ["removal_poses", "removal_path", "path", "poses"])
    if path is None:
        for key in ["motion", "removal", "path_study"]:
            if isinstance(data.get(key), dict):
                path = _first(data[key], ["path", "poses", "removal_path"])
                if path is not None:
                    break
    if p is None or path is None:
        raise ValueError(f"Expected params and removal_path/path/poses in {path}")
    from motion_design import get_parts
    p, parts, z0 = get_parts(p)
    if isinstance(path[0],dict):
        path = [[x["y"],x["z"],x["theta_deg"]] for x in path]
    poses = np.asarray(path, dtype=float)
    if poses.shape[1] != 3:
        raise ValueError("Motion poses must contain [translation_y, translation_z, angle_deg].")
    if np.linalg.norm(poses[0]) > np.linalg.norm(poses[-1]):
        poses = poses[::-1]
    return data, p, parts, z0, poses


def transformed_profile(poly, pose):
    y, z, angle = pose
    a = np.deg2rad(angle)
    rot = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    return np.asarray(poly.exterior.coords) @ rot.T + [y, z]


def board_section(ax, p, bottom=-37, top=12, labels=False):
    half = math.sqrt(p["hole_diameter"]**2 - p["width"]**2)/2
    t, pitch = p["board_thickness"], p["pitch"]
    intervals = [(bottom, -pitch-half), (-pitch+half, -half), (half, top)]
    for lo, hi in intervals:
        ax.add_patch(Rectangle((-t, lo), t, hi-lo, facecolor=BOARD,
                               edgecolor=BOARD_DARK, linewidth=1.0, zorder=1))
    for z in [0, -pitch]:
        ax.plot([-t-2.5, 6], [z, z], color=BOARD_DARK, lw=.55,
                linestyle=(0, (4, 4)), alpha=.7, zorder=0)
        # A fine red line shows the extra conservative model margin.
        if p.get("hole_clearance", 0) > 0:
            for s in [-1, 1]:
                zb = z+s*(half-p["hole_clearance"])
                ax.plot([-t, 0], [zb, zb], color=ORANGE, lw=.6, alpha=.8, zorder=2)
    if labels:
        ax.text(-t/2, top+.8, "PEGBOARD", ha="center", va="bottom", fontsize=8,
                fontweight="bold", color=BOARD_DARK)
    return half


def part_section(ax, poly, pose=(0,0,0), alpha=1, color=TEAL, zorder=4):
    patch = PatchPolygon(transformed_profile(poly, pose), closed=True,
                         facecolor=color, edgecolor=TEAL_DARK,
                         linewidth=1.35, joinstyle="round", alpha=alpha, zorder=zorder)
    ax.add_patch(patch)
    return patch


def clean_axes(ax, xlim, ylim, axis=False):
    ax.set_facecolor(BG)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect("equal")
    if axis:
        ax.set_xlabel("Front / away from board  →   [mm]", fontsize=9)
        ax.set_ylabel("Height [mm]", fontsize=9)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(lw=.5, color=GRID, zorder=-1)
        ax.tick_params(labelsize=8)
    else:
        ax.axis("off")


def leader(ax, xy, xytext, text, ha="left", color=INK):
    ax.annotate(text, xy=xy, xytext=xytext, ha=ha, va="center",
                fontsize=9.5, color=color,
                arrowprops=dict(arrowstyle="-", color=color, lw=.9,
                                connectionstyle="angle,angleA=0,angleB=90,rad=3"))


def dimension(ax, a, b, label, text_offset=(0,0), rotate=0):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="|-|", mutation_scale=4,
                                linewidth=.8, color=MUTED, zorder=5))
    mid=(np.asarray(a)+np.asarray(b))/2 + text_offset
    ax.text(*mid, label, fontsize=9, ha="center", va="center", rotation=rotate,
            color=MUTED, bbox=dict(facecolor=BG, edgecolor="none", pad=2))


def extrusion_faces(poly, width):
    """Triangulated planar caps and actual straight polygon-edge side walls."""
    caps=[]
    for triangle in triangulate(poly):
        if not poly.covers(triangle.representative_point()):
            continue
        yz=np.asarray(triangle.exterior.coords)[:3]
        for x in [-width/2, width/2]:
            caps.append(np.column_stack([np.full(3,x),yz]))
    outline=np.asarray(poly.exterior.coords)
    sides=[]
    for p1,p2 in zip(outline[:-1],outline[1:]):
        sides.append([[-width/2,*p1],[width/2,*p1],[width/2,*p2],[-width/2,*p2]])
    return caps,sides


def add_part_3d(ax, poly, width):
    caps,sides=extrusion_faces(poly,width)
    ax.add_collection3d(Poly3DCollection(caps, facecolors=TEAL,
                                        shade=True, lightsource=matplotlib.colors.LightSource(310,45)))
    ax.add_collection3d(Poly3DCollection(sides, facecolors=TEAL_DARK,
                                        shade=True,
                                        lightsource=matplotlib.colors.LightSource(310,45)))
    yz=np.asarray(poly.exterior.coords)
    for x in [-width/2,width/2]:
        ax.plot(np.full(len(yz),x),yz[:,0],yz[:,1], color=TEAL_DARK,lw=.55)


def isometric(ax, p, poly, board=False):
    add_part_3d(ax,poly,p["width"])
    bounds=poly.bounds
    ax.set_xlim(-10,10);ax.set_ylim(bounds[0]-2,12);ax.set_zlim(-34,8)
    ax.set_box_aspect([20,12-bounds[0]+2,42])
    ax.view_init(elev=20,azim=27)
    ax.set_proj_type("ortho");ax.axis("off");ax.set_facecolor(BG)


def evenly_sample_path(poses,n=100):
    # Euclidean path length uses degrees as 0.55 mm for stable visible motion.
    dist=np.linalg.norm(np.diff(poses,axis=0)*[1,1,.55],axis=1)
    cumulative=np.r_[0,np.cumsum(dist)]
    if cumulative[-1]==0:
        return poses[:1]
    values=np.linspace(0,cumulative[-1],n)
    return np.column_stack([np.interp(values,cumulative,poses[:,i]) for i in range(3)])


def save_summary(p,parts,z0,poses,out):
    fig=plt.figure(figsize=(16,10),facecolor=BG)
    fig.text(.045,.947,"MODULAR PEGBOARD ANCHOR",fontsize=24,fontweight="bold")
    fig.text(.045,.911,
             f"¼ in holes  /  1 in grid  /  {p['board_thickness']:.2f} mm board default  /  thickness is parametric",
             fontsize=12,color=MUTED)
    fig.add_artist(plt.Line2D([.045,.955],[.887,.887],transform=fig.transFigure,color=GRID,lw=1))
    ax=fig.add_axes([.045,.37,.38,.48])
    board_section(ax,p,labels=True)
    part_section(ax,parts["complete"],poses[0])
    clean_axes(ax,(-20,27),(-36,13))
    ax.text(-19,11,"01   SEATED",fontweight="bold",fontsize=11)
    t=p["board_thickness"]
    leader(ax,(-t-1.8,z0+2.5),(-18,6.8),"Rear tail\nretains the mount")
    leader(ax,(p["spine_depth"],-10),(11,-8),"Flat front spine\nfuses to your part")
    leader(ax,(-1.4,-p["pitch"]+z0),(10,-24),"Lower locator\nlimits rotation")
    dimension(ax,(-12,0),(-12,-p["pitch"]),"25.40 mm",(-1.8,0),90)
    dimension(ax,(-t,9),(0,9),f"t = {t:.2f}",(0,1.7))
    iso=fig.add_axes([.40,.345,.30,.52],projection="3d")
    isometric(iso,p,parts["complete"])
    fig.text(.47,.837,"02   ACTUAL EXTRUDED PROFILE",fontsize=11,fontweight="bold")
    fig.text(.48,.375,f"{p['width']:.2f} mm constant width\nRounded tongue • tapered locator",fontsize=10,color=MUTED)
    axp=fig.add_axes([.74,.40,.20,.39])
    yz=np.asarray(parts["complete"].exterior.coords)
    # Rotate only the drawing for a clear print-bed silhouette; x is vertical build axis.
    axp.add_patch(PatchPolygon(np.column_stack([yz[:,1],-yz[:,0]]),facecolor=TEAL,
                                edgecolor=TEAL_DARK,lw=1.2))
    axp.set_xlim(-35,8);axp.set_ylim(-12,12);axp.set_aspect("equal");axp.axis("off")
    fig.text(.735,.837,"03   PRINT ON ITS SIDE",fontsize=11,fontweight="bold")
    fig.text(.735,.705,"Lay the broad profile flat.\nBuild through the 4 mm width.",fontsize=11,linespacing=1.5)
    fig.text(.735,.422,"Hook and neck stay in one layer plane.\nNo support under the rear tail.",fontsize=10,color=MUTED,linespacing=1.6)
    fig.add_artist(plt.Line2D([.045,.955],[.343,.343],transform=fig.transFigure,color=GRID,lw=1))
    fig.text(.045,.305,"COMPUTED INSERTION PATH",fontsize=11,fontweight="bold")
    # The selected drawings are positions taken from the numerical path.
    labels=["Approach", "Feed rear tail", "Lower the mount", "Seated"]
    if len(poses)>=7:
        keyposes=[poses[-3],poses[-4],(poses[1]+poses[2])/2,poses[0]]
    else:
        sampled=evenly_sample_path(poses,101)
        keyposes=[sampled[i] for i in [100,67,33,0]]
    for i,(pose,label) in enumerate(zip(keyposes,labels)):
        axm=fig.add_axes([.06+.22*i,.066,.19,.219])
        board_section(axm,p,bottom=-33,top=8)
        part_section(axm,parts["complete"],pose)
        clean_axes(axm,(-13,30),(-35,13))
        axm.text(.5,1.015,label,transform=axm.transAxes,ha="center",fontsize=10)
        axm.text(.5,-.045,f"{pose[2]:.1f}° tilt",transform=axm.transAxes,ha="center",fontsize=9,color=MUTED)
    hc=math.sqrt(p['hole_diameter']**2-p['width']**2)
    fig.text(.045,.021,
             f"Side views cut at the part edge: Ø{p['hole_diameter']:.2f} mm circular bores leave a {hc:.2f} mm vertical chord.  "
             "The motion checker uses that limiting opening.",fontsize=9,color=MUTED)
    fig.savefig(out/"anchor-summary.png",dpi=160,bbox_inches=None)
    plt.close(fig)


def save_drawing(p,parts,z0,out):
    fig=plt.figure(figsize=(11.7,8.3),facecolor=BG)
    fig.text(.065,.925,"PEGBOARD ANCHOR  /  DIMENSIONED PROFILE",fontsize=18,fontweight="bold")
    fig.text(.065,.885,"Dimensions in millimetres.  Geometry is generated by the parametric model.",fontsize=10,color=MUTED)
    ax=fig.add_axes([.07,.14,.52,.70]);poly=parts["complete"]
    board_section(ax,p,bottom=-36,top=12)
    part_section(ax,poly)
    clean_axes(ax,(-21,18),(-39,15))
    t=p["board_thickness"]
    dimension(ax,(-14,0),(-14,-p["pitch"]),f"{p['pitch']:.2f}",(-1.8,0),90)
    dimension(ax,(-t,10),(0,10),f"t = {t:.2f}",(0,1.8))
    b=poly.bounds
    dimension(ax,(b[0],-35),(b[2],-35),f"{b[2]-b[0]:.2f} total depth",(0,-1.7))
    dimension(ax,(12,b[1]),(12,b[3]),f"{b[3]-b[1]:.2f} overall",(1.8,0),90)
    iso=fig.add_axes([.58,.35,.34,.43],projection="3d");isometric(iso,p,poly)
    rows=[("Hole diameter",f"{p['hole_diameter']:.2f}"),
          ("Hole pitch",f"{p['pitch']:.2f}"),
          ("Board thickness",f"{t:.2f}  [adjustable]"),
          ("Extruded width",f"{p['width']:.2f}"),
          ("Hook section height",f"{p['neck_height']:.2f}"),
          (("Pull clearance target" if "pull_clearance" in p else "Rear clearance"),
           f"{p.get('pull_clearance',p.get('rear_clearance',0)):.2f}"),
          ("Locator penetration",f"{p['locator_depth']:.2f}")]
    for i,(name,val) in enumerate(rows):
        fig.text(.62,.31-i*.026,name,fontsize=10,color=MUTED)
        fig.text(.92,.31-i*.026,val,fontsize=10,ha="right")
    fig.text(.065,.055,"REFERENCE DRAWING  •  Print the CAD/STL at 100% scale; do not scale this sheet.",fontsize=9,color=MUTED)
    fig.savefig(out/"anchor-drawing.svg")
    fig.savefig(out/"anchor-drawing.png",dpi=170)
    plt.close(fig)


def save_bore_section(p,z0,poses,out):
    fig=plt.figure(figsize=(10,6),facecolor=BG)
    fig.text(.055,.93,"WHY THE HOLE DIAMETER IS NOT THE PASSAGE HEIGHT",fontsize=16,fontweight="bold")
    fig.text(.055,.874,"The anchor has finite width. Its outside edges govern clearance through a round bore.",fontsize=10.5,color=MUTED)
    ax=fig.add_axes([.055,.14,.46,.68]);ax.set_facecolor(BG)
    r=p['hole_diameter']/2;w=p['width'];hh=math.sqrt(r*r-(w/2)**2)
    ax.add_patch(Rectangle((-4.5,-4.5),9,9,facecolor=BOARD,edgecolor="none"))
    ax.add_patch(Circle((0,0),r,facecolor=BG,edgecolor=BOARD_DARK,lw=1.4))
    ax.plot([-r-.4,r+.4],[0,0],color=MUTED,lw=.65,linestyle=(0,(5,5)))
    ax.plot([0,0],[-r-.4,r+.4],color=MUTED,lw=.65,linestyle=(0,(5,5)))
    for x in [-w/2,w/2]:
        ax.plot([x,x],[-hh,hh],color=ORANGE,lw=2)
    necklo=z0+poses[0,1]-p['neck_height']/2
    ax.add_patch(Rectangle((-w/2,necklo),w,p['neck_height'],facecolor=TEAL,edgecolor=TEAL_DARK,lw=1.4))
    dimension(ax,(-w/2,-3.65),(w/2,-3.65),f"{w:.2f} mm width",(0,-.38))
    ax.set_xlim(-4.7,4.7);ax.set_ylim(-4.6,4.5);ax.set_aspect('equal');ax.axis('off')
    fig.text(.575,.72,f"{p['hole_diameter']:.2f} mm",fontsize=29,fontweight='bold')
    fig.text(.575,.663,"Full hole diameter",fontsize=12,color=MUTED)
    fig.text(.575,.53,f"{2*hh:.2f} mm",fontsize=29,fontweight='bold',color=ORANGE)
    fig.text(.575,.473,"Available height at the part edge",fontsize=12,color=MUTED)
    fig.text(.575,.345,f"{p['neck_height']:.2f} mm",fontsize=29,fontweight='bold',color=TEAL)
    fig.text(.575,.288,"Printed neck height",fontsize=12,color=MUTED)
    fig.text(.055,.061,"Front bore section at the neck. Orange lines mark the limiting chords; the teal section shows the seated neck.",fontsize=9.5,color=MUTED)
    fig.savefig(out/'bore-clearance.png',dpi=170)
    plt.close(fig)


def save_animation(data,p,parts,poses,out):
    sample=evenly_sample_path(poses,95)
    # Animation includes exact checked path vertices as well as resampling.
    frames=[]
    fig=plt.figure(figsize=(10.4,7.2),facecolor=BG)
    fig.text(.055,.929,"INSERT  ·  SEAT  ·  REMOVE",fontsize=22,fontweight="bold")
    fig.text(.055,.882,"Rigid-body path from the geometric motion study",fontsize=11,color=MUTED)
    ax=fig.add_axes([.085,.17,.58,.67])
    board_section(ax,p,bottom=-36,top=12,labels=True)
    part=part_section(ax,parts["complete"],sample[-1])
    max_y=max(transformed_profile(parts['complete'],pose)[:,0].max() for pose in sample)
    clean_axes(ax,(-13,max_y+3),(-37,15),axis=True)
    phase=fig.text(.72,.76,"INSERT",fontsize=20,fontweight="bold",color=TEAL)
    stats=fig.text(.72,.70,"",fontsize=12,linespacing=1.7,va="top")
    guide=fig.text(.72,.48,"",fontsize=11,linespacing=1.55,color=MUTED,va="top")
    fig.text(.72,.32,f"Board  {p['board_thickness']:.2f} mm\nHoles  Ø{p['hole_diameter']:.2f} mm\nPitch  {p['pitch']:.2f} mm",fontsize=10,linespacing=1.8,color=MUTED,va="top")
    hc=math.sqrt(p['hole_diameter']**2-p['width']**2)
    fig.text(.055,.060,f"Edge cutaway at x = ±{p['width']/2:.2f} mm  ·  limiting bore chord = {hc:.2f} mm",fontsize=10,color=MUTED)
    fig.text(.055,.025,"Free threading reserves 0.10 mm at each bore edge; seating ends at physical contact. Removal reverses the verified path.",fontsize=9,color=MUTED)
    seq=[("INSERT",pose) for pose in sample[::-1]]
    seq += [("SEATED",sample[0])]*27
    seq += [("REMOVE",pose) for pose in sample]
    seq += [("REMOVED",sample[-1])]*16
    for name,pose in seq:
        part.set_xy(transformed_profile(parts['complete'],pose))
        phase.set_text(name)
        stats.set_text(f"Tilt  {pose[2]:.1f}°\nOut  {pose[0]-poses[0,0]:.2f} mm\nUp  {pose[1]-poses[0,1]:.2f} mm")
        if name=="SEATED":
            guide.set_text("Rear tail retained.\nLower locator engaged.")
        elif name=="REMOVED":
            guide.set_text("Anchor clears\nthe board completely.")
        elif pose[0]>14:
            guide.set_text("Approach / clear\nthe board and set\nthe insertion angle.")
        elif pose[0]>6:
            guide.set_text("Feed / withdraw\nthe rear tail.")
        elif pose[2]<2:
            guide.set_text("Seat / release\nthe lower locator.")
        else:
            guide.set_text("Tilt and lift\nas the tail passes\nthrough the upper hole.")
        fig.canvas.draw()
        img=Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[:,:,:3]).convert("P",palette=Image.Palette.ADAPTIVE,colors=128)
        frames.append(img)
    frames[0].save(out/"insertion-removal.gif",save_all=True,append_images=frames[1:],
                   duration=55,loop=0,optimize=True,disposal=2)
    # Still strips remain useful when a viewer does not animate GIFs.
    plt.close(fig)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--study",default=str(ROOT/"motion_results.json"))
    ap.add_argument("--out",default=str(ROOT/"visuals"))
    ap.add_argument("--no-animation",action="store_true")
    args=ap.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    data,p,parts,z0,poses=load_study(args.study)
    save_summary(p,parts,z0,poses,out)
    save_drawing(p,parts,z0,out)
    save_bore_section(p,z0,poses,out)
    if not args.no_animation:
        save_animation(data,p,parts,poses,out)
    print(json.dumps({"generated":[str(x) for x in sorted(out.iterdir())]},indent=2))


if __name__=="__main__":
    main()
