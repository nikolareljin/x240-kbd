#!/usr/bin/env python3
"""Fail if any relative Markdown link in the repo points at a file that does not exist.
Usage: check_links.py <repo-root>"""
import glob
import os
import re
import sys

root = sys.argv[1] if len(sys.argv) > 1 else "."
bad = []
for f in glob.glob(os.path.join(root, "**", "*.md"), recursive=True):
    if "/.git/" in f or "/scripts/script-helpers/" in f or "/qmk_firmware/" in f or "/build/" in f:
        continue
    d = os.path.dirname(f)
    for m in re.finditer(r"\]\(([^)#\s]+)(#[^)]*)?\)", open(f, encoding="utf8").read()):
        t = m.group(1)
        if t.startswith(("http://", "https://", "mailto:")):
            continue
        if not os.path.exists(os.path.normpath(os.path.join(d, t))):
            bad.append((os.path.relpath(f, root), t))
for f, t in bad:
    print(f"broken link: {f} -> {t}")
print(f"check_links: {len(bad)} broken")
sys.exit(1 if bad else 0)
