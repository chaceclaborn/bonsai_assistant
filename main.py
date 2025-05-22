# File: main.py

import time
import threading
import tkinter as tk
from tkinter import ttk

from hardware.display.rgb_display_driver import RGBDisplayDriver
from hardware.sensors.soil_moisture_sensor import SoilMoistureSensor
from hardware.actuators.pump_controller import PumpController

from core.timing import WateringCooldownManager
from core.test_tools import run_test_pulse
from utils.logging_utils import log_event, log_to_csv
from utils.status_icons import create_status_circle, set_tooltip

from simulation.mock_sensor import MockSoilMoistureSensor
from simulation.mock_pump import MockPumpController
from simulation.mock_display import MockDisplay

REFRESH_INTERVAL_SEC = 1
MOISTURE_THRESHOLD = 30


class BonsaiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bonsai Assistant")
        self.root.geometry("640x520")

        # Independent sim toggles
        self.sim_sensor = tk.BooleanVar(value=False)
        self.sim_pump = tk.BooleanVar(value=False)
        self.sim_display = tk.BooleanVar(value=False)
        self.sim_moisture = tk.DoubleVar(value=50.0)

        self.test_pulse_duration = tk.DoubleVar(value=20.0)
        self.test_pulse_on = tk.DoubleVar(value=0.3125)
        self.test_pulse_off = tk.DoubleVar(value=0.3125)

        self.sensor = SoilMoistureSensor(debug=False)
        self.pump = PumpController()
        self.display = RGBDisplayDriver()
        self.cooldown = WateringCooldownManager()

        self.moisture = None
        self.last_sensor_warning = 0
        self.sensor_warning_interval = 60
        self.auto_watering_active = False

        self.tab_control = ttk.Notebook(root)
        self.tab_dashboard = ttk.Frame(self.tab_control)
        self.tab_controls = ttk.Frame(self.tab_control)
        self.tab_graph = ttk.Frame(self.tab_control)
        self.tab_settings = ttk.Frame(self.tab_control)
        self.tab_journal = ttk.Frame(self.tab_control)
        self.tab_devtools = ttk.Frame(self.tab_control)

        self.tab_control.add(self.tab_dashboard, text="Dashboard")
        self.tab_control.add(self.tab_controls, text="Pump Controls")
        self.tab_control.add(self.tab_graph, text="Graph")
        self.tab_control.add(self.tab_settings, text="Settings")
        self.tab_control.add(self.tab_journal, text="Journal")
        self.tab_control.add(self.tab_devtools, text="Dev Tools")
        self.tab_control.pack(expand=1, fill="both")

        self.build_dashboard()
        self.build_controls()
        self.build_settings()
        self.build_devtools()

        self.root.after(100, self.update_ui)
        threading.Thread(target=self.automation_loop, daemon=True).start()

    def update_sim_components(self):
        try:
            if hasattr(self.pump, "close"):
                self.pump.close()
        except Exception as e:
            log_event(f"⚠️ Could not close pump: {e}")

        self.sensor = MockSoilMoistureSensor(lambda: self.sim_moisture.get()) if self.sim_sensor.get() else SoilMoistureSensor(debug=False)
        self.pump = MockPumpController() if self.sim_pump.get() else PumpController()
        self.display = MockDisplay() if self.sim_display.get() else RGBDisplayDriver()

        log_event("✅ Simulation components updated.")
        self.update_ui()

    def build_dashboard(self):
        frame = self.tab_dashboard
        tk.Label(frame, text="System Health", font=("Arial", 12, "bold")).pack(pady=5)

        sensor_row = tk.Frame(frame)
        sensor_row.pack(pady=2)
        self.sensor_canvas = tk.Canvas(sensor_row, width=20, height=20)
        self.sensor_canvas.pack(side="left")
        tk.Label(sensor_row, text="Soil Sensor").pack(side="left", padx=5)
        set_tooltip(self.sensor_canvas, "Detects moisture level")

        pump_row = tk.Frame(frame)
        pump_row.pack(pady=2)
        self.pump_canvas = tk.Canvas(pump_row, width=20, height=20)
        self.pump_canvas.pack(side="left")
        tk.Label(pump_row, text="Pump").pack(side="left", padx=5)
        set_tooltip(self.pump_canvas, "Pump control module")

        display_row = tk.Frame(frame)
        display_row.pack(pady=2)
        self.display_canvas = tk.Canvas(display_row, width=20, height=20)
        self.display_canvas.pack(side="left")
        tk.Label(display_row, text="OLED Display").pack(side="left", padx=5)
        set_tooltip(self.display_canvas, "Displays runtime + status")

        self.diagnostic_label = tk.Label(frame, text="", font=("Arial", 10), fg="red")
        self.diagnostic_label.pack(pady=3)

        self.moisture_label = tk.Label(frame, text="Moisture: ---%", font=("Arial", 14))
        self.moisture_label.pack(pady=5)

        self.runtime_label = tk.Label(frame, text="Pump Runtime: 0.00 sec", font=("Arial", 12))
        self.runtime_label.pack(pady=5)

    def build_controls(self):
        frame = self.tab_controls

        tk.Button(frame, text="Manual ON", command=self.pump.turn_on, bg="green", fg="white", width=20).pack(pady=3)
        tk.Button(frame, text="Manual OFF", command=self.pump.turn_off, bg="red", fg="white", width=20).pack(pady=3)

        tk.Label(frame, text="Run Pump (sec):").pack()
        self.timed_entry = tk.Entry(frame)
        self.timed_entry.insert(0, "5")
        self.timed_entry.pack()
        tk.Button(frame, text="Run Timed", command=self.run_timed, bg="blue", fg="white").pack(pady=3)

        pulse_frame = tk.Frame(frame)
        pulse_frame.pack(pady=3)
        tk.Label(pulse_frame, text="Test Pulse Settings:").grid(row=0, column=0, columnspan=2)
        tk.Label(pulse_frame, text="Duration").grid(row=1, column=0)
        tk.Entry(pulse_frame, textvariable=self.test_pulse_duration, width=6).grid(row=1, column=1)
        tk.Label(pulse_frame, text="On Time").grid(row=2, column=0)
        tk.Entry(pulse_frame, textvariable=self.test_pulse_on, width=6).grid(row=2, column=1)
        tk.Label(pulse_frame, text="Off Time").grid(row=3, column=0)
        tk.Entry(pulse_frame, textvariable=self.test_pulse_off, width=6).grid(row=3, column=1)

        tk.Button(frame, text="Test Pulse", command=self.test_pulse, bg="purple", fg="white").pack(pady=3)

    def build_settings(self):
        frame = self.tab_settings
        tk.Label(frame, text="Simulation Options", font=("Arial", 12, "bold")).pack(pady=10)

        tk.Checkbutton(frame, text="Simulate Moisture Sensor", variable=self.sim_sensor,
                       command=self.update_sim_components).pack(anchor="w")
        tk.Checkbutton(frame, text="Simulate Pump Output", variable=self.sim_pump,
                       command=self.update_sim_components).pack(anchor="w")
        tk.Checkbutton(frame, text="Simulate OLED Display", variable=self.sim_display,
                       command=self.update_sim_components).pack(anchor="w")

        tk.Label(frame, text="Simulated Moisture %:").pack(pady=(10, 0))
        tk.Scale(frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.sim_moisture).pack()

    def build_devtools(self):
        frame = self.tab_devtools
        tk.Label(frame, text="Developer Tools", font=("Arial", 12, "bold")).pack(pady=10)

        tk.Button(
            frame,
            text="Reset Watering Cooldown",
            command=self.reset_cooldown,
            bg="orange",
            fg="black",
            width=30
        ).pack(pady=5)

        tk.Label(frame, text="Manually clear daily lockout for testing.").pack(pady=2)

    def reset_cooldown(self):
        self.cooldown.reset()
        log_event("🧪 Watering cooldown manually reset.")
        self.update_ui()

    def update_ui(self):
        self.moisture = self.sensor.read_moisture_percent()
        self.moisture_label.config(
            text=f"Moisture: {self.moisture:.1f}%" if self.moisture is not None else "Moisture: ---"
        )
        self.runtime_label.config(
            text=f"Pump Runtime: {self.pump.get_runtime_seconds():.2f} sec"
        )

        self.display.draw_status(
            moisture=self.moisture,
            pump_status=self.pump.get_status(),
            runtime_sec=self.pump.get_runtime_seconds()
        )

        create_status_circle(self.sensor_canvas, "good" if self.moisture is not None else "bad")
        create_status_circle(self.pump_canvas, "good" if self.pump else "bad")
        create_status_circle(self.display_canvas, "good" if self.display else "bad")

        self.diagnostic_label.config(
            text="⚠️ Moisture sensor not detected or failed to read."
            if self.moisture is None else ""
        )

        self.root.after(REFRESH_INTERVAL_SEC * 1000, self.update_ui)

    def automation_loop(self):
        while True:
            time.sleep(REFRESH_INTERVAL_SEC)

            if self.auto_watering_active:
                continue

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
                    self.auto_watering_active = True

                    self.pump.run_timed(1)
                    time.sleep(1.1)
                    self.pump.start_pulsing(0.3125, 0.3125, 15)

                    self.cooldown.mark_watered()
                    log_to_csv(self.moisture, "WATERED")
                    log_event("⏳ Waiting 30 seconds...")
                    time.sleep(30)

                    self.auto_watering_active = False
                else:
                    log_event("🛑 Already watered in the last 24 hrs.")
            else:
                log_event("✅ Moisture sufficient.")

    def run_timed(self):
        try:
            duration = float(self.timed_entry.get())
            if duration > 0:
                self.pump.run_timed(duration)
                log_event(f"⏱️ Manual timed pump run: {duration}s")
        except ValueError:
            log_event("❌ Invalid manual duration entry")

    def test_pulse(self):
        run_test_pulse(
            self.pump,
            duration=self.test_pulse_duration.get(),
            on_time=self.test_pulse_on.get(),
            off_time=self.test_pulse_off.get()
        )
        log_event("🔁 Test pulse triggered")
        self.update_ui()


if __name__ == "__main__":
    print("✅ Bonsai Assistant GUI started.")
    root = tk.Tk()
    app = BonsaiApp(root)
    root.mainloop()
