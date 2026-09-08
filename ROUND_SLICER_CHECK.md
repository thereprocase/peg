# Round anchor: FDM toolpath check

We checked the frozen **5.6 mm circular neck and locator, 4.8 mm circular retaining tongue, and 6 mm spine**. Both supported STLs preserve the complete functional anchor. They add removable printing geometry; they do not flatten the peg-bearing surfaces.

## Print files

| File | Intended use | Review settings |
|---|---|---|
| `cad/round_side_supported.stl` | Side orientation, preferred strength starting point | 0.4 mm nozzle; 0.2 mm layers; 0.45 mm lines; five walls; solid line infill |
| `cad/round_upright_supported.stl` | Upright integration with a host | Same nozzle/layer/line values; two walls and solid line infill around cradles so bridge skin can span between webs |

The generic trials use a 6 mm brim and **automatic supports off**: the support geometry already appears in each STL. Keep all STL shells together. The side model contains four disconnected solids; these include the functional anchor and support solids, and all need to retain their relative placement. Use the colored `*_support_reference.step` assemblies to distinguish retained geometry from printing aids.

## Why the side file includes a thin pad

With a 6 mm spine, the 5.6 mm neck lies only 0.20 mm above the side print bed. At 0.20 mm layers, that space cannot accommodate a removable 0.20 mm support interface. Our first side cradle trial therefore still started long neck contours over air. The final support arrangement lifts the complete functional model **0.40 mm**, places a **0.20 mm sacrificial pad under the spine**, and puts conformal cradles under the side-facing hemisphere of each round projection. A 0.20 mm gap separates those aids from the model. The installed bottom bearing crown stays away from side-support contact.

For upright printing, conformal saddles support the earliest central underside of each circular section. Pairs of nominal 0.50 mm ramp webs carry those saddles from the spine or bed. The ramps rise at 45 degrees and the saddle floors bridge between them. Adjacent webs can merge where the neck and tongue supports intersect. The saddle-to-model gap remains 0.20 mm. A two-wall, solid-fill local modifier allows directed bridge skin through the saddle floors; blindly using five walls fills narrow floors with nested perimeters.

![CAD-derived print supports](visuals/round-print-options.png)

## Actual path evidence

We sliced with **CuraEngine 5.0.0 and matching Cura 5.0.0 generic FDM definitions**. Each supported model produced valid GCode for review. This is not a Bambu P1S profile or a physical print/load test.

The following conservative screen examines portions of actual perimeter paths, including parts of a path that remain connected to the spine:

| Configuration | Layers | Layers flagged | Longest flagged perimeter portion |
|---|---:|---:|---:|
| side supported | 32 | 0 | 0.000 mm |
| upright supported | 178 | 1 | 0.051 mm |
| side unsupported | 30 | 4 | 4.377 mm |
| upright unsupported | 178 | 4 | 3.024 mm |

A flagged portion lies outside the previous model deposition envelope or the support envelope two layers earlier, after a 0.20 mm horizontal expansion. Two layers account for the 0.20 mm removable interface at the tested 0.20 mm layer height. We classify modeled support using sections of the original functional STL, with a 0.05 mm numerical halo. For the lifted side print, we translate that functional reference upward by 0.40 mm before classifying paths.

These values identify overhang/bridge candidates; they are not pass/fail print simulations. A residual approximately 0.05 mm edge fringe is below the line-width scale and occurs at the early spine edge rather than a floating round-peg start. Read the raw `*_toolpath_evidence.json` segment coordinates for the exact residual. The supplied interfaces still require a physical check for release, surface finish, and peg fit. Upright layer adhesion requires separate load qualification from side printing.

## Removal

1. Let the print cool. Remove the brim and the side spine pad.
2. For the side print, lift the shallow cradle pieces away from the curved side surfaces. Do not remove material from the round peg to release a stubborn support.
3. For the upright print, cut each orange ramp root at the spine, then lift the connected ramp-and-saddle pieces away from the rods. Use the reference STEP to distinguish support roots from the functional neck.
4. Remove residual interface burrs and check that the neck and lower locator retain their round section. Test fit before loading the final holder.

`round_print_supports.py` exposes interface gap, web thickness, cradle floor, support angle, root embed, side lift, and relief settings independently of board thickness and functional peg geometry. A parameter change requires another slice preview, especially if it changes layer alignment or the relative neck/tongue diameters.

## Reproduction and limits

`review_settings/side.json` and `review_settings/upright.json` contain every explicit generic engine setting used. The definitions supply the remaining defaults. Temperatures and machine defaults exist only to make the geometry review reproducible; they are not a recommended printer/material profile. No GCode or slicer binary enters this repository.

The portable scripts in `tools/` record the actual engine command, reconstruct deposited widths from extrusion volume, and reproduce the path screen. `round_slicer_check.json` records package versions, final parameters, metrics, and input STL hashes. `tools/ROUND_REVIEW.md` gives the exact workflow. The geometry-only motion study applies after removing all printing aids.
