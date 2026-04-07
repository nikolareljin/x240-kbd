# Repository Guidelines

This repository converts a ThinkPad X240 keyboard assembly and ClickPad into a
standalone USB HID keyboard and pointing device using a Raspberry Pi Pico
(RP2040), QMK firmware, and a 3D-printed OpenSCAD enclosure.

## Project Structure

- `firmware/qmk/keyboards/x240_pico/`: QMK keyboard definition, RP2040 config,
  default keymap, and build flags.
- `hardware/pinout/`: FPC probing workflow and measured keyboard/touchpad pinout
  tables. Treat measured pinout data as the hardware source of truth.
- `hardware/wiring/`: active GPIO allocation and perfboard wiring reference.
- `tools/matrix_probe/`: CircuitPython tool for keyboard matrix discovery.
- `tools/ps2_sniffer/`: CircuitPython tool for ClickPad PS/2 CLK/DATA discovery.
- `cad/`: OpenSCAD sources for the bottom case, Pico mount, and FPC cable guide.
- `docs/`: durable maintainer documentation for project structure, design rules,
  code rules, and build/test workflow.
- `ASSEMBLY.md`, `BOM.md`, `PLAN.md`: builder-facing assembly, parts, and project
  planning references.

## Build And Test

- Do not finalize wiring or keymap changes until FPC probing results are captured
  in `hardware/pinout/`.
- Build firmware by copying `firmware/qmk/keyboards/x240_pico/` into a QMK
  checkout, then running `qmk compile -kb x240_pico -km default`.
- Flash with `qmk flash -kb x240_pico -km default` or copy the generated UF2 to
  the Pico bootloader drive.
- For CircuitPython probe tools, copy the selected script to the Pico as
  `code.py` and use a 115200 baud serial terminal.
- Validate every key, NKRO, FN layer behavior, ClickPad movement/clicks,
  backlight control, power-button long-press behavior, and driverless USB HID
  enumeration before final assembly.

## Coding Style

- QMK C: follow upstream QMK conventions; keep feature flags in `rules.mk`,
  hardware constants in `config.h`, layout metadata in `keyboard.json`, and
  user behavior in `keymaps/default/keymap.c`.
- CircuitPython: keep probe scripts standalone, explicit about GPIO assumptions,
  and dependency-free beyond CircuitPython built-ins used in the script.
- OpenSCAD: keep CAD parametric, documented in millimeters, and regenerate mesh
  exports from source instead of committing generated STL/3MF/AMF files.
- Markdown: use relative links, clear hardware assumptions, and update docs when
  wiring, pinout, feature behavior, or build workflow changes.

## Repository Hygiene

- Keep `CLAUDE.md` files local-only memory files. Do not commit root or nested
  `CLAUDE.md` files.
- Do not commit generated firmware artifacts such as `.uf2`, `.hex`, `.bin`,
  `.elf`, maps, or QMK `.build/` output.
- Do not commit generated CAD meshes by default; keep exports under
  `cad/exports/` when needed locally.
- Never commit secrets, local environment files, tokens, private keys, or
  hardware capture logs.
- Update `CHANGELOG.md` for notable user-facing or project-structure changes.
