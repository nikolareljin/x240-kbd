# Bill of Materials

All prices approximate. Total build cost: **$25–35 USD**.

## Core Components

| # | Component | Specific Part | Qty | Source | Est. Cost |
|---|---|---|---|---|---|
| 1 | Microcontroller | Raspberry Pi Pico (RP2040, Micro-USB) | 1 | Pimoroni / Adafruit / DigiKey | $4 |
| 2 | FPC breakout — keyboard | 40-pin 0.5 mm ZIF FPC to DIP adapter | 1 | Adafruit #1436 or AliExpress | $3–5 |
| 3 | FPC breakout — touchpad | 6–12 pin 0.5 mm ZIF FPC to DIP adapter | 1 | AliExpress / eBay | $2–3 |
| 4 | FFC extension — keyboard | 40-pin 0.5 mm pitch, 150 mm length | 1 | DigiKey / AliExpress | $3–5 |

## Discrete Components

| # | Component | Value / Part | Qty | Notes |
|---|---|---|---|---|
| 5 | Schottky diodes | 1N4148 DO-35 | 100 | Only needed if internal keyboard diodes are absent (verify in Phase 1) |
| 6 | N-channel MOSFET | 2N7002 SOT-23 or BS170 TO-92 | 2 | Backlight LED switch |
| 7 | Resistor | 4.7 kΩ 1/4 W | 2 | PS/2 CLK and DATA pull-ups |
| 8 | Resistor | 10 kΩ 1/4 W | 2 | MOSFET gate resistors |
| 9 | Resistor | 100 kΩ 1/4 W | 2 | MOSFET gate pull-down |
| 10 | Resistor | 100 Ω 1/4 W | 2 | Backlight current limit + touchpad LED |
| 11 | Ceramic capacitor | 100 nF (0.1 µF) | 4 | VCC decoupling |

## Mechanical

| # | Component | Detail | Qty |
|---|---|---|---|
| 12 | Stripboard / perfboard | ~80 × 60 mm | 1 |
| 13 | M2 standoffs | M2 × 6 mm brass, with matching screws | 8 |
| 14 | 30 AWG wire | Assorted colours recommended | — |
| 15 | Foam gasket tape | 1 mm self-adhesive craft foam | ~1 m |

## 3D Printing

| # | Component | Detail | Qty |
|---|---|---|---|
| 16 | PETG filament | Any colour, ~100 g for bottom case | — |

## Optional / USB-C Upgrade

| # | Component | Detail | Qty |
|---|---|---|---|
| 17 | USB-C female breakout | USB-C female to solder pads | 1 |

## Where to Buy

- **DigiKey** / **Mouser** — discrete components, FPC breakouts
- **Adafruit** — Pico, Adafruit #1436 FPC breakout
- **AliExpress** — FPC breakouts, FFC extension cables (cheaper, longer shipping)
- **Pimoroni** — Raspberry Pi Pico (UK/EU friendly)
- **JLCPCB / PCBWay** — if you later want a custom PCB (not needed for perfboard build)

## Tools Required

- Digital calipers (for measuring case dimensions)
- Soldering iron + solder
- Multimeter
- Logic analyser or oscilloscope (for PS/2 sniffing in Phase 1 — a cheap $10 logic
  analyser like the Cypress FX2 clone works fine)
- 3D printer (PETG capable, e.g., Bambu, Prusa, Ender 3 with all-metal hotend)
- OpenSCAD (free, for editing the case)
