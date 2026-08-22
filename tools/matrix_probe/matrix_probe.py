"""
matrix_probe.py — ThinkPad X240 keyboard-matrix discovery (CircuitPython, Raspberry Pi Pico)
=============================================================================================

The keyboard FPC has 40 pads; the Pico exposes 26 GPIO. The probe therefore runs in
TWO PASSES over the 40-pad ZIF breakout:

    pass A : breakout pads  1..26  -> Pico GPIO (see PASS_A_PADS)
    pass B : breakout pads 15..40  -> the same GPIO (see PASS_B_PADS)

Pads 15..26 are in both passes; those overlapping keys tie the two maps together.

Usage
-----
1. Wire the breakout pads for the chosen pass to the GPIO listed in GPIO_ORDER, in order.
2. Set PASS = "A" (or "B") below.  Copy this file to CIRCUITPY as code.py.
3. Open a serial terminal at 115200 baud.  Press and hold each key when prompted;
   type  s  + Enter to skip a key that cannot close in this pass.
4. Paste the printed Markdown table into hardware/pinout/x240_keyboard_fpc_pinout.md.
5. Repeat for the other pass.  Keys seen in both passes must agree.

Terminology: the pad the script drives LOW is the DRIVE pad; the pad that reads LOW in
response is the SENSE pad.  Which set becomes the 74HC165 chain is decided afterwards
(the larger set) — see docs/hardware/gpio-budget.md.

Safety: once a pad is known to be VCC, GND, or backlight, put its number in
NEVER_DRIVE_PADS so the probe never pulls it LOW.

The pure functions at the top run on a host Python too (see tools/tests/).
"""

# --------------------------------------------------------------------------------------
# Configuration — edit these
# --------------------------------------------------------------------------------------

PASS = "A"                      # "A" or "B"

# The 26 Pico GPIO used for probing, in the order they are wired to the breakout pads.
GPIO_ORDER = (
    "GP0", "GP1", "GP2", "GP3", "GP4", "GP5", "GP6", "GP7", "GP8", "GP9",
    "GP10", "GP11", "GP12", "GP13", "GP14", "GP15", "GP16", "GP17", "GP18", "GP19",
    "GP20", "GP21", "GP22", "GP26", "GP27", "GP28",
)

PASS_A_PADS = tuple(range(1, 27))    # pads 1..26  -> GPIO_ORDER[0..25]
PASS_B_PADS = tuple(range(15, 41))   # pads 15..40 -> GPIO_ORDER[0..25]

# Pads that must never be driven LOW (fill in as soon as they are identified).
NEVER_DRIVE_PADS = ()

# Keys to probe, in the order you want to be prompted.
KEY_NAMES = (
    "Esc", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
    "`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=",
    "Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]",
    "Caps", "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'", "Bsp",
    "LSft", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "RSft", "PgUp",
    "LCtl", "Win", "LAlt", "Spc", "RAlt", "Menu", "RCtl", "PgDn", "Ins",
    "Del", "Home", "End", "Up", "Left", "Down", "Rght", "\\", "Ent",
    "FN", "PwrBtn",   # PwrBtn usually closes a pad to a GND pad, not to the matrix
)

SETTLE_S = 0.001      # after driving a pad LOW, before reading
POLL_S = 0.01         # between scans while waiting for a key

# --------------------------------------------------------------------------------------
# Pure logic — no hardware imports; unit-tested on the host
# --------------------------------------------------------------------------------------


def pass_pads(which):
    """Return the tuple of breakout pad numbers wired for pass 'A' or 'B'."""
    if which == "A":
        return PASS_A_PADS
    if which == "B":
        return PASS_B_PADS
    raise ValueError("PASS must be 'A' or 'B'")


def build_pad_map(pads, gpio_order=GPIO_ORDER):
    """Map breakout pad number -> GPIO name for one pass.

    Raises if there are more pads than GPIO — that is a wiring plan error, not a
    runtime condition.
    """
    if len(pads) > len(gpio_order):
        raise ValueError("%d pads but only %d GPIO" % (len(pads), len(gpio_order)))
    return {pad: gpio_order[i] for i, pad in enumerate(pads)}


def group_pairs(results):
    """Split probe results {key: (drive_pad, sense_pad)} into sorted drive and sense pad lists."""
    drive = sorted({pair[0] for pair in results.values()})
    sense = sorted({pair[1] for pair in results.values()})
    return drive, sense


def merge_results(a, b):
    """Union two passes' results.  A key seen in both passes must have the same pads."""
    merged = dict(a)
    conflicts = []
    for key, pair in b.items():
        if key in merged and merged[key] != pair:
            conflicts.append((key, merged[key], pair))
        else:
            merged[key] = pair
    return merged, conflicts


def format_table(results, pass_name):
    """Markdown table that pastes into hardware/pinout/x240_keyboard_fpc_pinout.md."""
    lines = [
        "| Key | Drive pad | Sense pad | Pass |",
        "|-----|-----------|-----------|------|",
    ]
    for key in sorted(results, key=lambda k: (results[k][0], results[k][1], k)):
        d, s = results[key]
        lines.append("| %s | %d | %d | %s |" % (key, d, s, pass_name))
    return "\n".join(lines)


def format_summary(results):
    drive, sense = group_pairs(results)
    return (
        "Drive pads (%d): %s\nSense pads (%d): %s\n"
        "Matrix so far: %d x %d. The larger side goes to the 74HC165 chain."
        % (len(drive), drive, len(sense), sense, len(drive), len(sense))
    )


# --------------------------------------------------------------------------------------
# Hardware — CircuitPython only
# --------------------------------------------------------------------------------------

try:
    import board
    import digitalio
    import supervisor
    import time
    ON_DEVICE = True
except ImportError:          # host Python: only the pure functions are usable
    ON_DEVICE = False


def _pin(name):
    return getattr(board, name)


def scan_for_closure(pad_map, never_drive):
    """Drive each allowed pad LOW in turn; return (drive_pad, sense_pad) on the first
    closed pair, else None.  All DigitalInOut objects are released before returning."""
    pads = sorted(pad_map)
    for drive_pad in pads:
        if drive_pad in never_drive:
            continue
        driver = digitalio.DigitalInOut(_pin(pad_map[drive_pad]))
        driver.direction = digitalio.Direction.OUTPUT
        driver.value = False
        readers = {}
        for pad in pads:
            if pad == drive_pad:
                continue
            r = digitalio.DigitalInOut(_pin(pad_map[pad]))
            r.direction = digitalio.Direction.INPUT
            r.pull = digitalio.Pull.UP
            readers[pad] = r
        time.sleep(SETTLE_S)
        hit = None
        for pad, r in readers.items():
            if not r.value:
                hit = (drive_pad, pad)
                break
        driver.deinit()
        for r in readers.values():
            r.deinit()
        if hit:
            return hit
    return None


def wait_for_release(pad_map, never_drive):
    while scan_for_closure(pad_map, never_drive) is not None:
        time.sleep(0.05)


def main():
    pad_map = build_pad_map(pass_pads(PASS))
    print("\n=== x240-kbd matrix probe — pass %s ===" % PASS)
    print("Pads wired: %d..%d -> %s..%s" % (min(pad_map), max(pad_map),
                                           pad_map[min(pad_map)], pad_map[max(pad_map)]))
    print("Never driven: %s" % (list(NEVER_DRIVE_PADS) or "none yet"))
    print("Press and HOLD each key when prompted; 's' + Enter skips.\n")

    results = {}
    for key in KEY_NAMES:
        print("[%s]  press and hold..." % key)
        while True:
            if supervisor.runtime.serial_bytes_available:
                if input().strip().lower() == "s":
                    print("   skipped")
                    break
            pair = scan_for_closure(pad_map, NEVER_DRIVE_PADS)
            if pair:
                results[key] = pair
                print("   drive pad %d  sense pad %d" % pair)
                wait_for_release(pad_map, NEVER_DRIVE_PADS)
                break
            time.sleep(POLL_S)

    print("\n" + "=" * 60)
    print("PASS %s COMPLETE — paste into x240_keyboard_fpc_pinout.md:\n" % PASS)
    print(format_table(results, PASS))
    print()
    print(format_summary(results))
    if PASS == "A":
        print("\nNow rewire pads 15..40, set PASS = 'B', and run again.")
    else:
        print("\nMerge with pass A: keys in both passes must report the same pads.")


if ON_DEVICE:
    main()
