// Renders the overlap of the two case halves. A correct joint produces only the
// zero-thickness seam plane (X extent ~0); any real volume means interference.
// Checked by scripts/check_cad_joint.py via ./dev test.
use <../bottom_case.scad>
include <../params.scad>
intersection() { left_half(); right_half(); }
