Bondhus fans matched to the selected green 13190 design

13189 metric: 2, 2.5, 3, 4, 5, 6, 8 and 10 mm.
33034 Torx: T9, T10, T15, T20, T25, T27, T30 and T40.
The separate approved green inch file remains unchanged.

Extract the bundle and run SETUP_MATCHED_FANS.FCMacro once in FreeCAD.
This installs the included hx05_family.py module under your FreeCAD user Mod
folder and opens both native documents. No extra Python packages are needed.
Save personal working copies. Keep the installed module for future recomputes.

Double-click 01_GlobalParameters or 02_KeyLayout. Edit yellow cells and press
F5. Full native rebuilds can take several minutes. Preserve the leading '='
and units, for example '=0.38 mm' or '=12 deg'. Read-only feature properties
resolve from these sheets; make dimensional changes in the sheets.

Global controls: total shaft clearance, lead-in depth/opening, seating floor,
vent diameter, base corner radius and tapered gusset width/bedward extension.
Key controls: straight guide length, upward angle, out-of-board splay, handle
roll, seated tip XYZ, outer sleeve radius and reference tool dimensions.
X is across the board, Y toward the user, Z up. Handle roll zero puts its bar
in the board plane, not necessarily horizontal. All shafts rise >=10 degrees
from seated tip to handle. Guide lengths default to max(60 mm,12x shaft size).

Metric sockets are hexagonal. Clearance is TOTAL across flats (+0.38 mm by
default), not per side. Handle axes are flat-to-flat. Only the owner's 3/5 mm
coupon fit is physically selected; other sizes and long guides need testing.
A nominal 2 mm hex can rotate fully inside a 2.38 mm AF socket: longer guides
do not fix that rotational freedom. Its displayed handle clocking is provisional.

IMPORTANT FOR TORX: circular guide diameters inherit provisional catalogue
TIP envelopes, not measurements of the full shanks. The round diameter column
controls these sockets. Circular sockets do NOT key handle rotation; the shown
handle angles are the intended placement, not an anti-rotation guarantee.
Measure the actual shanks and test fit before manufacturing the Torx holder.
Nominal AF is an unused historical proxy for this round-socket document.

Named sleeve, gusset, stock and cutting features feed native Boolean history.
The rear mount is a fixed native feature using the existing PF02/PF07 profiles;
its grid/plate outline do not change with the fan spreadsheets. FinalHolder is
the finished solid: select ONLY that object for STEP/STL export. ReferenceTools
can be shown with Space. Failed features expose LastError; restore the prior
cell values before export. The FCStd is viewable without the module but custom
features require the module to recompute.

Long guides, filled tip-end stock, 8 mm base rounds, broad print-plane gussets,
3 mm axial / 1.5 mm per-side lead-ins and below-floor 1 mm vents follow the
approved green construction. The arrangement uses that fan's frames with
set-specific lengths and direct contact-limited shifts, not a shared fan centre.

Evidence distinguishes native solids, nominal stored-tool/access sweeps,
assumed two-finger pinch approaches and print-bed geometry from qualification.
The tool grips are assumed 18 mm diameter catalogue envelopes. Check receipts
for each model's actual bed fit. No slicer job, supports, whole-holder install
motion, physical fit or structural load rating is certified. Changed parameters
invalidate the supplied arrangement checks. No previous FEA result transfers.

The installer and native documents were tested headlessly in FreeCAD 1.1.3.
Local GUI startup stalled before model loading; a Windows GUI first open has
not been tested. No Windows build is needed for the supplied native geometry.
