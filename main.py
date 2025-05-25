# File: main.py - Fixed Controls Layout, Mock Switching, OLED Display, and Better Layout

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path

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
        self._canvas = None  # Store canvas reference
        self._create_controls()
    
    def _create_controls(self):
        """Create improved controls interface with proper scrolling"""
        # Main container - FIXED: fill entire space
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill="both", expand=True, padx=BonsaiTheme.SPACING['lg'], 
                           pady=BonsaiTheme.SPACING['md'])
        
        # Mini status at top (fixed)
        self.mini_status = MiniStatusWidget(main_container, self.app.automation, self.app.pump)
        self.mini_status.frame.pack(fill="x", pady=(0, BonsaiTheme.SPACING['lg']))
        
        # Scrollable content area
        self._create_scrollable_controls(main_container)
    
    def _create_scrollable_controls(self, parent):
        """Create scrollable controls area - PROFESSIONALLY ALIGNED"""
        # Canvas for scrolling
        canvas = tk.Canvas(parent, bg=BonsaiTheme.COLORS['bg_main'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Store canvas reference
        self._canvas = canvas
        
        # Configure canvas
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def configure_canvas(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Make frame fill canvas width
            if event:
                canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind('<Configure>', configure_canvas)
        scrollable_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Focus management for scrolling
        def on_frame_enter(event):
            canvas.focus_set()
        
        canvas.bind("<Enter>", on_frame_enter)
        scrollable_frame.bind("<Enter>", on_frame_enter)
        
        # Create content with PROFESSIONAL GRID LAYOUT
        content_container = ttk.Frame(scrollable_frame)
        content_container.pack(fill="both", expand=True, padx=BonsaiTheme.SPACING['md'])
        
        # PROFESSIONAL LAYOUT: Create rows for better alignment
        # Row 1: Manual Controls | Timed Operations
        row1_frame = ttk.Frame(content_container)
        row1_frame.pack(fill="x", pady=(0, BonsaiTheme.SPACING['lg']))
        
        # Configure grid weights for equal column widths
        row1_frame.columnconfigure(0, weight=1, uniform="col")
        row1_frame.columnconfigure(1, weight=1, uniform="col")
        
        # Row 1 sections
        manual_container = ttk.Frame(row1_frame)
        manual_container.grid(row=0, column=0, sticky="nsew", padx=(0, BonsaiTheme.SPACING['md']))
        
        timed_container = ttk.Frame(row1_frame)
        timed_container.grid(row=0, column=1, sticky="nsew", padx=(BonsaiTheme.SPACING['md'], 0))
        
        self._create_manual_controls_section(manual_container)
        self._create_timed_operations_section(timed_container)
        
        # Row 2: Pulse Controls | System Info
        row2_frame = ttk.Frame(content_container)
        row2_frame.pack(fill="x")
        
        # Configure grid weights for equal column widths
        row2_frame.columnconfigure(0, weight=1, uniform="col")
        row2_frame.columnconfigure(1, weight=1, uniform="col")
        
        # Row 2 sections
        pulse_container = ttk.Frame(row2_frame)
        pulse_container.grid(row=0, column=0, sticky="nsew", padx=(0, BonsaiTheme.SPACING['md']))
        
        system_container = ttk.Frame(row2_frame)
        system_container.grid(row=0, column=1, sticky="nsew", padx=(BonsaiTheme.SPACING['md'], 0))
        
        self._create_pulse_controls_section(pulse_container)
        self._create_system_info_section(system_container)
    
    def _create_manual_controls_section(self, parent):
        """Create manual controls with proper spacing"""
        create_section_header(parent, "🎮 Manual Pump Controls", 1)
        
        controls_card = create_professional_card(parent, "Direct Pump Operation")
        controls_card.pack(fill="both", expand=True, pady=(0, 0))
        
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
        timed_card.pack(fill="both", expand=True, pady=(0, 0))
        
        # Description
        desc_label = ttk.Label(timed_card, 
                              text="Run the pump for a specific duration with automatic shutoff",
                              font=BonsaiTheme.FONTS['body'],
                              foreground=BonsaiTheme.COLORS['text_muted'],
                              wraplength=400)
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
        pulse_card.pack(fill="both", expand=True, pady=(0, 0))
        
        # Description
        desc_text = ("Pulse watering delivers water in controlled bursts for optimal soil absorption. "
                    "This prevents runoff and ensures deep root hydration.")
        desc_label = ttk.Label(pulse_card, text=desc_text, wraplength=400,
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
        info_card.pack(fill="both", expand=True, pady=(0, 0))
        
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
        """Create settings interface with fixed mock switching and scrolling"""
        # Create scrollable container
        canvas = tk.Canvas(self.frame, bg=BonsaiTheme.COLORS['bg_main'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configure canvas
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def configure_canvas(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Make frame fill canvas width
            if event:
                canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind('<Configure>', configure_canvas)
        scrollable_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel scrolling
        def _on_mousewheel(event):
            if event.delta:
                canvas.yview_scroll(-1*(event.delta//120), "units")
            else:
                if event.num == 4:
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    canvas.yview_scroll(1, "units")
        
        # Bind to canvas and frame
        canvas.bind("<MouseWheel>", _on_mousewheel)  # Windows
        canvas.bind("<Button-4>", _on_mousewheel)    # Linux
        canvas.bind("<Button-5>", _on_mousewheel)    # Linux
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<Button-4>", _on_mousewheel)
        scrollable_frame.bind("<Button-5>", _on_mousewheel)
        
        # Focus on mouse enter
        def on_enter(event):
            canvas.focus_set()
        canvas.bind("<Enter>", on_enter)
        scrollable_frame.bind("<Enter>", on_enter)
        
        # Main container inside scrollable frame
        main_container = ttk.Frame(scrollable_frame)
        main_container.pack(fill="both", expand=True, padx=BonsaiTheme.SPACING['lg'], 
                           pady=BonsaiTheme.SPACING['md'])
        
        # Mini status at top
        self.mini_status = MiniStatusWidget(main_container, self.app.automation, self.app.pump)
        self.mini_status.frame.pack(fill="x", pady=(0, BonsaiTheme.SPACING['lg']))
        
        # Two column layout - FIXED: expand to fill space
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
        
        # NEW: Calibration section - make sure it's visible
        add_separator(main_container)
        self._create_calibration_section(main_container)
        
        # Add some padding at bottom for scrolling
        ttk.Frame(main_container).pack(pady=BonsaiTheme.SPACING['xl'])
    
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
        sim_card.pack(fill="both", expand=True, pady=(0, BonsaiTheme.SPACING['md']))
        
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
                            debug=False,
                            dry_calibration=self.app.config.sensor.calibration_dry,
                            wet_calibration=self.app.config.sensor.calibration_wet
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
        self._update_cal_status("✅ Cooldown timer reset! Watering available immediately.", "success")
        
    def _cleanup_data(self):
        """Cleanup old data with user confirmation"""
        # Create confirmation dialog
        result = tk.messagebox.askyesno(
            "Cleanup Data", 
            f"This will remove moisture readings older than 7 days and logs older than {self.app.config.system.log_retention_days} days.\n\nContinue?",
            parent=self.frame
        )
        
        if result:
            try:
                # Get counts before cleanup
                before_count = len(self.app.data_manager.get_moisture_history(hours=24*7))
                
                # Perform cleanup
                self.app.data_manager.cleanup_old_data(self.app.config.system.log_retention_days)
                
                # Get counts after
                after_count = len(self.app.data_manager.get_moisture_history(hours=24*7))
                
                # Show success message
                tk.messagebox.showinfo(
                    "Cleanup Complete",
                    f"Database cleaned successfully!\n\nRemoved {before_count - after_count} old moisture readings.",
                    parent=self.frame
                )
                
                self._update_cal_status("✅ Database cleanup completed!", "success")
                
            except Exception as e:
                tk.messagebox.showerror(
                    "Cleanup Error",
                    f"Error during cleanup: {str(e)}",
                    parent=self.frame
                )
                self._update_cal_status(f"❌ Cleanup error: {str(e)}", "error")
    
    def _export_data(self):
        """Export data to CSV files"""
        from tkinter import filedialog
        import csv
        from datetime import datetime
        
        # Ask for directory
        directory = filedialog.askdirectory(
            title="Select Export Directory",
            parent=self.frame
        )
        
        if not directory:
            return
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Export moisture data
            moisture_file = Path(directory) / f"moisture_data_{timestamp}.csv"
            moisture_history = self.app.data_manager.get_moisture_history(hours=24*30)  # 30 days
            
            with open(moisture_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'Moisture %', 'Raw Value', 'Channel'])
                for reading in moisture_history:
                    writer.writerow([
                        reading.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        reading.moisture_percent,
                        reading.raw_value,
                        reading.sensor_channel
                    ])
            
            # Export watering events
            watering_file = Path(directory) / f"watering_events_{timestamp}.csv"
            watering_history = self.app.data_manager.get_watering_history(days=30)
            
            with open(watering_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'Duration (sec)', 'Trigger Moisture %', 'Type', 'Notes'])
                for event in watering_history:
                    writer.writerow([
                        event.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        event.duration_seconds,
                        event.trigger_moisture,
                        event.event_type,
                        event.notes
                    ])
            
            # Show success
            tk.messagebox.showinfo(
                "Export Complete",
                f"Data exported successfully!\n\n📊 {moisture_file.name}\n💧 {watering_file.name}",
                parent=self.frame
            )
            
            self._update_cal_status("✅ Data exported successfully!", "success")
            
        except Exception as e:
            tk.messagebox.showerror(
                "Export Error", 
                f"Error exporting data: {str(e)}",
                parent=self.frame
            )
            self._update_cal_status(f"❌ Export error: {str(e)}", "error")
    
    def update_display(self):
        """Update settings display"""
        self.mini_status.update_display()
        self._update_hardware_status()
    
    def _create_calibration_section(self, parent):
        """Create sensor calibration section"""
        calibration_card = create_professional_card(parent, "🎯 Sensor Calibration")
        calibration_card.pack(fill="x", pady=BonsaiTheme.SPACING['md'])
        
        # Info section
        info_label = ttk.Label(calibration_card,
                              text="Calibrate your moisture sensor for accurate readings. Each sensor is unique!",
                              font=BonsaiTheme.FONTS['body'],
                              foreground=BonsaiTheme.COLORS['text_muted'],
                              wraplength=600)
        info_label.pack(anchor="w", pady=(0, BonsaiTheme.SPACING['md']))
        
        # Current calibration values display
        cal_frame = ttk.Frame(calibration_card)
        cal_frame.pack(fill="x", pady=BonsaiTheme.SPACING['sm'])
        
        ttk.Label(cal_frame, text="Current Calibration:",
                 font=BonsaiTheme.FONTS['body_bold'],
                 foreground=BonsaiTheme.COLORS['text_primary']).pack(anchor="w")
        
        self.cal_info_frame = ttk.Frame(cal_frame)
        self.cal_info_frame.pack(fill="x", padx=(BonsaiTheme.SPACING['md'], 0))
        
        # Create labels for current values
        self.dry_cal_label = ttk.Label(self.cal_info_frame, text="",
                                      font=BonsaiTheme.FONTS['body'])
        self.dry_cal_label.pack(anchor="w")
        
        self.wet_cal_label = ttk.Label(self.cal_info_frame, text="",
                                      font=BonsaiTheme.FONTS['body'])
        self.wet_cal_label.pack(anchor="w")
        
        # Live sensor reading display
        reading_frame = ttk.Frame(calibration_card)
        reading_frame.pack(fill="x", pady=BonsaiTheme.SPACING['md'])
        
        ttk.Label(reading_frame, text="Live Sensor Reading:",
                 font=BonsaiTheme.FONTS['body_bold'],
                 foreground=BonsaiTheme.COLORS['text_primary']).pack(anchor="w")
        
        # Reading display with visual indicator
        self.reading_display_frame = ttk.Frame(reading_frame)
        self.reading_display_frame.pack(fill="x", pady=BonsaiTheme.SPACING['sm'])
        
        self.raw_reading_label = ttk.Label(self.reading_display_frame,
                                          text="Raw ADC: -----",
                                          font=BonsaiTheme.FONTS['mono'])
        self.raw_reading_label.pack(side="left", padx=(BonsaiTheme.SPACING['md'], BonsaiTheme.SPACING['lg']))
        
        self.moisture_reading_label = ttk.Label(self.reading_display_frame,
                                               text="Moisture: ---%",
                                               font=BonsaiTheme.FONTS['heading_small'])
        self.moisture_reading_label.pack(side="left")
        
        # Visual moisture bar
        self.moisture_canvas = tk.Canvas(self.reading_display_frame,
                                       width=200, height=20,
                                       bg=BonsaiTheme.COLORS['bg_accent'],
                                       highlightthickness=1,
                                       highlightbackground=BonsaiTheme.COLORS['accent_green'])
        self.moisture_canvas.pack(side="left", padx=(BonsaiTheme.SPACING['lg'], 0))
        
        # Calibration buttons
        button_frame = ttk.Frame(calibration_card)
        button_frame.pack(fill="x", pady=BonsaiTheme.SPACING['lg'])
        
        # Start calibration button
        self.calibrate_button = create_action_button(
            button_frame, 
            "🔧 Start Calibration Wizard", 
            self._start_calibration,
            "primary"
        )
        self.calibrate_button.pack(side="left", padx=(0, BonsaiTheme.SPACING['md']))
        
        # Quick calibration info
        quick_info = ttk.Label(button_frame,
                              text="• Dry = sensor in air  • Wet = sensor in water",
                              font=BonsaiTheme.FONTS['caption'],
                              foreground=BonsaiTheme.COLORS['text_muted'])
        quick_info.pack(side="left", padx=BonsaiTheme.SPACING['md'])
        
        # Status message
        self.cal_status = ttk.Label(calibration_card, text="",
                                   font=BonsaiTheme.FONTS['body'],
                                   foreground=BonsaiTheme.COLORS['success'])
        self.cal_status.pack(pady=BonsaiTheme.SPACING['sm'])
        
        # Update display initially
        self._update_calibration_display()
        
        # Start live reading updates
        self._update_live_reading()
    
    def _update_calibration_display(self):
        """Update calibration values display"""
        try:
            config = self.app.config
            self.dry_cal_label.config(
                text=f"Dry (air): {config.sensor.calibration_dry} ADC"
            )
            self.wet_cal_label.config(
                text=f"Wet (water): {config.sensor.calibration_wet} ADC"
            )
        except Exception as e:
            print(f"Error updating calibration display: {e}")
    
    def _update_live_reading(self):
        """Update live sensor reading display"""
        try:
            # Only update if we have a real sensor
            if isinstance(self.app.sensor, MockSoilMoistureSensor):
                self.raw_reading_label.config(text="Raw ADC: (Mock)")
                self.moisture_reading_label.config(text="Moisture: (Mock)")
                self.moisture_canvas.delete("all")
            else:
                # Get raw and percentage readings
                raw = self.app.sensor.read_raw_adc()
                moisture = self.app.sensor.read_moisture_percent()
                
                if raw is not None:
                    self.raw_reading_label.config(text=f"Raw ADC: {raw:5d}")
                else:
                    self.raw_reading_label.config(text="Raw ADC: ERROR")
                
                if moisture is not None:
                    self.moisture_reading_label.config(text=f"Moisture: {moisture:.1f}%")
                    
                    # Color based on moisture level
                    if moisture < 20:
                        color = BonsaiTheme.COLORS['error']
                    elif moisture < 40:
                        color = BonsaiTheme.COLORS['warning']
                    elif moisture < 70:
                        color = BonsaiTheme.COLORS['success']
                    else:
                        color = BonsaiTheme.COLORS['info']
                    
                    self.moisture_reading_label.config(foreground=color)
                    
                    # Draw moisture bar
                    self.moisture_canvas.delete("all")
                    bar_width = int((moisture / 100) * 190)
                    self.moisture_canvas.create_rectangle(
                        5, 5, 5 + bar_width, 15,
                        fill=color, outline=""
                    )
                else:
                    self.moisture_reading_label.config(text="Moisture: ---")
                    self.moisture_canvas.delete("all")
                    
        except Exception as e:
            print(f"Error updating live reading: {e}")
        
        # Schedule next update
        self.frame.after(1000, self._update_live_reading)
    
    def _start_calibration(self):
        """Start interactive calibration wizard"""
        if isinstance(self.app.sensor, MockSoilMoistureSensor):
            self._update_cal_status("❌ Cannot calibrate mock sensor! Enable real hardware first.", "error")
            return
        
        # Create calibration window
        cal_window = tk.Toplevel(self.frame)
        cal_window.title("🎯 Sensor Calibration Wizard")
        cal_window.geometry("600x500")
        cal_window.transient(self.frame)
        
        # Make it modal
        cal_window.grab_set()
        
        # Variables to store calibration values
        self.cal_dry_values = []
        self.cal_wet_values = []
        self.cal_current_step = "intro"
        
        # Main container
        main_frame = ttk.Frame(cal_window)
        main_frame.pack(fill="both", expand=True, padx=BonsaiTheme.SPACING['lg'],
                       pady=BonsaiTheme.SPACING['lg'])
        
        # Header
        header_label = ttk.Label(main_frame, 
                               text="🌱 Moisture Sensor Calibration",
                               font=BonsaiTheme.FONTS['heading_medium'],
                               foreground=BonsaiTheme.COLORS['primary_green'])
        header_label.pack(pady=(0, BonsaiTheme.SPACING['lg']))
        
        # Content frame (will be updated for each step)
        self.cal_content_frame = ttk.Frame(main_frame)
        self.cal_content_frame.pack(fill="both", expand=True)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(BonsaiTheme.SPACING['lg'], 0))
        
        self.cal_cancel_btn = ttk.Button(button_frame, text="Cancel",
                                       command=cal_window.destroy)
        self.cal_cancel_btn.pack(side="left")
        
        self.cal_next_btn = create_action_button(button_frame, "Next →",
                                               lambda: self._cal_next_step(cal_window),
                                               "primary")
        self.cal_next_btn.pack(side="right")
        
        # Start with intro
        self._show_cal_intro()
    
    def _show_cal_intro(self):
        """Show calibration introduction"""
        # Clear content
        for widget in self.cal_content_frame.winfo_children():
            widget.destroy()
        
        # Intro text
        intro_text = """This wizard will help you calibrate your moisture sensor for accurate readings.

You'll need:
• Your moisture sensor (connected)
• A paper towel or tissue
• A glass of water

The process takes about 2 minutes and involves:
1. Reading the sensor when completely dry (in air)
2. Reading the sensor when wet (in water)

Ready to start?"""
        
        intro_label = ttk.Label(self.cal_content_frame, text=intro_text,
                              font=BonsaiTheme.FONTS['body'],
                              justify="left")
        intro_label.pack(pady=BonsaiTheme.SPACING['lg'])
        
        self.cal_current_step = "intro"
    
    def _show_cal_dry(self):
        """Show dry calibration step"""
        for widget in self.cal_content_frame.winfo_children():
            widget.destroy()
        
        # Instructions
        ttk.Label(self.cal_content_frame, 
                 text="Step 1: Dry Calibration",
                 font=BonsaiTheme.FONTS['heading_small'],
                 foreground=BonsaiTheme.COLORS['primary_green']).pack(pady=(0, BonsaiTheme.SPACING['md']))
        
        instructions = """1. Remove the sensor from any soil or water
2. Wipe it completely dry with a paper towel
3. Hold it in the air

The sensor should be completely dry for accurate calibration."""
        
        ttk.Label(self.cal_content_frame, text=instructions,
                 font=BonsaiTheme.FONTS['body'],
                 justify="left").pack(pady=BonsaiTheme.SPACING['md'])
        
        # Live reading display
        reading_frame = ttk.LabelFrame(self.cal_content_frame, 
                                     text="  Live Sensor Reading  ",
                                     padding=BonsaiTheme.SPACING['md'])
        reading_frame.pack(fill="x", pady=BonsaiTheme.SPACING['lg'])
        
        self.cal_live_label = ttk.Label(reading_frame, 
                                      text="Raw ADC: -----",
                                      font=BonsaiTheme.FONTS['heading_small'])
        self.cal_live_label.pack()
        
        # Progress
        self.cal_progress_label = ttk.Label(self.cal_content_frame,
                                          text="Click 'Next' when sensor is dry",
                                          font=BonsaiTheme.FONTS['body'],
                                          foreground=BonsaiTheme.COLORS['text_muted'])
        self.cal_progress_label.pack()
        
        self.cal_current_step = "dry"
        self.cal_dry_values = []
        
        # Start reading values
        self._update_cal_reading()
    
    def _show_cal_wet(self):
        """Show wet calibration step"""
        for widget in self.cal_content_frame.winfo_children():
            widget.destroy()
        
        # Instructions
        ttk.Label(self.cal_content_frame,
                 text="Step 2: Wet Calibration",
                 font=BonsaiTheme.FONTS['heading_small'],
                 foreground=BonsaiTheme.COLORS['primary_green']).pack(pady=(0, BonsaiTheme.SPACING['md']))
        
        instructions = """1. Fill a glass with water
2. Insert the sensor into the water
3. Submerge ONLY up to the line on the sensor PCB
4. DO NOT submerge the electronic components!

The sensor should be steady in the water."""
        
        ttk.Label(self.cal_content_frame, text=instructions,
                 font=BonsaiTheme.FONTS['body'],
                 justify="left").pack(pady=BonsaiTheme.SPACING['md'])
        
        # Warning
        warning_frame = ttk.Frame(self.cal_content_frame)
        warning_frame.pack(fill="x", pady=BonsaiTheme.SPACING['md'])
        
        ttk.Label(warning_frame, text="⚠️",
                 font=("Arial", 16),
                 foreground=BonsaiTheme.COLORS['warning']).pack(side="left")
        
        ttk.Label(warning_frame, 
                 text="Only submerge the metal probes, not the circuit board!",
                 font=BonsaiTheme.FONTS['body_bold'],
                 foreground=BonsaiTheme.COLORS['warning']).pack(side="left", padx=(BonsaiTheme.SPACING['sm'], 0))
        
        # Live reading display
        reading_frame = ttk.LabelFrame(self.cal_content_frame,
                                     text="  Live Sensor Reading  ",
                                     padding=BonsaiTheme.SPACING['md'])
        reading_frame.pack(fill="x", pady=BonsaiTheme.SPACING['lg'])
        
        self.cal_live_label = ttk.Label(reading_frame,
                                      text="Raw ADC: -----", 
                                      font=BonsaiTheme.FONTS['heading_small'])
        self.cal_live_label.pack()
        
        # Progress
        self.cal_progress_label = ttk.Label(self.cal_content_frame,
                                          text="Click 'Next' when sensor is in water",
                                          font=BonsaiTheme.FONTS['body'],
                                          foreground=BonsaiTheme.COLORS['text_muted'])
        self.cal_progress_label.pack()
        
        self.cal_current_step = "wet"
        self.cal_wet_values = []
        
        # Continue reading values
        self._update_cal_reading()
    
    def _show_cal_complete(self, cal_window):
        """Show calibration complete with results"""
        for widget in self.cal_content_frame.winfo_children():
            widget.destroy()
        
        # Calculate averages
        dry_avg = int(sum(self.cal_dry_values) / len(self.cal_dry_values))
        wet_avg = int(sum(self.cal_wet_values) / len(self.cal_wet_values))
        
        # Results
        ttk.Label(self.cal_content_frame,
                 text="✅ Calibration Complete!",
                 font=BonsaiTheme.FONTS['heading_small'],
                 foreground=BonsaiTheme.COLORS['success']).pack(pady=(0, BonsaiTheme.SPACING['lg']))
        
        # Show results
        results_frame = ttk.LabelFrame(self.cal_content_frame,
                                     text="  Calibration Results  ",
                                     padding=BonsaiTheme.SPACING['lg'])
        results_frame.pack(fill="x", pady=BonsaiTheme.SPACING['md'])
        
        ttk.Label(results_frame, 
                 text=f"Dry Value (in air): {dry_avg}",
                 font=BonsaiTheme.FONTS['body_bold']).pack(anchor="w")
        
        ttk.Label(results_frame,
                 text=f"Wet Value (in water): {wet_avg}",
                 font=BonsaiTheme.FONTS['body_bold']).pack(anchor="w")
        
        # Validate
        range_val = abs(dry_avg - wet_avg)
        if range_val < 1000:
            ttk.Label(results_frame,
                     text="⚠️ Warning: Small range detected. Sensor may have issues.",
                     font=BonsaiTheme.FONTS['body'],
                     foreground=BonsaiTheme.COLORS['warning']).pack(anchor="w", pady=(BonsaiTheme.SPACING['md'], 0))
        else:
            ttk.Label(results_frame,
                     text=f"✅ Good range: {range_val} ADC units",
                     font=BonsaiTheme.FONTS['body'],
                     foreground=BonsaiTheme.COLORS['success']).pack(anchor="w", pady=(BonsaiTheme.SPACING['md'], 0))
        
        # Test with new values
        ttk.Label(self.cal_content_frame,
                 text="Test your new calibration:",
                 font=BonsaiTheme.FONTS['body_bold'],
                 foreground=BonsaiTheme.COLORS['text_primary']).pack(pady=(BonsaiTheme.SPACING['lg'], BonsaiTheme.SPACING['sm']))
        
        test_frame = ttk.Frame(self.cal_content_frame)
        test_frame.pack(fill="x")
        
        self.cal_test_label = ttk.Label(test_frame,
                                      text="Calculating...",
                                      font=BonsaiTheme.FONTS['heading_small'])
        self.cal_test_label.pack()
        
        # Store values for saving
        self.new_dry_value = dry_avg
        self.new_wet_value = wet_avg
        
        # Change button to "Save"
        self.cal_next_btn.config(text="💾 Save Calibration",
                               command=lambda: self._save_calibration(cal_window))
        
        # Update test display
        self._test_new_calibration()
    
    def _test_new_calibration(self):
        """Test the new calibration values"""
        if hasattr(self, 'cal_test_label'):
            try:
                raw = self.app.sensor.read_raw_adc()
                if raw is not None:
                    # Calculate with new values
                    moisture = (self.new_dry_value - raw) / (self.new_dry_value - self.new_wet_value) * 100
                    moisture = max(0, min(100, moisture))
                    
                    # Determine condition
                    if moisture < 10:
                        condition = "Very Dry (air)"
                        color = BonsaiTheme.COLORS['error']
                    elif moisture < 30:
                        condition = "Dry"
                        color = BonsaiTheme.COLORS['warning']
                    elif moisture < 70:
                        condition = "Good"
                        color = BonsaiTheme.COLORS['success']
                    else:
                        condition = "Wet"
                        color = BonsaiTheme.COLORS['info']
                    
                    self.cal_test_label.config(
                        text=f"Current: {moisture:.1f}% - {condition}",
                        foreground=color
                    )
                    
                # Schedule next update
                self.frame.after(500, self._test_new_calibration)
            except:
                pass
    
    def _update_cal_reading(self):
        """Update live reading during calibration"""
        if hasattr(self, 'cal_live_label'):
            try:
                raw = self.app.sensor.read_raw_adc()
                if raw is not None:
                    self.cal_live_label.config(text=f"Raw ADC: {raw}")
                    
                    # Collect values
                    if self.cal_current_step == "dry":
                        self.cal_dry_values.append(raw)
                        if len(self.cal_dry_values) > 20:
                            self.cal_dry_values.pop(0)
                    elif self.cal_current_step == "wet":
                        self.cal_wet_values.append(raw)
                        if len(self.cal_wet_values) > 20:
                            self.cal_wet_values.pop(0)
                else:
                    self.cal_live_label.config(text="Raw ADC: ERROR")
                
                # Schedule next update
                self.frame.after(250, self._update_cal_reading)
            except:
                pass
    
    def _cal_next_step(self, cal_window):
        """Move to next calibration step"""
        if self.cal_current_step == "intro":
            self._show_cal_dry()
        elif self.cal_current_step == "dry":
            if len(self.cal_dry_values) < 5:
                self._update_cal_status("Please wait for sensor readings...", "warning")
                return
            self._show_cal_wet()
        elif self.cal_current_step == "wet":
            if len(self.cal_wet_values) < 5:
                self._update_cal_status("Please wait for sensor readings...", "warning")
                return
            self._show_cal_complete(cal_window)
    
    def _save_calibration(self, cal_window):
        """Save the new calibration values"""
        try:
            # Update config
            self.app.config_manager.update('sensor',
                                         calibration_dry=self.new_dry_value,
                                         calibration_wet=self.new_wet_value)
            
            # Update sensor
            self.app.sensor.calibrate(self.new_dry_value, self.new_wet_value)
            
            # Update display
            self._update_calibration_display()
            
            # Show success
            self._update_cal_status("✅ Calibration saved successfully!", "success")
            
            # Close window
            cal_window.destroy()
            
        except Exception as e:
            self._update_cal_status(f"❌ Error saving: {str(e)}", "error")
    
    def _update_cal_status(self, message, status_type):
        """Update calibration status message"""
        colors = {
            "success": BonsaiTheme.COLORS['success'],
            "error": BonsaiTheme.COLORS['error'],
            "warning": BonsaiTheme.COLORS['warning'],
            "info": BonsaiTheme.COLORS['info']
        }
        
        self.cal_status.config(text=message,
                             foreground=colors.get(status_type, BonsaiTheme.COLORS['text_muted']))
        
        # Clear after 5 seconds for non-error messages  
        if status_type != "error":
            self.frame.after(5000, lambda: self.cal_status.config(text=""))


class BonsaiAssistantApp:
    """Beautiful Professional Bonsai Care Assistant with FIXED controls and simulation"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🌱 Bonsai Assistant Professional v2.0")
        # FIXED: Larger default size and better minimum
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
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
        
        # FIXED: Start display update loop
        self._start_display_updates()
    
    def _init_hardware_components(self):
        """Initialize hardware with graceful fallbacks"""
        # Track initialization status
        hardware_status = {
            'sensor': {'real': False, 'error': None},
            'pump': {'real': False, 'error': None},
            'display': {'real': False, 'error': None}
        }
        
        try:
            self.sensor = SoilMoistureSensor(
                channel=self.config.sensor.i2c_channel, 
                debug=False,
                dry_calibration=self.config.sensor.calibration_dry,
                wet_calibration=self.config.sensor.calibration_wet
            )
            hardware_status['sensor']['real'] = True
            print("✅ Real moisture sensor initialized")
            print(f"   Using calibration: Dry={self.config.sensor.calibration_dry}, Wet={self.config.sensor.calibration_wet}")
        except Exception as e:
            hardware_status['sensor']['error'] = str(e)
            print(f"⚠️ Sensor init failed, using simulation: {e}")
            self.sensor = MockSoilMoistureSensor(lambda: 45.0)
            
        try:
            self.pump = PumpController(gpio_pin=self.config.pump.gpio_pin)
            hardware_status['pump']['real'] = True
            print("✅ Real pump controller initialized")
        except Exception as e:
            hardware_status['pump']['error'] = str(e)
            print(f"⚠️ Pump init failed, using simulation: {e}")
            self.pump = MockPumpController()
            
        try:
            self.display = RGBDisplayDriver(
                width=self.config.display.width,
                height=self.config.display.height,
                rotation=self.config.display.rotation
            )
            hardware_status['display']['real'] = True
            print("✅ Real display initialized")
        except Exception as e:
            hardware_status['display']['error'] = str(e)
            print(f"⚠️ Display init failed, using simulation: {e}")
            self.display = MockDisplay()
        
        # Store hardware status for UI display
        self.hardware_status = hardware_status
    
    def _setup_ui(self):
        """Setup beautiful UI with bonsai theme"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True)
        
        # Beautiful header with bonsai art
        self.header = create_bonsai_header(main_container)
        self.header.pack(fill="x", padx=BonsaiTheme.SPACING['lg'], 
                        pady=(BonsaiTheme.SPACING['lg'], BonsaiTheme.SPACING['md']))
        
        # Create notebook with professional tabs - FIXED: expand properly
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
        
        # FIXED: Make notebook expand to fill available space
        self.notebook.pack(fill="both", expand=True, 
                          padx=BonsaiTheme.SPACING['lg'],
                          pady=(0, BonsaiTheme.SPACING['lg']))
        
        # Beautiful status bar
        self._create_status_bar()
        
        # Setup master scrolling handler
        self._setup_master_scrolling()
    
    def _setup_master_scrolling(self):
        """Setup SIMPLE master scrolling for all tabs"""
        def on_mousewheel(event):
            # Get current tab
            try:
                current = self.notebook.index(self.notebook.select())
                
                # Find the active canvas
                canvas = None
                if current == 1 and hasattr(self.controls_tab, '_canvas'):  # Controls tab
                    canvas = self.controls_tab._canvas
                elif current == 2:  # Settings tab - add this!
                    # Find the canvas in settings tab
                    for child in self.settings_tab.frame.winfo_children():
                        if isinstance(child, tk.Canvas):
                            canvas = child
                            break
                # Dashboard has its own scrolling
                
                # Scroll the active canvas
                if canvas and canvas.winfo_exists():
                    if event.delta:
                        canvas.yview_scroll(-1*(event.delta//120), "units")
                    elif event.num == 4:
                        canvas.yview_scroll(-1, "units")
                    elif event.num == 5:
                        canvas.yview_scroll(1, "units")
            except:
                pass  # Ignore errors
        
        # Bind to root
        self.root.bind("<MouseWheel>", on_mousewheel)
        self.root.bind("<Button-4>", on_mousewheel)
        self.root.bind("<Button-5>", on_mousewheel)
    
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
    
    def _start_display_updates(self):
        """FIXED: Start regular display updates"""
        def update_display_loop():
            while True:
                try:
                    # Get current status
                    moisture = self.automation.last_moisture_reading
                    pump_status = self.pump.get_status()
                    runtime = self.pump.get_runtime_seconds()
                    
                    # Update display
                    if moisture is not None:
                        self.display.draw_status(
                            moisture=moisture,
                            pump_status=pump_status,
                            runtime_sec=runtime
                        )
                except Exception as e:
                    print(f"Display update error: {e}")
                
                # Wait before next update
                time.sleep(self.config.display.update_interval)
        
        # Start display thread
        display_thread = threading.Thread(target=update_display_loop, daemon=True)
        display_thread.start()
        print("📺 Display update loop started")
    
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
        # Display is now updated in the separate display thread
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