---
title: Hand-made enclosure
parent: Enclosure
nav_order: 2
---

# Enclosure route 2 — hand-made, no 3D printer

Four variants, cheapest and best-fitting first. All reuse the X240 palmrest + keyboard deck
as the top; they differ only in what closes the bottom.

| Variant | Cost | Tools | Fit | Looks |
|---|---|---|---|---|
| **E1 Original X240 base cover** | $22–25 | screwdriver, rotary tool | perfect — it was made for this deck | stock ThinkPad |
| E2 Laser-cut sandwich | $30–60 | none (service cuts it) | good | industrial / transparent |
| E3 Hammond sloped console | $50–60 | drill, nibbler or jigsaw | deck overhangs 9 mm | desk instrument |
| E4 Wood frame | $10–20 | saw, drill, sandpaper | good with care | warm, one-off |

## E1 — Reuse the original base cover (recommended)

FRU `04X5184` / `00HT389` / `0C64937` — the moulding itself is labelled `SCB0G39215` or
`AP0SX000I00`, and eBay listings use any of these — ~$22–25 used
([eBay 04X5184](https://www.ebay.com/itm/121981528885), [eBay SCB0G39215](https://www.ebay.com/itm/156310389262)). It is the laptop's own bottom shell: every
screw boss, clip and edge profile already matches the palmrest. **Zero CAD, zero
measuring.**

What you get for free: the rubber feet, the rear USB/port cutouts (one becomes the cable
exit), the mainboard standoffs (the board mounts on them), and the stock M2.5 screw set.

### Steps

1. **Strip it.** Remove any residual mainboard standoff screws, the fan duct, the battery
   latch mechanism and the battery-bay door. Keep the standoffs.
2. **Plan the board position.** The Rev A stripboard / Rev B PCB sits where the mainboard
   was, FPC connectors toward the keyboard's cable exit (front-centre of the deck). Mark
   which original standoffs line up with the board's M2 holes; the Rev B PCB is drilled to
   match at least three of them. For Rev A stripboard, drill to match.
3. **Clear the ribs.** A few internal ribs will foul the ZIF connectors or the Pico. Cut
   them flush with a rotary tool or flush cutters; the cover is thin ABS/PC and cuts easily.
   Cut less than you think — the deck's rigidity comes from the cover.
4. **USB exit.** Use an existing rear port opening (the old Ethernet or USB cutout). If
   the Pico's Micro-USB cannot reach, fit the optional USB-C breakout at the opening and
   wire TP1/TP2/TP3 (see [`../hardware/components.md`](../hardware/components.md)). Fit a
   cable-tie strain relief anchored to a standoff.
5. **Mount.** Adhesive M2 standoffs (or the original metal ones with M2.5→M2 adapters)
   under the board; keep ≥ 3 mm between the board's underside and the cover.
6. **Route the FFC.** Gentle S-curve, ≥ 5 mm radius; tape the extension to the cover so it
   cannot shift during closing.
7. **Close.** Deck face-down on a towel, cover on, original screws in the original holes.
   The stock rubber feet give the typing angle.
8. **Seal.** The original gasket is already there; add 1 mm foam only where light shows.

Serviceability is the stock laptop's: remove the screws and the cover lifts off.

## E2 — Laser-cut sandwich

A flat bottom plate plus two or three perimeter spacer frames, stacked and bolted with M3
standoffs, laser-cut from 3 mm acrylic or 1.5 mm aluminium.

- Geometry comes from the **same OpenSCAD source** as the printed case:
  `cad/export_plates.scad` uses `projection(cut = true)` at the relevant Z heights and
  exports DXF. The two routes cannot drift apart.
- Upload the DXFs to [SendCutSend](https://sendcutsend.com/) or
  [Ponoko](https://www.ponoko.com/); both quote instantly. Budget $30–60 for the set.
- Stack: bottom plate → spacer frames (height = the internal stack, ~18 mm) → the deck.
  M3 × 20 mm standoffs at the X240 boss positions.
- Acrylic shows the electronics; aluminium is stiffer and grounds the shield. Both need
  rubber feet.

## E3 — Hammond sloped console

[Hammond 515-0950](https://www.hammfg.com/electronics/small-case/general-purpose/500-515-519)
— 300 × 200 × 58 mm steel/aluminium sloped-front console, ~$50–60. The X240 deck is
309 × 210 mm, so it **overhangs 4–5 mm per side**.

- Cut the console's top opening 5 mm inboard of the deck outline; the deck sits on the
  remaining lip, screwed from below through the console top into the deck's bosses.
- Electronics mount to the console floor on adhesive standoffs. The USB cable leaves via a
  rear grommet.
- The sloped front gives a wrist-friendly typing angle; the extra internal height is
  wasted but harmless.

## E4 — Wood frame

A 6 mm plywood base with a hardwood perimeter (12 × 20 mm strip) mitred at the corners.

- Cut list: base 309 × 210; two sides 210 × 20 × 12; front and back 309 × 20 × 12.
- Glue and pin the frame to the base; sand; oil or lacquer.
- The deck sits on the frame's top edge; screw up through the base into the deck's bosses
  using M2 × 12 mm screws with washers (drill pilot holes at the boss positions, measured
  from the palmrest).
- Electronics on adhesive standoffs; USB through a drilled hole with a rubber grommet.

## Common to all hand-made variants

- Keep the FFC bend radius ≥ 5 mm. A printed cable guide is nice; a loop of tape around a
  10 mm dowel does the same job.
- Put the strain relief on the **cable**, not the connector: a cable tie through two holes
  in the base next to the exit.
- Probe, wire and flash on the bench **before** closing any enclosure. Opening a glued wood
  frame is not fun.
