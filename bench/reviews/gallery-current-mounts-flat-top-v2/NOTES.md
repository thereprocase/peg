# Current station mounts — final modeling selection

SELECTED.json is authoritative: **38 active mounted gallery products**. It selects 19 genuinely planar-top v2 Pegstr/array bodies and 19 v1 remounts from the other families. No spool wall rack, unrelated root projects, archived screwdriver studies, loose magnetic trays/plugs/spacers or retired versions are added.

The included Pegstr products are P01–P11 and all eight seat arrays, including P01/P02 and P09-36. P06/P07 remain open bins but now have the requested inverted-flat-top pose; their broad internal floor spans require substantial support/bridge review. The four PB expansion bins retain their useful existing upright flat-base pose. Other selected bodies are seven main solder modules (main tweezer v8), the additionally promoted v10 tweezer, four MH shaft holders, both MS01-v3 mounted halves, and SWD01's cradle.

## Geometry and print choices

All use the exact frozen station recipe in source/station_snapshot: PF02 #9 (0.49 clamp / 0.50 upper ribs), corrected PF07 #5 (0.8 arms, 2.95 root clip), and intermediate conformal locators on tall receivers. Original mounting columns are preserved, including the four-column P09-72 and three-column wide bins. One integral receiver is fused to the body; no separate crown pads or cosmetic mounting spine. Every selected rear-interface symmetric difference is zero.

The 19 planar-top models cut no more than 0.12 mm from the original irregular top, raise the remaining body 0.60 mm, and share a genuinely planar Z=5.60 mm body/receiver top. Their full hook crowns sit about 0.155 mm below that plane. They print inverted by 180 degrees about X; horizontal hoop flex remains in the XY layers. Exact post-planing body preservation and independent opening-section comparisons preserve seat capacity. P09-36 is already captured separately by root; its files/source are frozen.

The six MH/MS magnetic bodies retain their original magnet cavities and sloped functional seats. A 3 mm forward / 2 mm upward rigid body shift preserves 2.4 mm of overlap with the receiver and lets the original broad flat top set the bed plane without shortening the hooks. Their X=175-degree compensated flat-top pose retains X hoop flex in-plane. Old magnet loading pauses and sliced jobs do not transfer.

Cheek prints use turned hoops with the 0.10 mm downward correction; upright/inverted prints use horizontal hoops without that correction. All hoop flex directions are checked in print coordinates. Every selected model has actual geometric bed contact and a bare-body placement within the recorded P1S 256 × 256 × 250 mm profile, avoiding its front-left 18 × 28 mm exclusion. Largest selected extent is P09-72, 241.75 mm. Supports/brims are not included in that envelope check.

## What the checks establish

CHECKS.json and each product's report/native/mesh evidence establish one valid CAD solid, zero rear-interface change from the shared recipe, watertight consistently wound meshes, expected material/cavity shells, STEP read-back, exact source hashes, and a chosen print pose. All front body/upper extension material passes a sampled board-plane installation/removal screen on the nominal reference route, with 0.05 mm maximum point movement and 0.005 mm tessellation. This is not the nominal anchor's continuous proof transferred to an interference-fit peg. Printed fit, deformation, retention, stiffness/load capacity, adhesion and support release remain pending.

The v10 upper hook rear region is unchanged from its existing station-like design (zero difference); the full rear region differs by 209.0017 mm³ for corrected lower hardware. It was not assumed identical just because its source mentioned PF02.

P01/P02's historical faceted STEP Booleans fail at the exact mounting plane. Their exact published meshes are clipped at Y=0.151 mm; the new receiver restores the one-micron rear-wall strip. No seat remeshing or smoothing. Their source bundle must keep both ancestry and the prepared STL input, with its .stl suffix. The four PB bins also take their exact published STL inputs. Do not rename these six inputs to original.step in portable specs.

P06 native CAD is unchanged by its export repair. A separate adapter uses a 0.00001 mm grid and removes two degenerate triangles. Measured pre-serialization displacement is below 0.000009 mm; mesh/CAD volume differences remain recorded. This adapter does not modify frozen flat_top.py or station sources.

## Reproduction and integration

FreeCAD runtime: Linux Flatpak Python, FreeCAD imported before Part/Mesh. Example:

    timeout 240s flatpak run --env=PYTHONPATH=/app/freecad/lib --command=python3 org.freecad.FreeCAD -B bench/source/gallery_current_mounts_v1/flat_top.py SPEC.json OUTPUT_DIRECTORY

For non-planed bodies use remount.py. P06 uses flat_top_p06_export.py. Each spec identifies the exact input and SHA-256; a portable bundle may rewrite the input path while retaining its extension and exact bytes. Snapshot layout must remain intact. Geometry gates use the existing physics Python with trimesh, NumPy, SciPy, manifold3d and Shapely; no package installation is required. Root owns unchanged-mesh GLB/PNG conversion, browser checks, public notes, release packaging and Git integration.

BUILD.json selects modeling source, exact inputs and final modeling evidence only; it excludes root media/publication, private failures/logs, caches, backup files and superseded Pegstr/array v1 CAD. All old originals and interim evidence remain on disk. No slice, printer command, stage, commit or push was performed by the modeling session. Bare CAD/mesh downloads must not link historical G-code/3MF as current jobs. Original Pegstr CC BY-NC attribution remains applicable.
