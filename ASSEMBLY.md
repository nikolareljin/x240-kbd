# Assembly Guide

Complete step-by-step guide for building the x240-pico-kbd.

---

## Phase 1 — FPC Pinout Discovery

**This is mandatory before any wiring. Do not skip.**

The X240 keyboard FPC has 40 pins; not all are matrix signals. You must map every
pin before connecting it to the Pico.

### 1.1 Equipment

- 40-pin 0.5 mm ZIF FPC breakout (Adafruit #1436 or similar)
- Raspberry Pi Pico flashed with CircuitPython
- USB cable
- Serial terminal (e.g., Thonny, PuTTY at 115200 baud)
- Multimeter

### 1.2 Keyboard matrix probing

1. Lift the ZIF locking tab on the breakout board.
2. Insert the keyboard FPC ribbon cable with the contact side facing the correct
   direction (check your specific breakout's datasheet — typically film/blue side up).
3. Close the locking tab.
4. Install CircuitPython on the Pico (drag `.uf2` from circuitpython.org to RPI-RP2).
5. Copy `tools/matrix_probe/matrix_probe.py` to the `CIRCUITPY` drive, rename to
   `code.py`.
6. Open a serial terminal. The script will guide you interactively:
   - It drives each of the 40 pins LOW in turn
   - It reads all other pins for a LOW response (key pressed = circuit completed)
   - Press each key when prompted
   - The script prints `ROW=<pin_A>  COL=<pin_B>` for each keypress
7. Record every (row, col) pair in `hardware/pinout/x240_keyboard_fpc_pinout.md`.

### 1.3 Identifying non-matrix pins

After the matrix sweep, some pins will show no matrix activity:

- **GND**: multimeter continuity to the FPC cable's shield/chassis ground
- **VCC**: measures 3.3 V when the keyboard is passively powered via the breakout's
  VCC pin (use 3.3 V from Pico's 3V3 pin through a 100 Ω safety resistor)
- **Backlight**: with VCC and GND identified, briefly apply 3.3 V through a 100 Ω
  resistor across remaining candidate pairs — the LED strip glows on the correct pair
- **Power button**: probe remaining pins for near-zero resistance continuity when the
  power button is pressed

### 1.4 Touchpad FPC probing

The ClickPad uses a separate, smaller FPC cable.

1. Insert touchpad FPC into the small breakout board.
2. Power the touchpad at 3.3 V (try each candidate VCC pin one at a time with a
   100 Ω series resistor; the touchpad will draw ~10–15 mA when correctly powered).
3. Copy `tools/ps2_sniffer/ps2_sniffer.py` to the Pico (as `code.py`).
4. Edit the script to scan through candidate pin pairs for CLK and DATA.
5. Move a finger on the touchpad surface while monitoring serial output. When CLK
   and DATA are correctly identified, the script prints decoded PS/2 packets.
6. The remaining active pins are the LED signal (anode) — measure ~2 V forward
   voltage drop across them.
7. Record results in `hardware/pinout/x240_clickpad_fpc_pinout.md`.

### 1.5 Internal diode check

Press three keys simultaneously (e.g., A, S, D). If no phantom/ghost keys appear,
the X240 keyboard PCB already has anti-ghosting diodes built in — you do NOT need
external 1N4148 diodes on your adapter. Most ThinkPad keyboards have internal diodes.

---

## Phase 2 — Perfboard Wiring

See `hardware/wiring/wiring_diagram.md` for the full ASCII schematic and GPIO table.

### 2.1 Prepare perfboard

Cut a piece of stripboard to approximately 80 × 60 mm (adjust to fit your printed
case). Break any copper strips that would create unintended connections.

### 2.2 Mount FPC breakouts

Solder the 40-pin keyboard FPC breakout and the touchpad FPC breakout onto the
perfboard. Leave room for the Pico header pins.

### 2.3 Wire matrix rows and columns

Using 30 AWG wire-wrap wire:

- Connect breakout pins corresponding to matrix rows → Pico GP0–GP7
- Connect breakout pins corresponding to matrix cols → Pico GP8–GP20
- Use different wire colours for rows and columns to simplify debugging

Pico GPIO assignments (verify column count from Phase 1 — adjust if needed):

```
GP0  → Row 0      GP8  → Col 0     GP16 → Col 8
GP1  → Row 1      GP9  → Col 1     GP17 → Col 9
GP2  → Row 2      GP10 → Col 2     GP18 → Col 10
GP3  → Row 3      GP11 → Col 3     GP19 → Col 11
GP4  → Row 4      GP12 → Col 4     GP20 → Col 12
GP5  → Row 5      GP13 → Col 5
GP6  → Row 6      GP14 → Col 6
GP7  → Row 7      GP15 → Col 7
```

### 2.4 Backlight MOSFET circuit

```
3.3V ──── 100Ω ──── LED strip anode
                     LED strip cathode ──── MOSFET Drain
                                           MOSFET Source ──── GND
GP26 ──── 10kΩ ──── MOSFET Gate
                    MOSFET Gate ──── 100kΩ ──── GND
```

The 100 kΩ pull-down holds the gate LOW (LED off) when the Pico boots before
firmware takes control. The 10 kΩ gate resistor limits inrush current.

Measure the LED strip current: if it exceeds 20 mA, increase the 100 Ω series
resistor until current is within safe range.

### 2.5 PS/2 touchpad wiring

```
Pico 3.3V ──── Touchpad VCC
Pico GND  ──── Touchpad GND
GP21      ──── 4.7kΩ ──── 3.3V    (PS/2 CLK, pull-up)
GP21      ──────────────────────── Touchpad CLK pin
GP22      ──── 4.7kΩ ──── 3.3V    (PS/2 DATA, pull-up)
GP22      ──────────────────────── Touchpad DATA pin
```

### 2.6 Touchpad LED

```
GP28 ──── 100Ω ──── LED anode
                    LED cathode ──── GND
```

### 2.7 Power button

```
FPC power button pin ──── GP27
GP27 uses Pico internal pull-up (enabled in firmware config.h)
```

When button is pressed, GP27 is pulled LOW → firmware detects rising/falling edge.

### 2.8 Pico mounting

Mount the Pico on M2 standoffs (6 mm). Use the footprint in `cad/pico_mount_bracket.scad`
for drilling positions. Alternatively, design perfboard to include matching mounting holes.

---

## Phase 3 — Firmware

### 3.1 Install QMK

```bash
pip install qmk
qmk setup
```

Follow the QMK setup prompts. This clones QMK firmware into `~/qmk_firmware`.

### 3.2 Install keyboard definition

```bash
cp -r firmware/qmk/keyboards/x240_pico \
      ~/qmk_firmware/keyboards/x240_pico
```

### 3.3 Update matrix dimensions

Open `firmware/qmk/keyboards/x240_pico/keyboard.json` and update `matrix_size`
to match what you found in Phase 1:

```json
"matrix_size": {
    "rows": 8,
    "cols": 13
}
```

Also update `matrix_pins.cols` list length to match.

### 3.4 Fill the keymap

Open `firmware/qmk/keyboards/x240_pico/keymaps/default/keymap.c`.

The `LAYOUT(...)` macro needs one entry per matrix position. Using the row/col pairs
from Phase 1, map each physical key to its QMK keycode. QMK's key tester at
`qmk.fm/newbs/testing_your_keyboard.html` helps verify each key after flashing.

### 3.5 Compile

```bash
qmk compile -kb x240_pico -km default
```

The compiled `.uf2` file will be in `~/qmk_firmware/.build/x240_pico_default.uf2`.

### 3.6 Flash

Hold the **BOOTSEL** button on the Pico while plugging in the USB cable.
The Pico appears as a `RPI-RP2` USB drive. Drag the `.uf2` file onto it.
After flashing, the Pico reboots as a USB HID device automatically.

For subsequent flashes, hold the top-left key (Esc) while plugging in — Bootmagic
puts the Pico into bootloader mode without needing to press BOOTSEL.

### 3.7 Test

- Open a text editor and press every key
- Use an online NKRO tester to verify rollover
- Move the touchpad and click
- Test FN layer: FN+F1 (mute), FN+F11 (backlight), FN+Esc (FN lock)
- Long-press power button (>500 ms) — system power dialog should appear

### 3.8 Tune touchpad sensitivity

In `firmware/qmk/keyboards/x240_pico/config.h`, adjust:

```c
#define POINTING_DEVICE_ROTATION_90   // uncomment if cursor direction is rotated
#define PS2_MOUSE_X_MULTIPLIER 3      // increase for faster horizontal movement
#define PS2_MOUSE_Y_MULTIPLIER 3      // increase for faster vertical movement
```

Recompile and flash after each adjustment.

---

## Phase 4 — 3D Case

### 4.1 Measure X240 top section

Using digital calipers, measure:

- Outer perimeter of keyboard deck at the bottom mating surface
- Position of every screw hole relative to a fixed corner
- Existing plastic clip positions along edges
- Height of existing rubber feet (for clearance)

Update the parameter block at the top of `cad/bottom_case.scad` with your measurements.

### 4.2 Export STL

1. Open `cad/bottom_case.scad` in OpenSCAD
2. Set `$fn = 64` for smooth curves
3. Press **F6** (Render), then **File → Export → Export as STL**
4. Save to `cad/exports/bottom_case.stl`

### 4.3 Print

Recommended settings:

| Setting | Value |
|---|---|
| Material | PETG |
| Layer height | 0.20 mm |
| Perimeter walls | 4 |
| Infill | 25% gyroid |
| Supports | None needed (print flat side down) |
| Build plate adhesion | Brim (3–5 mm) if first layer adhesion is poor |

### 4.4 Test fit

Before final assembly, do a dry-fit:
- Check that the bottom case mates flush with the X240 top section
- Verify M2 screw holes align with existing X240 boss positions
- Confirm FPC cable guides are accessible and not obstructed

If anything is off, edit the OpenSCAD parameters and reprint.

---

## Phase 5 — Final Assembly

1. Seat the perfboard + Pico assembly onto the M2 standoffs inside the case.
2. Route keyboard FPC through the cable guide with no bends tighter than 5 mm radius.
3. Route touchpad FPC through its guide.
4. Connect both FPC cables to the breakout connectors; lock ZIF tabs.
5. Mate the bottom case to the X240 top section (keyboard deck face down on a soft surface).
6. Thread M2 screws through the bottom case into the X240 top's boss holes.
7. Apply 1 mm foam gasket tape around the perimeter to fill any gap between parts.
8. Route the USB cable through the cutout. Use a cable tie or clip inside to act as
   strain relief so pulling the cable does not stress solder joints.
9. Plug in, verify all functions work.
10. Flash final tuned firmware build.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| No USB device detected | Pico not powered or wrong `.uf2` | Check cable; reflash |
| Some keys missing / wrong | Keymap LAYOUT mismatch | Recheck Phase 1 matrix map |
| Ghost keys | No internal diodes; need 1N4148 | Add external diodes at FPC adapter |
| Touchpad not moving | PS/2 CLK/DATA swapped | Swap GP21/GP22 in `config.h` |
| Touchpad very slow | Sensitivity multiplier too low | Increase `PS2_MOUSE_X/Y_MULTIPLIER` |
| Backlight always off | MOSFET wired incorrectly | Check Gate/Drain/Source orientation |
| Backlight always on | Pull-down resistor missing | Add 100 kΩ Gate-to-GND |
| Power button triggers instantly | No long-press timer | Check `process_record_user` code |
