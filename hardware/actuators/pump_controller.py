import time

try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    GPIO = None  # Not available

class PumpController:
    def __init__(self, relay_pin=17):
        self.status = "OFF"
        self.total_runtime_sec = 0
        self.connected = False
        self.relay_pin = relay_pin

        if GPIO is not None:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.relay_pin, GPIO.OUT)
                GPIO.output(self.relay_pin, GPIO.HIGH)
                self.connected = True
                print("✅ Pump relay ready.")
            except Exception:
                # Silent fallback to simulation if setup fails
                self.connected = False
        else:
            # GPIO library not present
            self.connected = False

    def turn_on(self):
        if self.connected:
            GPIO.output(self.relay_pin, GPIO.LOW)
            self.status = "ON"
        else:
            self.status = "SIMULATED"

    def turn_off(self):
        if self.connected:
            GPIO.output(self.relay_pin, GPIO.HIGH)
            self.status = "OFF"
        else:
            self.status = "SIMULATED"

    def water_for(self, seconds):
        if self.connected:
            self.turn_on()
            time.sleep(seconds)
            self.turn_off()
        self.total_runtime_sec += seconds

    def get_status(self):
        return self.status

    def get_runtime_seconds(self):
        return int(self.total_runtime_sec)


if __name__ == "__main__":
    pump = PumpController()
    pump.water_for(3)
    print(f"Pump status: {pump.get_status()}")
    print(f"Runtime: {pump.get_runtime_seconds()} sec")
