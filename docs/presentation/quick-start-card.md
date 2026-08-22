---
title: Quick-start card
parent: Enclosure
nav_order: 6
---

# Quick-start card (A6, two sides)

Print at 100 % on card stock; fold nothing. Side 1 faces up in the box.

---

## Side 1 — plug in

**x240-kbd** — a ThinkPad X240 keyboard, ClickPad and TrackPoint as one USB device.

1. Plug the USB cable into any computer, phone or tablet with a USB host. No drivers:
   it enumerates as a keyboard + mouse.
2. Type. The **ClickPad** moves the cursor; its bottom corners are left/right click.
3. Push the **red stick** for the TrackPoint. Rest your finger on it lightly — it measures
   force, not travel.
4. **Power button:** hold ½ s for the system's power/sleep dialog. A tap does nothing.

**FN layer** (hold FN):

| | | | |
|---|---|---|---|
| F1 mute | F2 vol − | F3 vol + | F4 mic mute |
| F5 bright − | F6 bright + | F7 display | F8 wireless |
| F9 settings | F10 bluetooth | **F11 backlight** | F12 print screen |
| PgUp home | PgDn end | ← prev track | → next track |
| **Esc = FN lock** | | | |

---

## Side 2 — keep it working

**Firmware updates.** Hold **Esc** while plugging in (or press the reset hole on the
underside with BOOTSEL held). A drive named `RPI-RP2` appears; drag the new `.uf2` onto
it. The keyboard restarts by itself. Firmware and instructions:
`github.com/nikolareljin/x240-kbd`

**Cursor too fast or slow?** That is a firmware constant
(`SYN_TOUCHPAD_DIVISOR`, `SYN_TRACKPOINT_MULT`); rebuild and update as above.

**Opening it.** Deck screws out from below, lift the deck straight up, unlatch the two
ribbon-cable tabs. Nothing is glued.

**Don't.** Bend the ribbon cables tighter than a 5 mm radius. Pull the cable by the plug.
Run it from a USB hub that cannot supply 500 mA if the backlight is on.

Built ________ · serial ________ · GPL-2.0
