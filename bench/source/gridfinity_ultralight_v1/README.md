# Lightweight Gridfinity pegboard shelves

Prototype 1×1 and 2×1 shelves combine open-bottom Gridfinity receivers with two
mounting columns and triangular webs. The mounting interface is the current
PF02 #9 hook / PF07 #5 upright hoop from this repository, with its original
2 mm joining nubs. Existing releases are unchanged.

## Geometry

| Property | 1×1 | 2×1 |
|---|---:|---:|
| Board-lane width | 48.8 mm | 99.6 mm |
| Peg column X positions | ±12.7 mm | ±38.1 mm |
| Gridfinity pitch | 42 mm | 42 mm |
| Frame Y extent | 5.55–51.55 mm | 5.55–51.55 mm |
| Frame top Z | 5.72 mm | 5.72 mm |
| Hook/hoop vertical pitch | 25.4 mm | 25.4 mm |
| Receiver depth at peg roots | 5.4 mm | 5.4 mm |
| Web thickness | 2.4 mm | 2.4 mm |

Coordinates are X across the board, Y outward, Z up. The board-facing datum is
Y=0.15. The native hook crown reaches Z=5.445, leaving 0.275 mm beneath the
frame's inverted bed plane. The rear edge is trimmed to the repository's
conservative nominal host envelope. That containment check does not establish
installation clearance for the current interference-fit pegs.

The receiver uses the Rebuilt Gridfinity 0.7/1.8/2.15 mm profile, initially
expanded 0.10 mm radially and shifted 0.35 mm upward to align gravity contact
with the frame top. A separate 0.20 mm mouth relief gives a 41.9 mm opening at
the bed plane. The frame and shared ridge remain coplanar. Bin contact occurs
on the tapered surfaces below the relieved lip; upward withdrawal clears the
native reference bin. This is gravity seating, with unmeasured friction.

Dimensional source:
https://github.com/kennetek/gridfinity-rebuilt-openscad/blob/main/src/core/gridfinity-baseplate.scad

The 2×1 front perimeter extends 5 mm farther down than the 1×1 rim. This
increases its local beam depth from 5 to 10 mm without entering the bin-foot
sweep. A simplified simply supported beam estimate at E=1 GPa gives about
0.29 mm deflection under a 4.905 N central load across 76.2 mm, versus 2.28 mm
for the shallow rim. This excludes joints, webs, pegboard, creep and printing
anisotropy; it is not a whole-shelf stiffness prediction.

## Files and checks

`build.py OUTPUT` runs with FreeCAD Python and the existing repository sources.
It produces native installed and inverted-pose STEP/FCStd/STL files, reference
bin geometry, and a dimensional/check receipt. `verify_native.py OUTPUT`
reopens the STEP files, checks solid material around each joining nub, samples
vertical bin withdrawal, and crops a separate 1×1 seat-fit ring.
`check_meshes.py OUTPUT` requires NumPy; it independently checks closed mesh
edges, winding and positive volume, then produces geometry-only 3MF files.
Native tessellation uses 0.005 mm linear and 0.087 rad angular deflection.
The saved-mesh gate must remain enabled: coarser trial settings left open
seams on the hooks despite valid native solids. No hole filling is used.

The reference bin represents the stated standard foot and a simple body. It is
validation geometry, not a complete catalog bin or a claim about every remix.

## Print and physical review

The candidate pose prints on the frame top, with the pegs' hoop flex remaining
in the XY layer plane. Peg overhangs still require slicer review. These are
geometry inputs, not qualified printer jobs. Check elephant-foot compensation
and the actual opening in the printed fit ring before printing the full shelf.

Suggested sequence:

1. Slice and print the separate inverted seat-fit ring in the intended material.
2. Check an actual bin seats freely and lifts out without sticking.
3. Print a 1×1 shelf and check installation/removal on the owner's board.
4. Pull the empty bin vertically and modestly forward while checking the shelf
   stays attached; repeat with representative contents only after empty testing.
5. Check neighboring bins, labels, fingers and vertical withdrawal space.

The 0.25/0.5 kg contents and 10 N front-lift scenarios in the receipt are
analytical comparisons only. Pegboard strength, printed layer strength,
hoop unsnap force, creep and retention have not been measured. There is no
physical load rating, continuous installation proof or FEA qualification.

## Recorded review

[Geometry checks and real-CAD views](../../reviews/gridfinity-ultralight-v1/README.md)
include the later ASA slice review and remaining physical tests. Run the three
scripts in the order above against one output directory. Use FreeCAD Python
for the first two and Python with NumPy for mesh checks. The repository connector
sources and their frozen station snapshot must remain at their existing relative
paths; copying this directory alone is not a self-contained CAD rebuild.
