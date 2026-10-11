# Green inch fan: longer sleeves and flatter handles

The owner selected the green 13190 inch fan from the three-rack stack.
`reference-layout.json` freezes that published arrangement (a0e1056). Only the
inch rack changes; the metric and Torx racks retain their local geometry.

`arrange.py` increases every straight guide by 50%, from 40–76.2 mm to
60–114.3 mm. The 3 mm axial lead-in, 1.5 mm per-flat opening, +0.38 mm AF
clearance, square floor and 1 mm vents remain the same. Long-guide friction
and the other shaft sizes have not been physically qualified.

Each T-bar turns 30 degrees around its own shaft toward the pegboard plane.
This does not level the bar horizontally. Hex flat clocking follows the handle.
The main fan opens by an additional 0–15 degrees, in 2.5-degree increments,
keeping its staggered tip locations while allowing hand access with the flatter
bars. The 3/32 grip is checked at its opposite end; the symmetric bar and hex
have the same geometry when their direction vector is reversed. The 1/8 key
moves 18.12 mm sideways to clear the 5/16 release stroke. The final common
translation centres the receiver and sets the top hook row to zero.

The shared stacked-fan scripts calculate stack spacing, screen tool and hand
capsules, build native FreeCAD solids and check continuous axial socket-release
and front grasp sweeps against those solids. The earlier 50 mm grasp check remains as additional recorded clearance.
`pinch.py` independently checks two assumed 24 × 18 × 10 mm fingertip
pads at the frontmost end of every green-rack grip, including 3/32. Their
combined span around the 18 mm grip is 38 mm. Circumscribed convex hulls
bound both pads continuously during approach and axial release, tested against
all neighboring native tool and holder solids. This is not a whole-hand model.
The metric/Torx native solids may be reused only when all their tool parameters
match exactly; their assembly positions and layout hashes are regenerated.

```
python3 arrange.py BUILD
python3 ../stacked_fans_v1/spacing.py BUILD
python3 ../stacked_fans_v1/screen.py BUILD --saved
FreeCAD-Python build.py BUILD/tight-native
FreeCAD-Python print_pose.py BUILD/tight-native APPROVED_UNFILLED_BODY.brep
FreeCAD-Python ../stacked_fans_v1/verify_native.py BUILD/tight-native
FreeCAD-Python pinch.py BUILD/tight-native
FreeCAD-Python empty.py BUILD/tight-native
HX_FAN_BUILD_DIR=BUILD/tight-native HX_FAN_OUTPUT_DIR=BUILD/renders node ../stacked_fans_v1/render.cjs HX05C HX05C-empty HX05C-print stack
python3 publish.py BUILD
```

Native exports remain local review artifacts. The new page publishes renders
and numerical receipts. Subsequent free-hand removal, installation, printing,
supports and physical loads remain unqualified. No prior FEA result transfers.

The filled revision uses `strength.py`: a solid stock section with 8 mm
rounds in the print-bed XY plane (installed YZ), clipped beneath every socket
entrance. This connects the sleeve bending planes to a broad X-min foot.
A bounded 6 mm root-fillet operation succeeded at the longest eligible
backplate junction; the all-edge attempt did not succeed. Vents are extended
through the stock perpendicular to each shaft toward the front.

`print_pose.py` compares board-side geometry to the approved unfilled native
body from the 7c09b46 checkpoint, checks entrance/vent probes and exact flat
bed contact, then maps installed +X to printer +Z with 45 degrees of bed yaw.
It uses optimal bounding boxes because serialized trimmed faces can have
loose ordinary bounds. Native geometry remains nominal and unscaled.
The owner-profile Orca review, when recorded, is separate from these CAD
checks and from physical print qualification. No printer job is submitted.

The owner-profile Orca 2.3.2 review uses 0.20 mm layers, four walls, 35%
gyroid, five top/bottom layers, a 3 mm outer brim and bed-only organic
supports. ASA scale 1/0.9946 is applied once about the bed centre (Z about
zero), with filament shrink set to 100% in the flattened private profile.
The review archive estimates 57 h 32 min and 991.06 g, including supports.
Orca emitted repeated placeable-area diagnostics while generating organic
supports but completed export. This is not a qualified print job.

`toolpaths.py BUILD PRIVATE_GCODE OUTPUT_JSON` parses relative/absolute
extrusion and IJ arcs, screens sampled support centerlines against straight
hex socket cores and records feature/bounds totals. It excludes a 0.30 mm
wall margin, 0.50 mm end margins, funnels and vents; it is not a full bead
intersection or support-removal proof. Public receipts contain only review
settings, estimates, hashes and screen results. Machine profiles and G-code
remain private.

The review slice is NOT cleared for printing: 35 support moves enter the
9/64-inch socket core; the other nine cores have zero sampled hits. That
socket needs a support blocker and a new slice review. Aggregate extrusion
bounds can include machine sequences retaining the last feature tag and
are not a printable-area certificate. The geometry/renders are the delivered
review, not a released machine job.
