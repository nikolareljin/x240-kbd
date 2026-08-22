# Matrix: drive lines on GPIO, sense lines read through three 74HC165 shift
# registers over SPI0 — QMK's built-in scanner cannot do that, so matrix.c owns it.
CUSTOM_MATRIX = lite
SRC += matrix.c synaptics.c trackpoint.c
# matrix.c reads the chain through QMK's SPI master (spi_master.c is only linked on request)
SPI_DRIVER_REQUIRED = yes

# Pointing: the Synaptics ClickPad speaks PS/2, but QMK's ps2_mouse.c assembles
# 3-byte relative packets only. The TrackPoint arrives inside 6-byte Synaptics
# absolute packets (pass-through, W == 3), so synaptics.c implements the custom
# pointing-device driver directly on the PS/2 host API. PS2_MOUSE_ENABLE stays
# off on purpose — both cannot own the bus.
POINTING_DEVICE_ENABLE = yes
POINTING_DEVICE_DRIVER = custom
# PS2_ENABLE / PS2_DRIVER = vendor / mouse off live in keyboard.json ("ps2" block):
# vendor = RP2040 PIO host (usart is ATmega32u4-only) and requires CLK = DATA + 1.

# Keyboard backlight (backlit keyboard variants only; leave on, harmless if unpopulated)
BACKLIGHT_ENABLE = yes
# RP2040 hardware PWM backlight does not build (QMK #24470); software PWM is the workaround.
BACKLIGHT_DRIVER = software

# Console for bring-up: synaptics.c logs its identify result and any fallback.
CONSOLE_ENABLE = yes
COMMAND_ENABLE = no

LTO_ENABLE = yes
