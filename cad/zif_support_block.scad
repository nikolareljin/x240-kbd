/*
 * zif_support_block.scad — backs up an FPC ZIF connector against insertion force
 * =============================================================================
 * A 0.5 mm pitch ZIF on a breakout or PCB lifts its pads when a cable is pushed
 * in at an angle.  This block sits under the connector's overhanging edge and
 * screws to the sled, so the push goes into plastic.
 *
 *   variant = "keyboard" (40-pin) | "clickpad"
 */
include <params.scad>

variant = "keyboard";
blk_w = (variant == "keyboard") ? zif_body_w + 4 : zif_cp_body_w + 4;
blk_d = zif_body_d + 4;
blk_h = sled_standoff_h + 1.6;   // reaches the underside of the connector through the board edge

module zif_block() {
    difference() {
        union() {
            translate([-blk_w / 2, 0, 0]) cube([blk_w, blk_d, sled_t]);            // foot on the sled
            translate([-blk_w / 2, blk_d - 3, 0]) cube([blk_w, 3, blk_h]);         // upright under the connector lip
        }
        for (x = [-blk_w / 2 + 3, blk_w / 2 - 3]) translate([x, 3, -1]) cylinder(h = sled_t + 2, d = 2.4);
    }
}

zif_block();
