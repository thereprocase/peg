# Inward 20 v5 — open curved holder guides

This four-stack uses an open **6 mm radius holder roof**, with a free final settle above the retained taller fin. It retains 20° inward slope, 15° lateral seating, A/4.0 and the 23.05 mm plate-plane tip gap. The roof is a passive lead-in, not a latch or close-fitting tunnel. Natural guidance is a physical-test question, not established by a clear CAD route.

[Loaded](loaded.png), [empty](empty.png), [bare body](empty-body.png), [empty guide close-up](guide-empty-closeup.png), [arm approaching guide](guide-closeup.png), [CAD section](guide-section.png), [four guide sections](four-guide-paths.png), [independent pickup](pickup.png), [print pose](print-pose.png), [actual toolpaths](toolpaths.png). Views use the complete selected triangle meshes and ordinary depth-buffer rendering. Camera crops do not remove triangles. Orange denotes the separate fins; the prepared job is all yellow.

**Geometry and occupied space.** We increased the pitch modestly to make room for the guide and straightforward pickup. Vertical pitch is 28 mm, up from 23 mm: stations 1–4 move by global Z offsets 0/−5/−10/−15 mm from v4. Their angles, floor/pocket/fin shapes and tool seating relative to each floor remain the same. Two mounting columns, row 0 hooks / row 2 locators / row 4 hoops, bearing seams and peg roots remain unmodified. Exact CAD comparisons in [candidate.json](candidate.json) show zero rear-peg symmetric difference, zero floor/pocket inverse-translation difference, zero added guide material in blind pockets or floor contact skins, and zero inverse-translation difference for each fin. Tool export reorders triangle records, so [checks.json](checks.json) compares translated geometry bidirectionally and complete triangle incidence after vertex matching, independent of record order.

The upper rail rises nominally 6 mm and the lower seats extend 15 mm downward. The actual exterior bounds are reported below; these include filleted outlines and differ slightly from nominal rail changes. The rear window frame is 7 mm deep and tapers back before the receiving floors; its reinforcement does not consume the A4 seating gap. The perimeter flange is 20 mm deep across X, with a continuous rounded outline, and the inner bottom-web edge is lowered locally to retain the previously opened tip-clearance space. There is no separate sticking-out latch/tab. Width remains 48.8 mm and maximum front Y remains 135.579 mm. Hands and the pickup sweep require additional free space; the installed body outline is not the hand/removal envelope.

**Guide and motion.** Facing the board, operator-left is +X and right is −X. Global Y points away from the board and Z up. U=(0,cos 20°,sin 20°) follows the holder slope; V=(0,−sin 20°,cos 20°) is its normal. The roof occupies U 104–134.18745 mm at the top station and is translated with each lower station. Its underside radius is 6 mm, roof thickness 2.4 mm, exposed mouth fillet 0.7 mm. The underside ends at 80°, before it becomes a vertical hook. It blends into the right cheek/roof; it does not touch fragile tips or cross a fin during the selected motion.

The complete reference-tool route is reversible, without rotating the tool:

1. From stored, lift 6.75 mm freely along +Z until the arms clear the taller fin.
2. Sweep up-left: for θ decreasing 90°→0°, Xoffset=6(1−sinθ), Zoffset=6.75+6cosθ/cos 20°, Yoffset=0. This finishes 6 mm left and 13.1351 mm above the stored pose.
3. Continue 2 mm left to clear the open mouth, then withdraw 135 mm along (0,cos 20°,sin 20°). The final translation relative to stored is approximately (+8,+126.859,+59.308) mm. The reference tool is fully away from the board/holder at the end; fingertip clearance is additional.

Return reverses that route: approach above-left, sweep right/down beneath the curved roof, align above the fin, then settle the last 6.75 mm downward freely. The guide does **not** force a lateral arm movement through the fin. These waypoints describe the tested envelope; the user should not need a precision sequence or extra grip in ordinary use. If the actual tool requires that, the prototype fails the handling goal even if its nominal CAD route is clear.

[guide-contacts.json](guide-contacts.json) measures all four actual clipped guide meshes, rather than assuming that top and lower roofs are interchangeable. Its mesh-to-mesh minimum gap is separate from the nearest sampled robust-arm vertex and corresponding guide point. At 15°–75° on the curved segment the nominal gaps are approximately 0.195–0.294 mm, the open start about 0.606 mm and the relieved end about 1.152 mm. The selected route intentionally has clearance; an over-high presentation would meet the roof. These values are **nominal CAD diagnostics, not validated printed-fit allowances or a measured capture envelope**. Surface texture, ASA shrink, support removal, actual arm spread and friction may change contact substantially. The diagnostic records the distance of each sampled contact region from the fragile tip; the contact is on the robust upper arm.

**Independent paths and installation.** Each of the four complete reference meshes is checked against the complete body, board, all four fins and three stored neighbors. Free lift/left steps are at most 0.25 mm, arc steps 1° (at most about 0.112 mm), and outward steps 0.5 mm. The same configurations in reverse cover return. Full mesh Boolean intersections are used, not sparse sampled tool vertices. The bottom tray's complete 15 mm tip region is also swept through the extra 19.05 mm clearance volume; no obstructing web is moved into that space. Reported results below are sampled geometric screens, not continuous certificates or dynamic capture rates.

The changed bare front body has a fresh installation screen against the board front plane along the existing reference trajectory; it does not reuse a v4 body certificate. The exact unchanged rear peg/hoop geometry retains intentional fit/interference assumptions. Nominal-anchor evidence is not a physical fit qualification of the fitted pegs or hoops. Install the bare body before loading fins/tools.

**Stiffness.** The selected changed body has a fresh eight-case solve: independent 5 N side/down handling loads at all four seats, targets 1.0/0.5 mm at each load point. Max-anywhere deflection is reported separately. The model is solid isotropic ASA, E 1800 MPa, ν0.35, with fixed peg nodes and a nominal 2 mm second-order tetrahedral mesh. It does not represent the sliced two-wall/20% structure, layer anisotropy, actual board motion, guide contact force, fin glue, strength/fatigue, bumps or capture. No spring simulation or broad capture study was run. Failed preliminary attempts are preserved privately. Their side-deflection results, bottom-tip clash and guide-end ledge are not selected evidence.

**Print and physical acceptance.** The body prints on its right cheek; four exact v4 fins stand on their broad station 51 ends, 20 mm tall. Fin overhang/island checks pass without exceptions. The generic body overhang screen honestly fails at one accessible top-guide patch; organic support is explicitly required there and at the pegs. The final local job permits support to start on the printed cheek beneath the guide; bed-only trials did not generate the required interface. Actual toolpath support locations, bed bounds and five objects are checked separately. Remove the top-guide support cleanly without flattening the curved contact surface. Reachability is visible in the empty close-up; support release and surface finish remain physical tests.

Dry-fit the original fin feet, bond with the established assembly method, keep glue off catching surfaces and allow full cure. Follow [OWNER-TEST.md](OWNER-TEST.md): actual tools in every position, all neighbors loaded, natural return/pickup, false perches, fragile tips, finger clearance and guide surface quality. Retain 20° until those tests: stronger inward gravity at 30°/45° would also reduce normal spacing in the four-stack and does not ensure that an arm lands around the fin. No unbuilt-angle qualification is claimed.

**Selected numerical results.**

Body solid volume: 108.645316 cm³ (v4: 88.044766 cm³). Installed XYZ bounds: (-24.400000, -10.790000, -126.558115) to (24.400000, 135.578669, 30.731490) mm. Actual bottom growth is 14.8944 mm and top growth 5.7883 mm versus the filleted v4 outline. Four fins retain 484.878294 mm³ each. No material/print-weight reduction is claimed.

| Station | Side load-point / max anywhere (mm) | Down load-point / max anywhere (mm) | Tip-region nearest body gap (mm) |
|---|---:|---:|---:|
| 1 | 0.7212 / 0.7774 | 0.2165 / 0.2810 | 11.2707 |
| 2 | 0.8978 / 0.9573 | 0.2076 / 0.2805 | 1.9108 |
| 3 | 0.8641 / 0.9287 | 0.2077 / 0.2998 | 11.2707 |
| 4 | 0.6744 / 0.7242 | 0.2021 / 0.2882 | 1.9108 |

All eight load-point targets pass. Mesh: 162705 nodes, 89225 elements, 5350 fixed peg nodes. See [part-tweezers__inward20-v5-A4p0-guideR6-p28__right-cheek__fit-pf02c9-hoop5__fea.json](part-tweezers__inward20-v5-A4p0-guideR6-p28__right-cheek__fit-pf02c9-hoop5__fea.json) and [fea-provenance.json](fea-provenance.json). The nearest material gap is **not** the 23.05 mm distance to the plate plane: trays 2/4 are closer to the reinforced rear frame. Actual bent-tip variation still needs inspection.

All four tip-extension screens have zero intersection. Tool translation error is at most 3.82e-6 mm, with identical mapped triangle connectivity. All up-left, mouth-clearance and outward samples have zero intersection; the largest rest/lift trace is 8.87e-14 mm³, below the unchanged 1e-8 mm³ numerical criterion. The new front-body installation screen covers 2,973 poses with at most 0.05 mm vertex motion per subdivision and 0.005 mm surface tessellation deflection. Minimum front-plane clearance is approximately zero (5.96e-9 mm); this is nominal contact, not a positive manufacturing reserve.

The guide-end ledge was a real 0.187446 mm termination offset. [guide-junctions.json](guide-junctions.json) now verifies coincident STEP front planes at all four guide ends; the lower guides join the preceding floor on that plane. The selected full-body close-up shows the removed triangular ledge. [guide-contacts.json](guide-contacts.json) locates the sampled robust-arm contact regions about 104.6–106.8 mm in Y from the reference tip, separately for every station.

**Local print preparation.** The selected archive is `print/slice-tweezer-inward20-v5/TW-INWARD20-v5-ASA-yellow-organic.gcode.3mf`.

- SHA256 `aec8afb2e2a4f5f62aa83c73797a3f665b3b4f4e2049d8f2140c95dccc2d0b85`; 2513056 bytes.
- G-code MD5 `517ED99E53A2461F3F17DD90ACAABFE2`; C12/P1S, one ASA filament, five objects.
- 12517 s = 3 h 28 m 37 s; 63.96 g; 244 layers. Actual support/interface extrusion is approximately 1.389 g.
- P1S 0.4 / Textured PEI, calibrated PolyLite ASA yellow #FFF144, 260/100 °C, 0.2 mm layers, Arachne, two walls, 20% infill, by-layer sequence, 5 mm outer brim / 0.8 mm gap.
- This local process explicitly sets **45° support threshold, small-overhang removal off, organic supports allowed on the model (`support_on_build_plate_only=0`)**. The earlier bed-only trials omitted the guide interface. The original machine/process/filament profile files are unchanged.
- XY compensation 100/99.46 is baked exactly once about (128,128), Z unchanged; slicer filament shrink is 100%. Minimum object-box separation is 14.293955 mm, leaving 2.293955 mm beyond two conservative 6 mm brim envelopes.

[toolpaths.json](toolpaths.json) audits the exact archive, support zones, five objects, bed/exclusion bounds and MD5. [Guide support close-up](guide-toolpaths.png) shows actual extrusions at the top roof; support starts on the printed cheek. The reported interface paths are at print Z=3.4–3.6 mm; organic branches continue up to 6.2 mm under the roof. These are actual sliced paths, not a claim of a continuous conformal top-interface sheet. The purple overlay is the flagged nominal CAD overhang transformed into the exact compensated bed pose. The gray model paths and dashed print-Z=3 mm cheek surface show where the short support stack starts. Remove the branch/interface from the cheek and outer roof through the guide's open fore/aft ends; avoid gouging either printed surface. Actual release force and surface finish are unqualified. This support is accessible from the open guide mouth but needs physical release/finish inspection. Other support stays in the peg strips, and no fin support is generated. Actual extrusion-centre bounds, including brims/supports but excluding Custom startup/end, are [[44.435, 41.13049565829557, 0.2], [212.861, 222.634, 48.8]]. Arc plots use 5° subdivisions.

Orca retains `bed_temperature_too_high_than_filament` (level 3 / 1000C001) for the calibrated 100 °C bed. The local log also contains `Not precalculated Placeable areas requested` with exit 0; successful archive generation and actual extrusion checks are separate evidence. Time/mass come from archive metadata, not absent G-code summary comments. No printer command was sent.

**Reproduction and provenance.** Run from `/home/repro/code/peg-bt2` using fresh output directories; the generator refuses to overwrite evidence. Existing FreeCAD/physics/Orca runtimes are used; no package installation is needed.

```bash
V5_REVIEW=/home/repro/.local/state/peg-astra-3d/v5-rebuild
V5_SLICE=/home/repro/.local/state/peg-astra-3d/v5-slice-rebuild
timeout 240s flatpak run --env=PYTHONPATH=/app/freecad/lib --command=python3 org.freecad.FreeCAD -B bench/source/tweezers_v11/inward20_v5.py "$V5_REVIEW" --guide-count 4
timeout 900s /home/repro/venvs/physics/bin/python bench/source/tweezers_v11/inward20_v5_check.py "$V5_REVIEW"
timeout 240s /home/repro/venvs/physics/bin/python bench/source/tweezers_v11/inward20_v5_guide_check.py "$V5_REVIEW"
timeout 60s flatpak run --env=PYTHONPATH=/app/freecad/lib --command=python3 org.freecad.FreeCAD -B bench/source/tweezers_v11/inward20_v5_junction_check.py "$V5_REVIEW"
timeout 1800s flatpak run --env=PYTHONPATH=/app/freecad/lib --command=python3 org.freecad.FreeCAD -B bench/source/tweezers_v11/inward20_v5_fea.py "$V5_REVIEW"
timeout 360s env MPLCONFIGDIR=/tmp/peg-spool-mpl python3 bench/source/tweezers_v11/inward20_v5_render.py "$V5_REVIEW"
timeout 60s /home/repro/venvs/physics/bin/python bench/source/tweezers_v11/inward20_v5_plate.py "$V5_REVIEW" "$V5_SLICE"
timeout 720s python3 bench/source/tweezers_v11/inward20_v5_slice.py "$V5_SLICE"
timeout 120s env MPLCONFIGDIR=/tmp/peg-spool-mpl python3 bench/source/tweezers_v11/inward20_v5_toolpaths.py "$V5_SLICE" "$V5_REVIEW"
timeout 90s env MPLCONFIGDIR=/tmp/peg-spool-mpl python3 bench/source/tweezers_v11/inward20_v5_render.py "$V5_REVIEW" --slice "$V5_SLICE" --plate-only
```

[BUILD.json](BUILD.json) records the selected sources, CAD, exact numerical inputs, views, [OWNER-TEST.md](OWNER-TEST.md), frozen dependencies, existing profiles and local archive. The v3 renderer and its ordinary rasterizer dependency are included. Private failed drafts, unsupported trial slices, transient solver files, logs and slicer caches are not selected additions. All 320 preexisting staged baseline files are preserved; root owns index, README, manifest and integration. This session performed no index, commit, push, publication or printer action.
