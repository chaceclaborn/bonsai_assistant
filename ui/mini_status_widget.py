# File: ui/mini_status_widget.py

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from ui.professional_theme import BonsaiTheme

class MiniStatusWidget:
    """Beautiful compact status widget with professional green theme"""
    
    def __init__(self, parent, automation, pump):
        self.automation = automation
        self.pump = pump
        
        # Create main frame with beautiful styling
        self.frame = ttk.LabelFrame(parent, text="  🌱 System Status  ", 
                                   padding=BonsaiTheme.SPACING['md'])
        
        # Create horizontal layout
        self.main_container = ttk.Frame(self.frame)
        self.main_container.pack(fill="x")
        
        # Left side - Key metrics with beautiful cards
        self.metrics_frame = ttk.Frame(self.main_container)
        self.metrics_frame.pack(side="left", fill="x", expand=True)
        
        # Create status cards
        self._create_status_cards()
        
        # Right side - Visual indicators and time
        self.indicators_frame = ttk.Frame(self.main_container)
        self.indicators_frame.pack(side="right", padx=(BonsaiTheme.SPACING['lg'], 0))
        
        self._create_indicators()
        
        # Initialize displays
        self.update_display()
    
    def _create_status_cards(self):
        """Create beautiful status cards"""
        # Moisture card
        moisture_card = ttk.Frame(self.metrics_frame)
        moisture_card.pack(side="left", padx=(0, BonsaiTheme.SPACING['md']))
        
        moisture_icon = ttk.Label(moisture_card, text="💧", font=("Arial", 12))
        moisture_icon.pack()
        
        moisture_title = ttk.Label(moisture_card, text="Moisture",
                                  font=BonsaiTheme.FONTS['caption'],
                                  foreground=BonsaiTheme.COLORS['text_muted'])
        moisture_title.pack()
        
        self.moisture_label = ttk.Label(moisture_card, text="---%",
                                       font=BonsaiTheme.FONTS['body_bold'],
                                       foreground=BonsaiTheme.COLORS['primary_green'])
        self.moisture_label.pack()
        
        # Separator
        ttk.Separator(self.metrics_frame, orient="vertical").pack(
            side="left", fill="y", padx=BonsaiTheme.SPACING['md'])
        
        # Pump card
        pump_card = ttk.Frame(self.metrics_frame)
        pump_card.pack(side="left", padx=(0, BonsaiTheme.SPACING['md']))
        
        pump_icon = ttk.Label(pump_card, text="⚙️", font=("Arial", 12))
        pump_icon.pack()
        
        pump_title = ttk.Label(pump_card, text="Pump",
                              font=BonsaiTheme.FONTS['caption'],
                              foreground=BonsaiTheme.COLORS['text_muted'])
        pump_title.pack()
        
        self.pump_label = ttk.Label(pump_card, text="OFF",
                                   font=BonsaiTheme.FONTS['body_bold'],
                                   foreground=BonsaiTheme.COLORS['text_muted'])
        self.pump_label.pack()
        
        # Separator
        ttk.Separator(self.metrics_frame, orient="vertical").pack(
            side="left", fill="y", padx=BonsaiTheme.SPACING['md'])
        
        # Automation card
        auto_card = ttk.Frame(self.metrics_frame)
        auto_card.pack(side="left")
        
        auto_icon = ttk.Label(auto_card, text="🤖", font=("Arial", 12))
        auto_icon.pack()
        
        auto_title = ttk.Label(auto_card, text="Automation",
                              font=BonsaiTheme.FONTS['caption'],
                              foreground=BonsaiTheme.COLORS['text_muted'])
        auto_title.pack()
        
        self.auto_label = ttk.Label(auto_card, text="Starting...",
                                   font=BonsaiTheme.FONTS['body_bold'],
                                   foreground=BonsaiTheme.COLORS['primary_green'])
        self.auto_label.pack()
    
    def _create_indicators(self):
        """Create visual status indicators"""
        # Indicator container
        indicator_container = ttk.Frame(self.indicators_frame)
        indicator_container.pack()
        
        # Status lights label
        lights_label = ttk.Label(indicator_container, text="Status Lights",
                                font=BonsaiTheme.FONTS['caption'],
                                foreground=BonsaiTheme.COLORS['text_muted'])
        lights_label.pack()
        
        # Indicators row
        indicators_row = ttk.Frame(indicator_container)
        indicators_row.pack(pady=BonsaiTheme.SPACING['xs'])
        
        # Plant health indicator
        plant_frame = ttk.Frame(indicators_row)
        plant_frame.pack(side="left", padx=2)
        
        self.plant_canvas = tk.Canvas(plant_frame, width=16, height=16, 
                                     bg=BonsaiTheme.COLORS['bg_card'], 
                                     highlightthickness=0)
        self.plant_canvas.pack()
        
        plant_label = ttk.Label(plant_frame, text="Plant",
                               font=("Arial", 7),
                               foreground=BonsaiTheme.COLORS['text_muted'])
        plant_label.pack()
        
        # Sensor indicator
        sensor_frame = ttk.Frame(indicators_row)
        sensor_frame.pack(side="left", padx=2)
        
        self.sensor_canvas = tk.Canvas(sensor_frame, width=16, height=16,
                                      bg=BonsaiTheme.COLORS['bg_card'],
                                      highlightthickness=0)
        self.sensor_canvas.pack()
        
        sensor_label = ttk.Label(sensor_frame, text="Sensor",
                                font=("Arial", 7),
                                foreground=BonsaiTheme.COLORS['text_muted'])
        sensor_label.pack()
        
        # Pump indicator
        pump_ind_frame = ttk.Frame(indicators_row)
        pump_ind_frame.pack(side="left", padx=2)
        
        self.pump_canvas = tk.Canvas(pump_ind_frame, width=16, height=16,
                                    bg=BonsaiTheme.COLORS['bg_card'],
                                    highlightthickness=0)
        self.pump_canvas.pack()
        
        pump_ind_label = ttk.Label(pump_ind_frame, text="Pump",
                                  font=("Arial", 7),
                                  foreground=BonsaiTheme.COLORS['text_muted'])
        pump_ind_label.pack()
        
        # Time display
        self.time_label = ttk.Label(self.indicators_frame, text="",
                                   font=BonsaiTheme.FONTS['caption'],
                                   foreground=BonsaiTheme.COLORS['text_muted'])
        self.time_label.pack(pady=(BonsaiTheme.SPACING['sm'], 0))
    
    def update_display(self):
        """Update all status displays with beautiful styling"""
        try:
            # Get current status
            status = self.automation.get_status()
            
            # Update moisture with color coding
            moisture = status.get('last_moisture')
            if moisture is not None:
                self.moisture_label.config(text=f"{moisture:.1f}%")
                
                # Beautiful color coding
                if moisture < 15:
                    color = BonsaiTheme.COLORS['error']
                    status_type = "critical"
                elif moisture < 30:
                    color = BonsaiTheme.COLORS['warning']
                    status_type = "low"
                elif moisture < 60:
                    color = BonsaiTheme.COLORS['success']
                    status_type = "good"
                else:
                    color = BonsaiTheme.COLORS['info']
                    status_type = "high"
                
                self.moisture_label.config(foreground=color)
            else:
                self.moisture_label.config(text="---", 
                                         foreground=BonsaiTheme.COLORS['text_muted'])
                status_type = "error"
            
            # Update pump status with beautiful colors
            pump_running = self.pump.is_running()
            if pump_running:
                self.pump_label.config(text="ACTIVE", 
                                     foreground=BonsaiTheme.COLORS['success'])
            else:
                self.pump_label.config(text="IDLE", 
                                     foreground=BonsaiTheme.COLORS['text_muted'])
            
            # Update automation status with beautiful styling
            auto_running = status.get('running', False)
            auto_active = status.get('automation_active', False)
            
            if auto_active:
                self.auto_label.config(text="WATERING", 
                                     foreground=BonsaiTheme.COLORS['info'])
                auto_status = "watering"
            elif auto_running:
                self.auto_label.config(text="MONITORING", 
                                     foreground=BonsaiTheme.COLORS['success'])
                auto_status = "running"
            else:
                self.auto_label.config(text="PAUSED", 
                                     foreground=BonsaiTheme.COLORS['warning'])
                auto_status = "stopped"
            
            # FIXED: Update beautiful indicators with proper hardware detection
            self._draw_indicator(self.plant_canvas, 
                               self._get_plant_color(status.get('current_state', 'unknown')))
            
            # CRITICAL FIX: Check actual sensor reading, not just moisture value
            sensor_working = False
            try:
                # Test if sensor is actually responsive
                test_reading = self.automation.sensor.read_moisture_percent()
                sensor_working = test_reading is not None
            except:
                sensor_working = False
                
            self._draw_indicator(self.sensor_canvas, 
                               BonsaiTheme.COLORS['success'] if sensor_working 
                               else BonsaiTheme.COLORS['error'])
            
            self._draw_indicator(self.pump_canvas, 
                               BonsaiTheme.COLORS['success'] if pump_running 
                               else BonsaiTheme.COLORS['text_muted'])
            
            # Update time with beautiful formatting
            current_time = datetime.now().strftime("%H:%M:%S")
            self.time_label.config(text=f"🕐 {current_time}")
            
        except Exception as e:
            print(f"Error updating mini status: {e}")
            # Set error state with beautiful error styling
            self.moisture_label.config(text="ERROR", 
                                     foreground=BonsaiTheme.COLORS['error'])
            self.auto_label.config(text="ERROR", 
                                 foreground=BonsaiTheme.COLORS['error'])
    
    def _draw_indicator(self, canvas, color):
        """Draw beautiful status indicator with glow effect"""
        canvas.delete("all")
        
        # Create gradient effect
        # Outer glow
        canvas.create_oval(2, 2, 14, 14, fill=color, outline=color, width=0)
        
        # Inner bright spot for 3D effect
        lighter_color = self._lighten_color(color)
        canvas.create_oval(4, 4, 8, 8, fill=lighter_color, outline="", width=0)
    
    def _lighten_color(self, color):
        """Create a lighter version of the color for glow effect"""
        # Simple lightening - in a real app you'd use proper color manipulation
        light_colors = {
            BonsaiTheme.COLORS['success']: "#90EE90",
            BonsaiTheme.COLORS['error']: "#FFB3B3",
            BonsaiTheme.COLORS['warning']: "#FFE4B3",
            BonsaiTheme.COLORS['info']: "#B3D9FF",
            BonsaiTheme.COLORS['text_muted']: "#CCCCCC"
        }
        return light_colors.get(color, "#FFFFFF")
    
    def _get_plant_color(self, state):
        """Get beautiful color for plant state"""
        colors = {
            "healthy": BonsaiTheme.COLORS['success'],
            "needs_water": BonsaiTheme.COLORS['warning'], 
            "recently_watered": BonsaiTheme.COLORS['info'],
            "critical": BonsaiTheme.COLORS['error'],
            "sensor_error": BonsaiTheme.COLORS['text_muted']
        }
        return colors.get(state, BonsaiTheme.COLORS['text_muted'])