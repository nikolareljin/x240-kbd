# X240 ClickPad FPC Pinout

**Device:** Synaptics ClickPad (ThinkPad X240)  
**Protocol:** PS/2  
**Connector:** 0.5 mm pitch ZIF, 6–12 pins (count varies — measure yours)  
**Status:** Template — fill in verified data after Phase 1 probing (milestone M2, issue #29)

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
| PS/2 DATA   |         | GP21      | 4.7 kΩ pull-up to 3.3 V required   |
| PS/2 CLK    |         | GP22      | 4.7 kΩ pull-up to 3.3 V required; CLK = DATA + 1 for the PIO driver |
| LED anode   |         | GP28      | Via 100 Ω resistor                  |
| LED cathode |         | GND       |                                     |

---

## TrackPoint route (fill after probing)

With `tools/ps2_sniffer/ps2_sniffer.py` in Synaptics mode, push the stick with no finger on the pad.

| Observation | Result |
|---|---|
| Pass-through frames (`W == 3`) seen | ☐ yes → TrackPoint rides this bus; no extra wiring |
| No pass-through frames | ☐ → TrackPoint is standalone; record its CLK/DATA (keyboard FPC) → GP20/GP19 |
| Synaptics identify byte 1 | `0x__` (expect `0x47`) |
| Capabilities: PassThrough bit | ☐ set / ☐ clear |

## Notes

- The ClickPad's **top-edge zone** acts as the TrackPoint buttons and the bottom corners as
  the touchpad buttons; all arrive in the touchpad packet's L/R bits, not in the guest frame.
- Standard PS/2 relative mode gives cursor + clicks only. **Absolute mode with pass-through
  is required for the TrackPoint** — see `docs/hardware/trackpoint.md`.

- The Synaptics ClickPad powers up in standard PS/2 mouse mode automatically.
  No special initialisation sequence is needed for basic cursor + click operation.
- Multi-touch gestures are out of scope; absolute mode is used only to reach the
  pass-through port and to derive single-finger deltas.
- If VCC on your touchpad is 5 V (uncommon on X240 but possible on some revisions),
  add a 3.3 V → 5 V level shifter on CLK and DATA lines.
