# Project Structure

`x240-kbd` converts a ThinkPad X240 keyboard assembly and ClickPad into a
standalone USB HID device driven by a Raspberry Pi Pico running QMK.

## Top-Level Files

| Path | Purpose |
|---|---|
| `README.md` | Builder entry point, feature summary, quick start, and links. |
| `CHANGELOG.md` | Notable changes by release or unreleased work. |
| `PLAN.md` | Original project plan, assumptions, and phase breakdown. |
| `ASSEMBLY.md` | Step-by-step build instructions. |
| `BOM.md` | Parts list, approximate cost, and required tools. |
| `LICENSE` | Project license. |
| `.gitignore` | Generated, local-only, and build artifact exclusions. |

## Firmware

`firmware/qmk/keyboards/x240_pico/` is a QMK keyboard definition that is copied
into a QMK checkout when building.

| Path | Purpose |
|---|---|
| `keyboard.json` | USB metadata, RP2040 platform, matrix pins, diode direction, and layout metadata. |
| `config.h` | Debounce, PS/2 pins, backlight, power button, NKRO, and Bootmagic settings. |
| `rules.mk` | QMK feature flags and RP2040 build configuration. |
| `x240_pico.c` | Keyboard-level hooks and hardware initialization point. |
| `x240_pico.h` | Layout macro and shared declarations. |
| `keymaps/default/keymap.c` | Base and FN layers plus custom keycode behavior. |

The current firmware assumes an 8 row by 13 column matrix. Treat that as a
working assumption until Phase 1 probing confirms the actual FPC mapping.

## Hardware

`hardware/pinout/` contains the measurement workflow and the tables that must be
filled from real probing results before final wiring.

`hardware/wiring/` contains the active GPIO allocation and perfboard circuit
guidance. Update it whenever GPIO assignments, pull-ups, MOSFET circuits, or LED
drive behavior changes.

## Tools

`tools/matrix_probe/matrix_probe.py` is a CircuitPython probe for discovering
keyboard matrix row and column pairs on the 40-pin keyboard FPC.

`tools/ps2_sniffer/ps2_sniffer.py` is a CircuitPython PS/2 monitor for testing
candidate ClickPad CLK/DATA pin pairs.

Both tools are meant to be copied to a CircuitPython Pico as `code.py`. Keep them
standalone and avoid dependencies outside the CircuitPython standard modules they
already import.

## CAD

`cad/` stores OpenSCAD source for the bottom case, Pico mounting bracket, and FPC
cable guide. Generated mesh exports belong under `cad/exports/` and are ignored
because they should be regenerated from `.scad` source.

## Documentation

`docs/` stores project-maintenance guidance. It should not duplicate every detail
from `ASSEMBLY.md`; instead, it should explain where information lives, what
rules to follow, and how to safely change the design.
