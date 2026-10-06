# Three bespoke holder prototypes

Read the [print and design rules](../../source/bespoke_tools_v1/PRINT-DESIGN-RULES.md)
and each model's notes before changing geometry.

| Model | Function | Bed face | Local ASA time | 5 N down |
|---|---|---|---|---|
| [HX01](HX01/NOTES.md) | Nine open-front metric hex-key seats | Flat bottom | 3h 39m | 0.1469 mm |
| [TM01](TM01/NOTES.md) | Tape-measure dock | Flat bottom | 1h 53m | 0.0603 mm |
| [CL01](CL01/NOTES.md) | Coiled test-lead / cable hanger | Right cheek | 1h 39m | 0.0056 mm |

Each model passes the recorded native, mesh, print-geometry, nominal pickup, front-body
installation and solid-ASA stiffness checks. Actual local ASA slices put supports at
the pegs. Physical print, fit, handling and bump tests are pending. The owner stores the
multimeter flat elsewhere; this set excludes the proposed display cradle.

The public-facing prototype page is `docs/gallery/bespoke-tools/index.html`.
`docs/gallery/tool-references/index.html` links the inspected native hex-key and caliper
models with their provenance. Foreign source CAD remains outside the bundle.

The generated native exports live locally beside their evidence. Package them with:

```
python3 publication/package_bespoke_cad.py /path/to/local/release-directory
```

This creates a checked ZIP containing STEP, FreeCAD, installed/oriented STL, matching
construction sources, notes and numerical evidence. The generated native files and
machine-specific slices are excluded from Git. Public display media and oriented meshes
are copied by `publication/build_bespoke_review.py`; their exact receipts are checked
by `tools/check_bespoke_tools.py` through the gallery check.

Rebuild from repository root using a FreeCAD 1.1 Python runtime and a timeout:

```
timeout 600 FREECAD_PYTHON bench/source/bespoke_tools_v1/build.py
```

The review scripts accept an individual part ID for mesh/FEA/slicing. Slicing uses the
existing local P1S and calibrated ASA profiles; update the explicit runtime/profile paths
for another machine. Slicer G-code stays local. The original solder workbench and its
frozen studies are unchanged.
