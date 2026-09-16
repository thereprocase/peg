# GitHub Pages cutover — September 16, 2026

- 1,398 previous public allowlist entries migrated; all unchanged CAD/media verified against the source manifest.
- 237 large-download routes consolidated into 171 byte-identical GitHub Release assets; GitHub SHA256 digests and sizes checked for every asset.
- 589 static local HTML links checked, no missing targets. GitHub Pages site is about 440 MB.
- 18 live browser viewport checks: nine pages at 390 and 1440 px; no visible image failures or horizontal overflow. Pegstr interaction and 3D loading checked; sampler 3D loaded after opening its details and scrolling into view.
- Actual public MS01 v2 print-kit ZIP downloaded and SHA256 matched the original 15,851,616-byte file.
- 242 legacy redirect cases checked locally, including every migrated binary route. Query strings preserved. Private reviews/API remain blocked.
- Public Warpbus root, Domhammer page and health remain HTTP 200. Legacy gallery links now return HTTP 308 to Pages or Release assets.
- New Warpbus releases omit the gallery asset tree. Previous immutable snapshots remain available for rollback.

No CAD geometry, slicer settings, qualification claims or print-job bytes changed in this migration. Pegstr credits and licenses remain visible. Public/private boundaries match the previous public allowlist.
