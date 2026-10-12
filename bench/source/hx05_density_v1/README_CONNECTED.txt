HX05 connected reinforcement v3

The physical body, tested cuts, pegs and fixed print face are unchanged.
V3 corrects the solid-mask placement left behind during the v2 mass reduction:
ribs attach inside the actual solid socket band, not the older outer sleeve
radius. Their roots extend into the receiving rear wall skin and stay within
the plate height. DensityContinuousRibs must remain enabled for this layout.

Three continuous walls / 5% gyroid bulk; four independent 100% infill masks.
Masks are nonphysical slicer controls. Never fuse them into the print part.
Solid perimeter skins are also present outside the masks; they appear gray in
the mask drawings and blue in the actual toolpath comparison.

Fresh owner P1S 0.4 mm / 0.20 mm / calibrated ASA slice estimates:
13190 inch: 520 g / 18h 39m.
13189 metric: 488 g / 17h 09m.
33034 Torx: 331 g / 12h 00m.
All use normal/grid supports. Nominal unscaled projects carry no private profile
or G-code. Select the actual calibrated preset and compensate once.

Extract the full bundle and run SETUP_DENSITY_FANS.FCMacro to install/reload all
three portable modules. Open the matching FCStd. 86 DraftedHolder is the physical
part. DensityHelpers contains the four masks. Use DensityParameters' Density only
property group. Original RibWidth/RootWidth still affect outside construction;
DensityRibWidth/DensityRootWidth affect modifiers only. FrozenHistory features
are cached older constructions; leave their proxies disabled.

Native checks verify rib/socket-band overlaps at three stations per tool, 78
stations across 26 tools. These are sampled geometric connection checks, not
physical load/fatigue ratings. Actual Orca paths before/after are included for
review. Body identity allows reuse of the unchanged geometry/access evidence.
Torx full-shank fit and small-key rotation retain the prior limitations. Printed
fit, support removal and reduced-material strength remain separate checks.
