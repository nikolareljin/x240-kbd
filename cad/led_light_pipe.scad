/*
 * led_light_pipe.scad — carries the touchpad LED to the deck surface
 * ==================================================================
 * Print in clear PETG or natural PLA, 100 % infill, standing up, and polish
 * the tip.  Press-fits into the floor aperture (pipe_position in params.scad);
 * the flange stops it from pushing through.  The LED sits under the flange end.
 */
include <params.scad>

module light_pipe() {
    cylinder(h = pipe_len, d = pipe_d);
    cylinder(h = 1.5, d = pipe_flange_d);
}

light_pipe();
