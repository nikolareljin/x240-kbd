---
title: Documentation index
nav_exclude: true
---

# x240-kbd documentation

Builder-facing pages are grouped by subject; maintainer rules are at the bottom. The same
files are served as the GitHub Pages site (milestone M1).

## Hardware

- [`hardware/components.md`](hardware/components.md) — every part with datasheet and product links
- [`hardware/bom-and-cost.md`](hardware/bom-and-cost.md) — tiered BOM and all-in cost
- [`hardware/gpio-budget.md`](hardware/gpio-budget.md) — why a Pico needs a shift register here
- [`hardware/shift-register-matrix.md`](hardware/shift-register-matrix.md) — the 74HC165 sense chain
- [`hardware/trackpoint.md`](hardware/trackpoint.md) — TrackPoint via Synaptics pass-through
- [`hardware/backlight.md`](hardware/backlight.md) — MOSFET circuit and the RP2040 driver choice
- [`hardware/pcb.md`](hardware/pcb.md) — Rev A perfboard vs Rev B PCB

## Firmware

- [`firmware/architecture.md`](firmware/architecture.md) — file map and data paths
- [`firmware/qmk-configuration.md`](firmware/qmk-configuration.md) — every flag, with corrections
- [`firmware/pointing-stack.md`](firmware/pointing-stack.md) — ClickPad + TrackPoint decoding

## Enclosure

- [`enclosure/printed.md`](enclosure/printed.md) — split case and the small printed parts
- [`enclosure/handmade.md`](enclosure/handmade.md) — no printer: base cover, laser-cut, console, wood
- [`enclosure/integration.md`](enclosure/integration.md) — stack heights, routing, screws
- [`enclosure/durability.md`](enclosure/durability.md) — heat, EMI, FPC fatigue, stiffness
- [`enclosure/presentation.md`](enclosure/presentation.md) — assembly order, box, label, card

## Reference

- [`references.md`](references.md) — annotated sources
- [`glossary.md`](glossary.md)

## Maintainer rules (not published on the site)

- [`project-structure.md`](project-structure.md) — where things live
- [`design-instructions.md`](design-instructions.md) — design contract
- [`code-instructions.md`](code-instructions.md) — coding standards
- [`build-and-test.md`](build-and-test.md) — workflow from raw hardware to verified device

## Source of truth

1. Measured data in `hardware/pinout/*.md`
2. The GPIO table in `hardware/wiring/wiring_diagram.md`
3. QMK source under `firmware/`
4. `ASSEMBLY.md`, then `PLAN.md`

If documents disagree, the earlier item wins and the later one has a bug.
