# X240 ClickPad FPC Pinout

**Device:** Synaptics ClickPad (ThinkPad X240)  
**Protocol:** PS/2  
**Connector:** 0.5 mm pitch ZIF, 6–12 pins (count varies — measure yours)  
**Status:** Template — fill in verified data after Phase 1 probing

---

## Pin Map

| Pin | Function   | Pico GPIO | Notes                              |
|-----|------------|-----------|------------------------------------|
| 1   | ?          |           |                                    |
| 2   | ?          |           |                                    |
| 3   | ?          |           |                                    |
| 4   | ?          |           |                                    |
| 5   | ?          |           |                                    |
| 6   | ?          |           |                                    |
| 7   | (if >6)    |           |                                    |
| 8   | (if >7)    |           |                                    |

---

## Identified Signals (fill after probing)

| Signal      | FPC Pin | Pico GPIO | Notes                              |
|-------------|---------|-----------|-------------------------------------|
| VCC         |         | 3V3       | Typically 3.3 V; verify before connecting |
| GND         |         | GND       |                                     |
| PS/2 CLK    |         | GP21      | 4.7 kΩ pull-up to 3.3 V required   |
| PS/2 DATA   |         | GP22      | 4.7 kΩ pull-up to 3.3 V required   |
| LED anode   |         | GP28      | Via 100 Ω resistor                  |
| LED cathode |         | GND       |                                     |

---

## Notes

- The Synaptics ClickPad powers up in standard PS/2 mouse mode automatically.
  No special initialisation sequence is needed for basic cursor + click operation.
- Advanced Synaptics features (multi-touch gestures, extended reports) require
  proprietary PS/2 escape sequences not implemented in QMK — standard PS/2 mode
  gives relative X/Y movement and left/right button clicks, which is sufficient.
- The X240 ClickPad physical left/right areas (top of pad for TrackPoint buttons,
  bottom corners for click) are reported as PS/2 button 1 and button 2 by the
  Synaptics firmware internally.
- If VCC on your touchpad is 5 V (uncommon on X240 but possible on some revisions),
  add a 3.3 V → 5 V level shifter on CLK and DATA lines.
