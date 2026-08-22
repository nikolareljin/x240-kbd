#!/usr/bin/env python3
"""
gen_schematic.py — write x240_pico_rev_b.kicad_sch from netlist_model.py.

Runs inside the kicad/kicad image (needs /usr/share/kicad/symbols). Every part is placed
on a grid and every connected pin gets a global label carrying the net name; unconnected
pins get no-connect flags. The real library symbol definitions are embedded, parents of
`extends` symbols included, so the file opens in KiCad with nothing missing.

Usage: gen_schematic.py <out_dir>
"""
import os
import re
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netlist_model as M  # noqa: E402

SYMDIR = "/usr/share/kicad/symbols"
PROJECT = "x240_pico_rev_b"
ROOT_UUID = "0f3b1796-fc9b-41f1-a39b-000000000001"   # stable: instances path must not churn


_UID_NS = uuid.UUID("0f3b1796-fc9b-41f1-a39b-89554776f7dc")
_uid_n = 0


def uid():
    """Deterministic UUIDs: the file must not change unless the model does."""
    global _uid_n
    _uid_n += 1
    return str(uuid.uuid5(_UID_NS, f"x240:{_uid_n}"))


# ------------------------------------------------------------------ s-expression helpers
def block_at(text, start):
    """Return the balanced s-expression starting at text[start] == '('."""
    depth = 0
    i = start
    in_str = False
    while i < len(text):
        c = text[i]
        if in_str:
            if c == "\\":
                i += 1
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
        i += 1
    raise ValueError("unbalanced")


_libcache = {}


def lib_text(lib):
    if lib not in _libcache:
        _libcache[lib] = open(f"{SYMDIR}/{lib}.kicad_sym", encoding="utf8").read()
    return _libcache[lib]


def symbol_block(lib, name):
    t = lib_text(lib)
    m = re.search(r'\n\t\(symbol "%s"' % re.escape(name), t)
    if not m:
        raise KeyError(f"{lib}:{name}")
    return block_at(t, m.start() + 2)


def symbol_pins(lib, name):
    """[(number, name, x, y, angle, length)] in symbol units (mm, y up)."""
    blk = symbol_block(lib, name)
    ext = re.search(r'\(extends "([^"]+)"', blk)
    if ext:
        return symbol_pins(lib, ext.group(1))
    out = []
    for m in re.finditer(r"\(pin\s", blk):
        pb = block_at(blk, m.start())
        at = re.search(r"\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\)", pb)
        ln = re.search(r"\(length\s+([-\d.]+)\)", pb)
        nm = re.search(r'\(name\s+"([^"]*)"', pb)
        num = re.search(r'\(number\s+"([^"]*)"', pb)
        out.append((num.group(1), nm.group(1), float(at.group(1)), float(at.group(2)), float(at.group(3)), float(ln.group(1))))
    return out


def property_blocks(blk):
    """{property name: full (property ...) block} of a symbol."""
    out = {}
    for m in re.finditer(r'\(property "([^"]+)"', blk):
        out[m.group(1)] = block_at(blk, m.start())
    return out


def embedded_symbol(lib, name):
    """Symbol block renamed to Lib:Name.  A derived symbol (extends) is flattened the way
    KiCad itself caches it: the parent's body with the derived symbol's properties laid
    over it and the units renamed.  Returns (text, None)."""
    blk = symbol_block(lib, name)
    ext = re.search(r'\(extends "([^"]+)"', blk)
    if ext:
        parent = ext.group(1)
        body = symbol_block(lib, parent)
        for pname, pblk in property_blocks(blk).items():
            old = property_blocks(body).get(pname)
            body = body.replace(old, pblk, 1) if old else body.replace("\n\t\t(symbol \"", "\n\t\t" + pblk + "\n\t\t(symbol \"", 1)
        body = body.replace(f'(symbol "{parent}"', f'(symbol "{lib}:{name}"', 1)
        body = body.replace(f'(symbol "{parent}_', f'(symbol "{name}_')
        return body, None
    return blk.replace(f'(symbol "{name}"', f'(symbol "{lib}:{name}"', 1), None


# ------------------------------------------------------------------ layout
CELL_W, CELL_H = 70.0, 60.0
BIG = {"pico": (110, 110), "hc165": (70, 70), "fpc40": (70, 120), "hdr2x20": (70, 70), "hdr2x17": (70, 70)}
COLS = 9
PAPER = "A0"


def place(parts):
    """Simple shelf packing across the page; returns {ref: (x, y)}."""
    pos = {}
    x = y = 0.0
    row_h = 0.0
    margin = 25.0
    page_w = 1189.0 - 2 * margin
    for ref, kind, _ in parts:
        w, h = BIG.get(kind, (CELL_W, CELL_H))
        if x + w > page_w:
            x = 0.0
            y += row_h
            row_h = 0.0
        # snap to KiCad's 50 mil connection grid so pin ends land on it
        gx, gy = margin + x + w / 2, margin + y + h / 2
        pos[ref] = (round(gx / 1.27) * 1.27, round(gy / 1.27) * 1.27)
        x += w
        row_h = max(row_h, h)
    return pos


# ------------------------------------------------------------------ write
def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def main(out_dir):
    pin_net = {}
    for name, pins in M.NETS.items():
        for ref, pin in pins:
            pin_net[(ref, str(pin))] = name

    parts = [p for p in M.PARTS if M.LIB[p[1]][0]]          # holes have no symbol
    pos = place(parts)

    # lib_symbols, with parents
    libsyms = {}
    for _, kind, _ in parts:
        lib, name = M.LIB[kind][0].split(":")
        if f"{lib}:{name}" in libsyms:
            continue
        txt, parent = embedded_symbol(lib, name)
        libsyms[f"{lib}:{name}"] = txt
        if parent and f"{lib}:{parent}" not in libsyms:
            libsyms[f"{lib}:{parent}"] = embedded_symbol(lib, parent)[0]

    o = []
    o.append(f'(kicad_sch\n\t(version 20250114)\n\t(generator "x240_gen")\n\t(generator_version "9.0")\n\t(uuid "{ROOT_UUID}")\n\t(paper "{PAPER}")')
    o.append("\t(lib_symbols")
    for txt in libsyms.values():
        o.append("\t\t" + txt.replace("\n", "\n\t"))
    o.append("\t)")

    for ref, kind, value in parts:
        lib, name = M.LIB[kind][0].split(":")
        fp = M.LIB[kind][1]
        x, y = pos[ref]
        su = uid()
        o.append(f'\t(symbol\n\t\t(lib_id "{lib}:{name}")\n\t\t(at {x:.2f} {y:.2f} 0)\n\t\t(unit 1)\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp {"yes" if value.startswith("DNP") else "no"})\n\t\t(uuid "{su}")')
        o.append(f'\t\t(property "Reference" "{ref}"\n\t\t\t(at {x:.2f} {y - 30:.2f} 0)\n\t\t\t(effects (font (size 2 2)) (justify left))\n\t\t)')
        o.append(f'\t\t(property "Value" "{esc(value)}"\n\t\t\t(at {x:.2f} {y - 26:.2f} 0)\n\t\t\t(effects (font (size 1.5 1.5)) (justify left))\n\t\t)')
        o.append(f'\t\t(property "Footprint" "{fp}"\n\t\t\t(at {x:.2f} {y:.2f} 0)\n\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)')
        o.append(f'\t\t(property "Datasheet" ""\n\t\t\t(at {x:.2f} {y:.2f} 0)\n\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)')
        o.append(f'\t\t(property "Description" ""\n\t\t\t(at {x:.2f} {y:.2f} 0)\n\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)')
        pins = symbol_pins(lib, name)
        for num, _pn, px, py, ang, ln in pins:
            o.append(f'\t\t(pin "{num}"\n\t\t\t(uuid "{uid()}")\n\t\t)')
        o.append(f'\t\t(instances\n\t\t\t(project "{PROJECT}"\n\t\t\t\t(path "/{ROOT_UUID}"\n\t\t\t\t\t(reference "{ref}")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)')
        # labels / no-connects at the pin connection points (symbol y is up, sheet y is down)
        seen_nums = set()
        for num, _pn, px, py, ang, ln in pins:
            if num in seen_nums:
                continue
            seen_nums.add(num)
            cx, cy = x + px, y - py
            n = pin_net.get((ref, num))
            if n:
                rot = {0: 180, 180: 0, 90: 270, 270: 90}[int(ang) % 360]   # label points away from the body
                o.append(f'\t(global_label "{esc(n)}"\n\t\t(shape passive)\n\t\t(at {cx:.2f} {cy:.2f} {rot})\n\t\t(effects (font (size 1.27 1.27)) (justify {"right" if rot == 180 else "left"}))\n\t\t(uuid "{uid()}")\n\t\t(property "Intersheetrefs" "${{INTERSHEET_REFS}}"\n\t\t\t(at {cx:.2f} {cy:.2f} 0)\n\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)\n\t)')
            else:
                o.append(f'\t(no_connect\n\t\t(at {cx:.2f} {cy:.2f})\n\t\t(uuid "{uid()}")\n\t)')

    o.append('\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)\n)')
    os.makedirs(out_dir, exist_ok=True)
    with open(f"{out_dir}/{PROJECT}.kicad_sch", "w", encoding="utf8") as fh:
        fh.write("\n".join(o) + "\n")
    pro = f"{out_dir}/{PROJECT}.kicad_pro"
    if not os.path.exists(pro):
        with open(pro, "w") as fh:
            fh.write('{\n  "meta": { "filename": "%s.kicad_pro", "version": 1 },\n  "board": { "design_settings": { "rules": {} } },\n  "schematic": { "legacy_lib_dir": "", "legacy_lib_list": [] },\n  "sheets": [ [ "%s", "Root" ] ]\n}\n' % (PROJECT, ROOT_UUID))
    print(f"wrote {PROJECT}.kicad_sch: {len(parts)} symbols, {len(libsyms)} library symbols, {len(M.NETS)} nets")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
