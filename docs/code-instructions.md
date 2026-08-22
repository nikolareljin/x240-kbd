---
title: Code instructions
nav_exclude: true
---

# Code instructions

QMK C, CircuitPython tools, OpenSCAD and Markdown. Keep each hardware-verifiable.

## QMK C

- Upstream QMK conventions; build must succeed after copying the keyboard directory into a
  QMK checkout (`qmk compile -kb x240_pico -km default`).
- `rules.mk` selects features and lists extra sources; `config.h` holds pins and constants;
  `keyboard.json` holds USB/layout metadata and the `ps2` block — **no `matrix_pins`** with
  the custom matrix.
- `matrix.c` does only the chain scan. `synaptics.c` owns the PS/2 conversation.
  `trackpoint.c` owns guest frames. `x240_pico.c` merges and polls. Keep these boundaries.
- `process_record_user()` for custom keycodes; no side effects in scan hooks beyond the
  power-button timer.
- `KC_NO` for empty matrix cells, `KC_TRNS` for FN pass-through.
- Log every fallback path with `dprintf`; a degraded mode that says nothing is a bug.

## CircuitPython tools

- Standalone, built-in modules only; run as `code.py` at 115200 baud.
- Every physical pin assumption is a top-level constant.
- Output is a Markdown table that pastes into the pinout files unchanged.
- Deinitialise GPIO between passes; never drive an identified power or ground pin.
- The sniffer's Synaptics mode must print an unambiguous verdict on pass-through frames.

## OpenSCAD

- All dimensions from `cad/params.scad`, in millimetres, commented with what was measured.
- Parts select their variant by parameter (`half = "left"`), never by copied files.
- `export_plates.scad` derives laser-cut outlines from the same solids via `projection()`.
- No committed meshes.

## Markdown

- Relative links inside the repo; absolute links to datasheets and products.
- Front matter (`title`, `parent`, `nav_order`) on every `docs/` page; `nav_exclude: true`
  on maintainer pages.
- Mark unverified things as unverified. Tables for hardware facts.

## Review checklist

- Does the change match measured data, or say it is waiting for it?
- Is the GPIO table still stated once, in `hardware/wiring/wiring_diagram.md`?
- Is every new part in `components.md` and priced in `bom-and-cost.md`?
- Is a corrected claim recorded in `CHANGELOG.md` with its source?
- Do all relative links resolve and all URLs return 2xx?
- Are generated artifacts ignored?
- Would the firmware still build after the change (or is the build break tracked)?
