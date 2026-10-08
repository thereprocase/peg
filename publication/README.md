# Publishing the curated gallery

Canonical public front page: https://thereprocase.github.io/peg/
Current holder collection: https://thereprocase.github.io/peg/gallery/current-pegs/
GitHub Pages builds `main:/docs`. `docs/gallery` contains the static gallery, local scripts and 3D media. CAD STEP/FCStd, ZIP bundles and 3MF print jobs are GitHub Release assets. `release-downloads.json` maps original relative paths to immutable release URLs, including compatibility aliases; `release-assets.json` records exact SHA256 and size.

Preserve four groups, tombstones, Pegstr credit, model-specific limitations, explicit part/version filenames and private-data exclusions. This migration imported ONLY the previous public allowlist, recorded in gallery-source-manifest.json. No votes, photos, databases, credentials, workspace history or machine caches were imported.

For the next model: generate/review locally, stage only its approved public additions, upload versioned binary downloads to a new release, update the scoped gallery page, `release-downloads.json` and the matching `docs/gallery/release-downloads.js` map, run `python tools/check_gallery.py`, review the diff and push. Verify Pages and real downloads before changing links on another host. Never rerun the retired PVE publication scripts.

Offline: clone/download this repository and serve `docs` with a local static server for 3D. Pages and renders are local; release downloads require internet. Model/source ZIPs remain self-contained and unchanged.

Warpbus now keeps legacy redirects only, following GitHub verification. Historical immutable Warpbus snapshots are rollback evidence, not the publishing target.

## October 4 current-mount collection

`bench/reviews/gallery-current-mounts-flat-top-v2/SELECTED.json` selects 38 mounted gallery bodies: 19 planar-top Pegstr/arrays and 19 other holders with per-part poses. `verify_selection.py` validates the frozen source, native exports and checks. Do not regenerate frozen exports just to package them; native serialization hashes may change. P06 uses its bounded mesh-export adapter.

`prepare_current_pegs_media.py --selection SELECTED.json` converts the selected installed/print meshes to GLB. `build_current_pegs.py BUILD_DIR RELEASE_DIR --selection SELECTED.json --tag RELEASE_TAG --generation-source-map SOURCE_MAP.json` packages 114 native/source release assets and writes the catalog, receipts and redirect map. The generation-source map is local build state; the ZIPs preserve exact execution code and public provenance. Each bundle retains its true original input suffix, any original STEP/STL ancestry, the shared fit snapshot, native CAD, meshes and review evidence.

Run `python3 tools/check_gallery.py`, check the actual mobile/desktop viewer and both poses, review scoped staged paths, refresh `release_manifest.json`, upload immutable release assets, then publish the matching Pages commit. No current G-code or sliced job is included. Historical loose parts and print jobs remain in their original galleries. Print support/toolpath and changed-fit physical qualification are separate from the recorded CAD checks.

## Featured connector downloads

The front page features six current-fit connector/pair variants with +20% diameter, 2 mm holder-side joining nubs. `bench/source/peg_connectors_v1/build.py` constructs native solids and datum planes from the unchanged fit snapshot. Native STEP/BREP/IGES round-trips, unchanged board-side geometry and a sample host union are checked during generation. IGES topology is sewn for its solid comparison. Meshes are tessellated directly from the native solids without mesh repair.

`build_peg_downloads.py RELEASE_DIR` packages STEP, FCStd, BREP, IGES, STL, OBJ and geometry-only 3MF, plus all-format/source bundles. Native exports remain GitHub Release assets; `docs/pegs` holds the catalog, display GLBs and integration notes. `peg-connectors-v1-additions.json` records release/local receipts. Run `tools/check_peg_downloads.py` (also included in the gallery check) and review the actual front-page viewer before publishing. The original nominal study stays at `/peg/anchor-study/`; its CAD and certificates are unchanged.

## Workbench previews

`docs/viewer/workbench.js` applies four-band cel shading, a bright workbench background and soft ground shadows to the interactive viewers. The adapter uses the pinned model-viewer build's `correlatedObjects` material set and scene render request; verify these hooks when upgrading that vendor bundle. CAD, GLB geometry and downloadable materials retain their original bytes.

`render_workbench_previews.cjs` regenerates the current collection's installed, print and thumbnail PNGs from the same shader. Serve `docs`, set `PEG_PREVIEW_URL` to that server, and run with Playwright available via `PLAYWRIGHT_MODULE` and Chromium via `CHROMIUM_PATH`. Refresh the current-pegs receipts after rendering. Check viewer material application and browser/WebGL errors across model swaps before publishing.

CF01 v3 is a Repro bespoke catalog entry in `current-pegs` (solder-modules family). `add_cascade_to_collection.py` registers its slim-web revision, reviewed media, downloads, notes and front-facing camera. Apply it after rebuilding the base collection, then render only this entry with `PEG_PREVIEW_IDS=CF01` using `render_workbench_previews.cjs` and refresh the collection receipts. The standalone cascade page remains the detailed review linked from the catalog entry.

HX02 v1 is the full-depth 30-degree metric hex-key rack in Repro bespoke. `build_canted_hex_keys.py` publishes its matching model, evidence and catalog entry; `package_canted_hex_keys.py` packages native CAD and exact sources. Render its catalog previews with `PEG_PREVIEW_IDS=HX02`, refresh the collection receipts, and run the gallery checks before publishing.

HX02 v2 (graduated organ-pipe hex-key rack) replaces v1 on the canted-hex-keys page and in the Repro catalog; v1's print STL and CAD release stay linked as history. `bench/source/canted_hex_keys_v2/build.py` builds it (FreeCAD 1.1 with scipy; `--quick DIR` writes review meshes only), then `review.py`, `install_screen.py`, `stiffness.py`, `slice_local.py` (Windows OrcaSlicer, flattened system P1S/0.20 mm presets plus the owner's PolyLite ASA ReproCal filament) and `toolpaths.py` write the evidence. `build_canted_hex_keys_v2.py` publishes page, catalog and receipts; `package_canted_hex_keys_v2.py` makes the release bundle (`canted-hex-keys-v2-2026-10-07`). Render catalog previews with `PEG_PREVIEW_IDS=HX02` and refresh the receipts; `tools/check_canted_hex_keys_v2.py` runs from the gallery check.

HX04 v1 (three-tier key fan: hex L-keys back, Torx middle, Bondhus T-handles front) is a new Repro bespoke entry with its own page, `docs/gallery/key-fan/`. `bench/source/key_fan_v1` holds the layout study (`study/short.py`, final layout `short_dt_c2.json`) and the FreeCAD 1.1 model (`build_short.py`). Run it with the build env recorded in `report.json`. `check.py` (exact storage and withdrawal), `fea_run.py`, `coupon.py` and `tools/run_candidate.sh` write the evidence; `tools/evidence.py` collects it into `bench/reviews/key-fan-v1/HX04`. `build_key_fan.py` publishes the page, catalog entry and receipts. `package_key_fan.py` makes the release bundle and the solid-zone 3MF project (`key-fan-v1-2026-10-08`). Render catalog previews with `PEG_PREVIEW_IDS=HX04` and refresh the receipts; `tools/check_key_fan.py` runs from the gallery check. The fit coupon STL ships on the page; no G-code is published.
