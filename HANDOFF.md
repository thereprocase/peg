# Next-agent handoff

## Immediate objective and authority

The user directed publication of **all project work** to [thereprocase/peg](https://github.com/thereprocase/peg): CAD, sources, print files, animations, motion study, detailed README, research, and design knowledge. The active publishing agent handles that repository operation. These files preserve the project state independently of the conversation.

Do not state that a push succeeded merely because this handoff exists. Check the repository and commit state. Do not let optional new design work delay the authorized publication of the current concrete result.

## Read first

1. [README.md](README.md): start files, integration, dimensions, usage, and limits.
2. [DESIGN_HISTORY.md](DESIGN_HISTORY.md): requirements, design evolution, critique, and proposed improvements.
3. [PRINTING_OPTIONS.md](PRINTING_OPTIONS.md): flat and upright options; support removal.
4. [MOTION_STUDY.md](MOTION_STUDY.md): motion proof, seated pose, measured freedom, assumptions.
5. [SLICER_CHECK.md](SLICER_CHECK.md): actual generic Cura paths and the important upright wall-count correction.
6. [research.md](research.md): primary product evidence for board presets.

## The result now

The project supplies a reusable parametric pegboard anchor: upper shallow retaining tongue, lower chamfered locator one row below, and a flat front spine for fusion into the user's holder. It is not a finished tool holder. The default targets common nominal 3/16-inch US home-center hardboard at **3.94 mm actual thickness**, with **6.35 mm minimum hole diameter** and **25.4 mm hole pitch**.

The flat isolated model prints on its broad side. The optional upright model adds four sacrificial 0.50 mm webs with 45-degree growth ramps and a 2.70 mm transverse roof bridge. All webs must be cut away and trimmed flush before installation.

The design has verified rigid-body insertion/removal geometry and generic slicing evidence. It has **no physical fit or load qualification**. Do not describe it as tested strong, zero-rattle, snap-locked, universal, or equally strong in both orientations.

## User priorities

- Reusable and parametric; easy to integrate into many mounts.
- Strong FDM load path, smooth insertion and removal, limited seated movement.
- A full motion study, with actual movement shown clearly.
- Common Home Depot/Lowe's hardboard as the practical default.
- Functional visual polish and concise engineering documentation.
- Preserve every meaningful design decision and current usable artifact in GitHub.

The user asked whether the result was “strong and smart and nice” and then asked how to make it as FDM-friendly as possible. The response should distinguish good geometry from proven physical strength. The current detailed sources make that distinction explicitly.

## Coordinate contract

All geometry uses millimeters. X crosses the board horizontally, Y points toward the user, and Z points up. The board front is Y=0; the rear is Y=-board_thickness. Hole centers are X=0 at Z=0 and Z=-pitch. The default profile spans X=-2 to +2 mm. The fusion face is Y=4.5 mm; overlap a host by at least 0.3 mm for a reliable union.

The convenient CAD origin is not the physical seated pose. The final bearing pose is **Y=-0.15 mm, Z=-0.12 mm, rotation=0 degrees**. Apply the same transform to the attached host when inspecting its installed assembly.

Replicate columns horizontally at integer multiples of 25.4 mm and the same height. A second vertically spaced retaining hook is not automatically compatible with the verified threading motion. The host and surrounding obstacles need their own swept-envelope check.

## Source ownership and outputs

| Files | Role |
|---|---|
| `motion_design.py` | Canonical planar geometry, parameters, motion search, continuous certificates, fit/rock metrics |
| `anchor.py` | CadQuery solids and functional STEP/STL exports |
| `write_scad.py`, `pegboard_anchor.scad` | Alternate OpenSCAD source generation/module |
| `parameters.json` | Parameter snapshot; not an automatically loaded configuration |
| `geometry.json`, `motion_results.json` | Generated profiles and full motion evidence |
| `verify_cad.py`, `cad_validation.json`, `occ_motion_check.json` | CAD/mesh and independent 3D sampled interference evidence |
| `upright_supports_design.py` | Parametric sacrificial-web profiles and geometric layer-growth checks |
| `print_scaffold.py` | Supported upright CAD exports |
| `upright_supports_geometry.json`, `upright_supports_variant_checks.json`, `upright_cad_validation.json` | Support geometry and verification |
| `write_print_3mf.py`, `Pegboard_Print_Options.3mf`, `print_3mf_validation.json` | Geometry-only two-option 3MF and validation |
| `slicer_check.json`, `SLICER_CHECK.md` | Exact generic Cura setup, STL hashes, and path evidence |
| `render_study.py`, `render_print_options.py`, `visuals/` | Figures and insertion/removal animation |
| `write_reference_readme.py` | Earlier README generator; inspect before using because hand-edited publication text may supersede its output |
| `requirements.txt`, `release_manifest.json` | Dependency list and release inventory; inspect/update inventory when publishing added files |

STEP imports are solid geometry, not native Onshape/Fusion feature trees. The procedural sources provide the parameters. OpenSCAD syntax was inspected, but an OpenSCAD compiler was unavailable in this build; do not claim an OpenSCAD compile check. Its circle tessellation differs slightly from the canonical polygonal profile.

## Primary user-facing files

- `cad/anchor_default_3p94mm.step`: bare functional anchor in CAD coordinates.
- `cad/anchor_default_3p94mm.stl`: bare anchor already laid flat on its side.
- `cad/anchor_upright_supported.step`: same interface plus fused cutting webs in CAD coordinates.
- `cad/anchor_upright_supported.stl`: supported upright coupon shifted to the bed.
- `cad/upright_cutaway_reference.step`: retained and sacrificial geometry distinguished for inspection.
- `cad/two_column_example.step`: host-integration example; complete host orientation remains the user's decision.
- `Pegboard_Print_Options.3mf`: both printable options, geometry only.
- `visuals/insertion-removal.gif`: actual verified pose sequence.
- `visuals/anchor-summary.png`, `visuals/anchor-drawing.png`, `visuals/print-options.png`, `visuals/upright-actual-toolpaths.png`: geometry, dimensions, print choices, and actual generic paths.

## Facts to preserve

| Item | Current value / result |
|---|---|
| Width × neck height | 4.0 × 3.6 mm |
| Neck area / section modulus | 14.4 mm² / 8.64 mm³; geometry only |
| Tongue run / rise | 5.0 / 3.0 mm |
| Lower locator projection / height | 2.3 / 3.0 mm |
| Default motion | 19.25 degrees maximum tilt; 0.82 mm maximum lift |
| Default rear swept projection | 5.55 mm behind the board |
| Default seated movement to imposed-motion contact | 0.47 mm straight pull; about 0.282 mm straight lift; about 0.687 degrees outward rocking |
| Free-threading allowance | 0.10 mm per effective bore half-height; not a blanket printer tolerance |
| Presets with continuous motion pass | 3.94, 4.19, 4.7625, and 6.35 mm thickness with 6.35 mm holes; 3.94 mm thickness with 7.14375 mm holes |
| Earlier loose candidate | About 2.12 mm pull and 3.02 degrees rocking; superseded |
| Flat print review | 0.4 mm nozzle, 0.2 mm layers, five walls, automatic supports off |
| Upright print review | Same nozzle/layers, two walls, 100% line infill, four 0.50 mm membranes, 6 mm coupon brim, automatic supports off |

The source documents explain the continuous sweep certificate and the separate exact final seating sweep. The OpenCascade evidence is sampled. Do not swap those descriptions.

## The slicing lesson that must not be lost

**Do not transfer the flat version's five-wall setting blindly to the upright version.** The initial upright trial filled the narrow roofs with nested perimeter loops. The successful generic Cura review used two walls and solid line infill, with bridge settings that produced X-directed roof paths between the paired membranes. A local modifier can apply those settings to an anchor integrated into a larger host.

CuraEngine 5.0.0 retained all four membranes. The review found no wholly detached deposition components under its documented component test. It did not establish sag, thermal behavior, bond strength, support-removal quality, or machine-specific safety. Generated generic G-code is not part of the package and must not be passed to a printer.

The user should choose their own printer/filament profile and inspect the final host in Bambu Studio, OrcaSlicer, or their actual slicer. The geometry-only 3MF does not carry such a profile.

## Known weaknesses and unimplemented concepts

- The small neck, host lever arm, printed material, and hardboard breakout/crushing can govern strength.
- The rectangular neck's lower outside edges concentrate initial bore contact.
- Abrupt root shoulders remain. Adding material at a bore-limited contact can break installation; a radius needs design work and renewed motion validation.
- First-layer relief was proposed but has not been incorporated into the functional interface.
- A separately captured cartridge would preserve side-print strength for hosts that need another orientation. No cartridge connection has been designed or delivered yet.
- A curved bearing cross-section was proposed, not implemented; it would need a revised 3D/slice verification approach.
- Easy/snug coupons exist, but no physical trial has calibrated their feel or declared any one setting universally correct.
- Upright sacrificial webs solve deposition support, not the weaker orientation of the structural layer bonds.

## Best next work after publication

1. Print the flat fit coupon on the user's actual printer and board. Measure board thickness and several hole diameters first.
2. Print and trim the upright coupon; inspect the final surfaces and compare installation feel.
3. Test a representative holder and load lever arm. Compare the two print orientations rather than assuming equivalence.
4. Tune fit only from the actual trial. Change independent parameters, not the scale of the entire model.
5. Address a measured weakness: root shape, bore bearing, elephant foot, support-removal quality, or host attachment.
6. Regenerate affected geometry and verification after a geometry change, and keep the exported current prototype obvious in the repository.

Do not rebuild the entire project merely to restate the existing evidence. Broaden checks only for a concrete remaining risk or a changed interface.

## Reproduction notes

The source documents contain the runnable build steps. The functional chain starts with `python motion_design.py`, followed by `python anchor.py`; the upright chain uses `python print_scaffold.py` and `python write_print_3mf.py`. Renderers regenerate figures. The generic slicer check uses the exact settings and package identifiers in `slicer_check.json` and the reproduction script in `SLICER_CHECK.md`.

Inspect `write_reference_readme.py` before running it after publication: an earlier generator can overwrite the richer release README. Likewise, validate that `release_manifest.json` covers newly added documents and current exports rather than treating an older manifest as authoritative.

When publishing, include project sources, docs, CAD/STLs, 3MF, animations, diagrams, and JSON evidence. Keep generated Python caches and generic review-only G-code out of the user-facing release. Verify the final repository links and commit after the publishing operation.
