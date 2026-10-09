# Fit coupon v4 — increased clearance and vents

The v3 print was snug. This revision adds **0.18 mm total across flats**: **0.19 mm per flat / 0.38 mm total**, giving the 5 mm key a **5.38 mm AF bore**. Each square 3 mm socket floor has a **1 mm diameter through vent**, retaining a shoulder to stop even the 2 mm shaft. The straight guides remain 40 mm for L2, T2.5 and T5, and 80 mm for T10, plus the 0.8 mm entrance. Handles stay flat-to-flat. F19 labels identify the increased clearance.

Build using FreeCAD 1.1.3:

```bash
.local-runtime/freecad-python bench/source/tee_racks_v1/fit_coupon_v4.py --out bench/reviews/tee-fit-v4-guide40
.local-runtime/freecad-python bench/source/tee_racks_v1/tools/check_fit_coupon.py bench/reviews/tee-fit-v4-guide40
```

The coupon source specifies the revised clearance and vent; the unchanged socket policy supplies guide lengths. Sources and native/export checks accompany the CAD. The full racks retain their earlier geometry pending this trial. Actual slicing, physical fit and loads remain unqualified. Use the owner's printer and filament profile; no G-code is supplied.

At this allowance the L2 bore permits full rotation; T2.5 permits approximately ±26.1°, T5 ±8.72° and T10 ±4.02°. Guide length limits rocking, while hex clearance sets rotational play. The prior v3 release is preserved as history.
