# File: hardware/sensors/soil_moisture_sensor.py

class SoilMoistureSensor:
    def __init__(self, debug=True):
        self.debug = debug

    def read_percentage(self):
        if self.debug:
            print("🌱 [Simulated] No sensor connected.")
        return None


if __name__ == "__main__":
    sensor = SoilMoistureSensor()
    print(sensor.read_percentage())
