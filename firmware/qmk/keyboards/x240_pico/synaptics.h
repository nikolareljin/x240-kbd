#pragma once

#include <stdbool.h>
#include <stdint.h>
#include "report.h"

/* Synaptics PS/2 touchpad (ClickPad) in absolute + W mode, with the
 * TrackPoint arriving as pass-through (guest) frames.  Implements QMK's
 * custom pointing-device driver on top of the PS/2 host API. */

typedef enum {
    SYN_MODE_OFF = 0,      /* no device answered the reset             */
    SYN_MODE_RELATIVE,     /* fallback: plain PS/2 mouse, no TrackPoint */
    SYN_MODE_ABSOLUTE,     /* Synaptics absolute + W, guest decoded     */
} syn_mode_t;

typedef struct {
    syn_mode_t mode;
    uint8_t    ident[3];     /* identify query: ident[1] == 0x47 for Synaptics */
    uint8_t    caps[3];      /* capabilities query                              */
    bool       pass_through; /* capability bit: guest port present             */
    uint32_t   guest_frames; /* W == 3 frames seen since boot                   */
    uint32_t   touch_frames;
    uint32_t   resyncs;      /* bytes dropped while re-aligning                 */
} syn_state_t;

const syn_state_t *synaptics_state(void);

/* pure helpers, shared with the TrackPoint decoder and testable in isolation */
uint8_t synaptics_abs_w(const uint8_t p[6]);
bool    synaptics_abs_valid(const uint8_t p[6]);

/* HID axis limits follow the report width QMK was built with. */
#ifdef MOUSE_EXTENDED_REPORT
#    define SYN_XY_MAX INT16_MAX
#    define SYN_XY_MIN INT16_MIN
#else
#    define SYN_XY_MAX INT8_MAX
#    define SYN_XY_MIN INT8_MIN
#endif

static inline mouse_xy_report_t syn_clamp_xy(int32_t v) {
    if (v > SYN_XY_MAX) return SYN_XY_MAX;
    if (v < SYN_XY_MIN) return SYN_XY_MIN;
    return (mouse_xy_report_t)v;
}
