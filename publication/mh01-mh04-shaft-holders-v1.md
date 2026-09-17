## MH01-MH04 v1 — magnetic shaft holders from the MS01 result (form review)

User reported the physical MS01 result on 2026-09-17: letters E, I, M, O, and asked
for final holders: a narrow six-seat E bar for jeweler drivers, eight seats each of
I and M, and a four-seat O bar with extra handle spacing, all tiling on the grid.
User chose paired four-seat modules for the eight-seat rows and sealed
pause-and-cap magnets.

`magnetic_shaft_holders.py` in the holder workspace reuses the MS01 seat, 0.8 mm
skin, sealed v2 pocket/plug and canonical fit e586ab4ff6. Only width, seat count
and pitch change. Seat pitch = cells x 25.4 / seats, so spacing continues across
the 2 mm seam. MH01 E 6 seats / 4 cells / 16.93 mm; MH02 I 4 / 7 / 44.45;
MH03 M 4 / 8 / 50.8; MH04 O 4 / 8 / 50.8. MH02 and MH03 print twice. 26 magnets.

CAD single solids, STEP round trips, peg flats on the bed plane, bearing contact,
lift/forward withdrawal with neighbours seated, 0.99-1.04 mm magnet gap and pause
loading path pass. Handle envelopes are nominal. NOT sliced, no supports review,
no pause-layer verification, no physical print. No job sent to a printer.

Gallery: https://thereprocase.github.io/peg/gallery/shaft-holders/
Release: mh01-mh04-shaft-holders-v1 (12 STEP files and the review CAD kit ZIP).
Receipts: `mh01-mh04-shaft-holders-v1-additions.json`; `tools/check_gallery.py`
verifies their hashes. Staged by `publish_magnetic_shaft_holders.py`.
