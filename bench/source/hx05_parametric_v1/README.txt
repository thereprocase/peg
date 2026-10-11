HX05C / Bondhus 13190 inch fan — editable native FreeCAD model

FIRST OPEN (Windows / Linux / macOS)
1. Extract the ZIP into an ordinary folder. Keep its files together.
2. In FreeCAD, use Macro > Macros > Execute, or open SETUP_HX05.FCMacro
   and run it (F6). Select the extracted folder if prompted.
3. Setup installs the small hx05_parametric module in your FreeCAD user
   Mod/HX05Parametric folder and opens the native FCStd document.
   It changes no printer settings and installs no external Python packages.
4. Save As a personal working copy. Future opens need only that FCStd;
   the installed module restores its editable features automatically.

EDITING
Double-click 01_GlobalParameters or 02_KeyLayout in the tree. Edit yellow
cells and press F5 (Recompute). Keep the initial '=' and mm/deg units in
expressions, for example '=0.48 mm' or '=12 deg'. Full rebuilds can take several minutes.
The parameters also appear read-only on the generated features so there
is one clear editing authority: the two sheets.

Global sheet:
  AF clearance: total across-flats difference, NOT clearance per side.
  Lead depth/opening, seating floor, vent diameter, base corner radius,
  gusset width per side, gusset extension toward the print bed.
  Minimum upward angle: default 10 degrees.

Key layout sheet, one row per inch key:
  Guide: straight shaft engagement (lead-in is additional).
  Up: true angle above horizontal, tip toward handle, in installed pose.
  Out: angle of the shaft away from the pegboard plane.
  Roll: rotation of the T-bar/hex around the shaft; 0 lies in the board plane.
  Tip XYZ: seated tip location. X is right, Y toward you, Z up, in mm.
  Outer radius: sleeve envelope; keep enough material outside the lead-in.
  Nominal AF, overall tool length and handle length: catalogue dimensions.

Up and Out are independent angle controls, subject to sin(Up)^2+sin(Out)^2<1.
The shaft points toward +X; these parameters describe this selected fan family.
Invalid angles, short guides or insufficient lead-in wall produce an error.
Restore the previous cell value and press F5. Do not export an errored document.

FEATURE TREE
ApprovedMount: fixed native rear plate and approved peg interface.
ReferenceTools: editable reference tool features; select and Space to toggle.
AdditiveFeatures: filled base, individual sleeves and tapered gussets.
CuttingTools: individual entrance reserves and socket/lead-in/vent cutters.
BooleanHistory: native FreeCAD union/entrance cuts and robust socket cuts.
FinalHolder: the finished solid. Select this object alone for STEP/STL export.
START HERE: an editing guide embedded in the FCStd.

The rear peg profiles, grid and plate outline are deliberately preserved as
one protected native feature. This package parametrizes the fan construction;
it does not redesign or certify the mounting interface. Changing the fixed
mount independently is possible in FreeCAD but requires separate review.

The custom features use only FreeCAD and standard Python. Source is supplied,
with no NumPy, SciPy, downloaded executable, network call or repository path
required at recompute time. The FCStd contains the actual CAD shapes, sheets,
expressions and feature links. Without the module it remains viewable, but
custom geometry cannot recompute until setup has been run.

VALIDATION / PRINTING
Default geometry is compared to the approved 9a9e695 native solid. The supplied
receipt records rebuild, save/reopen and parameter-edit tests and versions.
Changes invalidate previous tool/access/printing checks: inspect collisions,
clearance, inlet/vent access, bed size, supports and installation after edits.
The previous fixed-body slice needed a support blocker in the 9/64 socket.
This package is editable CAD, not a sliced printer job or a physical load rating.

DEVELOPER REBUILD
The source folder includes the frozen layout, document builder and edit tests.
To recreate the document, export FinalHolder as BREP for the approved reference,
then run create_document.py OUTPUT_DIR approved-layout.json REFERENCE.brep in
a FreeCAD Python environment with hx05_parametric.py on the module search path.
The builder extracts the fixed rear interface and rebuilds the fan features.
The included checks describe the tested FreeCAD version and validation scope.
