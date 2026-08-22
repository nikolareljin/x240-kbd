#pragma once

/* ------------------------------------------------------------------------
 * Matrix — custom scan (matrix.c)
 *
 * Drive lines are pulled LOW one at a time; sense lines are read through
 * three cascaded 74HC165 shift registers over SPI0.  The 10 x 24 size is the
 * chain's capacity.  The real key -> (drive, sense) map comes from probing
 * (hardware/pinout/x240_keyboard_fpc_pinout.md) and regenerates the LAYOUT.
 * ------------------------------------------------------------------------ */
#define MATRIX_DRIVE_PINS { GP0, GP1, GP2, GP3, GP4, GP5, GP6, GP7, GP8, GP9 }

#define SENSE_PL_PIN   GP17          /* 74HC165 parallel load, active LOW   */
#define SENSE_CHAIN_BYTES 3          /* 3 chips x 8 inputs = 24 sense lines */

/* SPI0: SCK = GP18 -> 74HC165 CP, RX = GP16 <- U1 Q7.  No MOSI, no chip select. */
#define SPI_DRIVER   SPID0
#define SPI_SCK_PIN  GP18
#define SPI_MISO_PIN GP16
#define SPI_MOSI_PIN NO_PIN
#define SENSE_SPI_DIVISOR 16         /* ~7.8 MHz from the 125 MHz peripheral clock */

#define DEBOUNCE 5
#define MATRIX_IO_DELAY 30           /* us after a drive line goes LOW, before latching */

/* ------------------------------------------------------------------------
 * PS/2 — RP2040 PIO host.  Pins come from keyboard.json ("ps2" block):
 * DATA = GP21, CLK = GP22.  The PIO driver requires CLK = DATA + 1.
 * Both lines need 4.7 kOhm pull-ups to 3V3 on the board.
 * Pointing is synaptics.c (custom driver); see rules.mk for why.
 * ------------------------------------------------------------------------ */
#define POINTING_DEVICE_TASK_THROTTLE_MS 1

/* Synaptics absolute units are ~0..6143 on X, ~0..5119 on Y. */
#define SYN_TOUCHPAD_DIVISOR   8     /* absolute units per HID count            */
#define SYN_TOUCH_THRESHOLD    30    /* Z above this = finger down               */
#define SYN_TRACKPOINT_MULT    1     /* guest packet counts per HID count        */
#define SYN_TRACKPOINT_DEADZONE 0    /* |delta| <= this is dropped (drift guard) */
/* #define SYN_INVERT_Y */           /* uncomment if the cursor moves the wrong way vertically */

/* ------------------------------------------------------------------------
 * Backlight — software PWM on GP26 -> MOSFET gate (QMK #24470 workaround)
 * ------------------------------------------------------------------------ */
#define BACKLIGHT_PIN     GP26
#define BACKLIGHT_LEVELS  5
/* No BACKLIGHT_BREATHING: the software PWM driver refuses it at compile time
 * ("Backlight breathing is not available for software PWM").  Levels only. */

/* Power button — GP27, active LOW, internal pull-up; long-press guard in x240_pico.c */
#define POWER_BUTTON_PIN GP27
#define POWER_BUTTON_HOLD_MS 500

/* Touchpad indicator LED — GP28 HIGH = on */
#define TOUCHPAD_LED_PIN GP28

/* NKRO default is host.default.nkro in keyboard.json */
