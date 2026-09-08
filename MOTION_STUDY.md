# Pegboard anchor: motion and fit study

The final anchor threads through a 6.35 mm cylindrical hole in a 3.94 mm board at **19.25° maximum tilt**. Its verified path raises the reference point **0.82 mm** above the physical seated position. The study checks the complete hook, spine, and lower locator throughout insertion and reverse removal.

The default model has **0.47 mm ideal fore–aft travel before the retaining shoulder catches** and **0.69° outward rocking about the lower spine land**. These figures describe geometric freedom before contact. A cantilevered load can take up that freedom; the model does not claim a spring preload, zero rattle, or a rated holding force.

## Tested configurations

All dimensions below describe the actual modeled board and holes, independently. The 1/4-inch hole designation does not require a 1/4-inch-thick board.

| Board thickness | Hole diameter | Maximum tilt | Maximum lift | Required clear space behind board | Pull travel to stop | Rock to contact | Result |
|---:|---:|---:|---:|---:|---:|---:|---|
| 3.940 mm, default | 6.350 mm | 19.25° | 0.82 mm | 5.55 mm | 0.47 mm | 0.69° | Pass |
| 4.190 mm | 6.350 mm | 19.25° | 0.92 mm | 5.55 mm | 0.47 mm | 0.68° | Pass |
| 4.7625 mm | 6.350 mm | 19.75° | 1.17 mm | 5.55 mm | 0.47 mm | 0.66° | Pass |
| 6.350 mm | 6.350 mm | 20.00° | 1.77 mm | 5.55 mm | 0.47 mm | 0.62° | Pass |
| 3.940 mm | 7.14375 mm, 9/32 inch | 9.75° | 0.22 mm | 3.90 mm | 0.47 mm | 0.68° | Pass |

The backside dimensions are geometric minima for the anchor alone. Allow additional practical space for board irregularity, installation tolerance, and nearby obstructions. The last row uses the corresponding hole-specific geometry; changing only the board hole while retaining a smaller-hole anchor changes its fit.

## What changed during design

A short, steeper retaining tongue could thread through the default board with a 3.1 mm neck. Increasing that neck to 3.6 mm prevented the original path. Extending the tongue run to 5 mm and using a 3 mm rise made the stronger 3.6 mm neck feasible across the tested board thicknesses.

The first broadly compatible profile left approximately **2.12 mm pull travel and 3.02° rocking**. Those values undermined the requested firm rest position. Moving the elbow forward and searching simultaneous lift, rotation, and translation reduced the final values to **0.47 mm and 0.69°**. The final path preserves a 0.10 mm allowance in the limiting bore half-height during free threading.

The neck has a 4.0 × 3.6 mm section: 14.4 mm² area and 8.64 mm³ elastic section modulus for bending in the studied plane. These section properties describe geometry only. They do not establish an FDM allowable stress or load rating.

## Coordinate and motion contract

- X spans the width of the hook. The solid extends from X = −2 mm to +2 mm by default.
- Y points toward the user. The board front lies at Y = 0; its rear lies at Y = −thickness.
- Z points upward. Hole centers lie at Z = 0 and Z = −25.4 mm.
- Positive rotation tips the lower end of the spine away from the board.
- A pose transforms each profile point as `Y′ = cos(θ)Y − sin(θ)Z + pose.y`, `Z′ = sin(θ)Y + cos(θ)Z + pose.z`.

The physical seated reference pose is **(Y, Z, θ) = (−0.15 mm, −0.12 mm, 0°)**. This places the spine land against the board face and the upper neck against the limiting bore surface. The release pose **(−0.12 mm, 0 mm, 0°)** opens those contacts. The reference pose `(0,0,0)` does not define the snug anchor's seated condition.

Install by setting the tilt in clear space, threading the upper tongue, and bringing the lower end toward the board while lowering the anchor. The short chamfered lower locator enters during the last part of rotation. Reverse the same path to remove the anchor. The dense animation follows the actual certified pose sequence.

The default model blocks a straight pull after approximately 0.47 mm and a straight upward slide after approximately 0.28 mm. Those motions alone do not extract the anchor. Rotation combined with translation provides the verified release path. This does not make the anchor a positive lock against every arbitrary handling motion.

## How the clearance proof works

The profile has constant X width. A cylindrical hole of diameter `D` has its smallest available vertical half-height across that width at the outside X faces:

`h = sqrt(D² − width²) / 2`

For D = 6.35 mm and width = 4.0 mm, `h = 2.465892 mm`. The free-motion solver reduces that half-height by **0.10 mm**. It checks the entire Y–Z profile against the remaining board material, including both holes. This reduction accounts for the full rectangular neck width; a centerline-only section would overstate clearance.

An A* search explores coupled translation and rotation, then removes unnecessary waypoints. Sampled checks assist the search and provide a reproducible animation. A separate continuous calculation certifies every retained free-motion segment:

1. Evaluate the midpoint pose of an interval.
2. Compute the shape's distance to the board obstacle with the reduced bores.
3. Bound the displacement of every profile point anywhere in the interval by `|Δtranslation|/2 + 2R sin(|Δangle|/4)`, where R is the greatest distance from the rotation origin to any profile vertex.
4. Accept the interval only when the midpoint clearance exceeds that bound. Otherwise, bisect and repeat.

Consequently, the proof covers the motion between animation frames. It does not infer clearance from a few attractive poses. The default path required 1,434 accepted interval bounds and 1,962 additional dense verification frames. All five configurations completed without a colliding frame.

The final contact segment intentionally ends at zero clearance. It uses a separate exact polygonal translation sweep: union the endpoint profiles and the quadrilateral swept by every boundary edge, then intersect that swept region with the physical board. The intersection area is zero. Insertion and removal traverse the same swept volume in opposite directions.

The reported tiny positive residuals in individual interval certificates are margins in the mathematical bound, **not printer tolerances**. The 0.10 mm bore half-height allowance applies to the certified free-threading segments; the final seating segment closes the intended contacts.

## Parametric retention clearance

`pull_clearance` defaults to 0.47 mm. The generator derives the elbow position instead of treating a negative elbow offset as a physical gap. With `r = neck_height/2`, `m = tongue_rise/tongue_run`, and the half-height `h` above:

`elbow_offset = pull_clearance − front_gap − (2h − r)/m + r sqrt(1 + 1/m²)`

This positions the straight retaining shoulder to give the requested pull clearance. Polygonal arc discretization accounts for the approximately 0.00006 mm difference in the measured result. `elbow_offset=None` in `get_parts()` requests this automatic calculation; an explicit numeric override is an advanced geometry setting. Retention and motion must be rechecked after arbitrary parameter changes.

## Scope and reproduction

Run `python motion_design.py` to regenerate `geometry.json` and `motion_results.json`. `make_profile(params)` returns the reusable profile points; `get_parts(params)` also returns the component polygons and resolved parameter values. Both JSON files contain the parameters used for every result.

The study assumes a flat rigid board, ideal cylindrical bores, exact modeled geometry, and planar motion with no yaw or roll. It does not simulate print error, creep, fatigue, impact, board breakout, local crushing, insertion forces, or material flexibility. Print a fit sample before committing a large mount. Validate the complete attached mount against its own installation envelope; an accessory extending behind or beside the spine can obstruct a path that the anchor alone clears.
