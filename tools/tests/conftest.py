"""Make the CircuitPython tools importable on the host for their pure functions.
The hardware sections are skipped because `board` is not importable here."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for sub in ("matrix_probe", "ps2_sniffer", "shift_register_test"):
    sys.path.insert(0, os.path.join(ROOT, sub))
