/*
 * tilt_feet.scad — rear risers for a typing angle
 * ===============================================
 * Two wedge feet bolted through the rear floor (tilt_positions in params.scad)
 * with M3 screws; a recess on the underside takes a 10 mm rubber pad.
 */
include <params.scad>

module tilt_foot() {
    difference() {
        hull() {
            translate([-tilt_w / 2, -tilt_d / 2, 0]) cube([tilt_w, tilt_d, 1]);
            translate([-tilt_w / 2 + 3, -tilt_d / 2 + 3, tilt_h - 1]) cube([tilt_w - 6, tilt_d - 6, 1]);
        }
        translate([0, 0, -1]) cylinder(h = tilt_h + 2, d = tilt_screw_d);
        translate([0, 0, tilt_h - 3]) cylinder(h = 4, d = 6.5);              // screw head pocket (top, meets the case)
        translate([0, 0, -1]) cylinder(h = foot_recess + 1, d = foot_d + fit);  // rubber pad recess (bottom)
    }
}

tilt_foot();
translate([tilt_w + 10, 0, 0]) tilt_foot();
