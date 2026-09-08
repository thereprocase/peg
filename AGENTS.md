# Working on peg

The current model has true round bearing pegs. Read README.md, HANDOFF.md, ROUND_MOTION_STUDY.md, and ROUND_SLICER_CHECK.md before editing it. BASELINE_README.md preserves the earlier rectangular design.

- Keep current print downloads prominent in README.md. Current sources, CAD, evidence, and visuals live at the root and in cad/, visuals/, tools/, and review_settings/. Preserve old decisions in documentation and git history.
- Current canonical sources are round_anchor.py, round_motion.py, and round_print_supports.py. The unprefixed older anchor.py/motion_design.py/OpenSCAD module belong to the rectangular baseline.
- Default dimensions are 3.94 mm board, 6.35 mm holes, 25.4 mm pitch, 5.6 mm neck/locator, 4.8 mm tongue. Use tested thickness/diameter combinations; arbitrary parameter changes require a motion check.
- Preserve actual circular bearing geometry. Do not substitute small corner fillets or bearing flats. Include the complete host envelope when assessing an integrated holder.
- The side print uses a 0.40 mm lift, sacrificial pad, and cradles with a 0.20 mm interface. Keep all shells in their relative positions. Upright uses cradles on removable ramp webs; remove every printing aid before installation.
- Keep continuous motion certificates, sampled STEP checks, toolpath screens, and physical tests distinct. No physical load or support-release rating has been established.
- Generic Cura review uses five side walls, two upright walls, solid fill and modeled supports. Use the user's machine and filament profile for actual printing. Do not publish review G-code as printable output or send it to a printer.
- Keep CAD, exact input hashes, source, numerical evidence, and visuals together. Regenerate the release manifest after intended file changes.
- Tool calls must have timeouts. Prefer small visible GitHub checkpoints during long work; do not wait on one unbounded bulk upload.
- Do not publish credentials, unrelated user information, caches, downloaded slicer binaries, or machine-specific review G-code.
- README.md is authored. write_reference_readme.py regenerates the historical MODEL_REFERENCE.md only.
