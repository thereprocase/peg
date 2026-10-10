# Fit spectrum v5 — three connected five-slot coupons

Print the supplied flat bases without auto-orienting. Each coupon has five six-flat bores labelled with its size and A–E, full straight guides, a separate 0.8 mm entrance and a square 3 mm floor with a 1 mm through vent.

| Letter | Clearance per flat | Total across flats |
|---|---:|---:|
| A | 0.10 mm | 0.20 mm |
| B | 0.15 mm | 0.30 mm |
| C | 0.19 mm | 0.38 mm |
| D | 0.23 mm | 0.46 mm |
| E | 0.28 mm | 0.56 mm |

C matches the latest requested allowance; A matches the snug v3 target. Guides are 40 mm for 3 and 5 mm, 56 mm for 7 mm. The 3E bore allows full rotation geometrically. Choose the smallest clearance that seats fully and removes comfortably without forcing, then compare rocking and rotational play. Report **3 mm = _, 5 mm = _, 7 mm = _** after physical testing; no best letters have been established.

The rack prints on its left end. These bores retain the corresponding horizontal shaft and hex-flat orientation relative to the bed: 3 mm uses lower-tier grip turn 90 degrees, 5 mm uses upper-tier 65 degrees. 7 mm uses the upper-tier orientation as a trial because 7 mm is not in Bondhus set 13189. All have 20 degrees of heading in the bed plane, corresponding to the installed rack's forward tilt. Source flags independently set grip roll and bed heading.

```bash
.local-runtime/freecad-python bench/source/tee_racks_v1/fit_spectrum_v5.py --out bench/reviews/tee-fit-v5-spectra --angle-3 90 --angle-5 65 --angle-7 65 --heading 20
.local-runtime/freecad-python bench/source/tee_racks_v1/tools/check_fit_spectrum.py bench/reviews/tee-fit-v5-spectra
```

Individual STL/STEP files contain one connected coupon. The `three-spectra` files and FreeCAD document contain all three arranged separately on one plate. FreeCAD properties are metadata; rebuild the source to change the geometry.

Use the owner's actual printer/filament profile and calibrated compensation. Inspect horizontal roofs, supports, vents and toolpaths before printing. Native insertion, floor/vent, rotational-stop and export checks pass. Slicing and physical selection remain pending. This box has no configured printer connector or local owner-profile slicer, so **no overnight job has been submitted**. No G-code is published. The earlier complete racks retain their previous fit geometry.
