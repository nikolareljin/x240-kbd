/*
 * trackpoint.c — decode the guest's standard PS/2 mouse packet into the HID report
 *
 * b0: Yo Xo Ys Xs 1 M R L      b1: X delta      b2: Y delta  (sign bits in b0)
 * PS/2 Y is up-positive; HID Y is down-positive — inverted here, once.
 */
#include "quantum.h"
#include "trackpoint.h"
#include "synaptics.h"

#ifndef SYN_TRACKPOINT_MULT
#    define SYN_TRACKPOINT_MULT 1
#endif
#ifndef SYN_TRACKPOINT_DEADZONE
#    define SYN_TRACKPOINT_DEADZONE 0
#endif

void trackpoint_init(void) {}

void trackpoint_handle_guest(uint8_t b0, uint8_t b1, uint8_t b2, report_mouse_t *r) {
    int16_t dx = b1 - ((b0 & 0x10) ? 256 : 0);
    int16_t dy = b2 - ((b0 & 0x20) ? 256 : 0);

    /* inclusive, as documented: |delta| <= SYN_TRACKPOINT_DEADZONE is dropped */
    if (dx >= -SYN_TRACKPOINT_DEADZONE && dx <= SYN_TRACKPOINT_DEADZONE) dx = 0;
    if (dy >= -SYN_TRACKPOINT_DEADZONE && dy <= SYN_TRACKPOINT_DEADZONE) dy = 0;

    r->buttons |= b0 & 0x07;                          /* L, R, M -> BTN1..3 */
    r->x = syn_clamp_xy((int32_t)r->x + dx * SYN_TRACKPOINT_MULT);
    r->y = syn_clamp_xy((int32_t)r->y - dy * SYN_TRACKPOINT_MULT);
}
