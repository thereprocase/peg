## MS01 v3 — recoverable-magnet test print

User asked to salvage magnets between shaft-fit trials. `shaft_fit_sampler.py`
now has an explicit `recoverable=True` branch; the existing sealed v2 default
is unchanged. `shaft_fit_sampler_recoverable.py` exports v3 in
`independent-workups/shaft-fit-sampler-20x10x3-v3-recoverable`.

Both A-P strips retain v2 seats, bearing top, width and canonical fit e586ab4ff6.
Only magnet channel material is removed: 10.8 x 3.8 mm section, open through
print Z=40 instead of capped at 38. Magnets remain 20 x 10 x 3 nominal.
Loose spacers are 10 x 2.95 x 17 mm, flush with the mouth over a seated magnet.
Load AFTER printing/cooling. Mouths face downward installed; removable tape
holds the loose spacers/magnets. Remove from board and peel tape to recover.
Do not call the clearance fit a friction retainer. The nominal magnet-to-shaft
range is 0.82-1.62 mm; keep magnets shaft-side for repeatable comparisons.

CAD single solids, STEP round trips, changes confined to channels, full straight
extraction envelopes and tool withdrawal pass. Native P1S / 0.4 / PLA three-plate
job: spacers 9.25 g / 31m16s; A-H 103.32 g / 4h8m8s; I-P 101.21 g / 4h5m8s.
Zero pauses; all sixteen channel cores open through final layer; native settings,
bed/startup paths and ZIP contents checked. Physical fit, tape retention, magnetic
feel and desktop GUI opening remain untested. No job sent to printer.

Build/render/slice/check/package/publish scripts have `_recoverable` suffixes.
Gallery: https://thereprocase.github.io/peg/gallery/shaft-sampler/recoverable/
Publication remains GitHub-only; preserve sealed v2.

