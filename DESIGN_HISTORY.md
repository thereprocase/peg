# Design history

This record preserves the requirements, engineering decisions, alternatives, and remaining work from the September 2026 design session. It describes the visible project work and evidence; it is not a transcript of hidden reasoning. The current geometry and verification results take precedence over early candidate dimensions.

## What the user wanted

The opening request was:

> Create the perfect modular parametric standard 1/4" pegboard hook model I can drop onto all sorts of pegboard mounts.

The task developed into a reusable rear attachment interface: an upper retaining tongue, a lower locator one hole row below, and a front spine that can merge into an arbitrary holder. The user emphasized FDM strength, easy insertion and removal, firm seated holding, and a full motion study. They then directed the default toward common Home Depot/Lowe's hardboard rather than assuming every board is 1/4 inch thick.

Two later questions sharpened the evaluation:

> this is strong and smart and nice?

> what would make this the most FDM friendly possible?

The later work added a second print orientation with sacrificial supports for integration into upright holders. The final request directed publication of all project knowledge, sources, CAD, animations, motion study, and detailed documentation to [thereprocase/peg](https://github.com/thereprocase/peg), with immediate preservation of the design history and a next-agent handoff.

Only the three quoted prompts above were available verbatim to the author of this record. The intervening requirements and final publication request are summarized from the project coordination record; they are not reconstructed quotations.

## Requirements that should persist

- Provide a reusable parametric interface, not just one finished tool hook.
- Target the common US 1/4-inch hook/hole family on a 1-inch grid.
- Treat board thickness and actual hole diameter as separate dimensions.
- Prioritize a strong printable load path, smooth installation, and limited seated movement.
- Check the complete anchor through the whole insertion and removal motion, including its lower locator and front spine.
- Supply editable procedural sources and solid/mesh exports that ordinary CAD and slicers can use.
- Make the most immediately usable print and CAD choices obvious.
- Preserve the engineering evidence and design evolution in the repository.
- Describe what tests establish precisely; do not turn a geometric check into a load rating or a claim of universal fit.

## Board research changed the default

The first conceptual discussion used 6.35 mm board thickness because the request named 1/4-inch pegboard. Product research showed why that was too coarse. Multiple current Home Depot and Lowe's sheet-stock listings describe nominal 3/16-inch hardboard with **0.155-inch actual thickness, or 3.937 mm**. A smaller Home Depot panel lists 0.165 inch, or 4.191 mm. Lowe's also lists true 0.25-inch hardboard products.

The default therefore became **3.94 mm thickness, 6.35 mm minimum hole diameter, and 25.4 mm pitch**. Lowe's common DPI products can have **9/32-inch holes, or 7.14375 mm**; that became a separate hole-specific variant. The source assortment supports the practical default, but it does not establish a national sales majority or a universal board size. A Canada-only 5.5 mm/0.22-inch example was not used to establish a US default. A Lowe's listing with transposed panel/thickness fields was treated cautiously.

See [research.md](research.md) for the product evidence and direct links.

## The attachment concept

The anchor uses an upper neck that passes through the board and a shallow rising tongue that captures the board's rear face. The lower locator enters the hole one row below and limits rotation. A long front spine bears on the board face and provides a convenient fusion surface for the user's holder.

The core profile has constant 4 mm width across the board. Printing it on its broad side puts the complete bent hook and root inside each layer. The profile needs no automatic support in that orientation. A short chamfered locator helps it enter during the final rotation.

A tight, short 90-degree elbow was an unattractive starting point because its intermediate insertion orientations can need substantially more aperture than its final seated pose. The adopted shallow tongue trades a little rear projection for a feasible gentle threading motion and a thicker neck.

The anchor is removable by a combined rotation and translation. It has no spring preload or positive snap lock. The words “retaining” and “holding” describe the geometry and bearing arrangement, not a certified working load.

## Geometry development and the snug-fit revision

The early motion work found a path for a steeper, shorter tongue with a 3.1 mm neck. Increasing that neck to 3.6 mm invalidated the original path. Increasing the tongue's rearward run to **5 mm** with **3 mm rise** allowed the thicker neck across the tested thickness presets.

The first broadly compatible profile still allowed approximately **2.12 mm straight outward movement and 3.02 degrees of outward rocking**. That did not meet the user's request for firm seated holding. Moving the elbow forward and searching a combined lift, tip, and translation reduced those quantities to approximately **0.47 mm and 0.69 degrees**.

The final design calculates the elbow position from a target pull clearance rather than treating a fixed elbow coordinate as an unexplained fit setting. `elbow_offset=None` requests the derived value. `pull_clearance=0.47` sets the target straight outward movement before the retaining shoulder contacts the rear board surface.

The final design distinguishes the geometry's convenient coordinate origin from its physical seated pose. It seats at **Y=-0.15 mm, Z=-0.12 mm, rotation=0 degrees**, closing the front bearing and upper bore contacts. A centered part in a clearance hole would otherwise appear supported without establishing gravity bearing.

## Final functional dimensions

| Parameter | Value |
|---|---:|
| Default board thickness | 3.94 mm |
| Default hole diameter | 6.35 mm |
| Hole pitch | 25.4 mm |
| Constant profile width | 4.0 mm |
| Neck height | 3.6 mm |
| Spine depth | 4.5 mm |
| Spine height | 34.6 mm |
| Tongue run / rise | 5.0 / 3.0 mm |
| Lower locator projection / height | 2.3 / 3.0 mm |
| Target straight pull movement | 0.47 mm |
| Reserved free-threading bore half-height allowance | 0.10 mm |

The neck area is **14.4 mm²**, and its elastic section modulus for bending in the side-profile plane is **8.64 mm³**. These are geometric properties, not material allowables.

## What the full motion study establishes

For a constant-width part centered in a circular bore, the restrictive vertical opening is `sqrt(hole_diameter² - width²)`. For the default anchor, this is **4.932 mm**, rather than the full 6.35 mm hole diameter. The solver therefore accounts for the entire 4 mm width instead of checking an infinitesimally thin center section.

An A* search finds coupled translations and rotations. The retained path receives a continuous separation check that bounds every intermediate rigid-body position, recursively subdividing intervals where needed. The final translation into intended bearing contact uses an exact polygonal sweep. Reversing the verified path gives the same swept volume for removal. Dense samples provide additional evidence and the animation; they are not the sole basis of the continuous claim.

| Board / hole | Maximum tilt | Maximum lift | Result |
|---|---:|---:|---|
| 3.94 / 6.35 mm | 19.25 degrees | 0.82 mm | Pass |
| 4.19 / 6.35 mm | 19.25 degrees | 0.92 mm | Pass |
| 4.7625 / 6.35 mm | 19.75 degrees | 1.17 mm | Pass |
| 6.35 / 6.35 mm | 20.00 degrees | 1.77 mm | Pass |
| 3.94 / 7.14375 mm | 9.75 degrees | 0.22 mm | Pass |

The default needs approximately **5.55 mm clear projection behind the board** along its modeled path. An independent sampled OpenCascade check examines the default and two-column geometry in true 3D circular bores. The study proves a feasible path under its stated assumptions, not the minimum possible tilt or one exact human hand trajectory.

See [MOTION_STUDY.md](MOTION_STUDY.md), `motion_results.json`, and `occ_motion_check.json` for the complete methodology and results.

## The “strong, smart, nice” assessment

The design is coherent: it uses a shallow rounded tongue, short lead-in locator, measurable fit settings, real seated contacts, and a favorable flat print orientation. Its shape is compact and functional. Those are supportable design judgments.

The strength assessment remains conditional. The 4 × 3.6 mm neck is small, and a long host lever arm can amplify its load. The rectangular section initially contacts the round bore near its two outer lower edges, which can concentrate pressure in hardboard. The profile union leaves abrupt neck-to-spine shoulders; the widthwise edges remain sharp. The controlled pull movement and rocking are not equivalent to zero rattle or preload.

The accurate characterization at this stage is **a thoughtful, strength-oriented prototype with verified geometric motion**. No physical fit, pull, fatigue, creep, or comparative-orientation strength test has occurred. FEA has not occurred either.

## FDM improvements considered

The highest-value improvement identified was preserving the side-print orientation after integration into a real holder. A separate mechanically captured cartridge would achieve that when the holder needs another build orientation. Broad keyed shoulders should transfer load; a keeper should retain the cartridge. That cartridge interface remains a future concept, not a delivered feature.

Other proposed improvements remain unimplemented unless a later source revision explicitly adds them:

1. Add calibrated relief around the bed-facing perimeter to keep elephant foot outside the insertion envelope. A preliminary discussion suggested roughly 0.15–0.25 mm relief over 0.2–0.3 mm height; these are tuning ranges, not established production tolerances.
2. Improve abrupt root transitions using available front-side space. The lower neck already reaches its bore-bearing limit, so simply adding a large fillet there can collide with the board and requires renewed motion checks.
3. Provide physically calibrated easy-fit and snug-fit presets. The 0.10 mm free-threading allowance is demanding enough that actual printer and board variation matters.
4. Consider curved bore-bearing surfaces if tests show local wear or crushing. That would complicate the geometry and require replacing or extending the constant-width verification method.
5. Inspect actual continuous perimeter paths and seam placement. Convenient multiples of a nominal line width do not guarantee good toolpaths.

## Upright printing: supports solve a different problem

The second delivered print option keeps the installed Z direction upright for holders that must stand on the bed. It adds **four sacrificial membranes**, two below each projection. Each membrane is **0.50 mm thick**, sits **0.15 mm inside** an outer width face, and grows rearward on a **45-degree ramp**. The paired membranes leave a **2.70 mm bridge span** across X. They add approximately **22.6 mm³** of plastic to the default anchor.

These webs are cutting targets, not permanent reinforcing gussets. Cut every root and roof attachment, remove all four webs, and trim the original interface flush before installation. The inset protects the outer bearing corners during trimming. Do not twist the tongue to fracture supports away.

The supported CAD is a valid single solid with a watertight STL. Geometric web-growth checks cover all five presets at four layer phases. After complete flush removal, the functional interface returns to the existing motion-checked geometry. Residual support material can defeat that assumption.

## Actual slicing changed the recommendation

A generic **CuraEngine 5.0.0** toolpath review sliced both orientations with automatic supports off. The side orientation used **five walls**. Initially applying five walls to the upright version filled its narrow roofs with nested perimeter loops, leaving no clean transverse roof skin across the supporting webs.

The successful upright review used **two walls and 100% line infill**, with bridge controls described in [SLICER_CHECK.md](SLICER_CHECK.md). Cura retained all four 0.50 mm webs and produced X-directed roof skin. The inspected lower roof had approximately 2.241 mm centerline spans; the upper roof had approximately 2.650 mm spans. Those path lengths differ from the 2.70 mm geometric gap because the slicer also places perimeters and overlap.

The review found one connected first-layer model footprint and no wholly detached deposition components under its defined component check. The isolated upright coupon used a 6 mm brim. A larger holder may provide sufficient footprint without that brim.

This is actual generic toolpath evidence, not a physical print or a Bambu P1S/OrcaSlicer certification. The upright layers still carry the hook differently from the flat layers. The supports make deposition feasible; they do not recreate the flat orientation's continuous in-layer load path.

`Pegboard_Print_Options.3mf` contains both geometries as a standard geometry-only 3MF. It has no machine-specific profile or G-code. The generic review G-code is deliberately outside the deliverable package.

## Current boundary and next decisions

The sources, exports, figures, motion evidence, and generic slicing evidence are ready for a physical prototype. The next useful decision should follow a real board-and-printer trial: install/remove feel, snugness, support trimming quality, and a representative loaded holder. Increase engineering complexity only where those tests identify a concrete problem.

Preserve the functional interface and verification contract when changing support geometry. Preserve the provenance of tested versus proposed improvements. Keep the current usable exports prominent, with older alternatives retained in version history rather than mixed into the primary print choices.
