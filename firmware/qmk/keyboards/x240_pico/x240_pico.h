#pragma once

#include "quantum.h"

/* Custom keycodes */
enum x240_keycodes {
    CK_BKLT = SAFE_RANGE,  /* Toggle keyboard backlight */
    CK_FNLK,               /* Toggle FN Lock (permanently invert FN layer) */
};

/* Layer indices */
enum x240_layers {
    _BASE = 0,
    _FN,
};

/*
 * LAYOUT macro — 8 rows × 13 cols = 104 positions.
 *
 * Fill this in after Phase 1 probing reveals the actual key → (row, col) map.
 * Empty/unused matrix positions should be KC_NO.
 *
 * The argument order here is: left-to-right, top-to-bottom across all rows.
 * Match it to the keyboard.json layout array order.
 */
#define LAYOUT( \
    k00, k01, k02, k03, k04, k05, k06, k07, k08, k09, k0A, k0B, k0C, \
    k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k1A, k1B, k1C, \
    k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k2A, k2B, k2C, \
    k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, k3A, k3B, k3C, \
    k40, k41, k42, k43, k44, k45, k46, k47, k48, k49, k4A, k4B, k4C, \
    k50, k51, k52, k53, k54, k55, k56, k57, k58, k59, k5A, k5B, k5C, \
    k60, k61, k62, k63, k64, k65, k66, k67, k68, k69, k6A, k6B, k6C, \
    k70, k71, k72, k73, k74, k75, k76, k77, k78, k79, k7A, k7B, k7C  \
) { \
    { k00, k01, k02, k03, k04, k05, k06, k07, k08, k09, k0A, k0B, k0C }, \
    { k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k1A, k1B, k1C }, \
    { k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k2A, k2B, k2C }, \
    { k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, k3A, k3B, k3C }, \
    { k40, k41, k42, k43, k44, k45, k46, k47, k48, k49, k4A, k4B, k4C }, \
    { k50, k51, k52, k53, k54, k55, k56, k57, k58, k59, k5A, k5B, k5C }, \
    { k60, k61, k62, k63, k64, k65, k66, k67, k68, k69, k6A, k6B, k6C }, \
    { k70, k71, k72, k73, k74, k75, k76, k77, k78, k79, k7A, k7B, k7C }, \
}
