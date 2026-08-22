---
title: Printed enclosure
parent: Enclosure
nav_order: 1
---

# Enclosure route 1 — 3D printed

## The part that does not fit

`cad/bottom_case.scad` models the bottom shell as **one 309 × 210 mm part**. That is larger
than every common print bed:

| Printer | Bed (X × Y mm) | 309 mm fits? |
|---|---|---|
| Creality Ender 3 / V3 | 220 × 220 | no |
| Prusa MK4 / MK3S | 250 × 210 | no |
| Bambu X1 / P1 / A1 | 256 × 256 | no |
| Prusa XL, Bambu H2D, Elegoo Neptune 4 Max | ≥ 320 | yes |

So the case is printed as **two halves**, joined at the centreline (`split_x` in
`params.scad`):

- Each half is 154.5 mm wide plus 10 mm of tabs — fits a 220 mm bed flat.
- **Floor tabs:** three dovetail tabs (`tab_count`, `tab_w`, `tab_flare`, `tab_len`) on the
  left half's floor drop into matching pockets in the right half; pockets are grown by
  `joint_gap` (0.15 mm per face — tune with a 30 mm coupon).
- **Wall half-lap:** on the front and rear walls the left half's outer half-thickness
  continues 8 mm past the seam; the right wall is recessed to match.
- **Pins:** two 3 mm holes through the laps take a length of filament or brass rod.
- **The sled** screws to four bosses, two per half — that is what makes the joined shell
  stiff; the tabs only locate it.
- The gasket ledge continues across the seam so it is not a dust path.
- `half = "left" | "right" | "both"` — `"both"` for a large-format printer.

The joint is verified every `./dev test`: `cad/tests/joint_intersection.scad` renders the
overlap of the two halves and `scripts/check_cad_joint.py` fails if it has any volume.

## The eight printed parts

| # | Part | File | Purpose | Qty |
|---|---|---|---|---|
| 1 | Bottom case, left | `bottom_case.scad` (`half="left"`) | Shell, bosses, gasket ledge, vents, USB cutout, light-pipe aperture, foot recesses | 1 |
| 2 | Bottom case, right | `bottom_case.scad` (`half="right"`) | as above | 1 |
| 3 | Pico mount bracket | `pico_mount_bracket.scad` | Cradle holding the Pico at a fixed height (Rev A only; Rev B mounts the Pico on the board) | 1 |
| 4 | FPC cable guide | `fpc_cable_guide.scad` (`cable="keyboard"`/`"clickpad"`) | Enforces ≥ 5 mm bend radius on the FFC | 2 + 1 |
| 5 | Perfboard sled | `perfboard_sled.scad` | Tray with the common M2 hole pattern; holds Rev A stripboard or Rev B PCB; bridges the case seam | 1 |
| 6 | USB strain relief | `usb_strain_relief.scad` | Two-piece clamp (M2 bolts) gripping the cable jacket, screwed to the floor, so a pull loads the case, not the Pico's connector | 1 set |
| 7 | Tilt feet | `tilt_feet.scad` | Rear risers for a typing angle; front recesses take 10 mm rubber feet | 2 |
| 8 | ZIF support block | `zif_support_block.scad` (`variant="keyboard"`/`"clickpad"`) | Backs up the FPC connectors against insertion force so they do not lift off the board | 1 + 1 |
| 9 | LED light pipe | `led_light_pipe.scad` | Carries the touchpad LED to the deck surface; printed in clear PETG or natural PLA | 1 |

(Nine files, "eight parts" in the issues because the two case halves come from one source.)

All dimensions come from one shared file, `cad/params.scad`; values marked `MEASURE` are
targets until the real X240 deck is measured (#44). No number may be duplicated across
files. Render everything with `./dev build cad` → `out/cad/*.stl` (OpenSCAD 2021.01 in
Docker; PNG previews are not available headless — open the `.scad` in OpenSCAD to look).

## Print settings

| Part | Material | Layer | Walls | Infill | Supports | Notes |
|---|---|---|---|---|---|---|
| Case halves | PETG | 0.20 mm | 4 | 25 % gyroid | none, open side up | 3–5 mm brim if corners lift |
| Sled, bracket, ZIF block | PETG | 0.20 mm | 3 | 30 % | none | |
| Cable guide, strain relief | PETG | 0.16 mm | 3 | 40 % | none | small; print several |
| Tilt feet | PETG | 0.20 mm | 4 | 40 % | none | flat face down |
| Light pipe | clear PETG / natural PLA | 0.12 mm | 100 % | none | print standing | polish the tip |

PETG over PLA for the case: higher heat deflection (a laptop deck in the sun) and less
brittle at the dovetail. Estimated filament 120–180 g for the set.

## Tolerances

| Feature | Nominal | Printed allowance |
|---|---|---|
| M2 heat-set insert hole | 3.2 mm | +0 — inserts want a snug hole |
| Dovetail | — | 0.15 mm clearance per face; test with a 30 mm coupon before the full print |
| Alignment pins | 3.0 mm | hole 3.2 mm |
| Sled to case bosses | M2 | 2.4 mm clearance holes in the sled |
| Gasket ledge | 1.2 mm deep × 2.0 mm wide | foam tape is 1 mm; ledge leaves 0.2 mm compression |
| USB cutout | Micro-USB 8.5 × 3.5 / USB-C 9.5 × 4.0 | +0.5 mm each way |

Record actual measured-vs-designed values after the first dry-fit (issue #44); the table
above becomes the tolerance report.

## Assembly order for the printed route

1. Fit heat-set inserts into both halves and the sled.
2. Join the halves on the dovetail; push in the alignment pins.
3. Screw the sled across the seam — the case is now rigid.
4. Fit cable guides and ZIF support blocks to the sled.
5. Continue with [`integration.md`](integration.md).

## No printer?

Commercial print services (Craftcloud, JLC3DP, Treatstock) will quote the split halves
readily; a single 309 mm part is often refused or priced for an industrial machine. Expect
$25–45 for the set in PETG. Or skip printing entirely: [`handmade.md`](handmade.md).
