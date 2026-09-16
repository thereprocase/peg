# SD01–SD04 v2: human factors and print construction

Hold → Grab → Return → Build: support the handle shoulder, expose the grip, let
the shaft enter from the front, then settle into a short seat. A single resting
axis leans 5 degrees out. Tool rotation is unnecessary during the planned path.
The fork slot continues down the full supporting mass; an early audit caught and
removed a lower ledge before the outputs were accepted.

## NASA principles applied to this bench (not NASA certification)

NASA-STD-3001 Volume 2 section 7.6 asks designers to consider use frequency,
interference, restraint, reach and identification when arranging stowage. Here:

- Dedicated open slots make an absent tool conspicuous.
- High-use handles belong near the user's natural reach, not high on the board.
- Every intended removal path is checked with neighbors present.
- Seated and partly seated shoulders meet a positive forward obstruction.
- The user does not operate a latch, undo a fastener or use a second hand.

Source: https://www.nasa.gov/reference/7-0-habit-ability-functions-vol-2/ (7.6).

Section 4.1 calls for accommodation of the relevant user population and posture.
Our 7–11 mm radial hand allowances are explicit engineering assumptions, NOT
NASA percentile values. Whole grasp cylinders and widening approach cones are
checked, but the user's hand/clothing and no-look behavior need a real trial.
Source: https://www.nasa.gov/reference/4-0-physical-characteristics-and-capabilities-vol-2/
Background: https://www.nasa.gov/human-integration-design-handbook/

## Tool dimensional evidence

Wiha's 261P table lists PH00/PH000 blades 2.5 mm diameter and 40/60 mm long with
9 mm handles; PH0/PH1 use 3/4 mm shafts, 50–80 mm visible lengths and 18 mm handles.
The same page has contradictory headline dimensions, so the named technical
table, not the headline bounding size, informed the planning envelope.
https://wiha.com/gb/en/tools/screwdrivers/precision-screwdrivers/picofinish/phillips/picofinish-fine-screwdriver/42416

Craftsman CMHT68012 lists PH0/PH1 and 1.4/2.0/2.4/3.4 mm slotted tips but no
handle sizes. It is not automatically covered by SD01's 9 mm handle assumption.
https://www.craftsman.com/en-us/product/cmht68012/6pc-jewelers-precision-screwdriver-set

CMHT65618V lists PH1–PH4 and slotted sizes through 3/8 inch, with blades through
7 inches; its large tools have bolsters. CMHT65026 is titled 3/8 × 8 inches but
its Includes field inconsistently says 3/16 cabinet. SD04 uses 9.525 mm blade
and 203.2 mm length as a design envelope, not a reverse-engineered tool.
https://www.craftsman.com/en-us/product/cmht65618v/v-series-8pc-screwdriver-set
https://www.craftsman.com/en-us/product/cmht65026/38-x-8-slotted-acetate-screwdriver

Standard 30 mm and large 40 mm handles, shoulder profiles, grip lengths and shaft
spacing are provisional. Check the actual shoulder and any wrenching bolster.
12-inch drivers need their floor lowered; those lengths are not validated here.

## Verification boundaries

All eight mounted bodies are valid single solids with STEP reimport and closed
STLs. Every peg fetches reference/peg-fit.scad at build time. Nominal interference
is the existing accepted experiment, not a new physical force measurement.
The planned path uses 14 mm lift and 100 mm forward motion, sampled against
neighbors, floor and board. Reverse motion returns the tool. Each shoulder must
hit the intended seat after 0.15 mm downward movement. A forward slide from
seated and 2 mm raised positions must hit the seat. These are collision and
bearing-location checks, not contact-force, friction or bump simulations.

Each rack/floor prints upright. Straight 55-degree main undersides, 18/24/32/40 mm rack
foot depths, open-front shaft lanes and a steeper lower throat relief address curling
and inaccessible supports. The unchanged rear pegs need small build-plate
supports. Triangle-normal audit excludes the bed and reports peg support area
separately; it does not replace a layer preview. No slicer or print job was run.

Next acceptance: confirm actual shoulder/bolster fit, handle grasp and blind
return with one representative small and large tool. Approve the forms before
Orca layer verification. Do not infer certification from this study.

A v2: broader permanent foundations, shorter bodies, unchanged working seat geometry. See the foundation audit for actual contact area and geometric centroid margins. No calibrated mm2/g threshold, adhesion strength or overturning FOS is claimed.
