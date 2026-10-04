# Open spool storage cradle v14

**Reviewable geometry prototype, not a qualified print release.** This implements the
operator's corrected storage use: take the spool to the bench, then return it to an open
curved-bottom tub. There is no lid, axle, latch, spring, wire guide or feeding function.
The earlier [v13 gated mechanism](../spool-front-v13/SUPERSEDED.md) is superseded;
its final records remain unchanged.

## Current facts and design

The photographed cyan part is consistent with the two-column braid v12 cradle, rather
than the reel-thin holder. See the owner's [physical record](../../spool-physical-2026-10-03/).
The MAIYUM label specifies Sn63/Pb37, 1.8% flux and 100 g solder. Approximately 55 mm OD
and 30 mm overall width are product-family estimates, **not measured dimensions**;
100 g is not a measured total spool mass. The braid's original 38–52 OD × 6–12 width
coverage does not qualify this wider solder spool.

The new provisional coverage is **40–65 mm OD × 8–34 mm overall width**, including
40 × 8 and 40 × 12 narrow bobbins. It is a roomy bench-spool cradle, not a fitted seat.
Spool axis is X, away from the board is +Y, up is +Z. No required bore size is imposed:
all interference evidence uses conservative solid full-OD cylinders. Flanges, bore and
winding shapes in the white render stand-ins are illustrative only.

The two mounting columns remain X = ±12.7 mm, with hook row 0 and hoop row 1,
PF02#9/PF07#5 geometry and 48.8 mm body width. The generator calls the unchanged
shared receiver. Its board-side geometry below Y = 0.15 has zero symmetric-difference
volume against that receiver. This preserves the geometry, not a new physical fit rating.

Print face was selected first: right cheek (installed −X) on the bed, keeping the existing
hoop orientation. A radius-34 mm curved floor spans ±35° about its low point. Its shell
is 3.6 mm thick, with a 5 mm rear support, a left cheek, shallow side rims and two local
mounting-rail flanges. Two backplate windows remain open. There is no need for a solid
sheet behind the payload to claim the module's exterior perimeter.

The bottom is Z = −68 mm. The front floor rises **6.15 mm** from that bottom. Round
spools with radius below 34 mm settle into a local gravitational minimum. This gives
passive engagement: a horizontal outward slide hits the curved rise. It is not a latch
and has no rated bump acceleration, retention force or drop resistance. Smaller spools
sit lower in the same trough. Narrow bobbins can lean sideways and have less tipping
margin; their static seat checks do not establish bump stability.

## Removal and occupied board space

The checked path is **8 mm vertically up, then 65 mm straight out (+Y)**, reversed for
return. It needs no X translation, spool rotation or separate release action. The open
top permits a direct grasp; the user's hand and fingers need additional space beyond
the spool envelope. No hand-clearance or one-handed ergonomic qualification is claimed.

| Quantity | Final candidate |
| --- | --- |
| Body X | −24.4 to +24.4 mm |
| Body Z | −71.6 to +5.445 mm, including pegs |
| Body Y | −10.79 to +61.6 mm, including pegs |
| 65 × 34 spool top, seated → lifted | Z −3 → +5 mm |
| 55 × 30 spool top, seated → lifted | Z −13 → −5 mm |
| 40 mm spool top, seated → lifted | Z −28 → −20 mm |
| Largest loaded front | Y 72.5 mm |
| Nominal loaded front | Y 67.5 mm |
| Permanent growth versus braid body | 34.09 mm down, 6.46 mm forward, zero sideways |
| Solid CAD volume | 29.167 cm³ |
| Solid ASA mass estimate, 1.07 g/cm³ | 31.21 g; not sliced filament use |

The tub was lowered 8 mm while keeping the mount in place, so the largest lifted spool
stays below the existing flat plate top Z = 5.12. The permanent downward growth pays for
this lift allowance. The checked spool sweep requires **zero additional X/Z area outside
the installed occupied exterior perimeter**, not merely outside a rectangular bounding box.
`projected-outlines.json` contains the actual triangulated material projection, its exterior
perimeter, installed payload projection, continuous sweep projection and their difference.
Only enclosed internal holes are filled for the perimeter comparison; no convex hull is
substituted. [The footprint diagram](footprint-lift.png) shows the material and sweep.

The nominal and largest payloads project forward beyond the body's Y61.6 front edge;
this is explicitly included above. In X/Z their projections lie within the module's
exterior perimeter, although windows and open spaces have no material behind them.
The photographed solder spool already appears to extend below the old braid body;
its actual installed envelope has not been measured. The growth figures compare bodies,
not two measured loaded installations. The full body projection occupies 48.8 × 77.045 mm
in bounding dimensions, with the actual nonrectangular outline supplied separately.

Compared with v13, v14 is **51.2% lower in solid volume and 18.4 mm less deep**, but its
bottom is 1.1 mm lower. Compared with the original 16.466 cm³ braid, it uses about 77%
more solid volume. It is a simpler, shallower mechanism, not smaller in every dimension.

## Evidence and limits

The final generator asserts one valid CAD solid and unchanged board-side receiver geometry.
All five cases (40×8, 40×12, 40×20, 55×30, 65×34) have zero CAD common volume at rest,
through the **continuous** 8 mm lift swept solid, and through the continuous 65 mm outward
swept solid. A direct outward sweep without lifting collides in all five cases, confirming
the curved rise is real. Smaller diameter cylinders tangent to the same bottom and of
no greater width are contained by the largest conservative envelope. This covers ideal
round cylinders within the declared range, not arbitrary protruding labels or bent rims.

The shared mesh/pose/gravity/removal report is separate evidence: one watertight body,
pose matrix mapping, overhang/island screening, contacts and convex-hull centre of mass
over the contact region. Its removal samples are at intervals no larger than 2 mm and
allow the shared −0.15 mm clash threshold. They must not be called a continuous motion
certificate or physical test. The generator's solid sweep checks supply the continuous
collision evidence for this particular ideal payload and path.

All final shared geometry flags pass: one watertight body, 0.0000 mm pose-bound error,
zero non-peg overhang features, zero island features, and fit/seat/removal passes for
all five cases. Flagged peg overhang area is 132.2 mm² and remains exempt. The largest
mesh proxy reports 0.002 mm penetration at rest from tessellation; its exact CAD full
cylinder has zero common volume. `storage-review.json` independently reports zero
outside-perimeter sweep area for every case and exits nonzero on a failed shared or
containment check.

The final fixed-body linear-static screen uses the existing Gmsh/CalculiX runtime:
solid isotropic ASA E = 1800 MPa, Poisson ratio 0.35; nodes at Y < 0.10 fixed; 2 mm
quadratic tetrahedra; 48,634 nodes and 26,665 elements. Each 5 N load is distributed near
[16, 59.6, −63] mm with radius 3 mm. There is **no spring simulation**.

| Load | Displacement at load | Maximum displacement | Brief target |
| --- | --- | --- | --- |
| 5 N sideways | 0.2629 mm | 0.3402 mm | ≤1.0 mm: passes this screen |
| 5 N downward | 0.5772 mm | 0.6704 mm | ≤0.5 mm: **misses target** |

The rear support was locally thickened from 3.2 to 5 mm after a 0.6995 mm downward
screen, reducing that deflection without enlarging the exterior outline. The remaining
miss is retained as a prototype limitation. There is no infill, layer anisotropy, contact,
impact, fatigue, stress/strength or mesh-convergence qualification. A 5 N stiffness case
is not a payload capacity or a measured retention load. The lower loads expected from
storage do not convert this target miss into a pass.

Print-pose geometry is approximately 77.05 × 72.39 × 48.8 mm and fits the machine's
bed geometrically. Pegs are exempt from the shared overhang screen and need appropriate
print preparation. Passing the non-peg surface screen is not a sliced support result.
No toolpaths, printer commands or physical v14 print were produced. The changed body
has not received a new whole-module board installation-arc check; unchanged pegs alone
do not establish that clearance. ASA warp, hole fit, support removal and physical stiffness
remain to be qualified. Old nominal-anchor certificates are not transferred to this body.

The final loaded, empty, narrow, print and motion/perimeter images were inspected.
Triangle-level depth sorting keeps the spool visible with correct occlusion. The open
top and front are accessible in the nominal view; the narrow-bobbin view makes the
unused lateral room and potential lean apparent. The print view shows the unsupported
pegs and the pointed window ceilings. These are CAD visual assessments, not hand-use
or printed-surface observations.

## Next decisions

1. Measure actual spool maximum OD, overall flange width, rim shape and total mass;
   check the smallest purchased bobbin as well as the MAIYUM spool.
2. Confirm space down to Z−71.6 at the intended mount and room for fingers. Inspect
   [empty](empty.png), [loaded](loaded.png), [narrow](narrow-loaded.png) and
   [up/out](up-out-path.png) views; narrow bobbins may lean in this intentionally roomy tub.
3. Review the downward stiffness miss and new installation arc before print preparation.
   Use an actual ASA print to assess grip access, repeatable seating, tilt and modest bumps;
   do not infer these from static CAD or FEA.

## Reproduction and provenance

Sources are `bench/source/solder_v12/spool_storage_v14*.py`. Shared geometry sources are
unchanged. The render helper reuses only triangle-depth-buffer routines from the frozen
v13 `spool_front_render.py`, not its mechanism geometry. Final input and output hashes,
baseline commit and selected deliverables are recorded in `BUILD.json`; solver-binary
hashes are in `fea-provenance.json`. Run from the repository root with the existing runtimes:

```sh
timeout 180s flatpak run --env=PYTHONPATH=/app/freecad/lib --command=python3 org.freecad.FreeCAD -B "$PWD/bench/source/solder_v12/spool_storage_v14.py" "$PWD/bench/reviews/v12-build/spool-storage-v14"
timeout 240s /home/repro/venvs/physics/bin/python -B bench/source/solder_v12/checks.py bench/reviews/v12-build/spool-storage-v14 part-solder-spool-storage__v14__right-cheek__fit-pf02c9-hoop5
timeout 600s flatpak run --env=PYTHONPATH=/app/freecad/lib --command=python3 org.freecad.FreeCAD -B "$PWD/bench/source/solder_v12/spool_storage_v14_fea.py" "$PWD/bench/reviews/v12-build/spool-storage-v14"
timeout 90s /home/repro/venvs/physics/bin/python -B bench/source/solder_v12/spool_storage_v14_review.py bench/reviews/v12-build/spool-storage-v14
timeout 240s env MPLCONFIGDIR=/tmp/peg-spool-mpl python3 -B bench/source/solder_v12/spool_storage_v14_render.py bench/reviews/v12-build/spool-storage-v14
```

These are provenance/reproduction commands, not permission to overwrite frozen review
evidence later. Use a new output directory for further revisions and keep dependent
reports/renders together. FreeCAD 1.1.3 / OpenCascade 7.8.1 supplied the CAD build.
