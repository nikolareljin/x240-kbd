# Target MCU
MCU        = RP2040
BOOTLOADER = rp2040

# Core HID features
BOOTMAGIC_ENABLE = yes   # Plug-in bootloader shortcut (hold top-left key)
EXTRAKEY_ENABLE  = yes   # Media keys + system keys (sleep, power)
MOUSEKEY_ENABLE  = yes   # Mouse keys via keymap (optional; touchpad is PS/2)
NKRO_ENABLE      = yes   # N-Key Rollover
CONSOLE_ENABLE   = no
COMMAND_ENABLE   = no

# PS/2 touchpad as a USB pointing device
POINTING_DEVICE_ENABLE = yes
POINTING_DEVICE_DRIVER = ps2
# usart = RP2040 hardware UART0 (preferred — reliable, low CPU cost)
# bitbang = fallback if UART0 pins are unavailable
PS2_DRIVER = usart

# Keyboard backlight
BACKLIGHT_ENABLE = yes
# timer driver works around the RP2040 PWM bug (QMK issue #24470)
BACKLIGHT_DRIVER = timer

# Keep binary small
LTO_ENABLE = yes

# Not needed for this build
RGBLIGHT_ENABLE    = no
RGB_MATRIX_ENABLE  = no
AUDIO_ENABLE       = no
HAPTIC_ENABLE      = no
BLUETOOTH_ENABLE   = no
