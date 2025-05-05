# File: main.py

import time
from hardware.display.rgb_display_driver import RGBDisplayDriver
from hardware.sensors.soil_moisture_sensor import SoilMoistureSensor
from hardware.actuators.pump_controller import PumpController

REFRESH_INTERVAL_SEC = 1  # Update every second

def main():
    oled = RGBDisplayDriver()
    sensor = SoilMoistureSensor(debug=False)
    pump = PumpController()

    while True:
        moisture = sensor.read_percentage()
        pump_status = pump.get_status()
        runtime_sec = pump.get_runtime_seconds()

        oled.draw_status(moisture, pump_status, runtime_sec)
        time.sleep(REFRESH_INTERVAL_SEC)

if __name__ == "__main__":
    print("✅ Bonsai Assistant started successfully!")
    main()
