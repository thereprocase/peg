# CF01 · cascading rectangular tool funnels v1

The right seat is highest when facing the board; middle and left descend in 25.4 mm steps. Seat centres are 25 mm apart. Adjoining funnel shells intersect into solid joints. The 99.6 mm backplate occupies four grid columns, compared with six for three separate 48.8 mm modules (32% less width).

The aperture basis is the existing rectangular-tool-funnel v3: nominal 22 × 76 mm taper mouth, 11 × 48 mm throat, 14 × 48 mm lower exit, R2 exterior corners and a 0.6 mm rim break. The lower exit transition now rises 2 mm to keep its roof steeper than 45 degrees. Clearance cuts continue upward between adjacent seats, with sloped transitions that avoid suspended ledges. The body prints upright; lower tubes and rear webs extend to a common bed at Z=-114.8 mm. The shared PF02 #9 / PF07 #5 rear geometry remains unchanged.

Generic closed-tool envelopes illustrate storage and sampled removal. They are not measured models of the owner's tools. Each reference has 19 mm wide handles and a head extending 78 mm below its mouth. The checked path lifts 82 mm, then moves 100 mm forward with the other tools stored. Real finger access, tool shapes and retention need a trial print. Through-bores remain open, as on the existing funnel; long tips can project beneath the cassette.

Source: bench/source/cascade_funnels_v1/build.py. Native CAD and print STL are bundled with exact dependencies. junctions.json records positive overlap at both funnel junctions. print-geometry.json records face angles, starting islands and bed area. installation-screen.json covers the front body along the sampled nominal board route; it does not certify changed-fit installation. stiffness.json and toolpaths.json record the local numerical and slicer reviews. Physical print, fit, handling, load and support-release tests are pending.

Stiffness is screened with second-order tetrahedra at 4 mm nominal mesh size by cascade_funnels_v1/stiffness.py. The exported build spec starts at 2.5 mm; the review script records its actual 4 mm spec alongside the result. Mesh convergence is unqualified.
