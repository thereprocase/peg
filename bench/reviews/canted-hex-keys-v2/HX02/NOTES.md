# HX02 v2 · graduated organ-pipe metric hex-key rack

Same contract as v1. Nine blind sockets take the entire straight long arm. The axes lean 30 degrees outward from vertical. The bends and short arms stay above the mouths, and the short arms slope down toward the desk. From the user's left the sizes are 1.5, 2, 2.5, 3, 4, 5, 6, 8 and 10 mm, with owner straight lengths of 89, 98, 110, 123, 140, 157, 176, 194 and 217 mm. The 4 mm length of 140 mm is interpolated. Clearance is 0.35 mm radial, and every socket keeps its 50-degree pointed roof for the cheek print. Short arms and bend radii are illustrative assumptions, as in v1.

## What changed

- **Graduated pipes.** Each socket is its own fluted pipe: the lens between two crest cylinders, front and back, with a 3 mm wall round the bore at the crest. The pipes are 8.4 mm thick for the 1.5 mm key and 18.2 mm for the 10 mm key. Pitch is the full width divided by 9, so the pipes tile the 201.2 mm width. Neighbours meet where their crests cross, giving crisp 100-degree valleys with no steps. Each pipe's flank faces a larger neighbour on its print-down side, so no flank leans more than 40 degrees from vertical in the print.
- **Smooth underside.** A shape-preserving monotone curve replaces the v1 staircase. It passes 3 mm below each bore's shallow-side corner; measured blind floors are 3.47 to 8.38 mm. The depth falls toward the print top, so the whole underside faces up in print. The rack stands 8 mm further from the board than v1, so the curve can keep falling at the 10 mm end without reaching the board. This is the one change to the hanging geometry. The installation screen and stiffness are rechecked below.
- **Finish.**
  - The top surface flows into the mouth band over an 8 mm crease.
  - 100-degree V-reveals continue each valley across the top for 45 mm, with conical ends.
  - The size numerals (8 mm on top, 6.5 mm on each pipe face, 45 mm below the mouth) are cut 0.6 mm deep and obliquely, rising 62 degrees toward the print top, so no stroke has a flat ceiling.
  - Each mouth has the same 1.6 mm droplet countersink.
  - The bed outline (top and mouth edges) has 50-degree chamfers.
  - Both ends carry an inset V border, 6 mm in and 1 mm deep, with walls 40 degrees from vertical.
  - The upper +X opening is closed by a flush plug whose cavity ceiling rises to a point at 50 degrees.
  - The lower +X opening stays open, as in v1: it has a free edge, and a cap there would need an 80 mm bridge.
- **Fillets.** The underside edges, mouth rim and +X end are filleted wherever OpenCascade accepts it: 1.2 mm one edge at a time, and 2.5 mm on the end. 12 underside edges, 8 rim edges and 6 end edges were refused and stay sharp; their locations are listed in report.json under finish.operations.
- **Material.** The top tie is a constant 3.5 mm plate and the lower tie is 4 mm. Native volume is 576.66 cm³, against 813.34 cm³ for v1. The printed mass is set mostly by perimeters over the larger surface, so the local review slice is 333 g, against 345 g for v1.

## Evidence and limits

- **Native checks:** one valid solid, unchanged board-side geometry, measured blind floors, and sampled axial withdrawal with neighbour clearance and closed-floor stops for all nine keys.
- **STEP round trip:** checked by volume, area and bounds (max relative difference 1.9e-6). Self-booleans of coincident solids are unreliable in OpenCascade, so they are not used for this check.
- **Mesh checks:** watertight single body, zero flagged body faces, and bed contact of 15832.9 mm². 23 starting points are declared, all inside the numerals: the counters of 0, 4, 6 and 8 start as sub-millimetre islands.
- **Installation:** screening along the preserved nominal route passes.
- **Stiffness screen:** fixed peg nodes, isotropic solid ASA (E = 1800 MPa), nominal 5 mm second-order tetrahedra and 5 N at the far front rim of the 1.5 mm pipe. Deflection is 0.0029 mm sideways and 0.0158 mm down, against limits of 1.0 and 0.5 mm. Infill, layer bonds, mesh convergence, board compliance, fatigue and strength remain unqualified.
- **Local review slice:** Windows OrcaSlicer, system P1S 0.4 machine, 0.20 mm Standard process with the v1 overrides (two Arachne walls, 20 % infill, 5 mm brim, organic tree supports from the bed at 45°, small overhangs kept), and the owner's calibrated PolyLite ASA - ReproCal filament. Shrink compensation is applied once.
  - Result: 14h 43m 48s and 332.74 g in total, of which 19.61 g is support.
  - About 9 g of the support is peg support behind the mounting face, as in v1.
  - About 10 g is organic support the slicer sends to the engraved numerals' counters.
  - Changing the support threshold (30, 40 or 45 degrees) or the small-overhang removal setting does not change this. A straight cut is worse (26 g), because the stroke ceilings then attract support.
  - Painting a support blocker over the numerals should avoid it; this is not yet sliced.
  - No printer communication or published G-code is part of this review.
- **Physical checks pending:** print, socket fit, roof and numeral quality, first-layer adhesion, support release, peg fit, grasp and tool retention.

## Review history

The design went through five visual review rounds with an independent reviewer, on workbench-shaded and smooth renders. Scores went from 3/10 (v1) to 5.5, 7, 8 and 8.5 (publish).
