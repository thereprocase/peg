# Fit spectrum v6 — corrected HX04 fan print frames

V5 used the two-tier HX05 rack angles, not the HX04 fan. **Use v6 for the fan-angle test.** The same three connected coupons retain five lettered A–E slots, guide lengths 40/40/56 mm, a separate 0.8 mm entrance, square 3 mm floors and 1 mm through vents.

| Coupon | Shaft elevation above bed | Orientation authority |
|---|---:|---|
| 3 mm | 25.0982° | Actual HX04 T3 shaft and handle vectors |
| 5 mm | 38.5279° | Actual HX04 T5 shaft and handle vectors |
| 7 mm | 44.2220° | Normalized interpolation of HX04 T6/T8 vectors; no T7 exists |

Both shaft vectors **and hex-flat clocking** are transformed by the fan's left-cheek Y+90° print rotation. This tests the revised flat-to-flat fit, rather than the original corner-clocked seats. Flat feet preserve the angles. Keep the bases down; do not auto-orient. The feet and outer bodies are coupon geometry, not full fan structure.

| Letter | Clearance per flat | Total AF clearance |
|---|---:|---:|
| A | 0.10 mm | 0.20 mm |
| B | 0.15 mm | 0.30 mm |
| C | 0.19 mm | 0.38 mm |
| D | 0.23 mm | 0.46 mm |
| E | 0.28 mm | 0.56 mm |

C matches the latest requested clearance. Pick the smallest letter that seats fully and slides out comfortably without forcing, then compare rocking and rotation. 3E allows full rotation geometrically. Report **3 mm = _, 5 mm = _, 7 mm = _** after physical testing.

`fan_orientation_v6.json` records the actual shaft/bar frame, fan layout and source hashes, build environment and print rotation. To adjust an angle, change that orthonormal frame and rebuild; FreeCAD properties are metadata.

```bash
.local-runtime/freecad-python bench/source/tee_racks_v1/fit_spectrum_v6.py --out bench/reviews/tee-fit-v6-fan
.local-runtime/freecad-python bench/source/tee_racks_v1/tools/check_fit_spectrum_v6.py bench/reviews/tee-fit-v6-fan
```

Native source checks verify exact six-flat frame congruence, insertion, rotational stops or expected free rotation, floor shoulders, and vents remaining open after foot union. Delivered STL/STEP/FreeCAD exports are reloaded and checked. Actual owner-profile slicing, print submission and physical fit remain pending. Inspect the inclined bore roofs, undersides, supports and vents using the owner's calibrated printer/filament profile. No G-code is supplied, and no overnight print has been started from this box.
