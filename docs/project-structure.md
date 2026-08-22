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

## `./dev` and `scripts/`

`./dev` is the one entry point (`scripts/cli.sh`, copied from the script-helpers
`templates/dev-cli` and never edited here). Repo behaviour lives in `scripts/project.sh`:
build = `qmk compile` in the `qmkfm/qmk_cli` container against a `qmk_firmware` checkout
(`./dev install` clones one; `QMK_HOME` overrides), docs = Jekyll in Docker, test = pytest
+ `scripts/check_links.py` + shellcheck, deploy = copy to `RPI-RP2` / `CIRCUITPY`.
`scripts/script-helpers/` is the submodule (branch `production`). Shims: `./build`,
`./test`, `./flash`, `./probe`, `./site`. Output: `out/` (ignored).

**Toolchain pinning:** `scripts/toolchain.env` holds the five Docker images by digest
(`qmkfm/qmk_cli`, `jekyll/jekyll`, `openscad/openscad`, `kicad/kicad`,
`freerouting/freerouting`) and the exact `qmk_firmware` commit; `scripts/pull_toolchain.sh` pulls them (`--save`/`--load` for offline tarballs,
`--refresh` to re-resolve, `--verify` to print versions). `./dev install` and `./dev
update` go through it, so a build is repeatable later.

`docs/presentation/` holds the printable label (`label.svg`, 60 × 40 mm) and the A6
quick-start card.

`.github/workflows/ci.yml` calls ci-helpers' reusable `ci.yml@production` with
`./dev test` and `./dev install && ./dev build all`.

## `firmware/qmk/keyboards/x240_pico/`

Mounted into a QMK checkout to build. `keyboard.json` (USB IDs, `ps2` block, NKRO
default, Bootmagic key, layout metadata — QMK generates `LAYOUT` from it), `config.h`
(pins, SPI, tuning), `rules.mk` (custom matrix, custom pointing driver, software backlight),
`halconf.h`/`mcuconf.h` (SPI0 on), `matrix.c`, `synaptics.c/.h`, `trackpoint.c/.h`,
`x240_pico.c/.h`, `keymaps/default/keymap.c`. Builds; keymap is a placeholder until #38.

## `hardware/`

- `pinout/` — probing procedure and the measured pinout tables. **Hardware source of truth.**
- `wiring/wiring_diagram.md` — **the single authoritative GPIO table** plus schematics.
- `pcb/` — Rev B KiCad project, **generated**: `netlist_model.py` (parts, library names,
  nets) → `gen_schematic.py` (`.kicad_sch`, ERC) and `gen_pcb.py` (`.kicad_pcb`, placement,
  DRC); `route_pcb.py` round-trips a Specctra DSN/SES through freerouting. `./dev build pcb`
  runs the lot and exports PDF, gerbers, drill, position and BOM to `out/pcb/`. Edit the
  model, never the KiCad files by hand — they are overwritten.

## `tools/`

CircuitPython scripts run on the Pico as `code.py`: `matrix_probe/`, `ps2_sniffer/`,
`shift_register_test/`. Standalone; no host-side dependencies. Their pure protocol logic
is unit-tested on a PC under `tools/tests/` (pytest). Index: `tools/README.md`.

## `cad/`

OpenSCAD sources, all including `params.scad` (the only place a dimension lives): the
split `bottom_case`, `perfboard_sled`, `usb_strain_relief`, `tilt_feet`, `zif_support_block`,
`led_light_pipe`, `pico_mount_bracket`, `fpc_cable_guide`; `tests/joint_intersection.scad`
is the split-joint check run by `./dev test`; `export_plates.scad` projects the same solids
into the laser-cut plates and the box insert (DXF).
`./dev build cad` renders to `out/cad/`; meshes are never committed. Index: `cad/README.md`.

## `docs/`

The documentation site source. `hardware/`, `firmware/`, `enclosure/` each have an
`index.md` parent page; `references.md`, `glossary.md`; `images/`. Maintainer pages
(`project-structure`, `design-instructions`, `code-instructions`, `build-and-test`) carry
`nav_exclude: true` and are excluded from the site.

Where new work goes: a measured fact → `hardware/pinout/`; a wiring change →
`hardware/wiring/` first, then the docs that cite it; a design decision → the relevant
`docs/` page plus `CHANGELOG.md`; anything with a state → a GitHub issue, not a doc.
