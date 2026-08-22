---
title: GPIO budget
parent: Hardware
nav_order: 3
---

# GPIO budget and the shift-register decision

## The wall

A Raspberry Pi Pico exposes **26 GPIO**: GP0–GP22 and GP26–GP28. (GP23–GP25 exist on the
RP2040 but are consumed on the Pico by the SMPS mode pin, VBUS sense and the on-board LED.)

The earlier plan assumed an **8 × 13 matrix = 21 lines**, leaving 5 for everything else
and declaring "all 26 GPIOs used". That number was a guess. The closest documented
chiclet-era ThinkPad keyboard — the 04Y0819 reverse-engineered in
[delingren/thinkpad_keyboards](https://github.com/delingren/thinkpad_keyboards) — is a
**17 × 9 matrix = 26 lines for the matrix alone**, before PS/2, backlight, power button or
LED. The same author rejected the Pico for exactly this reason.

Until [probing](https://github.com/nikolareljin/x240-kbd/blob/main/hardware/pinout/probing_procedure.md) measures the X240's matrix, the
design has to assume the worst documented case.

## Demand

| Need | Lines | Notes |
|---|---|---|
| Matrix, worst documented case | 26 | 17 drive + 9 sense, or the transpose |
| PS/2 to the ClickPad | 2 | DATA + CLK, adjacent pins for the PIO driver |
| Backlight gate | 1 | |
| Power button | 1 | |
| Touchpad LED | 1 | |
| Reserve: second PS/2 for a standalone TrackPoint | 2 | only if probing shows the TrackPoint is not on the ClickPad's pass-through |
| **Total** | **33** | against 26 available |

## Options considered

| Option | GPIO | Verdict |
|---|---|---|
| **74HC165 sense chain on the Pico** | 26 − 24 sense + 3 = plenty | **Chosen.** 3 GPIO read up to 24 sense lines. Drive lines stay on GPIO. No new board, no new toolchain, ~$5 of parts. |
| Waveshare RP2040-Zero | 29 | 3 more pins is not enough margin against 33; castellated-only pins are hostile to perfboard. |
| Larger MCU (STM32G474, RP2350B-based boards) | 30–48 | Solves the count but changes the QMK platform, the bootloader story and every doc. delingren went this way; we do not need to. |
| I²C I/O expander (MCP23017) | 2 | Adds an I²C transaction per scan (~100 µs at 400 kHz per 16 bits) and driver complexity for no benefit over a shift register. |
| Diode-free charlieplexing | — | Not applicable — the membrane's matrix is fixed. |

## Chosen allocation

| GPIO | Function | Note |
|---|---|---|
| GP0–GP9 | Matrix **drive** lines D0–D9 | driven LOW one at a time; 10 available, ≥ the documented 9 |
| GP16 | Sense chain serial out ← 74HC165 `Q7` | SPI0 RX |
| GP17 | Sense chain `PL` (parallel load, active LOW) | plain GPIO |
| GP18 | Sense chain `CP` (shift clock) | SPI0 SCK |
| GP21 | PS/2 **DATA** (ClickPad) | |
| GP22 | PS/2 **CLK** (ClickPad) | PIO driver rule: clock = data + 1 |
| GP26 | Backlight → MOSFET gate | |
| GP27 | Power button, active LOW | internal pull-up |
| GP28 | Touchpad LED | via 100 Ω |
| GP10–GP15, GP19, GP20 | **Spare (8)** | GP19/GP20 reserved as a second PS/2 pair (DATA = 19, CLK = 20) |

The authoritative copy of this table lives in
[`../../hardware/wiring/wiring_diagram.md`](https://github.com/nikolareljin/x240-kbd/blob/main/hardware/wiring/wiring_diagram.md).
If the two ever disagree, the wiring diagram wins and this page is wrong.

If probing finds the matrix is transposed (many sense lines, few drive lines), swap roles:
put the larger dimension on the chain. The chain does not care which side it reads.

## Timing budget

QMK's scan loop should complete in well under 1 ms for good debounce behaviour.

- SPI0 at 8 MHz: 24 bits = **3 µs** per drive line.
- `PL` pulse + settle (`MATRIX_IO_DELAY`, 30 µs default) dominates: ~35 µs per drive line.
- 10 drive lines → **~350 µs** per full scan. Comfortable.

A bit-banged chain read would be ~10× slower and still acceptable, so SPI is a convenience,
not a requirement — useful to know when debugging.

## What this does *not* solve

Anti-ghosting. Whether the X240 membrane has diodes is a property of the keyboard, settled
by the three-key test in Phase 1, independent of how the sense lines are read.
