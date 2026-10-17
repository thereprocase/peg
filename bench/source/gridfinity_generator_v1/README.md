# Configurable Gridfinity pegboard shelves

This generator extends the reviewed 1×1 and 2×1 shelves to rectangular arrays.
The board-contact plane stays vertical at Y=0.15. PF02 #9 hooks, PF07 #5 upright
hoops, their joining nubs and 25.4 mm vertical pitch remain fixed. The seats and
braces accommodate the selected tilt. All exports put the frame face down.

## Parameters

| JSON key | Default | Range / meaning |
|---|---:|---|
| columns | 2 | 1–12 cells across the board |
| rows | 1 | 1–12 cells out from the board; at most 64 total cells |
| clearance | 0 | −0.10 to +0.20 mm additional receiver clearance per side |
| web | 2.4 | 2.4–6 mm side web thickness |
| beam | 10 | 5–20 mm front beam depth |
| mount_rows | 2 | 1–4 peg rows vertically; one row has hooks only |
| backplate | true | Solid 5.4 mm plate; false retains posts and cross-ties |
| angle | 0 | −30° downward to +5° upward; 0° is horizontal |

Gridfinity pitch is 42 mm. Board lanes use 25.4 mm pitch and a 2 mm total side
gap. Wider arrays gain mounting columns with no more than 76.2 mm between them.
The rear rail ends at the frame width (42 × columns + 4 mm); it no longer extends to the occupied board-lane width. Outer mounting columns move inward by whole board pitches where needed to keep their complete 10 mm posts inside the frame. Each web reaches the front beam outer face with a vertical connection, rather than ending short in a point.

The full 5.4 mm material around each joining nub is protected. Tilt raises the
seat hinge when necessary to retain the root wall and keep the hook crown below
the inverted bed plane. The fixed board-facing root blocks are not tilted.

A positive clearance loosens the receiver. Negative clearance deliberately
allows reference-foot interference at the original seat height: the bin may sit
proud, and this is reported. No tuning value changes the peg fit.

## Native generation

Run from a complete checkout of the peg repository with an existing FreeCAD
Python runtime that can import `FreeCAD`, `Part` and `MeshPart`:

```sh
python bench/source/gridfinity_generator_v1/generate.py output --config recipe.json
```

Omit `--config` for defaults. The JSON file contains only the eight keys above.
Output includes `shelf-print.step`, `shelf-print.stl`, `shelf-print.FCStd`,
`shelf-installed.step`, exact connector meshes and `CHECKS.json`.

The native source uses the repository's current connector builder and frozen
station snapshot through relative paths. Keep that source tree intact.
Generated STEP is reopened and compared by native symmetric volume difference.
Each complete shelf must be one valid solid. Checks protect the board-side peg
geometry, root material and nonnegative-clearance reference feet.

The 0.005 mm / 0.087 rad tessellation settings matter: coarser trials in the
original shelf study left open hook seams. Validate the saved mesh before using
it; native solid validity alone does not prove mesh closure.

## Scope and printing

Generated variants are prototypes. The earlier reviewed 1×1 and 2×1 files remain
unchanged under the original review. Generalization uses a continuous front beam;
not every generated 2×1 file is byte-identical to that frozen release.

Print the seat-fit ring first, then check a small shelf on the intended board.
Review first-layer contact and peg overhangs in the actual slicer. Tilted and deep
arrays have not inherited the original ASA slice check. A bounding box inside
256 × 256 mm does not account for the printer's exclusion area or purge space.

No load rating is assigned. More depth increases the moment at the board.
Friction, snap recovery, straight-up and forward bin removal, printing anisotropy,
creep and loaded installation remain physical checks. The original nominal
host-envelope containment screen is retained; it is not a motion proof for the
current interference-fit connectors or every completed array.

## Continuous frame revision

The outer frame is a single outline with straight rear/side joins and R5 tangent
front corners. Cell pockets are subtracted from that outline, so cell seams do
not create V-notches outside. The front beam and webs share the same outer trim.
Seat profiles, internal ribs and fixed connectors retain their existing datums.

The native checks include the front beam core between outer mounting columns
and 13 lift positions per cell for nonnegative clearance. The checked core
thickness is min(1.9, 2.05 − clearance) mm, accounting for the 1.85 mm top rim at
maximum +0.20 clearance. These are digital geometry checks, not a load rating.

## Backplate and independent grids

The default is a solid 5.4 mm backplate and two mounting rows. Gussets are at every Gridfinity cell boundary, 42 mm apart. Peg columns retain the 25.4 mm board grid. The backplate transfers load between these independent layouts. Turning the plate off retains a bottom cross-tie and posts at both grids.

One mounting row uses hooks only, with a backplate extending 12.7 mm below the hook centers. Two rows use top hooks and bottom locking hoops. Three and four rows add exact repository bearing locators between them; the lower hoop sits 50.8 or 76.2 mm below the top hook. Gussets extend down with the mounting plate. Added height is not a load rating. One-row mounting lacks the lower snap retention; taller arrays require a fresh installation trial.

The finite host-envelope lower export boundary is extended vertically to Z −200 mm, retaining its constant Y=0.15 lower boundary. This is a board-front containment screen; the original nominal two-peg motion certificate is not extended to these interference-fit arrays.
