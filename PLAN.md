# x240-pico-kbd — Full Project Plan

## Context

Repurpose a ThinkPad X240 keyboard (part 0C44020, SG-58950-XUA) and ClickPad touchpad
into a standalone USB HID device using a Raspberry Pi Pico (RP2040) running QMK
firmware. The X240 top section (keyboard deck, palmrest, touchpad bezel) is reused
as-is. The bottom enclosure is 3D-printed. Output is Micro-USB (USB-C optionally
documented). Works on any OS without drivers.

---

## Hardware

| Component | Detail |
|---|---|
| Controller | Raspberry Pi Pico (RP2040, Micro-USB) |
| Keyboard | ThinkPad X240 (0C44020), 40-pin FPC, 0.5 mm pitch, ZIF |
| Touchpad | Synaptics ClickPad, separate FPC (6–12 pin, 0.5 mm), PS/2 |
| Power button | Integrated in keyboard assembly |
| Backlight | Keyboard LED strip via 2N7002 N-MOSFET on GP26 |
| Touchpad LED | Single indicator LED via 100 Ω resistor on GP28 |
| USB | Pico built-in Micro-USB (USB-C upgrade path documented) |
| Enclosure | 3D-printed PETG bottom (OpenSCAD), reuse X240 top section |
| Build | Perfboard + 30 AWG wire — no PCB fab needed |

---

## GPIO Allocation (all 26 Pico GPIOs used)

Assumed 8×13 matrix from probing (adjust if actual count differs).

| GPIO | Function |
|---|---|
| GP0–GP7 | Matrix rows R0–R7 (driven LOW during scan) |
| GP8–GP20 | Matrix cols C0–C12 (input, internal pull-up) |
| GP21 | PS/2 CLK — UART0, 4.7 kΩ pull-up to 3.3 V |
| GP22 | PS/2 DATA — UART0, 4.7 kΩ pull-up to 3.3 V |
| GP26 | Keyboard backlight PWM → 2N7002 gate |
| GP27 | Power button (input, internal pull-up, 500 ms long-press guard) |
| GP28 | Touchpad LED (output HIGH = on) |

If probing reveals more than 13 columns, add a 74HC165 shift register on cols and
free up GP27/GP28 by controlling them through the shift register chain.

---

## Firmware: QMK on RP2040

**QMK chosen over KMK** because:
- Native PS/2 USART driver (hardware UART, not bit-bang)
- Compiled C — sub-1 ms scan latency
- TinyUSB composite HID (keyboard + mouse + consumer) built-in
- NKRO, media keys, backlight/breathing all native
- Actively maintained; RP2040 support stable since 2022

### rules.mk flags

```
MCU                    = RP2040
BOOTLOADER             = rp2040
POINTING_DEVICE_ENABLE = yes
POINTING_DEVICE_DRIVER = ps2
PS2_DRIVER             = usart       # RP2040 UART0; fallback: bitbang
BACKLIGHT_ENABLE       = yes
BACKLIGHT_DRIVER       = timer       # Workaround: RP2040 PWM bug QMK#24470
EXTRAKEY_ENABLE        = yes
NKRO_ENABLE            = yes
MOUSEKEY_ENABLE        = yes
LTO_ENABLE             = yes
```

### Layers

- **Layer 0 BASE:** Full X240 QWERTY. FN key → `MO(_FN)`.
- **Layer 1 FN:** F1–F12 → media/system keycodes. FN+Esc → FN Lock (`TG(_FN)`).
  FN+F11 → backlight toggle.
- **Custom keycodes:** `CK_BKLT`, `CK_FNLK`, `CK_PWR` (long-press system power).

### USB HID composite (no drivers, any OS)

QMK with `POINTING_DEVICE_ENABLE` enumerates automatically:
- Interface 0: HID Keyboard (boot-protocol + NKRO)
- Interface 1: HID Mouse (PS/2 touchpad data)
- Interface 2: HID Consumer Control (media keys)

---

## FN Key Map

| FN + Key | Action | QMK Keycode |
|---|---|---|
| F1 | Mute | `KC_MUTE` |
| F2 | Volume Down | `KC_VOLD` |
| F3 | Volume Up | `KC_VOLU` |
| F4 | Mic Mute | `KC_F20` |
| F5 | Brightness Down | `KC_BRID` |
| F6 | Brightness Up | `KC_BRIU` |
| F7 | External Display | `KC_F7` |
| F8 | Wireless Toggle | `KC_F8` |
| F9 | Settings | `KC_F9` |
| F10 | Bluetooth | `KC_F10` |
| F11 | Backlight Toggle | `CK_BKLT` |
| F12 | Print Screen | `KC_PSCR` |
| PgUp | Home | `KC_HOME` |
| PgDn | End | `KC_END` |
| Left | Previous Track | `KC_MPRV` |
| Right | Next Track | `KC_MNXT` |
| Esc | FN Lock toggle | `CK_FNLK` |

---

## Bill of Materials

| Component | Qty | Notes |
|---|---|---|
| Raspberry Pi Pico | 1 | RP2040, Micro-USB |
| 40-pin 0.5 mm ZIF FPC breakout | 1 | Adafruit #1436 or equiv. |
| 6–12 pin 0.5 mm ZIF FPC breakout | 1 | For touchpad |
| 40-pin 0.5 mm FFC extension, 150 mm | 1 | Strain relief inside case |
| 1N4148 diodes | 100 | Only if internal keyboard diodes absent |
| 2N7002 N-MOSFET SOT-23 | 2 | Backlight switch |
| 4.7 kΩ resistors | 2 | PS/2 pull-ups |
| 100 Ω resistors | 2 | Backlight current + touchpad LED |
| 100 nF ceramic caps | 4 | Decoupling |
| Stripboard ~80×60 mm | 1 | Adapter board |
| M2 × 6 mm standoffs + screws | 8 | Mounting |
| 30 AWG wire | — | Point-to-point |
| PETG filament ~100 g | — | Bottom case |
| USB-C female breakout (optional) | 1 | USB-C upgrade |
| **Total** | | **~$25–35 USD** |

---

## Assembly Phases

### Phase 1 — FPC Pinout Discovery (Days 1–3) — DO THIS FIRST

**Do not wire to the Pico before all pins are confirmed.**

1. Insert keyboard FPC into 40-pin ZIF breakout. Flash Pico with CircuitPython.
   Copy `tools/matrix_probe/matrix_probe.py` to the CIRCUITPY drive.
2. Open a serial terminal (115200 baud). The script drives each pin LOW in turn
   and prompts you to press keys. Record every (row, col) pair.
3. Idle pin voltages: GND = 0 V, VCC = 3.3 V. Identify power rails.
4. Backlight: apply 3.3 V through a 100 Ω resistor across candidate pins — LED
   strip glows on the correct pair.
5. Power button: probe for continuity (near-zero resistance) when pressed.
6. Touchpad FPC (separate cable): power touchpad at 3.3 V, use
   `tools/ps2_sniffer/ps2_sniffer.py` to capture PS/2 frames on each pin pair
   while moving a finger on the pad. CLK pin shows a clock waveform; DATA has data.
7. Touchpad LED pins: measure ~2 V forward voltage (LED) across candidate pairs.
8. Fill `hardware/pinout/x240_keyboard_fpc_pinout.md` and
   `hardware/pinout/x240_clickpad_fpc_pinout.md` with verified data.

**Internal diodes check:** press 3 keys simultaneously. No phantom keypresses = the
X240 PCB already has matrix diodes — skip external 1N4148s.

### Phase 2 — Perfboard Wiring (Days 4–6)

1. Cut stripboard ~80×60 mm to fit inside bottom case.
2. Solder 40-pin and touchpad FPC breakout boards onto the perfboard.
3. Wire matrix rows GP0–GP7 and cols GP8–GP20 from breakout to Pico pin headers.
4. MOSFET backlight circuit:
   - Gate → 10 kΩ resistor → GP26 (and 100 kΩ pull-down to GND)
   - Drain → backlight LED strip cathode
   - Source → GND
   - LED strip anode → 100 Ω → 3.3 V (measure current; X240 strip ~20 mA)
5. PS/2: 4.7 kΩ from GP21 to 3.3 V; 4.7 kΩ from GP22 to 3.3 V.
6. Touchpad LED: GP28 → 100 Ω → LED anode; LED cathode → GND.
7. Power button: FPC pin → GP27; GP27 uses Pico internal pull-up.
8. Mount Pico with M2 standoffs.
9. Document the complete wiring in `hardware/wiring/wiring_diagram.md`.

### Phase 3 — Firmware (Days 7–10)

```bash
pip install qmk
qmk setup
cp -r firmware/qmk/keyboards/x240_pico ~/qmk_firmware/keyboards/x240_pico
# Edit keyboard.json: update matrix_size to match Phase 1 results
# Edit keymaps/default/keymap.c: fill LAYOUT macro with actual key positions
qmk compile -kb x240_pico -km default
qmk flash   -kb x240_pico -km default   # hold BOOTSEL when plugging in
```

Test checklist:
- Every key fires correct keycode (use online key tester)
- Touchpad moves cursor; left/right regions click correctly
- FN layer: all media keys work
- Backlight cycles through 5 levels via FN+F11
- Power button long-press (>500 ms) triggers system power dialog
- FN Lock: FN+Esc permanently inverts FN layer

### Phase 4 — 3D Case (Days 11–16)

Measure with digital calipers:
- X240 outer dimensions (~309 × 210 mm)
- Screw boss positions from original bottom cover
- Required internal height (≥15 mm: Pico 3.5 mm + cables + clearance)
- USB port exit position

Edit parameters in `cad/bottom_case.scad`:
```
case_width      = 309;   // measured
case_depth      = 210;   // measured
wall_t          = 2.5;
corner_r        = 3;
internal_h      = 18;
usb_c           = false; // true = USB-C cutout, false = Micro-USB
```

Print settings: PETG, 0.2 mm layers, 4 perimeter walls, 25% gyroid infill.
Test-fit with X240 top before final print.

FPC cable routing rules:
- Minimum bend radius: 5 mm (FPC cables crack below 3 mm)
- Use the printed cable guide clips in `cad/fpc_cable_guide.scad`

### Phase 5 — Final Assembly (Days 17–20)

1. Install perfboard + Pico in case on M2 standoffs.
2. Route FPC cables through guides (no sharp bends).
3. Mate bottom case to X240 top section; secure with M2 screws at boss locations.
4. Apply 1 mm foam gasket around perimeter (craft foam, self-adhesive).
5. Route USB cable through cutout.
6. Tune firmware sensitivity constants, flash final build.
7. Full test on Windows, macOS, Linux.

---

## USB-C Upgrade Path

Default: Pico Micro-USB.

Optional upgrade:
- Solder USB-C female breakout to Pico pads TP1 (D−), TP2 (D+), VBUS, GND.
- Set `usb_c = true` in `cad/bottom_case.scad` before printing.
- No firmware changes needed.
- Alternative: Pimoroni Pico LiPo (USB-C native, same pinout).

---

## Verification Checklist

- [ ] Every key generates the correct HID keycode
- [ ] NKRO: 10+ simultaneous keys all register
- [ ] Touchpad: cursor, left click, right click
- [ ] Media keys work on Windows 10/11, macOS 14+, Ubuntu 24
- [ ] Backlight: 5 levels + breathing
- [ ] Power button: hold >500 ms → system power dialog
- [ ] FN Lock works
- [ ] Device enumerates with no driver install on a fresh OS

---

## Key References

- `hamishcoleman/thinkpad-usbkb` — ThinkPad FPC pinout community research
- `thedalles77/USB_Laptop_Keyboard_Controller` — matrix decoder technique
- QMK RP2040 platform docs: https://docs.qmk.fm/platformdev_rp2040
- QMK PS/2 mouse: https://docs.qmk.fm/features/ps2_mouse
- QMK pointing device: https://docs.qmk.fm/features/pointing_device
- QMK backlight: https://docs.qmk.fm/features/backlight
- QMK issue #24470 — RP2040 PWM backlight bug (`BACKLIGHT_DRIVER = timer` workaround)
