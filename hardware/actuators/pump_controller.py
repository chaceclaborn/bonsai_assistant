# File: hardware/actuators/pump_controller.py

import threading
from time import time, sleep
from gpiozero import OutputDevice
from gpiozero.pins.lgpio import LGPIOFactory


class PumpController:
    def __init__(self, gpio_pin=18):
        factory = LGPIOFactory()
        self.pump = OutputDevice(gpio_pin, active_high=True, initial_value=False, pin_factory=factory)

        self._start_time = None
        self._total_runtime = 0.0
        self._running = False
        self._pulsing = False
        self._pulse_thread = None
        self._lock = threading.Lock()

    def turn_on(self):
        with self._lock:
            if not self.pump.value:
                self.pump.on()
                self._start_time = time()
                self._running = True
                print("🚿 Pump ON")

    def turn_off(self):
        with self._lock:
            if self.pump.value:
                self.pump.off()
                if self._running and self._start_time:
                    self._total_runtime += time() - self._start_time
                self._running = False
                self._start_time = None
                print("🛑 Pump OFF")

    def run_timed(self, duration_sec):
        def worker():
            self.turn_on()
            sleep(duration_sec)
            self.turn_off()

        threading.Thread(target=worker, daemon=True).start()

    def start_pulsing(self, pulse_on=0.3125, pulse_off=0.3125, total_duration=15):
        if self._pulsing:
            print("⚠️ Already pulsing. Ignored.")
            return

        def pulser():
            self._pulsing = True
            print("🔁 Starting pulse loop")
            end_time = time() + total_duration
            while self._pulsing and time() < end_time:
                self.turn_on()
                sleep(pulse_on)
                self.turn_off()
                sleep(pulse_off)
            self._pulsing = False
            print("✅ Pulse sequence complete.")

        self._pulse_thread = threading.Thread(target=pulser, daemon=True)
        self._pulse_thread.start()

    def stop_pulsing(self):
        print("⛔ Stop pulse requested")
        self._pulsing = False
        self.turn_off()

    def is_running(self):
        return self._running or self._pulsing

    def get_status(self):
        return "ON" if self.is_running() else "OFF"

    def get_runtime_seconds(self):
        if self._running and self._start_time:
            return round(self._total_runtime + (time() - self._start_time), 2)
        return round(self._total_runtime, 2)

    def close(self):
        print("🔌 Releasing GPIO resources")
        try:
            self.pump.close()
        except Exception as e:
            print(f"⚠️ Error closing pump: {e}")
