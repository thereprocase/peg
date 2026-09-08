# Reproduce the toolpath evidence

These scripts preserve the actual September 2026 analysis used for `SLICER_CHECK.md`. They replace the original temporary `analyze_gcode.py`, `final_review.py`, and `slice_variant.py` with command-line inputs and no import-time execution. The underlying extrusion-width reconstruction, buffered line-envelope union, inspection layers, and 0.20 mm prior-layer reach match that work. No slicer binaries or GCode are included.

Python dependencies: `shapely`, and `matplotlib` when rendering a plot. Python 3.10 or newer is required. The historical run used CuraEngine 5.0.0 and Cura 5.0.0 generic definitions; exact Ubuntu package versions and every explicit settings input are in `../slicer_check.json`. `../SLICER_CHECK.md` explains their limitations.

From the repository root, with your own executable and definition paths:

```bash
python tools/slice_toolpaths.py \
  --engine /path/to/CuraEngine \
  --definitions /path/to/cura/resources/definitions \
  --output /tmp/peg-toolpath-review \
  --include-five-wall-trial

python tools/analyze_toolpaths.py \
  --side /tmp/peg-toolpath-review/side_REVIEW_ONLY.gcode \
  --upright /tmp/peg-toolpath-review/upright_REVIEW_ONLY.gcode \
  --output /tmp/peg-toolpath-evidence
```

If a locally extracted engine needs shared libraries, point `LD_LIBRARY_PATH` to that installation's library directory before running. Use the engine's matching definitions. The slice script records each exact command and engine log beside its scratch GCode. It never communicates with a printer.

The analyzer assumes absolute XYZE moves, 1.75 mm filament, uniform 0.20 mm layers, and a 128 mm XY translation from the generic 256 mm bed. CLI flags expose these values. It rejects relative-mode GCode. It analyzes positive-extrusion G0/G1 moves and excludes Cura's `SKIRT` feature, which also labels these brim lines. It is not a general GCode interpreter: volumetric extrusion, arcs, variable layer height, or firmware transformations require extending the parser.

Deposited bead width equals filament volume divided by XY path length and layer height. The analysis buffers each path by half that width, joins the envelopes, closes 0.01 mm numerical gaps, and looks for whole components larger than 0.01 mm² that miss the previous layer expanded horizontally by 0.20 mm. This catches fully detached components, not unsupported portions of connected components. It does not establish bridge sag, thermal performance, adhesion, collision freedom, machine readiness, or load capacity.

The default web and roof inspection layers refer specifically to the shipped 3.94 mm board model: webs at layers 8/10/12 and 115/120/125/130; lower and upper roofs at layers 15 and 140. The plots inspect layers 8/15/120/140. Geometry or layer-height changes require selecting new layers and coordinate bands. The analyzer emits raw sample segments and reconstructed widths rather than hard-coding a passing result. Use those segments and the layer preview to inspect bridge directions and changes.

Historical results: side 20 layers; upright 173 layers; one connected first-layer model footprint in each; no wholly detached components under the stated envelope check; approximately 0.500 mm sampled web extrusion width. With the upright two-wall settings, sampled first-roof skin runs across X. The five-wall comparison consumes the narrow roof with nested perimeters. Prefer a local two-wall/solid-line-fill modifier for that upright region, inspect your slicer's roof paths, and keep the side orientation as the stronger starting point.

The archived summary includes manually interpreted conclusions from these observations; the reconstructed JSON retains raw evidence to reassess them. Review GCode is intentionally outside the repository and is not a machine-ready P1S profile.
