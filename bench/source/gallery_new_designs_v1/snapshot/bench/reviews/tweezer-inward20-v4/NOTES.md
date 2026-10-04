# Inward20 v4 — taller catching fin checkpoint

Selected: **+1.8 mm crest in tool X, 55° two-sided roof, 6.75 mm initial vertical pickup**. The clean four-stack body, blind pockets, original wedge feet, four stored tool positions, 23 mm pitch, 20° inward slope, 15° lateral cant, A/4.0 and 23.05 mm plate-plane tip gap remain unchanged. This is the fin-only checkpoint; the later suggestion of a curved guide above/left is awaiting clarification and is not modeled here.

[Loaded](loaded.png), [empty](empty.png), [side](mounted-side.png), [fin comparison](fin-comparison.png), [actual CAD section](fin-section.png), [pickup](lift-out.png), [four paths](headroom-path.png), [print pose](print-pose.png), [plate](print-plate.png), [actual toolpaths](toolpaths.png). Orange identifies the separate fins; the prepared job is all yellow. Complete meshes are rendered, with no triangle removal or artificial repair. The fin section supplies the unambiguous height comparison; the loaded view naturally hides much of each fin behind the seated tool.

**What changed and what is proven.** The ridge rises from tool X=1.0 to 2.8 mm. In installed coordinates its displacement is approximately (0, -0.615636, +1.691447) mm, and its increase normal to the original receiving floor is 1.738666 mm. Ridge-to-floor normal heights at tool stations 31/41/51 mm are now 8.857771 / 8.645882 / 8.433994 mm, versus 7.119104 / 6.907216 / 6.695327 mm. The 55° roof applies to the added material; where it meets the old flat crest, original material is retained. No foot or old contact material is shaved away to create clearance.

[fin-comparison.json](fin-comparison.json) records zero exact CAD symmetric difference below the old crest and below the original floor, zero removed original material, zero fin/body intersection at all four seats, and zero reconstruction difference from the ordinary v3 fin. All four new fins are valid single solids. Volume per fin rises from 440.383429 to 484.878294 mm³; the body remains 88.044766 cm³. Thirteen body/print/tool/clearance files are copied byte-for-byte from v3, recorded in [candidate.json](candidate.json). Body installed STEP SHA256 is `2b33911d859bb48609843e7acf76e039776a84dcd2040c6a70853d7eb3505c2b` in both versions. The nominal anchor's old certificates are not a new physical fit qualification.

**Pickup and limits.** Lift the stored tool 6.75 mm along global +Z without rotation, then translate 135 mm along (0, cos20°, sin20°); reverse this path for insertion. [checks.json](checks.json) independently checks each complete reference tool against the complete body, board, all four fins and the other three seated tools. Lift sampling is 0.25 mm; outward sampling is 0.5 mm. All four outward paths have exactly zero computed intersection volume. Rest/lift traces are at most 8.87e-14 mm³, treated as numerical noise under a 1e-8 mm³ criterion. This is sampled full-mesh geometry, not a continuous certificate, rigid-body capture rate or demonstrated natural hand motion.

The minimum workable **sampled fin-release lift** is 6.75 mm among 6.5/6.75/7.0 mm. At 6.5 mm, the selected roof intersects the reference tool by 0.007583 mm³ during withdrawal. At 7.0 mm the fin releases, but the unchanged body intersects a middle tool during the outward stroke by 0.004802 mm³. Thus more lift is not automatically safer. A separate diagnostic at four previously troublesome roof positions gives 0.0654–0.1047 mm tool-to-own-fin gaps; see [roof-clearance.json](roof-clearance.json), which embeds the exact short reproduction script and input hashes. These are local diagnostic gaps, not a global minimum or an ASA manufacturing allowance.

| Tray, top to bottom | Last clear seated-position lift | First blocked sampled lift | Seated overhead reserve over 6.75 mm |
|---|---:|---:|---:|
| 1 | 9.25 mm | 9.50 mm | 2.50 mm |
| 2 | 7.50 mm | 7.75 mm | 0.75 mm |
| 3 | 7.50 mm | 7.75 mm | 0.75 mm |
| 4 | 7.50 mm | 7.75 mm | 0.75 mm |

Those overhead values apply at the stored fore-aft position only. They do **not** define an allowable full-path lift range. Lower/middle slots still require physical checks for natural pickup and fingertip access. The initial broad 40° roof with a +2.4 mm crest did not clear the old pickup; smaller 40° variants also produced shoulder contacts. Some final tiny trial traces could be below physical meshing accuracy; their volumes alone do not establish meaningful penetration. The selected narrower 55° added roof removes those traces and provides positive local measured gaps, without needing to classify them as acceptable collisions. No broad capture study or spring simulation was run.

**Inherited evidence.** Exact byte equality supports inheriting the v3 bare-body installation/front-plane screen, body overhang/island checks, stored tip/body distances and eight body-stiffness cases. The installation inheritance describes the bare body before loading tools/fins; shared rear peg/hoop interference assumptions remain unchanged. [fea-inheritance.json](fea-inheritance.json) links and hashes the actual v3 STEP, FEA spec/results/provenance, states `rerun: false`, and embeds the original results. All eight separate 5 N load-point targets passed. Largest side load-point displacement is 0.9429 mm; largest downward load-point displacement is 0.3111 mm. The maximum-anywhere side displacement is 1.0133 mm, a different quantity. The model uses solid isotropic ASA E=1800 MPa, nu=0.35 and fixed peg nodes. It does not qualify printed layers/infill, fin/glue strength, contact, fatigue or capture. No new solve is represented as having occurred.

**Why retain 20°.** For the fore-aft gravity decomposition, inward and normal weight components are W sin(theta) and W cos(theta):

| Angle | Inward / W | Normal / W | Ratio tan(theta) | 23 mm vertical pitch projected normal to fore-aft slope |
|---|---:|---:|---:|---:|
| 20° | 0.342 | 0.940 | 0.364 | 21.61 mm |
| 30° | 0.500 | 0.866 | 0.577 | 19.92 mm |
| 45° | 0.707 | 0.707 | 1.000 | 16.26 mm |

These are static projections, not exact clearances at unbuilt angles. The retained 15° lateral cant and multiple contacts complicate real seating. Steeper slope increases inward gravity but reduces four-stack separation; it does not ensure that a misdirected arm straddles the fin instead of overriding it. Actual friction, bends, arm spread and hand trajectory remain unmeasured. Test the taller fin at 20° first. No 30°/45° CAD or capture claim is included.

**Print preparation.** Body stays in the exact v3 right-cheek pose. The steeper roof fails the generic 45° overhang screen when lying on the original tapered side, so the four fins instead stand on their broad tool-station-51 ends: approximately 10.783 × 4.004 mm envelope, 20 mm tall. This pose passes the overhang and island screens without exceptions. Fins have a 5 mm outer brim / 0.8 mm gap; check adhesion and carefully remove brim without altering feet. Actual sliced supports are confined to body peg strips, none at fins or receiving surfaces.

The five bed objects retain one body and four separately identified fins. Calibrated ASA XY compensation 100/99.46 is baked once about bed (128,128), Z unchanged; slicer filament shrink is 100%. Minimum axis-separating object-box gap is 14.293955 mm, leaving 2.293955 mm after two conservative 6 mm brim envelopes. [toolpaths.json](toolpaths.json) audits actual extrusion centres, five objects, C12/P1S, one ASA filament, G-code MD5 and support locations. Custom startup/end is excluded from that geometry audit; arcs are subdivided 5° for plots. No printer command was sent.

Local-only archive: `print/slice-tweezer-inward20-v4/TW-INWARD20-v4-ASA-yellow-organic.gcode.3mf`.

- SHA256 `0a75359362a5d1d24449801690d3c261eb34ec67df1882dd82ac6b0558ea9636`; 2141342 bytes.
- G-code MD5 `F6FBFFF0F9367CA5DE01CEA675B805FB`.
- 10928 s = 3 h 02 m 08 s; 54.12 g; 244 layers; five objects. Approximately 1.142 g support/interface from actual extrusion.
- P1S 0.4, Textured PEI, calibrated PolyLite ASA yellow #FFF144, 260/100 °C, 0.2 mm layers, Arachne, two walls, 20% infill, organic build-plate-only supports, by-layer sequence. Original profile files are unchanged.
- Orca retained `bed_temperature_too_high_than_filament`, level 3 / 1000C001, for the calibrated 100 °C bed. Local log also contains `Not precalculated Placeable areas requested` with exit 0. The completed archive/toolpaths are independently checked; these messages are not suppressed. Time/mass are read from final archive metadata in toolpaths.json, not the null summary-comment fields.

**Assembly and physical acceptance.** Dry-fit the unchanged feet at all four pockets; narrow end points toward +Y/front and wide end toward the board. Use the established glue-in assembly, keeping glue away from catching faces and allowing full cure for the actual adhesive. The end-print orientation changes layers at the fin, so inspect the narrow ridge, adhesion and glue-foot integrity rather than inferring qualification from the unchanged body FEA. Follow root's [OWNER-TEST.md](OWNER-TEST.md): actual tools in every slot, all neighbors loaded, return misses versus false perches, independent pickup, tips/fingers, body/peg/glue motion. The intended benefit is a taller interception surface; no improved return success rate has been measured.

[BUILD.json](BUILD.json) selects the six new source scripts, exact generated/reused CAD, numerical evidence, views, root owner test, frozen references and local print inputs/archive. It includes the frozen v3 renderer and its ordinary rasterizer dependency. Private comparison drafts, slicer cache/logs and solver artifacts are not selected additions. All 269 preexisting staged baseline files are preserved; no index, commit, publication or printer action by this session.
