# HX05 fixed-pose density modifiers

Current approved physical geometry: `DraftedHolder`, with 30-degree outside
housing tapers and unchanged tested socket cutters. The selected tip-end bed
face and print rotation are fixed. Only internal modifier directions may vary.

`prepare_modifiers.py ID` exports four independent raw masks (Foundation,
Mounts, Sockets, Ribs) and the socket support blocker in exactly that pose.
It checks the physical body BREP hash within the process before and after,
exports native shapes and meshes, and updates the portable FCStd instructions.
The masks may extend into air as selection handles; they are never physical parts.
Raw exports are clipped to the build volume so they cannot lift the body off its
chosen bed face. Simple rear-peg envelopes avoid inheriting bearing mesh seams.

`package_drafted.py` creates REVIEW 3MF projects: one `normal_part`, four
`modifier_part` volumes at `100%`, one `support_blocker`; bulk 12% gyroid,
four walls. Projects are nominal/unscaled, with no private profile or G-code.
The body tessellation has bounded rear-peg seam caps. Watertightness alone does
not establish freedom from surface intersections; manufacturing mesh and current
actual-profile support/toolpath checks are still outstanding. These projects are
not print-qualified. Native CAD is the manufacturing reference.

`render_modifier_sections.py` shows actual print XY sections of the body and
masks; bed yaw is undone only for readability. The modifier contours are geometry,
not actual wall paths or infill. `README.txt` and the setup macro accompany the
native review bundle. Windows GUI first-open remains a separate owner check;
local headless FreeCAD is available and was used for these exports.

The former `build.py`, `package.py`, clipped cores, StructuralHolder and density
publisher describe earlier construction stages. Do not publish their old meshes,
volume fractions, slice estimates or gallery claims as current evidence.
`publish_finished.py` publishes the finished models at `/gallery/key-fan/finished/`
with exact immutable download hashes and separate current check receipts.

`../hx05_anisotropy_v1` contains comparative linear continuum studies, using
assumed anisotropy, idealized root restraints and unit loading. They are not
physical load ratings. The first inch and metric angle sweeps passed residual
and equilibrium gates; mesh refinement, boundary and bulk sensitivity remain
separate. Torx continuum meshing remains unresolved.
