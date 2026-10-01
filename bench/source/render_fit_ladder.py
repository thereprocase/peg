"""PF01 fit ladder visuals: locator sections in the hole, and shaded STL views."""
from pathlib import Path
import json, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Circle, Polygon
import FreeCAD, Mesh

OUT = Path(__file__).resolve().parents[2]/'docs/gallery/fit-ladder'
STEM = 'part-pf01-peg-fit-ladder__v1'
BG, INK, TEAL, HOLE, HOT = '#252e34', '#f3efe7', '#6fc1ad', '#d9c8a7', '#f0795b'


def unit(v):
    v = np.asarray(v, float); return v/np.linalg.norm(v)


def triangles(path):
    m = Mesh.Mesh(str(path))
    return np.array([[list(p) for p in f.Points] for f in m.Facets])


def shaded(ax, tris, cam, up=(0, 0, 1), colour=TEAL):
    """Orthographic painter's render; cam points from the model toward the viewer."""
    cam = unit(cam); right = unit(np.cross(up, cam)); upv = np.cross(cam, right)
    n = np.cross(tris[:, 1]-tris[:, 0], tris[:, 2]-tris[:, 0])
    n /= np.linalg.norm(n, axis=1)[:, None]+1e-12
    front = n@cam > 0
    tris, n = tris[front], n[front]
    depth = (tris@cam).mean(1)
    order = np.argsort(depth)
    light = unit(cam+.6*upv+.35*right)
    base = np.array(matplotlib.colors.to_rgb(colour))
    shade = .28+.72*np.clip(n@light, 0, 1)
    xy = np.stack([tris@right, tris@upv], -1)[order]
    ax.add_collection(PolyCollection(xy, facecolors=base[None]*shade[order, None], edgecolors='none', antialiased=False))
    ax.set_xlim(xy[..., 0].min()-2, xy[..., 0].max()+2); ax.set_ylim(xy[..., 1].min()-2, xy[..., 1].max()+2)
    ax.set_aspect('equal'); ax.axis('off')


def figure(w, h):
    fig = plt.figure(figsize=(w, h), dpi=130, facecolor=BG)
    return fig


def sections(catalog):
    fig, axes = plt.subplots(2, 5, figsize=(15, 6.6), dpi=130, facecolor=BG)
    R = catalog['coupons'][0]['hole_diameter_mm']/2
    for ax, c in zip(axes.flat, catalog['coupons']):
        ax.set_facecolor(BG)
        ax.add_patch(Circle((0, 0), R+2.2, color='#8d7858', zorder=0))
        ax.add_patch(Circle((0, 0), R, color=BG, zorder=1))
        pts = np.array(c['locator_section_xz_about_hole_centre_at_y_minus_1p85'])
        ax.add_patch(Polygon(pts, closed=True, color=TEAL, zorder=2))
        ax.add_patch(Circle((0, 0), R, fill=False, ec=HOLE, lw=1.3, zorder=3))
        v = c['diametral_interference_mm']
        if v:
            for s in (1, -1):
                ax.plot([s*R, s*(R+v/2)], [0, 0], color=HOT, lw=3, solid_capstyle='butt', zorder=4)
        width = c['locator_width_at_hole_centre_mm']
        note = 'no ribs, 0.40 gap each side' if v is None else f'ribs {width:.2f} across'
        ax.set_title(f"{c['rung']}   {c['label']}\n{note}", color=INK, fontsize=11)
        ax.set_xlim(-5.8, 5.8); ax.set_ylim(-5.8, 5.8); ax.set_aspect('equal'); ax.axis('off')
    fig.suptitle('Lower locator section inside a 6.35 mm hole (board shown brown, red = squeeze into the hole wall)',
                 color=INK, fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT/f'{STEM}__sections.png', facecolor=BG)


if __name__ == '__main__':
    fit = sys.argv[1] if len(sys.argv) > 1 else 'e586ab4ff6'
    catalog = json.loads((OUT/f'{STEM}__catalog.json').read_text())
    sections(catalog)
    lineup = triangles(OUT/f'{STEM}__all-10__installed__fit-{fit}.stl')
    fig = figure(16, 4.6); ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(BG)
    shaded(ax, lineup, (-.25, 1, .25)); fig.savefig(OUT/f'{STEM}__lineup.png', facecolor=BG)
    fig = figure(16, 5.2); ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(BG)
    shaded(ax, lineup, (.45, -1, .35)); fig.savefig(OUT/f'{STEM}__lineup-rear.png', facecolor=BG)
    plate = triangles(OUT/f'{STEM}__all-10__print-flat-top__fit-{fit}.stl')
    fig = figure(10, 7); ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(BG)
    shaded(ax, plate, (-.7, -1, .9)); fig.savefig(OUT/f'{STEM}__print-plate.png', facecolor=BG)
    for rung in (0, 9):
        t = triangles(OUT/f'{STEM}__rung-{rung}__installed__fit-{fit}.stl')
        fig = figure(6, 6); ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(BG)
        shaded(ax, t, (.9, -1, .45)); fig.savefig(OUT/f'{STEM}__rung-{rung}-detail.png', facecolor=BG)
