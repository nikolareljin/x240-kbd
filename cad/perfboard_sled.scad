/*
 * perfboard_sled.scad — tray that carries the Rev A stripboard or the Rev B PCB
 * ===========================================================================
 * Screws to the four sled bosses in the bottom case (two per half, so it bridges
 * the split seam and stiffens the joined shell).  The board sits on four M2
 * standoffs on the board's own hole pattern.  Both the stripboard and the Rev B
 * PCB are drilled to this pattern (docs/hardware/pcb.md).
 */
include <params.scad>

sled_w = board_w + 2 * sled_margin;
sled_d = board_d + 2 * sled_margin;

module sled() {
    difference() {
        union() {
            // plate
            translate([-sled_w / 2, -sled_d / 2, 0]) cube([sled_w, sled_d, sled_t]);
            // board standoffs
            for (x = [-1, 1], y = [-1, 1])
                translate([x * (board_w / 2 - board_hole_inset), y * (board_d / 2 - board_hole_inset), 0])
                    cylinder(h = sled_t + sled_standoff_h, d = sled_standoff_od);
        }
        // board M2 holes through the standoffs
        for (x = [-1, 1], y = [-1, 1])
            translate([x * (board_w / 2 - board_hole_inset), y * (board_d / 2 - board_hole_inset), -1])
                cylinder(h = sled_t + sled_standoff_h + 2, d = board_hole_d - 0.4);   // tap M2 directly into PETG
        // case boss holes
        for (o = sled_boss_offsets) translate([o[0], o[1], -1]) cylinder(h = sled_t + 2, d = board_hole_d);
        // lightening windows
        for (x = [-1, 1], y = [-1, 1])
            translate([x * 25 - 15, y * 18 - 10, -1]) cube([30, 20, sled_t + 2]);
    }
}

sled();
