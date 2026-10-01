"""PF02 visuals: centre-plane cut of each coupon seated in the board, and the print plate."""
from pathlib import Path
import json, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
import FreeCAD, Mesh, Part
from render_fit_ladder import triangles, shaded, BG, INK, TEAL

OUT = Path(__file__).resolve().parents[2]/'docs/gallery/fit-ladder-v2'
STEM = 'part-pf02-peg-fit-grid__v1'
BOARD, HOLE_R, PITCH = 3.94, 6.35/2, 25.4
SEAT = (-0.15, -0.12)


def board(ax):
    """Board section at X=0: solid between holes, 3/4 in shim gap behind."""
    wood = '#8d7858'
    spans = [(-60, -PITCH-HOLE_R), (-PITCH+HOLE_R, -HOLE_R), (HOLE_R, 30)]
    for z0, z1 in spans:
        ax.add_patch(Rectangle((-BOARD, z0), BOARD, z1-z0, color=wood, zorder=1))
    ax.axvline(-BOARD-19.05, color='#556', lw=1, ls='--')
    ax.text(-BOARD-18.6, -46, 'wall (3/4 in shims)', color='#aab', fontsize=8, rotation=90)


def cut(ax, path):
    """Exact CAD section at X=0 (the peg centre plane), seated."""
    shape = Part.read(str(path)); shape.translate(FreeCAD.Vector(0, *SEAT))
    for wire in shape.slice(FreeCAD.Vector(1, 0, 0), 0.0):
        pts = np.array([[p.y, p.z] for p in wire.discretize(Deflection=.01)])
        ax.add_patch(Polygon(pts, closed=True, fc=TEAL, ec='#dff', lw=.4, zorder=2))


if __name__ == '__main__':
    fit = sys.argv[1] if len(sys.argv) > 1 else 'e586ab4ff6'
    cat = json.loads((OUT/f'{STEM}__catalog.json').read_text())
    fig, axes = plt.subplots(2, 5, figsize=(16, 9), dpi=120, facecolor=BG)
    for ax, c in zip(axes.flat, cat['coupons']):
        ax.set_facecolor(BG); board(ax)
        cut(ax, OUT/f"{STEM}__coupon-{c['coupon']}__installed__fit-{fit}.step")
        ax.set_xlim(-16, 7); ax.set_ylim(-36, 8); ax.set_aspect('equal'); ax.axis('off')
        ax.set_title(f"{c['coupon']}  {c['label']}\nside +{c['upper_ribs_mm']:.2f}  clamp {c['clamp_mm']:.2f}",
                     color=INK, fontsize=10)
    fig.suptitle('Seated, cut through the peg centre plane (board brown, user on the right)', color=INK)
    fig.tight_layout(); fig.savefig(OUT/f'{STEM}__seated-sections.png', facecolor=BG)
    plate = triangles(OUT/f'{STEM}__all-10__print-flat-top__fit-{fit}.stl')
    fig = plt.figure(figsize=(10, 7), dpi=130, facecolor=BG); ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(BG)
    shaded(ax, plate, (-.7, -1, .9)); fig.savefig(OUT/f'{STEM}__print-plate.png', facecolor=BG)
    t = triangles(OUT/f"{STEM}__coupon-9__installed__fit-{fit}.stl")
    fig = plt.figure(figsize=(6, 6), dpi=130, facecolor=BG); ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(BG)
    shaded(ax, t, (.9, -1, .45)); fig.savefig(OUT/f'{STEM}__coupon-9-detail.png', facecolor=BG)
