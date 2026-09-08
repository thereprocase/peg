# Current project handoff

The user requested a modular parametric FDM pegboard anchor, common US board presets, a full motion study, side and upright printing, clear visuals, and preservation of all work in [thereprocase/peg](https://github.com/thereprocase/peg). They then rejected the rectangular bearing corners and explicitly required **round pegs**. The current canonical design is round.

Read [README.md](README.md), [ROUND_MOTION_STUDY.md](ROUND_MOTION_STUDY.md), [ROUND_SLICER_CHECK.md](ROUND_SLICER_CHECK.md), and [DESIGN_HISTORY.md](DESIGN_HISTORY.md). The [baseline guide](BASELINE_README.md) and [baseline handoff](BASELINE_HANDOFF.md) preserve the earlier rectangular model and decisions. Do not use baseline motion or support claims for the round version.

## Current geometry and files

Default: actual board thickness **3.94 mm**, minimum hole diameter **6.35 mm**, pitch **25.4 mm**, bearing peg/locator diameter **5.6 mm**, tongue diameter **4.8 mm**, spine width **6 mm**. All units are millimeters. X crosses the board, Y faces the user, Z points up. Board front is Y=0. Fuse hosts at the Y=4.5 mm front face with real overlap. The exact seated pose translates Y=-0.15 mm and Z=-0.12 mm, with zero rotation.

The upper solid is the union of a 2.8 mm-radius circular capsule and a 2.4 mm-radius circular capsule, preserving the large spherical junction. The lower locator is a circular cylinder with a 0.5 mm axial nose chamfer. Neither bearing surface is flattened. The rounded rear end of the neck means the full nominal diameter does not bear through the entire board thickness; do not claim full-cylinder contact over the complete board thickness.

Use `Round_Print_Options.3mf`, `cad/round_side_supported.stl`, and `cad/round_upright_supported.stl` for the current default print preparations. Use `cad/round.step` for host integration. Bare STLs are explicitly named `*_unsupported.stl`; provide appropriate supports when using them. `cad/round_design_reference.stl` retains design coordinates for rendering. `cad/round_two_column_example.step` demonstrates the front bridge and horizontal replication.

## Canonical sources and evidence

| File | Ownership / purpose |
|---|---|
| `round_anchor.py` | Exact CAD primitives, resolved geometry contract, defaults, tested preset combinations, STEP/STL exports, `round_pair()` |
| `cad/round_geometry.json` | Frozen default primitive contract and parameters |
| `round_motion.py` | Three-dimensional conservative collision bounds, bounded search, continuous segment certification, exact seating certificate |
| `round_motion_results.json`, `round_motion_presets.json` | Default and all five certified presets, poses, summaries, proof records |
| `ROUND_MOTION_STUDY.md`, `round_distance_crosscheck.json` | Method, rejected candidates, assumptions, independent distance comparison |
| `round_verify_cad.py`, `round_occ_motion_check.json`, `round_pair_occ_motion_check.json` | Actual STEP interference and rocking-stop checks |
| `round_cad_presets_validation.json`, `cad/*_cad_validation.json` | Valid BReps and watertight positive-volume meshes |
| `round_print_supports.py`, `cad/round_support_validation.json` | Removable conformal supports, pad/lift, gap and web parameters |
| `ROUND_SLICER_CHECK.md`, `round_slicer_check.json`, `*_toolpath_evidence.json` | Actual generic Cura toolpaths, exact input hashes, scope and residuals |
| `review_settings/`, `tools/ROUND_REVIEW.md`, `tools/*round_toolpaths.py` | Portable slicing replay and individual-perimeter support screen |
| `write_round_3mf.py`, `round_3mf_validation.json` | Geometry-only 3MF packaging and round-trip validation |
| `render_round.py`, `render_round_common.py`, `render_round_supports.py`, `render_bearing.py` | CAD-derived visuals and certified motion animation |
| `optimize_animation.py` | Shared-palette GIF compression; accepts an explicit image path |

The root `anchor.py`, `motion_design.py`, `pegboard_anchor.scad`, `MOTION_STUDY.md`, `PRINTING_OPTIONS.md`, and `SLICER_CHECK.md` describe the preserved rectangular baseline. Their separate names and history remain useful; the current round entry points are the `round_*` sources and `ROUND_*` reports.

## Results and important distinctions

The default continuous path reaches **20.875° tilt**, **1.07 mm lift**, and **6.62 mm rear swept projection**. Straight pull reaches a retaining stop after **0.47 mm**, lift after **0.282 mm**, and outward rocking reaches the modeled rear shoulder after about **0.675°**. These are geometry limits, not measured insertion force or rattle. The 0.10 mm reserved radial free-motion allowance is separate from the exact final seating contacts.

All five presets pass continuous certificates. Use 5.6 mm bearing pegs for 3.94/4.19 mm stock and the checked 9/32-inch-hole preset, 5.4 mm pegs for 4.7625 mm stock, and 5.2 mm pegs for 6.35 mm stock. All use the 4.8 mm tongue. A bounded search failure for a larger diameter is not proof that every imaginable motion is impossible. Arbitrary combinations remain unverified.

The default has 2,038 dense audit frames. Independent actual-STEP checks cover 80 single and 80 paired-anchor poses with zero overlap; those are sampled checks, separate from the continuous certificate. The rocking check intentionally tests a beyond-stop pose and expects positive overlap there.

The round neck has area 24.63 mm² and section modulus 17.24 mm³. The tongue has area 18.10 mm² and section modulus 10.86 mm³. Both exceed the rectangular baseline's 8.64 mm³ geometric section modulus. No physical load, fatigue, creep, interlayer bond, contact-pressure, or hardboard breakout rating exists.

## Printing lessons that must survive

A uniform round peg needs support beneath its lower quadrant. The final side preparation lifts the functional anchor 0.40 mm and adds a 0.20 mm sacrificial spine pad plus conformal cradles with 0.20 mm vertical interfaces. Keep the four supported STL solids in their supplied relative positions; independently dropping each shell to the bed destroys the design. The side supports contact the side-facing hemisphere, away from the installed lower bearing crown.

Upright cradles seed the circular center underside and sit on nominal 0.50 mm ramp webs. Webs can merge at intersections. Cut their sacrificial roots, lift the cradles away, and preserve the functional circular surfaces. The baseline pair-of-edge-web strategy did not transfer to a round rod.

Generic CuraEngine 5.0.0 review: 0.4 mm nozzle, 0.2 mm layers, 0.45 mm lines, 6 mm brim, automatic supports off. Side uses five walls; upright uses two walls and solid line fill so bridge skin can span the saddle floor. The side support screen has no flagged functional perimeter portions across 32 layers. Upright has 178 layers and a 0.051 mm early spine-edge fringe; no floating rod starts. Those are geometric path checks, not extrusion or strength simulations. Physical support release and surface finish remain to be tried.

Never print the review G-code. It is excluded from the repository. Use the user's machine and filament profile and inspect the actual final holder.

## Reproduction

From the repository root, install `requirements.txt`, then regenerate only what changed:

```bash
python round_anchor.py --all-presets
python round_motion.py
python round_verify_cad.py
python round_verify_cad.py --step cad/round_two_column_example.step --columns 2 --output round_pair_occ_motion_check.json
python round_print_supports.py --geometry cad/round_geometry.json --name round
python write_round_3mf.py
python render_round.py
python render_round_supports.py
python render_bearing.py --diameter 5.6
python optimize_animation.py visuals/round-insertion-removal.gif
```

Each motion search has a 20-second bound; the full five-preset certification takes longer than a single search. For isolated work use `python round_motion.py --default-only` or the custom thickness/hole/peg/tongue CLI options. Keep external tool calls bounded with explicit timeouts and make visible GitHub checkpoints during long tasks, as the user requested.

See `tools/ROUND_REVIEW.md` for exact Cura replay. Source outputs are deterministic geometry; regenerated file container timestamps or tessellation ordering may alter hashes. Stage the intended files, run `python write_manifest.py`, and stage `release_manifest.json` before publication. Check the published commit and content rather than claiming success from a local write.

## Next useful work

Print and trim one default side sample on the actual printer and board. Measure board thickness and several holes. Compare an upright sample, then test a representative holder and lever arm progressively. Adjust fit from evidence. The geometry has not established universal fit, zero play, easy support release on every filament, or a load rating.

A larger bearing neck with a thinner tongue was explored, but reducing the tongue to 4 mm weakened its geometric section modulus. The selected 5.6/4.8 combination balances round bearing, threading, and section size. A tangent-spine side-print experiment and pressure-distribution improvements remain research ideas. Preserve any future geometry change with new relevant motion and printing checks; do not broaden tests merely to restate existing evidence.
