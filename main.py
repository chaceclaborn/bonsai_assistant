# File: main.py

import time
import threading
import tkinter as tk
from hardware.display.rgb_display_driver import RGBDisplayDriver
from hardware.sensors.soil_moisture_sensor import SoilMoistureSensor
from hardware.actuators.pump_controller import PumpController
from core.timing import WateringCooldownManager
from utils.logging_utils import log_event, log_to_csv
from utils.status_icons import create_status_circle, set_tooltip

REFRESH_INTERVAL_SEC = 1
MOISTURE_THRESHOLD = 30


class BonsaiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bonsai Assistant Control Panel")

        self.sensor = SoilMoistureSensor(debug=False)
        self.pump = PumpController()
        self.display = RGBDisplayDriver()
        self.cooldown = WateringCooldownManager()

        self.moisture = None
        self.last_sensor_warning = 0
        self.sensor_warning_interval = 60  # seconds

        # --- STATUS ICONS ---
        status_frame = tk.Frame(root)
        status_frame.pack(pady=5)

        tk.Label(status_frame, text="System Health", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2)

        self.sensor_canvas = tk.Canvas(status_frame, width=20, height=20)
        self.sensor_canvas.grid(row=1, column=0)
        tk.Label(status_frame, text="Soil Sensor").grid(row=1, column=1)
        set_tooltip(self.sensor_canvas, "Detects moisture level in soil")

        self.pump_canvas = tk.Canvas(status_frame, width=20, height=20)
        self.pump_canvas.grid(row=2, column=0)
        tk.Label(status_frame, text="Pump").grid(row=2, column=1)
        set_tooltip(self.pump_canvas, "Controls watering pump")

        self.display_canvas = tk.Canvas(status_frame, width=20, height=20)
        self.display_canvas.grid(row=3, column=0)
        tk.Label(status_frame, text="OLED Display").grid(row=3, column=1)
        set_tooltip(self.display_canvas, "Displays system status on OLED")

        self.diagnostic_label = tk.Label(root, text="", font=("Arial", 10), fg="red")
        self.diagnostic_label.pack(pady=5)

        # --- SENSOR READOUT ---
        self.moisture_label = tk.Label(root, text="Moisture: ---%", font=("Arial", 14))
        self.moisture_label.pack(pady=5)

        self.runtime_label = tk.Label(root, text="Pump Runtime: 0.00 sec", font=("Arial", 12))
        self.runtime_label.pack(pady=5)

        # --- CONTROLS ---
        tk.Button(root, text="Manual ON", command=self.pump.turn_on, bg="green", fg="white", width=15).pack(pady=2)
        tk.Button(root, text="Manual OFF", command=self.pump.turn_off, bg="red", fg="white", width=15).pack(pady=2)

        tk.Label(root, text="Run Pump (sec):").pack()
        self.timed_entry = tk.Entry(root)
        self.timed_entry.insert(0, "5")
        self.timed_entry.pack()
        tk.Button(root, text="Run Timed", command=self.run_timed, bg="blue", fg="white").pack(pady=2)

        tk.Button(root, text="Test Pulse", command=self.test_pulse, bg="purple", fg="white").pack(pady=2)

        # Main update loops
        self.root.after(100, self.update_ui)
        threading.Thread(target=self.automation_loop, daemon=True).start()

    def update_ui(self):
        self.moisture = self.sensor.read_moisture_percent()
        moisture_str = f"{self.moisture:.1f}%" if self.moisture is not None else "---"
        self.moisture_label.config(text=f"Moisture: {moisture_str}")
        self.runtime_label.config(text=f"Pump Runtime: {self.pump.get_runtime_seconds():.2f} sec")

        self.display.draw_status(
            moisture=self.moisture,
            pump_status=self.pump.get_status(),
            runtime_sec=self.pump.get_runtime_seconds()
        )

        # Status indicators
        create_status_circle(self.sensor_canvas, "good" if self.moisture is not None else "bad")
        create_status_circle(self.pump_canvas, "good" if self.pump else "bad")
        create_status_circle(self.display_canvas, "good" if self.display else "bad")

        # Diagnostics
        if self.moisture is None:
            self.diagnostic_label.config(text="⚠️ Moisture sensor not detected or failed to read.")
        else:
            self.diagnostic_label.config(text="")

        self.root.after(REFRESH_INTERVAL_SEC * 1000, self.update_ui)

    def automation_loop(self):
        while True:
            time.sleep(REFRESH_INTERVAL_SEC)
            self.moisture = self.sensor.read_moisture_percent()

            if self.moisture is None:
                now = time.time()
                if now - self.last_sensor_warning >= self.sensor_warning_interval:
                    log_event("⚠️ No moisture reading. Skipping automation.")
                    self.last_sensor_warning = now
                continue

            if self.moisture < MOISTURE_THRESHOLD:
                if self.cooldown.can_water():
                    log_event("💧 Moisture low. Watering now...")
                    self.cooldown.mark_watered()
                    self.pump.run_timed(1)
                    time.sleep(1.1)
                    self.pump.start_pulsing(pulse_on=0.3125, pulse_off=0.3125, total_duration=15)
                    log_to_csv(self.moisture, "WATERED")
                else:
                    log_event("🛑 Already watered in the last 24 hrs.")
            else:
                log_event("✅ Moisture sufficient. No watering needed.")

    def run_timed(self):
        try:
            duration = float(self.timed_entry.get())
            if duration > 0:
                self.pump.run_timed(duration)
                log_event(f"⏱️ Manual timed pump run: {duration}s")
        except ValueError:
            log_event("❌ Invalid manual duration entry")

    def test_pulse(self):
        self.pump.start_pulsing(pulse_on=0.3125, pulse_off=0.3125, total_duration=5)
        log_event("🔁 Test pulse triggered")


if __name__ == "__main__":
    print("✅ Bonsai Assistant GUI started.")
    root = tk.Tk()
    app = BonsaiApp(root)
    root.mainloop()
