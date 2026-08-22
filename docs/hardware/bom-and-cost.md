---
title: BOM and cost
parent: Hardware
nav_order: 2
---

# Bill of materials and cost estimate

All prices are **USD street prices observed in August 2026** and will drift. Part numbers
and datasheets are in [`components.md`](components.md).

An earlier revision of this project quoted **$25–35 total**. That figure left out the donor
keyboard and palmrest, which are the largest single cost. The honest range is below.

## Totals at a glance

| Build path | All-in |
|---|---|
| Rev A perfboard + your own 3D printer | **$90–130** |
| Rev A perfboard + reused X240 base cover (hand-made route E1, no printer) | **$110–150** |
| Rev A perfboard + commercial print service | $115–170 |
| Rev B PCB instead of perfboard | add $25–35 to any row |
| Tools, if starting from nothing | add $75–135, once |

---

## A. Donor hardware — every build

| Part | FRU / spec | Qty | Est. | Source |
|---|---|---|---|---|
| X240 keyboard, US, with TrackPoint | `0C44020` non-backlit · `04X0177` backlit | 1 | $20–35 | [eBay](https://www.ebay.com/itm/387219786805), Amazon |
| X240 palmrest with ClickPad | `00HT393` (no FPR) · `00HT392` (FPR) | 1 | $20–40 | [eBay](https://www.ebay.com/p/1361311702), [iFixit](https://www.ifixit.com/products/00ht393-lenovo-thinkpad-x240-palmrest-touchpad-without-fpr) |
| *or* palmrest + keyboard + ClickPad as one used assembly | | 1 | $36–80 | eBay |
| **Subtotal** | | | **$45–75** | |

Buy the backlit keyboard variant only if you want the backlight; the non-backlit `0C44020`
has no LED strip and the backlight circuit is simply left unpopulated.

---

## B. Controller and electronics — Rev A perfboard

| Part | Spec | Qty | Est. | Source |
|---|---|---|---|---|
| Raspberry Pi Pico | RP2040, Micro-USB | 1 | $4 | [raspberrypi.com](https://www.raspberrypi.com/products/raspberry-pi-pico/) |
| *(alt)* Raspberry Pi Pico 2 | RP2350 — verify QMK PS/2 PIO support first | 1 | $5 | [Pico 2 launch](https://www.raspberrypi.com/news/raspberry-pi-pico-2-our-new-5-microcontroller-board-on-sale-now/) |
| 40-pin 0.5 mm FPC → DIP breakout, with ZIF | bottom contact | 1 | $3–5 | [Tinkersphere](https://tinkersphere.com/cables-wires/3608-40-pin-05mm-1mm-pitch-fpc-to-dip-breakout.html), [Amazon 2-pk](https://www.amazon.com/40-Pin-Connector-Breakout-Board-0-5mm/dp/B00XSC2G4A) |
| 8–12-pin 0.5 mm FPC → DIP breakout | ClickPad, count your cable first | 1 | $2.70 | [Tinkersphere](https://tinkersphere.com/cables-wires/3616-8-pin-05mm-1mm-pitch-fpc-to-dip-breakout.html) |
| 40-pin 0.5 mm FFC extension, 150 mm | | 1 | $2–4 | [BuyDisplay](https://www.buydisplay.com/150mm-length-40-pins-0-5mm-pitch-bottom-contact-ffc-fpc-flex-cable-4579) |
| 74HC165 shift register, DIP-16 | `SN74HC165N` | 3 | $4.26 | [DigiKey](https://www.digikey.com/en/products/detail/texas-instruments/SN74HC165N/376966) |
| 10 kΩ bussed SIP resistor network, 9-pin | sense pull-ups | 3 | ~$1 | [Jameco](https://www.jameco.com/c/Network-SIP-Resistors.html) |
| N-channel MOSFET | `BS170` TO-92 (or `2N7002`) | 2 | ~$0.50 | DigiKey / Mouser |
| Resistors 4.7 kΩ, 10 kΩ, 100 kΩ, 100 Ω | ¼ W | assorted | ~$1 | any |
| 100 nF ceramic capacitors | X7R | 6 | ~$0.50 | any |
| 1N4148 diodes | **only if the three-key test shows ghosting** | 100 | ~$2 | any |
| Stripboard ≈100 × 80 mm | | 1 | $3–5 | [Vero](https://verotl.com/circuitboards/veroboards) |
| 2 × 20-pin female headers | socket for the Pico | 1 set | $1 | any |
| M2 standoff + screw kit | brass, 6 mm | kit | $6–8 | Amazon |
| 30 AWG wire-wrap wire | assorted colours | 1 | $8 | Amazon |
| 1 mm foam gasket tape | self-adhesive | ~1 m | $5 | craft store |
| **Subtotal** | | | **$40–50** | |

---

## C. Rev B PCB increment

Replaces the two breakouts, the stripboard and the wire. Everything else in B is still needed.

| Part | Spec | Qty | Est. | Source |
|---|---|---|---|---|
| 2-layer PCB ≈100 × 80 mm, 5 pcs | JLCPCB / PCBWay | 1 order | $2 + $15–25 shipping | JLCPCB |
| 40-pin 0.5 mm ZIF, bottom contact | Hirose `FH12-40S-0.5SH(55)` | 1 | $2.70 | [DigiKey](https://www.digikey.com/en/products/detail/hirose-electric-co-ltd/FH12-40S-0-5SH-55/1110328) |
| ClickPad ZIF, 0.5 mm | Hirose `FH12-nnS-0.5SH(55)`, `nn` from probing | 1 | ~$1.45 | DigiKey |
| 74HC165, SSOP/TSSOP | `SN74HC165DBR` / `74HC165PW` | 3 | $1.35 | [DigiKey](https://www.digikey.com/en/products/detail/texas-instruments/SN74HC165DR/377068) |
| SMD passives and 4 × 0603 resistor arrays | | — | ~$2 | LCSC |
| **Subtotal** | | | **$25–35** | |

---

## D. Enclosure route 1 — 3D printed

| Item | Est. | Note |
|---|---|---|
| PETG, 120–180 g of a $20–25 spool | $4–6 | Bottom case printed as **two halves** plus seven small parts — see [`../enclosure/printed.md`](../enclosure/printed.md) |
| M2 × 3 mm heat-set inserts | $5 | |
| *(no printer)* commercial print of the split case | $25–45 | Craftcloud, JLC3DP; the split is what makes a 309 mm case quotable |

---

## E. Enclosure route 2 — hand-made, no printer

Full detail in [`../enclosure/handmade.md`](../enclosure/handmade.md).

| Variant | Est. | Note |
|---|---|---|
| **E1 Reuse the original X240 base cover** — recommended | $22–25 | FRU `04X5184` / `00HT389`. Already mates to the palmrest with the stock screw bosses; gut it, mount the board on adhesive standoffs, cut a rear USB slot. No CAD at all. [eBay](https://www.ebay.com/itm/121981528885) |
| E2 Laser-cut acrylic / aluminium sandwich | $30–60 | Plates exported from the same OpenSCAD source; cut by [SendCutSend](https://sendcutsend.com/) or [Ponoko](https://www.ponoko.com/) |
| E3 Off-the-shelf sloped console | $50–60 | [Hammond 515-0950](https://www.hammfg.com/electronics/small-case/general-purpose/500-515-519), 300 × 200 × 58 mm; the 309 mm deck overhangs 9 mm |
| E4 Plywood base + hardwood frame | $10–20 | Saw, drill, finish |

---

## F. Tools — one-time, if not owned

| Tool | Est. |
|---|---|
| Digital calipers | $15–20 |
| Temperature-controlled soldering iron + fine tip | $25–60 |
| Multimeter with diode mode | $15–25 |
| 8-channel USB logic analyser (FX2 clone) | $10–15 |
| Flush cutters, tweezers, flux, solder wick | $10–15 |
| **Total** | **$75–135** |

OpenSCAD and KiCad are free.

---

## Where to buy

- **DigiKey / Mouser** — 74HC165, MOSFETs, Hirose connectors, resistor networks, passives.
- **Tinkersphere / Amazon / AliExpress** — FPC ZIF breakouts, FFC extensions (AliExpress is
  cheapest and slowest).
- **raspberrypi.com approved resellers, Adafruit, Pimoroni** — Pico.
- **eBay / iFixit** — donor keyboard, palmrest, base cover.
- **JLCPCB / PCBWay** — Rev B board; **LCSC** for its SMD parts in the same order.
