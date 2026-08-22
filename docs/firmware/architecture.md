---
title: Architecture
parent: Firmware
nav_order: 1
---

# Firmware architecture

QMK keyboard definition under `firmware/qmk/keyboards/x240_pico/`, built by copying it
into a QMK checkout. Files marked **new** are created in milestone M4; the rest exist today
and are corrected there.

| File | Owns | Status |
|---|---|---|
| `keyboard.json` | USB IDs, `processor`/`bootloader`, feature flags, the `ps2` block, layout metadata. `matrix_pins` is **removed** — the custom matrix owns pins. | exists, corrected in M4 |
| `config.h` | Sense-chain pins (`SENSE_PL_PIN`, `SENSE_CP_PIN`, `SENSE_Q7_PIN`), drive-line list, SPI settings, debounce, backlight, power button, LED, Synaptics tuning constants | exists, corrected in M4 |
| `rules.mk` | `CUSTOM_MATRIX = lite`, `POINTING_DEVICE_DRIVER = custom`, `PS2_ENABLE = yes` + `PS2_DRIVER = vendor`, `PS2_MOUSE_ENABLE = no`, `BACKLIGHT_DRIVER = software`, `SRC += matrix.c synaptics.c trackpoint.c` | corrected in M4 |
| `halconf.h` / `mcuconf.h` | `HAL_USE_SPI`, `RP_SPI_USE_SPI0` — ChibiOS needs SPI0 switched on for the sense chain | **new** |
| `matrix.c` | Drive-line sequencing and the 74HC165 chain read | **new** |
| `synaptics.c` / `.h` | The custom pointing-device driver: ClickPad reset/identify/capabilities, mode byte, guest enable, 6-byte packet parser with resync, touchpad delta, logged relative-mode fallback | **new** |
| `trackpoint.c` / `.h` | Guest (pass-through) frame decode, TrackPoint delta and scaling | **new** |
| `x240_pico.c` | `keyboard_post_init_kb` (LED on, power-button pull-up), `matrix_scan_kb` (power-button long-press guard), `pointing_device_task_kb` (merges the two pointing sources) | exists |
| `x240_pico.h` | `LAYOUT` macro, custom keycodes `CK_BKLT`/`CK_FNLK`, layer enum | exists; `LAYOUT` regenerated from the measured matrix |
| `keymaps/default/keymap.c` | `_BASE` and `_FN` layers, `process_record_user` | exists; regenerated from the measured matrix |

![Signal flow](../images/signal_flow.svg)

## From a key press to a USB report

```
GP0..GP9 drive line LOW
   → membrane closes a sense line to it
      → 74HC165 latches 24 sense bits (PL)
         → SPI0 clocks them into GP16          matrix.c : matrix_scan_custom()
            → raw row bitmap
               → QMK debounce (DEBOUNCE 5 ms)   quantum/
                  → keymap lookup, layers        keymap.c
                     → NKRO / boot keyboard report over USB (TinyUSB)
```

## From the ClickPad to a USB mouse report

```
ClickPad + TrackPoint guest  ──PS/2──►  GP21 DATA / GP22 CLK
   → QMK vendor PS/2 driver (RP2040 PIO0)         platforms/chibios/drivers/vendor/RP/RP2040/ps2_vendor.c
      → pbuf_has_data() / ps2_host_recv() bytes
         → synaptics.c (custom pointing driver) assembles 6-byte packets
            ├─ W != 3 : touchpad frame  → finger delta, L/R from byte 0    synaptics.c
            └─ W == 3 : guest frame     → TrackPoint 3-byte packet          trackpoint.c
               → pointing_device_task_kb() merges into one report_mouse_t   x240_pico.c
                  → USB HID mouse report
```

If the Synaptics identify fails, `synaptics.c` falls back to plain relative mode and logs
once via `dprintf` — the touchpad still works, the TrackPoint does not, and the log says so.
Never a silent success.

## Hooks used and why

| Hook | Used for | Not used for |
|---|---|---|
| `matrix_init_custom` / `matrix_scan_custom` | the chain | anything else — keep the scan loop minimal |
| `keyboard_post_init_kb` | LED and power-button GPIO setup | keymap logic |
| `pointing_device_driver_init` | Synaptics init; failures logged on the console | matrix |
| `matrix_scan_kb` | power-button timing only | side effects on the matrix |
| `pointing_device_task_kb` | merging touchpad + TrackPoint, axis inversion | raw PS/2 reads |
| `process_record_user` | `CK_BKLT`, `CK_FNLK` | hardware polling |

## Build

```bash
cp -r firmware/qmk/keyboards/x240_pico ~/qmk_firmware/keyboards/x240_pico
qmk compile -kb x240_pico -km default
qmk flash   -kb x240_pico -km default     # hold BOOTSEL, or Bootmagic top-left key
```

Local build without installing a toolchain: the `qmkfm/qmk_cli` docker image plus a
`qmk_firmware` checkout, with this directory mounted at `keyboards/x240_pico`. The
placeholder `LAYOUT` still describes the old 8 × 13 arrangement inside the 10 × 24 matrix;
issue #38 regenerates it from the measured pinout.
