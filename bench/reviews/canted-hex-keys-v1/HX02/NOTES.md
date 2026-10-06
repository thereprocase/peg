# HX02 v1 · full-depth canted metric hex-key rack

Nine blind sockets take the entire straight long arm. The axes lean 30 degrees outward from vertical. The bends remain above the mouths and the short arms slope down toward the desk. The sizes, from the user's left to right, are 1.5, 2, 2.5, 3, 4, 5, 6, 8 and 10 mm. The owner's straight lengths are 89, 98, 110, 123, 140, 157, 176, 194 and 217 mm respectively; 140 mm for the 4 mm key is the requested linear interpolation. There are no 7 or 9 mm sockets.

Each key rests on a 3 mm blind floor. The bore encloses the full straight length, has 0.35 mm radial clearance outside the hexagonal circumradius and a 1.2 mm entry flare. Short-arm lengths and bend radii are illustrative assumptions recorded individually in report.json. The reference models use the supplied lengths for the straight sections, with the assumed bend added beyond each straight section.

Withdraw along the socket axis, upward and outward. The longest key needs approximately 220 mm of axial travel, reaching 110 mm outward and 191 mm upward from its seated position. Adjacent seated keys are checked along the sampled route. Tools elsewhere on the board are unmodeled; keep the withdrawal envelope clear. The inclined shaft allows gravity to favor the short arm's downward orientation. Friction, bumps, tool rotation and one-handed grip require a physical test.

## Body and print

The bank is 201.2 mm wide (eight grid cells), with 23 mm centre spacing and two mounting columns. A continuous upper tie and a lower diagonal tie brace the bank against the receiver. The longest socket is at the right cheek, and the blind ends step shorter toward the left.

Print on the broad right cheek. The bank's silhouette shrinks toward successive layers, while 50-degree pointed bore roofs close above each socket. The mounting hoops use the existing cheek orientation, so their flex stays within the layers. The original PF02 #9 hooks and PF07 #5 clipped-root hoops are retained behind the rear contact plane. Peg supports are externally accessible. Use the print-oriented STL and reslice for the printer and filament.

## Evidence and limits

The native checks cover one valid solid, unchanged board-side geometry, STEP round trips, tool withdrawal and closed-floor stops. Mesh checks cover bed contact, body face angles, disconnected starts and the print envelope. Installation screening checks the complete front body along the preserved nominal route; changed-fit physical installation remains unqualified.

The stiffness screen uses fixed peg nodes, isotropic solid ASA (E=1800 MPa) and a nominal 5 mm quadratic tetrahedral mesh, with 5 N loads at the far front rim near the left end. Infill, layer bonds, mesh convergence, board compliance, fatigue and strength remain unqualified. Local slicing uses the owner's P1S / PolyLite ASA profiles, 0.4 mm nozzle, 0.2 mm layers, two Arachne walls, 20% infill, 5 mm brim and organic supports from the bed. Shrink compensation is applied once. No printer communication or published G-code is part of this review.

Physical print, socket fit, first-layer adhesion, support release, peg fit, grasp and tool retention remain pending.

## Matching review numbers

Native volume: 813.34 cm³. Print envelope: 212.97 × 143.45 × 201.20 mm. Bed contact: 16226.17 mm². Flagged body overhang area and starting islands: zero.

5 N screen: 0.0026 mm sideways and 0.0205 mm downward. Local ASA slice: 16h 9m 54s, 344.95 g total, including 9.092 g of support and interface. The full extrusion classifications and bounds are in toolpaths.json; projections are in toolpaths.svg.

The slicer classifies the closing bore roofs as body bridges (0.577 g). Their 50-degree sides provide backing on both sides: at 0.2 mm layers the final transverse closure gap is at most 0.34 mm before shrink compensation. Four mouth-transition moves, each shorter than 0.02 mm, are classified as body overhang wall; together they extrude 0.00155 mm of filament. These are explicitly bounded in the publication check. The native body has zero flagged faces beyond the 45-degree screen. Physical roof quality and debris-free socket fit remain to be checked.
