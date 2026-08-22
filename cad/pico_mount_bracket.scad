/*
 * pico_mount_bracket.scad — Raspberry Pi Pico cradle (Rev A only)
 * ===============================================================
 * Holds a socketed Pico at a fixed height on the perfboard sled; the Rev B PCB
 * carries the Pico directly and does not need this.  Dimensions from params.scad.
 */
include <params.scad>

floor_clear = 2.0;     // under the PCB for solder joints
bracket_wall = 2.0;
lip_h = 1.5;
lip_inset = 1.0;
bracket_h = bracket_wall + floor_clear + pico_h + 1.0;

module pico_bracket() {
    difference() {
        cube([pico_w + 2 * bracket_wall, pico_d + 2 * bracket_wall, bracket_h]);
        translate([bracket_wall, bracket_wall, bracket_wall]) cube([pico_w, pico_d, bracket_h]);
        for (x = [bracket_wall / 2, pico_w + bracket_wall * 1.5], y = [bracket_wall / 2, pico_d + bracket_wall * 1.5])
            translate([x, y, -1]) cylinder(h = bracket_h + 2, d = 2.4);
        // USB opening in the front wall
        translate([pico_w / 2 + bracket_wall - usb_w / 2, -1, bracket_wall + floor_clear + 1]) cube([usb_w, bracket_wall + 2, 4]);
    }
    translate([bracket_wall, bracket_wall, bracket_wall + floor_clear + pico_h]) cube([lip_inset, pico_d, lip_h]);
    translate([bracket_wall + pico_w - lip_inset, bracket_wall, bracket_wall + floor_clear + pico_h]) cube([lip_inset, pico_d, lip_h]);
}

pico_bracket();
