---
title: Pointing stack
parent: Firmware
nav_order: 3
---

# Pointing stack — ClickPad and TrackPoint

Hardware background: [`../hardware/trackpoint.md`](../hardware/trackpoint.md).
Protocol: Synaptics *TouchPad Interfacing Guide* (PN 511-000275; no longer hosted publicly — the working reference is the Linux driver [`drivers/input/mouse/synaptics.c`](https://github.com/torvalds/linux/blob/master/drivers/input/mouse/synaptics.c));
reference implementation: Linux `drivers/input/mouse/synaptics.c`.

## Layers

```
QMK vendor PS/2 driver  (PIO0, GP21/GP22)     — bytes in, commands out
        │
synaptics.c                                   — identify, mode, 6-byte packet parser
        ├──► touchpad path   → dx, dy, buttons
        └──► trackpoint.c    → dx, dy, buttons  (from W == 3 guest frames)
                    │
x240_pico.c : pointing_device_task_kb()       — merge, scale, invert → report_mouse_t
```

QMK's PS/2 host API used: `ps2_host_init()`, `ps2_host_send(uint8_t)`,
`ps2_host_recv_response()`, `ps2_host_recv()`.

## Initialisation (`synaptics_init()`, called from `keyboard_post_init_kb`)

1. `ps2_host_init()`; send `0xFF` reset, expect `0xFA 0xAA 0x00`.
2. **Identify.** `synaptics_query(0x00)`: send `0xE8 0x00`, `0xE8 0x00`, `0xE8 0x00`,
   `0xE8 0x00` — wait, the query number is split across the four `SetResolution` values —
   then `0xE9`. Read three bytes. Byte 1 == `0x47` ⇒ Synaptics. Otherwise **fallback**.
3. **Capabilities.** `synaptics_query(0x02)`; note the `PassThrough` bit and whether
   extended capabilities exist.
4. **Mode byte.** `0x80 | 0x40 | 0x01` (absolute, rate 80, W-mode). Write with the knock
   then `0xF3 0x14` (`SetSampleRate 20`).
5. **Pass-through.** If capable, enable per the guide's pass-through section so guest
   packets are forwarded; the guest device also needs its own `0xF4` (enable streaming),
   sent *through* the pass-through mechanism.
6. `0xF4` enable data reporting on the ClickPad itself.

Each step checks the `0xFA` ack. Any failure ⇒ `synaptics_fallback()`: re-init as a plain
PS/2 mouse (`0xFF`, `0xF4`), set `mode = RELATIVE`, and `dprintf("synaptics: identify failed,
relative mode, no TrackPoint\n")`. The touchpad works; the log says the TrackPoint does not.

## Packet parsing (`synaptics_task()`)

Read bytes into a 6-byte buffer. Frame alignment: byte 0 has bits `1 0 W3 W2 0 W1 R L`
(bit 7 set, bit 6 clear, bit 3 clear) and byte 3 has bits 7 and 6 set. Drop bytes until
both patterns hold — the same resync the Linux driver does.

```c
uint8_t w = ((b0 & 0x30) >> 2) | ((b0 & 0x04) >> 1) | ((b3 & 0x04) >> 2);
if (w == 3) {
    trackpoint_handle_guest(b1, b4, b5);          // standard PS/2 3-byte packet
} else {
    x = ((b3 & 0x10) << 8) | ((b1 & 0x0F) << 8) | b4;
    y = ((b3 & 0x20) << 7) | ((b1 & 0xF0) << 4) | b5;
    z = b2;                                       // pressure
    touchpad_handle_abs(x, y, z, w, b0 & 0x01, b0 & 0x02);
}
```

The touchpad path converts absolute coordinates to a delta: keep the previous (x, y) while
`z` is above the touch threshold, emit `dx = x − x_prev`, reset when the finger lifts.
Scale by `SYN_TOUCHPAD_SCALE`. Ignore frames with `w` values that indicate palm or
multi-finger if they cause jumps.

## TrackPoint (`trackpoint.c`)

Guest frames carry a standard PS/2 mouse packet:

```
b1: Yo Xo Ys Xs 1 M R L        (overflow, sign, always-1, buttons)
b4: X delta (8 bits, sign from Xs)
b5: Y delta (8 bits, sign from Ys)
```

Decode exactly as `ps2_mouse.c` does, then scale by `SYN_TRACKPOINT_SCALE`. Sign convention:
PS/2 Y is positive-up, HID is positive-down — invert Y once, here, and nowhere else.

## Merge (`pointing_device_task_kb`)

```c
report.x = clamp(tp.dx + tpt.dx);
report.y = clamp(tp.dy + tpt.dy);
report.buttons = tp.buttons | tpt.buttons;
```

Both sources rarely move in the same scan; summing is simplest and feels right. Buttons are
OR-ed: the ClickPad's zones and the guest's buttons (if the module reports any) all count.

## Tuning constants

| Constant | Start | Tune by |
|---|---|---|
| `SYN_TOUCHPAD_SCALE` | 1/8 (absolute units are ~0–6000) | cursor should cross a 1080p screen in one comfortable swipe |
| `SYN_TRACKPOINT_SCALE` | 1 | slow drift when resting a finger ⇒ add a ±1 dead zone, not lower scale |
| `SYN_TOUCH_THRESHOLD` | `z > 30` | lower if light touches are missed |
| Y inversion | on | if the cursor goes up when you push down |

## Test checklist (M4)

- Identify succeeds: console shows `synaptics: id=0x47 …`, not the fallback line.
- Finger on pad moves cursor; bottom corners click L/R.
- Stick deflection moves cursor **with no finger on the pad** — this is the proof the
  pass-through works.
- Disconnect the TrackPoint (or cover the stick) — touchpad still works.
- Power-cycle ten times; every boot identifies. If not, the init sequence has a timing
  hole — add a delay after reset before the knock.
