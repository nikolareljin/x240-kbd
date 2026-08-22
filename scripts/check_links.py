#!/usr/bin/env python3
"""Fail if any relative Markdown link in the repo points at a file that does not exist.
Usage: check_links.py <repo-root>

Walks the tree with directory pruning so a qmk_firmware checkout, the script-helpers
submodule, build output and generated site content are never entered."""
import os
import re
import sys

PRUNE_DIRS = {".git", "qmk_firmware", "out", "_site", ".jekyll-cache", "node_modules", "__pycache__"}
PRUNE_PATHS = {os.path.join("scripts", "script-helpers")}
LINK = re.compile(r"\]\(([^)#\s]+)(#[^)]*)?\)")

root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
bad = []
for dirpath, dirnames, filenames in os.walk(root):
    rel_dir = os.path.relpath(dirpath, root)
    dirnames[:] = sorted(
        d for d in dirnames
        if d not in PRUNE_DIRS and os.path.normpath(os.path.join(rel_dir, d)) not in PRUNE_PATHS
    )
    for name in filenames:
        if not name.endswith(".md"):
            continue
        path = os.path.join(dirpath, name)
        with open(path, encoding="utf8") as fh:
            text = fh.read()
        for m in LINK.finditer(text):
            target = m.group(1)
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            if not os.path.exists(os.path.normpath(os.path.join(dirpath, target))):
                bad.append((os.path.relpath(path, root), target))
for f, t in bad:
    print(f"broken link: {f} -> {t}")
print(f"check_links: {len(bad)} broken")
sys.exit(1 if bad else 0)
