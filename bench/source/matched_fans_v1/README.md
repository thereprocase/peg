# Matched green-family Bondhus fans

The owner requested the green 13190 construction for 13189 metric and 33034
Torx, with a similar handle outline. `arrange.py` transfers the green main-fan
frames by interpolation, retains its three-tool deck frames and scales initial
XZ positions to tool length. Actual catalogue dimensions remain unchanged.
Direct forbidden-contact intervals place tools; the Torx deck's last tool uses
a sideways correction so it stays above the main tools rather than falling
below them. Two contact-limited compression passes tuck the decks. There is no
CAD candidate search. The green solid and local tool arrangement are unchanged.

Guides are max(60 mm,12 times shaft size), with the selected +0.38 mm total
clearance, separate 3 mm / 1.5 mm lead-ins and 1 mm vents. Filled stock, 8 mm
base rounds and 12 mm each-side / 16 mm bedward gussets follow green v3.
Tool angles rise >=10 degrees. Handle axes follow the hex flats; roll zero
is board-parallel, not gravity-horizontal. Torx uses the inherited circular
TIP envelopes: full shank diameter and rotational restraint remain unverified.
These circular sockets cannot enforce the rendered handle clocking.

`hx05_family.py` is a portable FreeCAD/stdlib feature module, separately named
from the already released inch module. `create_document.py` creates the two
spreadsheets, native receiver, named generators and Boolean history directly;
there is no static imported replacement for the parametric fan. The fixed rear
receiver uses the existing profile generator. New grids are sized to each body;
board-side cuts are checked against those exact generated receiver solids.

Build from repository root with a FreeCAD Python runtime. Native builders and
checkers require the existing numpy/scipy/trimesh build dependencies; the owner
bundle requires only FreeCAD and the included module.

```
python bench/source/matched_fans_v1/arrange.py BUILD
python bench/source/stacked_fans_v1/spacing.py BUILD
python bench/source/stacked_fans_v1/screen.py BUILD --saved
FreeCAD-Python bench/source/matched_fans_v1/create_document.py BUILD/tight-native/HX05A BUILD/layout.json HX05A
FreeCAD-Python bench/source/matched_fans_v1/create_document.py BUILD/tight-native/HX05B BUILD/layout.json HX05B
# Copy the frozen approved green body.brep into BUILD/tight-native/HX05C.
FreeCAD-Python bench/source/matched_fans_v1/export.py BUILD/tight-native
FreeCAD-Python bench/source/matched_fans_v1/print_pose.py BUILD/tight-native HX05A
FreeCAD-Python bench/source/matched_fans_v1/print_pose.py BUILD/tight-native HX05B
FreeCAD-Python bench/source/stacked_fans_v1/verify_native.py BUILD/tight-native
FreeCAD-Python bench/source/matched_fans_v1/pinch.py BUILD/tight-native
```

The edit/reopen tests use private copies. The setup macro installs the generator
and opens both documents; Installer smoke uses an isolated user module folder and real native document
loads, with display framing calls stubbed. Local GUI startup stalled before
model loading; Windows GUI first-open behavior remains untested.
Renders use the native solids and the existing scoped smoothed cel shader.
`publish.py BUILD` packages the validated files and creates the matched gallery
page; immutable CAD assets belong on the named release before publishing main.
Keep historical green/stacked pages and downloads, adding navigation links.

Evidence covers represented tool/hand envelopes and axial socket release,
not subsequent free-hand removal, whole-rack installation or load strength.
The native print pose is unscaled and unsliced; compensation, brim, supports
and physical fit remain to be checked. Metric's nominal bed margin is narrow.
