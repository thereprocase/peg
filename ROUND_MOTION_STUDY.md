# Round peg revision: geometry and full motion study

The default anchor uses a **5.6 mm round upper bearing neck and lower locator**, with a **4.8 mm round retaining tongue**. The neck and tongue form one continuous solid through a rounded junction. The lower locator has a conical lead-in. Neither bearing section has a flat or rectangular corner.

The default 3.94 mm board / 6.35 mm hole configuration passes a continuous three-dimensional insertion and removal study at **20.875° maximum tilt** and **1.07 mm reference-point lift**. It leaves **0.47 mm fore–aft travel before the rear shoulder catches**. The calculated rear-shoulder stop occurs at approximately **0.675° outward rocking** about the lower spine land. These dimensions describe ideal geometry, not insertion force or a load rating.

## Round sections and holding geometry

The round surfaces remove the rectangular bearing corners and permit a larger neck section. Clearance still means the pin initially touches a limited part of the bore under load; this design does not claim contact around the whole hole or a known bearing pressure.

| Section | Area | Elastic section modulus |
|---|---:|---:|
| Previous 4.0 × 3.6 mm rectangular neck | 14.40 mm² | 8.64 mm³ |
| New 5.6 mm circular neck | 24.63 mm² | 17.24 mm³ |
| New 4.8 mm circular retaining tongue | 18.10 mm² | 10.86 mm³ |

The round neck has approximately twice the previous geometric section modulus; the smaller round tongue also exceeds the previous rectangular section. Those comparisons do not establish twice the printed strength. Material, filament paths, layer adhesion, the junction, and the board all affect the load capacity.

The default diametral clearance is **0.75 mm**. The profile places the circular neck against the bottom of the hole at the physical seated pose. The snug rear shoulder limits forward travel, while the lower round locator controls the second mounting point. Downward loading can take up the small remaining movement. No spring preload or zero-rattle claim is made.

## Verified board presets

Board thickness and hole diameter remain independent parameters. The thicker-board presets use a smaller bearing diameter to preserve a verified installation path. Each uses the same 4.8 mm retaining tongue.

| Actual board thickness | Actual hole diameter | Bearing / locator diameter | Maximum tilt | Maximum lift | Minimum modeled rear space | Pull travel to stop |
|---:|---:|---:|---:|---:|---:|---:|
| 3.940 mm, default | 6.350 mm | 5.6 mm | 20.875° | 1.070 mm | 6.62 mm | 0.47 mm |
| 4.190 mm | 6.350 mm | 5.6 mm | 20.875° | 1.170 mm | 6.62 mm | 0.47 mm |
| 4.7625 mm | 6.350 mm | 5.4 mm | 20.375° | 1.320 mm | 6.45 mm | 0.47 mm |
| 6.350 mm | 6.350 mm | 5.2 mm | 19.750° | 1.795 mm | 6.29 mm | 0.47 mm |
| 3.940 mm | 7.14375 mm, 9/32 inch | 5.6 mm | 13.000° | 0.395 mm | 5.30 mm | 0.47 mm |

Rear-space values are conservative geometric minima for the modeled anchor during its path. Allow additional practical space for installation and board irregularity. The larger-hole preset adjusts the rear shoulder position but retains a 5.6 mm bearing diameter; its diametral clearance is consequently larger. Arbitrary intermediate thicknesses and diameters require their own run of the study.

## Design decisions from the search

A uniform round hook could install with 5.0, 5.2, and 5.4 mm diameters. Their initial paths required approximately 19°, 20.75°, and 23.25° tilt. The bounded search did not find a path for the compact uniform 5.6–5.9 mm candidates.

Longer, gentler tongues provided another option, but they increased rear projection and required more fore–aft clearance to accommodate the reserved bore clearance. A 5.6 mm uniform candidate with a 5 mm run, 2 mm rise, and 0.7 mm pull clearance also found a path. The selected stepped diameters retained the compact 5 mm run / 3 mm rise and the tighter 0.47 mm pull clearance.

A 5.8 mm bearing neck with a 4.0 mm tongue found a path at 17.625°, but that tongue's section modulus was lower than the previous rectangular section. A 5.7 / 4.6 mm candidate also found a path. The final **5.6 / 4.8 mm** pair preserves a stronger tongue while still providing a close round fit and a continuously verified path.

For the 6.35 mm-thick board, the search found the selected 5.2 / 4.8 mm pair; it did not find paths for the tested 5.3–5.6 mm bearing diameters with that tongue. A failed or timed-out bounded search is not a proof that every possible motion or alternative geometry is impossible.

## Coordinates and physical seating

X runs across the board; Y points toward the user; Z points upward. The board front is Y = 0 and its rear is Y = −thickness. Hole-row centers are Z = 0 and −25.4 mm. Positive rotation about X tips the lower end away from the board.

A pose applies:

`Y′ = cos(θ)Y − sin(θ)Z + pose.y`

`Z′ = sin(θ)Y + cos(θ)Z + pose.z`

The physical seated pose is **(−0.15 mm, −0.12 mm, 0°)**. The release pose is **(−0.12 mm, 0 mm, 0°)**. Installation reverses the removal path: set the angle in clear space, thread the retaining tongue, rotate and lower the body while the lower locator enters, then close the intended bearing contacts.

Straight pulling stops after 0.47 mm, and straight lifting stops after approximately 0.282 mm. The demonstrated removal motion combines lift, rotation, and translation. It remains intentionally removable and is not a positive lock against every possible handling motion.

## Three-dimensional clearance proof

The old constant-width rectangular proof cannot validate these circular parts. This revision uses the actual round construction and three complementary bounds.

**Upper neck and tongue.** The CAD model unions two capsules: cylinders with spherical ends. Their centerline lies in X = 0, and the spheres along each segment have the segment's radius. For a sphere center in this plane, the nearest board material around either cylindrical hole also lies in this plane. The center-plane distance therefore gives the exact sphere-to-board collision condition. The solver then encloses each true capsule in a circumscribed polygon, adding less than 0.001 mm to the radius. This is a conservative enclosure, not an inscribed mesh approximation.

**Lower locator.** The solver divides each half of the round locator into 96 X slabs. For every slab it uses the largest cylinder section within that slab and the smallest circular-hole section within that slab. It ignores the helpful nose chamfer, which enlarges the checked object. These bounds cover every X position, including positions between slab boundaries. Rotation about X and translation in Y/Z keep every material point in its original slab.

**Spine.** The spine remains in front of the entire board slab. The solver uses the same rounded polygon and 12-segment corner setting as the CAD source, rather than substituting a smaller approximate profile.

The free-motion checks reduce the **physical bore radius by 0.10 mm**. The default path received **5,733 continuous interval certificates** and **2,038 additional dense verification frames**. Every tested preset passed.

For each interval, the solver computes the clearance at its midpoint and bounds the motion of every point by:

`|Δtranslation| / 2 + 2R sin(|Δangle| / 4)`

Here R bounds the point's distance from the rotation axis in the Y–Z plane. If the conservative midpoint clearance exceeds this displacement, the entire interval clears. Otherwise the solver bisects the interval. This proves clearance between displayed frames. The final workflow also restores original search waypoints when a visually smooth shortcut fails the continuous check; one such narrow interference was caught during this revision.

The vectorized locator-distance implementation was cross-checked against independent polygon-distance calculations for all 96 slabs at five representative poses; the maximum difference was zero at reported precision. Separate CAD-kernel sampled checks provide an independent check on the actual union of cylinders, spheres, spine, and chamfer.

## Exact treatment of the final contacts

The final seating step intentionally reaches zero clearance, so the circumscribed free-motion bounds do not certify that step. A separate calculation uses the exact circular primitives:

- Sweep each capsule centerline through the final pure translation and compare its minimum board distance with its true radius. The neck reaches exactly 2.8 mm distance for its 2.8 mm radius; the tongue retains clearance.
- Bound the entire lower locator by its full circular section. Its maximum radial extent reaches exactly the physical bore radius, 3.175 mm. The conical nose is a subset of that cylinder.
- Confirm that the spine's minimum front coordinate remains nonnegative and reaches zero only at the intended contact.

Thus the study permits the intended bearing contacts while continuing to reject penetration. Insertion and removal traverse the same swept volume in opposite directions.

## Reproduce or change a parameter

`round_motion.py` reads the geometry contract from `round_anchor.py`; it does not require exploratory path files.

```bash
python round_motion.py --default-only
python round_motion.py
python round_motion.py --thickness 4.7625 --peg-diameter 5.4 --tongue-diameter 4.8
```

The first command regenerates the default study. The second checks all five presets. The third checks a custom configuration. Use `--output-dir` to keep a new study separate. `round_motion_results.json` contains the default path; `round_motion_presets.json` contains all preset parameters, poses, and certificates.

These are ideal rigid-body geometry results. They do not measure print tolerance, insertion force, bearing stress, creep, fatigue, impact, or board breakout. Print and trim a fit sample, then check the complete mounted object and its printing orientation. Any sacrificial print scaffolds must be removed before using the certified installation path.
