# ESP-FC

A MicroPython firmware for integrating PWM controlled PC fans with Home Assistant, inside or outside of a PC.

Authored by:
- shadowkrazee
    - [Github](https://github.com/shadowkrazee)
    - [Bio](https://madera.digital/bio)

**Links**
- [source](https://github.com/shadowkrazee/ESP-FC)
- [blog](https://madera.digital/maybe-someday)

# Dependencies
**Runtime**
- Micropython firmware: [download](https://micropython.org/download/)
- [microdot](https://github.com/miguelgrinberg/microdot) for REST API. [Docs](https://microdot.readthedocs.io/en/stable/intro.html#running-with-micropython)

**Development**
- [esptool](https://github.com/espressif/esptool) for firmware flashing and management of ESP8266/ESP32 devices. [Docs](https://docs.espressif.com/projects/esptool/en/latest/esp32/)
- [screen](https://www.gnu.org/software/screen/) for persistent terminal sessions and serial communication with devices.
- [mpremote](https://github.com/micropython/micropython/tree/master/tools/mpremote) for dev-testing and direct MicroPython integration. [Docs](https://docs.micropython.org/en/latest/reference/mpremote.html#mpremote)
- [rshell](https://github.com/dhylands/rshell) for file management and interactive scripting on MicroPython devices.


# Development tips:

**NixOS integration**
- Run `nix-shell` to initialize dev environment
- To Flash your ESP for the first time, run the following:
    - `esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash`
    - `esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 path/to/firmware.bin`
    
- **esp-fc**

    an `esp-fc` utility is also included to easily install dependencies, run/test code, and deploy to the board.
    - `esp-fc install` install dependencies into `src/lib`
    - `esp-fc test` TODO: Implement using mpremote | execute the specified script on the connected board
    - `esp-fc deploy` copy the required files to the ESP
    - `esp-fc rshell` a convenient alias for `rshell --port /dev/ttyUSB0`
    - `esp-fc screen` a convenient alias for `screen /dev/ttyUSB0 115200`


**MicroPython**
- Upload a single file using rshell:
    - `rshell --port /dev/ttyUSB0`
    - `cp file.py /pyboard/`
- Execute a script within rshell as follows:
    - `cd /pyboard/`
    - `repl`
    - `exec(open('my_script.py').read())`

- To simply view serial output, use `screen /dev/ttyUSB0 115200`
