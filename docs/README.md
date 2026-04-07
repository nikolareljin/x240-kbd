# x240-kbd Documentation

This directory contains the durable project guidance for the ThinkPad X240 USB
keyboard and pointing-device conversion.

## Documents

- [`project-structure.md`](project-structure.md) - repository layout, file
  ownership, and where new work belongs.
- [`design-instructions.md`](design-instructions.md) - electrical, mechanical,
  firmware, and documentation design constraints.
- [`code-instructions.md`](code-instructions.md) - coding standards for QMK C,
  CircuitPython tools, OpenSCAD CAD, and Markdown docs.
- [`build-and-test.md`](build-and-test.md) - pinout probing, firmware build,
  flashing, CAD export, and validation workflow.

## Source Of Truth

- `README.md` is the entry point for builders.
- `PLAN.md` captures the project plan and phase sequence.
- `ASSEMBLY.md` is the step-by-step build guide.
- `hardware/pinout/*.md` stores measured FPC pinout data.
- `hardware/wiring/wiring_diagram.md` stores the active GPIO and wiring plan.
- `firmware/qmk/keyboards/x240_pico/` stores the QMK keyboard implementation.
- `cad/*.scad` stores parametric mechanical source files.

If documents disagree, prefer measured hardware data first, then the QMK source,
then the assembly guide, then planning notes.
