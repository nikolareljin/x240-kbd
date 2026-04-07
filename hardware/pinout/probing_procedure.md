# FPC Pinout Probing Procedure

This document explains how to discover the exact function of every pin on the X240
keyboard and touchpad FPC cables before wiring them to the Pico.

---

## Equipment

- Raspberry Pi Pico (flashed with CircuitPython)
- 40-pin 0.5 mm ZIF FPC breakout board (Adafruit #1436 or equivalent)
- 6–12 pin 0.5 mm ZIF FPC breakout board (for touchpad)
- Multimeter (continuity + DC voltage modes)
- Logic analyser (cheap 8-channel USB type works fine) — for touchpad PS/2 sniffing
- Serial terminal (Thonny IDE, PuTTY, or screen — 115200 baud)
- `tools/matrix_probe/matrix_probe.py` (copy to Pico as `code.py`)
- `tools/ps2_sniffer/ps2_sniffer.py` (copy to Pico as `code.py` for touchpad phase)

---

## Part A — Keyboard Matrix

### A1. Insert FPC cable

1. Lift the ZIF locking lever on the breakout board.
2. Slide the keyboard FPC ribbon into the connector.
   - Most FPC breakouts require the contact pads (shiny metal) to face down.
   - Check your specific breakout board's silkscreen or datasheet.
3. Close the locking lever firmly.

### A2. Flash CircuitPython and run matrix_probe

1. Hold BOOTSEL while plugging Pico into USB → appears as `RPI-RP2`.
2. Drag the CircuitPython `.uf2` from circuitpython.org onto the drive.
3. Pico reboots as `CIRCUITPY`.
4. Copy `tools/matrix_probe/matrix_probe.py` onto `CIRCUITPY`, rename to `code.py`.
5. Open a serial terminal at 115200 baud (Thonny serial console works well).

The script will:
- Iterate through all 40 pins (via the breakout's numbered pads)
- Drive each pin LOW while configuring all other pins as inputs with pull-ups
- Display: `Press a key... ` and wait
- When you press a key, it prints the two pin numbers that went LOW together
- Record each (pin_A, pin_B) pair against the key name

Work through every key on the keyboard. Keys that share a row will produce the same
first pin number; keys in the same column share the second pin number.

### A3. Build the row/column map

After scanning all keys, group the results:

- **Rows**: the set of pins that appear as the "driven" pin across multiple keys
- **Columns**: the remaining active pins

Write the verified map into `hardware/pinout/x240_keyboard_fpc_pinout.md`.

### A4. Identify power, GND, backlight, power button

After the matrix sweep, find pins that produced no matrix activity:

**GND**: set multimeter to continuity mode. The FPC cable's metallic shield/foil
is GND. Touch one probe to it and sweep the other across all breakout pads. All GND
pins beep.

**VCC**: supply 3.3 V from the Pico's 3V3 pin through a 100 Ω safety resistor to each
candidate pin one at a time. Measure voltage on the same pin — it reads 3.3 V when
found. (Most X240 keyboards run at 3.3 V; verify before connecting directly.)

**Backlight**: with VCC and GND identified, try each remaining unidentified pair as a
potential LED+/LED- pair. Apply 3.3 V through a 100 Ω resistor across the pair. The
keyboard backlight strip will faintly glow. Note: the backlight on the non-backlit
variant (0C44020) is absent — these pins may be no-connect.

**Power button**: probe remaining pins for near-zero resistance when the power button
is physically pressed (multimeter continuity mode).

---

## Part B — Touchpad FPC

### B1. Insert touchpad FPC

Insert the touchpad's FPC cable into the small breakout board the same way as above.

### B2. Identify VCC and GND

- GND: continuity to the touchpad PCB chassis/shield
- VCC: try 3.3 V (via 100 Ω safety resistor) on each candidate pin; the Synaptics
  controller will draw ~10–15 mA when correctly powered. You can confirm by measuring
  current with the multimeter in series.

### B3. Identify PS/2 CLK and DATA

1. Flash Pico with `tools/ps2_sniffer/ps2_sniffer.py` (as `code.py`).
2. Edit the script to set the two candidate pin numbers to monitor.
3. Power the touchpad (VCC + GND from Pico).
4. Move your finger on the touchpad surface.
5. The serial console should show decoded PS/2 movement packets when CLK/DATA are
   correctly identified. The CLK line toggles at ~10 kHz; a logic analyser makes
   it easy to spot visually even before decoding.
6. If no output: swap the candidate pins for CLK and DATA and retry.

### B4. Identify LED pins

The touchpad indicator LED (if present) appears as a ~2 V forward-voltage drop
across a pair of pins. Measure with multimeter in diode mode across candidate pins.
The pair that reads ~1.8–2.2 V (forward drop) is the LED anode (+) and cathode (−).

---

## Recording Results

Fill in the two files below with your verified data:

- `hardware/pinout/x240_keyboard_fpc_pinout.md`
- `hardware/pinout/x240_clickpad_fpc_pinout.md`

Use the templates provided in those files. Accurate pinout data here is the foundation
of the entire build — take your time and double-check every entry.
