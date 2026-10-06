# CF01 v3 · slim rear webs

Each rear connecting web is narrowed from 30 to 18 mm, placing it 0.5 mm inside the lower tube on each side. This removes the tall projecting rectangular fins visible beside the funnels. All three funnel shells, apertures and touching junctions are retained. Explicit shell-containment checks guard against a CAD boolean dropping a funnel while still producing a valid solid.

The right seat is highest, with 25.4 mm steps toward the left and 25 mm between centres. The backplate remains 99.6 mm wide. Nominal mouths are 22 × 76 mm, throats 11 × 48 mm, and lower exits 14 × 48 mm. The original PF02 #9 hooks and PF07 #5 hoops are unchanged.

Print upright on the common flat bottom. The hoop flex remains in the print layers. A forward or diagonal print tilt is deferred. Load each closed tool jaws-first and lift clear of its through-bore before pulling forward. Long tips can extend below the cassette. Generic tool envelopes record clearance assumptions; actual fit, grasp, retention and handling await a physical test.

Source: bench/source/cascade_funnels_v3/build.py. Native STEP, FreeCAD, STL, exact source dependencies and per-version CAD, print geometry, tool withdrawal, installation, junction, fin-removal, stiffness and local ASA toolpath evidence accompany this revision.

The stiffness screen uses a 4 mm nominal second-order tetrahedral mesh, isotropic solid ASA E=1800 MPa and fixed peg nodes. Infill, layer bonds, mesh convergence and board compliance remain unqualified. Local slicing uses the owner's P1S / PolyLite ASA settings, 0.4 mm nozzle, 0.2 mm layers, two Arachne walls, 20% infill, 5 mm brim and organic bed supports. Physical print, support removal, fit and use remain pending.

Native volume: 236,971.62 mm³; 40,723.88 mm³ removed from v2 (14.7%). Full funnel shells survive unchanged. Planar bed contact: 2,485.70 mm²; body overhang and island screens pass. Solid-ASA deflection at 5 N: 0.0344 mm sideways and 0.0078 mm down. Local slice: 6h 38m 14s and 126.66 g, including 6.942 g of supports and interfaces behind the mounting face. Body bridge extrusion totals 0.040 g; infill internal bridges are classified separately in toolpaths.json.
