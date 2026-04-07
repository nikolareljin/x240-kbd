# Changelog

All notable project changes should be recorded here.

## Unreleased

- Moved power-button handling out of the placeholder matrix keymap and into
  keyboard-level GP27 polling with the existing long-press guard.
- Added a full `docs/` documentation set covering project structure, design rules,
  coding instructions, and the build/test workflow.
- Updated the README to link the new documentation and clarify repository layout.
- Expanded `.gitignore` for QMK build outputs, Python caches, OpenSCAD exports,
  local QMK checkouts, and transient hardware capture files.
- Preserved the existing X240 Pico design scope: Raspberry Pi Pico RP2040, QMK
  firmware, ThinkPad X240 keyboard matrix, PS/2 ClickPad, keyboard backlight,
  power button guard, and OpenSCAD enclosure workflow.

## 0.1.0

- Initial project structure for the ThinkPad X240 USB keyboard controller.
- Added QMK keyboard definition, default keymap skeleton, firmware config, and
  RP2040 build rules.
- Added hardware pinout templates, wiring diagram, matrix probing tool,
  PS/2 sniffer, bill of materials, assembly guide, and OpenSCAD CAD sources.
