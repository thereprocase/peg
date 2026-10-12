HX05 lightweight density revision v2

Same outside body, tested socket cuts, vents, pegs and chosen print face as v1.
The physical print meshes are byte-identical. Only printed internal structure
changes: 5% gyroid bulk / three continuous walls, with four independent 100%
infill masks. All recorded review slices use normal/grid supports.

SOLID ZONES
1.6 mm bed-face foundation; 1.2 mm bands at socket walls and lead-ins; solid
socket floors; 1.2 mm sleeve-to-back load-path plates with 2.5 mm root widths;
local 5.5 mm radius peg-root discs, 8 mm root depth and collector belts.
There are no local wall-count overrides: those created unnecessary shells at
modifier boundaries. Root and sleeve regions are reinforced by solid masks.

FREECAD
Extract the full bundle and run SETUP_DENSITY_FANS.FCMacro once. The three
portable modules are required for future recomputes. 86 DraftedHolder is the
physical part. Toggle DensityHelpers to inspect the nonphysical masks; never
fuse them into the body. Edit the Density only — outside fixed property group
on DensityParameters. Original RibWidth/RootWidth still control outside
construction; the new DensityRibWidth/DensityRootWidth affect modifiers only.
The fields BaseInfill and WallLoops record slicer intent, not CAD porosity.

ORCA
Open the 3MF as a PROJECT. It contains one physical normal part, four Modifier
parts at 100% infill and one socket support blocker. Bulk should read 5% gyroid
and three walls. Choose your actual calibrated printer/filament profile, keep
normal/grid supports for the reviewed preparation and compensate once.
All downloads are nominal/unscaled. No private profile or G-code is included.

Recorded owner P1S 0.4 mm / 0.20 mm / calibrated ASA estimates:
13190 inch: 503 g, 18h 20m.
13189 metric: 463 g, 16h 34m.
33034 Torx: 317 g, 11h 41m.
These are slicer estimates, not measured print masses or strength ratings.
The material reduction changes stiffness and load capacity. Previous structural
estimates do not qualify it; printed fit, support removal and loads are separate.
Torx full-shank fit and small-key rotation retain the previous limitations.
