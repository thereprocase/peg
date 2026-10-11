# Front shaft projection and print STEP handoff

`render.py BUILD` projects the reviewed tool coordinates and native holder mesh onto installed X/Z, with identical scale in all three panels. Dots identify tips and sleeve entrances. Projection overlaps do not establish 3D collisions. The compressed preview lives on Pages; the full PNG is a release asset.

`export_steps.py RELEASE_DIR` reads the frozen print-pose BREP bodies. Inch and Torx use exact rational B-spline surface conversion because direct analytic STEP reimports have unorientable vent faces. Export checks retain native BREP hashes, bounds and volume integration differences. `check_steps.py RELEASE_DIR` reopens each print STEP in FreeCAD and checks solid validity and nominal 256 mm bed placement. `publish.py WORK RENDER_DIR` installs the image, independent STEP checks and download links. The matched-fan publisher reapplies `overlay()` after regeneration. Existing immutable bundles remain unchanged; use these separate STEP downloads for printing.

Files contain holders only, in millimetres, unscaled, with the checked tip-end print orientation. Supports, compensation, brim, physical fit and loads are not qualified by this export check.
