# Publishing the curated gallery

Canonical public site: https://thereprocase.github.io/peg/gallery/
GitHub Pages builds `main:/docs`. `docs/gallery` contains the static gallery, local scripts and 3D media. CAD STEP/FCStd, ZIP bundles and 3MF print jobs are GitHub Release assets. `release-downloads.json` maps original relative paths to immutable release URLs, including compatibility aliases; `release-assets.json` records exact SHA256 and size.

Preserve four groups, tombstones, Pegstr credit, model-specific limitations, explicit part/version filenames and private-data exclusions. This migration imported ONLY the previous public allowlist, recorded in gallery-source-manifest.json. No votes, photos, databases, credentials, workspace history or machine caches were imported.

For the next model: generate/review locally, stage only its approved public additions, upload versioned binary downloads to a new release, update the scoped gallery page, `release-downloads.json` and the matching `docs/gallery/release-downloads.js` map, run `python tools/check_gallery.py`, review the diff and push. Verify Pages and real downloads before changing links on another host. Never rerun the retired PVE publication scripts.

Offline: clone/download this repository and serve `docs` with a local static server for 3D. Pages and renders are local; release downloads require internet. Model/source ZIPs remain self-contained and unchanged.

Warpbus now keeps legacy redirects only, following GitHub verification. Historical immutable Warpbus snapshots are rollback evidence, not the publishing target.

## October 4 current-mount collection

`bench/reviews/gallery-current-mounts-flat-top-v2/SELECTED.json` selects 38 mounted gallery bodies: 19 planar-top Pegstr/arrays and 19 other holders with per-part poses. `verify_selection.py` validates the frozen source, native exports and checks. Do not regenerate frozen exports just to package them; native serialization hashes may change. P06 uses its bounded mesh-export adapter.

`prepare_current_pegs_media.py --selection SELECTED.json` converts the selected installed/print meshes to GLB. `build_current_pegs.py BUILD_DIR RELEASE_DIR --selection SELECTED.json --tag RELEASE_TAG --generation-source-map SOURCE_MAP.json` packages 114 native/source release assets and writes the catalog, receipts and redirect map. The generation-source map is local build state; the ZIPs preserve exact execution code and public provenance. Each bundle retains its true original input suffix, any original STEP/STL ancestry, the shared fit snapshot, native CAD, meshes and review evidence.

Run `python3 tools/check_gallery.py`, check the actual mobile/desktop viewer and both poses, review scoped staged paths, refresh `release_manifest.json`, upload immutable release assets, then publish the matching Pages commit. No current G-code or sliced job is included. Historical loose parts and print jobs remain in their original galleries. Print support/toolpath and changed-fit physical qualification are separate from the recorded CAD checks.
