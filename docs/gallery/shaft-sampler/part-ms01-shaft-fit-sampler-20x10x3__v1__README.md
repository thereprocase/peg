# MS01 v1 — lettered magnetic shaft sampler

Open `part-ms01-shaft-fit-sampler-20x10x3__v1__P1S-04-PLA__PRINT-ME.gcode.3mf` in OrcaSlicer. Print plate 1 (sixteen plugs) FIRST, then either
or both strips on plates 2 and 3. `part-ms01-shaft-fit-sampler-20x10x3__v1__P1S-04-PLA__EDIT-ME.3mf` is the editable project; changes
require slicing again. P1S, 0.4 mm nozzle, Generic PLA starter preset, textured PEI.
PLA is an explicitly stated preparation assumption; no material reply was received.

| Plate | Contents | Estimated material | Estimated time |
|---|---|---|---|
| 1 | 16 plugs FIRST | 8.15 g | 29m 5s |
| 2 | A-H round 2–5.5 mm | 103.49 g | 4h 8m 42s |
| 3 | I-P round 6–8 mm and hex | 101.18 g | 4h 5m 32s |

Estimates exclude the time you spend at the magnet-loading pause. Each strip needs
EIGHT 20 x 10 x 3 mm nominal magnets and eight preprinted plugs; both need sixteen.
The 20 mm direction runs down the shaft, 10 mm spans the seat, and 3 mm is thickness.
The intended magnetization is through the 3 mm thickness, broad face toward shaft.
Print one strip first if you prefer. Magnets become permanently enclosed on resume.

## At the pause

The native pause is before the first cap layer at Z=38.2 mm, after 38.0 mm has
printed. All eight chimneys are open. Insert ONE magnet, immediately followed by
its matching plastic plug; repeat per pocket. Use a plastic implement to seat each
plug below the rim. The nominal plug top is 0.2 mm below the completed surface.
Do not resume with anything proud. The magnet top is 15 mm below the pause plane;
the long plug separates it from the following layers. Actual magnetic attraction
to the hotend has not been measured. The printer's normal native pause is used.

Pocket cross section: 10.4 x 3.4 mm. Plug: 10 x 2.95 x 14.8 mm, printed broad-face
down. In print coordinates the magnet occupies Z=3..23, plug Z=23..37.8, and cap
Z=38..40. Do not print the installed poses or reference section instead of the
explicit print-face STLs. Local peg supports and a 3 mm outer brim are included.

## What to test

Try ONE screwdriver at a time. Seat its shaft in the half-round or half-hex;
the root/collar bears on the flat 5 degree shelf. No collar threading required.
Try return, forward release, leaning and sideways rocking. Report the letter,
driver identity/tip, and whether it feels tight, good or loose. The blank feedback
CSV is included; a message such as "F — Craftsman #2 — good, little rocking" works.
The 17.5 mm test pitch is deliberately compact and is NOT final handle/grasp spacing.
Each strip is 150.4 mm wide, occupying six grid cells with the current tighter pegs.

| Letter | Nominal shaft | Actual CAD opening |
|---|---|---|
| A | 2 mm round | 2.3 mm diameter |
| B | 2.5 mm round | 2.8 mm diameter |
| C | 3 mm round | 3.3 mm diameter |
| D | 3.5 mm round | 3.8 mm diameter |
| E | 4 mm round | 4.3 mm diameter |
| F | 4.5 mm round | 4.8 mm diameter |
| G | 5 mm round | 5.3 mm diameter |
| H | 5.5 mm round | 5.8 mm diameter |
| I | 6 mm round | 6.3 mm diameter |
| J | 6.5 mm round | 6.8 mm diameter |
| K | 7 mm round | 7.3 mm diameter |
| L | 7.5 mm round | 7.8 mm diameter |
| M | 8 mm round | 8.3 mm diameter |
| N | 6.35 mm / quarter-inch hex | 6.55 mm across flats |
| O | 6.35 mm / quarter-inch hex | 6.75 mm across flats |
| P | 6.35 mm / quarter-inch hex | 6.95 mm across flats |

Round seats add 0.15 mm radial clearance. N/O/P add 0.10/0.20/0.30 mm per hex face.
Choose by feel, not only the nominal number: printed finish and real shafts vary.
The magnet is approximately 1.02 mm from a seated nominal shaft through the skin
and pocket clearance. Retention force is unmeasured; this is the experiment.

## Frozen settings and checks

0.20 mm layers, four walls, five top/bottom shells, 15% gyroid. Normal supports from
bed only, 50 degree threshold, bridge exemption; 3 mm outer brim. Arc fitting is
disabled in this job so every deposition segment can be audited directly. The
source user presets remain unchanged; frozen sources and overrides are included.
220 C nozzle and 55 C textured bed from the user's Generic PLA starter preset.
Orca reports its bed-temperature notice because the profile softening threshold
is 45 C. This notice is retained in verification/checks.json.

CAD solids, STEP round trips, loaded nominal shaft paths, pocket loading, native
three-plate structure, embedded-settings reslice, bed/exclusion bounds, startup
purge clearance, and each pause/first-cap layer checked. Emitted paths do not
intrude into the tested pocket cores before the pause. No mesh repairs reported.
Actual-path SVGs are in verification. GUI opening checks were not performed;
no physical print, tool-fit, adhesion or magnet-force qualification is claimed.
Nothing has been sent to a printer.

Native pause metadata follows OrcaSlicer v2.4.2:
https://github.com/OrcaSlicer/OrcaSlicer/blob/v2.4.2/src/libslic3r/Format/bbs_3mf.cpp
