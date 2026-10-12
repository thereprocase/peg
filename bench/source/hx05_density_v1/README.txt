HX05 density helpers — approved 30-degree outside holders

Current physical part: 86 DraftedHolder. Keep the chosen tip-end bed face and
print rotation. Fits, funnels, vents and outside massing remain unchanged.

DensityHelpers contains four independent NONPHYSICAL 100% infill masks:
Foundation: bed-face foundation.
Mounts: peg envelopes, local roots and collector belts.
Sockets: sleeve walls and floors.
Ribs: sleeve-to-back-body load paths.
Raw masks may extend through air as selection handles. Orca intersects modifiers
with the physical part. Never fuse masks into the body or print them as parts.
The former clipped cores and StructuralHolder are construction history.

FREECAD
Extract the full bundle, then run SETUP_DENSITY_FANS.FCMacro once to install the
three portable modules. Open the matching FCStd. Toggle DensityHelpers to inspect
individual zones. DensityParameters controls helper dimensions. RibWidth and
RootWidth also control outside construction: changing them invalidates the
approved outside geometry. Keep the tested socket parameters unchanged.

ORCA
The intended project has one normal part and four modifier_part volumes, each
with sparse_infill_density=100%. Remaining bulk starts at 12% gyroid / four walls.
The inch project requests normal/grid supports. Metric and Torx review slices
used organic tree supports. Use the actual owner printer and calibrated filament
profiles. Check modifiers,
supports, bed clearance and toolpaths before printing. Nominal exports have no
filament compensation. Do not compensate twice. No print job is submitted.

STATUS
Native modifier exports and fixed-shape/print-rotation checks have passed.
Release checks record Orca modifier retention, bed and socket-core toolpath screens.
Rear peg mesh seams use a bounded export adapter; watertight topology alone
does not establish a global surface-intersection certificate. Native CAD remains the manufacturing reference.
Continuum results use assumed anisotropy and idealized boundaries; they are
comparative studies, not physical load ratings. Windows GUI first-open is separate
from successful local headless FreeCAD builds.
