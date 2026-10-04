# Braid roll, v12 (rev 2: sourced bobbin envelope)

`part-solder-braid__v12__right-cheek__fit-pf02c9-hoop5`. The builder is
`bench/source/solder_v12/braid.py`. It is 2 cells wide, hangs on hoop row 1 and prints on its
right cheek. Its station position is unchanged: top-row centre at x -50.8, z -101.6. Its plate
footprint is the same as rev 1, so `station-layout.json` is unchanged. Coordinates are as in
BRIEF.md: facing the board, +X is your left and the right cheek is -X.

## What changed from rev 1, and why

| | rev 1 | rev 2 | why |
|---|---|---|---|
| roll it was built for | B6 proxy, 34 OD x 8 x 8 bore | every common bobbin: OD 38-52, width 6-12, bore 7-10.5 | TOOLS.md section 2: no common bobbin is under 38 mm; the old 41 mm drum fitted none of them (IMPACTS 2.2) |
| hood | a full drum, R_IN 20.5, open only at the front | top and back only (theta 50-180), R_IN 27.5, open at the front and the bottom | IMPACTS option 1b: a 52 mm rim hangs free below, so the module stays 2 cells and row 1 |
| axle | 6.0 mm, no catch | 5.6 mm (PIN_R 2.8) with a 0.8 mm lip on its top line | Frodo finding 1: a brush toward +X walked the roll off. The lip forces a 0.8 mm bore pass, so the axle had to shrink: a 7 mm cross-hub bore passes 5.6 + 0.8 = 6.4 with 0.6 to spare |
| hub seat | 13 mm (HUB_R 6.5), seat at u 6 | 10 mm (HUB_R 5), seat at u 8.5 | Every hub ring (12-16) is wider than the seat, so Chemtronics' domed face bears on its flat ring either way round. The seat moved out so a 52 mm roll's leaning top clears the cheek |
| cheek stiffening | the full drum | hood + a lower-edge flange + two webs crossing at the hub | the open bottom took away the drum's lower half. The FEA probe showed that the cheek bending round the hub was the compliance (below) |

## The design

- **Axis across the board.** The roll stands on edge on a stub axle that grows out of the
  right cheek. Its axis runs along X, rising 15 degrees toward the tip (the v11 tweezer cant).
  The braid pays off the front rim straight at you, flat and untwisted. The pull lies in the
  roll's plane, so it spins the roll and presses the bore onto the axle's top line.
- **Gravity seat.** Under the cant the roll leans into the cheek and seats its inner face on
  the 10 mm hub seat at u 8.5. Every roll hangs by its bore on the axle's top line.
- **Retention lip (nothing flexes).** The lip is 0.8 mm high and 2.0 mm wide, on the axle's
  top line at u 21.1, which is 0.6 mm past the face of the widest (12 mm) roll.
  - The keeper faces the roll and is a **V nose**. In the print its two faces rise 50 degrees
    from horizontal on either side of the leaning post, so they are print-down ramps with no
    overhang. The nose edge rises 10 degrees outward, so the lip's lowest point sits on the
    axle and there is no island.
  - Seen from the roll, the two faces push sideways (the axle already holds the bore
    sideways), not up. The nose edge stands 65 degrees off the axle.
  - A push toward +X meets the nose 80 degrees off its own direction (65 + the 15 degree
    cant). With no friction that takes about 5.7 x the roll's weight, and with
    plastic-on-plastic friction it locks. So a brush does not walk the roll off.
  - To pass the lip, the roll must be lifted 0.9 mm (measured). The tip side of the lip is a
    30 degree loading ramp, so pushing a roll on lifts it over by itself.
  - Measured on the final geometry (`scratch/lip_test.json`): sliding off without a lift,
    each roll hits the lip 0.8 mm deep, after 1.0 mm of travel (52 x 12), 3.0 (Chemtronics)
    or 7.0 (38 x 6). Each passes after a 0.9 mm lift.
- **Hood.** A 2.4 mm shell coaxial with the axle, R_IN 27.5. It runs from theta 50 (front-top,
  bullnose end) over the top to the back, where it runs into the plate. It covers the roll's
  inner 4 mm (rim at u 12.5). It is the cheek's top stiffening flange, and it catches lead
  ends falling from the snips above. The front, where the tail leaves, is open, and so is
  the whole bottom half.
- **Cheek.** A 3 mm bed face, 1885 mm2. Its outline is the hood's footprint, the hub flare and
  the plate edge, hulled. It is stiffened by:
  - a 6 mm L flange along its lower edge, from the plate's bottom corner to under the hub
    (with a 45 degree tapered end);
  - two 2.4 mm webs crossing at the hub: one back to the plate at the axle's height (for wag
    and pull), and one from the cheek's lower edge up toward the hood (for press). Both are
    trimmed to the plane 1.5 mm under the roll's inner face (u 7.0), so no roll touches them.
- **Receiver.** `common.receiver(2, 1, 'right-cheek')` with the shared install-arc hoop fix
  (root clipped to r 2.95, cheek hoop dropped 0.10 mm, verified rigid-clear on rows 1-6 in
  `install-arc/sweep-fixed.json`). The hooks are on row 0 and the PF07 #5 hoop is on row 1,
  turned into the cheek plane so it flexes in the print layers. The plate runs from Z 5.12
  to -31.28.
- **Plate.** A 50 degree pointed window in the free left half, with its point at +X (the
  print top), and 45 degree chamfers on the plate's two free corners.
- Nothing is glued and nothing snaps apart from the shared hoop. There are no bridges, and
  nothing overhangs except the pegs.

## Loading and unloading

- **Load (one motion):**
  1. Hold the roll so the free end comes off the front rim, toward you and downward.
  2. Offer the bore to the axle's cone tip from your left (+X, the open side) and push the
     roll on. It rides up the loading ramp, drops behind the lip and slides down the cant onto
     the hub.
  3. Let the tail hang from the front rim. Nothing sits under the roll, so it hangs free.
- **Use:** pinch the tail below the roll and pull it toward you or down. The roll spins.
  Snip with the cutters from the module above. The stub stays hanging at the front rim.
- **Unload (one motion):** pinch the roll by its outer face and its bottom rim. Both are fully
  exposed: the outer face stands 2-8 mm proud of the hood rim, and the whole lower half hangs
  below. Lift about 1 mm, until the bore rests on the axle's underside, and slide the roll left
  off the tip, about 19 mm along the axle. The roll stays inside the module's own width the
  whole way. A 52 x 12 roll's outer edge is at local x +5.3 on the seat and +23.9 when it
  leaves the tip; the module edge is +24.4 and the drip tray's plate starts at +26.4.
- **Wrong way round:** if the tail comes off the back of the roll, flip the roll over. Either
  face may go against the hub.

## Covered product range

The owner does not measure tools, so this module covers the sourced envelope
(`bench/reference/solder-tools/TOOLS.md` section 2). The checks run on three stand-ins built in
the builder:

- a 52 x 12 mm roll with a 7 mm bore: the envelope's largest OD and width with its smallest
  bore, the tightest case everywhere;
- a 38 x 6 mm roll with a 10.5 mm bore: the smallest and thinnest roll with the biggest bore,
  which hangs lowest;
- a Chemtronics Soder-Wick SD, 44.5 mm with an 8 mm bore and 10 mm thick at the hub, loaded
  domed face in.

The B6 34 mm proxy is no longer used. Every check and the station check pass for all three.

| dimension | covered | limit (what sets it) |
|---|---|---|
| OD | 38-52 | up to about 54: the hood back (1.5 mm gap at 52) and top (2.2 mm at 52 with a 7 mm bore; the 0.9 mm unload lift leaves 1.3) |
| width | 6-12 | 12.6: the lip sits 0.6 mm past a 12 mm roll. Thinner rolls just have axial play; the cant holds them on the hub |
| bore | 7-10.5, round or cross hub (7 mm inscribed) | at least 6.4 to pass pin + lip (7 leaves 0.6). Larger bores hang lower and still bear on the seat's upper crescent; checked to 10.5 |
| inner face | flat, or domed with a flat hub ring at least 10 mm across | the seat is 10 mm across. The face must not bulge more than 1.5 mm toward the cheek outside the hub ring (it sits 1.5 mm off the webs) |
| form | a bare bobbin or a case with a through-hole that spins whole | the whole roll spins on the axle (whether Japanese cases turn inside is unconfirmed; irrelevant here) |

- **Products covered:** MG Chemicals Super Wick 423-427 (39.9 mm), Chemtronics Soder-Wick SD
  (44.5, domed face), Techspray Pro Wick 1808-1813 (45.0), the generic Amazon/AliExpress
  cross-hub cases (45.7), goot Wick CP-xx15 (51), and the Hakko FR551/FR150 and Chip Quik
  SOLDERWICK cases (40-46 family, OD not confirmed).
- **Not covered (a different holder):**
  - dispensers with no bore: goot CP-xxY tadpole, Velleman/Whadda DESOLDER4 thumbwheel;
  - long-length spools (25-100 ft): 55-60 OD, 20-28 wide, 20 mm bore.

## Print

- **Pose:** right cheek (-X) on the bed. The bed footprint is the 3 mm cheek plus the plate
  edge. The print is 42.96 x 65.93 mm on the bed and 48.8 mm tall.
  - The plate, window walls, webs and flange stand vertical.
  - The hub, axle and hood lean 15 degrees off vertical.
  - The lip's V faces rise at 50 degrees.
  - Only the four pegs reach into air.
- **Supports:** Orca organic tree supports, on the build plate only. They land under the pegs
  only (verified below).
- **Settings, read from the sliced job:** `Repro - ASA - Polymaker PolyLite - Calibrated`,
  nozzle 260 C, bed 100 C, 0.2 mm layers, 2 walls (Arachne), 20 % crosshatch infill, 5 top and
  3 bottom layers, 5 mm outer brim. The job is
  `print/slice-v12/V12-braid-ASA/V12-braid-ASA.gcode.3mf`. It has not been sent to the printer.

## Numbers (last passing run)

- **Volume:** 16.47 cm3, 17.6 g solid ASA. B6 was 39 cm3, so this is 42 % of B6 (58 % less).
  Rev 1 was 17.30 cm3. The webs cost 0.55 cm3.
- **`checks.py`: passed.**

  | check | result |
  |---|---|
  | body | 1 watertight body, 16.47 cm3 |
  | pose-matrix error | 0.0 mm |
  | non-peg overhang area | 0.0 mm2 (peg 132.2 mm2) |
  | islands | none |
  | 52 x 12 bore 7 | deepest 0.000, 607 contacts, centre of mass over the contacts; removal (lift 1.2, slide 19.6 along the axle, out 70) min -0.000 (sliding on the seat) |
  | 38 x 6 bore 10.5 | deepest 0.000, 173 contacts, centre of mass over the contacts; removal (lift 1.0) min -0.000 |
  | Chemtronics 44.5 domed | deepest 0.000, 405 contacts, centre of mass over the contacts; removal (lift 1.3) min +0.001 |
  | tail stand-in | clear (17.7 mm off the holder) |

- **Clearance at rest, away from the axle and seat** (`scratch/lip_test.json`): 1.5 mm to the
  plate behind the 52 mm roll, and 1.5 mm from every roll's inner face to the webs (by
  design). The top gap under the hood is 2.2 mm (52 mm roll, 7 mm bore).
- **`fea.py`, pegs support, 5 N at the lip (u 21.6, radius 3.5), the farthest point a roll
  bears on:**

  | load | at the load | stiffness | worst node | limit |
  |---|---|---|---|---|
  | wag, sideways (+X) | **0.106 mm** | 47 N/mm | 0.173 at the cheek's front tip | 1.0 (9.4x margin) |
  | press, down (-Z) | **0.166 mm** | 30 N/mm | 0.225 at the axle tip | 0.5 (3.0x margin) |
  | pull, toward you (+Y) | 0.139 mm | 36 N/mm | 0.212 | |

  Where the deflection comes from (`scratch/fea_probe.py` / `.json`):
  - The plate and pegs move less than 0.01 mm.
  - Before the webs (0.147 / 0.208 / 0.216), the cheek bent out of plane round the hub.
  - Press now splits into: hub rotation (about 0.075 mm at the lip), the 5.6 mm pin bending
    over the 13 mm it needs for a 12 mm roll (about 0.05), and hub translation (0.03).
  - The pin's size and length are set by the envelope.
- **Slice** (`NAME__slice.json`): 51.7 min, 11.08 g, 244 layers.
  - Support is 1.06 g. All 6426 support and 378 support-interface points map to behind the
    plate, at the pegs (`scratch/support_where_xy.py`).
  - Overhang wall is 0.01 g, all at the pegs.
  - Bridge is 0.00 g: the pegs, plus the last points closing the window's apex at X 21.2.
  - Internal bridge (0.48 g) is solid infill over sparse infill inside the cheek, the hub and
    the plate, not over air.
- **Station** (`station.py` with this build, output in `scratch/station/`): passed.
  - The pegs are on the grid with no shared holes.
  - The braid plate is unchanged (x -75.2..-26.4, z -132.9..-96.2). It sits 2.0 mm from the
    thin reel and from the drip tray, and 39.5 mm below the snips. The station-wide minimum
    gap is 1.55 mm, between two other modules.
  - No solid clashes.
  - All three bobbins' removal paths clear the neighbours.
  - The 52 mm roll's bottom is at station z -152.4. Nothing is below the braid.
- **GLB:** `NAME__loaded.glb`, `__empty.glb` and `__print.glb`.

## Open risks

- **Bore-edge chamfers.** A roll whose bore edge is heavily chamfered or rounded meets the
  nose with its own slope, not the 65 degree edge. With a 45 degree chamfer a sideways push
  needs 1.7 x the roll's weight with no friction and about 4 x at a friction of 0.3. That is
  weaker than the locked case, but the roll still has to lift, not slide. Expect a cross-hub roll to index the lip into one of its notches; that is
  harmless.
- **The 5.6 mm axle prints as a near-vertical post,** so bending crosses the layer lines.
  5 N at the lip is about 4 MPa. A snagged-braid yank of 20 N is about 15 MPa, near ASA's
  layer strength. The roll spins freely, so a yank only loads the axle if the braid snags.
- **Overrun.** There is no brake. A fast yank may spin the roll on and throw a loop of braid.
  If that bothers the owner, a felt dot on the hub seat adds drag.
- **Hoop row 1 has not been hung on a board.** The shared install-arc sweep with the fix
  shows rows 1-6 rigid-clear.
- **The roll's lower half is open** by design. The cost is that nothing guards its bottom rim,
  where only the user's hand goes.
- **Window apex.** The slicer bridges the last points at the window's apex, which is normal
  for a pointed roof.

## Scratch tools

- `scratch/lip_test.py`: retention (slide with no lift, minimum lift to pass) and clearance by
  region.
- `scratch/fea_probe.py`: FEA displacements at named points (same mesh, material and loads as
  `fea.py`).
- `scratch/support_where_xy.py`: maps Orca support, bridge and overhang lines back to holder
  coordinates.
- `scratch/station/`: a station check run with this build.
