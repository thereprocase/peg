# HX04 key fan — source

A three-tier pegboard rack: metric hex L-keys at the back, Husky Torx L-keys in the middle and Bondhus T-handles in front. The review, printing notes and evidence are in `bench/reviews/key-fan-v1/HX04/NOTES.md`.

## Layout study (`study/`)

- **`short.py`** places every tool: rows of sockets with stepped tilt, lean and turn, plus the T fan's angle schedule. It holds the socket physics:
  - seat depth at least 4× the key size;
  - each L-key's short arm pointing downhill;
  - the rest pose, where a tool's weight tips it about the mouth lip onto a floor sloped 30° low on that side;
  - hex-keyed T bores and the turn play of each handle.

  It also scores storage and withdrawal against the other tools, the rails (with their label lips) and a 3″ shelf 2″ above. Its `rail_points` and `floor_plane` are shared with the CAD.
- **`nudge_rows.py`** is the local polish. The final layout is `short_dt_c2.json`.

## CAD and checks

- **`build_short.py`** is the FreeCAD 1.1 model. It covers rails and webs swept 50° and rounded by the owner's edge rule (chamfer in Z, fillet in XY), bottle bores with sloped floors, Fillaprint labels, the mirrored PF02 #9 / PF07 #5 receiver, and the solid-infill zones. `--quick OUT` writes the meshes and STEP.
- **`check.py`** is the exact OCC check: storage, straighten-then-lift withdrawal, shelf and floors.
- **`fea_run.py`** runs the gmsh + CalculiX stiffness screen and needs `FREECAD_BIN`.
- **`coupon.py`** builds the fit coupon.
- **`tools/`** holds:
  - the overhang gate;
  - the review slices: plain STL, and the 3MF with the solid-zone modifier;
  - the GLB and render helpers;
  - `run_candidate.sh`, which runs the whole pass and needs `FREECAD_PYTHON`.

The build environment for the published layout is recorded in `report.json` (`build_env`). Tool data come from `bench/source/three_set_rack_v1/key_sets.json` (catalogue values). The label font is Fillaprint (SIL Open Font License, `fonts/OFL.txt`).

## HX05 single-set T-handle racks

The HX05 branch adds two staggered rows per set (33034 Torx, 13189 metric, 13190 inch) to resolve the deep-fan blocker. [Selected layout evidence and the one-command owner Windows build](../tee_racks_v1/README.md) describe the opt-in row mode and pending native/physical checks. HX04’s published layout and evidence remain separate.
