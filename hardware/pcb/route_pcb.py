#!/usr/bin/env python3
"""
route_pcb.py — autoroute x240_pico_rev_b.kicad_pcb with freerouting.

Three steps, the middle one in the freerouting image (this script is called twice from
./dev build pcb, inside the kicad/kicad image, with the freerouting run in between):

    route_pcb.py export <pcb> <dsn>      # pcbnew: board -> Specctra DSN
    (java -jar freerouting-executable.jar -de <dsn> -do <ses> -mp 30)
    route_pcb.py import <pcb> <ses>      # pcbnew: apply the SES routes, add the GND pour, save
    route_pcb.py pour <pcb> -           # add the GND pour only

The pour is added after routing with island removal on: the router owns every connection,
the pour only lowers GND impedance where it can reach.
"""
import sys

import pcbnew

USAGE = "usage: route_pcb.py export <pcb> <dsn> | import <pcb> <ses> | pour <pcb> -"

if len(sys.argv) != 4 or sys.argv[1] not in ("export", "import", "pour"):
    sys.exit(USAGE)
cmd, pcb, other = sys.argv[1], sys.argv[2], sys.argv[3]
board = pcbnew.LoadBoard(pcb)


def mm(v):
    return pcbnew.FromMM(v)


def add_ground_pour(board):
    """Back-side GND pour, added after routing.  Island removal is on, so regions the
    pour cannot connect are simply not poured — every connection is still the router's."""
    gnd = board.FindNet("GND")
    bb = board.GetBoardEdgesBoundingBox()
    z = pcbnew.ZONE(board)
    z.SetLayer(pcbnew.B_Cu)
    z.SetNet(gnd)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    z.SetMinThickness(mm(0.25))
    z.SetLocalClearance(mm(0.2))
    o = z.Outline()
    o.NewOutline()
    for x, y in ((bb.GetLeft(), bb.GetTop()), (bb.GetRight(), bb.GetTop()), (bb.GetRight(), bb.GetBottom()), (bb.GetLeft(), bb.GetBottom())):
        o.Append(x, y)
    board.Add(z)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())


if cmd == "export":
    ok = pcbnew.ExportSpecctraDSN(board, other)
    print("dsn export", "ok" if ok else "FAILED")
    sys.exit(0 if ok else 1)
elif cmd == "import":
    ok = pcbnew.ImportSpecctraSES(board, other)
    if ok:
        add_ground_pour(board)
        pcbnew.SaveBoard(pcb, board)
    print("ses import", "ok" if ok else "FAILED", "- tracks:", len(board.GetTracks()))
    sys.exit(0 if ok else 1)
elif cmd == "pour":
    add_ground_pour(board)
    pcbnew.SaveBoard(pcb, board)
    print("ground pour added")
else:
    sys.exit(USAGE)
