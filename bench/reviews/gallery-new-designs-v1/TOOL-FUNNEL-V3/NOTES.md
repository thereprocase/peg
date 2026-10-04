# Rectangular tool funnel v3 — rounded exterior and softened rim

The owner's “fillets and chamfers” revision adds a restrained manufactured finish to the upright, open-bottom funnel. The simple rectangular passage, two-cell mount and straight vertical pickup remain. This is a fresh styled body, not a claim that its upper exterior is still v1-identical.

## Deliberate edge treatments

- **R2 mm** on the exterior corner/knee network: twelve connected edges soften the vertical corners, sloping corners and transition into the lower sleeve.
- **R2 mm** on the two forward web corners and two concave web-to-plate roots, making the connection less blocky without changing the rear interface.
- **0.6 mm outer rim chamfer** around the upper shell before fusion.
- A four-plane inner entry break, **0.6 mm axial depth / 0.6 mm horizontal offset per side**, opens the rim to **23.2 × 77.2 mm**. Below this short lead-in, the original taper remains; its nominal unbroken top was 22 × 76 mm.

These groups are explicit in the generator; failed fillets do not get silently omitted. The inner lead-in is constructed as a ruled rectangular cutter rather than relying on a fragile all-edge chamfer operation. There are no decorative windows, ribs, catches or mechanisms.

The **11 × 48 mm throat**, **14 × 48 mm bottom opening**, 22 mm lower extension and common **Z=-64 mm** flat base remain. Upper nominal wall offset is 4 mm; the straight lower side walls remain 2.5 mm. The vertical corner rounds change the bed's outline slightly, but no blanket wall-to-bottom fillet removes its planar contact. The candidate's `bed_perimeter_not_rounded` flag means the bottom-plane edge is not rolled upward; it does not deny the rounded corners in the bed's XY outline.

[Empty body](empty.png), [rim/top view](rim-top.png), [loaded pair](loaded.png), [actual mesh sections and dimensions](dimensions.png), [print pose](print-pose.png), and [actual bed face](bed-contact.png) show the selected geometry. [Native CAD](editable.FCStd) and installed/upright STLs are included. The [relative-asset viewer](viewer/index.html) reuses the browser-reviewed camera and supports both/single/empty views and the full pickup route. STEP remains internal FEA input, not a qualified download.

## Mount, bed and printing

The rear functional region has **zero exact CAD symmetric difference** from `common.receiver(2,2,'upright',z0=-64)`. Hooks, hoop/barb features, bearing surfaces and sharp board seams are protected; the upright hoops remain the same as v2. No shared geometry or prior files changed.

One connected bed face measures **1,201.7032 mm²** in CAD and **1,201.7014 mm²** from the complete print-mesh bed triangles, a 0.00174 mm² difference. The **672 mm² bottom hole remains fully open**. Upright pose is translation only; minimum print Z is 0.0000001 mm from the CAD bounding-box offset. `bed-contact.stl` is diagnostic surface evidence, not a printable solid.

The print facet screen adds **no front-body surface beyond 45°** with its 0.1° classification tolerance. The existing 45° internal transition remains separately recorded at 203.65 mm²; rear peg overhang screening remains 130.54 mm². Nominal taper angles are 9.75° X / 23.63° Y from vertical; the local rounds interpolate the adjacent exterior directions. Actual peg supports, transition quality and support removal still require slicer review. **No slice, toolpath, support-free or printed qualification is claimed.**

Mount width remains 48.8 mm, with identical holders shown at 50.8 mm centres. Installed bounds are X±24.4, Y=-10.79..89.773, Z=-64..5.445 mm. CAD volume is **71.477 cm³**, nominal solid ASA estimate **76.48 g**; these are not sliced usage. The ordinary native CAD shape is valid and the installed/print meshes are watertight; no optional deep STEP/BOP qualification was pursued.

## Focused matching checks

[checks.json](checks.json) passes all four nominal tool cases: Knipex and Klein in reference and illustrative +10° opening poses. First axial contact stays on a robust grip. Every full-component route, including the separate coil mesh, has zero overlap at **56 samples of the 110 mm vertical lift**. Minimum seated hardware gap remains **1.750 mm** at Klein's rivet; minimum lowest-12-mm tip clearance remains **2.869 mm**. Reference minimum lifts to clear the rim by 3 mm are **63 mm Knipex / 107 mm Klein** (+10°: 62 / 106 mm); the viewer conservatively displays the checked 110 mm route. Leave this overhead plus hand space.

Two holders at 50.8 mm centres retain 2 mm between plates and 34.014 mm between nominal tool X envelopes. Minimum modeled board gap is 8.196 mm. The complete front body clears the board plane at **2,031 sampled installation poses**. Print-transform mesh bounds agree within 0.000001 mm. These are nominal mesh and bare-body checks, not proof of actual free settling, friction, dynamic capture or hoop release.

Fresh matching **5 N FEA passes**: **0.0954 mm sideways / 0.0146 mm downward** at the load point, below 1 / 0.5 mm targets. Global maxima are 0.1124 / 0.0266 mm. The method is unchanged: solid isotropic ASA E=1800 MPa, ν=0.35, 2 mm target mesh and fixed peg nodes. Results are specific to this styled body; no printed infill, layer strength, fatigue or board compliance claim follows.

**Physical fit, settling angle, rattle, actual released opening and grasp remain untested.** See [OWNER-TEST.md](OWNER-TEST.md). Geometry changes are limited to the requested styling; the top entry is more forgiving, while the lower passage and nominal seating are preserved.

## Provenance and reproduction

Selected CAD/check/FEA files come from private `rectangular-funnel-v3-draft1`; final figures and viewer derive from those same selected meshes. Five new v3 Python sources live under `bench/source/tool_holders/`. The checker, solver and renderer reuse unchanged v1 helpers where appropriate. Cosmetic probes and transient solver logs remain private. The section renderer uses direct plane/triangle intersections and requires no additional installed packages. [BUILD.json](BUILD.json) records source/dependency/artifact hashes; root's baseline was read but not overwritten. Prior v1/v2 files and all frozen tool models remain immutable.

Commands from repository root, with a fresh output path:

```sh
timeout 180s flatpak run --env=PYTHONPATH=/app/freecad/lib --command=python3 org.freecad.FreeCAD -B bench/source/tool_holders/rectangular_funnel_v3.py /home/repro/.local/state/peg-astra-3d/funnel-v3-new
timeout 420s /home/repro/venvs/physics/bin/python bench/source/tool_holders/rectangular_funnel_check_v3.py /home/repro/.local/state/peg-astra-3d/funnel-v3-new
timeout 900s flatpak run --env=PYTHONPATH=/app/freecad/lib --command=python3 org.freecad.FreeCAD -B bench/source/tool_holders/rectangular_funnel_fea_v3.py /home/repro/.local/state/peg-astra-3d/funnel-v3-new
timeout 120s /home/repro/venvs/physics/bin/python bench/source/tool_holders/rectangular_funnel_viewer_v3.py /home/repro/.local/state/peg-astra-3d/funnel-v3-new /home/repro/.local/state/peg-astra-3d/funnel-v3-viewer
timeout 30s python3 bench/source/tool_holders/rectangular_funnel_figures_v3.py /home/repro/.local/state/peg-astra-3d/funnel-v3-new
```

No staging/index, commit, push, slicing, publication or printer action was performed by the modeler. Root handles integration and hosting.

Private review: [Tailscale viewer](https://cachy5540.tail958a3.ts.net/tool-holders/?v=3). Root refines empty/loaded camera framing in the v3 viewer only; v1/v2 sources and all CAD/numerical evidence are unchanged.
