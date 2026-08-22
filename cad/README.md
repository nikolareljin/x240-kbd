# Printed parts

Parametric OpenSCAD. Every dimension lives in [`params.scad`](params.scad); part files
only include it. Values marked `MEASURE` there are targets until a real X240 deck is
measured (issue #44).

| Part | File | Variants | Qty |
|---|---|---|---|
| Bottom case, split | `bottom_case.scad` | `half="left"`, `"right"`, `"both"` | 1 + 1 |
| Perfboard / PCB sled | `perfboard_sled.scad` | | 1 |
| USB strain relief (two clamp halves) | `usb_strain_relief.scad` | | 1 set |
| Tilt feet (pair) | `tilt_feet.scad` | | 1 set |
| ZIF support block | `zif_support_block.scad` | `variant="keyboard"`, `"clickpad"` | 1 each |
| LED light pipe | `led_light_pipe.scad` | | 1 |
| Pico mount bracket (Rev A) | `pico_mount_bracket.scad` | | 1 |
| FPC cable guide | `fpc_cable_guide.scad` | `cable="keyboard"`, `"clickpad"` | 2 + 1 |

Render everything: `./dev build cad` → `out/cad/*.stl` (OpenSCAD in Docker; no install
needed). Single part by hand: `openscad -D 'half="right"' -o right.stl bottom_case.scad`.

Settings, tolerances, joint design and assembly order:
[`../docs/enclosure/printed.md`](../docs/enclosure/printed.md). Meshes are never committed
(`out/` and `cad/exports/` are ignored).
