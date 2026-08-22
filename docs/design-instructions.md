---
title: Design instructions
nav_exclude: true
---

# Design instructions

The design contract for electrical, firmware, mechanical and documentation changes.

## Goals

- Standard USB HID composite device; no host drivers, any OS.
- First build possible on perfboard with off-the-shelf FPC breakouts; Rev B PCB is a
  drop-in with the same GPIO map and firmware.
- Measured data over assumptions: nothing is wired or finalised before Phase 1 probing.
- Two enclosure routes (printed, hand-made) from one set of dimensions.
- A USB-C path that needs no firmware change.

## Electrical

- 3.3 V logic everywhere; confirm every FPC pin before it touches a GPIO.
- Drive lines on GP0–GP9; sense lines through the 74HC165 chain on GP16/17/18. Put the
  larger matrix dimension on the chain.
- Every 74HC165 input has an external pull-up; `CE` grounded; last `DS` grounded; 100 nF
  per chip.
- PS/2 DATA = GP21, CLK = GP22 (PIO driver: clock = data + 1), 4.7 kΩ pull-ups. GP19/GP20
  stay reserved for a second PS/2 pair.
- Backlight through a MOSFET with a gate pull-down; series resistor set by measurement.
- Power button is an active-low input with a firmware long-press guard, not a matrix key.
- 1N4148 diodes only if the three-key test shows the membrane lacks them.
- The USB-C upgrade uses TP1 = GND, TP2 = D−, TP3 = D+. Never the other way.

## Firmware

- QMK. `PS2_DRIVER = vendor`, `BACKLIGHT_DRIVER = software`, `CUSTOM_MATRIX = lite`.
  Changing any of these needs a measured reason recorded in `CHANGELOG.md`.
- The TrackPoint is decoded from Synaptics pass-through frames. If the identify sequence
  fails, fall back to relative mode **and log it** — no silent degradation.
- The placeholder keymap is not verified; regenerate from measured data.
- FN + Esc = FN Lock, FN + F11 = backlight, unless a layout change is recorded.

## Mechanical

- One shared `cad/params.scad`; no dimension duplicated across files.
- The bottom case is printed as two halves; the sled bridges the seam.
- FPC bend radius ≥ 5 mm; strain relief loads the case, never a connector.
- Serviceable: deck off, two ZIF tabs, board out. No glue in the printed route.
- Meshes and DXFs go to `cad/exports/`, not into git.

## Documentation

- `hardware/wiring/wiring_diagram.md` holds the only GPIO table; other pages link to it.
- Every part named anywhere appears in `docs/hardware/components.md` with a link.
- Every cost figure traces to `docs/hardware/bom-and-cost.md`.
- A correction to a previously published claim goes in `CHANGELOG.md` with its source.
- Images are illustration unless authored as SVG with source in-tree; captions say which.
- State lives in GitHub issues, not in documents.
