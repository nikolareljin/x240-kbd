---
title: Home
nav_order: 1
---

# x240-kbd

A standalone USB keyboard with touchpad **and TrackPoint**, built from a ThinkPad X240
keyboard assembly (FRU 0C44020) and its Synaptics ClickPad, driven by a Raspberry Pi Pico
running QMK. No drivers on any OS — it is a plain USB HID composite device.

{: .warning }
> **Status: designed, not yet built.** Two things are decided only by measurement:
> the keyboard's matrix pinout, and whether the TrackPoint rides the ClickPad's PS/2
> pass-through port. Everything here is designed to survive either answer. The probing
> step is [milestone M2](https://github.com/nikolareljin/x240-kbd/milestone/3).

![Signal flow from keyboard to USB](images/signal_flow.svg)

## What you get

- Full 84-key X240 layout, NKRO, FN layer with the ThinkPad media keys, FN Lock
- ClickPad cursor and click zones, **TrackPoint** decoded from Synaptics pass-through frames
- Keyboard backlight (backlit variants), power button with a hold guard, touchpad LED
- Micro-USB, with a documented USB-C upgrade
- **Two enclosure routes** — 3D-printed split case, or hand-made with no printer
- **Two electronics revisions** — Rev A perfboard, Rev B PCB — same firmware, same GPIO map

## What it costs

| Build | All-in (USD, Aug 2026) |
|---|---|
| Rev A + your own printer | **$90–130** |
| Rev A + reused X240 base cover, no printer | **$110–150** |
| Rev B PCB | add $25–35 |

The donor keyboard and palmrest are most of it. [Full BOM →](hardware/bom-and-cost.html)

## Start here

1. [Component reference](hardware/components.html) — every part, datasheet, and where to buy it.
2. [GPIO budget](hardware/gpio-budget.html) — why a Pico needs a shift register for this keyboard.
3. [TrackPoint](hardware/trackpoint.html) — how the stick reaches the host, and the one measurement that confirms it.
4. [Firmware](firmware/) — what QMK is configured to do, and the two corrections that make it build on RP2040.
5. [Enclosure](enclosure/) — printed or hand-made.
6. [References](references.html) — the projects and datasheets this stands on.

The step-by-step build lives in the repository:
[`ASSEMBLY.md`](https://github.com/nikolareljin/x240-kbd/blob/main/ASSEMBLY.md), with the
wiring reference in
[`hardware/wiring/wiring_diagram.md`](https://github.com/nikolareljin/x240-kbd/blob/main/hardware/wiring/wiring_diagram.md).

## Two things the earlier plan got wrong

This project started as a paper design and was corrected after research. The full list is in
the [changelog](https://github.com/nikolareljin/x240-kbd/blob/main/CHANGELOG.md); the two a
builder must know:

- **USB-C wiring.** The Pico's underside pads are **TP1 = GND, TP2 = D−, TP3 = D+**. The
  first revision said TP1 = D−; built that way, ground shorts onto the data line.
- **PS/2 driver.** On RP2040 the only hardware PS/2 path is the PIO driver (`vendor`),
  and it requires the clock pin to be the data pin + 1 — so **DATA = GP21, CLK = GP22**.

## Progress

Nine milestones, M0 Documentation through M8 Release, tracked as
[issues](https://github.com/nikolareljin/x240-kbd/issues). Issues labelled
`blocked-on-hardware` wait for the donor parts to arrive.
