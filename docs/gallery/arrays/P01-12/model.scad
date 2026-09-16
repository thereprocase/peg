// PEGSTR ARRAY GENERATOR / custom board pegs
// Derived from Pegstr by Marius Gheorghescu / mgx, supplied CC BY-NC license.
// Change the profile and counts below. Pocket sizes stay fixed.
// Model coordinates: X along board, Y outward, Z up. Dimensions in mm.
// Form review only. No slicer, load or physical-fit qualification.

profile = "P01"; // [P01:6.5 mm square seats,P09:nominal 10 mm round seats]
columns = 3;
rows = 4;

/* [Hidden] */
include <PegBoard-library.scad>
include <our-peg.scad>

holder_x_size = profile == "P01" ? 6.5 : 10;
holder_y_size = holder_x_size;
wall_thickness = profile == "P01" ? 1.8 : 3.25;
holder_height = profile == "P01" ? 12.8 : 20;
corner_radius = profile == "P01" ? 1 : 5;
holder_sides = profile == "P01" ? 30 : 20;
holder_x_count = columns;
holder_y_count = rows;
taper_ratio = 1;
strength_factor = 0.66;
closed_bottom = 0;
holder_angle = 0;
holder_offset = 0;

// The upstream polygonal rounding makes P01 very slightly under nominal width.
body_width = holder_total_x - (profile == "P01" ? 2*1.1*(1-sin(84)) : 0);
receiver_width = max(35.56, body_width);
mount_x = our_peg_columns(receiver_width);

// Pegstr's gusset algorithm now grows into OUR receiving face. The archived
// generator's separate pegboard plate and clips are not part of this holder.
// This small construction face is fully buried in the final flush back.
module pinboard(clips) {
    translate([-3.8,-receiver_width/2,-30.01650011062622])
        cube([1.4,receiver_width,37.12]);
}

module flush_receiver() {
    a=receiver_width/2;
    // The entire back is the host. No standalone handle, pad or mounting tab.
    translate([0,0.15,0]) rotate([-90,0,0]) linear_extrude(5.4)
        polygon([[-a+2,-5.12],[a-2,-5.12],[a,-3.12],[a,30],
                 [a-2,32],[-a+2,32],[-a,30],[-a,-3.12]]);
    for(x=mount_x) translate([x,0,0]) our_peg();
}

assert(profile == "P01" || profile == "P09", "Select P01 or P09");
assert(columns >= 1 && floor(columns)==columns && rows >= 1 && floor(rows)==rows, "Counts must be positive integers");
union() {
    flush_receiver();
    multmatrix([[0,-1,0,0],[-1,0,0,1.75],[0,0,-1,-1.9834998893737792],[0,0,0,1]])
        intersection() {
            rotate([180,0,0]) pegstr();
            translate([-1002.4,-1000,-200]) cube([1000,2000,400]);
        }
}
