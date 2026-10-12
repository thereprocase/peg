# Comparative modifier-plane continuum study

The print pose and outside body remain fixed. Only hypothetical internal dense
rib directions vary. Initial inch/metric scans use six angles and three assumed
layer-stiffness ratios, with equal added-rib volume, unit gravity/extraction/twist
loads and idealized front-domain root restraints. Residual and force/moment checks
passed those scans; changing all ribs together generally worsened the worst cases.
These are provisional comparisons, not material measurements or load ratings.
Mesh refinement and boundary/bulk sensitivity remain separate; Torx continuum
meshing is unresolved. The finished release retains the established modifier
orientation. No continuum optimization claim is made for its physical strength.

`check_formulation.py` checks affine strains, rigid modes, material positivity and
wrench resultants. `campaign.py` bounds each solve and divides 40 host threads
among eight workers. `summarize.py` compares only matching material/boundary
baselines. Front-domain meshes exclude rear peg deformation/contact explicitly.
