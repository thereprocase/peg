# Working on peg

This repository is the durable source of truth for the parametric pegboard anchor. Read README.md, HANDOFF.md, DESIGN_HISTORY.md, MOTION_STUDY.md, PRINTING_OPTIONS.md, and SLICER_CHECK.md before changing geometry.

- Keep the newest printable models and their direct download links prominent in README.md. Preserve old states in git history; do not bury the current prototype in parallel revision folders.
- All dimensions are mm. Default board thickness is 3.94 mm, holes 6.35 mm, pitch 25.4 mm; hole diameter and thickness are independent.
- The original interface has continuous rigid-body clearance evidence. Rerun motion after changing functional geometry. Include the actual host envelope when assessing integrated holders.
- Four 0.5 mm cut-away webs support upright printing. They must be removed flush. Upright and flat prints do not have equal layer load paths or established load ratings.
- Toolpath evidence is generic CuraEngine 5.0.0; it is not a P1S profile or physical test. Read the local 2-wall/solid-fill roof strategy before re-slicing upright.
- Preserve source, STEP/STL/3MF exports, numerical evidence, input hashes, visuals, and user-facing explanations together. Clearly distinguish computational checks from physical tests.
- Never send review G-code to a printer or publish it as ready-to-run G-code. Use the user's own machine/filament profile for physical printing.
- README.md is authored documentation. write_reference_readme.py regenerates MODEL_REFERENCE.md only.
- Do not publish unrelated user information, credentials, environment dumps, cache files, or machine-specific review G-code.
- Write clear, precise, concise engineering prose in active voice. Explain decisions and limits without sales claims.
