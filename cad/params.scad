/*
 * params.scad — every dimension the printed parts share, in millimetres.
 * ======================================================================
 * Included by all cad/*.scad files. No dimension may be duplicated in a part
 * file; if two parts need the same number, it lives here.
 *
 * Values marked MEASURE are design targets until caliper measurements of a real
 * X240 top section replace them (issue #44). Everything else is a design choice.
 */

// ---------------------------------------------------------------- deck / case
case_width  = 309.0;   // MEASURE  X, left to right, at the deck's mating surface
case_depth  = 210.0;   // MEASURE  Y, front (palmrest) to back
wall_t      = 2.5;     // PETG shell wall
corner_r    = 3.0;     // MEASURE  outer corner radius
internal_h  = 18.0;    // floor-to-deck clearance (see docs/enclosure/integration.md)
case_h      = internal_h + wall_t;

// Screw bosses that meet the X240 deck, from the front-left corner.  MEASURE all.
deck_boss_positions = [
    [  8.0,   8.0 ], [ 60.0,   8.0 ], [150.0,   8.0 ], [250.0,   8.0 ], [301.0,   8.0 ],
    [  8.0, 202.0 ], [150.0, 202.0 ], [301.0, 202.0 ],
];
boss_od = 6.0;
boss_id = 3.2;         // M2 heat-set insert hole (insert OD ~3.2 for a 3.5 mm body)

// ---------------------------------------------------------------- split joint
split      = true;     // print as two halves (fits a 220 mm bed); false = one piece
split_x    = case_width / 2;
tab_count  = 3;        // dovetail tabs along the floor seam
tab_w      = 14.0;     // tab width at the seam
tab_flare  = 3.0;      // extra width at the tip (dovetail angle)
tab_len    = 10.0;     // how far the tab reaches into the other half
joint_gap  = 0.15;     // clearance per face; tune with a 30 mm coupon
pin_d      = 3.0;      // alignment pins through the front/rear walls
pin_len    = 10.0;

// ---------------------------------------------------------------- board / sled
board_w    = 100.0;    // stripboard or Rev B PCB
board_d    = 80.0;
board_hole_inset = 4.0;                  // M2 holes this far from each board corner
board_hole_d     = 2.4;
sled_margin      = 6.0;                  // sled extends this far past the board
sled_t           = 2.0;
sled_standoff_h  = 6.0;                  // board sits this high above the sled
sled_standoff_od = 5.0;
// sled centre in the case (rear-centre; see docs/enclosure/integration.md)
sled_center = [ case_width / 2, case_depth - 8 - board_d / 2 - sled_margin - 6 ];
// sled-to-case bosses (around the sled, two per half so the sled bridges the seam)
sled_boss_offsets = [ [-56, -46], [56, -46], [-56, 46], [56, 46] ];

// ---------------------------------------------------------------- Pico
pico_w = 51.0;
pico_d = 21.0;
pico_h = 1.0;          // PCB thickness
pico_hole_d = 2.1;     // Pico mounting holes, 11.4 x 47 mm pattern
pico_hole_dx = 47.0;
pico_hole_dy = 11.4;

// ---------------------------------------------------------------- USB
usb_c     = false;                     // false = Micro-USB cutout, true = USB-C
usb_w     = usb_c ? 9.5 : 8.5;
usb_h     = usb_c ? 4.0 : 3.5;
usb_x     = sled_center[0];            // cutout centred on the board
usb_z     = wall_t + sled_t + sled_standoff_h + 1.6;   // bottom of the Pico's connector
cable_d   = 4.5;                       // USB cable jacket diameter
relief_w  = 22.0;                      // strain-relief bezel footprint
relief_d  = 12.0;
relief_h  = 10.0;

// ---------------------------------------------------------------- FPC
fpc_w        = 22.0;   // 40-pin 0.5 mm cable width
fpc_t        = 0.3;
fpc_min_r    = 5.0;    // minimum bend radius
clickpad_fpc_w = 8.0;  // MEASURE  ClickPad cable width
zif_body_w   = 26.0;   // 40-pin ZIF connector body length along the cable edge
zif_body_d   = 6.0;
zif_body_h   = 5.0;
zif_cp_body_w = 12.0;  // ClickPad ZIF body (pin count from probing)

// ---------------------------------------------------------------- gasket, vents, feet
gasket_depth = 1.2;
gasket_width = 2.0;
vents        = false;  // not thermally needed (docs/enclosure/durability.md)
vent_w = 40.0; vent_h = 2.0; vent_count = 4; vent_spacing = 6.0;
ribs         = true;   // two front-to-back stiffening ribs in the floor
rib_t        = 2.0;
rib_h        = 4.0;

foot_d       = 10.0;   // rubber feet, front
foot_recess  = 1.0;
foot_positions = [ [25, 20], [case_width - 25, 20] ];
tilt_positions = [ [25, case_depth - 20], [case_width - 25, case_depth - 20] ];
tilt_h       = 12.0;   // rear riser height
tilt_w       = 30.0;
tilt_d       = 20.0;
tilt_screw_d = 3.4;    // M3 clearance

// ---------------------------------------------------------------- LED light pipe
pipe_d       = 3.0;
pipe_flange_d= 5.0;
pipe_len     = internal_h - 2;
pipe_position = [ sled_center[0] + board_w / 2 + 15, sled_center[1] - 20 ];  // beside the touchpad

// ---------------------------------------------------------------- printing
fit      = 0.2;        // general hole clearance for printed-in-place fits
$fn      = 48;
