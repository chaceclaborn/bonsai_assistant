# File: ui/mini_status_widget.py

import tkinter as tk
from tkinter import ttk
from datetime import datetime

class MiniStatusWidget:
    """Compact status widget to show on every tab"""
    
    def __init__(self, parent, automation, pump):
        self.automation = automation
        self.pump = pump
        
        # Create main frame with border
        self.frame = ttk.LabelFrame(parent, text="System Status", padding=8)
        
        # Create horizontal layout
        self.main_container = ttk.Frame(self.frame)
        self.main_container.pack(fill="x")
        
        # Left side - Key metrics
        self.metrics_frame = ttk.Frame(self.main_container)
        self.metrics_frame.pack(side="left", fill="x", expand=True)
        
        # Moisture display
        moisture_frame = ttk.Frame(self.metrics_frame)
        moisture_frame.pack(side="left", padx=5)
        
        ttk.Label(moisture_frame, text="Moisture:", font=("Arial", 9)).pack(side="left")
        self.moisture_label = ttk.Label(moisture_frame, text="---%", font=("Arial", 9, "bold"), foreground="#2c3e50")
        self.moisture_label.pack(side="left", padx=(2, 0))
        
        # Separator
        ttk.Separator(self.metrics_frame, orient="vertical").pack(side="left", fill="y", padx=8)
        
        # Pump status
        pump_frame = ttk.Frame(self.metrics_frame)
        pump_frame.pack(side="left", padx=5)
        
        ttk.Label(pump_frame, text="Pump:", font=("Arial", 9)).pack(side="left")
        self.pump_label = ttk.Label(pump_frame, text="OFF", font=("Arial", 9, "bold"))
        self.pump_label.pack(side="left", padx=(2, 0))
        
        # Separator
        ttk.Separator(self.metrics_frame, orient="vertical").pack(side="left", fill="y", padx=8)
        
        # Automation status
        auto_frame = ttk.Frame(self.metrics_frame)
        auto_frame.pack(side="left", padx=5)
        
        ttk.Label(auto_frame, text="Auto:", font=("Arial", 9)).pack(side="left")
        self.auto_label = ttk.Label(auto_frame, text="Stopped", font=("Arial", 9, "bold"))
        self.auto_label.pack(side="left", padx=(2, 0))
        
        # Right side - Status indicators
        self.indicators_frame = ttk.Frame(self.main_container)
        self.indicators_frame.pack(side="right", padx=10)
        
        # Plant state indicator
        self.plant_canvas = tk.Canvas(self.indicators_frame, width=20, height=20, bg='white')
        self.plant_canvas.pack(side="left", padx=2)
        
        # Sensor indicator  
        self.sensor_canvas = tk.Canvas(self.indicators_frame, width=20, height=20, bg='white')
        self.sensor_canvas.pack(side="left", padx=2)
        
        # Pump indicator
        self.pump_canvas = tk.Canvas(self.indicators_frame, width=20, height=20, bg='white')
        self.pump_canvas.pack(side="left", padx=2)
        
        # Time display
        self.time_label = ttk.Label(self.indicators_frame, text="", font=("Arial", 8))
        self.time_label.pack(side="left", padx=(8, 0))
        
        # Initialize displays
        self.update_display()
    
    def update_display(self):
        """Update all status displays"""
        try:
            # Get current status
            status = self.automation.get_status()
            
            # Update moisture
            moisture = status.get('last_moisture')
            if moisture is not None:
                self.moisture_label.config(text=f"{moisture:.1f}%")
                # Color coding for moisture
                if moisture < 20:
                    color = "#dc3545"  # Red
                elif moisture < 40:
                    color = "#ffc107"  # Yellow  
                else:
                    color = "#28a745"  # Green
                self.moisture_label.config(foreground=color)
            else:
                self.moisture_label.config(text="---", foreground="#6c757d")
            
            # Update pump status
            pump_running = self.pump.is_running()
            pump_text = "ON" if pump_running else "OFF"
            pump_color = "#28a745" if pump_running else "#6c757d"
            self.pump_label.config(text=pump_text, foreground=pump_color)
            
            # Update automation status
            auto_running = status.get('running', False)
            auto_active = status.get('automation_active', False)
            
            if auto_active:
                auto_text = "WATERING"
                auto_color = "#007bff"
            elif auto_running:
                auto_text = "Running"
                auto_color = "#28a745"
            else:
                auto_text = "Stopped"
                auto_color = "#6c757d"
            
            self.auto_label.config(text=auto_text, foreground=auto_color)
            
            # Update indicators
            self._draw_indicator(self.plant_canvas, self._get_plant_color(status.get('current_state', 'unknown')))
            self._draw_indicator(self.sensor_canvas, "#28a745" if moisture is not None else "#dc3545")
            self._draw_indicator(self.pump_canvas, "#28a745" if pump_running else "#6c757d")
            
            # Update time
            current_time = datetime.now().strftime("%H:%M")
            self.time_label.config(text=current_time)
            
        except Exception as e:
            print(f"Error updating mini status: {e}")
    
    def _draw_indicator(self, canvas, color):
        """Draw status indicator circle"""
        canvas.delete("all")
        canvas.create_oval(3, 3, 17, 17, fill=color, outline=color, width=1)
    
    def _get_plant_color(self, state):
        """Get color for plant state"""
        colors = {
            "healthy": "#28a745",
            "needs_water": "#ffc107", 
            "recently_watered": "#17a2b8",
            "critical": "#dc3545",
            "sensor_error": "#6c757d"
        }
        return colors.get(state, "#6c757d")