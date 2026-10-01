"""PF05: LATCH refined. Hook interference x return (catch) slope, meatier head.

PF04 feedback (2026-09-30): LATCH liked; the tip needs more meat and stiffness
is not a worry; the parameters to tune are the interference and the slope of
the return that brings the hook back out of the wall. PF04's 1.2 mm flex gap
was also too narrow for its 1.2 mm hook to fold inside the hole, so the gap is
now hook + 0.3 mm. Grid: hook 0.6/0.9/1.2 mm x catch 40/55/70 deg from the peg
axis (steeper = harder to pull out). Top = PF02 coupon 9, in-hole ribs +0.30.
Run with FreeCAD's Python.
"""
from pathlib import Path
import argparse
import peg_fit_ladder_v4 as C

OUT = C.ROOT.parent/'docs/gallery/fit-ladder-v5'
HOOKS = [0.6, 0.9, 1.2]
SLOPES = [40, 55, 70]


def coupons():
    return [{'coupon': i*3+j+1, 'concept': 'LATCH2', 'hook_mm': h, 'catch_deg': a,
             'label': f"H{h:.1f} R{a}".replace('0.', '.')}
            for i, h in enumerate(HOOKS) for j, a in enumerate(SLOPES)]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUT)
    C.main(parser.parse_args().output, coupons(), 'part-pf05-peg-latch-grid', 'PF05 latch grid')
