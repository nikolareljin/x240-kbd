# x240-pico-kbd

A standalone USB keyboard and pointing device built from a ThinkPad X240 keyboard
assembly (part 0C44020) and ClickPad touchpad, controlled by a Raspberry Pi Pico
(RP2040) running QMK firmware.

Works on **any OS without drivers** — enumerates as a standard USB HID composite
device (keyboard + mouse + media keys).

---

## Features

- Full 84-key ThinkPad X240 layout (QWERTY, US)
- ClickPad touchpad (Synaptics, PS/2) — cursor, left/right click
- FN layer with all ThinkPad media/system key mappings
- FN Lock toggle (FN+Esc)
- Keyboard backlight with 5 brightness levels + breathing effect
- Power button with long-press guard (500 ms) → OS sleep/power dialog
- Touchpad indicator LED
- N-Key Rollover (NKRO)
- USB Micro-USB output (USB-C upgrade path below)
- 3D-printed bottom enclosure (OpenSCAD), reuses X240 top section

---

## Hardware Overview

| Component | Detail |
|---|---|
| Controller | Raspberry Pi Pico (RP2040) |
| Keyboard FPC | 40-pin, 0.5 mm pitch, ZIF |
| Touchpad | Synaptics ClickPad, PS/2, separate FPC |
| Power button | Integrated in keyboard assembly |
| Backlight | Keyboard LED strip via 2N7002 MOSFET |
| USB output | Micro-USB (built-in Pico) |
| Enclosure | 3D-printed PETG bottom + X240 top section |
| Build style | Perfboard + 30 AWG wire (no PCB fab needed) |

### Estimated Cost: ~$25–35 USD

See [`BOM.md`](BOM.md) for the full parts list.

---

## Repository Structure

```
x240-pico-kbd/
├── firmware/qmk/keyboards/x240_pico/   QMK keyboard definition
├── hardware/pinout/                     FPC pin maps (filled after probing)
├── hardware/wiring/                     Wiring diagram and GPIO table
├── tools/matrix_probe/                  CircuitPython FPC probing script
├── tools/ps2_sniffer/                   CircuitPython PS/2 bus monitor
├── cad/                                 OpenSCAD bottom enclosure
└── docs/                                Project structure, design, and code docs
```

See [`docs/README.md`](docs/README.md) for the full project documentation index.

---

## Quick Start

### 1. Buy parts

See [`BOM.md`](BOM.md).

### 2. Probe FPC pinout (mandatory first step)

Flash the Pico with CircuitPython, copy `tools/matrix_probe/matrix_probe.py` to it,
and follow [`hardware/pinout/probing_procedure.md`](hardware/pinout/probing_procedure.md).
Do **not** wire to the Pico before the pinout is confirmed.

### 3. Build firmware

```bash
# Install QMK
pip install qmk
qmk setup

# Copy keyboard definition
cp -r firmware/qmk/keyboards/x240_pico \
      ~/qmk_firmware/keyboards/x240_pico

# Compile
qmk compile -kb x240_pico -km default

# Flash (hold BOOTSEL on Pico, then plug USB)
qmk flash -kb x240_pico -km default
```

### 4. Wire perfboard

Follow [`ASSEMBLY.md`](ASSEMBLY.md) — Phase 2.

### 5. Print enclosure

Open `cad/bottom_case.scad` in OpenSCAD. Adjust the parameters section to match your
measured X240 dimensions, export STL, print in PETG.

---

## FN Key Map

| FN + Key | Action |
|---|---|
| F1 | Mute |
| F2 | Volume Down |
| F3 | Volume Up |
| F4 | Mic Mute (KC_F20) |
| F5 | Brightness Down |
| F6 | Brightness Up |
| F7 | External Display |
| F8 | Wireless Toggle |
| F9 | Settings |
| F10 | Bluetooth |
| F11 | Keyboard Backlight Toggle |
| F12 | Print Screen |
| PgUp | Home |
| PgDn | End |
| Left | Previous Track |
| Right | Next Track |
| Esc | **FN Lock toggle** |

---

## USB-C Upgrade (Optional)

The default build uses the Pico's built-in Micro-USB port. To add USB-C:

1. Solder a USB-C female breakout board to the Pico's test pads:
   - TP1 → D−
   - TP2 → D+
   - VBUS and GND
2. Route it to a USB-C cutout in the printed bottom case (`cad/bottom_case.scad`
   has an `usb_c = true` parameter that swaps the cutout shape).
3. No firmware changes required.

Alternatively, use a **Pimoroni Pico LiPo** which has USB-C natively and the same
26 GPIO pinout.

---

## Flashing / Bootloader

- **First flash:** hold BOOTSEL button while plugging in USB → Pico appears as `RPI-RP2`
  drive → drag `.uf2` file onto it.
- **Subsequent flashes:** `qmk flash` uses QMK's Bootmagic — hold the top-left key
  (Esc) while plugging in to enter bootloader.
- **Manual bootloader:** hold BOOTSEL and tap RESET if a reset button is wired to RUN
  pad (optional, recommended for the final build).

---

## Documentation

- [`docs/project-structure.md`](docs/project-structure.md) - repository layout and file ownership
- [`docs/design-instructions.md`](docs/design-instructions.md) - electrical, mechanical, firmware, and documentation design rules
- [`docs/code-instructions.md`](docs/code-instructions.md) - QMK, CircuitPython, and OpenSCAD coding standards
- [`docs/build-and-test.md`](docs/build-and-test.md) - probe, build, flash, and validation workflow
- [`CHANGELOG.md`](CHANGELOG.md) - notable project changes

---

## Repository

Repository: [nikolareljin/x240-kbd](https://github.com/nikolareljin/x240-kbd)

## References

- [hamishcoleman/thinkpad-usbkb](https://github.com/hamishcoleman/thinkpad-usbkb) — ThinkPad FPC pinout research
- [thedalles77/USB_Laptop_Keyboard_Controller](https://github.com/thedalles77/USB_Laptop_Keyboard_Controller) — matrix decoder method
- [QMK RP2040 platform](https://docs.qmk.fm/platformdev_rp2040)
- [QMK PS/2 Mouse](https://docs.qmk.fm/features/ps2_mouse)
- [QMK Pointing Device](https://docs.qmk.fm/features/pointing_device)
- [QMK Backlighting](https://docs.qmk.fm/features/backlight)
- [QMK issue #24470](https://github.com/qmk/qmk_firmware/issues/24470) — RP2040 PWM backlight workaround

---

## License

GPL-2.0 — matching QMK firmware license.
