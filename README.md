# ESP-FC

A MicroPython firmware for integrating PWM controlled fans with Home Assistant
authors:
- "shadowkrazee <epicshadowkrazee@gmail.com>"

[homepage](https://madera.digital)

## Dependencies
- [microdot](https://github.com/miguelgrinberg/microdot) for REST API


# Development tips:

## NixOS development
- Run `nix-shell` to initialize dev environment
- To Flash your ESP for the first time, run the following:
    - `esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash`
    - `esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 MicroPython_FW/ESP32_GENERIC-20240222-v1.22.2.bin`
- an `esp-fc` utility is also included to easily install dependencies and upload code to the ESP
    - `esp-fc install` will install dependencies into `src/lib`
    - `esp-fc deploy` will copy the files to the ESP


## MicroPython
- Upload a single file using rshell:
    - `rshell --port /dev/ttyUSB0`
    - `cp file.py /pyboard/`
- Execute a script within rshell as follows:
    - `cd /pyboard/`
    - `repl`
    - `exec(open('my_script.py').read())`

- To simply view serial output, use `screen /dev/ttyUSB0 115200`
