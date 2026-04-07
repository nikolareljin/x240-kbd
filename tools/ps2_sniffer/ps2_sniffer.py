"""
ps2_sniffer.py — PS/2 bus monitor for ThinkPad X240 ClickPad identification
============================================================================
Run on a Raspberry Pi Pico flashed with CircuitPython.

Purpose:
  Scan candidate pin pairs on the touchpad FPC breakout to identify which
  pair carries PS/2 CLK and DATA. Once found, decode incoming PS/2 packets
  and print movement/button data to the serial console.

Usage:
  1. Power the touchpad at 3.3 V (confirmed VCC/GND pins from Phase 1).
  2. Edit CANDIDATE_PAIRS below — list (clk_pin, data_pin) tuples to try.
  3. Copy to CIRCUITPY as code.py and open serial terminal at 115200 baud.
  4. Move your finger on the touchpad. When CLK/DATA are correct, decoded
     PS/2 packets appear in the terminal.
  5. Record the correct pin indices in x240_clickpad_fpc_pinout.md.

PS/2 packet format (standard 3-byte mouse packet):
  Byte 0: [Yo Xo Ys Xs 1 MBtn RBtn LBtn]
  Byte 1: X movement (signed, 2's complement with Xs sign bit)
  Byte 2: Y movement (signed, 2's complement with Ys sign bit)
"""

import board
import digitalio
import time

# ---------------------------------------------------------------------------
# Edit these pairs: (clk_board_pin, data_board_pin)
# Try each pair in sequence — the correct one will produce decoded output
# when you move a finger on the touchpad.
# ---------------------------------------------------------------------------
CANDIDATE_PAIRS = [
    (board.GP21, board.GP22),
    (board.GP22, board.GP21),
    (board.GP19, board.GP20),
    (board.GP20, board.GP19),
]

# How many packets to capture per candidate pair before trying the next
PACKETS_PER_TRIAL = 5

# Timeout waiting for a CLK edge (microseconds)
CLK_TIMEOUT_US = 5000


def read_ps2_byte(clk_pin, data_pin):
    """
    Read one PS/2 byte from the bus (device-to-host direction).
    PS/2 protocol: CLK idles HIGH; device pulls CLK LOW for each bit.
    Bits arrive LSB first, with a start bit (0), 8 data bits, odd parity,
    and a stop bit (1).
    Returns the byte value, or None on timeout/framing error.
    """
    # Wait for start bit: CLK HIGH → LOW transition
    deadline = time.monotonic_ns() + CLK_TIMEOUT_US * 1000
    while clk_pin.value:
        if time.monotonic_ns() > deadline:
            return None  # timeout

    # Start bit: DATA should be LOW
    time.sleep(0.00002)  # wait to sample mid-bit (~20 µs into 100 µs bit period)
    if data_pin.value:
        return None  # framing error

    # Read 8 data bits (LSB first)
    byte = 0
    for bit_pos in range(8):
        # Wait for CLK to go HIGH then LOW again
        deadline = time.monotonic_ns() + CLK_TIMEOUT_US * 1000
        while not clk_pin.value:
            if time.monotonic_ns() > deadline:
                return None
        deadline = time.monotonic_ns() + CLK_TIMEOUT_US * 1000
        while clk_pin.value:
            if time.monotonic_ns() > deadline:
                return None
        time.sleep(0.00002)
        if data_pin.value:
            byte |= (1 << bit_pos)

    # Parity bit (ignore value, just clock through)
    deadline = time.monotonic_ns() + CLK_TIMEOUT_US * 1000
    while not clk_pin.value:
        if time.monotonic_ns() > deadline:
            return None
    deadline = time.monotonic_ns() + CLK_TIMEOUT_US * 1000
    while clk_pin.value:
        if time.monotonic_ns() > deadline:
            return None

    # Stop bit: DATA should be HIGH
    time.sleep(0.00002)
    if not data_pin.value:
        return None  # framing error

    # Clock through stop bit
    deadline = time.monotonic_ns() + CLK_TIMEOUT_US * 1000
    while not clk_pin.value:
        if time.monotonic_ns() > deadline:
            return None
    deadline = time.monotonic_ns() + CLK_TIMEOUT_US * 1000
    while clk_pin.value:
        if time.monotonic_ns() > deadline:
            return None

    return byte


def decode_packet(b0, b1, b2):
    """Decode a standard 3-byte PS/2 mouse packet."""
    left  = bool(b0 & 0x01)
    right = bool(b0 & 0x02)
    mid   = bool(b0 & 0x04)
    x_sign = -256 if (b0 & 0x10) else 0
    y_sign = -256 if (b0 & 0x20) else 0
    x = b1 + x_sign
    y = b2 + y_sign
    return x, y, left, right, mid


def try_pair(clk_board_pin, data_board_pin):
    """Try reading PS/2 packets on a given pin pair. Returns True if successful."""
    print(f"\nTrying CLK={clk_board_pin} DATA={data_board_pin}")
    print("  Move finger on touchpad...")

    clk  = digitalio.DigitalInOut(clk_board_pin)
    data = digitalio.DigitalInOut(data_board_pin)
    clk.direction  = digitalio.Direction.INPUT
    data.direction = digitalio.Direction.INPUT
    # No internal pull-ups — external 4.7 kΩ pull-ups are on the board

    packets_ok = 0
    attempts = 0
    max_attempts = 60  # ~6 seconds of trying

    while packets_ok < PACKETS_PER_TRIAL and attempts < max_attempts:
        attempts += 1
        b0 = read_ps2_byte(clk, data)
        if b0 is None:
            time.sleep(0.1)
            continue
        b1 = read_ps2_byte(clk, data)
        if b1 is None:
            continue
        b2 = read_ps2_byte(clk, data)
        if b2 is None:
            continue

        # Validate: bit 3 of byte 0 must always be 1 in standard PS/2 mouse
        if not (b0 & 0x08):
            continue

        x, y, left, right, mid = decode_packet(b0, b1, b2)
        print(f"  PKT: X={x:+4d}  Y={y:+4d}  L={int(left)} R={int(right)} M={int(mid)}")
        packets_ok += 1

    clk.deinit()
    data.deinit()

    if packets_ok >= PACKETS_PER_TRIAL:
        print(f"\n  SUCCESS: CLK={clk_board_pin}  DATA={data_board_pin}")
        print("  Record these in x240_clickpad_fpc_pinout.md")
        return True

    print(f"  No valid packets on this pair.")
    return False


def main():
    print("\n=== x240-pico-kbd PS/2 Sniffer ===")
    print(f"Testing {len(CANDIDATE_PAIRS)} candidate pin pair(s).\n")
    print("Make sure touchpad VCC and GND are connected and 4.7 kΩ pull-ups")
    print("are present on the CLK and DATA lines.\n")

    for clk_pin, data_pin in CANDIDATE_PAIRS:
        if try_pair(clk_pin, data_pin):
            print("\nDone — correct pins found.")
            return

    print("\nNo valid PS/2 signal found on any candidate pair.")
    print("Check:")
    print("  1. Touchpad VCC and GND are correct")
    print("  2. 4.7 kΩ pull-ups are present on CLK and DATA")
    print("  3. Add more pairs to CANDIDATE_PAIRS and retry")


main()
