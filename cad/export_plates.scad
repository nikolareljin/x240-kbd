/*
 * export_plates.scad — laser-cut plates for the hand-made route (E2) and the box insert
 * ====================================================================================
 * Flat 2D outlines derived from the SAME solids as the printed case, via projection(),
 * so the two enclosure routes cannot drift apart.  Export each as DXF:
 *
 *   openscad -D 'plate="bottom"' -o bottom.dxf export_plates.scad     (or ./dev build cad)
 *
 *   plate = "bottom"   floor plate: deck outline with the deck-boss holes, sled-boss
 *                      holes, light-pipe hole, feet and tilt-foot holes, reset hole
 *           "spacer"   perimeter ring at mid height: stack 2-3 of these (3 mm acrylic)
 *                      or one (12 mm ply) to reach internal_h, with the USB notch in the
 *                      rear edge
 *           "insert"   presentation-box foam insert: deck outline + insert_margin, with
 *                      the cable and card pockets
 *           "sheet"    every plate laid out on one sheet for a single upload
 *
 * Sheet materials: 3 mm cast acrylic or 1.5 mm aluminium for the bottom plate; 3 mm
 * acrylic x N or 12 mm plywood for the spacers.  Kerf is the cutter's problem — these
 * outlines are nominal.
 */
include <params.scad>
use <bottom_case.scad>

plate = "sheet";

spacer_usb_notch_w = usb_w + 6;      // cable passes through the spacer stack at the rear
insert_margin      = 5.0;            // foam insert clearance around the deck
insert_cable_pocket = [60, 40];      // coiled USB cable
insert_card_pocket  = [105, 74];     // A6 quick-start card, flat
sheet_gap = 10;

// ---------------------------------------------------------------- derived 2D
module deck_outline() { projection(cut = true) translate([0, 0, -case_h / 2]) whole_case(); }

module bottom_plate() {
    difference() {
        // outline of the shell at floor level
        projection(cut = true) translate([0, 0, -wall_t / 2]) whole_case();
        // through-holes the printed floor has blind: bosses become bolt holes
        for (p = deck_boss_positions) translate(p) circle(d = 3.4);                     // M3 standoffs
        for (o = sled_boss_offsets) translate(sled_center + o) circle(d = 2.4);          // M2 sled
        translate(pipe_position) circle(d = pipe_d + fit);
        for (p = foot_positions) translate(p) circle(d = 3.4);                          // screw-on feet
        for (p = tilt_positions) translate(p) circle(d = tilt_screw_d);
        translate([sled_center[0] - 30, sled_center[1] + 30]) circle(d = 3.2);          // reset
    }
}

module spacer_ring() {
    difference() {
        deck_outline();
        offset(r = -wall_t) deck_outline();
        // USB notch through the rear edge
        translate([usb_x - spacer_usb_notch_w / 2, case_depth - wall_t - 1]) square([spacer_usb_notch_w, wall_t + 2]);
        for (p = deck_boss_positions) translate(p) circle(d = 3.4);
    }
}

module box_insert() {
    difference() {
        offset(r = insert_margin) deck_outline();
        translate([20, case_depth + insert_margin - insert_cable_pocket[1] - 5]) square(insert_cable_pocket);
        translate([case_width - insert_card_pocket[0] - 20, case_depth + insert_margin - insert_card_pocket[1] - 5]) square(insert_card_pocket);
    }
}

module sheet() {
    bottom_plate();
    translate([0, case_depth + sheet_gap]) spacer_ring();
    translate([0, 2 * (case_depth + sheet_gap)]) box_insert();
}

if (plate == "bottom") bottom_plate();
else if (plate == "spacer") spacer_ring();
else if (plate == "insert") box_insert();
else sheet();
