# X240 Keyboard FPC Pinout

**Part:** 0C44020 / SG-58950-XUA  
**Connector:** 40-pin ZIF, 0.5 mm pitch  
**Status:** Template — fill in verified data after Phase 1 probing (milestone M2, issue #28)

Terminology: **drive** lines are pulled LOW one at a time by GP0–GP9; **sense** lines are
read through the 74HC165 chain (S0 = U1.D0 … S23 = U3.D7). If probing shows the matrix is
transposed (more drive than sense), swap the roles — the chain goes on the larger side.

---

## Pin Map

| Pin | Function | Pico GPIO | Notes |
|-----|----------|-----------|-------|
| 1   | ?        |           | |
| 2   | ?        |           | |
| 3   | ?        |           | |
| 4   | ?        |           | |
| 5   | ?        |           | |
| 6   | ?        |           | |
| 7   | ?        |           | |
| 8   | ?        |           | |
| 9   | ?        |           | |
| 10  | ?        |           | |
| 11  | ?        |           | |
| 12  | ?        |           | |
| 13  | ?        |           | |
| 14  | ?        |           | |
| 15  | ?        |           | |
| 16  | ?        |           | |
| 17  | ?        |           | |
| 18  | ?        |           | |
| 19  | ?        |           | |
| 20  | ?        |           | |
| 21  | ?        |           | |
| 22  | ?        |           | |
| 23  | ?        |           | |
| 24  | ?        |           | |
| 25  | ?        |           | |
| 26  | ?        |           | |
| 27  | ?        |           | |
| 28  | ?        |           | |
| 29  | ?        |           | |
| 30  | ?        |           | |
| 31  | ?        |           | |
| 32  | ?        |           | |
| 33  | ?        |           | |
| 34  | ?        |           | |
| 35  | ?        |           | |
| 36  | ?        |           | |
| 37  | ?        |           | |
| 38  | ?        |           | |
| 39  | ?        |           | |
| 40  | ?        |           | |

---

## Matrix Summary (fill after probing)

| Signal | FPC pin | Destination |
|--------|---------|-------------|
| Drive D0 | | GP0 |
| Drive D1 | | GP1 |
| Drive D2 | | GP2 |
| Drive D3 | | GP3 |
| Drive D4 | | GP4 |
| Drive D5 | | GP5 |
| Drive D6 | | GP6 |
| Drive D7 | | GP7 |
| Drive D8 | | GP8 |
| Drive D9 | | GP9 |
| Sense S0–S7 | | U1 D0–D7 |
| Sense S8–S15 | | U2 D0–D7 |
| Sense S16–S23 | | U3 D0–D7 |
| GND | | GND |
| VCC | | 3V3 |
| Backlight + | | R_series |
| Backlight − | | Q1 drain |
| Power button | | GP27 |
| TrackPoint CLK *(only if standalone — see ClickPad pinout)* | | GP20 |
| TrackPoint DATA *(only if standalone)* | | GP19 |
| TrackPoint reset *(if present)* | | spare GPIO, pulsed HIGH at boot |

Measured matrix size: ____ drive × ____ sense.  Three-key ghost test: diodes present ☐ / absent ☐

---

## Key → Matrix Cell Map (fill after probing)

| Key       | Drive | Sense |
|-----------|-------|-------|
| Esc      |       |       |
| F1       |       |       |
| F2       |       |       |
| F3       |       |       |
| F4       |       |       |
| F5       |       |       |
| F6       |       |       |
| F7       |       |       |
| F8       |       |       |
| F9       |       |       |
| F10      |       |       |
| F11      |       |       |
| F12      |       |       |
| `        |       |       |
| 1        |       |       |
| 2        |       |       |
| 3        |       |       |
| 4        |       |       |
| 5        |       |       |
| 6        |       |       |
| 7        |       |       |
| 8        |       |       |
| 9        |       |       |
| 0        |       |       |
| -        |       |       |
| =        |       |       |
| Tab      |       |       |
| Q        |       |       |
| W        |       |       |
| E        |       |       |
| R        |       |       |
| T        |       |       |
| Y        |       |       |
| U        |       |       |
| I        |       |       |
| O        |       |       |
| P        |       |       |
| [        |       |       |
| ]        |       |       |
| CapsLock |       |       |
| A        |       |       |
| S        |       |       |
| D        |       |       |
| F        |       |       |
| G        |       |       |
| H        |       |       |
| J        |       |       |
| K        |       |       |
| L        |       |       |
| ;        |       |       |
| '        |       |       |
| Backspace|       |       |
| LShift   |       |       |
| Z        |       |       |
| X        |       |       |
| C        |       |       |
| V        |       |       |
| B        |       |       |
| N        |       |       |
| M        |       |       |
| ,        |       |       |
| .        |       |       |
| /        |       |       |
| RShift   |       |       |
| PgUp     |       |       |
| LCtrl    |       |       |
| Win      |       |       |
| LAlt     |       |       |
| Space    |       |       |
| RAlt     |       |       |
| Menu     |       |       |
| RCtrl    |       |       |
| PgDn     |       |       |
| Ins      |       |       |
| Del      |       |       |
| Home     |       |       |
| End      |       |       |
| Up       |       |       |
| Left     |       |       |
| Down     |       |       |
| Right    |       |       |
| PrtSc    |       |       |
| ScrLk    |       |       |
| Pause    |       |       |
| \        |       |       |
| Enter    |       |       |
| FN       |       |       |

---

## References for Cross-Checking

Before probing, cross-reference with community documentation:

- [delingren/thinkpad_keyboards](https://github.com/delingren/thinkpad_keyboards) — 04Y0819, 17 × 9 matrix (era analogue, not this connector)
- [hamishcoleman/thinkpad-usbkb](https://github.com/hamishcoleman/thinkpad-usbkb) — `keyboard-thinkpad.pinout.txt` (older connector)
- [thedalles77/USB_Laptop_Keyboard_Controller](https://github.com/thedalles77/USB_Laptop_Keyboard_Controller) — method and T61 example
- [Lenovo X240 Hardware Maintenance Manual](https://support.lenovo.com/us/en/manuals/um019141)

None of these documents the 0C44020's 40-pin connector. Measure; do not copy.
