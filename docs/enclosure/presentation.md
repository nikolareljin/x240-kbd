---
title: Assembly and presentation
parent: Enclosure
nav_order: 5
---

# Assembly ergonomics and the presentation box

## Order of operations

Things become unreachable in this order, so do them in this order.

1. **Bench-test everything open.** Probing, wiring, firmware, every key, ClickPad,
   TrackPoint, backlight, power button — on the bench, case nowhere in sight. Nothing
   below this line should be the first time the electronics are powered.
2. **Prepare the enclosure.** Printed: inserts, dovetail join, pins, sled. E1: strip, clear
   ribs, choose standoffs. E2–E4: assemble the shell.
3. **Fit strain relief and guides** while the case is empty and you can see both sides.
4. **Mount the board on its sled / standoffs.** Pico socketed, USB toward the exit.
5. **Connect the ClickPad FPC** (short; it only reaches from one position), lock the ZIF.
6. **Connect the keyboard FFC extension** to the board, lock it, route through the guides.
7. **Plug in and re-test** with the deck lying beside the case. Last chance to fix a wire.
8. **Connect the keyboard's own tail** to the extension, lay the deck on, check nothing is
   pinched by looking along the seam with a torch.
9. **Screw the deck down** in a star pattern, finger-tight plus a quarter turn. PETG
   inserts strip if you lean on them.
10. **Gasket, feet, light pipe.** Cosmetic last.
11. **Final test on three OSes**, then flash the release firmware.

## Teardown

Reverse 9 → 4. The only consumable is the foam gasket; the only thing to be careful of is
lifting the deck straight up so the keyboard's tail is not bent at the ZIF.

## Torque and fit notes

- M2 into heat-set inserts: hand-tight only. Never a powered driver.
- M2.5 originals on E1: the same screws the laptop used, same torque (light).
- ZIF tabs: they are hinged, not sprung — lift to ~45°, do not pry.
- Dovetail: should slide with thumb pressure; if it needs a mallet the clearance is wrong,
  fix the parameter, do not force it.

## Presentation box

For handing the finished keyboard to someone, or for the shelf.

| Item | Spec |
|---|---|
| Outer box | Two-piece rigid cardboard ("shoulder box"), internal 330 × 230 × 60 mm. Stock sizes near this exist from packaging suppliers; a mailer-style kraft box is the cheap version. |
| Insert | 20 mm EVA foam, cut to the deck outline with a 5 mm margin, plus a pocket for the USB cable and one for the quick-start card. Cut with a hot knife from a paper template printed from `cad/export_plates.scad`'s outline. |
| Cable | 1.5 m USB-A to Micro-USB (or USB-C), coiled with a velcro tie |
| Label | 60 × 40 mm, printed: name, firmware version, FN-key legend, the repository URL as a QR code |
| Quick-start card | A6, double-sided: plug in; FN layer map; Bootmagic/BOOTSEL for updates; "press the stick, not the pad, for the TrackPoint"; link to the site |

The label template and the card are plain SVG/Markdown under `docs/presentation/` (M6).

## What to tell the recipient

- It is a USB HID device: no drivers, works on anything with a USB host, including a phone
  with an OTG adapter.
- The power button sends the system's power/sleep key after a half-second hold.
- The firmware is open; updates are a UF2 file dragged onto a drive.
