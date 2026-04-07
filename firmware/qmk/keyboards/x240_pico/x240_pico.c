#include "x240_pico.h"
#include "quantum.h"

/* ---------------------------------------------------------------------------
 * Touchpad LED
 *
 * The X240 ClickPad has a small indicator LED. We light it whenever the
 * pointing device is active (i.e., at startup and always-on during use).
 * To disable the touchpad temporarily, a user-defined keycode could call
 * pointing_device_set_status() and toggle the LED here.
 * --------------------------------------------------------------------------- */
void keyboard_post_init_kb(void) {
    setPinOutput(TOUCHPAD_LED_PIN);
    writePinHigh(TOUCHPAD_LED_PIN);   /* LED on = touchpad active */
    keyboard_post_init_user();
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
