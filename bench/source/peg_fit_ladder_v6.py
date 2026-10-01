"""PF06: tune PF04 #12 (LATCH, 1.2 mm hook) on the way out.

PF04 reprint feedback (2026-10-01): #12 "awesome but almost broke on the way
out"; #11 (0.9) goes in easy and grabs; #10 loose. User: keep the interference,
add a hair to the return ramp without moving the contact point. So the 1.2 mm
hook stays; its return face pivots about the point where #12's 60 deg face
crosses the hole wall and gets gentler: 60/55/50/45 deg from the peg axis.
These use PF05's meatier arm (gap hook+0.3, ~3.5 mm head, thicker root) but
PF04 #12's 0.3 mm crest, so the push-in ramp stays near #12's 23 deg.
References: #1 is PF04 #12 exactly; #6 is #11's hook with the meaty arm.
Run with FreeCAD's Python.
"""
from pathlib import Path
import argparse
import peg_fit_ladder_v4 as C

OUT = C.ROOT.parent/'docs/gallery/fit-ladder-v6'


def coupons():
    out = [{'coupon': 1, 'concept': 'LATCH', 'hook_mm': 1.2, 'label': 'PF04-12'}]
    for a in (60, 55, 50, 45):
        out.append({'coupon': len(out)+1, 'concept': 'LATCH2', 'hook_mm': 1.2, 'catch_deg': a,
                    'contact_ref_deg': 60, 'crest_mm': 0.3, 'label': f'H1.2 R{a}'})
    out.append({'coupon': 6, 'concept': 'LATCH2', 'hook_mm': 0.9, 'catch_deg': 60,
                'contact_ref_deg': 60, 'crest_mm': 0.3, 'label': 'H.9 R60'})
    # PF04 #8 (HOOP, 1.2 mm arms) was way too tight going in; user: "an 8 with a
    # few degrees more ramp might be perfect". Widen the nose to ease the lead-in
    # ramp from ~19 deg to ~16 and ~13 deg; hook, catch and contact unchanged.
    for tip in (2.0, 2.3):
        out.append({'coupon': len(out)+1, 'concept': 'HOOP', 'arm_mm': 1.2, 'tip_half': tip,
                    'label': f'HOOP T{tip:.1f}'})
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUT)
    C.main(parser.parse_args().output, coupons(), 'part-pf06-peg-latch-tune', 'PF06 latch tune')
