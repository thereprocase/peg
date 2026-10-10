# Current bench holders and fit

The [October 4 current-mount collection](https://thereprocase.github.io/peg/gallery/current-pegs/) contains all 38 active gallery bodies with PF02 #9 upper hooks (.49 mm clamp, .50 mm crush ribs) and PF07 #5 lower hoops with clipped rigid roots. All 19 Pegstr remixes and arrays have truly planar tops for 180° upside-down printing, broad body bed contact, and full hook crowns below the bed face. Other bodies retain their reviewed upright, cheek or compensated top print poses. Horizontal hoop flex stays within the layers. The shared recipe is preserved under `bench/source/gallery_current_mounts_v1/station_snapshot/`; `bench/reviews/gallery-current-mounts-flat-top-v2/SELECTED.json` records the exact 38-part selection. Per-part support notes and geometry evidence accompany each export. P06/P07 inverted bins require interior support review. Changed-fit physical installation and slicing remain pending. The fit snapshot and older exports described below retain their original versions.

[Six new session designs](https://thereprocase.github.io/peg/gallery/current-pegs/?family=new) are also published: open spool cradle v14, guided four-stack tweezers inward20-v5, rounded rectangular tool funnel v3, braid holder v12, drip tray v12 and its removable vase-mode liner. Each entry states its prototype/physical status. The tweezers require four separate fins; the liner has no pegs and requires spiral-vase settings.

[HX04 three-tier key fan](https://thereprocase.github.io/peg/gallery/key-fan/) holds hex L-keys, Torx L-keys and Bondhus T-handles on a 236 mm plate (ten cells shaved 8 mm a side). v2 puts a peg in every covered hole: hooks across the top row, locking hoops across the bottom row and gravity-load bearing pegs between, 9 × 10 on the 1-inch grid. It prints on its left end with the reviewed peg profiles mirrored; fit is assumed equal, so print the fit coupon first. The historical rear-peg swing screen omitted the front host: the [extended engineering audit](https://thereprocase.github.io/peg/gallery/key-fan/studies/) finds body/board collision on that assumed pivot. The original socket fit failed the owner’s print trial; revised 3/5 mm guide spectra await physical selection. The audit includes 60 computed films and explicit numerical limitations; installation, snap recovery and printed loads remain unqualified.

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
