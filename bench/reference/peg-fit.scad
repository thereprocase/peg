// THE CANONICAL FIT SOURCE. Python reads these scalar assignments; OpenSCAD
// includes this same file on every render. Change fit here, then regenerate.
// Dimensions mm. Negative clearance deliberately relies on board/plastic flex.
PEG_FIT_REVISION = "rear-tongue-3p80-interference0p05";
PEG_BOARD_GRIP = 3.80;
PEG_PULL_CLEARANCE = -0.05;
PEG_TONGUE_RUN = 5.0;
PEG_TONGUE_RISE = 3.30;
PEG_HOLE_DIAMETER = 6.35;
PEG_DIAMETER = 5.6;
PEG_TONGUE_DIAMETER = 4.8;
PEG_FACE_Y = 0.15;
PEG_ROOT_Y = 1.40;
PEG_SEAT_DROP = 0.12;
PEG_PITCH = 25.4;

// Optional full-height locator array, first used by tweezer module v7.
// Existing hooked mounts keep their settled geometry. These short straight
// locators replace the loose lower locator only for explicit array callers.
// Diametral interference is a physical trial, not a measured retention force.
PEG_ARRAY_DIAMETRAL_INTERFERENCE = 0.10;
PEG_ARRAY_DEPTH = 3.80;
PEG_ARRAY_TIP_DIAMETER = 5.20;
PEG_ARRAY_LEAD_LENGTH = 1.00;

// Same primitive construction as peg_profile.py, with the exact baseline lower
// locator supplied separately. No old upper-hook STL is imported.
module canonical_functional_peg(lower_locator_mesh) {
    r=PEG_DIAMETER/2; tr=PEG_TONGUE_DIAMETER/2;
    slope=PEG_TONGUE_RISE/PEG_TONGUE_RUN;
    offset=PEG_PULL_CLEARANCE-PEG_FACE_Y-(PEG_HOLE_DIAMETER-r)/slope+tr*sqrt(1+1/(slope*slope));
    ey=-PEG_BOARD_GRIP-offset;
    z=-(PEG_HOLE_DIAMETER-PEG_DIAMETER)/2+PEG_SEAT_DROP;
    a=[0,PEG_ROOT_Y,z]; b=[0,ey,z]; c=[0,ey-PEG_TONGUE_RUN,z+PEG_TONGUE_RISE];
    R=PEG_HOLE_DIAMETER/2; cutoff=PEG_SEAT_DROP-R*cos(60);
    module segment(p,q,radius) {
        d=q-p;
        translate(p) rotate(a=acos(d.z/norm(d)),v=[-d.y,d.x,0]) cylinder(r=radius,h=norm(d),$fn=96);
    }
    union() {
        intersection() {
            union() {
                translate(a) sphere(r=r,$fn=96);
                translate(b) sphere(r=r,$fn=96);
                translate(c) sphere(r=tr,$fn=96);
                segment(a,b,r);segment(b,c,tr);
                intersection() {
                    translate([0,ey,PEG_SEAT_DROP]) rotate([-90,0,0]) cylinder(r=R,h=PEG_ROOT_Y-ey,$fn=96);
                    translate([-R-1,ey-1,PEG_SEAT_DROP-R-1]) cube([2*R+2,PEG_ROOT_Y-ey+2,cutoff-(PEG_SEAT_DROP-R-1)]);
                }
            }
            translate([-20,-60,-50]) cube([40,60+PEG_ROOT_Y,100]);
        }
        import(lower_locator_mesh,convexity=10);
    }
}
