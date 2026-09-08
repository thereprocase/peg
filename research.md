# Pegboard compatibility and print basis

Research date: 8 September 2026. Dimensions are millimeters unless stated otherwise.

## Default

Use **3.94 mm board thickness, 25.4 mm hole pitch, and a 6.35 mm minimum hole diameter** as the starting preset for the common US home-center hardboard application. Keep all three independent parameters.

The 3.94 mm thickness follows several current Home Depot and Lowe's product listings for nominal 3/16-inch hardboard that report an actual thickness of 0.155 inch (3.937 mm). This is an inference from the assortment represented by those listings. We did not obtain national sales data or establish that this thickness accounts for a majority of installed US pegboard. Local availability and product specifications can vary.

The phrase “1/4-inch pegboard” does not reliably identify board thickness: it can identify the compatible hook/hole family. Lowe's common DPI hardboard listings specify 9/32-inch (7.144 mm) holes even though they accept the usual 1/4-inch hook family. The smaller 6.35 mm design aperture preserves compatibility with true 1/4-inch holes; larger holes leave more movement unless the user selects a measured-hole preset.

## Product evidence

| Product / primary listing | Stated board thickness | Hole evidence | Use in this design |
|---|---:|---|---|
| [Home Depot white 4 × 8, SKU 486140 / 202189722](https://www.homedepot.com/p/Pegboard-White-Panel-Common-3-16-in-x-4-ft-x-8-ft-Actual-0-155-in-x-47-7-in-x-95-7-in-486140/202189722) | Nominal 3/16 in; actual 0.155 in = **3.937 mm** | Not established from the retrieved product text | Supports the default thickness |
| [Lowe's white 4 × 8, 3014308](https://www.lowes.com/pd/1-Piece-Hardboard-Pegboard-Actual-47-75-in-95-75-in/3014308) | Nominal 3/16 in; actual 0.155 in = **3.937 mm** | Description specifies **9/32 in holes, 1 in centers** | Supports default thickness; demonstrates hole/nominal-size distinction |
| [Lowe's brown 4 × 8, 3014321](https://www.lowes.com/pd/Hardboard-Pegboard-Actual-47-75-in-x-95-75-in/3014321) | Actual 0.155 in = **3.937 mm** | Round holes | Independently corroborates default thickness |
| [Lowe's brown 2 × 4, 3043230](https://www.lowes.com/pd/Hardboard-Pegboard-Actual-23-875-in-x-0-155-in/3043230) | Nominal 3/16 in; actual listing/URL identifies **0.155 in** | Description specifies **9/32 in holes, 1 in centers** | Corroborates the family in a smaller panel |
| [Home Depot white 2 × 4, 7005028 / 202088812](https://www.homedepot.com/p/White-Peg-Board-Common-3-16-in-x-2-ft-x-4-ft-Actual-0-165-in-x-23-75-in-x-47-75-in-7005028/202088812) | Nominal 3/16 in; actual 0.165 in = **4.191 mm** | Not established from retrieved text | Shows why nominal size alone cannot set the throat |
| [DPI manufacturer pegboard family](https://www.decpanels.com/product/pegboard-paneling) | Lists **3/16 in = 4.7625 mm** for brown, white, and cherry panels; does not distinguish nominal from measured actual | Perforated hardboard | Supports a nominal 3/16 family, not a universal actual 4.7625 mm thickness |
| [Lowe's Triton white hardboard 2 × 4, 5013488893](https://www.lowes.com/pd/Triton-Products-4-Piece-Hardboard-Pegboard-Actual-24-in-x-48-in/5013488893) | Explicit actual **0.25 in = 6.35 mm** | **1/4 in** hole diameter | Basis for a separate thick-board preset |
| [Home Depot tempered 4 × 8, 210552 / 202088101](https://www.homedepot.com/p/1-4-in-x-4-ft-x-8-ft-Tempered-Pegboard-210552/202088101) | Product title specifies **1/4 in** | Not established from retrieved text | Corroborates a US home-center 1/4-inch board family; actual dimension not independently resolved |
| [Forest Plywood hardboard/pegboard assortment](https://forestplywood.com/product/hardboardpegboard/) | Lists **1/8–3/16 in** and explicitly discusses 1/8-inch pegboard | Describes **1/4 in holes, 1 in centers** | US supplier evidence for a thin 1/8-inch family; no current Home Depot/Lowe's 1/8-inch hardboard SKU was verified in this bounded search |

Two listing cautions affect interpretation. [Lowe's 3014320](https://www.lowes.com/pd/1-Piece-Hardboard-Pegboard-Actual-47-75-in-x-0-1875-in/3014320) appears to transpose its thickness and panel dimensions; it does not cleanly establish an actual 0.1875-inch thickness. The retrieved **0.22-inch / 5.5 mm Fibrex** example is from [Home Depot Canada](https://www.homedepot.ca/product/fibrex-5-5mm-48-inch-x96-inch-white-hdf-hardboard-pegboard/1000428749); it does not establish a US home-center thickness mode. We therefore retain 5.5 mm as a possible measured custom value, not a verified US default.

## Preset interpretation

| Family | Thickness to enter | Interpretation |
|---|---:|---|
| Common US home-center hardboard | **3.94** | Default based on the listings above |
| Other nominal 3/16 hardboard | **Measured value**, often represented here by 4.19 or nominal 4.76 | Recalculate geometry and motion for the actual board |
| True 1/4-inch hardboard | **6.35**, unless measured otherwise | Separate geometry; a thickness change requires another motion check |
| Thin 1/8-inch board | **Measured value**, nominal 3.175 | Custom compatibility case; verify hole diameter independently |
| Thin steel / ribbed plastic | **Measured local thickness at each hole** | Overall panel depth can include ribs or wall standoff and is not the hook throat dimension |

Triton's manufacturer specifications independently confirm **1/4-inch holes on 1-inch centers** for DuraBoard and list 1/4-inch-thick boards. [DuraBoard hole specifications](https://www.tritonproducts.com/duraboard-1), [DuraBoard dimensions](https://www.tritonproducts.com/duraboard-boards). Wall Control's manufacturer page specifies **20-gauge steel** and a **3/4-inch formed mounting flange**; the latter is wall standoff, not material thickness. [Wall Control panel construction](https://wallcontrol.com/products/16in-x-32in-horizontal-metal-pegboard-tool-board-panel).

## Print and fit precautions

The following are design recommendations, not manufacturer-certified settings or a load rating:

- Print the planar hook on its broad side so each layer contains the complete neck, retaining tongue, and root. Preserve continuous perimeter paths through the loaded bend.
- Start with a 0.4 mm nozzle, 0.16–0.20 mm layers, and five perimeters. Inspect the sliced small members to confirm they are effectively solid. Prusa recommends increasing perimeter count rather than infill for solid PETG parts. [Prusa PETG guidance](https://help.prusa3d.com/article/petg_2059).
- Start with dry unfilled PETG and its manufacturer-approved profile. Tune speed, temperature, and cooling for reliable layer bonding before evaluating strength. Do not assume a fast filament profile produces the same strength as a slower profile.
- Calibrate elephant-foot compensation; the first layer must not enlarge the section that passes through the holes. Remove strings and first-layer burrs before the fit trial.
- Print the small anchor coupon first. Measure several holes and the board thickness; paint buildup, worn holes, and local board variation affect fit.
- Tune hole clearance and board-throat clearance separately. The interface needs clearance to install and remove; a snug contact state requires verified bearing geometry rather than an assumed interference fit.
- Check the actual attached mount's swept envelope. A clear anchor-only trajectory does not guarantee that every host shape clears the board or neighboring tools.
- Establish any working load through physical tests of the printed material, orientation, board, and representative mount. A rigid-body motion study checks geometric interference; it does not establish strength, creep resistance, fatigue life, or positive locking.
