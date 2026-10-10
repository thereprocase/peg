# HX05 stacked fan review

New construction study for Bondhus 33034, 13189 and 13190. The owner's HX04
fan and the previous final-racks-v1 downloads are unchanged.

The longer tools have independent axes and staggered floors. Each successive
floor starts 6 mm farther left and 5 mm lower, before direct clearance
placement. The three small keys tuck individually into available gaps. There is
no common fan centre. The small-key deck sits farther back (70 mm handle-centre
depth versus 125 mm for the main fan), keeping its shafts out of the main run.
The top hook row is the shared grid datum; the plate is sized to the socket
envelope rather than rounded outward by a full board row. The handle bars are perpendicular to their shaft axes.
Hex flats retain the handle's flat-to-flat clocking.

Three different clearance requirements apply:

* At least approximately 1 mm between represented steel shaft surfaces near the
  buried ends. This is NOT a 1 mm plastic wall. Socket clearance consumes part
  of this gap; the shared web widens where shafts diverge.
* Separate full lead-in mouths, with a 2 mm envelope spacing target. Each lead
  adds 3 mm axial length and expands 1.5 mm per flat/radius at the entrance.
* Axial socket release and a 50 mm diameter front-end grasp envelope must clear
  neighboring stored tools. This proxy does not represent every grip or hand.

Hex guides use +0.38 mm total across flats, physically selected only for the
owner's 3 mm and 5 mm coupon tools. Guide length is max(40 mm, 8 times shaft
size), plus the lead-in. The floor is 3 mm thick with a 1 mm vent. Torx uses a
circular catalogue tip envelope and remains provisional for fit and clocking.
Catalogue tool lengths/bars and an assumed 18 mm grip diameter are envelopes,
not manufacturer-measured tool surfaces.

`layout.py` and `pack.py` construct the reference arrangement from these rules. Each
possible contact gives a forbidden interval of vertical translation; merging
those intervals gives the nearest available position without an optimizer or
candidate campaign. `densify.py` compresses the frozen `reference-layout.json`
using the same contact intervals in rotated coordinate frames: each translation
stops before its first contact. The metric deck's two upper keys first move
into the nearest clear vertical gaps, retaining the middle key's low pocket.
Tool angles, fits and hand envelopes are unchanged. This is a deterministic
compact arrangement, not a global optimum. `spacing.py` derives separate
conservative separations on the 25.4 mm board grid, including nonadjacent pairs.
`screen.py` independently checks stored tools, withdrawal
and hand envelopes. Its fine sphere covers and translation padding give lower
bounds for the represented capsules and paths, not physical qualification.

`build.py` grows native FreeCAD solids around the saved layout. It reuses the
reviewed receiver geometry without altering board-side profiles. Extended
straight cutters also relieve any supporting web along the shaft's exit path.
Cached native solids require an exact match of every local tool parameter.
Changes only to rack translations regenerate the stack assembly and its layout
hash without rebuilding unchanged individual solids.
`verify_native.py` checks conservative continuous tool/hand sweeps against the
native bodies for that axial release and grasp approach. The subsequent free-hand
maneuver is not modelled; no uniform 2 mm guide-wall requirement is imposed at the tips.

Example local sequence (FreeCAD Python needs numpy/scipy/trimesh):

```
python3 densify.py BUILD
python3 spacing.py BUILD
python3 screen.py BUILD --saved
FreeCAD-Python build.py BUILD/tight-native
FreeCAD-Python verify_native.py BUILD/tight-native
FreeCAD-Python sections.py BUILD/tight-native
HX_FAN_BUILD_DIR=BUILD/tight-native HX_FAN_OUTPUT_DIR=BUILD/renders node render.cjs
python3 publish_review.py BUILD
```

`handles_preview.py` makes capsule envelopes for checking the arrangement
before native construction. Its meshes are never manufacturing geometry.

These are review models. Whole-host installation motion, physical fit at the
new print orientations, supports, thin-web printability, stiffness and load
capacity require separate qualification. No prior FEA or installation proof
transfers to this geometry. No G-code is generated or sent.
