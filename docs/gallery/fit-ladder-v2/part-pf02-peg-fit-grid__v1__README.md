# PF02 v1 — upper fit grid on a longer lower peg

Follows PF01 feedback: lower rungs 6 (+0.50) and 8 (+0.80) held well; the board stands on
3/4 in shims; the top rocked away from the board, wiggled sideways and lifted.

Every coupon except 0 has:
- lower crush ribs at +0.65 (between the two good PF01 rungs);
- a 4.8 mm tail running 7 mm past the board's rear face. A sampled sweep of the baseline
  removal path cleared it with zero overlap up to 8 mm; 9 mm touched.

The top varies on a 3 x 3 grid. **S** = diametral interference of two side ribs on the upper
neck (wiggle). **C** = tongue clamp interference on a 3.94 mm board (rocking away).

| Coupon | Label | Upper side ribs | Clamp | Tail |
|---|---|---|---|---|
| 0 | PF01-7 | none (5.55 wide) | 0.19 (current) | no |
| 1 | S.00C.19 | none | 0.19 | yes |
| 2 | S.00C.34 | none | 0.34 | yes |
| 3 | S.00C.49 | none | 0.49 | yes |
| 4 | S.25C.19 | 6.60 across | 0.19 | yes |
| 5 | S.25C.34 | 6.60 | 0.34 | yes |
| 6 | S.25C.49 | 6.60 | 0.49 | yes |
| 7 | S.50C.19 | 6.85 across | 0.19 | yes |
| 8 | S.50C.34 | 6.85 | 0.34 | yes |
| 9 | S.50C.49 | 6.85 | 0.49 | yes |

Lift is not a separate knob: the hook needs about 1 mm of lift to go in, so it can't be
designed out without blocking insertion. Side ribs resist it with friction instead.

Report per coupon: insertion effort, rock, side wiggle, lift, removal effort, hole damage.

Scope: CAD geometry only; clamp and ribs deliberately exceed the nominal board and bore.
Source: `bench/source/peg_fit_ladder_v2.py` (per-clamp fit files in `bench/reviews/pf02-fits/`);
visuals: `bench/source/render_fit_ladder_v2.py`; slicing: `print/slice_pf.py pf02`.
