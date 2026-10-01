"""PF04/PF05 visuals (argv: pf04|pf05 [fit]): plan cut through each lower peg at hole-centre height, seated."""
from pathlib import Path
import json, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
import FreeCAD, Part
from render_fit_ladder import triangles, shaded, BG, INK, TEAL

SETS = {'pf04': ('fit-ladder-v4', 'part-pf04-peg-retention-concepts__v1', (3, 5)),
        'pf05': ('fit-ladder-v5', 'part-pf05-peg-latch-grid__v1', (3, 3))}
which = sys.argv[1] if len(sys.argv) > 1 else 'pf04'
folder, STEM, grid = SETS[which]
OUT = Path(__file__).resolve().parents[2]/'docs/gallery'/folder
BOARD, R = 3.94, 6.35/2
fit = sys.argv[2] if len(sys.argv) > 2 else 'e586ab4ff6'
cat = json.loads((OUT/f'{STEM}__catalog.json').read_text())
fig, axes = plt.subplots(*grid, figsize=(3.2*grid[1], 4.6*grid[0]), dpi=110, facecolor=BG)
for ax, c in zip((axes.T if which == 'pf04' else axes).flat, cat['coupons']):
    ax.set_facecolor(BG)
    for x0, x1 in ((-9, -R), (R, 9)):
        ax.add_patch(Rectangle((x0, -BOARD), x1-x0, BOARD, color='#8d7858', zorder=1))
    shape = Part.read(str(OUT/f"{STEM}__coupon-{c['coupon']}__installed__fit-{fit}.step"))
    shape.translate(FreeCAD.Vector(0, -0.15, -0.12))
    wires = shape.slice(FreeCAD.Vector(0, 0, 1), -25.4)
    faces = Part.Face(wires, 'Part::FaceMakerBullseye')   # nests holes inside outers
    for face in faces.Faces:
        for k, wire in enumerate(face.Wires):             # outer wire first, then holes
            pts = np.array([[p.x, p.y] for p in wire.discretize(Deflection=.005)])
            ax.add_patch(Polygon(pts, closed=True, fc=TEAL if wire.isSame(face.OuterWire) else BG,
                                 ec='#dff', lw=.4, zorder=3 if not wire.isSame(face.OuterWire) else 2))
    ax.set_xlim(-6, 6); ax.set_ylim(-12.5, 2.5); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(f"{c['coupon']}  {c['label']}", color=INK, fontsize=11)
fig.suptitle('Seated plan cut at the lower hole centre: board brown, holder front at top, wall below', color=INK)
fig.tight_layout(); fig.savefig(OUT/f'{STEM}__plan-sections.png', facecolor=BG)
