# PF01 v1 — peg fit ladder

Ten single-column coupons (20 mm wide, one upper hook plus the lower locator), numbered 0–9.
Rung 0 is the current stock mount. Rungs 1–9 add two crush ribs at 3 and 9 o'clock on the
lower locator, at hole-centre height, running the full board thickness with a 1.5 mm lead-in.

Why the lower locator: the stock locator is 5.55 mm wide in a 6.35 mm hole (0.40 mm gap each
side) and nothing holds it in axially, so the bottom of a holder can swing out and the part
lifts off. Insertion tilts the holder in the up/down plane, so side (X) interference squeezes
the hole walls without fighting the swing-in arc. Upper hook, tongue clamp and print variant
(`inverted-top-flat-v1`) are the current canonical fit, unchanged on every rung.

| Rung | Label | Width across ribs | Squeeze per side |
|---|---|---|---|
| 0 | STOCK | 5.55 (no ribs) | 0.40 gap |
| 1 | 0.00 | 6.35 | 0 |
| 2 | +0.10 | 6.45 | 0.05 |
| 3 | +0.20 | 6.55 | 0.10 |
| 4 | +0.30 | 6.65 | 0.15 |
| 5 | +0.40 | 6.75 | 0.20 |
| 6 | +0.50 | 6.85 | 0.25 |
| 7 | +0.65 | 7.00 | 0.325 |
| 8 | +0.80 | 7.15 | 0.40 |
| 9 | +1.00 | 7.35 | 0.50 |

Print the `print-flat-top` STLs (flat top on the bed, pegs need local supports). Hang each
coupon, then report per rung: insertion effort, whether it stays put when you flick or lift
the bottom edge, removal effort, and whether the hole looks crushed afterwards.

Scope: CAD geometry only. The ribs deliberately exceed the nominal bore, so the baseline
motion certificate does not cover them. Retention force, board wear and repeat-use are unmeasured.
Source: `bench/source/peg_fit_ladder.py`; visuals: `bench/source/render_fit_ladder.py`.
