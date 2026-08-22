#pragma once

#include <stdint.h>
#include "report.h"

/* TrackPoint as a second pointing source.  Its packets arrive as Synaptics
 * pass-through (guest) frames; synaptics.c hands the embedded 3-byte PS/2
 * packet here. */

void trackpoint_init(void);
void trackpoint_handle_guest(uint8_t b0, uint8_t b1, uint8_t b2, report_mouse_t *r);
