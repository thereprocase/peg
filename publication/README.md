# Publishing the curated gallery

Canonical public site: https://thereprocase.github.io/peg/gallery/
GitHub Pages builds `main:/docs`. `docs/gallery` contains the static gallery, local scripts and 3D media. CAD STEP/FCStd, ZIP bundles and 3MF print jobs are GitHub Release assets. `release-downloads.json` maps original relative paths to immutable release URLs, including compatibility aliases; `release-assets.json` records exact SHA256 and size.

Preserve four groups, tombstones, Pegstr credit, model-specific limitations, explicit part/version filenames and private-data exclusions. This migration imported ONLY the previous public allowlist, recorded in gallery-source-manifest.json. No votes, photos, databases, credentials, workspace history or machine caches were imported.

For the next model: generate/review locally, stage only its approved public additions, upload versioned binary downloads to a new release, update the scoped gallery page and map, run `python tools/check_gallery.py`, review the diff and push. Verify Pages and real downloads before changing links on another host. Never rerun the retired PVE publication scripts.

Offline: clone/download this repository and serve `docs` with a local static server for 3D. Pages and renders are local; release downloads require internet. Model/source ZIPs remain self-contained and unchanged.

Warpbus keeps legacy redirects only after GitHub verification. Historical immutable Warpbus snapshots are rollback evidence, not the publishing target.
