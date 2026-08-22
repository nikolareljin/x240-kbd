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
| `rules.mk` | `CUSTOM_MATRIX = lite`, `PS2_DRIVER = vendor`, `BACKLIGHT_DRIVER = software`, `SRC += matrix.c synaptics.c trackpoint.c` | exists, corrected in M4 |
| `matrix.c` | Drive-line sequencing and the 74HC165 chain read | **new** |
| `synaptics.c` / `.h` | ClickPad identify, mode byte, 6-byte packet parser, touchpad delta | **new** |
| `trackpoint.c` / `.h` | Guest (pass-through) frame decode, TrackPoint delta and scaling | **new** |
| `x240_pico.c` | `keyboard_post_init_kb` (LED on, power-button pull-up), `matrix_scan_kb` (power-button long-press guard), `pointing_device_task_kb` (merges the two pointing sources) | exists |
| `x240_pico.h` | `LAYOUT` macro, custom keycodes `CK_BKLT`/`CK_FNLK`, layer enum | exists; `LAYOUT` regenerated from the measured matrix |
| `keymaps/default/keymap.c` | `_BASE` and `_FN` layers, `process_record_user` | exists; regenerated from the measured matrix |

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
      → ps2_host_recv() bytes
         → synaptics.c assembles 6-byte packets
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
| `keyboard_post_init_kb` | GPIO setup, Synaptics init (after USB is up, so failures can be logged) | keymap logic |
| `matrix_scan_kb` | power-button timing only | side effects on the matrix |
| `pointing_device_task_kb` | merging touchpad + TrackPoint, axis inversion | raw PS/2 reads |
| `process_record_user` | `CK_BKLT`, `CK_FNLK` | hardware polling |

## Build

```bash
cp -r firmware/qmk/keyboards/x240_pico ~/qmk_firmware/keyboards/x240_pico
qmk compile -kb x240_pico -km default
qmk flash   -kb x240_pico -km default     # hold BOOTSEL, or Bootmagic top-left key
```

Until M4 lands, the definition **does not compile** — `PS2_DRIVER = usart` is not valid on
RP2040 and the `matrix_pins` block conflicts with the intended custom matrix. That is
expected and tracked; do not "fix" it by reverting to the 8 × 13 placeholder.
