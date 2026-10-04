# MH01 — current station mounts v1

MH01. Fresh remount of the exact archived body, preserving its seats/cavities and capacity. Body translation relative to the original installed CAD: [0, 3, 2] mm. No scaling or smoothing. Exact CAD checks: removed retained-body volume 0 mm³; added material beyond the mounting wall 0 mm³. Original rear peg material is replaced.

Mount: columns [-38.099999999999994, 38.099999999999994] mm; hook row 0; conformal bearing rows []; PF07 #5 hoop row [1]. PF02 #9 upper ribs 0.50 mm and nominal clamp interference 0.49 mm at 3.94 mm board. Lower hoop has 0.8 mm arms, 2.95 mm clipped root and pose-specific correction. New rear interface symmetric difference from the shared recipe: 0 mm³. Continuous integral back wall, one valid solid.

Upper material: highest front Z 11.149 mm, 6.029 mm above the nominal 5.12 mm lip. Original functional body shifted 3 mm forward / 2 mm up, overlapping the 5.4 mm receiver by 2.4 mm; no hook shortening or separate crown pad. All front material passed 1429 sampled board-plane poses with 0.05 mm maximum point step and 0.005 mm tessellation. This is a nominal reference-route obstruction screen, not a new continuous motion proof for intentionally interfering pegs. Physical fit, deformation, removal force and load rating remain untested.

Print pose: **flat-top**, bare bounds **99.60 × 60.70 × 40.00 mm**. Planar bed contact 4190.17 mm². Forward-body lowest print Z -0.000 mm. Original planar top and any coplanar receiver; hook material does not set the bed plane. Hoop flex in print coordinates [1.0, 0.0, 0.0] is in the layer plane. The bare body fits the recorded P1S 256 × 256 × 250 mm envelope after avoiding its 18 × 28 mm front-left exclusion; placements are recorded in report.json.

**Bare CAD/mesh inputs only.** Accessible local peg supports and any body overhangs/bridges need fresh support and toolpath review. No slice, printer action, physical test or support-free claim accompanies this update. Old G-code/3MF, old peg-fit evidence and any abandoned crown-pad builds do not qualify it. Check the original holder-specific assembly procedure, magnet pauses/closures and loose components; only this mounted body has changed.

The original flat top is retained as the bed face; full-height hooks are not truncated. Rotation about X by 175° leaves X-directed hoop flex exactly in the layer plane. The 3 mm forward / 2 mm upward body shift retains 2.4 mm of overlap with the receiver and preserves all magnet cavities and functional seats. Old sliced magnet-pause layers do not apply.

Evidence: report.json, mesh-checks.json and native-checks.json. Exact input/source hashes in report.json; source snapshot in bench/source/gallery_current_mounts_v1. Root owns derived GLB/PNG presentation and public packaging.
