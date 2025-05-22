# File: utils/status_icons.py

import tkinter as tk

def create_status_circle(canvas, status="unknown"):
    color_map = {
        "good": "#2ecc71",   # Green
        "bad": "#e74c3c",    # Red
        "unknown": "#bdc3c7" # Gray
    }
    canvas.delete("all")
    canvas.create_oval(2, 2, 18, 18, fill=color_map.get(status, "#bdc3c7"), outline="black")

def set_tooltip(widget, text):
    def on_enter(e):
        widget.tooltip = tk.Toplevel(widget)
        widget.tooltip.wm_overrideredirect(True)
        x = widget.winfo_rootx() + 20
        y = widget.winfo_rooty() + 20
        widget.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(widget.tooltip, text=text, background="yellow", relief="solid", borderwidth=1)
        label.pack()
    def on_leave(e):
        if hasattr(widget, "tooltip"):
            widget.tooltip.destroy()
            widget.tooltip = None
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)
