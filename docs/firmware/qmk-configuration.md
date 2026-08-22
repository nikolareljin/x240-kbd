---
title: QMK configuration
parent: Firmware
nav_order: 2
---

# QMK configuration reference

Every setting, what it does, where it is documented upstream, and — where the earlier plan
had it wrong — what changed and why.

## `rules.mk`

| Setting | Value | Upstream | Notes |
|---|---|---|---|
| `MCU` | `RP2040` | [RP2040 platform](https://docs.qmk.fm/platformdev_rp2040) | |
| `BOOTLOADER` | `rp2040` | same | UF2 drag-and-drop via BOOTSEL |
| `BOOTMAGIC_ENABLE` | `yes` | [Bootmagic](https://docs.qmk.fm/features/bootmagic) | Hold top-left key at plug-in → bootloader |
| `EXTRAKEY_ENABLE` | `yes` | [Keycodes](https://docs.qmk.fm/keycodes) | Media and system keys (`KC_SYSTEM_POWER`) |
| `MOUSEKEY_ENABLE` | `yes` | [Mouse keys](https://docs.qmk.fm/features/mouse_keys) | Optional; the pointing device does not need it |
| `NKRO_ENABLE` | `yes` | [NKRO](https://docs.qmk.fm/keycodes_magic) | With `FORCE_NKRO` in `config.h` |
| `CUSTOM_MATRIX` | `lite` | [Custom matrix](https://docs.qmk.fm/custom_matrix) | **Changed** — the 74HC165 chain needs `matrix_scan_custom()` |
| `SRC` | `+= matrix.c synaptics.c trackpoint.c` | | **Changed** — new sources |
| `POINTING_DEVICE_ENABLE` | `yes` | [Pointing device](https://docs.qmk.fm/features/pointing_device) | |
| `POINTING_DEVICE_DRIVER` | `ps2` | same | |
| `PS2_MOUSE_ENABLE` | `yes` | [PS/2 mouse](https://docs.qmk.fm/features/ps2_mouse) | |
| `PS2_ENABLE` | `yes` | same | |
| `PS2_DRIVER` | `vendor` | same | **Changed from `usart`** — see below |
| `BACKLIGHT_ENABLE` | `yes` (backlit keyboards only) | [Backlight](https://docs.qmk.fm/features/backlight) | |
| `BACKLIGHT_DRIVER` | `software` | same | **Changed from `timer`** — see below |
| `LTO_ENABLE` | `yes` | | Smaller binary |
| `CONSOLE_ENABLE` | `yes` during bring-up, `no` for release | [Debugging](https://docs.qmk.fm/faq_debug) | Needed to see the Synaptics fallback log |

### Why `PS2_DRIVER = vendor`

QMK's PS/2 page lists four drivers: `busywait` (any MCU, jerky), `interrupt` (AVR + ARM
ChibiOS), `usart` (**ATmega32u4 only**, fixed to PD5/PD2), and `vendor` — which on RP2040
is the **PIO implementation**. The earlier plan chose `usart` on the belief that it mapped
to an RP2040 UART. It does not; the build fails. The PIO driver is the intended RP2040 path.

The PIO driver has one hard rule: **the clock GPIO must be the data GPIO + 1.**
Hence DATA = GP21, CLK = GP22. The earlier `config.h` had them the other way round.

Optional: `#define PS2_PIO_USE_PIO1` moves the state machine to PIO1. Reserved for the
second-instance TrackPoint fallback.

### Why `BACKLIGHT_DRIVER = software`

`pwm` does not compile on RP2040 ([QMK #24470](https://github.com/qmk/qmk_firmware/issues/24470)).
`timer` is documented for AVR and STM32. `software` is the workaround the issue itself
records and is what we use. Detail in [`../hardware/backlight.md`](../hardware/backlight.md).

## `keyboard.json`

```json
{
  "keyboard_name": "X240 Pico",
  "manufacturer": "Custom",
  "url": "https://github.com/nikolareljin/x240-kbd",
  "maintainer": "nikolareljin",
  "usb": { "vid": "0x6E6B", "pid": "0x0240", "device_version": "0.2.0" },
  "processor": "RP2040",
  "bootloader": "rp2040",
  "features": { "bootmagic": true, "extrakey": true, "mousekey": true, "nkro": true },
  "ps2": {
    "enabled": true,
    "mouse_enabled": true,
    "driver": "vendor",
    "data_pin": "GP21",
    "clock_pin": "GP22"
  },
  "diode_direction": "COL2ROW",
  "matrix_size": { "rows": 10, "cols": 24 },
  "layouts": { "LAYOUT": { "layout": [ "...generated from the measured matrix..." ] } }
}
```

- **No `matrix_pins`.** With `CUSTOM_MATRIX = lite` the pins live in `config.h` and
  `matrix.c`. Leaving `matrix_pins` in causes QMK to also generate the default scanner.
- `matrix_size` is the chain's capacity (10 drive × 24 sense) until probing sets the real
  numbers; unused cells are `KC_NO`.
- `vid`/`pid` are placeholders in a vendor-less range; do not ship them in a product that
  could collide — see the [QMK VID/PID guidance](https://docs.qmk.fm/hardware_keyboard_guidelines).

## `config.h`

| Define | Value | Purpose |
|---|---|---|
| `DEBOUNCE` | `5` | ms, QMK default algorithm |
| `MATRIX_IO_DELAY` | `30` | µs settle after driving a line LOW, before `PL` |
| `MATRIX_DRIVE_PINS` | `{ GP0, …, GP9 }` | drive lines, consumed by `matrix.c` |
| `SENSE_PL_PIN` / `SENSE_CP_PIN` / `SENSE_Q7_PIN` | `GP17` / `GP18` / `GP16` | chain control; CP/Q7 are SPI0 SCK/RX |
| `SENSE_CHAIN_BITS` | `24` | 3 × 74HC165 |
| `SPI_SCK_PIN` / `SPI_MISO_PIN` | `GP18` / `GP16` | QMK SPI master config for the chain |
| `PS2_MOUSE_X_MULTIPLIER` / `_Y_` | `3` | only used in the relative-mode fallback |
| `SYN_TOUCHPAD_SCALE` / `SYN_TRACKPOINT_SCALE` | tuned in M4 | independent sensitivity for the two sources |
| `BACKLIGHT_PIN` | `GP26` | |
| `BACKLIGHT_LEVELS` | `5` | |
| `BACKLIGHT_BREATHING` | defined | |
| `BREATHING_PERIOD` | `6` | seconds — note the upstream name is `BREATHING_PERIOD`, not `BACKLIGHT_BREATHING_PERIOD` |
| `POWER_BUTTON_PIN` | `GP27` | active LOW, internal pull-up |
| `POWER_BUTTON_HOLD_MS` | `500` | long-press guard |
| `TOUCHPAD_LED_PIN` | `GP28` | HIGH = on |
| `FORCE_NKRO` | defined | |
| `BOOTMAGIC_ROW` / `BOOTMAGIC_COLUMN` | `0` / `0` | top-left key; note the current upstream names drop the `_LITE` |

**Removed:** the comment claiming GP21/GP22 are "UART0 CTS/TX / RX". On the RP2040, UART0
is on GP0/1, GP12/13 or GP16/17 and UART1 on GP4/5, GP8/9 or GP20/21. GP21/GP22 is not a
UART pair and the PIO driver does not use one anyway.

## Custom keycodes

| Keycode | Action |
|---|---|
| `CK_BKLT` | `backlight_step()` — FN + F11 |
| `CK_FNLK` | `layer_invert(_FN)` — FN + Esc, FN Lock |

The power button is **not** a keycode; `matrix_scan_kb()` polls GP27 and sends
`KC_SYSTEM_POWER` after a ≥ 500 ms hold.
