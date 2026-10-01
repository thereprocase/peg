"""PF03: PF02 coupon 9's top on three lower-rib fits, to pick the final mount.

PF02 feedback (2026-09-30): coupon 9's top (S.50 C.49) was best; its bottom
(+0.65 ribs) was looser than coupon 5's, although the CAD is identical.
Reprinting +0.65 beside +0.80 (PF01 rung 8, liked) and +0.95 separates print
variation from a real need for more lower grip. Run with FreeCAD's Python.
"""
from pathlib import Path
import argparse
import peg_fit_ladder_v2 as G

OUT = G.ROOT.parent/'docs/gallery/fit-ladder-v3'
LOWER = [0.65, 0.80, 0.95]


def coupons():
    return [dict(coupon=i, label=f"L{v:.2f}".replace('0.', '.'), lower_ribs_mm=v,
                 upper_ribs_mm=0.50, clamp_mm=0.49, tail=True) for i, v in enumerate(LOWER)]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUT)
    G.main(parser.parse_args().output, coupons(), 'part-pf03-peg-fit-final', 'PF03 peg fit final')
