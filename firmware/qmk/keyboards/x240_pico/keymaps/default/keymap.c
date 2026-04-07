#include QMK_KEYBOARD_H

/*
 * =========================================================================
 * IMPORTANT — fill the LAYOUT() macros below AFTER completing Phase 1 FPC
 * probing. Each position in LAYOUT() corresponds to a matrix cell (row, col).
 * Use KC_NO for any matrix position that has no physical key.
 *
 * The placeholder layout below represents a generic 84-key ThinkPad X240
 * row/column arrangement. Replace KC_TRNS / keycodes with the actual map
 * derived from your probing session.
 * =========================================================================
 *
 * Row 0:  Esc  F1   F2   F3   F4   F5   F6   F7   F8   F9   F10  F11  F12
 * Row 1:  `    1    2    3    4    5    6    7    8    9    0    -    =
 * Row 2:  Tab  Q    W    E    R    T    Y    U    I    O    P    [    ]
 * Row 3:  Caps A    S    D    F    G    H    J    K    L    ;    '    Bsp
 * Row 4:  LSft Z    X    C    V    B    N    M    ,    .    /    RSft PgUp
 * Row 5:  LCtl Win  LAlt          Spc            RAlt Menu RCtl PgDn Ins
 * Row 6:  Del  Home End  Up   Left Down Right    PrtS ScrL Paus \    Ent
 * Row 7:  FN   (power button handled separately via POWER_BUTTON_PIN)
 */

/* Layer definitions */
enum x240_layers {
    _BASE = 0,
    _FN,
};

/* Custom keycodes */
enum x240_keycodes {
    CK_BKLT = SAFE_RANGE,  /* Toggle backlight */
    CK_FNLK,               /* FN Lock toggle   */
    CK_PWR,                /* Power button     */
};

/* Power button long-press tracking */
static uint16_t power_press_timer = 0;

/* -------------------------------------------------------------------------
 * BASE layer — standard X240 QWERTY
 *
 * NOTE: This is a skeleton. Replace KC_NO with actual keycodes once you have
 * confirmed the matrix position of every physical key via probing.
 * ------------------------------------------------------------------------- */
const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {

[_BASE] = LAYOUT(
    /* Row 0 */
    KC_ESC,  KC_F1,   KC_F2,   KC_F3,   KC_F4,   KC_F5,   KC_F6,   KC_F7,   KC_F8,   KC_F9,   KC_F10,  KC_F11,  KC_F12,
    /* Row 1 */
    KC_GRV,  KC_1,    KC_2,    KC_3,    KC_4,    KC_5,    KC_6,    KC_7,    KC_8,    KC_9,    KC_0,    KC_MINS, KC_EQL,
    /* Row 2 */
    KC_TAB,  KC_Q,    KC_W,    KC_E,    KC_R,    KC_T,    KC_Y,    KC_U,    KC_I,    KC_O,    KC_P,    KC_LBRC, KC_RBRC,
    /* Row 3 */
    KC_CAPS, KC_A,    KC_S,    KC_D,    KC_F,    KC_G,    KC_H,    KC_J,    KC_K,    KC_L,    KC_SCLN, KC_QUOT, KC_BSPC,
    /* Row 4 */
    KC_LSFT, KC_Z,    KC_X,    KC_C,    KC_V,    KC_B,    KC_N,    KC_M,    KC_COMM, KC_DOT,  KC_SLSH, KC_RSFT, KC_PGUP,
    /* Row 5 */
    KC_LCTL, KC_LGUI, KC_LALT, KC_NO,   KC_NO,   KC_SPC,  KC_NO,   KC_NO,   KC_RALT, KC_APP,  KC_RCTL, KC_PGDN, KC_INS,
    /* Row 6 */
    KC_DEL,  KC_HOME, KC_END,  KC_UP,   KC_LEFT, KC_DOWN, KC_RGHT, KC_NO,   KC_PSCR, KC_SCRL, KC_PAUS, KC_BSLS, KC_ENT,
    /* Row 7 */
    MO(_FN), CK_PWR,  KC_NO,   KC_NO,   KC_NO,   KC_NO,   KC_NO,   KC_NO,   KC_NO,   KC_NO,   KC_NO,   KC_NO,   KC_NO
),

/* -------------------------------------------------------------------------
 * FN layer — ThinkPad media / system keys
 *
 * KC_TRNS = transparent (falls through to BASE layer)
 * Active keys replace the base keycode when FN is held.
 * ------------------------------------------------------------------------- */
[_FN] = LAYOUT(
    /* Row 0 — FN+Esc = FN Lock */
    CK_FNLK, KC_MUTE, KC_VOLD, KC_VOLU, KC_F20,  KC_BRID, KC_BRIU, KC_F7,   KC_F8,   KC_F9,   KC_F10,  CK_BKLT, KC_PSCR,
    /* Row 1 */
    KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS,
    /* Row 2 */
    KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS,
    /* Row 3 */
    KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS,
    /* Row 4 — FN+PgUp = Home, FN+PgDn = End */
    KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_HOME,
    /* Row 5 */
    KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_END,  KC_TRNS,
    /* Row 6 — FN+Left = Prev, FN+Right = Next */
    KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_MPRV, KC_TRNS, KC_MNXT, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS,
    /* Row 7 */
    KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS
),

};

/* -------------------------------------------------------------------------
 * Custom keycode handling
 * ------------------------------------------------------------------------- */
bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    switch (keycode) {

        case CK_BKLT:
            if (record->event.pressed) {
                backlight_step();
            }
            return false;

        case CK_FNLK:
            if (record->event.pressed) {
                /* Toggle FN layer permanently on/off */
                layer_invert(_FN);
            }
            return false;

        case CK_PWR:
            if (record->event.pressed) {
                power_press_timer = timer_read();
            } else {
                if (timer_elapsed(power_press_timer) >= POWER_BUTTON_HOLD_MS) {
                    /* Long press: send system power event */
                    tap_code(KC_SYSTEM_POWER);
                }
                /* Short press: ignore — prevents accidental power-off */
            }
            return false;

        default:
            break;
    }
    return true;
}
