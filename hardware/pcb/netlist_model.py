"""
netlist_model.py — the Rev B board as data: parts, library names, and nets.

Both generators consume this (gen_schematic.py writes the .kicad_sch, gen_pcb.py writes
the .kicad_pcb), so the schematic and the board agree by construction.

Design decision (see docs/hardware/pcb.md): which of the keyboard FPC's 40 lines are
drive, sense, VCC, GND, backlight or power button is unknown until probing (#28), and
the ClickPad's pin count until #29.  Rev B therefore brings every FPC line to a 0.1"
header (J_KB, J_TP) and every matrix/bus signal to a header beside it (J_MAT, J_PS2);
the assignment is made with jumper wires once measured.  A later revision hard-routes it.
"""

# ----------------------------------------------------------------- library names
# symbol  -> "Library:Symbol" in /usr/share/kicad/symbols
# footprint -> "Library:Footprint" in /usr/share/kicad/footprints
LIB = {
    "pico":      ("MCU_Module:RaspberryPi_Pico", "Module:RaspberryPi_Pico_Common_THT"),
    "hc165":     ("74xx:74HC165", "Package_SO:TSSOP-16_4.4x5mm_P0.65mm"),
    "fpc40":     ("Connector_Generic:Conn_01x40", "Connector_FFC-FPC:Hirose_FH12-40S-0.5SH_1x40-1MP_P0.50mm_Horizontal"),
    "fpc12":     ("Connector_Generic:Conn_01x12", "Connector_FFC-FPC:Hirose_FH12-12S-0.5SH_1x12-1MP_P0.50mm_Horizontal"),
    "hdr2x20":   ("Connector_Generic:Conn_02x20_Odd_Even", "Connector_PinHeader_2.54mm:PinHeader_2x20_P2.54mm_Vertical"),
    "hdr2x17":   ("Connector_Generic:Conn_02x17_Odd_Even", "Connector_PinHeader_2.54mm:PinHeader_2x17_P2.54mm_Vertical"),
    "hdr1x12":   ("Connector_Generic:Conn_01x12", "Connector_PinHeader_2.54mm:PinHeader_1x12_P2.54mm_Vertical"),
    "hdr1x08":   ("Connector_Generic:Conn_01x08", "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical"),
    "hdr1x04":   ("Connector_Generic:Conn_01x04", "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical"),
    "hdr1x03":   ("Connector_Generic:Conn_01x03", "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical"),
    "nmos":      ("Transistor_FET:2N7002", "Package_TO_SOT_SMD:SOT-23"),
    "rpack4":    ("Device:R_Pack04", "Resistor_SMD:R_Array_Convex_4x0603"),
    "r":         ("Device:R", "Resistor_SMD:R_0603_1608Metric"),
    "c":         ("Device:C", "Capacitor_SMD:C_0603_1608Metric"),
    "c_bulk":    ("Device:C", "Capacitor_SMD:C_0805_2012Metric"),
    "sw":        ("Switch:SW_Push", "Button_Switch_THT:SW_PUSH_6mm"),
    "sj3":       ("Jumper:SolderJumper_3_Open", "Jumper:SolderJumper-3_P1.3mm_Open_RoundedPad1.0x1.5mm"),
    "hole_m2":   (None, "MountingHole:MountingHole_2.2mm_M2"),
    "hole_m25":  (None, "MountingHole:MountingHole_2.7mm_M2.5"),
}

# ----------------------------------------------------------------- parts
# (ref, kind, value)
PARTS = [
    ("U1",  "pico",   "Raspberry_Pi_Pico"),
    ("U2",  "hc165",  "74HC165"), ("U3", "hc165", "74HC165"), ("U4", "hc165", "74HC165"),
    ("J1",  "fpc40",  "FH12-40S keyboard FPC"),
    ("J2",  "fpc12",  "FH12-12S ClickPad FPC"),
    ("J3",  "hdr2x20","J_KB  FPC lines 1-40"),
    ("J4",  "hdr2x17","J_MAT drive/sense/aux"),
    ("J5",  "hdr1x12","J_TP  ClickPad lines 1-12"),
    ("J6",  "hdr1x08","J_PS2 bus/aux"),
    ("J7",  "hdr1x04","J_USBC TP1/TP2/TP3/VBUS"),
    ("J8",  "hdr1x03","J_LED  3V3/GP28R/GND"),
    ("Q1",  "nmos",   "2N7002"),
    ("RN1", "rpack4", "10k"), ("RN2", "rpack4", "10k"), ("RN3", "rpack4", "10k"),
    ("RN4", "rpack4", "10k"), ("RN5", "rpack4", "10k"), ("RN6", "rpack4", "10k"),
    ("R1",  "r", "4.7k"), ("R2", "r", "4.7k"),          # PS/2 pull-ups, bus 1
    ("R3",  "r", "DNP 4.7k"), ("R4", "r", "DNP 4.7k"),  # PS/2 pull-ups, fallback bus
    ("R5",  "r", "10k"), ("R6", "r", "100k"),          # MOSFET gate series / pull-down
    ("R7",  "r", "100R"),                               # backlight series (value by measurement)
    ("R8",  "r", "100R"), ("R9", "r", "100R"),          # GP27 series, LED series
    ("C1",  "c", "100n"), ("C2", "c", "100n"), ("C3", "c", "100n"), ("C4", "c", "100n"),
    ("C5",  "c_bulk", "10u"),
    ("SW1", "sw", "RESET"),
    ("JP1", "sj3", "BL supply 3V3/VBUS"),
    ("H1",  "hole_m2", ""), ("H2", "hole_m2", ""), ("H3", "hole_m2", ""), ("H4", "hole_m2", ""),
    ("H5",  "hole_m25", ""), ("H6", "hole_m25", ""), ("H7", "hole_m25", ""),
]

# ----------------------------------------------------------------- Pico pin map (symbol pin numbers = header pins 1..40)
PICO = {
    "GP0": 1, "GP1": 2, "GND1": 3, "GP2": 4, "GP3": 5, "GP4": 6, "GP5": 7, "GND2": 8, "GP6": 9, "GP7": 10,
    "GP8": 11, "GP9": 12, "GND3": 13, "GP10": 14, "GP11": 15, "GP12": 16, "GP13": 17, "GND4": 18, "GP14": 19, "GP15": 20,
    "GP16": 21, "GP17": 22, "GND5": 23, "GP18": 24, "GP19": 25, "GP20": 26, "GP21": 27, "GND6": 28, "GP22": 29, "RUN": 30,
    "GP26": 31, "GP27": 32, "GND7": 33, "GP28": 34, "ADC_VREF": 35, "3V3": 36, "3V3_EN": 37, "GND8": 38, "VSYS": 39, "VBUS": 40,
}

# ----------------------------------------------------------------- nets: name -> [(ref, pin), ...]
NETS = {}
def net(name, *pins):
    NETS.setdefault(name, []).extend(pins)

# power
# Pico pin 33 is AGND, a second "power output" in the symbol; tying it to GND trips ERC
# (power output to power output) and it is the same ground inside the module anyway.
for g in ("GND1", "GND2", "GND3", "GND4", "GND5", "GND6", "GND8"):
    net("GND", ("U1", PICO[g]))
net("+3V3", ("U1", PICO["3V3"]), ("C5", 1)); net("GND", ("C5", 2))
net("VBUS", ("U1", PICO["VBUS"]))
for u, c in (("U2", "C1"), ("U3", "C2"), ("U4", "C3")):
    net("+3V3", (u, 16), (c, 1)); net("GND", (u, 8), (c, 2))
    net("GND", (u, 15))                      # CE (pin 15 on 74HC165) tied low
net("+3V3", ("C4", 1)); net("GND", ("C4", 2))

# drive lines GP0..GP9 -> J_MAT odd pins 1..19
for i in range(10):
    net(f"DRV{i}", ("U1", PICO[f"GP{i}"]), ("J4", 2 * i + 1))

# sense chain: 74HC165 D0..D7 pins = 11,12,13,14,3,4,5,6 ; SH/LD(PL)=1, CLK=2, CLK_INH=15, SER(DS)=10, QH(Q7)=9, /QH=7
D_PINS = [11, 12, 13, 14, 3, 4, 5, 6]
chain = [("U2", "RN1", "RN2"), ("U3", "RN3", "RN4"), ("U4", "RN5", "RN6")]
sense = 0
for u, rna, rnb in chain:
    for k, dpin in enumerate(D_PINS):
        rn, el = (rna, k) if k < 4 else (rnb, k - 4)
        # R_Pack04: isolated resistors, pins (1,8) (2,7) (3,6) (4,5)
        net(f"SENSE{sense}", (u, dpin), (rn, el + 1), ("J4", 2 * (sense + 1) if sense < 10 else 20 + 2 * (sense - 10) + 1 if sense < 17 else 34 - 0))  # placeholder, fixed below
        net("+3V3", (rn, 8 - el))
        sense += 1
# J_MAT pin plan (2x17 = 34 pins): odd 1..19 = DRV0..9 ; even 2..20 = SENSE0..9 ; 21..34 = SENSE10..23
# rebuild the J4 assignment cleanly:
for name in list(NETS):
    if name.startswith("SENSE"):
        NETS[name] = [p for p in NETS[name] if p[0] != "J4"]
for s in range(24):
    pin = 2 * (s + 1) if s < 10 else 21 + (s - 10)
    net(f"SENSE{s}", ("J4", pin))
# chain control
net("SENSE_PL", ("U1", PICO["GP17"]), ("U2", 1), ("U3", 1), ("U4", 1))
net("SENSE_CP", ("U1", PICO["GP18"]), ("U2", 2), ("U3", 2), ("U4", 2))
net("SENSE_Q7", ("U1", PICO["GP16"]), ("U2", 9))
net("CHAIN_23", ("U3", 9), ("U2", 10))
net("CHAIN_34", ("U4", 9), ("U3", 10))
net("GND", ("U4", 10))

# keyboard FPC: J1 pin n -> J_KB (2x20) pin n
for n in range(1, 41):
    net(f"KB{n}", ("J1", n), ("J3", n))
# ClickPad FPC: J2 pin n -> J_TP pin n
for n in range(1, 13):
    net(f"TP{n}", ("J2", n), ("J5", n))

# PS/2 bus 1 (GP21 DATA, GP22 CLK) with pull-ups; fallback bus (GP19 DATA, GP20 CLK) DNP pull-ups
net("PS2_DATA", ("U1", PICO["GP21"]), ("R1", 1), ("J6", 3))
net("PS2_CLK",  ("U1", PICO["GP22"]), ("R2", 1), ("J6", 4))
net("+3V3", ("R1", 2), ("R2", 2), ("R3", 2), ("R4", 2), ("J6", 1))
net("GND", ("J6", 2))
net("PS2B_DATA", ("U1", PICO["GP19"]), ("R3", 1), ("J6", 5))
net("PS2B_CLK",  ("U1", PICO["GP20"]), ("R4", 1), ("J6", 6))
# touchpad LED: GP28 -> R9 -> J8.2 ; J8.1 = 3V3, J8.3 = GND
net("GP28", ("U1", PICO["GP28"]), ("R9", 1))
net("LED_A", ("R9", 2), ("J8", 2), ("J6", 7))
net("+3V3", ("J8", 1)); net("GND", ("J8", 3)); net("GND", ("J6", 8))

# backlight: GP26 -> R5 -> gate ; R6 gate->GND ; drain = BL- ; source GND ; JP1 selects 3V3/VBUS -> R7 -> BL+
net("GP26", ("U1", PICO["GP26"]), ("R5", 1))
net("BL_GATE", ("R5", 2), ("R6", 1), ("Q1", 1))      # 2N7002 symbol: 1=G, 2=S, 3=D
net("GND", ("R6", 2), ("Q1", 2))
net("BL_N", ("Q1", 3), ("J4", 31))
net("+3V3", ("JP1", 1)); net("VBUS", ("JP1", 3)); net("BL_SUP", ("JP1", 2), ("R7", 1))
net("BL_P", ("R7", 2), ("J4", 32))
# power button: GP27 -> R8 -> J_MAT ; GND and 3V3 on J_MAT for the keyboard
net("GP27", ("U1", PICO["GP27"]), ("R8", 1))
net("PWR_BTN", ("R8", 2), ("J4", 33))
net("GND", ("J4", 34))
# J_MAT pins 21..34: SENSE10..23 occupy 21..34?  No: 21..30 = SENSE10..19 (10 pins), then BL_N 31, BL_P 32, PWR 33, GND 34.
# SENSE20..23 therefore go to J6? -> keep the matrix header honest: move them to a second row.
for s in range(20, 24):
    NETS[f"SENSE{s}"] = [p for p in NETS[f"SENSE{s}"] if p[0] != "J4"]
# reset and USB-C pads
net("RUN", ("U1", PICO["RUN"]), ("SW1", 1)); net("GND", ("SW1", 2))
net("VBUS", ("J7", 4)); net("GND", ("J7", 1))
net("USB_DM", ("J7", 2)); net("USB_DP", ("J7", 3))   # wired to the Pico's TP2/TP3 pads by hand (not on the header footprint)

# unconnected Pico pins get no-connect flags in the schematic
PICO_NC = ["GP10", "GP11", "GP12", "GP13", "GP14", "GP15", "ADC_VREF", "3V3_EN", "VSYS", "GND7"]   # GND7 = AGND, see above
