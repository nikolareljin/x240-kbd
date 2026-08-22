#!/usr/bin/env python3
"""
gen_pcb.py — build x240_pico_rev_b.kicad_pcb from netlist_model.py with the pcbnew API.

Runs inside the kicad/kicad image.  Loads the real library footprints, places them from
the PLACEMENT table below, assigns every pad its net, draws the 100 x 80 mm outline and
the two mounting patterns, and saves.  Routing is a separate step (route_pcb.py).

Usage: gen_pcb.py <out_dir>
"""
import os
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netlist_model as M  # noqa: E402

FPDIR = "/usr/share/kicad/footprints"
PROJECT = "x240_pico_rev_b"
BOARD_W, BOARD_H = 100.0, 80.0

# Desired COURTYARD CENTRE (x, y) in mm from the board's top-left (y down) and rotation.
# The generator moves each footprint so its courtyard centre lands here, so anchor
# offsets inside the library footprints do not matter.
# Rear edge y = 0 (Pico USB, reset), front edge y = 80 faces the deck: both FPC sockets.
PLACEMENT = {
    "U1": (14.0, 35.0, 180),    # Pico vertical, USB toward the rear edge (courtyard 23 x 74 incl. cable zone)
    "SW1": (16.0, 71.0, 0),     # reset, under the Pico's far end, reachable through the floor hole
    "J1": (40.0, 75.0, 0),      # keyboard FPC, 40-pin, on the front edge
    "J2": (80.0, 75.0, 0),      # ClickPad FPC, 12-pin
    "J3": (33.0, 42.0, 0),      # J_KB  2x20 vertical (6 x 52)
    "J4": (43.0, 45.0, 0),      # J_MAT 2x17 vertical (6 x 44), beside J_KB
    "J5": (80.0, 52.0, 0),      # J_TP  1x12 vertical
    "J6": (88.0, 52.0, 0),      # J_PS2 1x8 vertical
    "J7": (46.0, 8.0, 0),       # USB-C pad header, rear
    "J8": (90.0, 8.0, 0),       # LED header, rear-right
    "U2": (58.0, 16.0, 0), "U3": (70.0, 16.0, 0), "U4": (82.0, 16.0, 0),     # chain
    "C1": (58.0, 10.0, 0), "C2": (70.0, 10.0, 0), "C3": (82.0, 10.0, 0),
    "RN1": (56.0, 23.0, 0), "RN2": (60.5, 23.0, 0), "RN3": (68.0, 23.0, 0),
    "RN4": (72.5, 23.0, 0), "RN5": (80.0, 23.0, 0), "RN6": (84.5, 23.0, 0),
    "R5": (58.0, 30.0, 0), "R6": (62.0, 30.0, 0), "Q1": (66.5, 30.0, 0), "R7": (71.0, 30.0, 0),
    "JP1": (76.5, 30.0, 0), "R8": (82.0, 30.0, 0), "R9": (86.0, 30.0, 0), "C4": (90.0, 30.0, 0),
    "C5": (94.0, 30.0, 90),
    "R1": (95.0, 44.0, 90), "R2": (95.0, 47.5, 90), "R3": (95.0, 51.0, 90), "R4": (95.0, 54.5, 90),
    # sled pattern (board_hole_inset 4 mm from the corners) and base-cover standoffs (MEASURE)
    "H1": (4.0, 4.0, 0), "H2": (96.0, 4.0, 0), "H3": (4.0, 76.0, 0), "H4": (96.0, 76.0, 0),
    "H5": (54.0, 5.0, 0), "H6": (62.0, 58.0, 0), "H7": (96.0, 36.0, 0),
}


def mm(v):
    return pcbnew.FromMM(v)


def main(out_dir):
    board = pcbnew.BOARD()
    nets = {}
    for name in M.NETS:
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        nets[name] = ni

    for ref, kind, value in M.PARTS:
        lib, fpname = M.LIB[kind][1].split(":")
        fp = pcbnew.FootprintLoad(f"{FPDIR}/{lib}.pretty", fpname)
        if fp is None:
            raise SystemExit(f"footprint not found: {lib}:{fpname}")
        fp.SetReference(ref)
        fp.SetValue(value)
        x, y, rot = PLACEMENT[ref]
        fp.SetOrientationDegrees(rot)
        fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        cy = fp.GetCourtyard(pcbnew.F_CrtYd)
        bb = cy.BBox() if cy.OutlineCount() else fp.GetBoundingBox(False, False)
        c = bb.GetCenter()
        fp.SetPosition(pcbnew.VECTOR2I(mm(x) - (c.x - mm(x)), mm(y) - (c.y - mm(y))))
        board.Add(fp)

    # pads -> nets
    by_ref = {fp.GetReference(): fp for fp in board.GetFootprints()}
    missing = []
    for name, pins in M.NETS.items():
        for ref, pin in pins:
            fp = by_ref[ref]
            pad = fp.FindPadByNumber(str(pin))
            if pad is None:
                missing.append((ref, pin))
                continue
            pad.SetNet(nets[name])
    if missing:
        raise SystemExit(f"pads not found: {missing}")

    # outline
    pts = [(0, 0), (BOARD_W, 0), (BOARD_W, BOARD_H), (0, BOARD_H)]
    for i in range(4):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(mm(0.1))
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % 4]
        seg.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
        seg.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
        board.Add(seg)

    # No copper pour at this stage: the router must connect every GND pad itself.  The
    # back-side GND pour is added after routing (route_pcb.py) with island removal on,
    # so it only ever adds copper and never creates unconnected islands.

    # design rules for a 2-layer JLCPCB/PCBWay board
    ds = board.GetDesignSettings()
    # Minimums are the fab's (JLCPCB/PCBWay 2-layer: 0.127 mm track/space) with margin;
    # the netclass targets below are what the router aims for.  Freerouting necks tracks
    # down between the 0.5 mm-pitch FPC pads, so the minimum must sit below the target.
    ds.m_TrackMinWidth = mm(0.127)
    ds.m_ViasMinSize = mm(0.5)
    ds.m_MinClearance = mm(0.127)
    ds.m_SolderMaskMinWidth = 0          # 0.5 mm pitch FPC pads: let the fab's mask rules apply
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetTrackWidth(mm(0.2))
    nc.SetViaDiameter(mm(0.6))
    nc.SetViaDrill(mm(0.3))
    nc.SetClearance(mm(0.15))   # router target (DRC checks it exactly); fab minimum is 0.127

    os.makedirs(out_dir, exist_ok=True)
    path = f"{out_dir}/{PROJECT}.kicad_pcb"
    pcbnew.SaveBoard(path, board)
    print(f"wrote {path}: {len(board.GetFootprints())} footprints, {len(M.NETS)} nets, {len(board.GetPads())} pads")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
