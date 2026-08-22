"""
shift_register_test.py — 74HC165 sense-chain self-test (CircuitPython, Raspberry Pi Pico)
==========================================================================================

Verifies the three-chip 74HC165 chain BEFORE any keyboard FPC is connected.

Wiring under test (hardware/wiring/wiring_diagram.md):
    GP17 -> PL  (parallel load, active LOW) on all three chips
    GP18 -> CP  (clock)                      on all three chips   = SPI0 SCK
    GP16 <- Q7  of U1                                              = SPI0 RX
    U2.Q7 -> U1.DS,  U3.Q7 -> U2.DS,  U3.DS -> GND,  CE -> GND on all
    every D input pulled up to 3V3 through the 10 kΩ SIP networks

What you should see
-------------------
With nothing grounded every sense line reads HIGH:   24 x '1'.
Touch a ground wire to an input and exactly ONE bit goes '0' — its index must match the
sense number printed next to it (S0 = U1.D0 ... S23 = U3.D7).

Modes (MODE below):
    "watch"  — prints the pattern whenever it changes.  Ground inputs at will.
    "walk"   — prompts S0..S23 in order and checks each one; reports wiring swaps.

The pure functions at the top run on a host Python too (see tools/tests/).
"""

MODE = "watch"

PL_PIN = "GP17"
SCK_PIN = "GP18"
MISO_PIN = "GP16"
CHIPS = 3
SPI_HZ = 8_000_000

# --------------------------------------------------------------------------------------
# Pure logic — unit-tested on the host
# --------------------------------------------------------------------------------------


def sense_index(byte_i, bit):
    """Sense-line number for bit `bit` (0..7, MSB first off the wire = 7) of the
    `byte_i`-th byte clocked out.  Byte 0 is U1, whose D7 is the first bit on the wire."""
    return byte_i * 8 + bit


def decode_chain(raw):
    """bytes from the chain -> list of 8*len(raw) booleans, index = sense line, True = HIGH."""
    levels = [True] * (8 * len(raw))
    for byte_i, value in enumerate(raw):
        for bit in range(8):
            levels[sense_index(byte_i, bit)] = bool((value >> bit) & 1)
    return levels


def low_lines(levels):
    return [i for i, high in enumerate(levels) if not high]


def pattern(levels):
    """Human string, S23 on the left down to S0 on the right, grouped per chip."""
    groups = []
    for chip in range(len(levels) // 8 - 1, -1, -1):
        bits = "".join("1" if levels[chip * 8 + b] else "0" for b in range(7, -1, -1))
        groups.append("U%d:%s" % (chip + 1, bits))
    return "  ".join(groups)


def diagnose(expected, got):
    """Explain a mismatch during the walk test."""
    if not got:
        return "nothing went LOW — S%d not wired, or its pull-up network is missing" % expected
    if len(got) > 1:
        return "%s went LOW together — adjacent inputs shorted" % ["S%d" % g for g in got]
    g = got[0]
    if g // 8 != expected // 8:
        return "S%d read as S%d — chip order wrong (Q7 -> DS cascade crossed)" % (expected, g)
    if g == 7 - (expected % 8) + (expected // 8) * 8:
        return "S%d read as S%d — D0..D7 wired in reverse on U%d" % (expected, g, expected // 8 + 1)
    return "S%d read as S%d — wires swapped" % (expected, g)


# --------------------------------------------------------------------------------------
# Hardware — CircuitPython only
# --------------------------------------------------------------------------------------

try:
    import board
    import busio
    import digitalio
    import time
    ON_DEVICE = True
except ImportError:
    ON_DEVICE = False


class Chain:
    def __init__(self):
        self.pl = digitalio.DigitalInOut(getattr(board, PL_PIN))
        self.pl.direction = digitalio.Direction.OUTPUT
        self.pl.value = True
        self.spi = busio.SPI(clock=getattr(board, SCK_PIN), MISO=getattr(board, MISO_PIN))
        while not self.spi.try_lock():
            pass
        self.spi.configure(baudrate=SPI_HZ, polarity=0, phase=0)
        self.buf = bytearray(CHIPS)

    def read(self):
        self.pl.value = False          # latch all inputs
        self.pl.value = True           # (CircuitPython is slow enough for the 25 ns minimum)
        self.spi.readinto(self.buf)
        return decode_chain(self.buf)

    def deinit(self):
        self.spi.unlock()
        self.spi.deinit()
        self.pl.deinit()


def watch(chain):
    print("watch mode — ground any sense input; Ctrl-C to stop\n")
    last = None
    while True:
        levels = chain.read()
        if levels != last:
            lows = low_lines(levels)
            print("%s   LOW: %s" % (pattern(levels), ["S%d" % i for i in lows] or "none"))
            last = levels
        time.sleep(0.05)


def walk(chain):
    print("walk mode — ground each input when prompted\n")
    idle = chain.read()
    if low_lines(idle):
        print("WARNING: with nothing grounded these read LOW: %s" % low_lines(idle))
        print("         fix the pull-ups before continuing\n")
    problems = 0
    for s in range(8 * CHIPS):
        print("ground S%d (U%d.D%d) ..." % (s, s // 8 + 1, s % 8))
        while True:
            lows = low_lines(chain.read())
            if lows:
                break
            time.sleep(0.05)
        if lows == [s]:
            print("   ok")
        else:
            problems += 1
            print("   MISMATCH: " + diagnose(s, lows))
        while low_lines(chain.read()):
            time.sleep(0.05)           # wait for release
    print("\nwalk complete: %d problem(s)" % problems)
    print("chain verified — connect the keyboard FPC" if not problems else "fix the wiring and re-run")


def main():
    print("=== x240-kbd 74HC165 chain test — %d chips, %d lines, SPI %d Hz ===" % (CHIPS, 8 * CHIPS, SPI_HZ))
    chain = Chain()
    try:
        walk(chain) if MODE == "walk" else watch(chain)
    finally:
        chain.deinit()


if ON_DEVICE:
    main()
