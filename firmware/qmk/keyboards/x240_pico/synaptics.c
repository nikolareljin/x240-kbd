/*
 * synaptics.c — Synaptics ClickPad + TrackPoint pass-through as a QMK pointing device
 *
 * Protocol reference: Linux drivers/input/mouse/synaptics.c (the official
 * "TouchPad Interfacing Guide" is no longer hosted).
 *
 * Init:   reset -> identify (magic 0x47) -> capabilities -> mode 0xC1
 *         (absolute, 80 pps, W mode) -> enable the guest through the pass-through
 *         -> enable streaming.  Any failure falls back to plain relative mode and
 *         says so on the console — never a silent success with a dead TrackPoint.
 *
 * Stream: 6-byte packets.  W == 3 is a pass-through frame carrying the guest's
 *         standard 3-byte PS/2 packet in bytes 1, 4, 5 -> trackpoint.c.
 *         Anything else is finger data: absolute X/Y/Z -> relative delta.
 */
#include "quantum.h"
#include "pointing_device.h"
#include "ps2.h"
#include "synaptics.h"
#include "trackpoint.h"

#define PS2_CMD_RESET        0xFF
#define PS2_CMD_ENABLE       0xF4
#define PS2_CMD_DISABLE      0xF5
#define PS2_CMD_SET_RATE     0xF3
#define PS2_CMD_SET_RES      0xE8
#define PS2_CMD_STATUS       0xE9
#define PS2_BAT_OK           0xAA

#define SYN_QUERY_IDENTIFY   0x00
#define SYN_QUERY_CAPS       0x02
#define SYN_MAGIC            0x47
#define SYN_MODE_BYTE        0xC1   /* absolute | rate 80 | W mode */
#define SYN_RATE_SET_MODE    0x14   /* F3 0x14 after the special sequence = set mode byte */
#define SYN_RATE_PASSTHROUGH 0x28   /* F3 0x28 after the special sequence = send to guest */

#ifndef SYN_TOUCHPAD_DIVISOR
#    define SYN_TOUCHPAD_DIVISOR 8
#endif
#ifndef SYN_TOUCH_THRESHOLD
#    define SYN_TOUCH_THRESHOLD 30
#endif

static syn_state_t st;

/* touch-to-delta state */
static bool     finger_down = false;
static uint16_t last_x, last_y;

/* packet assembly */
static uint8_t pkt[6];
static uint8_t pkt_len = 0;

const syn_state_t *synaptics_state(void) {
    return &st;
}

/* ---------------------------------------------------------------- pure helpers */

uint8_t synaptics_abs_w(const uint8_t p[6]) {
    return ((p[0] & 0x30) >> 2) | ((p[0] & 0x04) >> 1) | ((p[3] & 0x04) >> 2);
}

bool synaptics_abs_valid(const uint8_t p[6]) {
    return (p[0] & 0xC8) == 0x80 && (p[3] & 0xC8) == 0xC0;
}

/* ---------------------------------------------------------------- PS/2 plumbing */

/* Send a command byte; true if the device ACKed. */
static bool cmd(uint8_t c) {
    ps2_error = PS2_ERR_NONE;
    uint8_t r = ps2_host_send(c);
    return ps2_error == PS2_ERR_NONE && r == PS2_ACK;
}

static bool recv_into(uint8_t *out) {
    ps2_error = PS2_ERR_NONE;
    uint8_t r = ps2_host_recv_response();
    if (ps2_error != PS2_ERR_NONE) return false;
    *out = r;
    return true;
}

/* Synaptics "special command": four SetResolution with 2-bit chunks of arg, MSB pair first. */
static bool special(uint8_t arg) {
    for (int8_t shift = 6; shift >= 0; shift -= 2) {
        if (!cmd(PS2_CMD_SET_RES)) return false;
        if (!cmd((arg >> shift) & 0x03)) return false;
    }
    return true;
}

static bool query(uint8_t q, uint8_t out[3]) {
    if (!special(q)) return false;
    if (!cmd(PS2_CMD_STATUS)) return false;
    return recv_into(&out[0]) && recv_into(&out[1]) && recv_into(&out[2]);
}

static bool set_mode(uint8_t mode) {
    return special(mode) && cmd(PS2_CMD_SET_RATE) && cmd(SYN_RATE_SET_MODE);
}

/* One byte to the pass-through guest (what Linux's synaptics_pt_write does). */
static bool guest_write(uint8_t b) {
    return special(b) && cmd(PS2_CMD_SET_RATE) && cmd(SYN_RATE_PASSTHROUGH);
}

static bool reset_device(void) {
    if (!cmd(PS2_CMD_RESET)) return false;
    uint8_t bat = 0, id = 0;
    /* BAT completion 0xAA then device id 0x00 — allow the slow path (~500 ms) */
    for (uint8_t tries = 0; tries < 8 && !recv_into(&bat); tries++) {
        wait_ms(100);
    }
    recv_into(&id);
    return bat == PS2_BAT_OK;
}

static void fallback_relative(const char *why) {
    dprintf("synaptics: %s -> relative mode, TrackPoint unavailable\n", why);
    st.mode = SYN_MODE_RELATIVE;
    pkt_len = 0;
    reset_device();
    cmd(PS2_CMD_ENABLE);
}

/* ---------------------------------------------------------------- QMK driver hooks */

bool pointing_device_driver_init(void) {
    memset(&st, 0, sizeof(st));
    ps2_host_init();
    wait_ms(50);

    if (!reset_device()) {
        dprintf("synaptics: no device after reset (ps2_error=%u)\n", ps2_error);
        st.mode = SYN_MODE_OFF;
        return false;
    }
    cmd(PS2_CMD_DISABLE);

    if (!query(SYN_QUERY_IDENTIFY, st.ident) || st.ident[1] != SYN_MAGIC) {
        fallback_relative("identify failed (not 0x47)");
        return true;
    }
    dprintf("synaptics: id=%02X %02X %02X model %u.%u\n", st.ident[0], st.ident[1], st.ident[2],
            st.ident[2] & 0x0F, st.ident[0]);

    if (query(SYN_QUERY_CAPS, st.caps)) {
        st.pass_through = (st.caps[2] & 0x80) != 0;   /* SYN_CAP_PASS_THROUGH, as Linux */
        dprintf("synaptics: caps=%02X %02X %02X pass_through=%u\n", st.caps[0], st.caps[1], st.caps[2],
                st.pass_through);
    }

    if (!set_mode(SYN_MODE_BYTE)) {
        fallback_relative("mode byte rejected");
        return true;
    }

    if (st.pass_through) {
        if (!guest_write(PS2_CMD_ENABLE)) {
            dprintf("synaptics: guest enable not ACKed — TrackPoint may be absent\n");
        }
    } else {
        dprintf("synaptics: no pass-through capability — TrackPoint will not appear on this bus\n");
    }

    cmd(PS2_CMD_ENABLE);
    st.mode = SYN_MODE_ABSOLUTE;
    trackpoint_init();
    return true;
}

static void handle_touch(const uint8_t p[6], report_mouse_t *r) {
    uint16_t x = ((p[3] & 0x10) << 8) | ((p[1] & 0x0F) << 8) | p[4];
    uint16_t y = ((p[3] & 0x20) << 7) | ((p[1] & 0xF0) << 4) | p[5];
    uint8_t  z = p[2];

    if (p[0] & 0x01) r->buttons |= MOUSE_BTN1;
    if (p[0] & 0x02) r->buttons |= MOUSE_BTN2;

    if (z > SYN_TOUCH_THRESHOLD) {
        if (finger_down) {
            int32_t dx = ((int32_t)x - (int32_t)last_x) / SYN_TOUCHPAD_DIVISOR;
            int32_t dy = ((int32_t)last_y - (int32_t)y) / SYN_TOUCHPAD_DIVISOR; /* pad Y is up-positive */
#ifdef SYN_INVERT_Y
            dy = -dy;
#endif
            r->x = syn_clamp_xy((int32_t)r->x + dx);
            r->y = syn_clamp_xy((int32_t)r->y + dy);
        }
        finger_down = true;
        last_x      = x;
        last_y      = y;
    } else {
        finger_down = false;
    }
}

static void handle_relative(const uint8_t p[3], report_mouse_t *r) {
    int16_t dx = p[1] - ((p[0] & 0x10) ? 256 : 0);
    int16_t dy = p[2] - ((p[0] & 0x20) ? 256 : 0);
    r->buttons |= p[0] & 0x07;
    r->x = syn_clamp_xy((int32_t)r->x + dx);
    r->y = syn_clamp_xy((int32_t)r->y - dy);   /* PS/2 Y is up-positive, HID is down-positive */
}

report_mouse_t pointing_device_driver_get_report(report_mouse_t r) {
    if (st.mode == SYN_MODE_OFF) return r;
    const uint8_t want = (st.mode == SYN_MODE_ABSOLUTE) ? 6 : 3;

    while (pbuf_has_data()) {
        ps2_error = PS2_ERR_NONE;
        uint8_t b = ps2_host_recv();
        if (ps2_error != PS2_ERR_NONE) {
            pkt_len = 0;
            continue;
        }
        pkt[pkt_len++] = b;
        if (pkt_len < want) continue;

        if (st.mode == SYN_MODE_ABSOLUTE) {
            if (!synaptics_abs_valid(pkt)) {
                memmove(pkt, pkt + 1, 5);      /* drop one byte, keep looking */
                pkt_len = 5;
                st.resyncs++;
                continue;
            }
            if (synaptics_abs_w(pkt) == 3) {
                st.guest_frames++;
                trackpoint_handle_guest(pkt[1], pkt[4], pkt[5], &r);
            } else {
                st.touch_frames++;
                handle_touch(pkt, &r);
            }
        } else {
            if (!(pkt[0] & 0x08)) {            /* bit 3 is always set in a valid relative packet */
                memmove(pkt, pkt + 1, 2);
                pkt_len = 2;
                st.resyncs++;
                continue;
            }
            handle_relative(pkt, &r);
        }
        pkt_len = 0;
    }
    return r;
}

uint16_t pointing_device_driver_get_cpi(void) {
    return 0;
}

void pointing_device_driver_set_cpi(uint16_t cpi) {}
