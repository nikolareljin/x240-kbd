# Design Instructions

Use this file as the design contract for electrical, firmware, mechanical, and
documentation changes.

## Project Goals

- Expose the ThinkPad X240 keyboard and ClickPad as a standard USB HID composite
  device requiring no host drivers.
- Keep the first build possible on perfboard with 30 AWG wire and off-the-shelf
  FPC breakouts.
- Prefer measured pinout data over assumptions. Do not finalize firmware or
  wiring until Phase 1 probing is complete.
- Preserve a clear upgrade path for USB-C without requiring firmware changes.

## Electrical Rules

- Run the keyboard matrix and ClickPad at 3.3 V logic.
- Confirm every FPC pin before connecting it to Pico GPIO.
- Keep GP0-GP7 as matrix row outputs and GP8-GP20 as matrix column inputs unless
  probing proves the matrix needs a different allocation.
- Use external 4.7 kOhm pull-ups on PS/2 CLK and DATA.
- Drive the keyboard backlight through a MOSFET, not directly from a GPIO.
- Keep the MOSFET gate pull-down so the backlight stays off during boot.
- Treat the power button as active-low input with a firmware long-press guard.
- Add external 1N4148 diodes only if testing shows the keyboard matrix lacks
  internal anti-ghosting diodes.

## Firmware Rules

- Keep QMK as the primary firmware because it provides RP2040 support, NKRO,
  PS/2 pointing-device support, Bootmagic, media keys, and TinyUSB HID.
- Keep `POINTING_DEVICE_DRIVER = ps2` and prefer `PS2_DRIVER = usart` while GP21
  and GP22 remain available.
- Keep `BACKLIGHT_DRIVER = timer` unless the RP2040 PWM limitation is confirmed
  fixed for the QMK version being used.
- Poll the dedicated GP27 power-button input in keyboard-level firmware rather
  than representing it as a matrix key.
- Do not treat the placeholder keymap as verified. Replace it with measured
  matrix positions after FPC probing.
- Keep FN+Esc as FN Lock and FN+F11 as keyboard backlight control unless there is
  a deliberate layout change recorded in `CHANGELOG.md`.

## Mechanical Rules

- Keep CAD parametric and editable in OpenSCAD.
- Measure the actual X240 top section with calipers before final STL export.
- Keep FPC bend radius at or above 5 mm in the final enclosure.
- Preserve serviceability: the Pico, perfboard, ZIF connectors, and cable strain
  relief should remain accessible after the bottom case is removed.
- Export meshes into `cad/exports/`; do not commit generated STL/3MF/AMF files by
  default.

## Documentation Rules

- Update `README.md` when the user-facing build flow or feature set changes.
- Update `CHANGELOG.md` for notable project changes.
- Update `hardware/pinout/*.md` immediately after measured pinout discoveries.
- Update `hardware/wiring/wiring_diagram.md` whenever GPIO allocation or circuit
  topology changes.
- Update these docs when project structure or design rules change.
