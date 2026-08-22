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

A flat bottom plate plus perimeter spacer frames, stacked and bolted with M3 standoffs.

**Files.** `./dev build cad` writes them to `out/cad/`, all derived from the same solids
as the printed case by `cad/export_plates.scad` (`projection(cut = true)`), so the two
routes cannot drift apart:

| DXF | What | Material |
|---|---|---|
| `plate_bottom.dxf` | Floor outline with every hole: M3 at the deck bosses, M2 for the sled, light pipe, feet, tilt feet, reset | 3 mm cast acrylic **or** 1.5 mm 5052 aluminium |
| `plate_spacer.dxf` | Perimeter ring, `wall_t` wide, with the USB notch in the rear edge and the M3 holes | 3 mm acrylic × 6, or 12 mm plywood × 1, or 6 mm acrylic × 3 — whatever sums to `internal_h` (18 mm) |
| `plates_sheet.dxf` | Bottom + spacer + box insert on one sheet | one upload |

**Order.** Upload the DXF to [SendCutSend](https://sendcutsend.com/) (aluminium, acrylic)
or [Ponoko](https://www.ponoko.com/) (acrylic, plywood); both quote instantly. Outlines are
nominal — the service applies kerf. Budget $30–60 for a bottom plate and six acrylic rings.

**Hardware.** 8 × M3 × 20 mm F-F standoffs (or 8 × M3 × 25 mm bolts + nuts), 8 × M3 × 6 mm
screws into the deck's bosses from below, M2 × 6 mm for the sled, 4 rubber feet.

**Stack**, bottom to top: plate → rings (2–3 mm foam tape between the top ring and the
deck as the gasket) → deck. The sled bolts to the plate through its four M2 holes; the USB
cable leaves through the notch, with a cable tie through two extra 4 mm holes you drill
20 mm inboard.

Acrylic shows the electronics; aluminium is stiffer and can be bonded to the board's GND
through one standoff. Both need feet.

## E3 — Hammond sloped console

[Hammond 515-0950](https://www.hammfg.com/electronics/small-case/general-purpose/500-515-519)
— 300 × 200 × 58 mm steel/aluminium sloped-front console, ~$50–60. The X240 deck is
309 × 210 mm, so it **overhangs 4–5 mm per side**; that is acceptable — the deck's own
edge hides the console's edge.

1. **Mark** the opening on the console's top panel: print `plate_spacer.dxf` at 1:1 (or
   trace the deck) and draw the outline **5 mm inboard** all round. Mark the 8 boss
   positions from `params.scad` (`deck_boss_positions`).
2. **Cut** the opening with a nibbler or a jigsaw (fine metal blade), file the edge,
   deburr. Keep the cut-out panel — it becomes a template for the gasket foam.
3. **Drill** the 8 boss holes at 3.5 mm in the remaining lip; countersink from below.
4. **Mount** the board on adhesive M2 standoffs on the console floor, rear-centre, with
   the USB cable to a rear grommet (`cable_d` 4.5 mm → 6 mm grommet hole).
5. **Fit** the deck: foam tape on the lip, deck down, M3 screws from below into the bosses.

The sloped front gives a wrist-friendly angle; the spare internal height is harmless.

## E4 — Wood frame

A 6 mm plywood base with a hardwood perimeter, height `internal_h` (18 mm) so the stack
matches the printed case.

**Cut list** (finished sizes; mitre the strips at 45° or butt-join and plug):

| Piece | Size | Qty |
|---|---|---|
| Base, 6 mm birch ply | 309 × 210 | 1 |
| Side strip, hardwood 18 × 12 | 210 long | 2 |
| Front/back strip, hardwood 18 × 12 | 309 long (285 inside the sides if butt-joined) | 2 |
| Rear strip USB notch | 15 wide × 10 deep, centred on `usb_x` | — |

**Sequence.** Cut the base square (check diagonals). Glue and pin the strips flush with
the base edge, USB notch cut first. Clamp, cure, sand to 180, break the edges. Finish
(oil is forgiving; lacquer is harder). Drill the 8 boss positions through the base at
2.5 mm (print `plate_bottom.dxf` 1:1 as the template) and countersink from below. Fit
rubber feet at `foot_positions`.

**Mount.** Board on adhesive M2 standoffs; cable tie through two 4 mm holes for strain
relief; foam tape on the frame's top edge; deck on; M2 × 12 mm screws with washers up
into the bosses.

## Common to all hand-made variants

- Keep the FFC bend radius ≥ 5 mm. A printed cable guide is nice; a loop of tape around a
  10 mm dowel does the same job.
- Put the strain relief on the **cable**, not the connector: a cable tie through two holes
  in the base next to the exit.
- Probe, wire and flash on the bench **before** closing any enclosure. Opening a glued wood
  frame is not fun.
