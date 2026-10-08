# HX04 v1 — three-tier key fan (Torx L, hex L, T-handles)

A ten-cell-wide pegboard rack for three tool sets, built from the `bench/source/key_fan_v1` study and CAD:

- **Back row:** metric hex L-keys, 1.5–10 mm. Their seats get deeper toward the long keys (hex 10 sits 61 mm deep), so the tall keys sit lower. Sizes are debossed on top.
- **Middle row:** Husky Torx L-keys, T10–T50. Sizes are on the front lip.
- **Front fan:** Bondhus T-handles, 2–10 mm. Grips are spaced evenly, about 39 mm centre to centre. T2 and T2.5 sit in deep seats so their grips are 46 and 38 mm below the hex keys' short arms. Sizes are on the front lip.

The plate is 236 mm wide (shaved 8 mm a side from ten cells) and hangs on the PF02 #9 / PF07 #5 receiver on the nine-cell peg pattern. Its columns are at ±101.6 mm. The part prints on the user's left end.

## How the sockets hold the tools

- **Depth.** Every seat is at least 4× the key size and never under 12 mm. Deeper seats are used where they lower a tall key or a small T-handle.
- **Rotation.** Each L-key's short arm points straight downhill, so a key dropped in at any turn swings to its rest. T-handles have no preferred turn, so T3 and up sit in hex-keyed bores clocked to their grip turn, with 0.2 mm per flat. The layout clears every handle turned through its full play in the same direction. T2 and T2.5 are too small for flats to grip, so you set them by eye.
- **Walking in, not out.** Every bore is a bottle: a straight neck for the top quarter of the depth (at least 4 mm), then a 5° flare of up to 0.6 mm. Every floor slopes 30°, low on the side the tool's own weight tips its tip toward. A tool whose weight pinches it in the bore therefore has its tip slide down the slope, deeper, rather than hanging.
- **Withdrawal.** Each tool is drawn out by first straightening it from its resting lean, then lifting it out of the seat, then leaving forward, up-forward or along its axis.

## Checks (CAD and screens; no physical tests yet)

- **Exact OCC check** (`exact-check.json`). All 26 tools in their resting lean are clear of the holder and of each other. Each one straightens and lifts out clear of the holder, the other tools at rest, and a 3″-deep shelf 2″ above the top stored point. The thinnest floor is 7.4 mm.
- **Stiffness** (`stiffness.json`). Solid ASA, E 1800 MPa, 7 mm second-order tetrahedra, held by its pegs only. The weakest case is a Torx T50 pulled straight out at 30 N: 0.098 mm, 307 N/mm. Printed infill is softer than solid.
- **Print geometry** (`print-geometry.json`). One component, no islands. The largest overhang patches are about 16 mm² at the T10 mouth and the label counters.
- **Slices** (`slice-summary.json`). These are local review slices on a P1S 0.4 nozzle, 0.20 mm layers, owner ASA profile, 2 walls, tree supports on the build plate and a 5 mm outer brim:

  | Slice | Weight | Time | Support |
  |---|---|---|---|
  | Full part, plain 20% | 479 g | 21.3 h | 24 g |
  | Full part with the solid-infill zones | 654 g | 29.4 h | 24 g |
  | Fit coupon, plain 20% | 100 g | 4.7 h | 1 g |

  No G-code is published.

## Printing recommendations

1. **Print the fit coupon first** (`…__coupon_print.stl`, plain 20%). It is cut from the final CAD and prints the same way:
   - The **end slice** carries the left peg column, Torx T10/T15, hex 1.5/2 and T-handles T2 (deep seat), T2.5 (unclocked) and T3 (clocked, the most strongly pinched tool). Hang it on the board, drop the tools in, knock the board, and pull each tool out.
   - **T5 C and T5 F** are the same socket keyed to the shaft's hex corners and to its flats. Whichever one lets the bar sit at the intended turn tells you how your handles are made. The full part assumes corners; if flats wins, rebuild with `HX4S_TBAR=flats`.
   - **TX30** checks a mid-size Torx seat.
2. **Full part:** open `…__hx04_solid-zones.3mf` in Bambu Studio or OrcaSlicer. It carries the body plus a modifier part at 100% infill: a sleeve round every socket and the peg-receiver band. Print it as oriented, on its left end, with your own machine and filament profile. Use tree supports on the build plate only; they land under the peg hooks behind the mounting face. For a lighter rack, print `…__print.stl` at plain 20%.
3. **ASA:** use an enclosure and a 5 mm brim. Keep the part's 253 mm height in mind; it fits a 256 mm bed.
4. **Labels:** paint the 0.8 mm Fillaprint debosses after printing.

## Pending and limits

- Physical print, peg fit, tool fit, seating under knocks and support release are untested.
- The receiver is the proven right-cheek PF02 #9 / PF07 #5 geometry, mirrored for the left-end print. Its fit is assumed equal.
- T-handle bars are assumed to lie along the hex corners. Printed hex-bore clearance (0.2 mm per flat) is unverified.
- Turn clearance is checked with all T-handles turned the same way. Neighbours turned opposite ways may brush grips.
- Tool data come from catalogue lengths and stated assumptions, not measurements.
- 147 of the sharp edges left by the web's tool-clearance cuts could not be softened by the CAD kernel and print sharp. The label debosses are deliberately sharp.
