#!/usr/bin/env python3
"""Fail if the split-case halves overlap in volume.
Usage: check_cad_joint.py <intersection.stl>
The STL is the rendered intersection of left_half() and right_half(). Touching faces on
the seam plane are expected and show up as a zero-thickness sheet; anything with an X
extent beyond a hair is real interference."""
import struct
import sys

TOLERANCE = 0.01  # mm

path = sys.argv[1]
with open(path, "rb") as fh:
    data = fh.read()
xs = []
if data[:5] == b"solid" and b"facet" in data[:400]:
    for line in data.decode(errors="ignore").splitlines():
        t = line.split()
        if t and t[0] == "vertex":
            xs.append(float(t[1]))
else:
    n = struct.unpack("<I", data[80:84])[0]
    for i in range(n):
        v = struct.unpack("<12f", data[84 + i * 50 : 84 + i * 50 + 48])
        xs.extend((v[3], v[6], v[9]))
if not xs:
    print("cad joint: halves share no surface at all — the seam is not where params.scad says")
    sys.exit(1)
extent = max(xs) - min(xs)
print(f"cad joint: intersection X extent {extent:.3f} mm over {len(xs)//3} facets (tolerance {TOLERANCE})")
sys.exit(0 if extent <= TOLERANCE else 1)
