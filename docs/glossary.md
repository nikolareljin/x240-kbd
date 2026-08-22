---
title: Glossary
nav_order: 91
---

# Glossary

| Term | Meaning here |
|---|---|
| **Absolute mode** | Synaptics ClickPad reporting finger X/Y/Z position in 6-byte packets instead of relative deltas. Required to receive pass-through frames. |
| **Bit-bang** | Driving a serial protocol from software GPIO toggling instead of a hardware peripheral. QMK's `busywait` PS/2 driver; slow and jittery. |
| **Bootmagic** | QMK feature: holding a designated key (here top-left) while plugging in enters the bootloader. |
| **BOOTSEL** | The button on the Pico that, held at power-up, exposes the `RPI-RP2` UF2 drive. |
| **ClickPad** | A Synaptics touchpad with no separate buttons; the whole surface clicks and zones on it act as buttons. Distinct from a TouchPad with discrete buttons. |
| **COL2ROW** | QMK diode direction: current flows from column to row through the key's diode. Determines which side is driven and which is sensed. With the shift-register chain the "column" side is the chain. |
| **Drive line** | A matrix line the firmware pulls LOW one at a time while reading the others. Rows in QMK's default terminology. |
| **FFC** | Flat Flexible Cable — a laminated ribbon with exposed ends; used here as the 40-pin extension. |
| **FPC** | Flexible Printed Circuit — a polyimide flex with etched traces; the keyboard and ClickPad tails. |
| **FRU** | Field Replaceable Unit — Lenovo's part number for a service part (e.g. `0C44020`). |
| **Guest / pass-through** | The Synaptics mechanism that forwards a second PS/2 device's packets (the TrackPoint) inside the touchpad's own stream, marked by `W == 3`. |
| **Magic knock** | The Synaptics identify sequence: four `SetResolution` commands encoding a query number, then `StatusRequest`. |
| **NKRO** | N-Key Rollover — every key reports independently; needs the matrix diodes to avoid ghosting. |
| **PIO** | RP2040 Programmable I/O — small state machines that implement protocols in hardware. QMK's `vendor` PS/2 driver runs on PIO0. |
| **PL / CP / Q7 / DS / CE** | 74HC165 pins: parallel load, clock, serial out, serial in, clock enable. |
| **PS/2** | The two-wire (CLK, DATA) bidirectional serial bus used by the ClickPad and TrackPoint. |
| **Rev A / Rev B** | Perfboard build / KiCad PCB build. Same firmware, same GPIO map. |
| **Sense line** | A matrix line read (with a pull-up) while a drive line is LOW. Read through the 74HC165 chain. |
| **SIP network** | Single-in-line resistor network; "bussed" means all resistors share one common pin. |
| **TrackPoint** | The red pointing stick; strain gauges plus a controller that outputs PS/2. |
| **UF2** | USB Flashing Format — the file you drag onto the `RPI-RP2` drive. |
| **ZIF** | Zero Insertion Force connector — a hinged tab clamps the FPC after insertion. |
