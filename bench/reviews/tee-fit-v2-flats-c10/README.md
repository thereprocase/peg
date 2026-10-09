# Straight-guide fit coupon v2 — flat-to-flat, half clearance

Owner reported weak small-key seating, roughly 15° rocking of the 2 mm L-key, and complete rotation in both 5 mm tests of the published HX04 v2 coupon. The owner confirmed that the T-handle axis runs **flat-to-flat**, and requested halving hex clearance.

This coupon has three independent blocks: **L2 F10**, **T2.5 F10**, **T5 F10**. F denotes flat-to-flat orientation along design Y; 10 denotes **0.10 mm per-flat clearance**, adding **0.20 mm total across flats**. The 5 mm bore is **5.20 mm AF**. Dimensions are CAD targets; printed dimensions and fit remain to be measured.

| Tool | Bore AF | Burial along shaft | Straight hex guide |
|---|---:|---:|---:|
| 2 mm L-key | 2.20 mm | 14.6 mm | 13.8 mm |
| 2.5 mm T-handle | 2.70 mm | 12.0 mm | 11.2 mm |
| 5 mm T-handle | 5.20 mm | 20.0 mm | 19.2 mm |

There is a **0.8 mm entrance chamfer**, a straight six-flat bore and a square-ended **3 mm floor**. No rounded seating chamber, widening flare or sloped floor. The original hex ceiling is preserved; its short flat bridge requires inspection in the owner's actual slice. This is a new trial geometry, not a calibrated production fit or a support-free claim.

- `HX05-fit-v2.FCStd`: native FreeCAD solids arranged in left-end print orientation; dimension properties are metadata, rebuild with the Python source to change the geometry.
- `HX05-fit-v2__left-end__print.stl`: bare print-preparation mesh of all three blocks. Use the owner's printer/filament profile and review bore roofs, supports and shrink compensation before printing. No G-code is included.
- `HX05-fit-v2__left-end__print.step`: same assembled print pose in native STEP.
- Individual `*__installed.step` files: socket axis is design Z; handle flat-to-flat direction is design Y.
- `fit-v2-check.json`: native validity, rotational stops, floor probes, dimensions and source/font hashes.
- `old-seat-audit.json`: audit of the actual published HX04 native coupon. Both old 5 mm sockets interfere with a nominal 5 mm shaft at 30° by only about **0.34–0.41 mm³**, concentrated in the short neck; ideal CAD still has a stop, but the owner’s print does not provide effective restraint.

The new 5.20 mm bore has a theoretical one-sided rotational allowance of **4.25°**, or **8.49° total**. Native 0.25° rotation samples first intersect at 4.25°. That remains clearance fit, rather than zero-play or mechanical locking. The same checks confirm positive stops for the other two blocks and solid floors.

Built and checked locally with **FreeCAD 1.1.3 / OpenCascade 7.8.1** from the checksum-verified official AppImage. The source is `bench/source/tee_racks_v1/fit_coupon_v2.py`. Reproduce from the repo root:

```bash
bash bench/source/tee_racks_v1/tools/setup_freecad_linux.sh
.local-runtime/freecad-python bench/source/tee_racks_v1/fit_coupon_v2.py --out bench/reviews/tee-fit-v2-flats-c10
```

The published HX04 source and files remain unchanged as history. HX05's hex clearance and handle orientation are corrected; its full racks still retain the earlier seating shape until this straight-guide coupon establishes fit. Physical seating, rotation, extraction and print quality of this new coupon remain pending.
