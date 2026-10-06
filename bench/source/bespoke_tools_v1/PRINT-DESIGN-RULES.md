# Bespoke holder print and use rules

Review date: 2026-10-05. Owner priority: easy FDM quality.

## Sources and precedence

Read the repository's AGENTS.md, BENCH_HOLDERS.md, current connector integration notes,
publication/README.md, and the frozen solder_v12/BRIEF.md. Also reviewed the active
peg-bt2 workbench's bench/README.md, recovery/handoff records, tool-source notes,
module reviews, physical feedback and current funnel/tweezer/spool design notes.
The workshop human-factors report, screwdriver revisions, sampler and magnetic-pocket
notes, and current-mount per-part orientation records supply specific precedents.
PRINTING_OPTIONS.md, SLICER_CHECK.md and ROUND_SLICER_CHECK.md describe historical
anchor preparations; their support geometry and qualification apply to those exports.

BENCH_HOLDERS.md now permits a flat bottom, inverted flat top or right cheek, with
accessible local supports and actual toolpath inspection. The older v12 brief requires
body geometry that supports itself, with organic supports at the pegs. New designs
use that stricter body-geometry target to serve the owner's easy-FDM request.

## Design gates

1. Choose a substantial planar bed face before the holder body. Respect ASA warp,
   first-layer contact, print height and the 256 mm bed including brim/supports.
2. Body geometry grows from the bed. Downward faces stay within 45 degrees from
   vertical; pointed roofs use at least 50 degrees. Horizontal overhangs need material
   beneath them. Declared bridges require real end anchors, backing, and span <=10 mm.
   Check local starting islands as well as face angles.
3. Peg supports must be accessible for removal. Check the actual owner's ASA slice,
   including support contact, bridge direction, hoop paths and seam buildup.
4. Flexing hoops and any added clips flex in the layers. Use the correct existing hoop
   orientation for each pose. Preserve the PF02 #9 hook and PF07 #5 root-clipped hoop.
5. Width is 25.4*cells-2 mm; use two mounting columns where they fit. Integral peg roots
   overlap the receiver. Preserve the rear contact plane and board-side geometry.
   Each complete body needs its own installation screen; old nominal certificates
   cannot qualify the changed fit.
6. Use webs, flanges and triangulation for stiffness. At the farthest tool-bearing
   point with peg nodes fixed, target <=1.0 mm sideways and <=0.5 mm down under 5 N.
   Report assumptions for solid isotropic ASA and the limits of printed infill.
7. Walk through hold, grasp, removal, return and incidental bumps. Provide forgiving
   entry, positive gravity retention, clear grip space and short one-handed motion.
   Check neighboring stored tools and the complete swept tool, including its tips.
8. Protect exposed points. Keep refill and cleaning access practical. Blind seats are
   required for glue-in parts. Simplicity and access take priority over material saving.
9. Source real common tool dimensions. Keep manufacturer data, downloaded CAD,
   reconstructed engineering surfaces and conservative fit envelopes explicitly labeled.
   The owner does not measure tools. Preserve existing owner-specific barrel seats.
10. Use consistent edge finishing that preserves the bed face and printable undersides.
    Verify native solids, round trips, meshes, orientation, tool fit and paths; inspect
    rendered installed, loaded and print views. Record volume, bed contact, stiffness,
    slice time/material/support and remaining physical checks with the matching source.

## Candidate decisions

- HX01: upright floor. Long key legs point upward; short feet sit on a floor between
  open-front guides. A 9 mm lift clears the front lip. Check slender-key lean and grasp.
- TM01: upright floor and side webs; low front lip. The 94 mm pocket accommodates
  a tape-measure case plus clip up to 92x48 mm. Check grip and short pickup.
  The owner stores the multimeter flat elsewhere; a display cradle is excluded.
- CL01: full right-cheek section on the bed. A broad saddle supports a coiled cable
  bundle and a raised nose retains it. Check grip, saddle contact and coil clearance.

CAD checks, linear stiffness, sliced toolpaths and physical print/use results are
separate evidence. Physical tests remain pending until performed.
