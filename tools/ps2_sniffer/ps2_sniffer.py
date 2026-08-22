"""
ps2_sniffer.py — PS/2 pin finder and Synaptics pass-through probe (CircuitPython, Pico)
=======================================================================================

Two modes, selected by MODE below.

MODE = "find"
    Listens on each (clk, data) pair in CANDIDATE_PAIRS for standard 3-byte PS/2
    mouse packets while you move a finger on the ClickPad.  Finds CLK and DATA.

MODE = "synaptics"
    On the known CLK/DATA pair: resets the device, sends the Synaptics identify
    sequence, reads capabilities, switches to absolute + W mode, enables the
    pass-through guest, then decodes 6-byte packets for VERDICT_SECONDS.
    Push the TrackPoint with NO finger on the pad.  The verdict line says whether
    pass-through (W == 3) frames were seen.  That single observation decides the
    TrackPoint route — see docs/hardware/trackpoint.md.

Wiring: 4.7 kΩ pull-ups to 3V3 on CLK and DATA.  For the final build DATA is GP21
and CLK is GP22 (RP2040 PIO driver needs clock = data + 1); probing can use any pair.

Timing caveat: CircuitPython bit-bangs at tens of µs per operation and PS/2 clocks at
10–16 kHz, so reads are marginal.  If packets never decode, confirm the pins with a
logic analyser first; the Synaptics mode only needs a few good bytes to give a verdict.

Reference implementation for the protocol: Linux drivers/input/mouse/synaptics.c.
The pure functions at the top run on a host Python too (see tools/tests/).
"""

# --------------------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------------------

MODE = "find"                    # "find" or "synaptics"

# find mode: (clk_pin_name, data_pin_name) pairs to try, in order
CANDIDATE_PAIRS = (
    ("GP22", "GP21"),
    ("GP21", "GP22"),
    ("GP20", "GP19"),
    ("GP19", "GP20"),
)
PACKETS_PER_TRIAL = 5

# synaptics mode: the pair found above
CLK_PIN = "GP22"
DATA_PIN = "GP21"
VERDICT_SECONDS = 20

CLK_TIMEOUT_US = 5000

# PS/2 commands
CMD_RESET = 0xFF
CMD_ENABLE = 0xF4
CMD_DISABLE = 0xF5
CMD_SET_RATE = 0xF3
CMD_SET_RES = 0xE8
CMD_STATUS = 0xE9
ACK = 0xFA

# Synaptics queries (argument to the "special command" sequence)
SYN_QUERY_IDENTIFY = 0x00
SYN_QUERY_MODES = 0x01
SYN_QUERY_CAPABILITIES = 0x02
SYN_MAGIC = 0x47

SYN_MODE_ABSOLUTE = 0x80
SYN_MODE_RATE80 = 0x40
SYN_MODE_WMODE = 0x01
SYN_MODE = SYN_MODE_ABSOLUTE | SYN_MODE_RATE80 | SYN_MODE_WMODE      # 0xC1

SYN_RATE_SET_MODE = 0x14       # F3 0x14 after the special sequence = "set mode byte"
SYN_RATE_PASSTHROUGH = 0x28    # F3 0x28 after the special sequence = "send to guest"

# --------------------------------------------------------------------------------------
# Pure logic — unit-tested on the host
# --------------------------------------------------------------------------------------


def odd_parity(byte):
    """PS/2 uses odd parity: parity bit makes the total number of 1s odd."""
    ones = 0
    for i in range(8):
        ones += (byte >> i) & 1
    return 0 if ones % 2 else 1


def special_sequence(arg):
    """The Synaptics 'special command': four SetResolution commands whose 2-bit
    arguments spell out `arg`, most-significant pair first.  Returns the byte list
    to send (command, value, command, value, ...)."""
    seq = []
    for shift in (6, 4, 2, 0):
        seq.append(CMD_SET_RES)
        seq.append((arg >> shift) & 0x03)
    return seq


def decode_relative(b0, b1, b2):
    """Standard 3-byte PS/2 mouse packet -> (dx, dy, left, right, middle)."""
    dx = b1 - 256 if b0 & 0x10 else b1
    dy = b2 - 256 if b0 & 0x20 else b2
    return dx, dy, bool(b0 & 0x01), bool(b0 & 0x02), bool(b0 & 0x04)


def relative_packet_valid(b0):
    return bool(b0 & 0x08)


def abs_packet_valid(p):
    """Synaptics 'newabs' framing: byte0 & 0xC8 == 0x80 and byte3 & 0xC8 == 0xC0."""
    return len(p) == 6 and (p[0] & 0xC8) == 0x80 and (p[3] & 0xC8) == 0xC0


def abs_w(p):
    return ((p[0] & 0x30) >> 2) | ((p[0] & 0x04) >> 1) | ((p[3] & 0x04) >> 2)


def decode_absolute(p):
    """6-byte Synaptics absolute packet -> dict.  kind is 'guest' for a pass-through
    frame (W == 3), in which case 'guest' holds the embedded 3-byte PS/2 packet."""
    w = abs_w(p)
    if w == 3:
        return {"kind": "guest", "w": w, "guest": (p[1], p[4], p[5])}
    x = ((p[3] & 0x10) << 8) | ((p[1] & 0x0F) << 8) | p[4]
    y = ((p[3] & 0x20) << 7) | ((p[1] & 0xF0) << 4) | p[5]
    return {
        "kind": "touch", "w": w, "x": x, "y": y, "z": p[2],
        "left": bool(p[0] & 0x01), "right": bool(p[0] & 0x02),
    }


def capabilities(c0, c1, c2):
    """Decode the capabilities query bytes as Linux does (c = c0<<16 | c1<<8 | c2)."""
    return {
        "extended": bool(c0 & 0x80),
        "middle_button": bool(c0 & 0x04),
        "pass_through": bool(c2 & 0x80),
        "multi_finger": bool(c2 & 0x02),
        "palm_detect": bool(c2 & 0x01),
        "ext_queries": (c0 & 0x70) >> 4,
    }


def verdict(guest_frames, touch_frames, cap_pass_through, seconds):
    if guest_frames:
        return ("VERDICT: PASS-THROUGH FRAMES SEEN (%d guest, %d touch in %ds)\n"
                "         TrackPoint rides this PS/2 bus. No extra wiring. Firmware: decode W == 3."
                % (guest_frames, touch_frames, seconds))
    if not cap_pass_through:
        return ("VERDICT: NO pass-through frames, and the capability bit is CLEAR (%d touch frames).\n"
                "         This ClickPad has no guest port. TrackPoint is standalone: find its CLK/DATA\n"
                "         on the keyboard FPC -> GP20/GP19." % touch_frames)
    return ("VERDICT: NO pass-through frames in %ds although the capability bit is SET (%d touch frames).\n"
            "         Either the guest was not enabled (check the 0xF4 via pass-through step) or the\n"
            "         TrackPoint is not connected to this ClickPad. Retry; if still none, treat as standalone."
            % (seconds, touch_frames))


# --------------------------------------------------------------------------------------
# Hardware — CircuitPython only
# --------------------------------------------------------------------------------------

try:
    import board
    import digitalio
    import time
    ON_DEVICE = True
except ImportError:
    ON_DEVICE = False


class PS2Bus:
    """Bit-banged PS/2 host on two open-drain lines (external pull-ups)."""

    def __init__(self, clk_name, data_name):
        self.clk = digitalio.DigitalInOut(getattr(board, clk_name))
        self.data = digitalio.DigitalInOut(getattr(board, data_name))
        self.release(self.clk)
        self.release(self.data)

    @staticmethod
    def release(line):
        line.direction = digitalio.Direction.INPUT   # high via pull-up

    @staticmethod
    def pull_low(line):
        line.direction = digitalio.Direction.OUTPUT
        line.value = False

    def deinit(self):
        self.clk.deinit()
        self.data.deinit()

    # -- timing helpers --------------------------------------------------------------
    def _wait(self, line, level, timeout_us=CLK_TIMEOUT_US):
        deadline = time.monotonic_ns() + timeout_us * 1000
        while line.value != level:
            if time.monotonic_ns() > deadline:
                return False
        return True

    def _clock_pulse(self):
        """Wait for one falling edge of CLK (device-driven), return False on timeout."""
        if not self._wait(self.clk, True):
            return False
        return self._wait(self.clk, False)

    # -- device -> host ---------------------------------------------------------------
    def read_byte(self):
        if not self._wait(self.clk, False):
            return None                               # no start bit
        time.sleep(0.00002)
        if self.data.value:
            return None                               # framing error
        byte = 0
        for i in range(8):
            if not self._clock_pulse():
                return None
            time.sleep(0.00002)
            if self.data.value:
                byte |= 1 << i
        if not self._clock_pulse():                   # parity
            return None
        if not self._clock_pulse():                   # stop
            return None
        return byte

    # -- host -> device ---------------------------------------------------------------
    def write_byte(self, byte):
        """Host-to-device transmission.  Returns True if the device clocked all bits
        and sent its ACK bit."""
        self.pull_low(self.clk)
        time.sleep(0.00012)                           # >= 100 us request-to-send
        self.pull_low(self.data)                      # start bit
        self.release(self.clk)
        bits = [(byte >> i) & 1 for i in range(8)] + [odd_parity(byte), 1]
        for bit in bits:
            if not self._wait(self.clk, False):
                self.release(self.data)
                return False
            if bit:
                self.release(self.data)
            else:
                self.pull_low(self.data)
            if not self._wait(self.clk, True):
                self.release(self.data)
                return False
        self.release(self.data)
        # ACK: device pulls DATA low for one clock
        if not self._wait(self.data, False):
            return False
        if not self._wait(self.clk, False):
            return False
        self._wait(self.clk, True)
        self._wait(self.data, True)
        return True

    def command(self, byte, expect_ack=True):
        if not self.write_byte(byte):
            return None
        resp = self.read_byte()
        if expect_ack and resp != ACK:
            return None
        return resp

    def read_bytes(self, n):
        out = []
        for _ in range(n):
            b = self.read_byte()
            if b is None:
                return None
            out.append(b)
        return out


# -- find mode ---------------------------------------------------------------------------

def try_pair(clk_name, data_name):
    print("\nTrying CLK=%s DATA=%s — move a finger on the pad..." % (clk_name, data_name))
    bus = PS2Bus(clk_name, data_name)
    ok, attempts = 0, 0
    while ok < PACKETS_PER_TRIAL and attempts < 60:
        attempts += 1
        b0 = bus.read_byte()
        if b0 is None or not relative_packet_valid(b0):
            time.sleep(0.1)
            continue
        b1 = bus.read_byte()
        b2 = bus.read_byte()
        if b1 is None or b2 is None:
            continue
        dx, dy, l, r, m = decode_relative(b0, b1, b2)
        print("  PKT dx=%+4d dy=%+4d L=%d R=%d M=%d" % (dx, dy, l, r, m))
        ok += 1
    bus.deinit()
    if ok >= PACKETS_PER_TRIAL:
        print("\n  FOUND: CLK=%s DATA=%s" % (clk_name, data_name))
        print("  Record in x240_clickpad_fpc_pinout.md; for the build use DATA=GP21, CLK=GP22.")
        return True
    print("  no valid packets")
    return False


def find_mode():
    print("\n=== x240-kbd PS/2 sniffer — find mode (%d pairs) ===" % len(CANDIDATE_PAIRS))
    for clk, data in CANDIDATE_PAIRS:
        if try_pair(clk, data):
            return
    print("\nNo PS/2 traffic on any pair. Check VCC/GND, the 4.7 kΩ pull-ups, and add pairs.")


# -- synaptics mode -------------------------------------------------------------------------

def syn_query(bus, q):
    for b in special_sequence(q):
        if bus.command(b) is None:
            return None
    if bus.command(CMD_STATUS) is None:
        return None
    return bus.read_bytes(3)


def syn_set_mode(bus, mode):
    for b in special_sequence(mode):
        if bus.command(b) is None:
            return False
    return bus.command(CMD_SET_RATE) is not None and bus.command(SYN_RATE_SET_MODE) is not None


def syn_pt_write(bus, byte):
    """Send one byte to the pass-through guest (special sequence + SetRate 0x28)."""
    for b in special_sequence(byte):
        if bus.command(b) is None:
            return False
    return bus.command(CMD_SET_RATE) is not None and bus.command(SYN_RATE_PASSTHROUGH) is not None


def synaptics_mode():
    print("\n=== x240-kbd PS/2 sniffer — Synaptics mode on CLK=%s DATA=%s ===" % (CLK_PIN, DATA_PIN))
    bus = PS2Bus(CLK_PIN, DATA_PIN)

    print("reset...")
    if bus.command(CMD_RESET) is None:
        print("FAIL: no ACK to reset. Check pins, pull-ups, power.")
        return
    bat = bus.read_bytes(2)
    print("  BAT: %s (expect [0xAA, 0x00])" % bat)
    bus.command(CMD_DISABLE)

    ident = syn_query(bus, SYN_QUERY_IDENTIFY)
    print("identify: %s" % ident)
    if not ident or ident[1] != SYN_MAGIC:
        print("FAIL: not a Synaptics device (byte 1 is not 0x47). Plain PS/2 relative mode only.")
        bus.deinit()
        return
    print("  Synaptics OK — model %d.%d" % (ident[2] & 0x0F, ident[0]))

    caps_raw = syn_query(bus, SYN_QUERY_CAPABILITIES)
    caps = capabilities(*caps_raw) if caps_raw else {}
    print("capabilities: %s -> %s" % (caps_raw, caps))

    print("set mode 0x%02X (absolute, rate 80, W mode)..." % SYN_MODE)
    if not syn_set_mode(bus, SYN_MODE):
        print("FAIL: mode byte not accepted")
        bus.deinit()
        return

    if caps.get("pass_through"):
        print("enable guest streaming via pass-through (0xF4)...")
        print("  %s" % ("ok" if syn_pt_write(bus, CMD_ENABLE) else "no ACK — guest may be absent"))

    bus.command(CMD_ENABLE)
    print("\nStreaming for %ds. Push the TrackPoint with NO finger on the pad.\n" % VERDICT_SECONDS)

    guest, touch, junk = 0, 0, 0
    buf = []
    deadline = time.monotonic() + VERDICT_SECONDS
    while time.monotonic() < deadline:
        b = bus.read_byte()
        if b is None:
            continue
        buf.append(b)
        if len(buf) < 6:
            continue
        if not abs_packet_valid(buf):
            buf.pop(0)                                 # resync one byte at a time
            junk += 1
            continue
        pkt = decode_absolute(buf)
        buf = []
        if pkt["kind"] == "guest":
            guest += 1
            dx, dy, l, r, m = decode_relative(*pkt["guest"])
            print("  GUEST  dx=%+4d dy=%+4d L=%d R=%d" % (dx, dy, l, r))
        else:
            touch += 1
            if touch % 10 == 1:
                print("  TOUCH  x=%4d y=%4d z=%3d w=%d L=%d R=%d"
                      % (pkt["x"], pkt["y"], pkt["z"], pkt["w"], pkt["left"], pkt["right"]))

    bus.command(CMD_DISABLE)
    bus.deinit()
    print("\n(%d bytes discarded while resyncing)" % junk)
    print(verdict(guest, touch, caps.get("pass_through", False), VERDICT_SECONDS))
    print("Record the verdict in hardware/pinout/x240_clickpad_fpc_pinout.md.")


def main():
    if MODE == "find":
        find_mode()
    elif MODE == "synaptics":
        synaptics_mode()
    else:
        print("MODE must be 'find' or 'synaptics'")


if ON_DEVICE:
    main()
