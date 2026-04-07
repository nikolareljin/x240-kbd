# Build And Test Workflow

Follow this workflow when taking the project from raw hardware to a verified USB
keyboard and pointing device.

## 1. Probe The Keyboard FPC

1. Flash CircuitPython to a Raspberry Pi Pico.
2. Wire candidate keyboard FPC breakout pads to available Pico GPIO pins.
3. Copy `tools/matrix_probe/matrix_probe.py` to the `CIRCUITPY` drive as
   `code.py`.
4. Open a serial terminal at 115200 baud.
5. Press each prompted key and record the reported row/column pair.
6. Copy the results into `hardware/pinout/x240_keyboard_fpc_pinout.md`.
7. Identify GND, VCC, backlight, and power-button pins with a multimeter and
   safe series resistance before final wiring.

## 2. Probe The ClickPad

1. Confirm touchpad VCC and GND pins.
2. Add 4.7 kOhm pull-ups on candidate PS/2 CLK and DATA lines.
3. Copy `tools/ps2_sniffer/ps2_sniffer.py` to the `CIRCUITPY` drive as `code.py`.
4. Edit `CANDIDATE_PAIRS` for the candidate FPC breakout pins.
5. Move a finger on the touchpad and record the first pair that produces valid
   PS/2 packets.
6. Copy the result into `hardware/pinout/x240_clickpad_fpc_pinout.md`.

## 3. Wire The Perfboard

Use `hardware/wiring/wiring_diagram.md` as the active wiring reference.

- Matrix rows: GP0-GP7.
- Matrix columns: GP8-GP20.
- PS/2 CLK/DATA: GP21/GP22 with external pull-ups.
- Keyboard backlight: GP26 through a MOSFET circuit.
- Power button: GP27 active-low input.
- Touchpad LED: GP28 through a current-limiting resistor.

After wiring, inspect for shorts before connecting USB power.

## 4. Build Firmware

Install and initialize QMK, then copy this keyboard definition into the QMK tree.

```bash
pip install qmk
qmk setup
cp -r firmware/qmk/keyboards/x240_pico ~/qmk_firmware/keyboards/x240_pico
qmk compile -kb x240_pico -km default
```

The compiled UF2 should appear in `~/qmk_firmware/.build/`.

## 5. Flash Firmware

For the first flash, hold BOOTSEL while plugging in the Pico and copy the UF2 to
the `RPI-RP2` drive. For later flashes, hold the top-left key while plugging in
if Bootmagic is working.

```bash
qmk flash -kb x240_pico -km default
```

## 6. Validate USB HID Behavior

- Confirm the device enumerates without custom drivers.
- Press every key and compare against the intended X240 layout.
- Verify NKRO with 10 or more simultaneous keys.
- Verify FN layer media keys and FN+Esc lock behavior.
- Verify FN+F11 cycles the backlight.
- Verify ClickPad cursor movement and left/right click behavior.
- Verify power button only sends the system power event after the configured
  long press.
- Test on at least one Linux host before final enclosure assembly. Test Windows
  and macOS as compatibility targets when available.

## 7. Export And Test-Fit CAD

1. Measure the actual X240 top section with calipers.
2. Update parameters in `cad/bottom_case.scad`.
3. Render in OpenSCAD and export meshes to `cad/exports/`.
4. Print in PETG and dry-fit before final assembly.
5. Confirm FPC bend radius, USB cutout alignment, screw alignment, and standoff
   clearance.

## 8. Final Acceptance

The build is ready when every key, the ClickPad, the backlight, FN Lock, the
power button guard, and USB enumeration work after the case is assembled.
