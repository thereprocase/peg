// Pegstr by Marius Gheorghescu / mgx, CC BY-NC (supplied license).
// Custom peg remix: original body openings preserved; original pins removed.
// Form review only. No print or load qualification.
include <our-peg.scad>
union() {
  import("receiver-host.stl");
  for(x=[-12.7, 12.7]) translate([x,0,0]) our_peg();
  multmatrix([[0,-1,0,0],[-1,0,0,1.75],[0,0,-1,-1.983499889],[0,0,0,1]])
    intersection() {
      import("original.stl");
      translate([-502.4,-250,-250]) cube([500,500,500]);
    }
}
