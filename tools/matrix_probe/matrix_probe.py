"""
matrix_probe.py — ThinkPad X240 FPC keyboard matrix discovery tool
===================================================================
Run on a Raspberry Pi Pico flashed with CircuitPython.

Instructions:
1. Connect the 40-pin FPC breakout to the Pico.
   Wire breakout pads 0-39 to Pico GP0-GP22, GP26-GP28, then use
   a second pass if you have more than 26 pins (most keyboards use
   fewer active pins; GND/VCC/NC eat up many of the 40).
2. Copy this file to CIRCUITPY as code.py.
3. Open a serial terminal at 115200 baud (Thonny works well).
4. Follow the prompts: press each key when asked, record the output.

Output format:
  KEY "Esc"  ->  ROW_PIN=2  COL_PIN=15
"""

import board
import busio
import digitalio
import time
import supervisor

# ---------------------------------------------------------------------------
# Map the 40 FPC breakout pads to Pico GPIO pins.
# Adjust this list to match how you physically wired the breakout to the Pico.
# If your breakout has numbered pads (0-39), list the corresponding GP pin objects.
# ---------------------------------------------------------------------------
ALL_PINS = [
    board.GP0,  board.GP1,  board.GP2,  board.GP3,
    board.GP4,  board.GP5,  board.GP6,  board.GP7,
    board.GP8,  board.GP9,  board.GP10, board.GP11,
    board.GP12, board.GP13, board.GP14, board.GP15,
    board.GP16, board.GP17, board.GP18, board.GP19,
    board.GP20, board.GP21, board.GP22,
    board.GP26, board.GP27, board.GP28,
]

NUM_PINS = len(ALL_PINS)

# Keys to probe — edit this list to match your keyboard layout order
KEY_NAMES = [
    "Esc", "F1",  "F2",  "F3",  "F4",  "F5",  "F6",  "F7",
    "F8",  "F9",  "F10", "F11", "F12",
    "`",   "1",   "2",   "3",   "4",   "5",   "6",   "7",
    "8",   "9",   "0",   "-",   "=",
    "Tab", "Q",   "W",   "E",   "R",   "T",   "Y",   "U",
    "I",   "O",   "P",   "[",   "]",
    "Caps","A",   "S",   "D",   "F",   "G",   "H",   "J",
    "K",   "L",   ";",   "'",   "Bsp",
    "LSft","Z",   "X",   "C",   "V",   "B",   "N",   "M",
    ",",   ".",   "/",   "RSft","PgUp",
    "LCtl","Win", "LAlt","Spc", "RAlt","Menu","RCtl","PgDn","Ins",
    "Del", "Home","End", "Up",  "Left","Down","Rght","\\",  "Ent",
    "FN",  "PwrBtn",
]


def scan_for_closure():
    """Drive each pin LOW one at a time; return (driver_idx, reader_idx) pair
    when a second pin also reads LOW (key pressed = circuit closed)."""
    for driver_idx in range(NUM_PINS):
        # Set up driver pin as output LOW
        driver = digitalio.DigitalInOut(ALL_PINS[driver_idx])
        driver.direction = digitalio.Direction.OUTPUT
        driver.value = False

        # Set all others as inputs with pull-up
        readers = []
        for i in range(NUM_PINS):
            if i == driver_idx:
                readers.append(None)
                continue
            pin = digitalio.DigitalInOut(ALL_PINS[i])
            pin.direction = digitalio.Direction.INPUT
            pin.pull = digitalio.Pull.UP
            readers.append(pin)

        time.sleep(0.001)  # settle

        for reader_idx, reader in enumerate(readers):
            if reader is None:
                continue
            if not reader.value:  # LOW = closed circuit through key
                # Clean up before returning
                driver.deinit()
                for r in readers:
                    if r is not None:
                        r.deinit()
                return (driver_idx, reader_idx)

        # Clean up this driver pass
        driver.deinit()
        for r in readers:
            if r is not None:
                r.deinit()

    return None


def wait_for_release():
    """Wait until no key is pressed (all pin pairs open)."""
    while scan_for_closure() is not None:
        time.sleep(0.05)


def wait_for_keypress():
    """Block until a key is pressed; return the (row, col) pin indices."""
    result = None
    while result is None:
        result = scan_for_closure()
        time.sleep(0.005)
    return result


def main():
    print("\n=== x240-pico-kbd Matrix Probe ===")
    print(f"Scanning {NUM_PINS} pins for {len(KEY_NAMES)} keys.\n")
    print("For each prompt, press and HOLD the named key, then release.\n")
    print("Results will be printed as:  KEY -> ROW_PIN=N  COL_PIN=M\n")
    print("Copy results into hardware/pinout/x240_keyboard_fpc_pinout.md\n")
    print("-" * 50)

    results = {}

    for key_name in KEY_NAMES:
        print(f"\nPress and hold key: [{key_name}]  (or type 's' + Enter to skip)")

        # Allow skip via serial
        start = supervisor.ticks_ms()
        skipped = False
        while True:
            if supervisor.runtime.serial_bytes_available:
                ch = input().strip().lower()
                if ch == "s":
                    print(f"  Skipped {key_name}")
                    skipped = True
                    break
            pair = scan_for_closure()
            if pair is not None:
                row_pin, col_pin = pair
                results[key_name] = pair
                print(f"  -> ROW_PIN={row_pin}  COL_PIN={col_pin}")
                wait_for_release()
                break
            time.sleep(0.01)

    print("\n" + "=" * 50)
    print("PROBING COMPLETE — Summary:")
    print("=" * 50)
    for key, (r, c) in results.items():
        print(f"  {key:<12} ROW_PIN={r:<3}  COL_PIN={c}")

    print("\nGroup pins with the same ROW_PIN value → those are matrix rows.")
    print("Group pins with the same COL_PIN value → those are matrix columns.")
    print("\nCopy this output into x240_keyboard_fpc_pinout.md")


main()
