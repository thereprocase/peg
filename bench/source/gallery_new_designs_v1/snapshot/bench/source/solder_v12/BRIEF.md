# Solder station v12: design brief

The owner's goal (2026-10-02): perfect the rest of the solder workstation. That covers print
orientation, attaching the refined pegs, checks for flex, tool holding, stiffness and
printability. No cantilevers and no unprintable overhangs. Use cheek printing or
bottom-side printing strategically. Check the massing, think through the prints and imagine
being the user.

The station is seven pegboard modules (B6 is published at
https://thereprocase.github.io/peg/gallery/solder-modules/). The tweezer rack is done
(v11.2, `bench/source/tweezers_v11/holder.py`; read it for style and stiffening). The
other six are rebuilt here as v12:

| id | B6 module | cells | B6 pose | B6 volume | station position (top-row centre, mm) |
|---|---|---|---|---|---|
| barrels | flux syringe, paste syringe, solder sucker, nozzles down | 5 | upright | 257 cm3 | x 38.1, z 0 |
| reel-thick | large solder reel | 3 | right cheek | 99 cm3 | x -114.3, z 0 |
| reel-thin | small solder reel | 3 | right cheek | 99 cm3 | x -114.3, z -101.6 |
| braid | desoldering braid roll | 2 | right cheek | 39 cm3 | x -50.8, z -101.6 |
| drip-tray | removable drip tray + vase-mode liner, below the barrel nozzles | 5 | upright | 89 cm3 | x 38.1, z -127 |
| snips-pliers | micro snips + needle-nose pliers, jaws down | 2 | right cheek | 79 cm3 | x -50.8, z 0 |
| tweezers (done) | v11.2 | 2 | right cheek | 94.5 cm3 | x 127, z 0 |

Positions are on the 1-inch grid. A module may change its cells or height when the reason is
good, but it must not collide with its neighbours' plates or tools. Report any change.

## Inputs

- **Tool stand-ins** in module-local holder coordinates (the B6 placement):
  `bench/reference/solder-tools/<id>__*.stl`. These are open meshes, the same planning
  proxies B6 used, not measured tools. Design for them with forgiving fits. Say which
  dimensions matter so the owner can measure the real tools.
- **The B6 holder** for each module: `docs/gallery/solder-modules/<id>/holder.stl`,
  `print-pose.stl` and `checks.json`, with renders at `docs/gallery/solder-modules/<id>.png`,
  `<id>-print.png` and `<id>-toolpaths.png`. These show what the old design did. B6 was never
  printed and was replaced as a design basis, so keep its intent, not its geometry.

## Coordinates and the shared library

All in `bench/source/solder_v12/`:

- **Coordinates:** X is lateral (+X is to your left when facing the board; the right cheek
  is at -X), Y is out of the
  board (pegs at Y < 0.15), Z is up. The top peg row's hole centre is at Z 0.12; row k is at
  0.12 - 25.4k. The plate's sharp lip is at Z 5.12; the plate wall runs from Y 0.15 to 5.55.
- **`common.py`:**
  - `receiver(cells, hoop_row, pose, ...)` builds the plate and pegs: hooks on row 0,
    bearing locators every other row between, and the PF07 #5 hoop on `hoop_row`. The hoop
    is turned into the cheek plane for `right-cheek` and left as is for `upright`. Pass
    `x0/x1/z0` to trim the plate.
  - Helpers:
    - `pointed_window(..., up='+X' | '+Z')` cuts plate windows with pointed roofs, so no
      bridges.
    - `peg_keepout()` keeps cuts away from the peg roots.
    - `band()`, `poly_prism()` and `box()` for strips and prisms.
    - `export()` writes the installed STEP/STL, the print-pose STEP/STL and the pose matrix.
    - `save_design()`.
- **`template_module.py`:** a runnable pipeline example, not a design. Copy its structure:
  1. receiver,
  2. body,
  3. `export`,
  4. tools placed and written as STLs in installed coordinates,
  5. `NAME__checks-spec.json` and `NAME__fea-spec.json`,
  6. `NAME__design.json`.
- **`checks.py`** (cadpy) checks:
  - one watertight body;
  - the pose matrix;
  - print-pose overhang features (pegs exempt);
  - tool fit (depth inside the holder);
  - seat (contacts, centre of mass over the contacts for gravity seats);
  - the removal path.
- **`fea.py`** (cadpy): a CalculiX linear-static solve under `face` and `pegs` support.
- **`render.py`** (cadpy): the loaded, empty, front, side and print views.
- **`slice_report.py`** (python3): time, grams, and support, bridge and overhang-wall grams.

Do not edit the shared files. If one needs a change, say so in your result.

## Commands

Run all of these from `/mnt/f/code/peg-fit-ladder-20260930`, with a timeout on every one:

```
timeout 900 "/mnt/c/Program Files/FreeCAD 1.1/bin/python.exe" 'F:\code\peg-fit-ladder-20260930\bench\source\solder_v12\<id>.py' 'F:\code\peg-fit-ladder-20260930\bench\reviews\v12-build\<id>'
cd bench && timeout 900 cadpy source/solder_v12/checks.py reviews/v12-build/<id> <NAME>
cd bench && timeout 900 cadpy source/solder_v12/render.py reviews/v12-build/<id> <NAME>
cd bench && timeout 3000 cadpy source/solder_v12/fea.py reviews/v12-build/<id> <NAME>
cd print && timeout 900 "/mnt/c/Program Files/FreeCAD 1.1/bin/python.exe" 'F:\code\peg-fit-ladder-20260930\print\slice_pf.py' 'v12:bench/reviews/v12-build/<id>/<print stl>:V12-<id>-ASA'
python3 bench/source/solder_v12/slice_report.py print/slice-v12/V12-<id>-ASA/V12-<id>-ASA.gcode.3mf bench/reviews/v12-build/<id>/<NAME>__slice.json
```

Naming: `NAME = 'part-solder-<id>__v12__<role>__fit-pf02c9-hoop5'`. Role is the pose, e.g.
`right-cheek` or `upright`. Never use `$(...)` in a shell command. Do not commit, push,
print or touch the printer.

## Owner rules (non-negotiable)

1. **Choose the bed face first.** Use the right cheek (-X) on the bed for narrow, deep
   modules, or the flat bottom for wide, shallow ones. Nothing prints in the air but the
   pegs, and Orca's organic supports go under the pegs only.
2. **Bridges or overhangs, never a cantilever.** In the print pose, every face steeper than
   45 degrees from vertical must be a peg. Openings get pointed roofs (at least 50 degrees),
   undersides get 45-degree chamfers or ramps, and anything horizontal sits on a wall. The
   v11 rack's through-slot ceilings printed as spaghetti. A bridge needs real walls at both
   ends, a span of at most 10 mm, and something behind it. Declare every bridge in
   `overhang_exceptions` with its reason; `checks.py` re-measures it.
3. **Flex in the print layers.** Clips, catches and spring arms must flex in the layer
   plane. `receiver()` already orients the hoop by pose. Any snap feature you add follows the
   same rule.
4. **Glue-in parts seat in blind pockets**, never through-holes: a vertical wall on the bed
   side and a chamfer on the other.
5. **Stiffness.** A thin cheek is flexy: v11 measured 45 mm at 5 N, and the owner rejected
   it. Use flanges (L or C sections), triangulated struts, plate-to-cheek gussets and webs
   (v11.2: 1.4 mm at 5 N, 114 mm out). Target: at most **1.0 mm** of sideways deflection at
   5 N at the farthest tool-bearing point under `pegs` support (5 N/mm or better). Also at
   most 0.5 mm at 5 N down. Report the numbers.
6. **Minimal plastic without sacrificing looks, strength or function.** Report the volume
   against B6. Do not save plastic at the cost of access or stiffness.
7. **BENCH_HOLDERS working rules:**
   - Width = 25.4 x cells - 2.
   - Two mounting columns.
   - Keep bearing, grasp and a one-motion return clear.
   - Prefer forgiving lead-ins.
   - Protect delicate tips and keep exposed points above a floor.
8. **Device data is a hint.** The tool proxies are guesses. Make fits forgiving (lead-ins,
   ramps, generous clearances where retention does not depend on them). List the real
   dimensions the owner should measure.

## Think as the user

The owner solders at this bench and wants:

- **Grab and return one-handed:**
  - one motion out;
  - one motion back;
  - no fiddling;
  - nothing to knock the neighbouring tools.
- **Tools stay put when the board is bumped.** Use gravity seats with a lip or cant, not
  friction alone.
- **Easy refills:**
  - reel and braid changes without tools;
  - liner out to empty it;
  - syringes in and out.
- **No hot iron here:** the iron lives elsewhere. Flux and paste drip, so nozzles point into
  the drip tray below the barrels.
- **Printing it:** one plate per module where it fits, with ASA's warp tendency respected
  (no huge thin flat sheets standing tall without ribs; a big first-layer footprint is good).
- **Shapes that look intentional.** Use consistent fillets and chamfers and the v11 visual
  language: flanges, triangulated windows, a tidy massing.

## Pass criteria for your module

1. `checks.py` passes:
   - one body;
   - non-peg overhang area 0, or declared bridges that pass;
   - every tool fits with no clash deeper than 0.15 mm;
   - every seat passes;
   - every removal path is at least -0.15 mm.
2. `fea.py`: the farthest tool-bearing point moves at most 1.0 mm sideways and at most
   0.5 mm down at 5 N under `pegs` support.
3. Sliced with the owner's ASA preset:
   - `slice_report`'s support grams are pegs only;
   - bridge and overhang-wall grams are near zero outside the pegs;
   - the print fits the 256 mm bed.
4. **Renders viewed and critiqued.** Open each PNG with the Read tool and look at it as the
   owner would.
5. A `NOTES.md` in your build dir with:
   - the design and why;
   - how the user loads and unloads each tool;
   - the print pose and settings;
   - the numbers (volume vs B6, FEA, slice time, grams, support);
   - open risks and the dimensions to measure.
