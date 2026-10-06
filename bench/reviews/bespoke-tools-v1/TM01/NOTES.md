# TM01 — Tape-measure dock

A shallow open dock for a tape measure up to 92 mm across and 48 mm deep including its clip. Lift 10 mm and pull forward.

## Print and use

Bed face: **upright**. Chosen before massing. The body grows from a continuous
planar footprint; the lower hoops flex in the layers. Existing PF02 #9 upper hooks and
PF07 #5 clipped-root lower hoops are retained exactly behind the rear contact plane.

The case rests on the broad floor behind a low lip, between stiff side walls. Coverage is a conservative 92 mm width / 48 mm depth including the belt clip. Tool dimensions in some product listings describe packaging, so exact brand fit remains unqualified. Test the tape body, clip and lock clearance during pickup.

Print envelope: 99.6 × 70.79 × 62.45 mm.
Planar bed contact: 5961.1 mm². Solid CAD volume: 59.00 cm³.
This is a new collection category; comparison is against the recorded functional and
print targets. Broad floors and continuous webs favor reliable printing and stiffness.

## Matching checks

- One valid native solid; installed and print STEP read-backs pass the build assertions.
- Watertight positive-volume mesh; one connected component.
- Board-side symmetric difference from the shared receiver: 0 mm³.
- Flagged non-peg overhang area: 0 mm²; starting body islands: 0.
- Nominal rigid pickup routes pass. The complete front body passes its own sampled
  installation-plane screen; that screen uses the preserved nominal reference route.
- Fixed-peg solid-ASA calculation at 5 N: **0.0034 mm sideways**, **0.0603 mm down**.
  Targets: 1.0 / 0.5 mm. Material is isotropic E=1800 MPa, Poisson ratio 0.35.
- Local Orca 2.4.2 slice with the owner's P1S / PolyLite ASA profiles: **1h 53m 16s**,
  approximately **36.39 g** of classified extrusion, including **2.057 g**
  of support/interface. The filament profile supplies density 1.02 g/cm³.

Settings: 0.4 mm nozzle, 0.2 mm layers, two Arachne walls, 20% infill, organic supports
from the bed and 5 mm outer brim. ASA shrink compensation is baked once at
100/99.46; the slicer's shrink setting is then 100%. Support and overhang-wall moves
stay behind the mounting face. TM01's pointed-window apex contributes about 0.001 g
of air bridge; CL01's small bridge extrusion is at the pegs. Internal bridges cover infill.
The matching `toolpaths.svg` shows actual extrusion projections.

Installed, loaded and print orientations were reviewed in the browser. Body surfaces
are exposed for printing; rear support trees are accessible from outside the holder.
The keys use open guide pairs; the tape dock keeps its upper grip open; the coil saddle
prints as a constant section across its width.

## Remaining physical checks

Check first-layer adhesion, peg support removal, board fit and hoop action before loading.
Check one-handed return, neighboring tools, accidental bumps and actual tool retention.
Printed infill and layer adhesion differ from the solid linear model; stiffness results
are separate from a load or fatigue rating. No physical print/use qualification is recorded.
Machine-specific slice files stay local and have not been sent to a printer.

## Reproduction and files

The generator is `bench/source/bespoke_tools_v1/build.py`. The reviewed rules are in
`PRINT-DESIGN-RULES.md` beside it. `report.json` records exact native/mesh hashes and
nominal tool paths; `print-geometry.json`, `stiffness.json`, `installation-screen.json`,
`slice-summary.json` and `toolpaths.json` record independent checks and their inputs.
Native STEP / FreeCAD exports and source are packaged as a local CAD review bundle.
