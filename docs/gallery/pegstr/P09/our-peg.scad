// Exact custom peg adapter for OpenSCAD. Never scale this module.
// Every F6 reads peg-fit.scad. Python uses that same canonical parameter file.
// Only the unchanged lower locator is a supplied mesh; upper fit is procedural.
// Two closed solids: upper retaining peg and lower locator, 25.4 mm apart.
// Board reference face Y=0.15; material at Y>0.15 is buried shaft continuation.
// The standalone STEP's rectangular reference handle is deliberately absent.
// Host must cover each root through Y=1.40 (1.25 mm buried overlap).
// See peg-contract.json and functional-peg.step for geometry and provenance.

include <peg-fit.scad>
OUR_PEG_PITCH = PEG_PITCH;
OUR_PEG_BOARD_FACE = 0.15;
OUR_PEG_BURIED_OVERLAP = 1.25;

module our_peg() {
    canonical_functional_peg("lower-locator.stl");
}

// Module coordinates match the installed holder. Mount columns always land
// on one 25.4 mm lattice; wide hosts get extra columns, at most four grid cells
// between neighbors. All host material belongs in front of the board face.
function our_peg_columns(width) =
    assert(width >= 35.56, "Two mount columns need a receiver at least 35.56 mm wide")
    let(grid=max(1,floor((width-9.6)/OUR_PEG_PITCH)), spans=max(1,ceil(grid/4)))
    [for(i=[0:spans]) (round(i*grid/spans)-grid/2)*OUR_PEG_PITCH];
