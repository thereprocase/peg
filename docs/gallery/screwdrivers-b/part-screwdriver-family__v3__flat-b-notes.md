# Flat square screwdriver seats: B v3

The user requested diagonal-bed alternatives to the upright A family, then
identified the actual escape direction: handle backward, shaft forward. Early
front-stop revisions addressed the wrong motion and were not published. The
user proposed a square flat seat; this is that simpler A/B form trial.

Four racks retain counts, pitches, modular widths and canonical pegs. B has
5.12 mm-deep shallow square recesses with flat floors and open-front shaft slots.
Tools are vertical for level flat bearing; A retains its 5-degree tilt. Rear entry
facets and a pointed underside opening keep the selected 55-degree bed pose
support-free in the review slices. No tall backrest or cone is used.

All 19 nominal flat-handle tool paths pass at 14 mm lift followed by forward
withdrawal. Grasp clearances match A. Bearings and seated forward obstruction
were checked. A separate test rotates the handle toward the board and shaft
toward the user about the rear heel; rotating about the shaft center would
incorrectly drive the front base into the floor and overstate restraint.

That test is a LIMIT, not a pass for universal anti-tip function: nominal flat
handles first collide near 28 degrees, smaller handles later; the smallest test
in SD04 with 0.5 mm lift is unobstructed through 60 degrees. No force, friction,
full escape search or rounded-shoulder qualification is claimed. Exact shoulder
geometry and a physical trial are still needed to settle the shaft-pop concern.

Orca P1S / 0.4 nozzle / inherited PETG review profile / 0.2 mm layers. Normal auto
supports ON, threshold 50 degrees, internal allowed, critical-only OFF, bridge
exemption OFF, brim/raft OFF. All four yield zero actual support extrusion
segments, zero repairs, within the plate. The inherited profile warns about bed
temperature; it is not a released manufacturing profile. No G-code or print sent.

Geometric sections at 0.2 mm Z and 0.25 mm XY find no new unanchored component
above 0.2 mm2. Full-surface screen includes pegs; only about 0.00187 mm2 of fixed
peg facets fall below 49.5 degrees, with a minimum about 48.3. All four models
are single valid solids and reimported STEP; meshes are closed. The bed is placed
using the actual planar face, not the conservative OCC trimmed-surface bounds.

Sources: source/screwdriver_flat_b.py; render_screwdriver_diagonal_b.py -- --flat;
slice_screwdriver_diagonal_b.py --flat; check_screwdriver_diagonal_layers.py --flat;
check_screwdriver_flat_rock.py. Canonical fit is reference/peg-fit.scad on each build.
Original tip floors are only references in the views, unchanged and outside the
support-free claim. Existing A geometry and votes were preserved.
