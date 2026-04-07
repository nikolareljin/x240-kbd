#pragma once

/* USB device identity */
#define VENDOR_ID    0x6E6B
#define PRODUCT_ID   0x0240
#define DEVICE_VER   0x0001
#define MANUFACTURER "Custom"
#define PRODUCT      "ThinkPad X240 USB Keyboard"

/* Debounce in milliseconds */
#define DEBOUNCE 5

/* Matrix timing */
#define MATRIX_IO_DELAY 30

/* ---------------------------------------------------------------
 * PS/2 touchpad — UART0 hardware driver (preferred over bit-bang)
 * GP21 = CLK (UART0 CTS/TX), GP22 = DATA (UART0 RX)
 * Both lines need 4.7 kΩ pull-up resistors to 3.3 V on the board.
 * --------------------------------------------------------------- */
#define PS2_CLOCK_PIN GP21
#define PS2_DATA_PIN  GP22

/* Pointing device sensitivity — increase for faster cursor */
#define PS2_MOUSE_X_MULTIPLIER 3
#define PS2_MOUSE_Y_MULTIPLIER 3
#define PS2_MOUSE_SCROLL_BTN_SEND_DUMMY

/* ---------------------------------------------------------------
 * Backlight
 * NOTE: RP2040 hardware PWM driver has a known QMK bug (#24470).
 * Use BACKLIGHT_DRIVER = timer (set in rules.mk) as a workaround.
 * --------------------------------------------------------------- */
#define BACKLIGHT_PIN     GP26
#define BACKLIGHT_LEVELS  5
#define BACKLIGHT_BREATHING
#define BACKLIGHT_BREATHING_PERIOD 6  /* breathing cycle in seconds */

/* ---------------------------------------------------------------
 * Power button — GP27, active LOW, internal pull-up
 * Long-press guard (500 ms) is enforced in process_record_user().
 * --------------------------------------------------------------- */
#define POWER_BUTTON_PIN GP27
#define POWER_BUTTON_HOLD_MS 500

/* Touchpad indicator LED — GP28 HIGH = on */
#define TOUCHPAD_LED_PIN GP28

/* ---------------------------------------------------------------
 * N-Key Rollover
 * --------------------------------------------------------------- */
#define FORCE_NKRO

/* ---------------------------------------------------------------
 * Bootmagic — hold top-left key (row 0, col 0) while plugging in
 * to enter the RP2040 UF2 bootloader without pressing BOOTSEL.
 * --------------------------------------------------------------- */
#define BOOTMAGIC_LITE_ROW    0
#define BOOTMAGIC_LITE_COLUMN 0
