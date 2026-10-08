# HX04 v2 — three-tier key fan (Torx L, hex L, T-handles)

A ten-cell-wide pegboard rack for three tool sets, built from `bench/source/key_fan_v1`:

- **Back row:** metric hex L-keys, 1.5–10 mm. Their seats get deeper toward the long keys (hex 10 sits 61 mm deep), so the tall keys sit lower. Sizes are debossed on top.
- **Middle row:** Husky Torx L-keys, T10–T50. Sizes are on the front lip.
- **Front fan:** Bondhus T-handles, 2–10 mm. Grips are spaced evenly, about 39 mm centre to centre. T2 and T2.5 sit in deep seats so their grips are 46 and 38 mm below the hex keys' short arms.

The plate is 236 mm wide and prints on the user's left end.

## What changed from v1

- **Peg grid (owner: hook pegs every inch, locking pegs on the very bottom, gravity-load pegs in the other spots).** Every hole the plate covers now carries a peg: 90 in all, on 9 columns at 25.4 mm pitch (±101.6 mm) by 10 rows.
  - The top row has 9 PF02 #9 upper hooks.
  - The bottom row has 9 PF07 #5 locking hoops.
  - The 72 holes in between have the lower bearing peg (full board thickness, 120° bearing arcs).

  All three profiles are the reviewed, unchanged ones, mirrored for the left-end print. They root in the reviewed 5.4 mm wall, so the back plate is now 5.4 mm thick throughout. The sharp top lip stays at the board face; its front edge is filleted.
- **Solid helpers are braces, not padding (owner).** The 3MF project's 100% infill zones are now:
  - one row shear web per rail: a 1.6 mm plane through all the socket axes that prints as an internal vertical wall and runs from the mouths through the floors to the plate;
  - a 1.6 mm bulkhead at every socket, tying it to the nearby rail walls;
  - a solid disc through the plate round every peg root.

  Solid infill drops from 244 g in v1 (padded sleeves) to 117 g.

## How the sockets hold the tools

These are unchanged from v1:

- Seats are at least 4× the key size.
- Each L-key's short arm hangs downhill.
- T3 and up sit in hex-keyed bores, 0.2 mm per flat.
- Each bore is a bottle: a short neck, then a 5° flare to a floor sloped 30°, low on the side the tool's own weight tips its tip toward. A tool pinched by its weight slides deeper instead of hanging.
- A tool is drawn out by straightening it, lifting it from its seat, then leaving forward.

## Checks (CAD and screens; no physical tests yet)

- **Exact OCC check** (`exact-check.json`). All 26 tools in their resting lean are clear of the holder and of each other. Each one straightens and lifts out clear of the holder, the other tools and a 3″-deep shelf 2″ above. The thinnest floor is 7.4 mm.
- **Install swing** (`install-swing.json`). The part hangs on its top-row hooks and swings down 25° onto a 3.94 mm board with 6.35 mm holes on the 25.4 mm grid, in 0.5° steps.
  - Seated, every bearing peg is clear and the hoops show their designed snap (3.0 mm³ in all).
  - In the last ~3°, bearing pegs graze the hole edges by up to 0.21 mm³ per peg, most next to the hooks and fading to nothing by row 8. That is hundredths of a millimetre, against a declared limit of 0.25 mm³.
  - The pivot (the top of the top holes at mid-board) is an assumption.
- **Stiffness** (`stiffness.json`). Solid ASA, 7 mm tetrahedra, held by its pegs only. The weakest case is a Torx T50 pulled straight out at 30 N: 0.008 mm, 3740 N/mm. T-handle 10 under 50 N down moves 0.006 mm. v1, with two peg columns, was 307 N/mm at its weakest. Printed infill is softer than solid.
- **Print geometry** (`print-geometry.json`). One component. The largest overhang patches are about 16 mm² at the T10 mouth and the label counters. Declared single-vertex island artefacts sit on the vertical end wall.
- **Slices** (`slice-summary.json`). These are local review slices on a P1S 0.4 nozzle, 0.20 mm layers, owner ASA profile, 2 walls, tree supports on the build plate and a 5 mm brim:

  | Slice | Weight | Time | Support |
  |---|---|---|---|
  | Full part, plain 20% | 554 g | 25.7 h | 85 g |
  | Full part with the brace zones | 636 g | 30.4 h | 88 g |
  | Fit coupon, plain 20% | 113 g | 5.4 h | 2 g |

  Support is mostly under the 90 pegs behind the mounting face. No G-code is published.

## Printing recommendations

1. **Print the fit coupon first** (`…__coupon_print.stl`, plain 20%). It is cut from the final model and prints the same way.
   - **End slice:** the top of the left peg column (hooks and the first bearing rows), with Torx T10/T15, hex 1.5/2 and T-handles T2, T2.5 and T3. Hang it on the board, drop the tools in, knock the board, and pull each tool out.
   - **PEGS:** the rest of that peg column down to the locking hoop (plate and pegs only). Hang it alone to feel the bearing pegs and the hoop snap.
   - **T5 C and T5 F:** the T5 socket keyed to the shaft's corners and to its flats. The one that holds the bar at the right turn tells you how your handles are made. The full part assumes corners; if flats wins, rebuild with `HX4S_TBAR=flats`.
   - **TX30:** a mid-size Torx seat.
2. **Full part:** open `…__hx04_solid-zones.3mf` in Bambu Studio or OrcaSlicer (the body plus the brace zones at 100% infill). Print it as oriented, on its left end, with your own machine and filament profile. Use tree supports on the build plate only. For a lighter rack, print `…__print.stl` at plain 20%.
3. **Install:** hook the top row in, then swing the bottom onto the board until the hoops click.
4. **ASA:** use an enclosure and a 5 mm brim. The print is 253 mm long on the bed (fits a 256 mm bed) and 236 mm tall. Paint the 0.8 mm Fillaprint debosses afterwards.

## Pending and limits

- Physical print, peg fit, tool fit, install swing, seating under knocks and support release are untested.
- The peg profiles are the reviewed right-cheek PF02 #9 / PF07 #5 / lower-bearing geometry, mirrored for the left-end print, now on a 9 × 10 grid. Fit is assumed equal to the reviewed pegs, and the install-swing pivot is modelled, not measured.
- T-handle bars are assumed to lie along the hex corners. Printed hex-bore clearance is unverified.
- Turn clearance is checked with all T-handles turned the same way.
- Tool data are catalogue values, not measurements.
- 147 of the sharp edges left by the web's tool-clearance cuts could not be softened by the CAD kernel. The label debosses are deliberately sharp.
- v1 (two peg columns, padded solid sleeves) stays available as history.
