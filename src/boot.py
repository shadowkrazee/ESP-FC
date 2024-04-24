# boot.py
# This script is executed on every boot, including wake-boot from deep sleep

import machine
import network
import esp
import esp32
import gc
import time

# Disable ESP debugging messages
esp.osdebug(None)

# Garbage collector control (optional)
gc.collect()

# Wait for 1 second, so the fans can spin up
time.sleep(1)

# Init PWM and slow fans down
print(esp32.raw_temperature()) # read the internal temperature of the MCU, in Fahrenheit

fan = machine.PWM(machine.Pin(21))
fan.freq(25000)
fan_percent = 30.0
duty = int(fan_percent * 65535 / 100)
fan.duty_u16(duty)
print(f'Duty cycle set to: {duty}')

# Wi-Fi connection information
ssid = 'Tomorrowland'
password = 'Epcot19!'

# Connect to Wi-Fi
station = network.WLAN(network.STA_IF)
station.active(True)
station.config(dhcp_hostname='ESP-FC')
station.scan() # Scanning first helps connection reliabliity for some reason
station.connect(ssid, password)

# Wait for connection
while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())

# Add any additional system-wide initializations here

