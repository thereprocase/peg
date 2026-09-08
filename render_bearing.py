"""Exact transverse bearing geometry; contact stress is not simulated.

Run from the repository root, using the selected revision diameter:
  python render_bearing.py --diameter 5.6
"""
from pathlib import Path
import argparse
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle


def render(diameter, hole, output):
    if not 0 < diameter < hole:
        raise ValueError('Peg diameter must be positive and smaller than the hole')
    bg, board, ink, dim = '#0d1b25', '#243e4a', '#edf3f0', '#95adb5'
    orange, teal = '#ed985d', '#31bec1'
    R, r = hole / 2, diameter / 2
    width, height = 4.0, 3.6
    old_bottom = -math.sqrt(R * R - (width / 2) ** 2)
    old_center = old_bottom + height / 2
    new_center = -(R - r)
    fig, axes = plt.subplots(1, 2, figsize=(13, 8), facecolor=bg)
    fig.subplots_adjust(left=.07, right=.93, top=.78, bottom=.20, wspace=.28)
    fig.text(.07, .925, 'A round hole deserves a round bearing.', color=ink,
             fontsize=25, weight='bold')
    fig.text(.07, .872, 'Exact cross-sections at downward seating contact',
             color=dim, fontsize=14)
    for ax in axes:
        ax.set_facecolor(bg)
        ax.add_patch(Rectangle((-4.1, -4.1), 8.2, 8.2, facecolor=board))
        ax.add_patch(Circle((0, 0), R, facecolor=bg, edgecolor=dim, linewidth=1.5))
        ax.axhline(0, color=dim, alpha=.22, linewidth=.7, linestyle='--')
        ax.axvline(0, color=dim, alpha=.22, linewidth=.7, linestyle='--')
        ax.set(xlim=(-4.1, 4.1), ylim=(-4.1, 4.1), aspect='equal')
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values(): spine.set_visible(False)
    axes[0].add_patch(Rectangle((-width/2, old_bottom), width, height,
                               facecolor=orange, edgecolor=ink, linewidth=1.2))
    axes[0].scatter([-width/2, width/2], [old_bottom]*2, s=70,
                    facecolor=ink, edgecolor=orange, linewidth=2, zorder=5)
    axes[1].add_patch(Circle((0, new_center), r, facecolor=teal,
                            edgecolor=ink, linewidth=1.2))
    axes[1].scatter([0], [-R], s=70, facecolor=ink, edgecolor=teal,
                    linewidth=2, zorder=5)
    axes[0].set_title('RECTANGULAR BASELINE', color=orange, fontsize=15, pad=17,
                      weight='bold')
    axes[1].set_title('ROUND BEARING REVISION', color=teal, fontsize=15, pad=17,
                      weight='bold')
    for ax, center in zip(axes, [old_center, new_center]):
        ax.annotate('', xy=(0, center-.65), xytext=(0, center+.65),
                    arrowprops={'arrowstyle':'-|>', 'color':bg, 'lw':2.5})
    axes[0].text(.5, -.07, '4.0 × 3.6 mm · two sharp corner contacts',
                 transform=axes[0].transAxes, color=ink, fontsize=12, ha='center')
    axes[1].text(.5, -.07, f'Ø{diameter:.2f} mm · smooth lower bearing crown',
                 transform=axes[1].transAxes, color=ink, fontsize=12, ha='center')
    fig.text(.07, .09, f'Bore Ø{hole:.2f} mm   /   Round peg diametral clearance '
             f'{hole-diameter:.2f} mm', color=ink, fontsize=13)
    fig.text(.07, .048, 'Ideal rigid contact locations only. Actual contact width '
             'and pressure depend on deformation, material, and load.',
             color=dim, fontsize=10.5)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180, facecolor=bg)
    fig.savefig(output.with_suffix('.svg'), facecolor=bg)
    plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--diameter', type=float, default=5.6)
    parser.add_argument('--hole', type=float, default=6.35)
    parser.add_argument('--output', type=Path, default=Path(__file__).parent /
                        'visuals' / 'bearing-comparison.png')
    args = parser.parse_args()
    render(args.diameter, args.hole, args.output)
