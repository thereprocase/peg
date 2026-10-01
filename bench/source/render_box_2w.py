"""BX01 visuals: a tiled group on the board, and the single box from behind."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from render_fit_ladder import triangles, shaded, BG

OUT = Path(__file__).resolve().parents[2]/'docs/gallery/box-2w'
STEM = 'part-bx01-box-2w__v1'
fit = 'e586ab4ff6'
t = triangles(OUT/f'{STEM}__installed__fit-{fit}.stl')
group = np.concatenate([t+np.array([dx, 0, dz]) for dx, dz in [(-50.8, 0), (0, 0), (50.8, 0), (-50.8, 50.8), (0, 50.8)]])
board = np.array([[[x0, -4, z0], [x1, -4, z0], [x1, -4, z1]] for x0, x1, z0, z1 in [(-90, 90, -60, 110)]])
board = np.concatenate([board, np.array([[[-90, -4, -60], [90, -4, 110], [-90, -4, 110]]])])
fig = plt.figure(figsize=(10, 8), dpi=130, facecolor=BG); ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(BG)
shaded(ax, group, (.45, 1, .35)); fig.savefig(OUT/f'{STEM}__tiled.png', facecolor=BG)
fig = plt.figure(figsize=(7, 6), dpi=130, facecolor=BG); ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(BG)
shaded(ax, t, (.8, -1, .5)); fig.savefig(OUT/f'{STEM}__rear.png', facecolor=BG)
