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
FreeCAD-Python ../stacked_fans_v1/build.py BUILD/tight-native
FreeCAD-Python ../stacked_fans_v1/verify_native.py BUILD/tight-native
FreeCAD-Python pinch.py BUILD/tight-native
FreeCAD-Python empty.py BUILD/tight-native
HX_FAN_BUILD_DIR=BUILD/tight-native HX_FAN_OUTPUT_DIR=BUILD/renders node ../stacked_fans_v1/render.cjs HX05C HX05C-empty stack
python3 publish.py BUILD
```

Native exports remain local review artifacts. The new page publishes renders
and numerical receipts. Subsequent free-hand removal, installation, printing,
supports and physical loads remain unqualified. No prior FEA result transfers.
