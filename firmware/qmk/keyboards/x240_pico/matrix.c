/*
 * matrix.c — custom matrix scan for the X240 Pico keyboard
 *
 * Drive side : MATRIX_DRIVE_PINS, pulled LOW one at a time (others high-Z with pull-up).
 * Sense side : three cascaded 74HC165 shift registers read over SPI0.
 *              SENSE_PL_PIN latches all inputs; SPI clocks 24 bits out of U1.Q7.
 *
 * Bit order on the wire: the first bit clocked out is U1.D7 (sense line S7); so
 * byte 0 holds S7..S0 (MSB..LSB), byte 1 holds S15..S8, byte 2 holds S23..S16.
 * Sense line index = byte * 8 + bit — the same mapping the probing tools use.
 *
 * A pressed key pulls its sense line LOW through the drive line, so a 0 bit = pressed.
 */
#include "quantum.h"
#include "spi_master.h"

#ifndef SENSE_CHAIN_BYTES
#    define SENSE_CHAIN_BYTES 3
#endif
#ifndef SENSE_SPI_DIVISOR
#    define SENSE_SPI_DIVISOR 16
#endif

_Static_assert(MATRIX_COLS == SENSE_CHAIN_BYTES * 8, "MATRIX_COLS must equal 8 x SENSE_CHAIN_BYTES");

static const pin_t drive_pins[MATRIX_ROWS] = MATRIX_DRIVE_PINS;

static inline void drive_release(pin_t pin) {
    gpio_set_pin_input_high(pin);
}

static inline void drive_assert(pin_t pin) {
    gpio_set_pin_output(pin);
    gpio_write_pin_low(pin);
}

static inline void sense_latch(void) {
    /* 74HC165 PL: LOW loads D0..D7 into the register (min pulse ~25 ns at 3.3 V). */
    gpio_write_pin_low(SENSE_PL_PIN);
    wait_us(1);
    gpio_write_pin_high(SENSE_PL_PIN);
}

static matrix_row_t sense_read(void) {
    uint8_t raw[SENSE_CHAIN_BYTES] = {0};
    sense_latch();
    spi_receive(raw, SENSE_CHAIN_BYTES);
    matrix_row_t bits = 0;
    for (uint8_t i = 0; i < SENSE_CHAIN_BYTES; i++) {
        bits |= (matrix_row_t)raw[i] << (8 * i);
    }
    return bits;
}

void matrix_init_custom(void) {
    for (uint8_t r = 0; r < MATRIX_ROWS; r++) {
        drive_release(drive_pins[r]);
    }
    gpio_set_pin_output(SENSE_PL_PIN);
    gpio_write_pin_high(SENSE_PL_PIN);
    spi_init();
}

bool matrix_scan_custom(matrix_row_t current_matrix[]) {
    bool changed = false;
    const matrix_row_t mask = (MATRIX_COLS >= 32) ? (matrix_row_t)~0 : (((matrix_row_t)1 << MATRIX_COLS) - 1);

    /* mode 0, MSB first, no slave select: the chain has no CS, PL is handled by hand */
    if (!spi_start(NO_PIN, false, 0, SENSE_SPI_DIVISOR)) {
        return false;
    }
    for (uint8_t r = 0; r < MATRIX_ROWS; r++) {
        drive_assert(drive_pins[r]);
        wait_us(MATRIX_IO_DELAY);
        matrix_row_t row = (~sense_read()) & mask;   /* LOW = pressed */
        drive_release(drive_pins[r]);
        if (current_matrix[r] != row) {
            current_matrix[r] = row;
            changed           = true;
        }
    }
    spi_stop();
    return changed;
}
