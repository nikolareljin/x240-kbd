/*
 * bottom_case.scad — X240 Pico keyboard bottom shell, printed as two halves
 * =========================================================================
 * The X240 top section (deck + palmrest) is the lid; this closes the assembly.
 * 309 x 210 mm exceeds every common print bed, so the shell splits at the
 * centre line with dovetail tabs in the floor, a half-lap on the front and rear
 * walls, and two alignment pins.  The perfboard sled screws across the seam and
 * is what makes the joined case stiff.
 *
 *   half = "left" | "right" | "both"     ("both" for a large-format printer)
 *
 * All dimensions come from params.scad.  Export:  F6, then File > Export > STL,
 * or ./dev build cad for every part at once.
 */
include <params.scad>

half = "left";

// ---------------------------------------------------------------- primitives
module rounded_box(w, d, h, r) {
    hull() for (x = [r, w - r], y = [r, d - r]) translate([x, y, 0]) cylinder(h = h, r = r);
}

module shell() {
    difference() {
        rounded_box(case_width, case_depth, case_h, corner_r);
        translate([wall_t, wall_t, wall_t])
            rounded_box(case_width - 2 * wall_t, case_depth - 2 * wall_t, case_h, max(0.1, corner_r - wall_t));
    }
}

module boss(x, y, h = case_h, od = boss_od, id = boss_id) {
    translate([x, y, 0]) difference() { cylinder(h = h, d = od); translate([0, 0, wall_t]) cylinder(h = h, d = id); }
}

module deck_bosses()  { for (p = deck_boss_positions) boss(p[0], p[1]); }
module sled_bosses()  { for (o = sled_boss_offsets) boss(sled_center[0] + o[0], sled_center[1] + o[1], wall_t + 4, 7, boss_id); }

module gasket_ledge() {
    translate([0, 0, case_h - gasket_depth]) difference() {
        rounded_box(case_width, case_depth, gasket_depth, corner_r);
        translate([gasket_width, gasket_width, -1])
            rounded_box(case_width - 2 * gasket_width, case_depth - 2 * gasket_width, gasket_depth + 2, max(0.1, corner_r - gasket_width));
    }
}

module stiffening_ribs() {
    if (ribs) for (x = [case_width * 0.25, case_width * 0.75])
        translate([x - rib_t / 2, wall_t, wall_t]) cube([rib_t, case_depth - 2 * wall_t, rib_h]);
}

// ---------------------------------------------------------------- cutouts
module usb_cutout() {
    translate([usb_x - usb_w / 2 - fit, case_depth - wall_t - 1, usb_z]) cube([usb_w + 2 * fit, wall_t + 2, usb_h + 2 * fit]);
}
module vent_slots() {
    if (vents) {
        sx = (case_width - vent_w) / 2; sy = case_depth / 2 - ((vent_count - 1) * vent_spacing) / 2;
        for (i = [0 : vent_count - 1]) translate([sx, sy + i * vent_spacing, -1]) cube([vent_w, vent_h, wall_t + 2]);
    }
}
module foot_recesses()   { for (p = foot_positions) translate([p[0], p[1], -1]) cylinder(h = foot_recess + 1, d = foot_d + fit); }
module tilt_screw_holes(){ for (p = tilt_positions) translate([p[0], p[1], -1]) cylinder(h = wall_t + 2, d = tilt_screw_d); }
module light_pipe_hole() { translate([pipe_position[0], pipe_position[1], -1]) cylinder(h = wall_t + 2, d = pipe_d + fit); }
module reset_hole()      { translate([sled_center[0] - 30, sled_center[1] + 30, -1]) cylinder(h = wall_t + 2, d = 3.2); }

// ---------------------------------------------------------------- split joint
// Dovetail tab profile in XY, extruded through the floor; the left half carries
// the tabs, the right half the pockets (pocket = tab grown by joint_gap).
module tab_profile(grow = 0) {
    w0 = tab_w + 2 * grow; w1 = tab_w + tab_flare + 2 * grow; l = tab_len + grow;
    polygon([[0, -w0 / 2], [l, -w1 / 2], [l, w1 / 2], [0, w0 / 2]]);
}
module floor_tabs(grow = 0) {
    for (i = [1 : tab_count])
        translate([split_x, case_depth * i / (tab_count + 1), 0])
            linear_extrude(wall_t) tab_profile(grow);
}
// Half-lap on the front and rear walls: the left wall's outer half continues past
// the seam; the right wall's outer half stops short by the same amount.
lap_len = 8;
module wall_lap(grow = 0) {
    for (y = [0, case_depth - wall_t / 2])
        translate([split_x - grow, y - grow, wall_t]) cube([lap_len + 2 * grow, wall_t / 2 + 2 * grow, case_h - wall_t + 1]);
}
module pins(grow = 0) {
    for (y = [wall_t / 4, case_depth - wall_t / 4])
        translate([split_x - pin_len / 2 - grow, y, case_h / 2]) rotate([0, 90, 0]) cylinder(h = pin_len + 2 * grow, d = pin_d + 2 * grow);
}

module whole_case() {
    difference() {
        union() { shell(); deck_bosses(); sled_bosses(); gasket_ledge(); stiffening_ribs(); }
        usb_cutout(); vent_slots(); foot_recesses(); tilt_screw_holes(); light_pipe_hole(); reset_hole();
    }
}

module left_half() {
    union() {
        difference() {
            intersection() { whole_case(); translate([-1, -1, -1]) cube([split_x + 1, case_depth + 2, case_h + 2]); }
            wall_lap(joint_gap);             // clear the lap pocket on the inner half...
            pins(joint_gap);
        }
        intersection() { whole_case(); floor_tabs(); }   // ...then add the tabs and lap tongue
        intersection() { whole_case(); wall_lap(); }
    }
}
module right_half() {
    difference() {
        intersection() { whole_case(); translate([split_x, -1, -1]) cube([case_width - split_x + 1, case_depth + 2, case_h + 2]); }
        floor_tabs(joint_gap);
        wall_lap(joint_gap);
        pins(joint_gap);
    }
}

if (!split || half == "both") whole_case();
else if (half == "left") left_half();
else right_half();
