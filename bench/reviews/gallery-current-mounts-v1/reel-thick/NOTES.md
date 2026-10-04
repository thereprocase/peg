# reel-thick — current station mounts v1

Large solder reel. Fresh remount of the exact archived body, preserving its seats/cavities and capacity. Body translation relative to the original installed CAD: [0, 0, 0] mm. No scaling or smoothing. Exact CAD checks: removed retained-body volume 0 mm³; added material beyond the mounting wall 0 mm³. Original rear peg material is replaced.

Mount: columns [-25.4, 25.4] mm; hook row 0; conformal bearing rows []; PF07 #5 hoop row [2]. PF02 #9 upper ribs 0.50 mm and nominal clamp interference 0.49 mm at 3.94 mm board. Lower hoop has 0.8 mm arms, 2.95 mm clipped root and pose-specific correction. New rear interface symmetric difference from the shared recipe: 0 mm³. Continuous integral back wall, one valid solid.

Upper material: highest front Z 5.120 mm, 0.000 mm above the nominal 5.12 mm lip. Original forward body retained and fused into full-thickness integral receiver; no separate crown pad. All front material passed 1822 sampled board-plane poses with 0.05 mm maximum point step and 0.005 mm tessellation. This is a nominal reference-route obstruction screen, not a new continuous motion proof for intentionally interfering pegs. Physical fit, deformation, removal force and load rating remain untested.

Print pose: **right-cheek**, bare bounds **75.45 × 58.94 × 74.20 mm**. Planar bed contact 3140.66 mm². Forward-body lowest print Z 0.000 mm. Coplanar triangles on selected body cheek / bottom and integral receiver; bed contact is geometric, not adhesion qualification. Hoop flex in print coordinates [-1.0, 0.0, 6.123233995736766e-17] is in the layer plane. The bare body fits the recorded P1S 256 × 256 × 250 mm envelope after avoiding its 18 × 28 mm front-left exclusion; placements are recorded in report.json.

**Bare CAD/mesh inputs only.** Accessible local peg supports and any body overhangs/bridges need fresh support and toolpath review. No slice, printer action, physical test or support-free claim accompanies this update. Old G-code/3MF, old peg-fit evidence and any abandoned crown-pad builds do not qualify it. Check the original holder-specific assembly procedure, magnet pauses/closures and loose components; only this mounted body has changed.

Evidence: report.json, mesh-checks.json and native-checks.json. Exact input/source hashes in report.json; source snapshot in bench/source/gallery_current_mounts_v1. Root owns derived GLB/PNG presentation and public packaging.
