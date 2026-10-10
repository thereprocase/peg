# Final straight-socket racks v1

Owner request, 2026-10-10: render and publish the complete owner fan and three single-set Bondhus racks as `/final/` models. The owner physically selected v6 coupon letters **3C and 5C**. Preserve historical HX04/HX05 geometry/evidence; this is a new source namespace.

Socket authority: `study/socket_policy.py`. Six straight flats at +0.38 mm total AF clearance, engagement max(40 mm,8× shaft size); separate 3 mm axial lead widened 1.5 mm per flat. T handle axis is flat-to-flat. Square stop shoulders and 1 mm vents: 3.5 mm axial floor passage joins an outward passage below the socket. Torx L-key guides use straight circular nominal blade envelopes; 33034 T-handles retain the inherited hex proxy, not measured Torx blade CAD. Other-size fit and Torx clocking are provisional. Small hexes can rotate at this clearance; long guides do not guarantee clocking.

Models: HX04 owner 26-tool three-tier fan (9 hex L,9 Torx L,8 graduated metric T handles); HX05A 33034 Torx; HX05B 13189 metric; HX05C 13190 inch. Catalogue overall/bar lengths for the latter sets are in `study/tee_sets_note.json`; grip thickness remains assumed. Three Bondhus racks are separate bodies, each with two staggered rows. Saved `study/*_final.json` layouts are authoritative. The fan adjusts L-key row positions to clear the longer guides, retaining T-handle shaft/clocking angles from the tested fan orientation. Nominal sampled screens pass; worst clock-play and native continuous motion remain separate.

## Build

FreeCAD 1.1 Python with numpy/scipy is required. Pinned FreeCAD 1.1.3 Linux runs locally; no owner Windows build is needed for native exports. From the repository root:

```
FREECAD_PYTHON=/path/to/freecad-python python bench/source/final_racks_v1/build_final.py --out OUTPUT
```

`--rack HX04` / HX05A / HX05B / HX05C selects one. Set FREECAD_PYTHON in the environment on Windows. Every subprocess has a timeout; two native builds run concurrently. `prepare_layouts.py` is the bounded selection search, not required to reproduce the saved model. `check_model.py OUT` reloads exported STEP and checks guide walls/clearance, vent passages, floor shoulders, nominal stored tools, meshes and native document. Run it with the same build environment recorded in `run.json`. `preview.py OUT DISPLAY` creates compressed, reduced browser previews with trimesh 4.11.2 / fast-simplification 0.1.13. Display reduction does not change CAD/print downloads.

Print STL is bare, unscaled, left-end pose. The aligned brace STL is a slicer modifier, not a physical second part. Apply owner filament compensation once and review support/toolpath/bed/brim clearance before printing. No profiles or G-code are included. Previous v2 FEA and installation evidence does not qualify these changed models; the old mounting approach's whole-body installation collision still needs resolution. Full-rack printing, installation, snap recovery and loads remain unqualified.

The owner fan additionally runs `refine_owner.py`: restore the complete guide walls cut by neighboring opening/vent corridors, then add below-floor lateral vent routes toward positive installed X (the print-bed end). The source base STEP is retained as an intermediate; download the refined final STEP. All nominal withdrawals are re-screened at 1 mm against the added material. `check_owner_model.py` verifies the new vents and exported walls. The three single-set bodies do not need this correction.

Use a fresh output directory. The owner pipeline also extends wall protection all the way to the floor and lead boundary (`complete_guide_walls.py`) and normalizes the FreeCAD document through the delivered STEP (`normalize_document.py`). `check_full_model.py` checks the whole straight guide for all four models; no bottom section is excluded from the wall check. Native document round-trips are independently recorded.
