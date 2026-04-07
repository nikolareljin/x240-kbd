#include "x240_pico.h"
#include "quantum.h"

static bool power_button_pressed = false;
static uint16_t power_button_timer = 0;

/* ---------------------------------------------------------------------------
 * Hardware initialization
 *
 * The X240 ClickPad has a small indicator LED. We light it whenever the
 * pointing device is active (i.e., at startup and always-on during use).
 * To disable the touchpad temporarily, a user-defined keycode could call
 * pointing_device_set_status() and toggle the LED here.
 *
 * The X240 power button is wired as a dedicated active-LOW GPIO on GP27. It is
 * not part of the keyboard matrix, so matrix_scan_kb() polls it separately.
 * --------------------------------------------------------------------------- */
void keyboard_post_init_kb(void) {
    gpio_set_pin_output(TOUCHPAD_LED_PIN);
    gpio_write_pin_high(TOUCHPAD_LED_PIN);   /* LED on = touchpad active */

    gpio_set_pin_input_high(POWER_BUTTON_PIN);

    keyboard_post_init_user();
}

/* ---------------------------------------------------------------------------
 * Dedicated power button handling
 *
 * A short press is ignored to prevent accidental suspend/power-off. A release
 * after POWER_BUTTON_HOLD_MS sends a standard System Power HID event.
 * --------------------------------------------------------------------------- */
void matrix_scan_kb(void) {
    bool pressed = !gpio_read_pin(POWER_BUTTON_PIN);

    if (pressed && !power_button_pressed) {
        power_button_pressed = true;
        power_button_timer = timer_read();
    } else if (!pressed && power_button_pressed) {
        power_button_pressed = false;
        if (timer_elapsed(power_button_timer) >= POWER_BUTTON_HOLD_MS) {
            tap_code(KC_SYSTEM_POWER);
        }
    }

    matrix_scan_user();
}

/* ---------------------------------------------------------------------------
 * Pointing device callback — called after each PS/2 report is assembled.
 * Use this to apply any per-axis inversion or dead-zone filtering.
 * --------------------------------------------------------------------------- */
report_mouse_t pointing_device_task_kb(report_mouse_t mouse_report) {
    /* Uncomment the line below if the Y axis is inverted on your touchpad:
     * mouse_report.y = -mouse_report.y;
     */
    return pointing_device_task_user(mouse_report);
}
