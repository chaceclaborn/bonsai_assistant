# File: main.py - Fixed Controls Layout and Mock Switching

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

# UI Components and Theme
from ui.dashboard_tab import DashboardTab
from ui.mini_status_widget import MiniStatusWidget
from ui.professional_theme import (
    BonsaiTheme, setup_professional_style, create_bonsai_header,
    create_professional_card, create_status_card, create_action_button,
    create_info_panel, add_separator, create_section_header
)


class ImprovedControlsTab:
    """Improved controls tab with proper spacing and scrolling"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        self.frame = ttk.Frame(parent)
        self.frame.configure(style='TFrame')
        self._create_controls()
    
    def _create_controls(self):
        """Create improved controls interface with proper scrolling"""
        # Main container
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill="both", expand=True, padx=BonsaiTheme.SPACING['lg'], 
                           pady=BonsaiTheme.SPACING['md'])
        
        # Mini status at top (fixed)
        self.mini_status = MiniStatusWidget(main_container, self.app.automation, self.app.pump)
        self.mini_status.frame.pack(fill="x", pady=(0, BonsaiTheme.SPACING['lg']))
        
        # Scrollable content area
        self._create_scrollable_controls(main_container)
    
    def _create_scrollable_controls(self, parent):
        """Create scrollable controls area"""
        # Canvas for scrolling
        canvas = tk.Canvas(parent, bg=BonsaiTheme.COLORS['bg_main'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Create sections with proper spacing
        self._create_manual_controls_section(scrollable_frame)
        self._create_timed_operations_section(scrollable_frame)
        self._create_pulse_controls_section(scrollable_frame)
        self._create_system_info_section(scrollable_frame)
    
    def _create_manual_controls_section(self, parent):
        """Create manual controls with proper spacing"""
        create_section_header(parent, "🎮 Manual Pump Controls", 1)
        
        controls_card = create_professional_card(parent, "Direct Pump Operation")
        controls_card.pack(fill="x", pady=(0, BonsaiTheme.SPACING['xl']))
        
        # Current status - larger display
        status_frame = ttk.Frame(controls_card)
        status_frame.pack(fill="x", pady=(0, BonsaiTheme.SPACING['lg']))
        
        self.pump_status_card, self.pump_status_label, self.pump_status_title = create_status_card(
            status_frame, "Pump Status", "CHECKING...", "", "normal"
        )
        self.pump_status_card.pack(fill="x")
        
        # Control buttons - bigger and better spaced
        button_frame = ttk.Frame(controls_card)
        button_frame.pack(fill="x", pady=BonsaiTheme.SPACING['lg'])
        
        # ON button
        on_button = create_action_button(button_frame, "🟢 TURN ON PUMP", 
                                       self._turn_on, "primary")
        on_button.pack(side="left", padx=(0, BonsaiTheme.SPACING['md']), 
                      fill="x", expand=True, ipady=BonsaiTheme.SPACING['md'])
        
        # OFF button  
        off_button = create_action_button(button_frame, "🔴 TURN OFF PUMP", 
                                        self._turn_off, "normal")
        off_button.pack(side="right", padx=(BonsaiTheme.SPACING['md'], 0), 
                       fill="x", expand=True, ipady=BonsaiTheme.SPACING['md'])
        
        # Status message area
        self.manual_status = ttk.Label(controls_card, text="Ready for manual operation",
                                      font=BonsaiTheme.FONTS['body'],
                                      foreground=BonsaiTheme.COLORS['text_muted'])
        self.manual_status.pack(pady=BonsaiTheme.SPACING['md'])
        
        # Runtime info panel - bigger
        runtime_info = create_info_panel(controls_card, "Runtime Information", {
            "Total Runtime": "0.0 seconds",
            "Current Session": "0.0 seconds", 
            "Last Operation": "None",
            "Operation Count": "0"
        })
        runtime_info.pack(fill="x", pady=(BonsaiTheme.SPACING['lg'], 0))
        self.runtime_info = runtime_info
    
    def _create_timed_operations_section(self, parent):
        """Create timed operations with better layout"""
        create_section_header(parent, "⏱️ Timed Operations", 1)
        
        timed_card = create_professional_card(parent, "Scheduled Pump Control")
        timed_card.pack(fill="x", pady=(0, BonsaiTheme.SPACING['xl']))
        
        # Description
        desc_label = ttk.Label(timed_card, 
                              text="Run the pump for a specific duration with automatic shutoff",
                              font=BonsaiTheme.FONTS['body'],
                              foreground=BonsaiTheme.COLORS['text_muted'])
        desc_label.pack(anchor="w", pady=(0, BonsaiTheme.SPACING['lg']))
        
        # Duration control - larger and better spaced
        duration_container = ttk.Frame(timed_card)
        duration_container.pack(fill="x", pady=BonsaiTheme.SPACING['md'])
        
        # Duration label
        duration_label = ttk.Label(duration_container, text="Duration (seconds):",
                                  font=BonsaiTheme.FONTS['heading_small'],
                                  foreground=BonsaiTheme.COLORS['text_primary'])
        duration_label.pack(anchor="w", pady=(0, BonsaiTheme.SPACING['sm']))
        
        # Duration input row
        input_row = ttk.Frame(duration_container)
        input_row.pack(fill="x", pady=(0, BonsaiTheme.SPACING['lg']))
        
        self.duration_var = tk.StringVar(value="5")
        duration_entry = ttk.Entry(input_row, textvariable=self.duration_var, 
                                  font=BonsaiTheme.FONTS['heading_small'], width=15)
        duration_entry.pack(side="left", ipady=BonsaiTheme.SPACING['sm'])
        
        # Run button - bigger
        run_button = create_action_button(input_row, "▶️ RUN TIMED", 
                                        self._run_timed, "primary")
        run_button.pack(side="right", ipady=BonsaiTheme.SPACING['sm'], 
                       ipadx=BonsaiTheme.SPACING['lg'])
        
        # Quick presets - bigger buttons
        presets_label = ttk.Label(timed_card, text="Quick Duration Presets:",
                                 font=BonsaiTheme.FONTS['body_bold'],
                                 foreground=BonsaiTheme.COLORS['text_primary'])
        presets_label.pack(anchor="w", pady=(BonsaiTheme.SPACING['lg'], BonsaiTheme.SPACING['sm']))
        
        presets_frame = ttk.Frame(timed_card)
        presets_frame.pack(fill="x", pady=(0, BonsaiTheme.SPACING['md']))
        
        preset_data = [(3, "3 sec"), (5, "5 sec"), (10, "10 sec"), (30, "30 sec"), (60, "1 min")]
        for seconds, label in preset_data:
            preset_btn = ttk.Button(presets_frame, text=label,
                                   command=lambda s=seconds: self._set_duration(s))
            preset_btn.pack(side="left", padx=(0, BonsaiTheme.SPACING['sm']), 
                           fill="x", expand=True, ipady=BonsaiTheme.SPACING['xs'])
        
        # Status area
        self.timed_status = ttk.Label(timed_card, text="Ready for timed operation",
                                     font=BonsaiTheme.FONTS['body'],
                                     foreground=BonsaiTheme.COLORS['success'])
        self.timed_status.pack(pady=BonsaiTheme.SPACING['md'])
    
    def _create_pulse_controls_section(self, parent):
        """Create pulse controls with proper spacing"""
        create_section_header(parent, "🔄 Advanced Pulse Watering", 1)
        
        pulse_card = create_professional_card(parent, "Intelligent Pulse System")
        pulse_card.pack(fill="x", pady=(0, BonsaiTheme.SPACING['xl']))
        
        # Description
        desc_text = ("Pulse watering delivers water in controlled bursts for optimal soil absorption. "
                    "This prevents runoff and ensures deep root hydration.")
        desc_label = ttk.Label(pulse_card, text=desc_text, wraplength=600,
                              font=BonsaiTheme.FONTS['body'],
                              foreground=BonsaiTheme.COLORS['text_muted'])
        desc_label.pack(anchor="w", pady=(0, BonsaiTheme.SPACING['lg']))
        
        # Pulse settings - better grid layout
        settings_label = ttk.Label(pulse_card, text="Pulse Configuration:",
                                  font=BonsaiTheme.FONTS['heading_small'],
                                  foreground=BonsaiTheme.COLORS['text_primary'])
        settings_label.pack(anchor="w", pady=(0, BonsaiTheme.SPACING['md']))
        
        settings_frame = ttk.Frame(pulse_card)
        settings_frame.pack(fill="x", pady=(0, BonsaiTheme.SPACING['lg']))
        
        # Configure grid weights for better spacing
        settings_frame.columnconfigure(1, weight=1)
        
        settings_data = [
            ("Total Duration:", "15", "pulse_duration_var", "Total time for entire pulse sequence"),
            ("ON Time:", "0.3125", "pulse_on_var", "Duration pump runs during each pulse"),
            ("OFF Time:", "0.3125", "pulse_off_var", "Pause between each pulse")
        ]
        
        self.pulse_vars = {}
        
        for i, (label_text, default_val, var_name, help_text) in enumerate(settings_data):
            # Label
            label = ttk.Label(settings_frame, text=label_text,
                             font=BonsaiTheme.FONTS['body_bold'])
            label.grid(row=i*2, column=0, sticky="w", pady=(BonsaiTheme.SPACING['sm'], 0))
            
            # Help text
            help_label = ttk.Label(settings_frame, text=help_text,
                                  font=BonsaiTheme.FONTS['caption'],
                                  foreground=BonsaiTheme.COLORS['text_muted'])
            help_label.grid(row=i*2+1, column=0, columnspan=2, sticky="w", 
                           pady=(0, BonsaiTheme.SPACING['md']))
            
            # Entry
            var = tk.StringVar(value=default_val)
            self.pulse_vars[var_name] = var
            
            entry = ttk.Entry(settings_frame, textvariable=var, width=15,
                             font=BonsaiTheme.FONTS['body'])
            entry.grid(row=i*2, column=1, sticky="e", pady=(BonsaiTheme.SPACING['sm'], 0),
                      padx=(BonsaiTheme.SPACING['lg'], 0))
        
        # Control buttons - bigger and better spaced
        button_frame = ttk.Frame(pulse_card)
        button_frame.pack(fill="x", pady=BonsaiTheme.SPACING['lg'])
        
        start_button = create_action_button(button_frame, "🚀 START PULSING", 
                                          self._start_pulsing, "primary")
        start_button.pack(side="left", padx=(0, BonsaiTheme.SPACING['md']), 
                         fill="x", expand=True, ipady=BonsaiTheme.SPACING['md'])
        
        stop_button = create_action_button(button_frame, "⏹️ STOP PULSING", 
                                         self._stop_pulsing, "normal")
        stop_button.pack(side="right", padx=(BonsaiTheme.SPACING['md'], 0), 
                        fill="x", expand=True, ipady=BonsaiTheme.SPACING['md'])
        
        # Status area
        self.pulse_status = ttk.Label(pulse_card, text="Pulse system ready",
                                     font=BonsaiTheme.FONTS['body'],
                                     foreground=BonsaiTheme.COLORS['success'])
        self.pulse_status.pack(pady=BonsaiTheme.SPACING['md'])
    
    def _create_system_info_section(self, parent):
        """Create system info section"""
        create_section_header(parent, "📊 System Information", 1)
        
        info_card = create_professional_card(parent, "Real-time System Status")
        info_card.pack(fill="x", pady=(0, BonsaiTheme.SPACING['xl']))
        
        # System metrics
        self.system_info = create_info_panel(info_card, "Current Status", {
            "Automation": "Checking...",
            "Moisture Level": "Reading...",
            "Last Watering": "Never",  
            "Next Available": "Calculating...",
            "Hardware Mode": "Detecting..."
        })
        self.system_info.pack(fill="x")
    
    def _turn_on(self):
        """Turn pump on with better feedback"""
        try:
            self.app.pump.turn_on()
            self._update_manual_status("✅ Pump manually activated", "success")
        except Exception as e:
            self._update_manual_status(f"❌ Error: {str(e)}", "error")
    
    def _turn_off(self):
        """Turn pump off with better feedback"""
        try:
            self.app.pump.turn_off()
            self._update_manual_status("🛑 Pump manually deactivated", "info")
        except Exception as e:
            self._update_manual_status(f"❌ Error: {str(e)}", "error")
    
    def _run_timed(self):
        """Run pump for specified duration"""
        try:
            duration = float(self.duration_var.get())
            if duration > 0:
                self.app.pump.run_timed(duration)
                self._update_timed_status(f"⏱️ Running pump for {duration} seconds", "success")
                # Auto-clear after duration + 2 seconds
                self.frame.after(int((duration + 2) * 1000), 
                                lambda: self._update_timed_status("Ready for timed operation", "normal"))
            else:
                self._update_timed_status("❌ Duration must be greater than 0", "error")
        except ValueError:
            self._update_timed_status("❌ Please enter a valid number", "error")
        except Exception as e:
            self._update_timed_status(f"❌ Error: {str(e)}", "error")
    
    def _set_duration(self, seconds):
        """Set duration preset"""
        self.duration_var.set(str(seconds))
        self._update_timed_status(f"⚙️ Duration set to {seconds} seconds", "info")
    
    def _start_pulsing(self):
        """Start pulse watering"""
        try:
            duration = float(self.pulse_vars['pulse_duration_var'].get())
            on_time = float(self.pulse_vars['pulse_on_var'].get())
            off_time = float(self.pulse_vars['pulse_off_var'].get())
            
            if duration > 0 and on_time > 0 and off_time >= 0:
                self.app.pump.start_pulsing(on_time, off_time, duration)
                cycles = int(duration / (on_time + off_time))
                self._update_pulse_status(
                    f"🔄 Pulsing: {cycles} cycles • {on_time}s ON, {off_time}s OFF • Total: {duration}s", 
                    "info"
                )
                # Auto-clear after completion
                self.frame.after(int((duration + 2) * 1000),
                                lambda: self._update_pulse_status("Pulse system ready", "normal"))
            else:
                self._update_pulse_status("❌ All values must be greater than 0", "error")
        except ValueError:
            self._update_pulse_status("❌ Please enter valid numbers", "error")
        except Exception as e:
            self._update_pulse_status(f"❌ Error: {str(e)}", "error")
    
    def _stop_pulsing(self):
        """Stop pulse watering"""
        try:
            self.app.pump.stop_pulsing()
            self._update_pulse_status("⏹️ Pulse operation stopped manually", "warning")
        except Exception as e:
            self._update_pulse_status(f"❌ Error stopping: {str(e)}", "error")
    
    def _update_manual_status(self, message, status_type):
        """Update manual operation status"""
        colors = {
            "success": BonsaiTheme.COLORS['success'],
            "error": BonsaiTheme.COLORS['error'],
            "warning": BonsaiTheme.COLORS['warning'],
            "info": BonsaiTheme.COLORS['info'],
            "normal": BonsaiTheme.COLORS['text_muted']
        }
        
        self.manual_status.config(text=message, 
                                 foreground=colors.get(status_type, BonsaiTheme.COLORS['text_muted']))
        
        if status_type != "normal":
            # Clear after 5 seconds for non-normal status
            self.frame.after(5000, lambda: self.manual_status.config(
                text="Ready for manual operation",
                foreground=BonsaiTheme.COLORS['text_muted']
            ))
    
    def _update_timed_status(self, message, status_type):
        """Update timed operation status"""
        colors = {
            "success": BonsaiTheme.COLORS['success'],
            "error": BonsaiTheme.COLORS['error'],
            "warning": BonsaiTheme.COLORS['warning'],
            "info": BonsaiTheme.COLORS['info'],
            "normal": BonsaiTheme.COLORS['success']
        }
        
        self.timed_status.config(text=message,
                                foreground=colors.get(status_type, BonsaiTheme.COLORS['text_muted']))
    
    def _update_pulse_status(self, message, status_type):
        """Update pulse operation status"""
        colors = {
            "success": BonsaiTheme.COLORS['success'],
            "error": BonsaiTheme.COLORS['error'],
            "warning": BonsaiTheme.COLORS['warning'],
            "info": BonsaiTheme.COLORS['info'],
            "normal": BonsaiTheme.COLORS['success']
        }
        
        self.pulse_status.config(text=message,
                                foreground=colors.get(status_type, BonsaiTheme.COLORS['text_muted']))
    
    def update_display(self):
        """Update controls display"""
        try:
            self.mini_status.update_display()
            
            # Update pump status card
            pump_running = self.app.pump.is_running()
            if pump_running:
                self.pump_status_label.config(text="ACTIVE", 
                                            foreground=BonsaiTheme.COLORS['success'])
            else:
                self.pump_status_label.config(text="IDLE", 
                                            foreground=BonsaiTheme.COLORS['text_muted'])
            
            # Update system info
            status = self.app.automation.get_status()
            
            # Update system info panel (this would need proper implementation)
            automation_status = "RUNNING" if status.get('running') else "STOPPED"
            moisture = status.get('last_moisture')
            moisture_text = f"{moisture:.1f}%" if moisture is not None else "No reading"
            
            # Get hardware types
            sensor_type = "Mock" if isinstance(self.app.sensor, MockSoilMoistureSensor) else "Real"
            pump_type = "Mock" if isinstance(self.app.pump, MockPumpController) else "Real"
            
        except Exception as e:
            print(f"Error updating controls display: {e}")


class FixedSettingsTab:
    """Fixed settings tab with proper mock switching"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        self.frame = ttk.Frame(parent)
        self._create_settings()
    
    def _create_settings(self):
        """Create settings interface with fixed mock switching"""
        # Main container
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill="both", expand=True, padx=BonsaiTheme.SPACING['lg'], 
                           pady=BonsaiTheme.SPACING['md'])
        
        # Mini status at top
        self.mini_status = MiniStatusWidget(main_container, self.app.automation, self.app.pump)
        self.mini_status.frame.pack(fill="x", pady=(0, BonsaiTheme.SPACING['lg']))
        
        # Two column layout
        columns_frame = ttk.Frame(main_container)
        columns_frame.pack(fill="both", expand=True)
        
        left_column = ttk.Frame(columns_frame)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, BonsaiTheme.SPACING['md']))
        
        right_column = ttk.Frame(columns_frame)
        right_column.pack(side="right", fill="both", expand=True, padx=(BonsaiTheme.SPACING['md'], 0))
        
        # System Settings
        self._create_system_settings(left_column)
        
        # Fixed Simulation Controls
        self._create_fixed_simulation_controls(right_column)
        
        # Tools section at bottom
        add_separator(main_container)
        self._create_tools_section(main_container)
    
    def _create_system_settings(self, parent):
        """Create system configuration settings"""
        settings_card = create_professional_card(parent, "⚙️ System Configuration")
        settings_card.pack(fill="both", expand=True)
        
        # Moisture threshold
        create_section_header(settings_card, "Watering Threshold", 2)
        
        threshold_frame = ttk.Frame(settings_card)
        threshold_frame.pack(fill="x", pady=BonsaiTheme.SPACING['md'])
        
        ttk.Label(threshold_frame, text="Moisture Threshold (%):",
                 font=BonsaiTheme.FONTS['body']).pack(anchor="w")
        
        self.threshold_var = tk.StringVar(value=str(self.app.config.sensor.moisture_threshold))
        
        threshold_container = ttk.Frame(threshold_frame)
        threshold_container.pack(fill="x", pady=BonsaiTheme.SPACING['xs'])
        
        threshold_spin = ttk.Spinbox(threshold_container, from_=10, to=80, 
                                   textvariable=self.threshold_var, width=8)
        threshold_spin.pack(side="left")
        
        threshold_label = ttk.Label(threshold_container, text="% (Water when below this level)",
                                   font=BonsaiTheme.FONTS['caption'],
                                   foreground=BonsaiTheme.COLORS['text_muted'])
        threshold_label.pack(side="left", padx=(BonsaiTheme.SPACING['sm'], 0))
        
        # Cooldown period
        create_section_header(settings_card, "Safety Cooldown", 2)
        
        cooldown_frame = ttk.Frame(settings_card)
        cooldown_frame.pack(fill="x", pady=BonsaiTheme.SPACING['md'])
        
        ttk.Label(cooldown_frame, text="Watering Cooldown (hours):",
                 font=BonsaiTheme.FONTS['body']).pack(anchor="w")
        
        self.cooldown_var = tk.StringVar(value=str(self.app.config.system.watering_cooldown_hours))
        
        cooldown_container = ttk.Frame(cooldown_frame)
        cooldown_container.pack(fill="x", pady=BonsaiTheme.SPACING['xs'])
        
        cooldown_spin = ttk.Spinbox(cooldown_container, from_=1, to=72,
                                  textvariable=self.cooldown_var, width=8)
        cooldown_spin.pack(side="left")
        
        cooldown_label = ttk.Label(cooldown_container, text="hours (Prevent over-watering)",
                                  font=BonsaiTheme.FONTS['caption'],
                                  foreground=BonsaiTheme.COLORS['text_muted'])
        cooldown_label.pack(side="left", padx=(BonsaiTheme.SPACING['sm'], 0))
        
        # Auto-save notice
        notice_label = ttk.Label(settings_card,
                               text="💾 Settings are saved automatically as you type",
                               font=BonsaiTheme.FONTS['caption'],
                               foreground=BonsaiTheme.COLORS['success'])
        notice_label.pack(pady=BonsaiTheme.SPACING['md'])
        
        # Bind change events
        self.threshold_var.trace('w', lambda *args: self._on_settings_change())
        self.cooldown_var.trace('w', lambda *args: self._on_settings_change())
    
    def _create_fixed_simulation_controls(self, parent):
        """Create FIXED simulation controls"""
        sim_card = create_professional_card(parent, "🧪 Hardware Simulation")
        sim_card.pack(fill="both", expand=True)
        
        # Hardware status display
        self.hardware_status_labels = {}
        
        status_frame = ttk.Frame(sim_card)
        status_frame.pack(fill="x", pady=(0, BonsaiTheme.SPACING['md']))
        
        # Current hardware status
        create_section_header(status_frame, "Current Hardware Status", 3)
        
        for component in ["Sensor", "Pump", "Display"]:
            comp_frame = ttk.Frame(status_frame)
            comp_frame.pack(fill="x", pady=BonsaiTheme.SPACING['xs'])
            
            ttk.Label(comp_frame, text=f"{component}:",
                     font=BonsaiTheme.FONTS['body']).pack(side="left")
            
            status_label = ttk.Label(comp_frame, text="Checking...",
                                   font=BonsaiTheme.FONTS['body_bold'])
            status_label.pack(side="right")
            
            self.hardware_status_labels[component.lower()] = status_label
        
        # Simulation toggles
        create_section_header(sim_card, "Simulation Controls", 2)
        
        # Initialize simulation state properly
        self.sim_sensor_var = tk.BooleanVar(value=isinstance(self.app.sensor, MockSoilMoistureSensor))
        self.sim_pump_var = tk.BooleanVar(value=isinstance(self.app.pump, MockPumpController))
        self.sim_display_var = tk.BooleanVar(value=isinstance(self.app.display, MockDisplay))
        
        sim_frame = ttk.Frame(sim_card)
        sim_frame.pack(fill="x", pady=BonsaiTheme.SPACING['sm'])
        
        ttk.Checkbutton(sim_frame, text="🔬 Simulate Moisture Sensor",
                       variable=self.sim_sensor_var,
                       command=self._fixed_update_simulation).pack(anchor="w", pady=2)
        
        ttk.Checkbutton(sim_frame, text="⚙️ Simulate Water Pump",
                       variable=self.sim_pump_var,
                       command=self._fixed_update_simulation).pack(anchor="w", pady=2)
        
        ttk.Checkbutton(sim_frame, text="📺 Simulate OLED Display",
                       variable=self.sim_display_var, 
                       command=self._fixed_update_simulation).pack(anchor="w", pady=2)
        
        # Mock moisture control
        create_section_header(sim_card, "Mock Moisture Level", 2)
        
        moisture_frame = ttk.Frame(sim_card)
        moisture_frame.pack(fill="x", pady=BonsaiTheme.SPACING['md'])
        
        self.mock_moisture_var = tk.DoubleVar(value=45.0)
        
        # Slider
        moisture_scale = ttk.Scale(moisture_frame, from_=0, to=100,
                                 orient=tk.HORIZONTAL, variable=self.mock_moisture_var,
                                 command=self._update_mock_moisture)
        moisture_scale.pack(fill="x", pady=BonsaiTheme.SPACING['xs'])
        
        # Value display
        self.moisture_value_label = ttk.Label(moisture_frame, text="45.0%",
                                            font=BonsaiTheme.FONTS['heading_small'],
                                            foreground=BonsaiTheme.COLORS['success'])
        self.moisture_value_label.pack(pady=BonsaiTheme.SPACING['xs'])
        
        # Quick presets
        presets_frame = ttk.Frame(moisture_frame)
        presets_frame.pack(fill="x", pady=BonsaiTheme.SPACING['sm'])
        
        preset_data = [("Critical", 15, BonsaiTheme.COLORS['error']),
                      ("Low", 25, BonsaiTheme.COLORS['warning']),
                      ("Good", 50, BonsaiTheme.COLORS['success']),
                      ("High", 80, BonsaiTheme.COLORS['info'])]
        
        for name, value, color in preset_data:
            btn = ttk.Button(presets_frame, text=f"{name}\n{value}%",
                           command=lambda v=value: self._set_moisture(v))
            btn.pack(side="left", padx=(0, BonsaiTheme.SPACING['xs']), fill="x", expand=True)
        
        # Status message area
        self.sim_status = ttk.Label(sim_card, text="Simulation controls ready",
                                   font=BonsaiTheme.FONTS['body'],
                                   foreground=BonsaiTheme.COLORS['success'])
        self.sim_status.pack(pady=BonsaiTheme.SPACING['md'])
        
        # Update initial display
        self._update_hardware_status()
    
    def _fixed_update_simulation(self):
        """FIXED simulation switching - properly handles real hardware fallback AND status updates"""
        try:
            # Show status
            self._update_sim_status("🔄 Switching hardware components...", "info")
            
            # Stop automation temporarily
            was_running = self.app.automation.running
            if was_running:
                self.app.automation.stop_automation()
            
            # Update SENSOR
            if self.sim_sensor_var.get():
                # Switch to mock sensor
                if not isinstance(self.app.sensor, MockSoilMoistureSensor):
                    self.app.sensor = MockSoilMoistureSensor(lambda: self.mock_moisture_var.get())
                    self._update_sim_status("✅ Switched to mock sensor", "success")
            else:
                # Switch to real sensor
                if isinstance(self.app.sensor, MockSoilMoistureSensor):
                    try:
                        self.app.sensor = SoilMoistureSensor(
                            channel=self.app.config.sensor.i2c_channel,
                            debug=False
                        )
                        self._update_sim_status("✅ Switched to real sensor", "success")
                    except Exception as e:
                        self._update_sim_status(f"⚠️ Real sensor failed: {str(e)[:50]}...", "warning")
                        # Revert checkbox and stay with mock
                        self.sim_sensor_var.set(True)
                        self.app.sensor = MockSoilMoistureSensor(lambda: self.mock_moisture_var.get())
            
            # Update PUMP
            if self.sim_pump_var.get():
                # Switch to mock pump
                if not isinstance(self.app.pump, MockPumpController):
                    # Properly close old pump
                    try:
                        if hasattr(self.app.pump, 'close'):
                            self.app.pump.close()
                    except Exception as e:
                        print(f"Error closing old pump: {e}")
                    
                    self.app.pump = MockPumpController()
                    self._update_sim_status("✅ Switched to mock pump", "success")
            else:
                # Switch to real pump
                if isinstance(self.app.pump, MockPumpController):
                    try:
                        # Close mock pump
                        try:
                            self.app.pump.close()
                        except:
                            pass
                        
                        # Initialize real pump
                        self.app.pump = PumpController(gpio_pin=self.app.config.pump.gpio_pin)
                        self._update_sim_status("✅ Switched to real pump", "success")
                    except Exception as e:
                        self._update_sim_status(f"⚠️ Real pump failed: {str(e)[:50]}...", "warning")
                        # Revert checkbox and stay with mock
                        self.sim_pump_var.set(True)
                        self.app.pump = MockPumpController()
            
            # Update DISPLAY
            if self.sim_display_var.get():
                # Switch to mock display
                if not isinstance(self.app.display, MockDisplay):
                    self.app.display = MockDisplay()
                    self._update_sim_status("✅ Switched to mock display", "success")
            else:
                # Switch to real display
                if isinstance(self.app.display, MockDisplay):
                    try:
                        self.app.display = RGBDisplayDriver(
                            width=self.app.config.display.width,
                            height=self.app.config.display.height,
                            rotation=self.app.config.display.rotation
                        )
                        self._update_sim_status("✅ Switched to real display", "success")
                    except Exception as e:
                        self._update_sim_status(f"⚠️ Real display failed: {str(e)[:50]}...", "warning")
                        # Revert checkbox and stay with mock
                        self.sim_display_var.set(True)
                        self.app.display = MockDisplay()
            
            # CRITICAL: Update automation with new components
            self.app.automation.sensor = self.app.sensor
            self.app.automation.pump = self.app.pump
            self.app.automation.display = self.app.display
            
            # CRITICAL: Force immediate UI status updates across all components
            self._force_status_updates()
            
            # Restart automation if it was running
            if was_running:
                self.app.automation.start_automation()
            
            # Update hardware status display
            self._update_hardware_status()
            
            # Clear status after 3 seconds
            self.frame.after(3000, lambda: self._update_sim_status("Simulation controls ready", "normal"))
            
        except Exception as e:
            self._update_sim_status(f"❌ Error switching: {str(e)}", "error")
            print(f"Detailed simulation switching error: {e}")
    
    def _force_status_updates(self):
        """Force immediate status updates across all UI components"""
        try:
            # Force mini status widget updates on all tabs
            if hasattr(self.app.controls_tab, 'mini_status'):
                self.app.controls_tab.mini_status.update_display()
            if hasattr(self.app.dashboard_tab, 'update_display'):
                self.app.dashboard_tab.update_display()
            
            # Force main status bar update
            self.app._update_status_bar()
            
            # Force settings tab hardware status update
            self._update_hardware_status()
            
            print("🔄 Forced status updates across all UI components")
            
        except Exception as e:
            print(f"Error forcing status updates: {e}")
    
    def _update_sim_status(self, message, status_type):
        """Update simulation status message"""
        colors = {
            "success": BonsaiTheme.COLORS['success'],
            "error": BonsaiTheme.COLORS['error'],
            "warning": BonsaiTheme.COLORS['warning'],
            "info": BonsaiTheme.COLORS['info'],
            "normal": BonsaiTheme.COLORS['success']
        }
        
        self.sim_status.config(text=message,
                              foreground=colors.get(status_type, BonsaiTheme.COLORS['text_muted']))
    
    def _on_settings_change(self):
        """Handle settings changes"""
        try:
            threshold = int(self.threshold_var.get())
            cooldown = int(self.cooldown_var.get())
            
            self.app.config_manager.update('sensor', moisture_threshold=threshold)
            self.app.config_manager.update('system', watering_cooldown_hours=cooldown)
            
            self.app.config = self.app.config_manager.get()
            self.app.automation.config = self.app.config
            self.app.cooldown_manager.cooldown_sec = cooldown * 3600
            
        except ValueError:
            pass  # Ignore invalid values during typing
    
    def _update_mock_moisture(self, value):
        """Update mock moisture display"""
        moisture = float(value)
        self.moisture_value_label.config(text=f"{moisture:.1f}%")
        
        # Color based on threshold
        try:
            threshold = float(self.threshold_var.get())
        except:
            threshold = 30
            
        if moisture < threshold * 0.5:
            color = BonsaiTheme.COLORS['error']
        elif moisture < threshold:
            color = BonsaiTheme.COLORS['warning'] 
        else:
            color = BonsaiTheme.COLORS['success']
        
        self.moisture_value_label.config(foreground=color)
    
    def _set_moisture(self, value):
        """Set mock moisture to preset"""
        self.mock_moisture_var.set(value)
        self._update_mock_moisture(value)
    
    def _update_hardware_status(self):
        """Update hardware status display"""
        try:
            # Sensor status
            if isinstance(self.app.sensor, MockSoilMoistureSensor):
                self.hardware_status_labels['sensor'].config(
                    text="🔬 Mock Sensor", 
                    foreground=BonsaiTheme.COLORS['info']
                )
            else:
                self.hardware_status_labels['sensor'].config(
                    text="📡 Real Hardware", 
                    foreground=BonsaiTheme.COLORS['success']
                )
            
            # Pump status
            if isinstance(self.app.pump, MockPumpController):
                self.hardware_status_labels['pump'].config(
                    text="🔬 Mock Pump", 
                    foreground=BonsaiTheme.COLORS['info']
                )
            else:
                self.hardware_status_labels['pump'].config(
                    text="⚙️ Real Hardware", 
                    foreground=BonsaiTheme.COLORS['success']
                )
            
            # Display status
            if isinstance(self.app.display, MockDisplay):
                self.hardware_status_labels['display'].config(
                    text="🔬 Mock Display", 
                    foreground=BonsaiTheme.COLORS['info']
                )
            else:
                self.hardware_status_labels['display'].config(
                    text="📺 Real Hardware", 
                    foreground=BonsaiTheme.COLORS['success']
                )
                
        except Exception as e:
            print(f"Error updating hardware status: {e}")
    
    def _create_tools_section(self, parent):
        """Create tools and utilities"""
        tools_card = create_professional_card(parent, "🔧 System Tools")
        tools_card.pack(fill="x", pady=BonsaiTheme.SPACING['md'])
        
        # Tools buttons
        button_frame = ttk.Frame(tools_card)
        button_frame.pack(fill="x")
        
        tools_data = [
            ("⏰ Reset Cooldown", self._reset_cooldown, "Allows immediate watering"),
            ("🧹 Cleanup Data", self._cleanup_data, "Remove old logs and readings"),
            ("📤 Export Data", self._export_data, "Export plant data to CSV")
        ]
        
        for i, (text, command, description) in enumerate(tools_data):
            tool_frame = ttk.Frame(button_frame)
            tool_frame.pack(fill="x", pady=BonsaiTheme.SPACING['xs'])
            
            btn = create_action_button(tool_frame, text, command, "normal")
            btn.pack(side="left")
            
            desc_label = ttk.Label(tool_frame, text=f"• {description}",
                                  font=BonsaiTheme.FONTS['caption'],
                                  foreground=BonsaiTheme.COLORS['text_muted'])
            desc_label.pack(side="left", padx=(BonsaiTheme.SPACING['md'], 0))
    
    def _reset_cooldown(self):
        """Reset watering cooldown"""
        self.app.cooldown_manager.reset()
        
    def _cleanup_data(self):
        """Cleanup old data"""
        try:
            self.app.data_manager.cleanup_old_data(self.app.config.system.log_retention_days)
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    def _export_data(self):
        """Export data"""
        print("Export feature coming soon!")
    
    def update_display(self):
        """Update settings display"""
        self.mini_status.update_display()
        self._update_hardware_status()


class BonsaiAssistantApp:
    """Beautiful Professional Bonsai Care Assistant with FIXED controls and simulation"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🌱 Bonsai Assistant Professional v2.0")
        self.root.geometry("1100x750")  # More compact but still roomy
        self.root.minsize(900, 650)
        
        # Setup professional styling
        self.style = setup_professional_style(root)
        
        # Initialize core components
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get()
        self.data_manager = DataManager()
        
        # Initialize hardware
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
        
        # Setup beautiful UI
        self._setup_ui()
        self._setup_callbacks()
        self._start_systems()
    
    def _init_hardware_components(self):
        """Initialize hardware with graceful fallbacks"""
        try:
            self.sensor = SoilMoistureSensor(channel=self.config.sensor.i2c_channel, debug=False)
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
        """Setup beautiful UI with bonsai theme"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True)
        
        # Beautiful header with bonsai art
        self.header = create_bonsai_header(main_container)
        self.header.pack(fill="x", padx=BonsaiTheme.SPACING['lg'], 
                        pady=(BonsaiTheme.SPACING['lg'], BonsaiTheme.SPACING['md']))
        
        # Create notebook with professional tabs
        self.notebook = ttk.Notebook(main_container)
        
        # Initialize beautiful tabs with FIXED components
        self.dashboard_tab = DashboardTab(self.notebook, self.automation, 
                                        self.data_manager, self.config)
        
        self.controls_tab = ImprovedControlsTab(self.notebook, self)  # IMPROVED
        self.settings_tab = FixedSettingsTab(self.notebook, self)     # FIXED
        
        # Add tabs with beautiful icons
        self.notebook.add(self.dashboard_tab.frame, text="🏠  Dashboard")
        self.notebook.add(self.controls_tab.frame, text="🎮  Controls") 
        self.notebook.add(self.settings_tab.frame, text="⚙️  Settings")
        
        self.notebook.pack(fill="both", expand=True, 
                          padx=BonsaiTheme.SPACING['lg'],
                          pady=(0, BonsaiTheme.SPACING['lg']))
        
        # Beautiful status bar
        self._create_status_bar()
    
    def _create_status_bar(self):
        """Create beautiful status bar"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.configure(style='Card.TFrame')
        self.status_bar.pack(side="bottom", fill="x", padx=BonsaiTheme.SPACING['lg'], 
                            pady=(0, BonsaiTheme.SPACING['md']))
        
        # Status container
        status_container = ttk.Frame(self.status_bar)
        status_container.pack(fill="x", padx=BonsaiTheme.SPACING['md'], 
                             pady=BonsaiTheme.SPACING['sm'])
        
        # Left side status
        self.status_automation = ttk.Label(status_container, 
                                         text="🤖 Automation: Starting...",
                                         font=BonsaiTheme.FONTS['body_bold'],
                                         foreground=BonsaiTheme.COLORS['primary_green'])
        self.status_automation.pack(side="left")
        
        # Separator
        ttk.Separator(status_container, orient="vertical").pack(side="left", fill="y", 
                                                               padx=BonsaiTheme.SPACING['md'])
        
        # Connection status
        self.status_connection = ttk.Label(status_container,
                                         text="📡 Sensors: Checking...",
                                         font=BonsaiTheme.FONTS['body'])
        self.status_connection.pack(side="left")
        
        # Right side - time
        self.status_time = ttk.Label(status_container, text="",
                                   font=BonsaiTheme.FONTS['caption'],
                                   foreground=BonsaiTheme.COLORS['text_muted'])
        self.status_time.pack(side="right")
    
    def _setup_callbacks(self):
        """Setup automation callbacks"""
        self.automation.add_state_callback(self._on_plant_state_changed)
        self.automation.add_moisture_callback(self._on_moisture_update)
        self._schedule_ui_updates()
    
    def _start_systems(self):
        """Start automation systems"""
        self.automation.start_automation()
        self.data_manager.log_system_event("APP_START", 
                                          "Bonsai Assistant Professional started", "INFO")
    
    def _schedule_ui_updates(self):
        """Schedule regular UI updates"""
        self._update_status_bar()
        
        # Update all tabs
        self.dashboard_tab.update_display()
        self.controls_tab.update_display()
        self.settings_tab.update_display()
        
        # Schedule next update
        self.root.after(self.config.display.update_interval * 1000, self._schedule_ui_updates)
    
    def _update_status_bar(self):
        """Update beautiful status bar with FIXED hardware detection"""
        try:
            status = self.automation.get_status()
            
            # Automation status with colors
            if status.get('automation_active'):
                auto_text = "🤖 Automation: 💧 WATERING"
                auto_color = BonsaiTheme.COLORS['info']
            elif status.get('running'):
                auto_text = "🤖 Automation: ✅ ACTIVE"
                auto_color = BonsaiTheme.COLORS['success']
            else:
                auto_text = "🤖 Automation: ⏸️ STOPPED"
                auto_color = BonsaiTheme.COLORS['warning']
            
            self.status_automation.config(text=auto_text, foreground=auto_color)
            
            # FIXED: Connection status with proper hardware detection
            moisture = status.get('last_moisture')
            
            # Test actual sensor responsiveness
            sensor_working = False
            try:
                test_reading = self.sensor.read_moisture_percent()
                sensor_working = test_reading is not None
            except:
                sensor_working = False
            
            if sensor_working and moisture is not None:
                conn_text = f"📡 Sensors: ✅ CONNECTED ({moisture:.1f}%)"
                conn_color = BonsaiTheme.COLORS['success']
                
                # Add hardware type indicator
                sensor_type = "Mock" if isinstance(self.sensor, MockSoilMoistureSensor) else "Real"
                conn_text += f" [{sensor_type}]"
            else:
                conn_text = "📡 Sensors: ❌ DISCONNECTED"
                conn_color = BonsaiTheme.COLORS['error']
            
            self.status_connection.config(text=conn_text, foreground=conn_color)
            
            # Time
            current_time = datetime.now().strftime("%Y-%m-%d  •  %H:%M:%S")
            self.status_time.config(text=current_time)
            
        except Exception as e:
            print(f"Error updating status bar: {e}")
            # Fallback display
            self.status_automation.config(text="🤖 Automation: ❌ ERROR", 
                                        foreground=BonsaiTheme.COLORS['error'])
            self.status_connection.config(text="📡 Sensors: ❌ ERROR", 
                                        foreground=BonsaiTheme.COLORS['error'])
    
    def _on_plant_state_changed(self, old_state: PlantState, new_state: PlantState):
        """Handle plant state changes"""
        self.dashboard_tab.on_state_changed(old_state, new_state)
        
        # Show status updates
        if new_state == PlantState.CRITICAL:
            self._show_status("🚨 CRITICAL: Emergency watering initiated!", BonsaiTheme.COLORS['error'])
        elif new_state == PlantState.SENSOR_ERROR:
            self._show_status("❌ SENSOR ERROR: Check connections", BonsaiTheme.COLORS['error'])
    
    def _on_moisture_update(self, moisture: float):
        """Handle moisture updates"""
        self.display.draw_status(
            moisture=moisture,
            pump_status=self.pump.get_status(),
            runtime_sec=self.pump.get_runtime_seconds()
        )
        self.dashboard_tab.on_moisture_update(moisture)
    
    def _show_status(self, message: str, color: str):
        """Show temporary status message"""
        original_text = self.status_automation.cget("text")
        original_color = self.status_automation.cget("foreground")
        
        self.status_automation.config(text=message, foreground=color)
        
        # Restore after 5 seconds
        self.root.after(5000, lambda: self.status_automation.config(
            text=original_text, foreground=original_color))


def main():
    """Launch the beautiful Bonsai Assistant"""
    root = tk.Tk()
    
    # Create beautiful app
    app = BonsaiAssistantApp(root)
    
    # Graceful exit
    root.protocol("WM_DELETE_WINDOW", lambda: (
        app.automation.stop_automation(),
        app.data_manager.log_system_event("APP_SHUTDOWN", "Professional shutdown", "INFO"),
        root.destroy()
    ))
    
    print("🌱 Bonsai Assistant Professional v2.0 - FIXED Edition Started! 🌿")
    root.mainloop()


if __name__ == "__main__":
    main()