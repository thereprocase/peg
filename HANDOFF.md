# Current project handoff

The current design is the **120-degree conformal anchor** in [README.md](README.md), with a full-thickness lower bearing, sharp 5 mm nominal lip and an importable allowed volume for real attached parts. The user authorized updating and publishing this design, README and all current visuals to `main` on [thereprocase/peg](https://github.com/thereprocase/peg).

Read [CONFORMAL_STUDY.md](CONFORMAL_STUDY.md), [HOST_INTERFACE.md](HOST_INTERFACE.md) and [DESIGN_HISTORY.md](DESIGN_HISTORY.md) before editing. [ROUND_README.md](ROUND_README.md) preserves the previous round release and its print preparation. [BASELINE_README.md](BASELINE_README.md) and [BASELINE_HANDOFF.md](BASELINE_HANDOFF.md) preserve the rectangular baseline. Each generation has separate evidence.

## Current geometry and interface

Default actual board thickness is **3.94 mm**, hole diameter **6.35 mm**, and pitch **25.4 mm**. Both lower bearing arcs have **3.175 mm radius over 120 degrees**. The upper conformal land is **3.158095 mm** long; the lower is **3.94 mm**, with an ordinary **0.50 mm nose beyond the rear board face**, giving **4.44 mm total projection**. The retained upper core and tongue are **5.6 / 4.8 mm** diameter. The spine is **6 mm** wide with a sharp board-facing corner.

The nominal lip is **5 mm above the upper hole center**, not above the peg crown. The board-facing rear face is design **Y = 0.15 mm**, the top is design **Z = 5.12 mm**, and the front fusion face is design **Y = 4.50 mm**. The seated transform is **Y = -0.15 mm, Z = -0.12 mm, rotation = 0 degrees**. X crosses the board, Y faces the user, and Z points up.

All added host material must lie inside `cad/conformal/host-envelope/allowed_host_volume.step` in anchor design coordinates. The anchor itself is excluded from containment. Fuse the host with real shared volume, then apply the same motion to the complete assembly. The envelope is clipped for export; regenerate larger bounds for larger hosts. It checks clearance from the whole board front and takes no credit for holes.

## Sources and outputs

| Source or output | Purpose |
|---|---|
| `conformal_anchor.py` | Current exact CAD, geometry contract and STEP/bare STL exports |
| `round_anchor.py` | Shared round-core primitives and previous round model |
| `check_conformal_geometry.py` | Independent measurement of exported cylindrical bearing faces |
| `conformal_motion.py` | Conservative curved-section bounds, continuous intervals and exact final-contact certificates |
| `verify_conformal.py` | Independent actual-STEP board intersections along sampled paths |
| `cad/conformal/conformal_120*` | Current functional STEP, three bare STL orientations, geometry and CAD/bearing validation |
| `cad/conformal/conformal_motion_results.json` | Current continuous motion certificate and poses |
| `cad/conformal/conformal_motion_check.json` | Independent sampled CAD evidence |
| `host_envelope.py`, `export_host_envelope.py` | Exact movement envelope, conservative allowed-volume export and continuous host check |
| `cad/conformal/host_envelope.json`, `cad/conformal/host-envelope/` | Current theoretical limits, allowed CAD volume and certificate |
| `render_conformal.py`, `render_conformal_media.py` | Current CAD hero, bearing comparison, drawing, movement GIF and envelope visuals |
| `write_manifest.py`, `release_manifest.json` | Publication inventory with hashes |

The current visual set is `visuals/conformal-hero.png`, `conformal-bearing.png/.svg`, `conformal-design-review.png/.svg`, `conformal-motion.gif`, `conformal-motion-envelope.png/.svg` and `conformal-host-envelope.png/.svg`. All current README images must show the current conformal geometry or explicitly labeled comparisons.

## Verification and its limits

The current path reaches **20.875 degrees maximum tilt** and **1.07 mm reference-point lift**. The retained **12-waypoint path** passes without an additional lift adjustment. The certificate covers the complete ideal rigid solid, with **768 X slabs per half** for curved additions, **168 interval certificates across 10 free-motion segments**, and **one exact final-contact translation**. It uses the physical nominal hole and does not retain the previous round design's 0.10 mm radial free-motion allowance.

Independent CAD checking covers **400 current-path samples including seating**, with **0.0 mm3 maximum intersection volume**. Exported STEP bearing-face measurements and watertight positive-volume meshes establish the delivered geometry's shape and validity.

The host's allowed volume has its own continuous board-front certificate tied to the current motion. A changed peg, board or path needs corresponding new motion evidence before inheriting or regenerating a host envelope. The earlier round presets do not certify conformal variants.

No current conformal supports, generic slicing evidence or physical printed sample has been qualified. There is no physical fit, force, fatigue, creep, contact-pressure or load rating. The next useful work is print preparation and a sample on the intended board, followed by a representative integrated-holder trial.

## Reproduction

Use an available compatible Python CAD runtime or `requirements.txt`. CAD validation records the package versions actually used. From the repository root:

```text
python conformal_anchor.py
python check_conformal_geometry.py
python conformal_motion.py --certify --slabs 768 --max-seconds 180
python verify_conformal.py --candidate-poses 400 --max-seconds 600
python host_envelope.py --motion cad/conformal/conformal_motion_results.json --output cad/conformal/host_envelope.json
python export_host_envelope.py --motion cad/conformal/conformal_motion_results.json --output cad/conformal/host-envelope --nominal-lip 5
python render_conformal.py
python render_conformal_media.py
```

Run only the outputs relevant to a change, in dependency order. Keep calls bounded by explicit timeouts. Review generated images and representative animation frames, validate links, stage intended files, run `python write_manifest.py`, and stage the manifest before publication. Check the remote `main` commit and published contents before claiming the push succeeded. Text outputs use UTF-8 and LF newlines; preserve source/evidence hashes after normalization.

## Earlier releases remain available

`Round_Print_Options.3mf`, `cad/round_side_supported.stl`, `cad/round_upright_supported.stl` and `cad/round.step` belong to the **previous 5.6 mm round release**. The 3MF contains geometry only and no machine profile. The [archived round guide](ROUND_README.md), [round motion study](ROUND_MOTION_STUDY.md), [round slicing report](ROUND_SLICER_CHECK.md) and [replay guide](tools/ROUND_REVIEW.md) retain its dimensions, presets and exact checks.

That side preparation uses a 0.40 mm lift, a 0.20 mm sacrificial spine pad and removable cradles with a 0.20 mm interface; keep its disconnected shells together. Upright cradles sit on removable ramp webs. These lessons may inform future conformal support work, but the shapes and slicing results do not transfer automatically. Never print the generic review G-code.

Unprefixed `anchor.py`, `motion_design.py`, `pegboard_anchor.scad`, `MOTION_STUDY.md`, `PRINTING_OPTIONS.md` and `SLICER_CHECK.md` describe the rectangular baseline. Its support-free side-print claim applies to that earlier extrusion. Keep historical labels and evidence intact when advancing the current design.
