Tweezers v10: compact, continuous RIGHT cheek
============================================

The tools may move independently of the mounting grid. The four measured-tool
cradles now sit beside the actual right cheek: negative X when facing the board.
The cheek is a continuous 3 mm wall. Each existing contoured floor overlaps it
by 2.4 mm; the broad support blocks used in v9 are gone. The heels move 12 mm
closer to the board and 6 mm lower. Slot spacing remains 42 mm and tilt 40 deg.

Keep points DOWN while storing, inserting and removing. Grasp the fused heel,
lift vertically 5 mm, then move LEFT (+X in the repository coordinates) 30 mm.
Insertion reverses that path. The open arms have no closing jaw. The guide
supports the lower arm's broad face over stations 6..64 mm from the heel; the
working points remain beyond it, with no point floor or stop.

The supplied tweezer model is placed using a proper rigid rotation, not a
reflected tool mesh. Its arms swap through a 180-degree roll about the length
axis; the heel-to-point axis stays downward. This establishes its orientation
in the station, and does not add a flipping step during insertion or removal.

The exact v9 receiver and pegs are preserved: two upper PF02 #9 hooks, four
loose bearing pegs and two PF06-style bottom latches. The receiver width is
48.8 mm, mounting columns remain X = +/-12.7 mm, and occupied rows remain
0, 2, 4 and 6. The scalar fit source SHA256 is
9328ccc5d4bfd4ef7f5c88efb68cc4714da8b0017cd2c2d0a85e52ddc1669f3a.
The included fit-pf02-clamp-0.49.scad is a frozen provenance snapshot, not a
second editable fit authority. That hash identifies the PF02 clamp snapshot;
the exact v9 baseline STEP hash and
the retained-geometry comparison also identify the added ribs and latch.

Print preparation and fit
-------------------------
The full print STL lies on its actual negative-X right cheek, with Z minimum
zero. The face is solid and continuous; no windows cut through the bed face.
The projecting pegs still require local support and an inspection of actual
toolpaths. These are CAD/mesh print-preparation inputs, not printer-ready jobs.

Print the small single-throat coupon first. Hold it at the station's 40-degree
incline with the points down. Check the measured tweezer's body
seat, lateral rocking, arm opening and short lift/left movement. The nominal
side clearance remains 0.08 mm per edge over the closer guides, with 0.35 mm
aft and lower-face allowance. The outline/opening are reconstructed estimates.
The coupon includes a short flat cheek to reproduce this print orientation.

All four slots repeat the supplied 122.76 mm bent tweezer. The measured aft
dimensions are TOTAL fused thicknesses: 1.17 mm at the heel, then 1.31 mm a
little forward. The 1.47 mm photo dimension belongs to a separated forward arm.
Other tweezer shapes are not fitted or physically tested by this model.

Verification
------------
The design-and-checks JSON records the actual CAD volumes, print bounds, bed
contact area, baseline hash, exact receiver/peg comparison and mesh hashes.
review.py checks the actual exported meshes with the other three tools present.
Adaptive translation distance bounds cover both complete removal segments.
The reverse path establishes the same nominal insertion clearance. The point
region is checked separately; a downward displacement checks for a body stop.
Those results exclude hand clearance, print tolerance, bending and contact
forces. The interfering v9 peg fit remains its own physical prototype.

CAD volume savings compare the regenerated complete v9 and v10 solids. They
are not a prediction of sliced filament savings or a load/strength rating.

Rebuild
-------
Use Python 3.12 with ../tweezers_v8/requirements.txt for front.py and review.py.
Use a complete FreeCAD Python runtime for holder.py. The v10 source depends on
the unchanged v8 guide/model source and the existing bench geometry envelope.

  cadpy front.py BUILD_DIR
  freecad-python holder.py BUILD_DIR V9_INSTALLED_STEP
  cadpy review.py BUILD_DIR

The self-contained release bundle includes the exact regenerated v9 baseline
STEP from the v9 development release, the minimal public source/reference tree,
exported CAD/meshes and review
evidence. Supply that baseline STEP to holder.py. To rebuild v9 itself, use the
unchanged bench/source/tweezers_v9 sources on the fit-ladder branch at 9f5c923.
Raw photographs, photogrammetry scans and printer credentials are excluded.
