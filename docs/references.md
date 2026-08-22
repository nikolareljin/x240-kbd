---
title: References
nav_order: 90
---

# Annotated references

Sources this project relies on, with a note on **how much of each applies to the X240
specifically**. "Era analogue" means a closely related ThinkPad that informs the design
but whose numbers must not be copied into our pinout files.

## Community projects

| Source | What it gives us | X240-specific? |
|---|---|---|
| [delingren/thinkpad_keyboards](https://github.com/delingren/thinkpad_keyboards) | Reverse-engineering of the 04Y0819 (X1 Carbon Gen 1 era): 32-pin matrix FPC, **17 × 9 matrix**, 20-pin TrackPoint/backlight FPC, QMK with the RP2040 PIO PS/2 driver, backlight current measurement, the TrackPoint reset-pulse finding, and the MCU pin-count comparison that rejected the Pico. | Era analogue — the pin-budget lesson transfers; the pinout does not. |
| [hamishcoleman/thinkpad-usbkb](https://github.com/hamishcoleman/thinkpad-usbkb) | KiCad design of a ThinkPad-keyboard USB adapter on an EFM32; `keyboard-thinkpad.pinout.txt` has an 8 × 8 matrix map for an older (X220-era) connector. | Era analogue — different connector and matrix. |
| [thedalles77/USB_Laptop_Keyboard_Controller](https://github.com/thedalles77/USB_Laptop_Keyboard_Controller) (Frank Adams) | The general method: Teensy/RP2040 matrix decoding, `matrixgenerator.py`, Eagle scanner boards, and worked examples for the T61, P15/P17 and older ThinkPads. Also the [RP2350 Stamp XL version](https://www.hackster.io/frank-adams/usb-laptop-keyboard-controller-solder-party-rp2350-stamp-xl-4fa642) with 40 GPIO. | Method only. |
| [Frank Adams — touchpad/TrackPoint conversion](https://www.hackster.io/frank-adams/laptop-touchpad-trackpoint-conversion-to-usb-d70519) | PS/2 touchpad and TrackPoint bring-up on Teensy/Pico, including level-shifting notes. | Method only. |
| [Instructables — reverse-engineer any keyboard matrix with a Pico](https://www.instructables.com/How-to-Reverse-Engineer-Almost-Any-Keyboard-Matrix/) | The probing technique our `matrix_probe.py` implements. | Method only. |
| [sharktastica — TrackPoint wiki](https://sharktastica.co.uk/wiki/trackpoint) | Module generations; confirms the **two-piece T440/X240-family module with four connections**. | Yes, module family. |
| [ThinkPads forum — X240 trackpoint/trackpad](https://forum.thinkpads.com/viewtopic.php?t=128403) | Field reports on X240 ClickPad/TrackPoint behaviour. | Yes. |
| [iFixit — X240 keyboard replacement](https://www.ifixit.com/Guide/Lenovo+Thinkpad+X240+Keyboard+Replacement/118924) | Photos of the connectors and disassembly order. | Yes. |

## Manufacturer documentation

| Source | Used for |
|---|---|
| [Raspberry Pi Pico datasheet](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf) | Pinout, **test points TP1 = GND, TP2 = D−, TP3 = D+**, power |
| [RP2040 datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf) | UART/SPI pin muxing, PIO |
| [Nexperia 74HC165 datasheet](https://assets.nexperia.com/documents/data-sheet/74HC_HCT165.pdf) | Timing, supply range, pin functions |
| [Nexperia 2N7002](https://assets.nexperia.com/documents/data-sheet/2N7002.pdf) · [onsemi BS170](https://www.onsemi.com/pdf/datasheet/bs170-d.pdf) | Backlight switch |
| [Hirose FH12 catalogue](https://www.hirose.com/en/product/document?series=FH12&documenttype=Catalog&lang=en&documentid=D31648_en) | Rev B FPC connectors |
| Synaptics *TouchPad Interfacing Guide* (PN 511-000275; no longer hosted publicly — the working reference is the Linux driver [`drivers/input/mouse/synaptics.c`](https://github.com/torvalds/linux/blob/master/drivers/input/mouse/synaptics.c)) | Absolute mode, packet format, pass-through |
| [Lenovo ThinkPad X240 Hardware Maintenance Manual](https://support.lenovo.com/us/en/manuals/um019141) | FRU numbers, disassembly, screw positions |
| [Adafruit 1436 product page](https://www.adafruit.com/product/1436) | To show it is a solder-pad plate, not a ZIF breakout |

## QMK

| Page | Used for |
|---|---|
| [RP2040 platform](https://docs.qmk.fm/platformdev_rp2040) | Bootloader, pin naming, PIO notes |
| [PS/2 mouse](https://docs.qmk.fm/features/ps2_mouse) | Driver table — `usart` is ATmega32u4-only; `vendor` = RP2040 PIO; clock = data + 1 |
| [Pointing device](https://docs.qmk.fm/features/pointing_device) | `pointing_device_task_kb`, report merging |
| [Backlight](https://docs.qmk.fm/features/backlight) | Driver table |
| [Issue #24470](https://github.com/qmk/qmk_firmware/issues/24470) | RP2040 `pwm` backlight does not compile; `software` works |
| [Custom matrix](https://docs.qmk.fm/custom_matrix) | `CUSTOM_MATRIX = lite` API |
| [Bootmagic](https://docs.qmk.fm/features/bootmagic) | Top-left-key bootloader entry |
| [Hardware keyboard guidelines](https://docs.qmk.fm/hardware_keyboard_guidelines) | VID/PID, layout metadata |

## Linux kernel

`drivers/input/mouse/synaptics.c` and `psmouse-base.c` — the working reference for the
identify sequence, mode byte, packet resync and pass-through handling. The ArchWiki
[Touchpad Synaptics](https://wiki.archlinux.org/title/Touchpad_Synaptics) page documents the
`serio: Synaptics pass-through port` behaviour seen on X240-class machines.

## Suppliers referenced

DigiKey, Mouser, LCSC, Jameco, Tinkersphere, Adafruit, Pimoroni, BuyDisplay, Crystalfontz,
JLCPCB, PCBWay, SendCutSend, Ponoko, Hammond Manufacturing, eBay, iFixit. Links are on the
[component reference](hardware/components.md) and [BOM](hardware/bom-and-cost.md) pages.
