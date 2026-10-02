"""PF07: HOOP tune for PolyLite ASA.

PF06 (2026-10-02, cyan ASA): the LATCH arms and hooks snapped; the shared top
(upper ribs 0.5 + tongue clamp 0.49) held. ASA cracks at a far smaller strain
than PETG, and a latch puts its whole deflection into one short arm. A HOOP is
held at both ends, so the same squeeze spreads along the loop. In PETG, PF04
HOOP 0.9 "printed really well but a little too firm to insert" and 1.2 was "way
too tight"; PF06 eased the hoop's lead-in with a wider nose (tip 2.0 / 2.3).
Bending strain at a given deflection scales with arm thickness, so for ASA go
thinner: arms 0.6 / 0.7 / 0.8 mm, each with both eased lead-ins. Review (2026-10-02)
found the old void left a 0.574 t notch at the catch; PF07 offsets the catch face by t
(even_catch_wall), which stiffens the root, hence the thinner arms. Hook, catch
and contact are PF06's; the top is unchanged.
Run with FreeCAD's Python.
"""
from pathlib import Path
import argparse
import peg_fit_ladder_v4 as C

OUT = C.ROOT.parent/'docs/gallery/fit-ladder-v7'


def coupons():
    out = []
    for arm in (0.6, 0.7, 0.8):
        for tip in (2.0, 2.3):
            out.append({'coupon': len(out)+1, 'concept': 'HOOP', 'arm_mm': arm, 'tip_half': tip, 'even_catch_wall': True,
                        'label': f'H{arm:.1f} T{tip:.1f}'.replace('H0.', 'H.')})   # H = hoop arm; long labels cut the arm
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUT)
    C.main(parser.parse_args().output, coupons(), 'part-pf07-peg-hoop-tune', 'PF07 hoop tune (ASA)')
