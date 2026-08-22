# x240-kbd — Project Plan

This is the living plan. It was corrected in August 2026 after research contradicted
several of its original claims; the corrections are listed in [`CHANGELOG.md`](CHANGELOG.md)
and the reasoning lives in the `docs/` pages linked below. Work is tracked as
[GitHub issues](https://github.com/nikolareljin/x240-kbd/issues) in nine milestones.

## Goal

Repurpose a ThinkPad X240 keyboard (FRU 0C44020, with TrackPoint) and its Synaptics
ClickPad into a standalone USB HID device on a Raspberry Pi Pico running QMK. Reuse the
X240 top section as-is. Close the bottom with either a 3D-printed split case or a hand-made
enclosure. Works on any OS without drivers.

Two electronics revisions share one firmware and one GPIO map: **Rev A** perfboard,
**Rev B** KiCad PCB. "Done" is a project someone else can rebuild from the repo.

---

## Hardware

| Component | Detail | Reference |
|---|---|---|
| Controller | Raspberry Pi Pico, RP2040, 26 exposed GPIO | [components](docs/hardware/components.md) |
| Keyboard | X240 0C44020, 40-pin 0.5 mm FPC; **matrix size unknown until probed** | [probing](hardware/pinout/probing_procedure.md) |
| Sense expansion | 3 × 74HC165, 24 sense lines on 3 GPIO | [sense chain](docs/hardware/shift-register-matrix.md) |
| Touchpad | Synaptics ClickPad, PS/2, separate FPC | [pointing stack](docs/firmware/pointing-stack.md) |
| TrackPoint | Through the ClickPad's pass-through port — no extra pins | [trackpoint](docs/hardware/trackpoint.md) |
| Power button | In the keyboard assembly, GP27 | |
| Backlight | LED strip via MOSFET on GP26, `software` driver | [backlight](docs/hardware/backlight.md) |
| Touchpad LED | GP28 via 100 Ω | |
| USB | Micro-USB; USB-C via TP1 (GND) / TP2 (D−) / TP3 (D+) | README |
| Enclosure | Printed split case **or** hand-made (E1–E4) | [printed](docs/enclosure/printed.md) · [hand-made](docs/enclosure/handmade.md) |

### GPIO allocation

The authoritative table is in
[`hardware/wiring/wiring_diagram.md`](hardware/wiring/wiring_diagram.md). Summary:

| GPIO | Function |
|---|---|
| GP0–GP9 | Matrix drive lines D0–D9 |
| GP16 / GP17 / GP18 | Sense chain Q7 (SPI0 RX) / PL / CP (SPI0 SCK) |
| GP21 / GP22 | PS/2 DATA / CLK — ClickPad + TrackPoint (PIO rule: clock = data + 1) |
| GP26 | Backlight MOSFET gate |
| GP27 | Power button, active LOW |
| GP28 | Touchpad LED |
| GP10–GP15, GP19, GP20 | Spare; GP19/GP20 reserved for a standalone-TrackPoint PS/2 line |

Why not a plain 8 × 13 matrix on GPIO: [`docs/hardware/gpio-budget.md`](docs/hardware/gpio-budget.md).

---

## Firmware: QMK on RP2040

QMK over KMK because it has the RP2040 PIO PS/2 host driver, compiled C scan latency,
TinyUSB composite HID, NKRO and a custom-matrix API — all of which this design uses.

```make
MCU                    = RP2040
BOOTLOADER             = rp2040
CUSTOM_MATRIX          = lite        # 74HC165 chain in matrix.c
SRC                   += matrix.c synaptics.c trackpoint.c
POINTING_DEVICE_ENABLE = yes
POINTING_DEVICE_DRIVER = ps2
PS2_MOUSE_ENABLE       = yes
PS2_ENABLE             = yes
PS2_DRIVER             = vendor      # RP2040 PIO; usart is ATmega32u4-only
BACKLIGHT_ENABLE       = yes         # backlit keyboard variants
BACKLIGHT_DRIVER       = software    # RP2040 pwm fails to build (QMK #24470)
EXTRAKEY_ENABLE        = yes
NKRO_ENABLE            = yes
MOUSEKEY_ENABLE        = yes
LTO_ENABLE             = yes
```

Every flag, with its upstream reference: [`docs/firmware/qmk-configuration.md`](docs/firmware/qmk-configuration.md).
File map and data paths: [`docs/firmware/architecture.md`](docs/firmware/architecture.md).

### Layers

- **Layer 0 BASE** — full X240 QWERTY; FN → `MO(_FN)`.
- **Layer 1 FN** — F1–F12 → media/system keys; FN + Esc → FN Lock (`CK_FNLK`);
  FN + F11 → backlight step (`CK_BKLT`).
- Power button is a dedicated GP27 input polled in `matrix_scan_kb()` with a 500 ms guard,
  not a matrix key.

### USB HID composite

Interface 0 keyboard (boot + NKRO) · interface 1 mouse (ClickPad + TrackPoint merged) ·
interface 2 consumer control.

---

## FN key map

| FN + | Action | Keycode | | FN + | Action | Keycode |
|---|---|---|---|---|---|---|
| F1 | Mute | `KC_MUTE` | | F9 | Settings | `KC_F9` |
| F2 | Volume down | `KC_VOLD` | | F10 | Bluetooth | `KC_F10` |
| F3 | Volume up | `KC_VOLU` | | F11 | Backlight | `CK_BKLT` |
| F4 | Mic mute | `KC_F20` | | F12 | Print Screen | `KC_PSCR` |
| F5 | Brightness down | `KC_BRID` | | PgUp | Home | `KC_HOME` |
| F6 | Brightness up | `KC_BRIU` | | PgDn | End | `KC_END` |
| F7 | External display | `KC_F7` | | Left / Right | Prev / next track | `KC_MPRV` / `KC_MNXT` |
| F8 | Wireless | `KC_F8` | | Esc | FN Lock | `CK_FNLK` |

---

## Bill of materials

Full tiers with prices and links: [`docs/hardware/bom-and-cost.md`](docs/hardware/bom-and-cost.md).
All-in **$90–130** (Rev A, own printer) to **$110–150** (Rev A, reused X240 base cover);
Rev B PCB adds $25–35. The donor parts are most of the cost.

---

## Phases

Each phase is a GitHub milestone. Hardware-dependent issues carry `blocked-on-hardware`.

### M0 Documentation — this pass

Component reference, priced BOM, design corrections, the new `docs/` tree, rewrites of the
builder files. Done when the PR merges.

### M1 Diagrams & site

Authored SVG schematics (USB-C, sense chain, backlight, PS/2, internal layout, FPC
orientation, signal flow); Jekyll `just-the-docs` from `/docs`; landing page; Pages enabled.

### M2 Probing — do this before any wiring

1. Rework `tools/matrix_probe/matrix_probe.py` for > 26 FPC pins; extend
   `tools/ps2_sniffer/ps2_sniffer.py` with the Synaptics identify sequence and
   pass-through detection; add `tools/shift_register_test/`.
2. Probe the keyboard FPC: matrix size, every key's (drive, sense) cell, GND/VCC,
   backlight, power button. **Three-key ghosting test** decides whether 1N4148s are needed.
3. Probe the ClickPad FPC: VCC/GND/CLK/DATA/LED. **Push the stick: do `W == 3` frames
   appear?** That answer fixes the TrackPoint route.
4. Fill `hardware/pinout/*.md`.

### M3 Electronics (Rev A)

Stripboard ≈100 × 80 mm: ZIF breakouts, 3 × 74HC165 with SIP pull-ups and decoupling,
backlight MOSFET, PS/2 pull-ups, power button, LED, socketed Pico. Continuity test before
USB power. Procedure: [`ASSEMBLY.md`](ASSEMBLY.md) Phase 2;
schematics: [`hardware/wiring/wiring_diagram.md`](hardware/wiring/wiring_diagram.md).

### M4 Firmware

Correct the configuration; write `matrix.c` (chain scan), `synaptics.c` (identify,
absolute mode, packet parser, logged fallback), `trackpoint.c` (guest frames); regenerate
`LAYOUT` and the keymap from the measured matrix; verify backlight, FN Lock, power guard.

Test checklist: every key; NKRO ≥ 10; ClickPad move/click; **stick moves the cursor with
no finger on the pad**; FN media keys; FN Lock; backlight levels; power button ≥ 500 ms.

### M5 Enclosure, printed

Split `bottom_case.scad` into two halves (dovetail, pins, sled as the bridge); shared
`cad/params.scad`; sled, USB strain relief, tilt feet, ZIF support block, LED light pipe;
measure, print, dry-fit, tolerance report. [`docs/enclosure/printed.md`](docs/enclosure/printed.md).

Print settings: PETG, 0.2 mm, 4 walls, 25 % gyroid. FPC bend radius ≥ 5 mm.

### M6 Enclosure, hand-made

E1 original X240 base cover (worked example with photos), E2 laser-cut plates from the same
SCAD via `projection()`, E3 Hammond 515 console, E4 wood frame; presentation box.
[`docs/enclosure/handmade.md`](docs/enclosure/handmade.md).

### M7 PCB (Rev B)

KiCad schematic and layout, DRC, gerbers, interactive BOM, ordering notes, bring-up on Rev A
firmware. Mounting holes fit both the printed sled and the X240 base-cover standoffs.
[`docs/hardware/pcb.md`](docs/hardware/pcb.md).

### M8 Release

Validate on Linux, Windows, macOS; publish v0.2.0 with a tested `.uf2`.

---

## USB-C upgrade path

Default is the Pico's Micro-USB. Optional: solder a USB-C breakout (with 5.1 kΩ CC
pull-downs) to the Pico's underside pads **TP1 = GND, TP2 = D−, TP3 = D+** plus VBUS; set
`usb_c = true` in `cad/bottom_case.scad`. No firmware change. Or use a Pimoroni Pico LiPo.

![USB-C breakout to Pico test pads](docs/images/usb_c_wiring.svg)

---

## Verification checklist

- [ ] Every key generates the correct HID keycode
- [ ] NKRO: 10+ simultaneous keys register
- [ ] ClickPad: cursor, left click, right click
- [ ] TrackPoint: cursor moves from the stick alone
- [ ] Media keys work on Windows 10/11, macOS 14+, Ubuntu 24
- [ ] Backlight: 5 levels + breathing (backlit variant)
- [ ] Power button: hold ≥ 500 ms → system power dialog; short press ignored
- [ ] FN Lock works
- [ ] Enumerates with no driver install on a fresh OS
- [ ] Enclosure closes with no pinched cable and the USB strain relief takes a pull

---

## Key references

Annotated list: [`docs/references.md`](docs/references.md).
