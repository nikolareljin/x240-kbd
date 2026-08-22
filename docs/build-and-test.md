---
title: Build and test
nav_exclude: true
---

# Build and test workflow

From raw hardware to a verified device. Each step maps to a milestone. The commands are
`./dev` verbs (`scripts/project.sh`); CI runs `./dev test` and `./dev build all`.

## 1. Probe the keyboard FPC (M2)

CircuitPython on the Pico; `./probe matrix_probe` copies the tool as `code.py`; two passes
over the 40 pads (`PASS = "A"` then `"B"`); 115200 baud. Output is a Markdown table. Record drive/sense pairs per key, matrix size, GND/VCC,
backlight, power button, and the three-key ghost result in
`hardware/pinout/x240_keyboard_fpc_pinout.md`.

## 2. Probe the ClickPad and decide the TrackPoint route (M2)

VCC/GND first; 4.7 kΩ pull-ups on candidate CLK/DATA; `tools/ps2_sniffer/ps2_sniffer.py`
in `MODE = "find"` finds the pair, then in `MODE = "synaptics"` prints a `VERDICT:` line
stating whether `W == 3` pass-through frames appeared when the stick was pushed. Record in `hardware/pinout/x240_clickpad_fpc_pinout.md`.

## 3. Verify the sense chain alone (M3)

Build the 74HC165 chain; run `tools/shift_register_test/shift_register_test.py` in
`MODE = "walk"` — it prompts S0…S23 in order and names the wiring fault on any mismatch.
Only then connect the keyboard FPC.

Host-side checks: `./dev test` (pytest for the tools, byte-compile, link check, shellcheck).

## 4. Wire the rest (M3)

Per `hardware/wiring/wiring_diagram.md`. Complete its pre-power checklist before USB.

## 5. Build and flash firmware (M4)

```bash
./dev install        # once: submodules, docker images, shallow qmk_firmware checkout
./dev build          # qmk compile in qmkfm/qmk_cli -> out/x240_pico_default.uf2
./dev deploy         # waits for the RPI-RP2 drive and copies the UF2
```

`QMK_HOME` points the build at an existing checkout. Images and the QMK commit are pinned
in `scripts/toolchain.env`; `scripts/pull_toolchain.sh --save <dir>` writes offline
tarballs and `--load <dir>` restores them on a machine without registry access. First flash: BOOTSEL → `RPI-RP2`.
Later: `./dev deploy`, Bootmagic (top-left key), or the `RUN` reset switch + BOOTSEL.
Debug output: `./dev logs` (`qmk console`).

## 6. Validate USB HID (M4 → M8)

- Enumerates with no driver on a fresh OS.
- Every key; NKRO with 10+ keys.
- ClickPad move and corner clicks; **stick alone moves the cursor**.
- `qmk console` shows the Synaptics identify succeeding, not the fallback line.
- FN media keys, FN Lock, backlight levels (backlit variant), power button ≥ 500 ms.
- Linux first, then Windows and macOS.

## 7. Enclosure (M5 or M6)

Printed: measure, `params.scad`, `./dev build cad`, print halves + parts, dry-fit,
tolerance report. The split-joint interference check runs in `./dev test`.
Hand-made: E1 base cover or another variant. Then the assembly order in
`docs/enclosure/presentation.md`.

## 8. Acceptance (M8)

Every line in the README's verification checklist passes with the case closed, on three
OSes, and the release carries the tested `.uf2`.
