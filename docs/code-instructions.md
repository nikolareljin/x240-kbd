# Code Instructions

This project contains QMK C firmware, CircuitPython probing tools, OpenSCAD CAD,
and Markdown documentation. Keep each area simple and hardware-verifiable.

## QMK C

- Follow QMK conventions and keep code compatible with upstream QMK.
- Keep keyboard-wide constants in `config.h` when QMK expects preprocessor
  defines.
- Keep feature selection in `rules.mk`.
- Keep layout metadata in `keyboard.json` synchronized with `x240_pico.h`.
- Keep user-facing behavior in `keymaps/default/keymap.c`, including base layer,
  FN layer, and custom keycodes.
- Keep keyboard-level hardware behavior in `x240_pico.c`, including dedicated
  GPIO polling for the GP27 power button.
- Use `KC_NO` for unused physical matrix positions and `KC_TRNS` for FN-layer
  pass-through entries.
- Prefer small custom keycode handlers in `process_record_user()` over broad
  side effects in scan hooks.
- Recompile after changing matrix dimensions, GPIO pins, QMK feature flags, or
  layout macros.

## CircuitPython Tools

- Keep `tools/matrix_probe/matrix_probe.py` and
  `tools/ps2_sniffer/ps2_sniffer.py` standalone.
- Avoid host-side Python dependencies. These scripts run on the Pico.
- Make all physical pin assumptions explicit in top-level constants.
- Print results in a format that can be copied directly into the pinout docs.
- Deinitialize GPIO objects after each probing pass to avoid stale pin state.
- Never let a probe script drive candidate power or ground pins as normal GPIO
  after they have been identified.

## OpenSCAD

- Keep source files parametric and document measurement variables near the top.
- Keep mechanical dimensions in millimeters.
- Avoid committing generated mesh outputs; regenerate them from `.scad` files.
- Keep cable guides and cutouts conservative until test-fit against real hardware.

## Markdown

- Use concise headings and tables for hardware references.
- Prefer relative links for repository files.
- Mark assumptions clearly, especially unverified pinouts and placeholder
  keymaps.
- Keep builder-facing steps in `ASSEMBLY.md` and maintenance guidance in `docs/`.

## Review Checklist

- Does the change match measured hardware data?
- Are README, CHANGELOG, wiring, and pinout docs updated when relevant?
- Are generated files ignored or intentionally excluded from the commit?
- Can the firmware still build after copying `firmware/qmk/keyboards/x240_pico/`
  into a QMK checkout?
- Does the change avoid adding network-dependent unit tests or tools?
