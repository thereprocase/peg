# MH01-MH04 v1 — magnetic shaft holders from MS01 letters E, I, M, O

After the physical MS01 trial the user chose four seats and asked for final
holders. These reuse the sampler's seat, 0.8 mm seat skin, flat 5 degree bearing
top, canonical tight pegs (fit e586ab4ff6) and the **sealed v2** magnet pocket
(10.4 x 3.4 mm, pause at geometric Z=38 mm, 10 x 2.95 x 14 mm plug, 1 mm recess).
Only width, seat count and pitch change. Form review: not sliced, not printed.

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

## Magnets and printing

26 magnets, 20 x 10 x 3 mm: 6 + 2x4 + 2x4 + 4. Print the plugs first on their broad
face. Holders print flat top down. Pause at geometric Z=38 mm, insert each magnet
then its plug, resume to cap. Verify the pause layer in the slicer before use.
The magnets are permanent in this version.

## Checked / not checked

Single valid solid per holder; STEP round trips; two peg flats on the bed plane;
seated tool clear of host; bearing contact under a 0.1 mm drop; lift then forward
withdrawal with every neighbour seated; 0.99-1.04 mm magnet-to-shaft gap (same as
sealed v2); straight magnet/plug loading path at the pause; plug top 1 mm below
the pause plane; print bounds under 250 mm. Numbers are in each
`design-and-checks.json`.

Handle envelopes are nominal planning cylinders (12 / 30 / 40 / 40 mm diameter),
not measured tools. Magnetic feel was judged in the v3 open channel, whose
magnet gap could range 0.82-1.62 mm; the sealed pocket fixes it near 1.02 mm.
No slicing, support review, physical fit or load has been established.

Sources: `source/magnetic_shaft_holders.py`, `source/render_magnetic_shaft_holders.py`.
