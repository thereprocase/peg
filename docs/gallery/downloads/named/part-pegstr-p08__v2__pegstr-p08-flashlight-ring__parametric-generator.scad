// Pegstr by Marius Gheorghescu / mgx, CC BY-NC (supplied license).
// Custom peg remix: original body openings preserved; original pins removed.
// Form review only. No print or load qualification.
include <part-peg-interface__v-srcde46cec026__our-peg.scad>
union() {
  import("part-pegstr-p08__v2__pegstr-p08-flashlight-ring__receiver-host.stl");
  for(x=[-12.7, 12.7]) translate([x,0,0]) our_peg();
  multmatrix([[0,-1,0,0],[-1,0,0,1.75],[0,0,-1,-1.983499889],[0,0,0,1]])
    intersection() {
      import("part-pegstr-p08__v2__pegstr-p08-flashlight-ring__reference-original.stl");
      translate([-502.4,-250,-250]) cube([500,500,500]);
    }
}
