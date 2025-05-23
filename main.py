# File: main.py - Fixed with Inline UI and Working Simulation

import tkinter as tk
from tkinter import ttk
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# Hardware components
from hardware.display.rgb_display_driver import RGBDisplayDriver
from hardware.sensors.soil_moisture_sensor import SoilMoistureSensor
from hardware.actuators.pump_controller import PumpController

# Core components
from core.timing import WateringCooldownManager
from core.automation_controller import AutomationController, PlantState
from core.data_manager import DataManager
from config.app_config import ConfigManager

# Simulation components
from simulation.mock_sensor import MockSoilMoistureSensor
from simulation.mock_pump import MockPumpController
from simulation.mock_display import MockDisplay

# UI Components
from ui.dashboard_tab import DashboardTab
from ui.mini_status_widget import MiniStatusWidget


class ControlsTab:
    """Controls tab with mini status and inline interface"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        self.frame = ttk.Frame(parent)
        self._create_controls()
    
    def _create_controls(self):
        """Create controls interface"""
        # Mini status at top
        self.mini_status = MiniStatusWidget(self.frame, self.app.automation, self.app.pump)
        self.mini_status.frame.pack(fill="x", padx=10, pady=5)
        
        # Manual controls section
        manual_frame = ttk.LabelFrame(self.frame, text="Manual Controls", padding=15)
        manual_frame.pack(fill="x", padx=10, pady=5)
        
        # ON/OFF buttons
        button_frame = ttk.Frame(manual_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(
            button_frame, 
            text="Turn ON", 
            command=self.app.pump.turn_on,
            style="Accent.TButton"
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame, 
            text="Turn OFF", 
            command=self.app.pump.turn_off
        ).pack(side="left", padx=5)
        
        # Timed run section
        timed_frame = ttk.LabelFrame(self.frame, text="Timed Operation", padding=15)
        timed_frame.pack(fill="x", padx=10, pady=5)
        
        # Duration input
        duration_frame = ttk.Frame(timed_frame)
        duration_frame.pack(pady=5)
        
        ttk.Label(duration_frame, text="Duration (seconds):").pack(side="left")
        self.duration_var = tk.StringVar(value="5")
        ttk.Entry(duration_frame, textvariable=self.duration_var, width=10).pack(side="left", padx=5)
        
        ttk.Button(
            duration_frame, 
            text="Run Timed", 
            command=self._run_timed
        ).pack(side="left", padx=5)
        
        # Status display for timed run
        self.timed_status = ttk.Label(timed_frame, text="", foreground="#28a745")
        self.timed_status.pack(pady=5)
        
        # Pulse settings section
        pulse_frame = ttk.LabelFrame(self.frame, text="Pulse Settings", padding=15)
        pulse_frame.pack(fill="x", padx=10, pady=5)
        
        # Pulse duration
        pulse_controls = ttk.Frame(pulse_frame)
        pulse_controls.pack(fill="x")
        
        ttk.Label(pulse_controls, text="Total Duration:").grid(row=0, column=0, sticky="w", pady=2)
        self.pulse_duration_var = tk.StringVar(value="15")
        ttk.Entry(pulse_controls, textvariable=self.pulse_duration_var, width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(pulse_controls, text="ON Time:").grid(row=1, column=0, sticky="w", pady=2)
        self.pulse_on_var = tk.StringVar(value="0.3125")
        ttk.Entry(pulse_controls, textvariable=self.pulse_on_var, width=10).grid(row=1, column=1, padx=5)
        
        ttk.Label(pulse_controls, text="OFF Time:").grid(row=2, column=0, sticky="w", pady=2)
        self.pulse_off_var = tk.StringVar(value="0.3125")
        ttk.Entry(pulse_controls, textvariable=self.pulse_off_var, width=10).grid(row=2, column=1, padx=5)
        
        pulse_button_frame = ttk.Frame(pulse_frame)
        pulse_button_frame.pack(pady=10)
        
        ttk.Button(
            pulse_button_frame, 
            text="Start Pulsing", 
            command=self._start_pulsing
        ).pack(side="left", padx=5)
        
        ttk.Button(
            pulse_button_frame, 
            text="Stop Pulsing", 
            command=self.app.pump.stop_pulsing
        ).pack(side="left", padx=5)
        
        # Status display for pulse
        self.pulse_status = ttk.Label(pulse_frame, text="", foreground="#007bff")
        self.pulse_status.pack(pady=5)
    
    def _run_timed(self):
        """Run pump for specified duration"""
        try:
            duration = float(self.duration_var.get())
            if duration > 0:
                self.app.pump.run_timed(duration)
                self.timed_status.config(text=f"✅ Pump will run for {duration} seconds")
                # Clear status after a few seconds
                self.frame.after(3000, lambda: self.timed_status.config(text=""))
        except ValueError:
            self.timed_status.config(text="❌ Please enter a valid duration", foreground="#dc3545")
    
    def _start_pulsing(self):
        """Start pulse watering"""
        try:
            duration = float(self.pulse_duration_var.get())
            on_time = float(self.pulse_on_var.get())
            off_time = float(self.pulse_off_var.get())
            
            if duration > 0 and on_time > 0 and off_time >= 0:
                self.app.pump.start_pulsing(on_time, off_time, duration)
                self.pulse_status.config(text=f"✅ Pulsing for {duration} seconds", foreground="#007bff")
                # Clear status after duration + 2 seconds
                self.frame.after(int((duration + 2) * 1000), lambda: self.pulse_status.config(text=""))
        except ValueError:
            self.pulse_status.config(text="❌ Please enter valid pulse settings", foreground="#dc3545")
    
    def update_display(self):
        """Update mini status display"""
        self.mini_status.update_display()


class SettingsTab:
    """Inline settings tab with live simulation controls"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        self.frame = ttk.Frame(parent)
        self._create_settings()
    
    def _create_settings(self):
        """Create inline settings interface"""
        # Mini status at top
        self.mini_status = MiniStatusWidget(self.frame, self.app.automation, self.app.pump)
        self.mini_status.frame.pack(fill="x", padx=10, pady=5)
        
        # Create main container with two columns
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Left column - System Settings
        left_column = ttk.Frame(main_container)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Right column - Simulation
        right_column = ttk.Frame(main_container)
        right_column.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # System Settings
        self._create_system_settings(left_column)
        
        # Simulation Settings
        self._create_simulation_settings(right_column)
        
        # Tools section at bottom
        self._create_tools_section(self.frame)
    
    def _create_system_settings(self, parent):
        """Create system configuration settings"""
        system_frame = ttk.LabelFrame(parent, text="System Configuration", padding=15)
        system_frame.pack(fill="both", expand=True, pady=5)
        
        # Moisture threshold
        threshold_frame = ttk.Frame(system_frame)
        threshold_frame.pack(fill="x", pady=5)
        
        ttk.Label(threshold_frame, text="Moisture Threshold (%):").pack(side="left")
        self.threshold_var = tk.StringVar(value=str(self.app.config.sensor.moisture_threshold))
        threshold_spin = ttk.Spinbox(
            threshold_frame, 
            from_=10, to=80, 
            textvariable=self.threshold_var,
            width=10,
            command=self._on_settings_change
        )
        threshold_spin.pack(side="left", padx=5)
        
        # Bind manual entry changes
        self.threshold_var.trace('w', lambda *args: self._on_settings_change())
        
        # Cooldown hours
        cooldown_frame = ttk.Frame(system_frame)
        cooldown_frame.pack(fill="x", pady=5)
        
        ttk.Label(cooldown_frame, text="Watering Cooldown (hours):").pack(side="left")
        self.cooldown_var = tk.StringVar(value=str(self.app.config.system.watering_cooldown_hours))
        cooldown_spin = ttk.Spinbox(
            cooldown_frame, 
            from_=1, to=72, 
            textvariable=self.cooldown_var,
            width=10,
            command=self._on_settings_change
        )
        cooldown_spin.pack(side="left", padx=5)
        
        self.cooldown_var.trace('w', lambda *args: self._on_settings_change())
        
        # Settings status
        self.settings_status = ttk.Label(system_frame, text="", foreground="#28a745")
        self.settings_status.pack(pady=10)
    
    def _create_simulation_settings(self, parent):
        """Create simulation controls"""
        sim_frame = ttk.LabelFrame(parent, text="Simulation Controls", padding=15)
        sim_frame.pack(fill="both", expand=True, pady=5)
        
        # Current hardware status
        status_frame = ttk.Frame(sim_frame)
        status_frame.pack(fill="x", pady=5)
        
        ttk.Label(status_frame, text="Current Hardware:", font=("Arial", 9, "bold")).pack(anchor="w")
        self.hardware_status = ttk.Label(status_frame, text="", font=("Arial", 8))
        self.hardware_status.pack(anchor="w", padx=10)
        
        # Simulation toggles
        self.sim_sensor_var = tk.BooleanVar(value=isinstance(self.app.sensor, MockSoilMoistureSensor))
        self.sim_pump_var = tk.BooleanVar(value=isinstance(self.app.pump, MockPumpController))
        self.sim_display_var = tk.BooleanVar(value=isinstance(self.app.display, MockDisplay))
        
        sensor_cb = ttk.Checkbutton(
            sim_frame, 
            text="Simulate Moisture Sensor", 
            variable=self.sim_sensor_var,
            command=self._update_simulation
        )
        sensor_cb.pack(anchor="w", pady=2)
        
        pump_cb = ttk.Checkbutton(
            sim_frame, 
            text="Simulate Pump", 
            variable=self.sim_pump_var,
            command=self._update_simulation
        )
        pump_cb.pack(anchor="w", pady=2)
        
        display_cb = ttk.Checkbutton(
            sim_frame, 
            text="Simulate Display", 
            variable=self.sim_display_var,
            command=self._update_simulation
        )
        display_cb.pack(anchor="w", pady=2)
        
        # Mock moisture level
        mock_frame = ttk.Frame(sim_frame)
        mock_frame.pack(fill="x", pady=10)
        
        ttk.Label(mock_frame, text="Mock Moisture Level:").pack(anchor="w")
        
        # Moisture slider with live update
        self.mock_moisture_var = tk.DoubleVar(value=45.0)
        moisture_scale = ttk.Scale(
            mock_frame, 
            from_=0, to=100, 
            orient=tk.HORIZONTAL,
            variable=self.mock_moisture_var,
            command=self._update_mock_moisture
        )
        moisture_scale.pack(fill="x", pady=2)
        
        # Moisture value display
        self.moisture_value_label = ttk.Label(mock_frame, text="45.0%", font=("Arial", 9, "bold"))
        self.moisture_value_label.pack(anchor="w")
        
        # Quick preset buttons
        preset_frame = ttk.Frame(mock_frame)
        preset_frame.pack(fill="x", pady=5)
        
        ttk.Button(preset_frame, text="Dry (20%)", command=lambda: self._set_moisture(20)).pack(side="left", padx=2)
        ttk.Button(preset_frame, text="Low (25%)", command=lambda: self._set_moisture(25)).pack(side="left", padx=2)
        ttk.Button(preset_frame, text="Good (50%)", command=lambda: self._set_moisture(50)).pack(side="left", padx=2)
        ttk.Button(preset_frame, text="Wet (80%)", command=lambda: self._set_moisture(80)).pack(side="left", padx=2)
        
        # Simulation status
        self.sim_status = ttk.Label(sim_frame, text="", foreground="#007bff")
        self.sim_status.pack(pady=5)
        
        # Update initial display
        self._update_hardware_status()
    
    def _create_tools_section(self, parent):
        """Create tools and utilities section"""
        tools_frame = ttk.LabelFrame(parent, text="Tools & Utilities", padding=15)
        tools_frame.pack(fill="x", padx=10, pady=5)
        
        # Tools buttons
        button_frame = ttk.Frame(tools_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(
            button_frame, 
            text="Reset Cooldown", 
            command=self._reset_cooldown
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame, 
            text="Cleanup Old Data", 
            command=self._cleanup_data
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame, 
            text="Export Data", 
            command=self._export_data
        ).pack(side="left", padx=5)
        
        # Tools status
        self.tools_status = ttk.Label(tools_frame, text="", foreground="#28a745")
        self.tools_status.pack(pady=5)
    
    def _on_settings_change(self):
        """Handle settings changes with live update"""
        try:
            # Update configuration
            threshold = int(self.threshold_var.get())
            cooldown = int(self.cooldown_var.get())
            
            self.app.config_manager.update('sensor', moisture_threshold=threshold)
            self.app.config_manager.update('system', watering_cooldown_hours=cooldown)
            
            # Update the app's config reference
            self.app.config = self.app.config_manager.get()
            
            # Update automation parameters
            self.app.automation.config = self.app.config
            self.app.cooldown_manager.cooldown_sec = cooldown * 3600
            
            self.app.data_manager.log_system_event(
                "SETTINGS_CHANGED", 
                f"Threshold: {threshold}%, Cooldown: {cooldown}h", 
                "INFO"
            )
            
            self.settings_status.config(text="✅ Settings updated automatically", foreground="#28a745")
            # Clear status after 3 seconds
            self.frame.after(3000, lambda: self.settings_status.config(text=""))
            
        except ValueError:
            self.settings_status.config(text="❌ Please enter valid values", foreground="#dc3545")
    
    def _update_simulation(self):
        """Update simulation components in real-time"""
        try:
            # Stop automation temporarily
            was_running = self.app.automation.running
            if was_running:
                self.app.automation.stop_automation()
            
            # Update sensor
            if self.sim_sensor_var.get():
                if not isinstance(self.app.sensor, MockSoilMoistureSensor):
                    self.app.sensor = MockSoilMoistureSensor(lambda: self.mock_moisture_var.get())
                    self.sim_status.config(text="✅ Switched to mock sensor", foreground="#007bff")
            else:
                if isinstance(self.app.sensor, MockSoilMoistureSensor):
                    try:
                        self.app.sensor = SoilMoistureSensor(
                            channel=self.app.config.sensor.i2c_channel,
                            debug=False
                        )
                        self.sim_status.config(text="✅ Switched to real sensor", foreground="#007bff")
                    except Exception as e:
                        self.sim_status.config(text=f"⚠️ Real sensor failed, keeping mock: {str(e)}", foreground="#ffc107")
                        self.sim_sensor_var.set(True)
            
            # Update pump
            if self.sim_pump_var.get():
                if not isinstance(self.app.pump, MockPumpController):
                    # Close old pump
                    try:
                        if hasattr(self.app.pump, 'close'):
                            self.app.pump.close()
                    except:
                        pass
                    self.app.pump = MockPumpController()
                    self.sim_status.config(text="✅ Switched to mock pump", foreground="#007bff")
            else:
                if isinstance(self.app.pump, MockPumpController):
                    try:
                        self.app.pump.close()
                        self.app.pump = PumpController(gpio_pin=self.app.config.pump.gpio_pin)
                        self.sim_status.config(text="✅ Switched to real pump", foreground="#007bff")
                    except Exception as e:
                        self.sim_status.config(text=f"⚠️ Real pump failed, keeping mock: {str(e)}", foreground="#ffc107")
                        self.sim_pump_var.set(True)
            
            # Update display
            if self.sim_display_var.get():
                if not isinstance(self.app.display, MockDisplay):
                    self.app.display = MockDisplay()
                    self.sim_status.config(text="✅ Switched to mock display", foreground="#007bff")
            else:
                if isinstance(self.app.display, MockDisplay):
                    try:
                        self.app.display = RGBDisplayDriver(
                            width=self.app.config.display.width,
                            height=self.app.config.display.height,
                            rotation=self.app.config.display.rotation
                        )
                        self.sim_status.config(text="✅ Switched to real display", foreground="#007bff")
                    except Exception as e:
                        self.sim_status.config(text=f"⚠️ Real display failed, keeping mock: {str(e)}", foreground="#ffc107")
                        self.sim_display_var.set(True)
            
            # Update automation with new components
            self.app.automation.sensor = self.app.sensor
            self.app.automation.pump = self.app.pump
            self.app.automation.display = self.app.display
            
            # Restart automation if it was running
            if was_running:
                self.app.automation.start_automation()
            
            self._update_hardware_status()
            
            # Clear status after 3 seconds
            self.frame.after(3000, lambda: self.sim_status.config(text=""))
            
        except Exception as e:
            self.sim_status.config(text=f"❌ Simulation update failed: {str(e)}", foreground="#dc3545")
    
    def _update_mock_moisture(self, value):
        """Update mock moisture value display"""
        moisture = float(value)
        self.moisture_value_label.config(text=f"{moisture:.1f}%")
        
        # Update color based on threshold
        threshold = float(self.threshold_var.get()) if self.threshold_var.get().isdigit() else 30
        if moisture < threshold * 0.7:
            color = "#dc3545"  # Red - critical
        elif moisture < threshold:
            color = "#ffc107"  # Yellow - low
        else:
            color = "#28a745"  # Green - good
        
        self.moisture_value_label.config(foreground=color)
    
    def _set_moisture(self, value):
        """Set mock moisture to specific value"""
        self.mock_moisture_var.set(value)
        self._update_mock_moisture(value)
    
    def _update_hardware_status(self):
        """Update hardware status display"""
        sensor_type = "Mock" if isinstance(self.app.sensor, MockSoilMoistureSensor) else "Real"
        pump_type = "Mock" if isinstance(self.app.pump, MockPumpController) else "Real"
        display_type = "Mock" if isinstance(self.app.display, MockDisplay) else "Real"
        
        status_text = f"Sensor: {sensor_type} | Pump: {pump_type} | Display: {display_type}"
        self.hardware_status.config(text=status_text)
    
    def _reset_cooldown(self):
        """Reset watering cooldown"""
        self.app.cooldown_manager.reset()
        self.app.data_manager.log_system_event("COOLDOWN_RESET", "Watering cooldown manually reset", "INFO")
        self.tools_status.config(text="✅ Watering cooldown has been reset", foreground="#28a745")
        self.frame.after(3000, lambda: self.tools_status.config(text=""))
    
    def _cleanup_data(self):
        """Manually trigger data cleanup"""
        try:
            self.app.data_manager.cleanup_old_data(self.app.config.system.log_retention_days)
            self.tools_status.config(text="✅ Old data has been cleaned up successfully", foreground="#28a745")
        except Exception as e:
            self.tools_status.config(text=f"❌ Cleanup error: {str(e)}", foreground="#dc3545")
        self.frame.after(5000, lambda: self.tools_status.config(text=""))
    
    def _export_data(self):
        """Export data feature"""
        self.tools_status.config(text="📤 Data export feature coming soon!", foreground="#007bff")
        self.frame.after(3000, lambda: self.tools_status.config(text=""))
    
    def update_display(self):
        """Update mini status display"""
        self.mini_status.update_display()


class DiagnosticsTab:
    """Inline diagnostics tab"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        self.frame = ttk.Frame(parent)
        self._create_diagnostics()
    
    def _create_diagnostics(self):
        """Create inline diagnostics interface"""
        # Mini status at top
        self.mini_status = MiniStatusWidget(self.frame, self.app.automation, self.app.pump)
        self.mini_status.frame.pack(fill="x", padx=10, pady=5)
        
        # Diagnostics display
        diag_frame = ttk.LabelFrame(self.frame, text="System Diagnostics", padding=15)
        diag_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create text widget with scrollbar
        text_container = ttk.Frame(diag_frame)
        text_container.pack(fill="both", expand=True)
        
        self.text_widget = tk.Text(text_container, wrap="word", font=("Courier", 9))
        scrollbar = ttk.Scrollbar(text_container, orient="vertical", command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        self.text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Auto-refresh button
        refresh_frame = ttk.Frame(self.frame)
        refresh_frame.pack(fill="x", padx=10, pady=5)
        
        self.auto_refresh_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            refresh_frame, 
            text="Auto-refresh every 5 seconds", 
            variable=self.auto_refresh_var
        ).pack(side="left")
        
        ttk.Button(
            refresh_frame, 
            text="Refresh Now", 
            command=self.update_diagnostics
        ).pack(side="right")
        
        # Initial update
        self.update_diagnostics()
        self._schedule_refresh()
    
    def update_diagnostics(self):
        """Update diagnostics display"""
        try:
            status = self.app.automation.get_status()
            
            diagnostics = f"""SYSTEM STATUS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'='*60}
AUTOMATION STATUS
{'='*60}
Running: {status['running']}
Current State: {status['current_state']}
Last Moisture Reading: {status['last_moisture']}%
Adaptive Threshold: {status['adaptive_threshold']}%
Consecutive Low Readings: {status['consecutive_low_readings']}
Automation Active (Watering): {status['automation_active']}
Can Water (Cooldown): {status['can_water']}

{'='*60}
HARDWARE STATUS
{'='*60}
Sensor Type: {type(self.app.sensor).__name__}
Pump Type: {type(self.app.pump).__name__}
Display Type: {type(self.app.display).__name__}

Pump Runtime: {self.app.pump.get_runtime_seconds()}s
Pump Currently Running: {self.app.pump.is_running()}

{'='*60}
CONFIGURATION
{'='*60}
Moisture Threshold: {self.app.config.sensor.moisture_threshold}%
Cooldown Hours: {self.app.config.system.watering_cooldown_hours}
Refresh Interval: {self.app.config.system.refresh_interval_sec}s
Log Retention Days: {self.app.config.system.log_retention_days}

Sensor Channel: {self.app.config.sensor.i2c_channel}
Pump GPIO Pin: {self.app.config.pump.gpio_pin}

{'='*60}
DATABASE STATUS
{'='*60}
Data Manager: {type(self.app.data_manager).__name__}
Database Path: {self.app.data_manager.db_path}

Recent Activity Summary:
"""
            
            # Add recent activity
            try:
                today_summary = self.app.data_manager.get_daily_summary()
                diagnostics += f"""- Today's Readings: {today_summary.get('readings_count', 0)}
- Today's Watering Events: {today_summary.get('watering_events', 0)}
- Today's Water Time: {today_summary.get('total_water_time', 0):.1f}s
- Avg Moisture Today: {today_summary.get('moisture_avg', 0):.1f}%
"""
                
                watering_events = self.app.data_manager.get_watering_history(days=1)
                if watering_events:
                    diagnostics += f"\nLast Watering: {watering_events[0].timestamp.strftime('%H:%M:%S')}\n"
                else:
                    diagnostics += "\nNo watering events today\n"
            except Exception as e:
                diagnostics += f"\nError loading activity: {str(e)}\n"
            
            diagnostics += f"\n{'='*60}\nLAST UPDATED: {datetime.now().strftime('%H:%M:%S')}"
            
            # Update text widget
            self.text_widget.config(state="normal")
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert("1.0", diagnostics)
            self.text_widget.config(state="disabled")
            
        except Exception as e:
            error_text = f"Error generating diagnostics: {str(e)}\nTime: {datetime.now().strftime('%H:%M:%S')}"
            self.text_widget.config(state="normal")
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert("1.0", error_text)
            self.text_widget.config(state="disabled")
    
    def _schedule_refresh(self):
        """Schedule automatic refresh"""
        if self.auto_refresh_var.get():
            self.update_diagnostics()
        
        # Schedule next refresh
        self.frame.after(5000, self._schedule_refresh)
    
    def update_display(self):
        """Update mini status display"""
        self.mini_status.update_display()


class SimpleTab:
    """Simple placeholder tab with mini status"""
    
    def __init__(self, parent, app, title_text):
        self.app = app
        self.frame = ttk.Frame(parent)
        
        # Mini status at top
        self.mini_status = MiniStatusWidget(self.frame, app.automation, app.pump)
        self.mini_status.frame.pack(fill="x", padx=10, pady=5)
        
        # Create simple content
        container = ttk.Frame(self.frame)
        container.pack(expand=True, fill="both")
        
        ttk.Label(
            container, 
            text=f"{title_text}\n\nThis feature is coming soon!",
            font=("Arial", 12),
            anchor="center"
        ).pack(expand=True)
    
    def update_display(self):
        """Update mini status display"""
        self.mini_status.update_display()


class BonsaiAssistantApp:
    """Professional Bonsai Care Assistant Application with Inline UI"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Bonsai Assistant Professional v2.0")
        self.root.geometry("900x700")
        self.root.minsize(700, 600)
        
        # Initialize core components
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get()
        self.data_manager = DataManager()
        
        # Initialize hardware components
        self._init_hardware_components()
        
        # Initialize automation
        self.cooldown_manager = WateringCooldownManager(
            cooldown_sec=self.config.system.watering_cooldown_hours * 3600
        )
        
        self.automation = AutomationController(
            sensor=self.sensor,
            pump=self.pump,
            display=self.display,
            cooldown_manager=self.cooldown_manager,
            data_manager=self.data_manager,
            config=self.config
        )
        
        # Setup UI
        self._setup_ui()
        self._setup_callbacks()
        
        # Start systems
        self._start_systems()
        
    def _init_hardware_components(self):
        """Initialize hardware components with simulation fallbacks"""
        try:
            self.sensor = SoilMoistureSensor(
                channel=self.config.sensor.i2c_channel,
                debug=False
            )
            print("✅ Real moisture sensor initialized")
        except Exception as e:
            print(f"⚠️ Sensor init failed, using simulation: {e}")
            self.sensor = MockSoilMoistureSensor(lambda: 45.0)
            
        try:
            self.pump = PumpController(gpio_pin=self.config.pump.gpio_pin)
            print("✅ Real pump controller initialized")
        except Exception as e:
            print(f"⚠️ Pump init failed, using simulation: {e}")
            self.pump = MockPumpController()
            
        try:
            self.display = RGBDisplayDriver(
                width=self.config.display.width,
                height=self.config.display.height,
                rotation=self.config.display.rotation
            )
            print("✅ Real display initialized")
        except Exception as e:
            print(f"⚠️ Display init failed, using simulation: {e}")
            self.display = MockDisplay()
    
    def _setup_ui(self):
        """Setup the main UI with tabs"""
        # Create menu bar (simplified, no popups)
        self._create_menu_bar()
        
        # Create status bar
        self._create_status_bar()
        
        # Create main notebook with tabs
        self.notebook = ttk.Notebook(self.root)
        
        # Initialize tab components (all with mini status bars)
        self.dashboard_tab = DashboardTab(
            self.notebook, 
            self.automation,
            self.data_manager,
            self.config
        )
        
        self.controls_tab = ControlsTab(self.notebook, self)
        self.settings_tab = SettingsTab(self.notebook, self)
        self.diagnostics_tab = DiagnosticsTab(self.notebook, self)
        
        # Create simple placeholder tabs
        self.analytics_tab = SimpleTab(self.notebook, self, "Analytics & Graphs")
        self.journal_tab = SimpleTab(self.notebook, self, "Plant Care Journal")
        
        # Add tabs to notebook
        self.notebook.add(self.dashboard_tab.frame, text="🏠 Dashboard")
        self.notebook.add(self.controls_tab.frame, text="🎮 Controls")
        self.notebook.add(self.analytics_tab.frame, text="📊 Analytics")
        self.notebook.add(self.settings_tab.frame, text="⚙️ Settings")
        self.notebook.add(self.diagnostics_tab.frame, text="🔧 Diagnostics")
        self.notebook.add(self.journal_tab.frame, text="📝 Journal")
        
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _create_menu_bar(self):
        """Create simplified menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Data...", command=lambda: self._show_status("Export feature in Settings tab"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_exit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about_inline)
    
    def _create_status_bar(self):
        """Create status bar at bottom of window"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side="bottom", fill="x", padx=5, pady=2)
        
        # Status labels
        self.status_automation = ttk.Label(self.status_bar, text="● Automation: Starting...")
        self.status_automation.pack(side="left")
        
        ttk.Separator(self.status_bar, orient="vertical").pack(side="left", padx=10, fill="y")
        
        self.status_connection = ttk.Label(self.status_bar, text="● Sensors: Checking...")
        self.status_connection.pack(side="left")
        
        # Current time on right
        self.status_time = ttk.Label(self.status_bar, text="")
        self.status_time.pack(side="right")
    
    def _setup_callbacks(self):
        """Setup callbacks for automation events"""
        self.automation.add_state_callback(self._on_plant_state_changed)
        self.automation.add_moisture_callback(self._on_moisture_update)
        
        # Schedule regular UI updates
        self._schedule_ui_updates()
    
    def _start_systems(self):
        """Start automation and other background systems"""
        self.automation.start_automation()
        
        self.data_manager.log_system_event(
            "APP_START", 
            "Bonsai Assistant started successfully", 
            "INFO"
        )
    
    def _schedule_ui_updates(self):
        """Schedule regular UI updates"""
        self._update_status_bar()
        
        # Update all tabs
        self.dashboard_tab.update_display()
        self.controls_tab.update_display()
        self.settings_tab.update_display()
        self.diagnostics_tab.update_display()
        self.analytics_tab.update_display()
        self.journal_tab.update_display()
        
        # Schedule next update
        self.root.after(self.config.display.update_interval * 1000, self._schedule_ui_updates)
    
    def _update_status_bar(self):
        """Update status bar information"""
        try:
            # Update automation status
            status = self.automation.get_status()
            automation_text = "● Automation: Running" if status['running'] else "● Automation: Stopped"
            if status['automation_active']:
                automation_text += " (Watering)"
            self.status_automation.config(text=automation_text)
            
            # Update connection status
            moisture = status.get('last_moisture')
            if moisture is not None:
                connection_text = f"● Sensors: Connected ({moisture:.1f}%)"
            else:
                connection_text = "● Sensors: Disconnected"
            self.status_connection.config(text=connection_text)
            
            # Update time
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.status_time.config(text=current_time)
        except Exception as e:
            print(f"Error updating status bar: {e}")
    
    def _on_plant_state_changed(self, old_state: PlantState, new_state: PlantState):
        """Handle plant state changes with inline notifications"""
        # Update dashboard indicators
        self.dashboard_tab.on_state_changed(old_state, new_state)
        
        # Show inline status instead of popups
        if new_state == PlantState.CRITICAL:
            self._show_status("🚨 CRITICAL: Moisture level critically low! Emergency watering initiated.", "#dc3545")
        elif new_state == PlantState.SENSOR_ERROR:
            self._show_status("❌ SENSOR ERROR: Unable to read moisture sensor. Check connections.", "#dc3545")
    
    def _on_moisture_update(self, moisture: float):
        """Handle moisture reading updates"""
        # Update display
        self.display.draw_status(
            moisture=moisture,
            pump_status=self.pump.get_status(),
            runtime_sec=self.pump.get_runtime_seconds()
        )
        
        # Update dashboard
        self.dashboard_tab.on_moisture_update(moisture)
    
    def _show_status(self, message: str, color: str = "#007bff"):
        """Show status message in status bar"""
        original_text = self.status_automation.cget("text")
        self.status_automation.config(text=message, foreground=color)
        
        # Restore original text after 5 seconds
        self.root.after(5000, lambda: self.status_automation.config(text=original_text, foreground="black"))
    
    def _show_about_inline(self):
        """Show about information inline"""
        self._show_status("Bonsai Assistant Professional v2.0 - Created with ❤️ for plants!")
    
    def _on_exit(self):
        """Handle application exit with inline confirmation"""
        # Simple exit without popup
        try:
            # Stop automation
            self.automation.stop_automation()
            
            # Close hardware
            if hasattr(self.pump, 'close'):
                self.pump.close()
            
            # Log shutdown
            self.data_manager.log_system_event(
                "APP_SHUTDOWN", 
                "Bonsai Assistant shutting down", 
                "INFO"
            )
            
        except Exception as e:
            print(f"Error during shutdown: {e}")
        
        self.root.destroy()


def main():
    """Main application entry point"""
    # Create and configure root window
    root = tk.Tk()
    
    # Create application
    app = BonsaiAssistantApp(root)
    
    # Handle window close
    root.protocol("WM_DELETE_WINDOW", app._on_exit)
    
    # Start main loop
    print("🌱 Bonsai Assistant Professional v2.0 started")
    root.mainloop()


if __name__ == "__main__":
    main()