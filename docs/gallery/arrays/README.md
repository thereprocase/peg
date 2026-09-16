# Pegstr arrays with our custom peg interface

Open pegstr-custom.scad in OpenSCAD. Change profile (P01 or P09), columns and rows.
Keep PegBoard-library.scad, our-peg.scad and functional-peg.stl in the same folder.
F6 renders the solid; export STL after rendering. Preset SCAD files are included.

P01: 6.5 mm nominal rounded square openings, 8.3 mm pitch, 12.8 mm seat height.
P09: 10 mm nominal round openings (10.4 mm across in the original and generated
polygonal profile), 13.25 mm pitch, 20 mm seat height.

The eight reviewed presets all have four depth rows:
P01: 3, 6, 8 or 12 columns (12, 24, 32 or 48 seats).
P09: 4, 9, 12 or 18 columns (16, 36, 48 or 72 seats).

This uses the actual supplied Pegstr OpenSCAD modules, not mesh tiling. Profile
settings were recovered against the archived models. The archived STLs appear
to use a slightly different outer rounding/gusset implementation; P09 from this
source is 0.33 mm shallower. Hole size, profile, pitch and all four row positions
are compared against the retained originals. The original STL files are unchanged.

our-peg.scad defines our_peg() and our_peg_columns(width). The peg is a frozen
tessellation of the settled STEP, with the reference handle removed and exact
shaft sections extended only inside the host. It is not an approximate SCAD
hook. peg-contract.json records the source hash, reference face and dimensions.
Pegstr's gusset construction now uses our receiving face instead of its own
separate plate. The functional peg geometry is never scaled or redesigned.

The back automatically widens to receive two horizontal peg columns, minimum
35.56 mm. Wider arrays add mount columns on the 25.4 mm lattice. The reference
handle is absent; the unchanged functional shafts overlap the host by 1.25 mm.
The complete back bears at Y=0.15 against the board. Do not scale the whole model.

Selected print face: right side down. The round roofs and local peg starts still
need bridge/support review. The smaller P01 also needs support beneath its bank,
which starts 4.44 mm above the edge of the wider receiving back in this pose.
Pose meshes are form-review assets, not qualified print files. No slicing or
physical fit test has been performed. Changed counts beyond these eight presets
need their own checks, including available printer volume and tool access.

Original Pegstr by Marius Gheorghescu / mgx. See ATTRIBUTION.txt and LICENSE.txt.
