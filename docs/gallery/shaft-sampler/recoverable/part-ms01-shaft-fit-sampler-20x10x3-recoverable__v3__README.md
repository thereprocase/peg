# MS01 v3 — recoverable-magnet shaft sampler

Same A-P seats as v2. The magnet channels have 10.8 x 3.8 mm cross-sections
for nominal 20 x 10 x 3 mm magnets: 0.8 mm total clearance in each cross-section
dimension (0.4 mm per side when centered). No final caps. No loading pause.
The 20 mm magnet dimension runs along the shaft. The mounting pegs still use
the canonical tighter fit, e586ab4ff6. Width remains 150.4 mm / six cells.

## Print, then load

Open `part-ms01-shaft-fit-sampler-20x10x3-recoverable__v3__P1S-04-PLA__PRINT-ME.gcode.3mf` in OrcaSlicer. Three P1S / 0.4 / Generic PLA / textured PEI
plates: sixteen loose spacers, A-H strip, I-P strip. Print one strip if preferred.
`part-ms01-shaft-fit-sampler-20x10x3-recoverable__v3__P1S-04-PLA__EDIT-ME.3mf` is the editable project; changes require slicing again.
Both holders print flat top down; the open channel mouths face UP on the bed.
Do not load magnets while printing. Allow the part to finish and cool first.

| Plate | Contents | Material estimate | Time estimate |
|---|---|---|---|
| 1 | 16 loose spacers | 9.25 g | 31m 16s |
| 2 | A-H: 2-5.5 mm round | 103.32 g | 4h 8m 8s |
| 3 | I-P: 6-8 mm round + hex | 101.21 g | 4h 5m 8s |

With the finished strip inverted, slide a magnet into a channel, then a loose
10 x 2.95 x 17 mm spacer. The spacer ends flush with the mouth when the magnet
is fully seated. A strip of removable tape across the mouths holds the spacers
and magnets for the trial. Wrap tape onto the solid back of the bar; keep it off
the shaft seats and board contact face. These mouths face DOWN when mounted:
the loose fit is intentionally not a friction retainer. One magnet can be moved
between letters; eight populate a strip, sixteen populate both.

To recover: remove the holder from the board, support the mouths over a tray,
peel off the tape, and let the loose spacers and magnets slide out. The full
straight extraction volume is clear in CAD. Real print and magnet tolerances
still need the physical trial; do not force a magnet that binds.

## Compare the letters

A-M: round 2-8 mm in 0.5 mm steps with 0.15 mm radial clearance.
N/O/P: 6.35 mm hex, adding 0.10/0.20/0.30 mm per face.
Try ONE driver at a time; 17.5 mm test pitch is not final grasp spacing.
Tell us the letter, driver and how return, forward release and rocking feel.
Seats, bearing top and peg geometry are unchanged from v2; only material in
the magnet channels was removed. The nominal v2 magnet location gives a
1.02 mm magnet-to-shaft gap. Added sliding clearance allows 0.82-1.62 mm,
so keep the magnet against the shaft-side wall for repeatable comparisons.
This is a recoverable experiment, not a calibrated magnetic-force comparison.

## Preparation checks

One valid solid per holder; STEP round trips; no geometry change outside magnet
channels; clear full extraction paths for magnets/spacers; nominal driver
withdrawal; native Orca three-plate export and embedded-settings reslice;
no mesh repairs; bed/exclusion bounds and startup clearance checked.
All sixteen channel cores stay open from above the 3 mm floor to the final
40 mm layer. Zero magnet-loading pauses and zero channel-closing toolpaths.

0.20 mm layers, four walls, five top/bottom shells, 15% gyroid; local bed-grown
supports and 3 mm brim. PLA preset: 220 C nozzle / 55 C bed. Orca's existing
bed-temperature notice is retained in verification. Desktop GUI opening was
not checked. Physical sliding, tape retention, print finish and magnet feel
remain untested. Nothing has been sent to a printer.
