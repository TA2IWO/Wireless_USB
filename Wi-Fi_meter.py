#!/usr/bin/env python3
"""Wi-Fi signal-strength meter: Raspberry Pi Zero 2 W, 8 LEDs.

BCM GPIO order, left to right: 5, 6, 13, 12, 26, 16, 20, 21.
Each LED is active-HIGH, with its other terminal connected to GND
through an individual current-limiting resistor.
"""

import re
import subprocess
from time import sleep

from gpiozero import LED

WIFI_INTERFACE = "wlan0"
LED_PINS = (5, 6, 13, 12, 26, 16, 20, 21)
REFRESH_SECONDS = 1.0

# One threshold for each illuminated LED, from weak to strong (dBm).
THRESHOLDS_DBM = (-90, -85, -80, -75, -70, -65, -60, -55)


def wifi_signal_dbm():
    """Return RSSI in dBm; None if disconnected/unavailable."""
    try:
        result = subprocess.run(
            ("iw", "dev", WIFI_INTERFACE, "link"),
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        if result.returncode != 0 or "Not connected." in result.stdout:
            return None
        match = re.search(r"^\s*signal:\s*(-?\d+(?:\.\d+)?)\s*dBm", result.stdout, re.M)
        return float(match.group(1)) if match else None
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None


def main():
    leds = [LED(pin, active_high=True, initial_value=False) for pin in LED_PINS]
    try:
        while True:
            dbm = wifi_signal_dbm()
            count = 0 if dbm is None else max(1, sum(dbm >= threshold for threshold in THRESHOLDS_DBM))

            for index, led in enumerate(leds):
                if index < count:
                    led.on()
                else:
                    led.off()

            sleep(REFRESH_SECONDS)
    except KeyboardInterrupt:
        pass
    finally:
        for led in leds:
            led.off()
            led.close()


if __name__ == "__main__":
    main()
