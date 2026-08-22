/*
 * usb_strain_relief.scad — bezel that grips the USB cable in the case cutout
 * ==========================================================================
 * A pull on the cable loads this block (screwed to the case floor) and the
 * cable jacket pinched in its channel, never the Pico's receptacle.  Print in
 * two halves that bolt together around the cable, or thread the cable through
 * before plugging it into the Pico.
 */
include <params.scad>

channel_d = cable_d + 0.2;

module strain_relief_half() {
    difference() {
        translate([-relief_w / 2, 0, 0]) cube([relief_w, relief_d, relief_h / 2]);
        // cable channel, half round, along Y
        translate([0, -1, relief_h / 2]) rotate([-90, 0, 0]) cylinder(h = relief_d + 2, d = channel_d);
        // ribs that bite the jacket
        for (y = [3, relief_d - 3]) translate([0, y, relief_h / 2]) rotate([-90, 0, 0]) cylinder(h = 1, d = channel_d - 0.6);
        // two M2 bolts clamping the halves
        for (x = [-relief_w / 2 + 4, relief_w / 2 - 4]) translate([x, relief_d / 2, -1]) cylinder(h = relief_h, d = 2.4);
        // M2 hole to the case floor
        translate([0, relief_d / 2, -1]) cylinder(h = relief_h, d = 2.4);
    }
}

strain_relief_half();
translate([0, relief_d + 5, 0]) strain_relief_half();
