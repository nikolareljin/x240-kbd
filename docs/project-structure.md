---
title: Project structure
nav_exclude: true
---

# Project structure

`x240-kbd` converts a ThinkPad X240 keyboard assembly (with TrackPoint) and ClickPad into a
standalone USB HID device driven by a Raspberry Pi Pico running QMK.

## Top level

| Path | Purpose |
|---|---|
| `README.md` | Builder entry point, status, features, honest cost, quick start |
| `PLAN.md` | The living plan: corrected design and the milestone sequence |
| `ASSEMBLY.md` | Step-by-step Rev A build |
| `BOM.md` | Pointer to the priced BOM in `docs/hardware/bom-and-cost.md` |
| `CHANGELOG.md` | Notable changes, including every design correction with its reason |
| `AGENTS.md` | Repository guidelines for agents and contributors |
| `LICENSE` | GPL-2.0 |

## `firmware/qmk/keyboards/x240_pico/`

Copied into a QMK checkout to build. `keyboard.json` (USB IDs, `ps2` block, layout
metadata), `config.h` (pins, timing, tuning), `rules.mk` (features, drivers, extra sources),
`x240_pico.c/.h` (keyboard-level hooks, LAYOUT), `keymaps/default/keymap.c`. Milestone M4
adds `matrix.c`, `synaptics.c/.h`, `trackpoint.c/.h`. Until then the definition does not
build — see `docs/firmware/architecture.md`.

## `hardware/`

- `pinout/` — probing procedure and the measured pinout tables. **Hardware source of truth.**
- `wiring/wiring_diagram.md` — **the single authoritative GPIO table** plus schematics.
- `pcb/` — Rev B KiCad project (milestone M7).

## `tools/`

CircuitPython scripts run on the Pico as `code.py`: `matrix_probe/`, `ps2_sniffer/`, and
(M2) `shift_register_test/`. Standalone; no host-side dependencies.

## `cad/`

OpenSCAD sources: `params.scad` (shared measured dimensions, M5), the split `bottom_case`,
`pico_mount_bracket`, `fpc_cable_guide`, `perfboard_sled`, `usb_strain_relief`,
`tilt_feet`, `zif_support_block`, `led_light_pipe`, `export_plates` (DXF for laser cutting,
M6). Meshes go to `cad/exports/` and are not committed.

## `docs/`

The documentation site source. `hardware/`, `firmware/`, `enclosure/` each have an
`index.md` parent page; `references.md`, `glossary.md`; `images/`. Maintainer pages
(`project-structure`, `design-instructions`, `code-instructions`, `build-and-test`) carry
`nav_exclude: true` and are excluded from the site.

Where new work goes: a measured fact → `hardware/pinout/`; a wiring change →
`hardware/wiring/` first, then the docs that cite it; a design decision → the relevant
`docs/` page plus `CHANGELOG.md`; anything with a state → a GitHub issue, not a doc.
