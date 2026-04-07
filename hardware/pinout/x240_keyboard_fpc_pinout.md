# X240 Keyboard FPC Pinout

**Part:** 0C44020 / SG-58950-XUA  
**Connector:** 40-pin ZIF, 0.5 mm pitch  
**Status:** Template — fill in verified data after Phase 1 probing

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

| Signal | FPC Pins | Pico GPIOs |
|--------|----------|------------|
| Row 0  |          | GP0        |
| Row 1  |          | GP1        |
| Row 2  |          | GP2        |
| Row 3  |          | GP3        |
| Row 4  |          | GP4        |
| Row 5  |          | GP5        |
| Row 6  |          | GP6        |
| Row 7  |          | GP7        |
| Col 0  |          | GP8        |
| Col 1  |          | GP9        |
| Col 2  |          | GP10       |
| Col 3  |          | GP11       |
| Col 4  |          | GP12       |
| Col 5  |          | GP13       |
| Col 6  |          | GP14       |
| Col 7  |          | GP15       |
| Col 8  |          | GP16       |
| Col 9  |          | GP17       |
| Col 10 |          | GP18       |
| Col 11 |          | GP19       |
| Col 12 |          | GP20       |
| GND    |          | GND        |
| VCC    |          | 3V3        |
| BL+    |          | via MOSFET |
| BL-    |          | GND        |
| PWR BTN|          | GP27       |

---

## Key → Matrix Cell Map (fill after probing)

| Key       | Row | Col |
|-----------|-----|-----|
| Esc       |     |     |
| F1        |     |     |
| F2        |     |     |
| F3        |     |     |
| F4        |     |     |
| F5        |     |     |
| F6        |     |     |
| F7        |     |     |
| F8        |     |     |
| F9        |     |     |
| F10       |     |     |
| F11       |     |     |
| F12       |     |     |
| `         |     |     |
| 1         |     |     |
| 2         |     |     |
| 3         |     |     |
| 4         |     |     |
| 5         |     |     |
| 6         |     |     |
| 7         |     |     |
| 8         |     |     |
| 9         |     |     |
| 0         |     |     |
| -         |     |     |
| =         |     |     |
| Tab       |     |     |
| Q         |     |     |
| W         |     |     |
| E         |     |     |
| R         |     |     |
| T         |     |     |
| Y         |     |     |
| U         |     |     |
| I         |     |     |
| O         |     |     |
| P         |     |     |
| [         |     |     |
| ]         |     |     |
| CapsLock  |     |     |
| A         |     |     |
| S         |     |     |
| D         |     |     |
| F         |     |     |
| G         |     |     |
| H         |     |     |
| J         |     |     |
| K         |     |     |
| L         |     |     |
| ;         |     |     |
| '         |     |     |
| Backspace |     |     |
| LShift    |     |     |
| Z         |     |     |
| X         |     |     |
| C         |     |     |
| V         |     |     |
| B         |     |     |
| N         |     |     |
| M         |     |     |
| ,         |     |     |
| .         |     |     |
| /         |     |     |
| RShift    |     |     |
| PgUp      |     |     |
| LCtrl     |     |     |
| Win       |     |     |
| LAlt      |     |     |
| Space     |     |     |
| RAlt      |     |     |
| Menu      |     |     |
| RCtrl     |     |     |
| PgDn      |     |     |
| Ins       |     |     |
| Del       |     |     |
| Home      |     |     |
| End       |     |     |
| Up        |     |     |
| Left      |     |     |
| Down      |     |     |
| Right     |     |     |
| PrtSc     |     |     |
| ScrLk     |     |     |
| Pause     |     |     |
| \         |     |     |
| Enter     |     |     |
| FN        |     |     |

---

## References for Cross-Checking

Before probing, cross-reference with community documentation:

- `hamishcoleman/thinkpad-usbkb` — `keyboard-thinkpad.pinout.txt`
- `thedalles77/USB_Laptop_Keyboard_Controller` — T61 and X-series examples
- ThinkPad X240 Hardware Maintenance Manual (Lenovo, freely available)
