# ESP-FC
An ESP32-based PWM fan controller using MicroPython.

## NixOS development
- Run `nix-shell` to initialize dev environment
- To Flash your ESP for the first time, run the following:
    - `esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash`
    - `esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 MicroPython_FW/ESP32_GENERIC-20240222-v1.22.2.bin`
