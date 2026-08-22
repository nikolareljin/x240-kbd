# Bill of materials

The priced, tiered BOM with part numbers and links lives at
**[`docs/hardware/bom-and-cost.md`](docs/hardware/bom-and-cost.md)**; the part-by-part
reference with datasheets is **[`docs/hardware/components.md`](docs/hardware/components.md)**.

## Totals (USD, August 2026)

| Build | All-in |
|---|---|
| Rev A perfboard + your own 3D printer | **$90–130** |
| Rev A perfboard + reused X240 base cover (no printer) | **$110–150** |
| Rev A + commercial print service | $115–170 |
| Rev B PCB | add $25–35 |
| Tools, once, if starting from nothing | add $75–135 |

Earlier revisions quoted $25–35; that omitted the donor keyboard and palmrest.

## Tiers

- **A. Donor** — X240 keyboard `0C44020` (or backlit `04X0177`), palmrest + ClickPad `00HT393`.
- **B. Rev A electronics** — Pico, 40-pin and ClickPad ZIF breakouts, 150 mm FFC extension,
  3 × `SN74HC165N`, 3 × 10 kΩ SIP networks, MOSFET, resistors, 100 nF, stripboard, headers,
  M2 hardware, wire, gasket.
- **C. Rev B PCB** — JLCPCB/PCBWay board, Hirose `FH12-40S-0.5SH(55)` + ClickPad FH12,
  SSOP 74HC165, SMD passives.
- **D. Printed enclosure** — ~150 g PETG, M2 heat-set inserts.
- **E. Hand-made enclosure** — X240 base cover `04X5184` (recommended), or laser-cut
  plates, Hammond 515-0950, or wood.
- **F. Tools** — calipers, iron, multimeter, logic analyser, hand tools.
