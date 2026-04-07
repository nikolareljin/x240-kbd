/*
 * fpc_cable_guide.scad — FPC cable strain relief clip
 * ====================================================
 * Snap-fit clip that guides FPC ribbon cables through the case
 * interior with a controlled minimum bend radius of 5 mm.
 * FPC cables crack when bent below ~3 mm radius; 5 mm is safe.
 *
 * Print multiples and place at each cable routing bend point.
 * Glue to case interior floor with cyanoacrylate or double-sided tape.
 *
 * Parameters:
 *   cable_w  — width of the FPC cable (40-pin 0.5 mm = ~22 mm)
 *   min_r    — minimum bend radius (5 mm recommended)
 */

$fn = 48;

// Cable dimensions
cable_w   = 22.0;   // FPC cable width (40-pin 0.5 mm pitch ≈ 22 mm)
cable_t   = 0.3;    // FPC cable thickness (typical)

// Minimum safe bend radius
min_r = 5.0;

// Clip body dimensions
body_t    = 2.0;    // wall thickness
clip_gap  = cable_t + 0.3;  // gap for cable + slight clearance
arch_r    = min_r + cable_t / 2;  // arch inner radius

// Snap-fit tab
tab_w     = 3.0;
tab_h     = 2.5;
tab_t     = 1.2;

module cable_guide() {
    arch_od = arch_r + body_t;
    total_w = cable_w + 2 * body_t;

    difference() {
        union() {
            // Straight entry section
            translate([-body_t, 0, 0])
                cube([total_w, body_t + arch_od, body_t + clip_gap]);

            // Arch (quarter-circle guide for bend radius)
            translate([0, arch_od, 0])
                rotate([0, 0, 0])
                rotate_extrude(angle=90)
                    translate([arch_r, 0, 0])
                        square([body_t, cable_w + 2*body_t], center=false);

            // Snap-fit retaining tab (presses cable against arch inner face)
            translate([-body_t - tab_t, arch_od - tab_w, body_t])
                cube([tab_t, tab_w, clip_gap + tab_h]);
        }

        // Cable channel through straight section
        translate([0, -1, body_t])
            cube([cable_w, body_t + arch_od + 2, clip_gap]);
    }
}

cable_guide();
