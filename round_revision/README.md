# Round bearing pegs — working revision

The user requested true round pegs because the rectangular baseline loads the lower outside corners of round pegboard holes. This revision replaces the upper neck, retaining tongue, and lower locator with circular bearing geometry. Diameter (or diametral clearance) and board thickness are independent parameters.

This is an active design checkpoint. The baseline remains preserved at the repository root. The round candidate has valid solids and meshes and an interference-free nominal seated pose; final diameter selection, continuous insertion/removal evidence, and new printing supports are being completed. The baseline motion proof and support recipe do not transfer automatically.

- `round_anchor.py` builds the real 3D circular geometry in CadQuery.
- `round_motion.py` checks the upper capsule geometry and bounds the lower round locator with conservative X slabs for motion about X.
- `render_bearing.py` creates the exact transverse geometry comparison.

A smooth round bearing crown removes the sharp lower corner contact. Actual pressure and bearing width depend on material deformation and load; they have not been simulated or physically measured. A larger round section can reduce transverse clearance, but seated retention and axial looseness also depend on the retaining tongue and front bearing face.

Round undersides need new support strategies. Side printing protects the main hook load path but no longer has the flat underside of the rectangular extrusion. Upright printing requires support below the earliest circular underside; the previous pair of edge webs cannot simply be reused.
