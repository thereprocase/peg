# MH01-MH04 v1 — magnetic shaft holders from MS01 letters E, I, M, O

After the physical MS01 trial the user chose four seats and asked for final
holders. These reuse the sampler's seat, 0.8 mm seat skin, flat 5 degree bearing
top, canonical tight pegs (fit e586ab4ff6) and the **sealed v2** magnet pocket
(10.4 x 3.4 mm, pause before the 38.2 mm layer, 10 x 2.95 x 14 mm plug, 1 mm
recess). Only width, seat count and pitch change. Sliced and path-checked; not
yet printed.

| Part | MS01 letter | Seat | Seats | Cells | Width | Seat pitch | Print |
|---|---|---|---|---|---|---|---|
| MH01 | E | 4.0 mm round, 4.3 opening | 6 | 4 | 99.6 mm | 16.93 mm | one |
| MH02 | I | 6.0 mm round, 6.3 opening | 4 | 7 | 175.8 mm | 44.45 mm | **two** for 8 seats |
| MH03 | M | 8.0 mm round, 8.3 opening | 4 | 8 | 201.2 mm | 50.80 mm | **two** for 8 seats |
| MH04 | O | 1/4 in hex, 6.75 AF opening | 4 | 8 | 201.2 mm | 50.80 mm | one |

## Grid rules

Width = 25.4 x cells - 2 mm; peg columns sit in the two outermost cell centres.
Seat pitch = cells x 25.4 / seats, with the row centred, so the end seats sit half
a pitch from the cell boundary. Identical modules placed side by side keep the
same seat spacing straight across their 2 mm seam. That is how the requested
eight-seat I and M rows are made: eight handle-clear seats need 355-406 mm, which
exceeds one P1S print, so each is a pair of 4-seat modules.

MH01 is the narrow jeweler bar: 16.93 mm is tighter than the sampler's 17.5 mm
trial pitch. Three cells (12.7 mm pitch) was rejected: the outer 10.4 mm magnet
pockets would leave a 0.15 mm side wall. MH04 uses the widest pitch for
bit-holder handles.

## Print, pause, load

Open `part-mh01-mh04-magnetic-shaft-holders__v1__P1S-04-PLA__PRINT-ME.gcode.3mf`
in OrcaSlicer. Five P1S / 0.4 / Generic PLA / textured PEI plates. **Print plate 1
first**: the plugs must exist before any holder reaches its pause. Print plates 3
and 4 twice for the eight-seat rows. `...__EDIT-ME.3mf` is the editable project;
changes require slicing again.

| Plate | Contents | Material estimate | Time estimate | Pause |
|---|---|---|---|---|
| 1 | 26 plugs | 12.54 g | 41m 48s | none |
| 2 | MH01 E, 6 magnets | 71.72 g | 3h 1m 29s | before Z 38.2 |
| 3 | MH02 I, 4 magnets — print twice | 108.04 g | 4h 2m 19s | before Z 38.2 |
| 4 | MH03 M, 4 magnets — print twice | 120.94 g | 4h 27m 40s | before Z 38.2 |
| 5 | MH04 O, 4 magnets | 120.87 g | 4h 23m 24s | before Z 38.2 |

All seven prints: about 663 g and 25 hours. 26 magnets, 20 x 10 x 3 mm.

Holders print flat top down. Each holder plate has one native pause after the
38.0 mm layer, with every chimney still open. At the pause: slide one magnet into
each chimney with its 20 mm length vertical, then a plug on top; the plug ends
1 mm below the rim. Keep loose magnets away from the nozzle and from each other.
Resume; the next layer starts the permanent 2 mm cap. The magnets cannot be
recovered from this version.

0.20 mm layers, four walls, five top/bottom shells, 15% gyroid, build-plate-only
supports and 3 mm brim, same as the MS01 v2 job. Remove the local peg supports
and brim before mounting.

## Checked / not checked

CAD: single valid solid per holder; STEP round trips; two peg flats on the bed
plane; seated tool clear of host; bearing contact under a 0.1 mm drop; lift then
forward withdrawal with every neighbour seated; 0.99-1.04 mm magnet-to-shaft gap
(same as sealed v2); straight magnet/plug loading path at the pause; plug top
1 mm below the pause plane. Numbers are in each `design-and-checks.json`.

Sliced job: native Orca 2.4.2 five-plate export from the embedded settings; no
mesh repairs; nothing outside the bed; path accounting and startup clearance pass
on all plates; exactly one pause per holder plate, before layer 38.2 with 38.0
complete; **zero extrusion inside any of the 18 magnet chimneys below 38.0**, and
every chimney's first closing layer is 38.2. Orca's existing bed-temperature
notice is retained in `checks.json`.

Not established: desktop GUI opening, support removal, physical fit, load, and
magnetic feel at these spacings. Handle envelopes are nominal planning cylinders
(12 / 30 / 40 / 40 mm diameter), not measured tools. Magnetic feel was judged in
the v3 open channel, whose magnet gap could range 0.82-1.62 mm; the sealed pocket
fixes it near 1.02 mm. Nothing has been sent to a printer.

Sources: `source/magnetic_shaft_holders.py`, `render_`, `slice_`, `check_`,
`package_` and `publish_magnetic_shaft_holders.py`.
