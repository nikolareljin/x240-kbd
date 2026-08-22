# Changelog

All notable project changes should be recorded here.

## Unreleased

### Probing tools (milestone M2)

- `tools/matrix_probe/matrix_probe.py` reworked: two-pass procedure (`PASS = "A"`/`"B"`)
  so 40 FPC pads are covered with 26 GPIO, `NEVER_DRIVE_PADS` safety list, drive/sense
  terminology, Markdown table output that pastes into the pinout file, pass merging.
- `tools/ps2_sniffer/ps2_sniffer.py` gains host-to-device writes and a `synaptics` mode:
  reset, identify (magic 0x47), capability bits, absolute + W mode, guest enable through
  the pass-through, 6-byte packet decode, and an unambiguous `VERDICT:` on whether
  `W == 3` TrackPoint frames were seen.
- New `tools/shift_register_test/shift_register_test.py`: reads the 74HC165 chain over
  SPI0, `watch` and `walk` modes, names the wiring fault on a mismatch.
- New `tools/tests/` (pytest, 21 tests) covering the tools' protocol and formatting
  logic on the host; `tools/README.md` index.

### Design corrections (documentation pass, milestone M0)

These change what a builder would wire or configure. Each is recorded in the relevant doc
with its source.

- **USB-C upgrade wiring was wrong.** `README.md`, `PLAN.md` and the `usb_c_wiring.png`
  illustration said TP1 → D−, TP2 → D+. Per the Pico datasheet **TP1 = GND, TP2 = USB D−,
  TP3 = USB D+**; the old wiring shorts ground onto D−. Prose corrected everywhere; the
  image is kept as decoration and marked as not the wiring reference.
- **PS/2 driver.** `PS2_DRIVER = usart` is ATmega32u4-only and does not build on RP2040.
  The design now uses the RP2040 PIO driver (`vendor`), which requires clock = data + 1, so
  the pins become **DATA = GP21, CLK = GP22** (previously inverted). The "UART0" description
  of those pins was removed — GP21/GP22 is not a UART pair on the RP2040.
- **Backlight driver.** `BACKLIGHT_DRIVER = timer` was cited as the QMK #24470 workaround;
  the issue's workaround on RP2040 is `software`. Changed.
- **GPIO budget.** The 8 × 13 matrix assumption (21 GPIO) was unverified; the closest
  documented ThinkPad keyboard of this era is 17 × 9 (26 GPIO — every pin the Pico has).
  The design now reads sense lines through **three cascaded 74HC165 shift registers**
  (24 lines on 3 GPIO). Drive lines GP0–GP9; chain on GP16/GP17/GP18; eight GPIO spare.
- **TrackPoint added.** The X240 keyboard's TrackPoint was never mentioned. It is now a
  first-class feature, reached through the ClickPad's Synaptics pass-through port and
  decoded in firmware; GP19/GP20 reserved for a second PS/2 line if probing shows the
  TrackPoint is standalone.
- **Cost.** "$25–35 total" omitted the donor keyboard and palmrest. Honest totals are
  $90–150 depending on route; full tiers in `docs/hardware/bom-and-cost.md`.
- **Adafruit #1436** is a solder-pad adapter plate, not a ZIF breakout; the BOM now lists
  actual ZIF breakouts and says so.
- **Printability.** `cad/bottom_case.scad` is a single 309 × 210 mm part that exceeds every
  common print bed; the design moves to a split case (milestone M5), and a hand-made route
  with no printer is documented.

### Added

- `docs/hardware/` — components, BOM & cost, GPIO budget, 74HC165 sense chain, TrackPoint,
  backlight, PCB (Rev A vs Rev B).
- `docs/firmware/` — architecture, QMK configuration reference, pointing stack.
- `docs/enclosure/` — printed route, hand-made route (E1 base-cover reuse, E2 laser-cut,
  E3 Hammond console, E4 wood), mechanical integration, durability, assembly order and
  presentation box.
- `docs/references.md`, `docs/glossary.md`, section index pages with Jekyll front matter
  for the GitHub Pages site (configured in milestone M1).
- GitHub issue backlog: 51 issues across milestones M0–M8.

### Changed

- `README.md`, `BOM.md`, `PLAN.md`, `ASSEMBLY.md`, `hardware/wiring/wiring_diagram.md`,
  `hardware/pinout/*.md`, and the maintainer docs under `docs/` rewritten for the
  corrected design. `hardware/wiring/wiring_diagram.md` is now the single authoritative
  copy of the GPIO table.
- Pinout templates use drive/sense terminology and carry TrackPoint and chain columns.

### Earlier unreleased work

- Moved power-button handling out of the placeholder matrix keymap and into
  keyboard-level GP27 polling with the existing long-press guard.
- Added a full `docs/` documentation set covering project structure, design rules,
  coding instructions, and the build/test workflow.
- Added illustrated connector diagrams for the USB-C breakout and FPC ZIF connection.
- Expanded `.gitignore` for QMK build outputs, Python caches, OpenSCAD exports,
  local QMK checkouts, and transient hardware capture files.

## 0.1.0

- Initial project structure for the ThinkPad X240 USB keyboard controller.
- Added QMK keyboard definition, default keymap skeleton, firmware config, and
  RP2040 build rules.
- Added hardware pinout templates, wiring diagram, matrix probing tool,
  PS/2 sniffer, bill of materials, assembly guide, and OpenSCAD CAD sources.
