# Probing and bring-up tools

CircuitPython scripts that run on the Raspberry Pi Pico **before** QMK is flashed. Each is
standalone: copy it to the `CIRCUITPY` drive as `code.py`, open a serial terminal at
115200 baud, and edit the constants at the top of the file to match your wiring.

| Tool | Milestone step | Edit first |
|---|---|---|
| [`matrix_probe/matrix_probe.py`](matrix_probe/matrix_probe.py) | Keyboard FPC: which pads are drive, which are sense, per key | `PASS` (`"A"` pads 1–26, `"B"` pads 15–40), `NEVER_DRIVE_PADS` once VCC/GND/backlight are known |
| [`ps2_sniffer/ps2_sniffer.py`](ps2_sniffer/ps2_sniffer.py) | ClickPad FPC: find CLK/DATA, then the **TrackPoint verdict** | `MODE` (`"find"` → `"synaptics"`), `CANDIDATE_PAIRS`, then `CLK_PIN`/`DATA_PIN` |
| [`shift_register_test/shift_register_test.py`](shift_register_test/shift_register_test.py) | Verify the 74HC165 chain with nothing else connected | `MODE` (`"watch"` or `"walk"`) |

Order of use: `shift_register_test` (walk mode, on the bare adapter) → `matrix_probe`
pass A → pass B → `ps2_sniffer` find → `ps2_sniffer` synaptics. Results go into
[`../hardware/pinout/`](../hardware/pinout/).

Full procedure: [`../hardware/pinout/probing_procedure.md`](../hardware/pinout/probing_procedure.md).

## Host-side tests

The protocol and table-formatting logic in each script is plain Python with no hardware
imports, so it is unit-tested on a PC:

```bash
cd tools/tests && python3 -m pytest -q
```

Covers the two-pass pad maps and result merging, PS/2 parity and packet decoding, the
Synaptics special-command encoding, 6-byte absolute packets including `W == 3` guest
frames, the capability bits, the verdict text, and the 74HC165 bit-to-sense-line mapping.
The hardware sections are skipped on the host (`ON_DEVICE` is `False`).

## Timing caveat

CircuitPython bit-bangs at tens of microseconds per GPIO operation; PS/2 clocks at
10–16 kHz. Reads are marginal and framing errors are normal — the scripts resync and
only need a handful of good bytes. If nothing decodes, put a logic analyser on the
candidate pins first ([`../docs/hardware/components.md`](../docs/hardware/components.md)).
