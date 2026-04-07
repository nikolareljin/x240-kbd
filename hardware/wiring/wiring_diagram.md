# Wiring Diagram

Complete GPIO-to-FPC wiring reference for the perfboard adapter.

---

## GPIO Allocation Table

| Pico GPIO | Pin# | Function              | Direction | Notes                              |
|-----------|------|-----------------------|-----------|------------------------------------|
| GP0       | 1    | Matrix Row 0          | Output    | Driven LOW during row scan         |
| GP1       | 2    | Matrix Row 1          | Output    |                                    |
| GP2       | 3    | Matrix Row 2          | Output    |                                    |
| GP3       | 4    | Matrix Row 3          | Output    |                                    |
| GP4       | 5    | Matrix Row 4          | Output    |                                    |
| GP5       | 6    | Matrix Row 5          | Output    |                                    |
| GP6       | 7    | Matrix Row 6          | Output    |                                    |
| GP7       | 8    | Matrix Row 7          | Output    |                                    |
| GP8       | 11   | Matrix Col 0          | Input     | Internal pull-up enabled           |
| GP9       | 12   | Matrix Col 1          | Input     |                                    |
| GP10      | 14   | Matrix Col 2          | Input     |                                    |
| GP11      | 15   | Matrix Col 3          | Input     |                                    |
| GP12      | 16   | Matrix Col 4          | Input     |                                    |
| GP13      | 17   | Matrix Col 5          | Input     |                                    |
| GP14      | 19   | Matrix Col 6          | Input     |                                    |
| GP15      | 20   | Matrix Col 7          | Input     |                                    |
| GP16      | 21   | Matrix Col 8          | Input     |                                    |
| GP17      | 22   | Matrix Col 9          | Input     |                                    |
| GP18      | 24   | Matrix Col 10         | Input     |                                    |
| GP19      | 25   | Matrix Col 11         | Input     |                                    |
| GP20      | 26   | Matrix Col 12         | Input     |                                    |
| GP21      | 27   | PS/2 CLK (UART0)      | Bidir     | 4.7 kΩ pull-up to 3.3 V           |
| GP22      | 29   | PS/2 DATA (UART0)     | Bidir     | 4.7 kΩ pull-up to 3.3 V           |
| GP26      | 31   | Backlight PWM         | Output    | To 2N7002 MOSFET gate              |
| GP27      | 32   | Power button          | Input     | Internal pull-up; active LOW       |
| GP28      | 34   | Touchpad LED          | Output    | HIGH = LED on, via 100 Ω resistor  |
| 3V3       | 36   | 3.3 V rail            | Supply    | Powers touchpad + pull-ups         |
| GND       | 38   | Ground                | Supply    |                                    |
| VBUS      | 40   | 5 V from USB          | Supply    | Available if backlight needs 5 V   |

*Pico Pin# refers to the physical pin number on the 40-pin header.*

---

## ASCII Schematic

```
                         RASPBERRY PI PICO
                    ┌────────────────────────┐
            GP0 ───│1                      40│─── VBUS (5V USB)
            GP1 ───│2                      39│─── VSYS
            GP2 ───│3  Row 0-7             38│─── GND ──────────────── GND rail
            GP3 ───│4  (driven LOW         37│─── 3V3_EN
            GP4 ───│5  during scan)        36│─── 3V3 ──┬─── Touchpad VCC
            GP5 ───│6                      35│─── ADC_VRef   │
            GP6 ───│7                      34│─── GP28 ──┤── 100Ω ── LED(+)
            GP7 ───│8                      33│─── GND        │              LED(-)─── GND
                   │9  GND                 32│─── GP27 ──── Power button FPC pin
                   │10 GND                 31│─── GP26 ──── 10kΩ ──┬── MOSFET Gate
            GP8 ───│11 Col 0               30│─── RUN              │
            GP9 ───│12 Col 1               29│─── GP22 ──── 4.7kΩ ─┤─── PS/2 DATA
                   │13 GND                 28│─── GND              │
           GP10 ───│14 Col 2               27│─── GP21 ──── 4.7kΩ ─┘─── PS/2 CLK
           GP11 ───│15 Col 3               26│─── GP16         │
           GP12 ───│16 Col 4               25│─── GP19    [4.7kΩ pull-ups connect
           GP13 ───│17 Col 5               24│─── GP18     to 3V3 rail]
                   │18 GND                 23│─── GND
           GP14 ───│19 Col 6               22│─── GP17
           GP15 ───│20 Col 7               21│─── GP16
                   └────────────────────────┘

   MOSFET Backlight Circuit (2N7002 SOT-23):
   ───────────────────────────────────────────
   GP26 ─── 10 kΩ ─── Gate
                       Drain ─── LED strip cathode (–)
                       Source ── GND
   Gate ─── 100 kΩ ─── GND    (pull-down; prevents false trigger at boot)
   3V3  ─── 100 Ω  ─── LED strip anode (+)

   PS/2 Touchpad:
   ──────────────
   3V3 ────────────── Touchpad VCC
   GND ────────────── Touchpad GND
   GP21 ─┬─ 4.7kΩ ─ 3V3
         └─────────── Touchpad CLK
   GP22 ─┬─ 4.7kΩ ─ 3V3
         └─────────── Touchpad DATA

   Power Button:
   ─────────────
   GP27 ──────────── Power button FPC pin  (other side of button → GND via matrix)
   (Pico internal pull-up keeps GP27 HIGH; button pulls it LOW when pressed)

   Touchpad LED:
   ─────────────
   GP28 ─── 100 Ω ─── LED anode (+)
                       LED cathode (–) ─── GND
```

---

## Keyboard FPC to Breakout to Pico

After completing Phase 1 probing, fill the table below with the actual FPC pin
numbers that correspond to each matrix row/column:

| Signal  | FPC Pin | Breakout Pad | Pico GPIO |
|---------|---------|--------------|-----------|
| Row 0   |         |              | GP0       |
| Row 1   |         |              | GP1       |
| Row 2   |         |              | GP2       |
| Row 3   |         |              | GP3       |
| Row 4   |         |              | GP4       |
| Row 5   |         |              | GP5       |
| Row 6   |         |              | GP6       |
| Row 7   |         |              | GP7       |
| Col 0   |         |              | GP8       |
| Col 1   |         |              | GP9       |
| Col 2   |         |              | GP10      |
| Col 3   |         |              | GP11      |
| Col 4   |         |              | GP12      |
| Col 5   |         |              | GP13      |
| Col 6   |         |              | GP14      |
| Col 7   |         |              | GP15      |
| Col 8   |         |              | GP16      |
| Col 9   |         |              | GP17      |
| Col 10  |         |              | GP18      |
| Col 11  |         |              | GP19      |
| Col 12  |         |              | GP20      |
| GND     |         |              | GND       |
| VCC     |         |              | 3V3       |
| BL+     |         |              | MOSFET D  |
| PWR BTN |         |              | GP27      |
