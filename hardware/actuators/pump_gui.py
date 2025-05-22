import tkinter as tk
from gpiozero import OutputDevice
from gpiozero.pins.lgpio import LGPIOFactory
from time import time

# Setup GPIO18 as HIGH-triggered
factory = LGPIOFactory()
pump = OutputDevice(18, active_high=True, initial_value=False, pin_factory=factory)

root = tk.Tk()
root.title("Pump Control")

# Global states
start_time = None
total_runtime = 0.0
running = False
timed_mode = False
time_remaining = 0
pulsing = False
pulse_on = False
pulse_duration = 0.1
pulse_interval = 0.5

# Labels
status_label = tk.Label(root, text="Pump is OFF", font=("Arial", 14))
status_label.pack(pady=10)

runtime_label = tk.Label(root, text="Total Runtime: 0.00 sec", font=("Arial", 12))
runtime_label.pack(pady=5)

countdown_label = tk.Label(root, text="", font=("Arial", 12), fg="blue")
countdown_label.pack(pady=5)

# Pulse input fields
tk.Label(root, text="Pulse ON Duration (sec):", font=("Arial", 12)).pack()
pulse_on_entry = tk.Entry(root)
pulse_on_entry.insert(0, "0.1")
pulse_on_entry.pack()

tk.Label(root, text="Pulse OFF Interval (sec):", font=("Arial", 12)).pack()
pulse_off_entry = tk.Entry(root)
pulse_off_entry.insert(0, "0.5")
pulse_off_entry.pack()

# Timed run input
tk.Label(root, text="Run for seconds:", font=("Arial", 12)).pack(pady=10)
time_entry = tk.Entry(root)
time_entry.pack()

# Control functions
def update_display():
    global total_runtime, time_remaining, running, timed_mode

    if running and not pulsing:
        now = time() - start_time
        runtime_label.config(text=f"Total Runtime: {total_runtime + now:.2f} sec")

        if timed_mode:
            remaining = time_remaining - int(now)
            if remaining <= 0:
                countdown_label.config(text="Time Remaining: 0 sec")
                turn_off()
                return
            else:
                countdown_label.config(text=f"Time Remaining: {remaining} sec")
        else:
            countdown_label.config(text="")

        root.after(100, update_display)

def pulse_loop():
    global pulse_on, pulsing, total_runtime

    if not pulsing:
        return

    if pulse_on:
        pump.off()
        pulse_on = False
        total_runtime += pulse_duration
        runtime_label.config(text=f"Total Runtime: {total_runtime:.2f} sec")
        root.after(int(pulse_interval * 1000), pulse_loop)
    else:
        pump.on()
        pulse_on = True
        status_label.config(text="Pulsing Mode: ON")
        root.after(int(pulse_duration * 1000), pulse_loop)

def turn_on():
    global start_time, running
    if not pump.value:
        pump.on()
        start_time = time()
        running = True
        status_label.config(text="Pump is ON")
        if not pulsing:
            update_display()

def turn_off():
    global total_runtime, running, timed_mode, pulsing
    if pump.value:
        pump.off()
    if running and not pulsing:
        total_runtime += time() - start_time
    running = False
    timed_mode = False
    pulsing = False
    status_label.config(text="Pump is OFF")
    countdown_label.config(text="")
    runtime_label.config(text=f"Total Runtime: {total_runtime:.2f} sec")

def run_timed():
    global time_remaining, timed_mode
    try:
        seconds = int(time_entry.get())
        if seconds <= 0:
            raise ValueError
        time_remaining = seconds
        timed_mode = True
        turn_on()
    except ValueError:
        status_label.config(text="❌ Invalid time!")

def toggle_pulsing():
    global pulse_duration, pulse_interval, pulsing, pulse_on
    try:
        pulse_duration = float(pulse_on_entry.get())
        pulse_interval = float(pulse_off_entry.get())
        if pulse_duration <= 0 or pulse_interval < 0:
            raise ValueError
        pulsing = not pulsing
        pulse_on = False
        countdown_label.config(text="")
        if pulsing:
            status_label.config(text="Pulsing Mode: ON")
            pulse_loop()
        else:
            turn_off()
    except ValueError:
        status_label.config(text="❌ Invalid pulse times!")

# Buttons
btn_on = tk.Button(root, text="Turn ON", command=turn_on, bg="green", fg="white", width=15, height=2)
btn_on.pack(pady=5)

btn_off = tk.Button(root, text="Turn OFF", command=turn_off, bg="red", fg="white", width=15, height=2)
btn_off.pack(pady=5)

btn_timed = tk.Button(root, text="Run Timed", command=run_timed, bg="blue", fg="white", width=15, height=2)
btn_timed.pack(pady=5)

btn_pulse = tk.Button(root, text="Toggle Pulsing", command=toggle_pulsing, bg="purple", fg="white", width=15, height=2)
btn_pulse.pack(pady=10)

# Run the GUI
root.mainloop()
