/*
 * bottom_case.scad — X240 Pico Keyboard Bottom Enclosure
 * =======================================================
 * OpenSCAD parametric design for the 3D-printed bottom shell.
 * The X240 top section (keyboard deck + palmrest) is reused as-is.
 * This part closes the assembly from below.
 *
 * Workflow:
 *   1. Measure your X240 top section with digital calipers.
 *   2. Update the Parameters section below.
 *   3. Press F6 (Render) then File → Export → Export as STL.
 *   4. Print in PETG: 0.2 mm layers, 4 perimeter walls, 25% gyroid infill.
 *
 * Coordinate system: X = width (left/right), Y = depth (front/back), Z = height
 */

// ============================================================
// Parameters — edit these to match your measured X240 dimensions
// ============================================================

// Outer dimensions of the keyboard deck footprint (measure with calipers)
case_width  = 309.0;   // X — left to right (mm)
case_depth  = 210.0;   // Y — front to back (mm)

// Wall thickness
wall_t = 2.5;          // (mm) — 2.5 recommended for PETG strength

// Corner radius (matches X240 rounded corners)
corner_r = 3.0;

// Internal cavity height — must fit: Pico (3.5 mm) + perfboard (2 mm) + standoffs (6 mm) + cable routing
internal_h = 18.0;

// Total external case height
case_h = internal_h + wall_t;

// Screw boss dimensions (M2)
boss_od     = 6.0;     // boss outer diameter
boss_id     = 2.2;     // M2 screw hole inner diameter
boss_h      = case_h;  // bosses extend full height

// USB connector cutout
usb_c = false;         // false = Micro-USB, true = USB-C
usb_w = usb_c ? 9.5 : 8.5;   // cutout width
usb_h = usb_c ? 4.0 : 3.5;   // cutout height
// USB cutout centre position (from left edge, from front edge)
usb_x = case_width / 2;
usb_y = 0;             // rear edge (y=0 is front)

// Vent slots (set to false to disable)
vents = true;
vent_w     = 40.0;
vent_h     = 2.0;
vent_count = 4;
vent_spacing = 6.0;

// Foam gasket ledge (1 mm step around perimeter for foam tape)
gasket_depth  = 1.2;
gasket_width  = 2.0;

// Rendering quality
$fn = 64;

// ============================================================
// Screw boss positions — measured from bottom-left corner (x=0, y=0)
// Update these after measuring your X240 top section screw holes.
// ============================================================
boss_positions = [
    [  8.0,   8.0 ],   // front-left
    [ 60.0,   8.0 ],
    [150.0,   8.0 ],   // front-centre
    [250.0,   8.0 ],
    [301.0,   8.0 ],   // front-right
    [  8.0, 202.0 ],   // rear-left
    [150.0, 202.0 ],   // rear-centre
    [301.0, 202.0 ],   // rear-right
];

// ============================================================
// Modules
// ============================================================

module rounded_box(w, d, h, r) {
    // Solid box with rounded vertical corners
    hull() {
        translate([r, r, 0])       cylinder(h=h, r=r);
        translate([w-r, r, 0])     cylinder(h=h, r=r);
        translate([r, d-r, 0])     cylinder(h=h, r=r);
        translate([w-r, d-r, 0])   cylinder(h=h, r=r);
    }
}

module shell() {
    // Hollow shell: outer box minus inner cavity
    difference() {
        rounded_box(case_width, case_depth, case_h, corner_r);
        translate([wall_t, wall_t, wall_t])
            rounded_box(
                case_width  - 2*wall_t,
                case_depth  - 2*wall_t,
                case_h,          // open top (no lid — X240 top is the lid)
                max(0.1, corner_r - wall_t)
            );
    }
}

module boss(x, y) {
    translate([x, y, 0])
        difference() {
            cylinder(h=boss_h, d=boss_od);
            cylinder(h=boss_h, d=boss_id);
        }
}

module all_bosses() {
    for (pos = boss_positions)
        boss(pos[0], pos[1]);
}

module usb_cutout() {
    // Cutout through the rear wall for USB cable exit
    translate([usb_x - usb_w/2, -1, wall_t + 2])
        cube([usb_w, wall_t + 2, usb_h]);
}

module vent_slots() {
    // Horizontal slots on the bottom face for airflow
    if (vents) {
        start_x = (case_width - vent_w) / 2;
        start_y = case_depth / 2 - ((vent_count - 1) * vent_spacing) / 2;
        for (i = [0 : vent_count - 1]) {
            translate([start_x, start_y + i * vent_spacing, -1])
                cube([vent_w, vent_h, wall_t + 2]);
        }
    }
}

module gasket_ledge() {
    // Recessed step around the top perimeter for 1 mm foam gasket tape
    difference() {
        rounded_box(case_width, case_depth, gasket_depth, corner_r);
        translate([gasket_width, gasket_width, -1])
            rounded_box(
                case_width  - 2*gasket_width,
                case_depth  - 2*gasket_width,
                gasket_depth + 2,
                max(0.1, corner_r - gasket_width)
            );
    }
}

// ============================================================
// Perfboard mount rail (two parallel rails inside the case)
// The perfboard rests on these and is secured with M2 screws into bosses.
// ============================================================
rail_h      = 4.0;    // height of rail above case floor
rail_w      = 4.0;    // rail width
rail_length = 90.0;   // rail length — adjust to perfboard size
rail_x      = 40.0;   // X position of left rail
rail_y      = 80.0;   // Y position of both rails (centred roughly)
rail_sep    = 60.0;   // separation between the two rails (= perfboard width)

module perfboard_rails() {
    // Left rail
    translate([rail_x, rail_y, wall_t])
        cube([rail_w, rail_length, rail_h]);
    // Right rail
    translate([rail_x + rail_sep, rail_y, wall_t])
        cube([rail_w, rail_length, rail_h]);
}

// ============================================================
// FPC cable clip (small bridge to guide cable without kinking)
// Minimum bend radius enforced by the 5 mm bridge height.
// ============================================================
module fpc_clip(x, y) {
    clip_w   = 12.0;
    clip_d   = 4.0;
    clip_h   = 5.0;    // 5 mm = safe minimum bend radius for 0.5 mm FPC
    arch_t   = 1.5;
    translate([x, y, wall_t]) {
        difference() {
            cube([clip_w, clip_d, clip_h]);
            translate([arch_t, -1, arch_t])
                cube([clip_w - 2*arch_t, clip_d + 2, clip_h]);
        }
    }
}

// ============================================================
// Final assembly
// ============================================================
difference() {
    union() {
        shell();
        all_bosses();
        perfboard_rails();
        // Gasket ledge at the top of the case
        translate([0, 0, case_h - gasket_depth])
            gasket_ledge();
        // FPC cable guides — adjust X/Y positions to your cable routing
        fpc_clip(20, 100);
        fpc_clip(20, 120);
    }
    usb_cutout();
    vent_slots();
}
