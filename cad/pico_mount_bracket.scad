/*
 * pico_mount_bracket.scad — Raspberry Pi Pico mounting bracket
 * =============================================================
 * A simple cradle that holds the Pico PCB at a fixed height
 * inside the bottom case. Print separately and glue or screw
 * into the bottom case before mounting the Pico.
 *
 * Pico dimensions: 51 mm × 21 mm × 3.5 mm (PCB only)
 * Clearance below Pico for solder joints: 2 mm
 */

$fn = 48;

// Pico PCB dimensions
pico_w = 51.0;
pico_d = 21.0;
pico_h = 3.5;   // PCB thickness

// Clearance under PCB for component legs / solder joints
floor_clear = 2.0;

// Bracket wall thickness
wall_t = 2.0;

// Total bracket height = floor + clearance + PCB thickness + 1 mm lip
bracket_h = wall_t + floor_clear + pico_h + 1.0;

// Mounting hole diameter (M2 screw through bracket into case)
mount_hole_d = 2.4;

// PCB retention lip height (keeps Pico from sliding out)
lip_h = 1.5;
lip_inset = 1.0;

module pico_bracket() {
    difference() {
        // Outer shell
        cube([pico_w + 2*wall_t, pico_d + 2*wall_t, bracket_h]);

        // Inner cavity — clears Pico PCB + underside clearance
        translate([wall_t, wall_t, wall_t])
            cube([pico_w, pico_d, bracket_h]);

        // Mount holes — one at each corner of the bracket
        for (x = [wall_t/2, pico_w + wall_t + wall_t/2])
            for (y = [wall_t/2, pico_d + wall_t + wall_t/2])
                translate([x, y, -1])
                    cylinder(h = bracket_h + 2, d = mount_hole_d);

        // USB cutout in front wall (Micro-USB port on Pico)
        translate([pico_w/2 + wall_t - 4.5, -1, wall_t + floor_clear + 1])
            cube([9.0, wall_t + 2, 4.0]);
    }

    // Retention lips — two small tabs that hook over the Pico PCB edges
    translate([wall_t, wall_t, wall_t + floor_clear + pico_h])
        cube([lip_inset, pico_d, lip_h]);
    translate([wall_t + pico_w - lip_inset, wall_t, wall_t + floor_clear + pico_h])
        cube([lip_inset, pico_d, lip_h]);
}

pico_bracket();
