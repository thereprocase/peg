# Reproduce the round-anchor print review

Run from the directory containing `round_anchor.py`. Python dependencies are CadQuery, trimesh, NumPy, Shapely, and the repository's generic `tools/analyze_toolpaths.py` parser. The optional CAD support renderer also uses Matplotlib. The recorded slice used CuraEngine 5.0.0 with Cura 5.0.0 `fdmprinter.def.json` and `fdmextruder.def.json`; package versions appear in `round_slicer_check.json`.

Generate the two supported orientations from the exact frozen functional parameters:

```bash
python round_print_supports.py --geometry cad/round_geometry.json --name round
```

Slice to a scratch directory. These are generic geometry-review settings, not a machine-ready printer profile:

```bash
python tools/slice_round_toolpaths.py \
  --engine /path/to/CuraEngine \
  --definitions /path/to/cura/resources/definitions \
  --settings review_settings/side.json \
  --mesh cad/round_side_supported.stl \
  --output /tmp/peg-round-review/side_REVIEW_ONLY.gcode

python tools/slice_round_toolpaths.py \
  --engine /path/to/CuraEngine \
  --definitions /path/to/cura/resources/definitions \
  --settings review_settings/upright.json \
  --mesh cad/round_upright_supported.stl \
  --output /tmp/peg-round-review/upright_REVIEW_ONLY.gcode
```

If the extracted engine requires libraries, set `LD_LIBRARY_PATH` for that local installation. The slice helper saves its exact command and engine log next to the scratch GCode. It does not communicate with any printer.

Reconstruct deposited widths and screen every functional perimeter portion:

```bash
python tools/check_round_toolpaths.py /tmp/peg-round-review/side_REVIEW_ONLY.gcode \
  --functional-mesh cad/round_side_unsupported.stl \
  --functional-z-offset 0.4 \
  --output /tmp/peg-round-review/side.paths.json

python tools/check_round_toolpaths.py /tmp/peg-round-review/upright_REVIEW_ONLY.gcode \
  --functional-mesh cad/round_upright_unsupported.stl \
  --output /tmp/peg-round-review/upright.paths.json
```

The 0.40 mm side offset is essential: the final side support arrangement lifts the complete functional anchor above a 0.20 mm sacrificial pad. The original unsupported reference remains normalized to its own lowest face. Upright needs no extra Z translation. Do not let a slicer's “drop each part to bed” operation change the relative placement of separate STL shells.

To reproduce the unsupported comparison, slice the corresponding `round_*_unsupported.stl` using the same orientation's settings; omit `--functional-mesh` from the screen. All extrusion paths then count as model geometry.

## Method and provenance

`check_round_toolpaths.py` extends the earlier `analyze_gcode.py` / `final_review.py` workflow. The previous whole-component check could miss an unsupported peg because that peg still connected to the spine. This revision intersects individual perimeter centerlines with the supported region and records uncovered portions.

The parser reads absolute G0/G1 XYZ/E moves, assumes 1.75 mm filament and uniform 0.20 mm layers, and subtracts the generic 128 mm XY placement. It derives nominal deposited width from filament volume divided by path length and layer height. It does not interpret arcs, volumetric E, relative positioning, firmware transforms, or variable layers. The reviewed support-gap treatment specifically assumes 0.20 mm layer height and 0.20 mm interface gap.

For modeled supports, a section of the original functional STL at each Cura slice plane separates functional paths from sacrificial paths. Endpoints round to five decimal places before polygonization; a 0.05 mm halo handles small tessellation differences. Each deposited segment receives a half-width buffer. A functional perimeter portion is flagged if it extends more than 0.20 mm beyond the previous functional layer or the support layer two steps earlier. The two-layer reference accounts for one omitted layer at the support interface. The JSON retains every flagged segment so a reviewer can distinguish intended bridges, numerical fringes, and genuine unseeded contours.

This remains a geometric screen. It does not model extrudate sag, fan behavior, thermal history, support bonding/release, or strength. Physical fit and load tests remain separate.

## Design iteration retained in the source

A first uniform 5 mm candidate established the support approach. The final neck/locator grew to 5.6 mm while the retaining tongue became 4.8 mm. The support generator therefore builds projections for each segment radius and subtracts the complete exact functional shape, including the large spherical junction.

A nominal side cradle without lift failed at the frozen dimensions: the 0.20 mm neck-to-bed clearance could not fit a 0.20 mm removable interface at 0.20 mm layers. A 0.40 mm lift and thin spine pad fixed that deposition geometry. The source also retains a 0.12 mm sacrificial centerline-relief parameter to avoid zero-thickness bed tangencies in alternate support configurations; the final lifted configuration no longer relies on that tangency.

The upright support is intentionally different from the old rectangular anchor's edge-web roof. A round peg's center underside appears before its sides. Conformal saddles now seed that first curvature; pairs of ramp webs support each saddle. Support intersections may merge nominal 0.50 mm webs into wider removable roots.

The final source, exact input meshes, settings, raw JSON evidence, and support-reference STEP assemblies preserve this work. GCode and downloaded slicer binaries remain outside the repository.
