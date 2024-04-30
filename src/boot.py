# boot.py
# This script is executed on every boot, including wake-boot from deep sleep
import esp

# Disable ESP debugging messages
esp.osdebug(None)