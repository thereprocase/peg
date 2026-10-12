# Connected-v3 tensile calculation — scope and rejected continuum results

The whole-holder tensile factor of safety is **not established**. The isolated
straight-sleeve nominal axial calculation is usable as an explicit first-pass
section estimate; the continuum peak-stress ratios in the accompanying JSON
files are **rejected as physical safety factors**.

This study uses the finished connected-v3 geometry published at commit
2e8b16fd8f413b97240b3089fe5d18400576ba69. It changes no manufacturing geometry,
tested fits, modifiers, print pose or release assets.

## Isolated sleeve calculation

Assume a 100 N axial tensile load carried uniformly by an intact 1.2 mm solid
socket band. Credit no surrounding perimeter walls, ribs or sparse infill beyond
that band. Use the modeled +0.38 mm opening clearance. For a hex opening of
across-flats dimension s and band thickness t:

    A = sqrt(3)/2 * ((s + 2*t)^2 - s^2)
    sigma = F/A
    nominal tensile factor = reference_strength/sigma

For the round Torx-shank sockets replace sqrt(3)/2 by pi/4 and use the nominal
modeled shank diameter plus clearance. These are round-shank seats, not Torx
star-section sockets.

| Set | Governing sleeve | Band area (mm²) | Nominal stress at 100 N (MPa) | Factor using 30 MPa | Factor using assumed 15 MPa |
|---|---|---:|---:|---:|---:|
| 13190 inch | 3/32 | 16.467 | 6.073 | 4.94 | 2.47 |
| 13189 metric | 2 mm | 14.882 | 6.720 | 4.46 | 2.23 |
| 33034 Torx | T9 shank | 14.118 | 7.083 | 4.24 | 2.12 |

These factors halve at 200 N and double at 50 N. They describe uniform direct
tension in the straight sleeve, **not** bending at the mouth, the lead-in,
vent intersections, rib/sleeve attachment, peg roots, interlayer shear,
installation stress, creep or impact. Ignoring surrounding material makes the
credited area smaller, but omitting stress concentrations does not make the
complete fracture prediction conservative.

The [manufacturer's PolyLite ASA page](https://polymaker.com/product/polylite-asa)
lists 38.6 MPa XY and 30.0 MPa Z tensile strengths. The newer
[V6.0 technical sheet](https://polymaker.com/wp-content/uploads/lana-downloads/TDS_Polymaker_ASA-V6.0_2025-12-02_EN.pdf)
lists 43.8 MPa XY and 32 MPa Z, with specimen printing conditions including
100% infill, 260°C nozzle, fan off and 90°C environmental temperature. This
study retains **30 MPa as a reference**, not a verified lower bound for the
owner's P1S print. The 15 MPa column is an **assumed 50% strength sensitivity**;
it is not measured P1S coupon strength or a material standard allowable.

`socket-axial-section.json` preserves all 26 calculations and the input hash.
The source's independent regular-hex and circle area checks pass.

## Attempted whole-body tensile screen

On keith-box (port 22), the existing front-domain meshes were classified against
all four actual connected-v3 modifier meshes transformed with each actual print
pose. Nominal skins were assumed as three 0.42 mm walls and five 0.2 mm top/bottom
layers. Bulk stiffness was assumed 0.025 of solid, with 5% solid fraction for
sparse-phase stress recovery; layer stiffness was 0.9 of in-plane stiffness.
These bulk and wall assumptions are not measurements of the owner's toolpaths.

Load cases were 5 N at every key grip center plus 5.1 N uniformly distributed
holder weight, then that gravity case plus one key receiving either 100 N axial
pull, 20 N downward grip force, or 1 N·m axial torque. These are stated screening
loads, not operator-measured loads. The front-domain root patches were clamped;
rear pegs, board contact and snap preload were omitted.

The isolated tensor mapping/principal-value invariance, affine strain, six rigid
modes, positive-definite material and exact applied wrench checks passed. The
Torx and metric solves passed residual and resultant force/moment gates. The
inch solve failed the resultant force/moment gates, despite its small relative
linear-system residual. No factor from that inch solve is accepted.

The Torx and metric maxima were in near-degenerate elements: representative
critical tetrahedron volumes were 1.84e-10 and 4.66e-10 mm³, mean-ratio qualities
0.000254 and 0.000102. They produced thousands of MPa under the screening loads.
These peaks do not resolve physical FDM material at a 0.2 mm layer scale and
are not usable fracture predictions. Percentile filtering would hide the
problem, not establish the minimum safety factor.

The centroid classification also overestimated metric rib volume (148,357 mm³
inside the tetrahedra versus 128,282 mm³ in the entire raw rib mesh), proving
the 1.2 mm reinforcement field needs finer integration/resolution. This is
another independent reason to reject the current whole-body factors.

Two bounded replacement-mesh paths were attempted for each set: surface
reparameterization/remeshing and native BREP meshing. The former reported
topology/overlapping-facet errors; the latter crashed at intersecting curves.
Those replacement files are not accepted meshes. Manufacturing geometry was
not edited to make these numerical methods succeed.

To establish a whole-holder estimate, use a valid analysis mesh resolving the
thin bands and actual skin, compare at least two resolutions and boundary/bulk
assumptions, include a separate peg/contact model, and use a tensile strength
appropriate to the actual print conditions. Local peak stresses must converge
or be assessed with a justified physical length scale. A printed destructive
test remains distinct from that calculated estimate.

The baseline JSON files are diagnostic records only; their field
`raw_strength_to_peak_stress_ratio` must not be quoted as a physical safety
factor. No whole-rack tensile rating was added to the finished gallery.
