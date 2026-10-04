# v12 drip tray + vase liner (rev 2)

Builder: `bench/source/solder_v12/drip_tray.py`. Module name
`part-solder-drip-tray__v12__upright__fit-pf02c9-hoop5`; liner
`part-solder-drip-tray-liner__v12__vase-filled`. 5 cells (125 mm), station origin x 38.1,
z -127, hung under the barrels (`barrels-b6seats`, the final barrels module). Cells, height,
rows and position are unchanged; the `station-layout.json` entry is unchanged.

Rev 2 (2026-10-02), after Frodo's bench review (rev 2):

- A 20 x 3 mm finger scallop in the lip's top centre (finding 2), so the liner comes out
  from the outside of its front wall.
- The tip-height rule is a hard number, -141.6 station z, and the builder asserts it
  against the barrels-b6seats tools (finding 1).
- Spare liners are planned as one vase job of three (finding 3).
- The tray was rebuilt with `common.receiver`'s install-arc hoop fix (root clipped to r 2.95;
  the upright hoop is not dropped).

## Design and why

- **Bed face: the flat floor (upright).** The module is wide and shallow, so the floor is
  the first layer (125 x 80 mm) and every wall rises straight off it. Nothing prints in
  the air but the pegs: hooks on row 0, the PF07 #5 hoop on row 1 (band horizontal, so it
  flexes in X, in the print layers).
- **One open box.** The box has five parts:
  - a 2 mm floor;
  - two 2.4 mm side cheeks that run from the plate's top edge down at 28 deg to a 14 mm
    front post (chamfered top corner);
  - a 4 x 3 mm back curb;
  - a 6 mm front lip, a chamfered beam across the front (60 deg inner face, 3 mm flat top,
    55 deg outer face).

  The cheeks are deep webs that carry the tray's load into the plate beside the peg
  columns. Floor, cheeks, lip and plate make a stiff open box.
- **Finger scallop (rev 2).** A circular arc (r 18.2 mm) cut straight through the lip in Y
  at x 0: 20 mm wide at the lip top, 3 mm deep. Its faces all look up (33 deg from
  horizontal at the edges, flat at the bottom). In the upright print it is the top of a
  wall, so it adds no overhang and no island (checks: 0 non-peg overhang, 0 islands).
  - The lip stays 6 mm tall for 50 mm either side, so the liner's base still bears on
    full-height lip and retention is unchanged.
  - It is at the tray's centre, under the paste nozzle and 37 mm from the flux needle at
    the left end (the barrels review's finding 1: keep the liner grip away from the
    needle).
- **Plate.** Four pointed (55 deg) windows between the peg columns, 17.75 mm wide, sills
  flush with the curb top. No bridges, no flat roofs. The liner hides their lower half.
- **Liner.** A tapered rounded box (8.5 deg draft, corners r 8 at the base, r 11 at the
  rim), 116.2 x 63.45 mm at the rim, 110.2 x 57.45 mm at the base, 20 mm tall, about
  125 cm3 to the brim.
  - It fills the tray from the curb to the lip, so the catch window is as large as the
    module allows.
  - It is located by the curb and the lip at the base (1 mm each) and by the cheeks at the
    rim (2 mm each side, so the return needs no aiming).
  - The curb keeps the rim 2 mm off the plate windows, so the rim can't drop into one.
  - The draft lets spare liners nest. The vase profile is unchanged from rev 1.
- **Why not floor windows:** the floor is the backup catch when the liner is out, and a
  solid floor gives the full first layer. Why not cheek windows: with the cheek top at
  28 deg, any window under it needs a 55 deg roof, and the triangles that fit save about
  1 cm3 per cheek while costing cheek stiffness.

Design iterations (FEA, 5 N down at the lip centre, `pegs` support):

| version | change | lip sag |
|---|---|---|
| first cut | 45 deg cheeks dropping to a 5 mm lip at y 50 | 0.503 mm (fail) |
| deep cheeks | cheek web runs to a 14 mm front post | 0.358 mm |
| variant | lip 5 mm, 3.5 mm top, 55 deg out | 0.329 mm |
| variant | floor 2.4 mm (+3.9 cm3) | 0.294 mm |
| rev 1 | lip 6 mm, 3 mm top, 55 deg out (+1.7 cm3) | 0.261 mm |
| **rev 2** | **20 x 3 mm finger scallop; load moved to the scallop bottom** | **0.343 mm** |

## The tip-height rule (hard numbers; the builder asserts them)

**Every barrel tip must sit above station z -141.6 and inside station x -17.4 .. 93.6,
y 10.2 .. 68.4.**

- The height is the liner rim at -151.0, plus the 6.4 mm removal lift (to -144.6), plus a
  3.0 mm margin.
- The x and y window is the liner's inner rim, less 2 mm for liner play and drip spread.

`drip_tray.py` reads the barrels-b6seats module's own tool STLs and stops the build if a
tip breaks the rule. A lower cup, a longer needle, a taller liner or a thicker floor then
fails at build time instead of at the bench. The numbers are also in `__design.json` under
`tip_rule`.

| tip (barrels-b6seats) | station x, y, z | above -141.6 | above the lifted rim | x / y margin in the window |
|---|---|---|---|---|
| flux needle | 75.09, 55.89, -134.66 | 6.94 | 9.94 | 18.5 / 12.5 |
| paste nozzle | 38.09, 54.05, -120.86 | 20.74 | 23.74 | 55.5 / 14.4 |
| sucker nose | 1.07, 53.07, -116.03 | 25.57 | 28.57 | 18.5 / 15.3 |

Catch window, nominal inner rim (the liner has ±2 mm lateral and ±1 mm fore-aft play):

| | module-local | station |
|---|---|---|
| x | -57.5 .. 57.5 | -19.4 .. 95.6 |
| y (out of the board) | 8.2 .. 70.4 | 8.2 .. 70.4 |
| rim z | -24.0 | -151.0 |

## Covered range

The tray has no tool of its own. It serves the three barrels-b6seats tools, which are the
owner's own, photo-scaled and fixed, so nothing here needs measuring. Along each tool's
10 deg axis, it covers:

- **Flux syringe needle:** up to 7.0 mm longer than the photographed 8 mm needle, so
  about 15 mm overall.
  - A 1/2 in (12.7 mm) blunt dispensing tip fits: its tip lands at about -139.3, 2.3 mm
    above the rule and 5.3 mm above the lifted rim.
  - A 1 in (25.4 mm) tip does not fit. It would reach -151.8, below the rim at rest, and
    sit in the flux. Cut it down. The other fix would be moving the tray down one row,
    which leaves a 27 mm open band under the barrels; the plates either side are
    x-separated, but that move is not built or checked.
- **Paste syringe tip:** up to 21.1 mm longer than the photographed nozzle.
- **Sucker nose:** fixed. It has 25.6 mm in hand.
- **Lateral:** any tip from station x -17.4 to 93.6 and y 10.2 to 68.4. At those length
  limits the 10 deg lean moves the tips forward 1.2 mm (flux) and 3.7 mm (paste), to
  y 57.1 and 57.7, still at least 10 mm inside the window.
- **The liner** is printed for this tray. It holds about 125 cm3 to the brim, and flux
  and paste drips are a few drops a session.

## Using it

- **Hanging the tray:** hang it after the barrels. Hook row 0, then swing the bottom in
  until the row-1 hoop snaps. The plate gap to the barrels' underside is 1.6 mm.
- **Liner out** (to empty it):
  1. Put a fingertip in the scallop, against the outside of the liner's front wall.
  2. Press back and up. The wall flares out 8.5 deg, so the push lifts the front edge.
  3. Once the base edge is above the lip (6.4 mm), the fingertip is 3.4 mm under it in
     the scallop. Hook it and pull the liner forward.

  It passes under the stored nozzles with 9.9 mm to spare, and the hand never goes inside
  the flux-coated rim. Pinching the front wall's top still works too.
- **Liner back:** rest its back edge on the lip's 55 deg outer ramp and push it back. It
  rides over the lip and drops behind the 60 deg inner face. The cheeks funnel the rim to
  centre.
- **When bumped:** the liner has to climb the 6 mm lip to escape. Gravity seats it flat
  on the floor; there is no friction fit.
- **Cleaning and spares:** wipe the liner with IPA; ASA does not care. Liners nest, so
  keep the three from the spares job stacked under the bench and swap one in.
- **Leaning on it:** your forearm rests on the lip when you reach for a syringe. The lip
  has a 3 mm flat top and chamfers both sides; keep them.

## Print

- **Tray:** `part-solder-drip-tray__v12__upright__fit-pf02c9-hoop5__print-upright.stl`,
  floor on the bed, 125.0 x 90.5 x 51.4 mm. Slice with the owner's ASA preset via
  `print/slice_pf.py`:
  - Repro Normal 0.4;
  - PolyLite ASA calibrated;
  - 2 walls (Arachne), 20 % infill;
  - organic tree supports on the build plate only;
  - 5 mm outer brim.

  The job is `print/slice-v12/V12-drip-tray-ASA/V12-drip-tray-ASA.gcode.3mf`.
- **Liners: three in one job.** `scratch/slice_liner_plate.py stagger3 69 5` places three
  copies of `part-solder-drip-tray-liner__v12__vase-filled__print-vase.stl` (a filled
  solid, base on the bed) as separate objects.
  - Layout: two along Y and one turned 90 deg beside them, 69 mm rim to rim.
  - Settings: spiral vase (smooth), print sequence by object, 1 wall at 0.6 mm, 0 top
    layers, 5 bottom layers, 0 % infill, no supports, the preset's 5 mm outer brim. Same
    ASA filament and 0.2 mm process.
  - Job: `print/slice-v12/V12-drip-tray-liner-stagger3-ASA-vase/V12-drip-tray-liner-stagger3-ASA-vase.gcode.3mf`.
    The G-code was checked: `spiral_mode = 1`, `print_sequence = by object`, three
    objects, each spiralling.
  - Placement on the bed: rims at x 3-253, y 43.6-240.6, so 15.6 mm clear of the
    front-left exclusion zone (x 0-18, y 0-28) and the front purge line.
  - The brim's outer loop reaches x 0.86 and 255.14 in the G-code, inside Orca's 256 mm
    printable area.
  - Render: `scratch/liner_plate_x3.png`.

  Why this layout:
  - Orca allows several objects in spiral vase only when printing by object.
  - It then wants the P1S's 68 mm toolhead clearance between objects, because a 20 mm
    liner is taller than the 4.2 mm exposed nozzle. It rejected gaps of 10, 35 and 60 mm
    ("too close to others").
  - Three liners at 69 mm fit the 256 mm bed only staggered: 250 x 197 mm.

  Alternatives:
  - If a brim within 1 mm of the plate edge worries you, `stagger3 69 3` (3 mm brim)
    also slices. The brim then ends on the rim's outline, because the rim overhangs
    the base by 3 mm: 54.1 min, 28.67 g.
  - `column2 75` (two liners, 5 mm brim): `V12-drip-tray-liner-column2-ASA-vase`.
  - The single-liner job: `V12-drip-tray-liner-ASA-vase`.

## Numbers (last passing run)

- **Volume:** 57.42 cm3 solid (61.4 g solid ASA), against B6's 89 cm3, so 35 % less.
  Rev 1 was 57.60 cm3; the scallop and the hoop-root clip took the difference.
- **checks.py:** passed.
  - One watertight body.
  - Pose error 0.0 mm.
  - Non-peg overhang area 0; peg overhang 130.5 mm2; islands none.
  - Liner: deepest 0.0 mm; 152 contacts; centre of mass over the contacts.
  - Removal, lift 6.4 then 95 forward: minimum clearance 0.40 mm, at the lip top.
- **fea.py** (`pegs` support, solid ASA E 1800 MPa, 92,966 nodes):

  | load case (5 N) | deflection | stiffness |
  |---|---|---|
  | wag: sideways at the lip centre, under the scallop (the farthest tool-bearing point) | **0.021 mm** (limit 1.0) | 242 N/mm |
  | press: down at the lip centre, under the scallop | **0.343 mm** (limit 0.5) | 14.6 N/mm |
  | press on the full-height lip 15 mm off centre | 0.290 mm | 17.3 N/mm |
  | press at the floor centre | 0.202 mm | |
  | press at the lip near the cheek | 0.112 mm | |
  | 5 N inward on the cheek's top edge, mid-length | 0.301 mm | |

- **Tray slice:** 125.9 min, 41.03 g, 257 layers. From `slice_report`:
  - support_g 1.43;
  - bridge_g (air) 0.01;
  - internal_bridge_g 2.64;
  - overhang_wall_g 0.01.

  Toolpath audit (`scratch/gcode_where.py`, output in `scratch/gcode_where.txt`):
  - **Support:** 1.41 g, all at installed y <= -0.30, i.e. under the pegs, plus 0.02 g
    of interface.
  - **Air bridge:** 0.01 g, at the plate-window apex points.
  - **Internal bridge:** 2.64 g, solid over sparse infill in the floor, the curb, the
    lip and the plate top.
  - **Overhang wall:** 0.01 g, behind the plate (pegs).
- **Liner slices (vase, 0 support, 0 bridge):**

  | job | minutes | grams | layers |
  |---|---|---|---|
  | three in one job (stagger3, 5 mm brim) | 55.0 | 29.04 | 3 x 101 |
  | three in one job (stagger3, 3 mm brim) | 54.1 | 28.67 | 3 x 101 |
  | two in one job (column2, 5 mm brim) | 38.8 | 19.37 | 2 x 101 |
  | one | 22.6 | 9.7 | 101 |

- **Station** (`station.py` on `station-layout.json`, run into `scratch/station/` so the
  shared station folder is untouched): passed.
  - Pegs on holes; no shared holes.
  - Plates at least 1.55 mm apart (tray to barrels 1.6 mm).
  - No solid or stored-tool clashes.
  - Every removal path is clear.
  - `station.py` prints null for the liner path because nothing came within its 1 mm
    pre-filter.
- **Liner removal path in station coordinates** (`scratch/liner_path_station.py`, output in
  `scratch/liner_path_station.json`). This is lift 6.4, then 95 forward, against every
  neighbour. The rim's straight edges were densely sampled against the barrel tools,
  because vertex sampling alone read 13.9 mm at the flux needle.

  | neighbour | minimum distance | where on the path |
  |---|---|---|
  | barrels-b6seats flux needle | **9.95 mm** | lifted, 47.5 forward (the back rim passes under it) |
  | barrels-b6seats paste nozzle | 23.75 mm | lifted, 45.5 forward |
  | barrels-b6seats holder (underside, z -120) | 24.6 mm | lifted, at the start |
  | barrels-b6seats sucker nose | 28.57 mm | lifted, 45.5 forward |
  | tweezers plate (beside, x 102.6) | 6.4 mm | at rest |
  | braid holder | 17.96 mm | lifted |

## Open risks

1. **The scallop costs stiffness.** 5 N at the scallop's bottom sags 0.343 mm, against
   0.261 mm at the full lip in rev 1. The limit is 0.5.
   - FEA assumes solid ASA, and the lip prints with 2 walls and 20 % infill, so the real
     sag is higher.
   - If the lip feels soft under a resting forearm, slice the tray with 40 % infill. That
     costs a few grams and nothing else changes.
2. **The three-liner plate is tight on the bed.**
   - Its rims come within 3 mm of the bed's X edges, and the brim within 0.9 mm. Orca
     accepts it.
   - In Y it has 15.6 mm to the front-left exclusion zone and 15.4 mm to the back edge.
   - If the plate edge gives trouble, use the 3 mm brim variant or the two-liner job.
3. **The printed liner against the tray:** 2 mm side play and 1 mm front and back. The ASA
   preset's 99.46 % shrink is baked into the slice. If the liner binds, scale it to 99 % in
   X/Y; nothing else changes.
4. **The 0.6 mm vase wall** is a consumable. Pinching the rim flexes it; that is why the
   job prints three.
5. **ASA warp on a 125 x 80 mm first layer.** The front corners are chamfered; the back
   corners are square where the plate stands. Rely on the preset's 5 mm brim, and watch
   the back corners.
6. **The flux needle** hangs 14.7 mm below the barrels module at the left end, in the
   band a hand crosses for the liner. The scallop keeps the grip 37 mm away from it. A
   guard would be a separate clip-on print.
7. **Shared library note:** `render.py` titles its side view "from the left". Its camera is
   at -X, which per the brief is the user's **right**.

## Files

- `__installed.step/.stl`, `__print-upright.step/.stl`: the tray.
- `__design.json`: everything, including `tip_rule`, `tray.finger_scallop` and
  `catch_window`.
- `__checks-spec.json`, `__checks.json`, `__fea-spec.json`, `__fea.json`, `__slice.json`.
- `__loaded/empty/front/side/print.png` and `.glb`.
- `__tool-liner.stl`: the in-use liner. `__ref-b6-nozzles.stl`: the barrel nozzle tips, for
  reference only.
- `part-solder-drip-tray-liner__v12__vase-filled__print-vase.stl/.step`, `__installed.step`:
  the liner.
- `__slice.json`: one liner. `__plate-x3__slice.json`: three.
- `scratch/`:
  - `slice_liner_plate.py` and `look_liner_plate.py`: the spares plate, with its render
    `liner_plate_x3.png`.
  - `slice_liner_vase.py`: one liner.
  - `liner_path_station.py`: the station path clearances.
  - `gcode_where.py`: the toolpath audit.
  - `station/`: the station check run.
  - `drip_tray_before_rev2.py`: the rev 1 builder.
