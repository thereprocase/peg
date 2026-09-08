# Host attachment envelope

Use a **5.00 mm nominal flush lip above the upper hole center**. Its rear edge is sharp and planar against the board, with **0 mm board-facing corner radius** and no modeled recess at the seam. This is the permitted nominal height of a flush back above the hole, not a limit on the overall height of the attached part.

Above the lip, draw any host shape that remains inside the supplied allowed volume. A taller part can step or slope forward, or place the upper peg closer to its own top. All added host material, including ribs and fasteners, must satisfy the envelope; checking only the top corner is insufficient.

![Allowed host envelope for the current anchor](visuals/conformal-host-envelope.png)

## Files for downstream CAD

- [Current functional anchor STEP](cad/conformal/conformal_120.step)
- [Current allowed host volume STEP](cad/conformal/host-envelope/allowed_host_volume.step)
- [Envelope dimensions, boundary and continuous certificate](cad/conformal/host-envelope/allowed_host_volume.json)
- [Exact geometric height/setback calculations](cad/conformal/host_envelope.json)
- [Envelope generator](export_host_envelope.py)

Import the allowed volume in the same **design coordinates** as the functional anchor. It is reference geometry, not a part to print or fuse. The **added host** must fit inside it; the anchor's pegs intentionally extend outside it. Fuse the host into the anchor's front spine with real overlap at its front face, **design Y = 4.50 mm**. About 0.3 mm overlap is a useful Boolean construction starting point, not a strength specification.

The envelope follows every continuously interpolated pose in the identified motion study. It keeps the complete host in front of the board plane for any horizontal width. The exported reference volume is clipped to **X = -50 to +50 mm**, installed height **-80 to +100 mm**, and front projection **60 mm**. These are export bounds, not physical size limits; regenerate larger bounds as needed.

## Coordinates

All dimensions are millimeters. X is horizontal, Y points toward the user, and Z points up. The board front is Y = 0, its rear is Y = -3.94 mm, and the installed hole centers are Z = 0 and Z = -25.4 mm.

The supplied movement seats the anchor with translation **Y = -0.15 mm, Z = -0.12 mm**, at zero rotation. Consequently, the **5.00 mm installed lip is at design Z = 5.12 mm**, and its board-facing rear plane is **design Y = 0.15 mm**. Apply the same rigid transform to the complete anchor and attached host when inspecting the installed assembly.

For a pose rotating by angle theta about X, the board-front condition is:

```text
cos(theta) * design_Y - sin(theta) * design_Z + pose.y >= 0
```

The envelope takes the most restrictive condition across the entire motion, not only the installed and most-tilted positions.

## Exact limit versus nominal interface

The exact movement-dependent flush ceiling is **6.08635 mm above the upper hole center**, recorded in `geometric_flush_height_limit_mm` in the [allowed-volume JSON](cad/conformal/host-envelope/allowed_host_volume.json). It is a limiting geometric contact height. The delivered interface deliberately uses the agreed **5.00 mm nominal maximum flush height**, with a setback above it.

The generator shifts the theoretical envelope downward by the difference between that exact ceiling and the nominal lip. Its setbacks are therefore slightly larger than the unshifted theoretical values in `host_envelope.json`. Use the delivered allowed volume when designing an attached part, rather than treating the theoretical ceiling as an alternate lip specification.

The setback boundary is a convex function of height. Joining exact boundary values with straight chords produces a conservative CAD outline. The exported polygon also receives an independent continuous check against the full board front plane. Its certificate and source hashes are stored beside the STEP.

```python
import cadquery as cq

allowed = cq.importers.importStep(
    'cad/conformal/host-envelope/allowed_host_volume.step'
)
# `host` contains only the added part, before fusing the functional anchor.
outside = host.cut(allowed)
assert sum(s.Volume() for s in outside.solids().vals()) < 1e-6
```

This example tests containment within the supplied finite export. A larger part may need a regenerated envelope with wider or taller bounds before its containment check is meaningful.

## Regenerate when geometry or movement changes

```text
python host_envelope.py --motion cad/conformal/conformal_motion_results.json --output cad/conformal/host_envelope.json
python export_host_envelope.py --motion cad/conformal/conformal_motion_results.json --output cad/conformal/host-envelope --nominal-lip 5
```

To export a wider or taller reference, add `--width`, `--minimum-height`, `--maximum-height` and `--front-limit` as needed. Dimensions are in millimeters; installed heights are relative to the upper hole center.

Every export identifies and hashes its source motion. A changed peg, locator, board thickness, hole diameter or insertion path needs corresponding motion evidence and a regenerated envelope. A host certificate alone does not validate a modified peg's insertion. The [previous round envelope](cad/host-envelope/allowed_host_volume.step) belongs to the earlier [round release](ROUND_README.md), with its own geometry and path.

The current envelope covers board clearance. It does not establish host strength, printing, neighboring-holder clearance, rear-wall space or access for hands. Matching the modeled sharp face and nominal bore requires physical fit checks on the intended board and printer.
