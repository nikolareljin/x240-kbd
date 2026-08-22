# FPC Pinout Probing Procedure

This document explains how to discover the exact function of every pin on the X240
keyboard and touchpad FPC cables before wiring them to the Pico.

---

## Equipment

- Raspberry Pi Pico (flashed with CircuitPython) — the *same* Pico is reused for the build
- 40-pin 0.5 mm FPC-to-DIP breakout **with a ZIF connector** (see `docs/hardware/components.md`; Adafruit #1436 is a bare solder-pad plate, not a ZIF breakout)
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

The 40-pad breakout has more pads than the Pico has GPIO (26). The script runs in
**two passes**: wire pads 1–26 for pass A, then pads 15–40 for pass B (the overlap ties the
two maps together). Record which pad is on which GPIO for each pass at the top of the script.

The script will:
- Iterate through the wired pads
- Drive each pin LOW while configuring all other pins as inputs with pull-ups
- Display: `Press a key... ` and wait
- When you press a key, it prints the two pin numbers that went LOW together
- Record each (pin_A, pin_B) pair against the key name

Work through every key on the keyboard. Keys that share a row will produce the same
first pin number; keys in the same column share the second pin number.

### A3. Build the drive/sense map

After scanning all keys, group the results:

- **Drive lines**: the set of pads that appear as the "driven" pad across multiple keys
- **Sense lines**: the remaining active pads

Count them. The smaller set goes to GP0–GP9 as drive lines; the larger set goes to the
74HC165 chain as sense lines. If both are ≤ 10 you could skip the chain — but keep it; it
is what makes the design survive a transposed or larger-than-expected matrix.

### A3b. Ghosting test

Hold A + S + D. If a fourth key appears, the membrane has no diodes and every sense line
needs a 1N4148 at the breakout. Most ThinkPad membranes have them.

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

### A5. TrackPoint lines (only if Part B shows a standalone TrackPoint)

If Part B finds no pass-through frames, two of the remaining keyboard FPC pins are the
TrackPoint controller's CLK and DATA (and possibly a reset). Find them as in B3, with
4.7 kΩ pull-ups, using the sniffer in plain PS/2 mode while pushing the stick.

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
   correctly identified. The CLK line toggles at ~10–16 kHz; a logic analyser makes
   it easy to spot visually even before decoding.
6. If no output: swap the candidate pins for CLK and DATA and retry.
7. For the build, DATA goes to **GP21** and CLK to **GP22** — the RP2040 PIO driver needs
   clock = data + 1.

### B3b. Confirm the TrackPoint route

Switch the sniffer to Synaptics mode (it sends the identify sequence and enables absolute
mode with pass-through). Push the stick with no finger on the pad:

- Packets with `W == 3` ⇒ the TrackPoint rides this bus. **Done — no extra wiring.**
- No such packets ⇒ go to A5 and wire the TrackPoint's own line to GP20/GP19.

Record the result in `x240_clickpad_fpc_pinout.md`. This single observation decides the
firmware path; do not skip it.

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
