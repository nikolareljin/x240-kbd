# Repository Guidelines

This repository converts a ThinkPad X240 keyboard assembly and ClickPad into a
standalone USB HID keyboard and pointing device using a Raspberry Pi Pico
(RP2040), QMK firmware, and a 3D-printed OpenSCAD enclosure.

## Project Structure

- `firmware/qmk/keyboards/x240_pico/`: QMK keyboard definition, RP2040 config,
  default keymap, and build flags.
- `hardware/pinout/`: FPC probing workflow and measured keyboard/touchpad pinout
  tables. Treat measured pinout data as the hardware source of truth.
- `hardware/wiring/wiring_diagram.md`: **the single authoritative GPIO table** and
  schematics. Other documents link to it; never restate the table elsewhere.
- `hardware/pcb/`: Rev B KiCad project (milestone M7).
- `tools/matrix_probe/`: CircuitPython tool for keyboard matrix discovery.
- `tools/ps2_sniffer/`: CircuitPython tool for ClickPad PS/2 CLK/DATA discovery.
- `cad/`: OpenSCAD sources for the bottom case, Pico mount, and FPC cable guide.
- `docs/`: the documentation site (GitHub Pages from `/docs`): `hardware/`,
  `firmware/`, `enclosure/`, `references.md`, `glossary.md`, plus maintainer pages
  marked `nav_exclude: true`. Every part named anywhere must appear in
  `docs/hardware/components.md`; every cost in `docs/hardware/bom-and-cost.md`.
- `ASSEMBLY.md`, `BOM.md`, `PLAN.md`: builder-facing assembly, parts, and project
  planning references.

## Build And Test

- Do not finalize wiring or keymap changes until FPC probing results are captured
  in `hardware/pinout/`.
- Use `./dev` for everything: `install`, `build [firmware|docs|tools|all]`, `test`,
  `preflight`, `deploy [firmware|<tool>]`, `devices`, `logs`, `clean`, `update`.
  `scripts/cli.sh` is the script-helpers template — do not edit it; repo behaviour
  goes in `scripts/project.sh`. Toolchains run in Docker (`qmkfm/qmk_cli`,
  `jekyll/jekyll`); `QMK_HOME` points at an existing qmk_firmware checkout.
- `./dev preflight` must be green before a PR: it is exactly what CI runs
  (`.github/workflows/ci.yml` → ci-helpers `ci.yml@production`).
- Probe tools: `./probe <tool>` copies it to `CIRCUITPY` as `code.py`; serial at
  115200 baud. Keep hardware imports guarded so `tools/tests/` runs on the host.
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
- Update `CHANGELOG.md` for notable user-facing or project-structure changes, and for
  every correction of a previously published claim, with its source.
- Work state lives in GitHub issues (milestones M0–M8), not in documents.
