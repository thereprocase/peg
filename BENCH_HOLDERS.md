# Current bench holders and fit

The [curated gallery](https://thereprocase.github.io/peg/gallery/) now lives on GitHub Pages. It contains only Pegstr remixes, the array/bin expansion pack, solder WIP and screwdriver WIP. Earlier collections remain tombstoned. Work one model at a time through discussion, test print and feedback.

## Current fit versus the original anchor study

`bench/reference/peg-fit.scad` publishes the bench fit snapshot; `bench/source/peg_profile.py` rereads it on every generation. It uses a 3.80 mm grip assumption, -0.05 mm deliberate seated clearance and a 5.0 mm run / 3.30 mm rise. Negative clearance relies on printed plastic and board compliance; force is not measured. Full-height locator arrays are opt-in. Downloaded exports do not update when source changes: regenerate them, record their fit hash, then publish them.

This snapshot comes from the holder workspace's single editable `reference/peg-fit.scad`. Do not independently tune the published copy: change the holder authority, regenerate the selected model and synchronize these exact source bytes. The current hash is e586ab4ff6173c76e10c960ca707da94b01c615a629480d4bceeae71c80e2438.

The repository-root 3.94 mm conformal anchor and its motion certificates remain the **original nominal baseline**. They do not certify the bench interference variant. Earlier gallery fit hashes remain attached to their original exports; adding locator parameters changed the config hash without changing the basic hooked mount. This hosting migration changed no CAD or print-job bytes.

## The reference handle is not part of your holder

Remove the anchor's demonstration spine / handle at the board-reference face. Preserve the functional horizontal shaft and everything behind it. Continue the shafts into appropriately strengthened, continuous receiving material. Bury the roots with real overlap; do not bolt on a rectangular tab or add an external pad. The finished holder has a flush rear contact face and integral pegs. The demonstrated holder receiver uses Y=0.15 rear contact, 5.4 mm wall and 1.25 mm buried overlap. Those are construction values, not a load rating.

The baseline host envelope explains insertion space. A changed peg fit or complete holder needs its own motion check; a baseline certificate does not automatically transfer.

## Working rules

- Width = 25.4 mm times occupied cells minus 2 mm. Tool count is independent of cell count.
- Use two horizontal mounting columns whenever they fit; a lower locator is not a second column.
- Choose the bed face before massing: flat bottom, flat top inverted, or right cheek as appropriate. Local accessible supports are allowed. Inspect actual toolpaths before calling a print qualified.
- Keep bearing, grasp and one-motion return clear. Prefer stiffness and forgiving lead-ins to saving material. Protect delicate tips; keep exposed points above a floor.
- Filename contains part ID, design version, role and applicable fit hash. Do not confuse a Keep vote, CAD checks, slicing and a physical test.

The current MS01 v3 recoverable sampler has native P1S 0.4 / PLA print files, open channels for 20 x 10 x 3 mm magnets and loose 17 mm spacers. Load after printing and retain with removable tape; the installed mouths face down. No pause or permanent caps. Sealed v2 remains available. Physical fit and magnetic retention remain untested.
