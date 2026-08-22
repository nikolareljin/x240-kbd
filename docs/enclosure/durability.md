---
title: Durability
parent: Enclosure
nav_order: 4
---

# Thermal, EMI and durability

## Heat

| Source | Power | Note |
|---|---|---|
| Backlight strip (backlit variants) | ~0.3 W (100 mA × 3.3 V) | spread along the keyboard's own aluminium backplate — the deck is the heatsink |
| Pico | < 0.2 W | RP2040 at 125 MHz doing almost nothing |
| 74HC165 × 3, MOSFET | negligible | |

Total well under 1 W in a 309 × 210 mm shell. **Vents are not thermally necessary.** The
`vents = true` slots in `bottom_case.scad` exist for the look and can be set to `false` on
the printed route with no penalty; E1 keeps the laptop's own vents. A deck in direct sun
will get warmer from the sun than from the electronics — PETG's ~80 °C HDT covers that
where PLA's ~55 °C might not.

## EMI and signal integrity

- The PS/2 run is short (< 100 mm) and slow (~10–16 kHz clock); 4.7 kΩ pull-ups and no
  termination are fine.
- The sense chain's SPI at 8 MHz runs on wires of < 80 mm on Rev A — keep `CP` and `Q7`
  twisted or adjacent, and put the 100 nF decouplers within 5 mm of each chip's `VCC`.
- The FFC carries only DC-ish matrix signals. No shielding needed.
- The metal deck of the keyboard is grounded through its mounting screws on a laptop; here,
  run one wire from a deck screw boss to the board's GND so the keyboard's backplate is not
  a floating antenna. An aluminium E2 bottom plate should be bonded the same way.

## FPC fatigue

Polyimide FPCs fail at the bend, after repeated flexing or a single bend under ~3 mm radius.

- ≥ 5 mm radius, enforced by the guide or a taped loop.
- The **extension** takes the bends; the keyboard's own short tail stays nearly straight.
  A cracked $3 extension is a consumable; a cracked keyboard tail is a new keyboard.
- ZIF tabs: open fully before inserting, close only when the cable is square. Count on
  ~20 insertion cycles per connector — more is why the ZIF support block exists.
- Never route an FFC over a cut rib edge (E1) or the dovetail seam (printed).

## Strain relief

The Pico's Micro-USB receptacle is rated for ~10 000 mating cycles but **not** for lateral
pulls. Every route puts the strain on something other than the connector:

- Printed: the snap-in bezel grips the cable jacket in the cutout.
- E1/E3/E4: a cable tie through two holes in the floor, 20 mm inboard of the exit.
- Optional USB-C breakout: the breakout board is screwed to the case; the Pico connects by
  30 AWG wires with slack.

## Shell stiffness

A 309 mm PETG shell with 2.5 mm walls flexes visibly when picked up by one end unless
something bridges it. That is the **sled's** structural job: 4 screws across the seam make
the two halves one box. If flex remains, add two 2 mm ribs running front-to-back in
`bottom_case.scad` (parameter `ribs = true`).

E1 has the laptop's engineered stiffness. E2 in 3 mm acrylic is stiff but brittle — do
not over-torque; aluminium is the stiff choice. E4 is as stiff as the wood.

## Drop and wear

- Feet: 10 mm rubber in the front recesses, the printed tilt feet at the rear with rubber
  pads glued on, or the X240's own feet on E1.
- Edge chips on PETG corners are cosmetic; `corner_r = 3` helps. A chipped dovetail is
  structural — reprint that half.
- Keycap and ClickPad wear are the donor's problem; a worn keyboard is a $25 swap, which is
  the point of keeping the FPC connectors pluggable.
