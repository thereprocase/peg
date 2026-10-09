# Fit coupon v3 — 40 mm minimum shaft hug

Owner's new rule: **at least 40 mm of straight guiding contact**, increasing to **8× shaft size for larger tools**. The **0.8 mm entrance chamfer is additional**. Hex clearance stays **0.10 mm per flat** and T-handle alignment stays **flat-to-flat**. Guides retain all six flats and end on a square 3 mm floor; there is no rounded/flared seating chamber.

| Coupon block | Bore across flats | Straight shaft hug | Burial including entrance |
|---|---:|---:|---:|
| L2 F10 | 2.20 mm | 40.0 mm | 40.8 mm |
| T2.5 F10 | 2.70 mm | 40.0 mm | 40.8 mm |
| T5 F10 | 5.20 mm | 40.0 mm | 40.8 mm |
| T10 F10 | 10.20 mm | 80.0 mm | 80.8 mm |

The same policy gives a 6 mm shaft 48 mm of hug and an 8 mm shaft 64 mm. The rack study uses across-flat size for hex tools and nominal point-to-point size for Torx proxies. F10 denotes flat-to-flat orientation and 0.10 mm clearance per flat, not 10 mm of guide.

`HX05-fit-v3.FCStd`, `HX05-fit-v3__left-end__print.step` and `HX05-fit-v3__left-end__print.stl` contain all four blocks in left-end print orientation. Individual `*__installed.step` files use design Z as shaft axis and design Y as handle flat-to-flat direction. Document dimensions are metadata; rebuild the source to change geometry.

Native FreeCAD validity, nominal insertion, positive rotational stops, square floor probes, STEP/FCStd reload and closed positive-volume meshes pass. See `fit-v3-check.json` and `export-check.json`. These establish geometry; **actual slicing and physical fit remain pending**. Use the owner's printer/filament profile, account for its calibrated compensation, and inspect the hex roofs and supports before printing. No G-code is included.

Build from the repository root with the local FreeCAD 1.1.3 runtime:

```bash
.local-runtime/freecad-python bench/source/tee_racks_v1/fit_coupon_v3.py --out bench/reviews/tee-fit-v3-guide40
.local-runtime/freecad-python bench/source/tee_racks_v1/tools/check_fit_coupon.py bench/reviews/tee-fit-v3-guide40
```

The single dimensional authority is `bench/source/tee_racks_v1/study/socket_policy.py`; source and policy hashes are recorded with the native checks. The earlier [v2 coupon](../tee-fit-v2-flats-c10/README.md) is history and has shorter guides.
