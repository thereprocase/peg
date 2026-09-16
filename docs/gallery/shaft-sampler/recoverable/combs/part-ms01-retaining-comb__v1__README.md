# MS01 retaining combs v1 — print FLAT

Matching A-H and I-P eight-finger retainers for the existing MS01 v3 recoverable
holders. NO HOLDER REPRINT NEEDED. Replace the eight loose spacers with the
matching labeled comb. These do not fit the sealed v2 holders.

Open `part-ms01-retaining-comb__v1__P1S-04-PLA__PRINT-ME.gcode.3mf` in OrcaSlicer. One plate, both combs lying on their common broad
faces. P1S / 0.4 mm / Generic PLA / textured PEI. Estimated 9.47 g and 30m23s for
both. No supports, brim or pauses. `part-ms01-retaining-comb__v1__P1S-04-PLA__EDIT-ME.3mf` is editable; reslice after edits.
Use the explicit `print-flat` STEP/STLs, not the installed-coordinate files.

## Load and tape

After printing and cooling, hold the holder inverted and load the magnets into
its open channels. Match the A-H or I-P marking. Slide all eight fingers into
the channels together until the shared rail meets the mouths, then tape the
rail to the solid holder body. Keep tape away from the shaft grooves. The
rail sits beneath the holder when mounted. To recover, remove from the board,
peel the tape, withdraw the comb, and tip the magnets into a tray.

Fingers are 16.8 mm long with a 0.6 mm tapered lead, leaving 0.2 mm nominal
end play behind the 20 mm magnets. The flat-backed fingers vary in thickness
to follow the staggered channels. A-H: 1.25-3 mm, I-P: 2-3 mm. All fingers
share a full bed face; nothing starts in midair. The broad faces print flat,
not with the rail on the bed and the fingers standing up. Rails span 150.4 mm.
The rail supports axial seating, not sideways magnet centering. Existing
channel clearance and magnetic-gap variation remain.

## Checks

One valid solid each; STEP round trips; compatible holder geometry identical
to exported v3; full finger slide envelopes and complete comb extraction;
0.2 mm magnet end clearance; clear shaft withdrawal. Native Orca export,
embedded-settings reslice, mesh repair count, bed bounds and startup paths
checked. Actual job reports no support use, no pause and no outside-bed parts.
Four walls, 0.20 mm layers, 15% gyroid; thin fingers are mostly solid shells.
PLA 220 C nozzle / 55 C bed from frozen user profiles. Desktop GUI opening,
physical insertion, finger flex and tape retention remain untested.
Nothing has been sent to a printer.
