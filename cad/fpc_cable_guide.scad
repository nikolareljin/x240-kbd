/*
 * fpc_cable_guide.scad — FPC bend-radius clip
 * ===========================================
 * Guides the 40-pin FFC through a quarter turn at no less than fpc_min_r, so the
 * cable cannot kink at the seam or a rib.  Screws or glues to the case floor.
 *
 *   cable = "keyboard" | "clickpad"
 */
include <params.scad>

cable = "keyboard";
cw = (cable == "keyboard") ? fpc_w : clickpad_fpc_w;
body_t = 2.0;
gap = fpc_t + 0.3;
arch_r = fpc_min_r + fpc_t / 2;

module cable_guide() {
    arch_od = arch_r + body_t;
    difference() {
        union() {
            translate([-body_t, 0, 0]) cube([cw + 2 * body_t, body_t + arch_od, body_t + gap]);
            translate([0, arch_od, 0]) rotate_extrude(angle = 90) translate([arch_r, 0, 0]) square([body_t, cw + 2 * body_t]);
            translate([-body_t - 1.2, arch_od - 3, body_t]) cube([1.2, 3, gap + 2.5]);   // retaining tab
        }
        translate([0, -1, body_t]) cube([cw, body_t + arch_od + 2, gap]);
        translate([cw / 2, body_t + 2, -1]) cylinder(h = body_t + 2, d = 2.4);              // M2 to the floor
    }
}

cable_guide();
