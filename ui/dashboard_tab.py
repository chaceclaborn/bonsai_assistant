# File: ui/dashboard_tab.py

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from typing import Optional, List
from ui.professional_theme import (
    BonsaiTheme, create_professional_card, create_status_card, 
    create_info_panel, add_separator, create_section_header
)

class StatusIndicator:
    """Beautiful status indicator with professional styling"""
    
    def __init__(self, parent, title: str, icon: str = "⚫"):
        self.frame = ttk.Frame(parent)
        self.frame.configure(style='Card.TFrame')
        
        # Main container with beautiful padding
        container = ttk.Frame(self.frame)
        container.pack(fill="both", expand=True, padx=BonsaiTheme.SPACING['md'], 
                      pady=BonsaiTheme.SPACING['md'])
        
        # Icon and title row
        header_frame = ttk.Frame(container)
        header_frame.pack(fill="x")
        
        # Icon
        self.icon_label = ttk.Label(header_frame, text=icon, 
                                   font=("Arial", 16))
        self.icon_label.pack(side="left")
        
        # Title
        title_label = ttk.Label(header_frame, text=title,
                               font=BonsaiTheme.FONTS['body_bold'],
                               foreground=BonsaiTheme.COLORS['text_primary'])
        title_label.pack(side="left", padx=(BonsaiTheme.SPACING['sm'], 0))
        
        # Status display
        self.status_label = ttk.Label(container, text="Unknown",
                                     font=BonsaiTheme.FONTS['caption'],
                                     foreground=BonsaiTheme.COLORS['text_muted'])
        self.status_label.pack(anchor="w", pady=(BonsaiTheme.SPACING['xs'], 0))
        
        # Value display
        self.value_label = ttk.Label(container, text="",
                                    font=BonsaiTheme.FONTS['body'],
                                    foreground=BonsaiTheme.COLORS['text_secondary'])
        self.value_label.pack(anchor="w")
        
        self.current_status = "unknown"
    
    def update(self, status: str, value: str = ""):
        """Update indicator with beautiful color coding"""
        self.current_status = status
        self.status_label.config(text=status.upper())
        self.value_label.config(text=value)
        
        # Beautiful color mapping
        color_map = {
            "healthy": BonsaiTheme.COLORS['success'],
            "needs_water": BonsaiTheme.COLORS['warning'],
            "recently_watered": BonsaiTheme.COLORS['info'],
            "critical": BonsaiTheme.COLORS['error'],
            "sensor_error": BonsaiTheme.COLORS['text_muted'],
            "connected": BonsaiTheme.COLORS['success'],
            "disconnected": BonsaiTheme.COLORS['error'],
            "running": BonsaiTheme.COLORS['success'],
            "stopped": BonsaiTheme.COLORS['text_muted'],
            "watering": BonsaiTheme.COLORS['info']
        }
        
        color = color_map.get(status.lower(), BonsaiTheme.COLORS['text_muted'])
        self.status_label.config(foreground=color)


class BeautifulChart:
    """Beautiful chart widget with professional styling"""
    
    def __init__(self, parent, title: str, width=400, height=200):
        self.frame = ttk.LabelFrame(parent, text=f"  📊 {title}  ", 
                                   padding=BonsaiTheme.SPACING['md'])
        
        # Create canvas for chart
        self.canvas = tk.Canvas(self.frame, width=width, height=height, 
                               bg=BonsaiTheme.COLORS['bg_card'],
                               highlightthickness=1,
                               highlightbackground=BonsaiTheme.COLORS['accent_green'])
        self.canvas.pack(fill="both", expand=True)
        
        # Chart parameters
        self.width = width
        self.height = height
        self.margin_left = 50
        self.margin_right = 20
        self.margin_top = 20
        self.margin_bottom = 40
        
        self.chart_width = width - self.margin_left - self.margin_right
        self.chart_height = height - self.margin_top - self.margin_bottom
        
        # Data storage
        self.data_points = []
        self.max_points = 30
        
        # Draw initial empty chart
        self._draw_empty_chart()
    
    def _draw_empty_chart(self):
        """Draw beautiful empty chart template"""
        self.canvas.delete("all")
        
        chart_x = self.margin_left
        chart_y = self.margin_top
        
        # Draw beautiful chart background
        self.canvas.create_rectangle(
            chart_x, chart_y,
            chart_x + self.chart_width, chart_y + self.chart_height,
            fill=BonsaiTheme.COLORS['bg_accent'],
            outline=BonsaiTheme.COLORS['accent_green'],
            width=2
        )
        
        # Draw grid lines
        for i in range(1, 5):
            y = chart_y + (i / 4) * self.chart_height
            self.canvas.create_line(
                chart_x, y, chart_x + self.chart_width, y,
                fill=BonsaiTheme.COLORS['accent_green'],
                width=1, dash=(2, 2)
            )
        
        # Draw Y-axis labels
        for i in range(5):
            y_pos = chart_y + (i / 4) * self.chart_height
            value = 100 - (i / 4) * 100  # 0-100 scale
            self.canvas.create_text(
                chart_x - 10, y_pos,
                text=f"{value:.0f}%",
                font=BonsaiTheme.FONTS['caption'],
                fill=BonsaiTheme.COLORS['text_muted'],
                anchor="e"
            )
        
        # "No data" message
        self.canvas.create_text(
            chart_x + self.chart_width // 2,
            chart_y + self.chart_height // 2,
            text="📈 Waiting for data...",
            font=BonsaiTheme.FONTS['body'],
            fill=BonsaiTheme.COLORS['text_muted']
        )
    
    def add_data_point(self, value: float, timestamp: datetime = None):
        """Add new data point with beautiful visualization"""
        if timestamp is None:
            timestamp = datetime.now()
            
        self.data_points.append({'value': value, 'time': timestamp})
        
        # Keep only recent points
        if len(self.data_points) > self.max_points:
            self.data_points.pop(0)
        
        self.redraw()
    
    def redraw(self):
        """Redraw beautiful chart"""
        self.canvas.delete("all")
        
        chart_x = self.margin_left
        chart_y = self.margin_top
        
        # Draw chart background
        self.canvas.create_rectangle(
            chart_x, chart_y,
            chart_x + self.chart_width, chart_y + self.chart_height,
            fill=BonsaiTheme.COLORS['bg_accent'],
            outline=BonsaiTheme.COLORS['accent_green'],
            width=2
        )
        
        if len(self.data_points) < 2:
            self._draw_empty_chart()
            return
        
        # Get value range
        values = [point['value'] for point in self.data_points]
        min_val = min(values)
        max_val = max(values)
        
        # Ensure reasonable range
        if max_val == min_val:
            max_val = min_val + 10
        
        # Draw grid
        for i in range(1, 5):
            y = chart_y + (i / 4) * self.chart_height
            self.canvas.create_line(
                chart_x, y, chart_x + self.chart_width, y,
                fill=BonsaiTheme.COLORS['accent_green'],
                width=1, dash=(3, 3)
            )
        
        # Calculate points
        points = []
        for i, point in enumerate(self.data_points):
            x = chart_x + (i / (len(self.data_points) - 1)) * self.chart_width
            y = chart_y + self.chart_height - ((point['value'] - min_val) / (max_val - min_val)) * self.chart_height
            points.append((x, y))
        
        # Draw beautiful area fill
        if len(points) > 1:
            # Create area points
            area_points = [(chart_x, chart_y + self.chart_height)]
            area_points.extend(points)
            area_points.append((chart_x + self.chart_width, chart_y + self.chart_height))
            
            # Draw gradient-like area
            self.canvas.create_polygon(
                area_points,
                fill=BonsaiTheme.COLORS['accent_green'],
                outline="",
                stipple="gray50"
            )
        
        # Draw beautiful line
        for i in range(len(points) - 1):
            self.canvas.create_line(
                points[i][0], points[i][1],
                points[i+1][0], points[i+1][1],
                fill=BonsaiTheme.COLORS['secondary_green'],
                width=3, smooth=True
            )
        
        # Draw data points
        for i, (x, y) in enumerate(points):
            # Point circle
            self.canvas.create_oval(
                x-4, y-4, x+4, y+4,
                fill=BonsaiTheme.COLORS['primary_green'],
                outline=BonsaiTheme.COLORS['bg_card'],
                width=2
            )
            
            # Show value on last point
            if i == len(points) - 1:
                self.canvas.create_text(
                    x + 15, y,
                    text=f"{self.data_points[i]['value']:.1f}%",
                    font=BonsaiTheme.FONTS['body_bold'],
                    fill=BonsaiTheme.COLORS['primary_green'],
                    anchor="w"
                )
        
        # Draw Y-axis labels
        for i in range(5):
            y_pos = chart_y + (i / 4) * self.chart_height
            value = max_val - (i / 4) * (max_val - min_val)
            self.canvas.create_text(
                chart_x - 10, y_pos,
                text=f"{value:.1f}%",
                font=BonsaiTheme.FONTS['caption'],
                fill=BonsaiTheme.COLORS['text_secondary'],
                anchor="e"
            )


class DashboardTab:
    """Beautiful professional dashboard with green theme"""
    
    def __init__(self, parent, automation, data_manager, config):
        self.parent = parent
        self.automation = automation
        self.data_manager = data_manager
        self.config = config
        
        # Create main frame with beautiful styling
        self.frame = ttk.Frame(parent)
        self._create_beautiful_dashboard()
        
        # Data tracking
        self.moisture_history = []
        self.last_update = None
    
    def _create_beautiful_dashboard(self):
        """Create stunning dashboard layout"""
        # Main container with proper padding
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill="both", expand=True, padx=BonsaiTheme.SPACING['lg'], 
                           pady=BonsaiTheme.SPACING['md'])
        
        # Beautiful quick status header
        self._create_quick_status(main_container)
        
        # Main content in scrollable area
        self._create_scrollable_content(main_container)
    
    def _create_quick_status(self, parent):
        """Create beautiful quick status header"""
        status_card = ttk.Frame(parent)
        status_card.configure(style='Card.TFrame')
        status_card.pack(fill="x", pady=(0, BonsaiTheme.SPACING['lg']))
        
        # Header container
        header_container = ttk.Frame(status_card)
        header_container.pack(fill="x", padx=BonsaiTheme.SPACING['lg'], 
                             pady=BonsaiTheme.SPACING['md'])
        
        # Title with icon
        title_frame = ttk.Frame(header_container)
        title_frame.pack(fill="x")
        
        title_label = ttk.Label(title_frame, text="🏠 Dashboard Overview",
                               font=BonsaiTheme.FONTS['heading_medium'],
                               foreground=BonsaiTheme.COLORS['primary_green'])
        title_label.pack(side="left")
        
        # Current time
        self.time_label = ttk.Label(title_frame, text="",
                                   font=BonsaiTheme.FONTS['body'],
                                   foreground=BonsaiTheme.COLORS['text_muted'])
        self.time_label.pack(side="right")
        
        # Quick metrics row
        metrics_row = ttk.Frame(header_container)
        metrics_row.pack(fill="x", pady=(BonsaiTheme.SPACING['md'], 0))
        
        # Moisture quick display
        moisture_frame = ttk.Frame(metrics_row)
        moisture_frame.pack(side="left", padx=(0, BonsaiTheme.SPACING['xl']))
        
        ttk.Label(moisture_frame, text="💧 Current Moisture",
                 font=BonsaiTheme.FONTS['caption'],
                 foreground=BonsaiTheme.COLORS['text_muted']).pack(anchor="w")
        
        self.quick_moisture = ttk.Label(moisture_frame, text="---%",
                                       font=BonsaiTheme.FONTS['heading_small'],
                                       foreground=BonsaiTheme.COLORS['secondary_green'])
        self.quick_moisture.pack(anchor="w")
        
        # Automation quick display
        auto_frame = ttk.Frame(metrics_row)
        auto_frame.pack(side="left", padx=(0, BonsaiTheme.SPACING['xl']))
        
        ttk.Label(auto_frame, text="🤖 Automation Status",
                 font=BonsaiTheme.FONTS['caption'],
                 foreground=BonsaiTheme.COLORS['text_muted']).pack(anchor="w")
        
        self.quick_auto = ttk.Label(auto_frame, text="Starting...",
                                   font=BonsaiTheme.FONTS['heading_small'],
                                   foreground=BonsaiTheme.COLORS['primary_green'])
        self.quick_auto.pack(anchor="w")
        
        # Plant status quick display
        plant_frame = ttk.Frame(metrics_row)
        plant_frame.pack(side="left")
        
        ttk.Label(plant_frame, text="🌱 Plant Health",
                 font=BonsaiTheme.FONTS['caption'],
                 foreground=BonsaiTheme.COLORS['text_muted']).pack(anchor="w")
        
        self.quick_plant = ttk.Label(plant_frame, text="Monitoring...",
                                    font=BonsaiTheme.FONTS['heading_small'],
                                    foreground=BonsaiTheme.COLORS['success'])
        self.quick_plant.pack(anchor="w")
    
    def _create_scrollable_content(self, parent):
        """Create scrollable main content area"""
        # Canvas and scrollbar for scrolling
        canvas = tk.Canvas(parent, bg=BonsaiTheme.COLORS['bg_main'],
                          highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Make scrollable frame expand to canvas width
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas_width = canvas.winfo_width()
            if canvas_width > 0:
                canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas.bind('<Configure>', configure_scroll_region)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # FIXED: Proper mouse wheel scrolling
        def _on_mousewheel(event):
            # Windows
            if event.delta:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            # Linux
            else:
                if event.num == 4:
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    canvas.yview_scroll(1, "units")
        
        # Bind mouse wheel to canvas and all its children
        def bind_mouse_wheel(widget):
            # Windows
            widget.bind("<MouseWheel>", _on_mousewheel)
            # Linux
            widget.bind("<Button-4>", _on_mousewheel)
            widget.bind("<Button-5>", _on_mousewheel)
            # Bind to all children recursively
            for child in widget.winfo_children():
                bind_mouse_wheel(child)
        
        # Initial binding
        bind_mouse_wheel(canvas)
        bind_mouse_wheel(scrollable_frame)
        
        # Re-bind when new widgets are added
        scrollable_frame.bind("<Map>", lambda e: bind_mouse_wheel(scrollable_frame))
        
        # Create dashboard sections
        self._create_system_status(scrollable_frame)
        self._create_metrics_section(scrollable_frame)
        self._create_charts_section(scrollable_frame)
        self._create_recent_activity(scrollable_frame)
    
    def _create_system_status(self, parent):
        """Create beautiful system status section"""
        create_section_header(parent, "System Health Status", 1)
        
        # Status grid
        status_container = ttk.Frame(parent)
        status_container.pack(fill="x", pady=BonsaiTheme.SPACING['md'])
        
        # Create beautiful status indicators
        self.plant_status = StatusIndicator(status_container, "Plant Health", "🌱")
        self.plant_status.frame.pack(side="left", fill="both", expand=True, 
                                    padx=(0, BonsaiTheme.SPACING['sm']))
        
        self.automation_status = StatusIndicator(status_container, "Automation", "🤖")
        self.automation_status.frame.pack(side="left", fill="both", expand=True, 
                                         padx=BonsaiTheme.SPACING['sm'])
        
        self.sensor_status = StatusIndicator(status_container, "Sensors", "📡")
        self.sensor_status.frame.pack(side="left", fill="both", expand=True, 
                                     padx=BonsaiTheme.SPACING['sm'])
        
        self.pump_status = StatusIndicator(status_container, "Pump System", "⚙️")
        self.pump_status.frame.pack(side="right", fill="both", expand=True, 
                                   padx=(BonsaiTheme.SPACING['sm'], 0))
    
    def _create_metrics_section(self, parent):
        """Create beautiful key metrics section"""
        add_separator(parent)
        create_section_header(parent, "Key Performance Metrics", 1)
        
        metrics_container = ttk.Frame(parent)
        metrics_container.pack(fill="x", pady=BonsaiTheme.SPACING['md'])
        
        # Create metric cards
        self.moisture_card, self.moisture_value, _ = create_status_card(
            metrics_container, "Current Moisture Level", "--", "%", "normal"
        )
        self.moisture_card.pack(side="left", fill="both", expand=True, 
                               padx=(0, BonsaiTheme.SPACING['sm']))
        
        self.water_usage_card, self.water_usage_value, _ = create_status_card(
            metrics_container, "Today's Water Usage", "0", "seconds", "normal"
        )
        self.water_usage_card.pack(side="left", fill="both", expand=True, 
                                  padx=BonsaiTheme.SPACING['sm'])
        
        self.next_watering_card, self.next_watering_value, _ = create_status_card(
            metrics_container, "Next Watering", "Available", "", "normal"
        )
        self.next_watering_card.pack(side="left", fill="both", expand=True, 
                                    padx=BonsaiTheme.SPACING['sm'])
        
        self.uptime_card, self.uptime_value, _ = create_status_card(
            metrics_container, "System Uptime", "Active", "", "normal"
        )
        self.uptime_card.pack(side="right", fill="both", expand=True, 
                             padx=(BonsaiTheme.SPACING['sm'], 0))
    
    def _create_charts_section(self, parent):
        """Create beautiful charts section"""
        add_separator(parent)
        create_section_header(parent, "Real-time Analytics", 1)
        
        charts_container = ttk.Frame(parent)
        charts_container.pack(fill="both", expand=True, pady=BonsaiTheme.SPACING['md'])
        
        # Moisture trend chart
        self.moisture_chart = BeautifulChart(charts_container, "Moisture Trend (Last 30 Readings)")
        self.moisture_chart.frame.pack(side="left", fill="both", expand=True, 
                                      padx=(0, BonsaiTheme.SPACING['sm']))
        
        # Daily summary chart
        self.daily_chart = BeautifulChart(charts_container, "Daily Averages (Last 7 Days)")
        self.daily_chart.frame.pack(side="right", fill="both", expand=True, 
                                    padx=(BonsaiTheme.SPACING['sm'], 0))
    
    def _create_recent_activity(self, parent):
        """Create beautiful recent activity section"""
        add_separator(parent)
        create_section_header(parent, "Recent System Activity", 1)
        
        activity_card = create_professional_card(parent, "📋 Activity Log")
        activity_card.pack(fill="x", pady=BonsaiTheme.SPACING['md'])
        
        # Create beautiful treeview
        columns = ("Time", "Event", "Details")
        self.activity_tree = ttk.Treeview(activity_card, columns=columns, 
                                         show="headings", height=8)
        
        # Configure columns with beautiful headers
        self.activity_tree.heading("Time", text="🕐 Time")
        self.activity_tree.heading("Event", text="📋 Event") 
        self.activity_tree.heading("Details", text="📝 Details")
        
        self.activity_tree.column("Time", width=120, minwidth=100)
        self.activity_tree.column("Event", width=150, minwidth=120)
        self.activity_tree.column("Details", width=300, minwidth=200)
        
        # Scrollbar for activity
        activity_scroll = ttk.Scrollbar(activity_card, orient="vertical", 
                                       command=self.activity_tree.yview)
        self.activity_tree.configure(yscrollcommand=activity_scroll.set)
        
        self.activity_tree.pack(side="left", fill="both", expand=True)
        activity_scroll.pack(side="right", fill="y")
    
    def update_display(self):
        """Update all beautiful dashboard elements"""
        try:
            status = self.automation.get_status()
            
            # Update beautiful quick status
            self._update_quick_status(status)
            
            # Update system status indicators
            self._update_status_indicators(status)
            
            # Update metrics cards
            self._update_metrics(status)
            
            # Update beautiful charts
            self._update_charts()
            
            # Update activity log
            self._update_activity_log()
            
        except Exception as e:
            print(f"Error updating beautiful dashboard: {e}")
    
    def _update_quick_status(self, status):
        """Update beautiful quick status header"""
        # Time
        current_time = datetime.now().strftime("%A, %B %d  •  %H:%M:%S")
        self.time_label.config(text=current_time)
        
        # Moisture with beautiful color coding
        moisture = status.get('last_moisture')
        if moisture is not None:
            self.quick_moisture.config(text=f"{moisture:.1f}%")
            
            if moisture < 15:
                color = BonsaiTheme.COLORS['error']
            elif moisture < 30:
                color = BonsaiTheme.COLORS['warning']
            else:
                color = BonsaiTheme.COLORS['success']
            
            self.quick_moisture.config(foreground=color)
        else:
            self.quick_moisture.config(text="---", 
                                     foreground=BonsaiTheme.COLORS['text_muted'])
        
        # Automation status
        auto_running = status.get('running', False)
        auto_active = status.get('automation_active', False)
        
        if auto_active:
            self.quick_auto.config(text="💧 WATERING", 
                                 foreground=BonsaiTheme.COLORS['info'])
        elif auto_running:
            self.quick_auto.config(text="✅ MONITORING", 
                                 foreground=BonsaiTheme.COLORS['success'])
        else:
            self.quick_auto.config(text="⏸️ PAUSED", 
                                 foreground=BonsaiTheme.COLORS['warning'])
        
        # Plant health
        plant_state = status.get('current_state', 'unknown')
        state_colors = {
            "healthy": (BonsaiTheme.COLORS['success'], "💚 THRIVING"),
            "needs_water": (BonsaiTheme.COLORS['warning'], "💛 NEEDS WATER"),
            "critical": (BonsaiTheme.COLORS['error'], "❤️ CRITICAL"),
            "recently_watered": (BonsaiTheme.COLORS['info'], "💙 WELL WATERED"),
            "sensor_error": (BonsaiTheme.COLORS['text_muted'], "❓ UNKNOWN")
        }
        
        color, text = state_colors.get(plant_state, 
                                     (BonsaiTheme.COLORS['text_muted'], "❓ UNKNOWN"))
        self.quick_plant.config(text=text, foreground=color)
    
    def _update_status_indicators(self, status):
        """Update beautiful status indicators"""
        # Plant health
        plant_state = status.get('current_state', 'unknown')
        moisture = status.get('last_moisture')
        moisture_text = f"{moisture:.1f}%" if moisture is not None else "No reading"
        self.plant_status.update(plant_state, moisture_text)
        
        # Automation
        auto_status = "running" if status.get('running') else "stopped"
        if status.get('automation_active'):
            auto_status = "watering"
        self.automation_status.update(auto_status)
        
        # Sensors
        sensor_status = "connected" if moisture is not None else "disconnected"
        self.sensor_status.update(sensor_status)
        
        # Pump
        pump_status = "running" if self.automation.pump.is_running() else "stopped"
        runtime = f"{self.automation.pump.get_runtime_seconds():.1f}s total"
        self.pump_status.update(pump_status, runtime)
    
    def _update_metrics(self, status):
        """Update beautiful metric cards"""
        # Current moisture
        moisture = status.get('last_moisture')
        if moisture is not None:
            self.moisture_value.config(text=f"{moisture:.1f}")
            
            if moisture < 20:
                color = BonsaiTheme.COLORS['error']
                status_type = "error"
            elif moisture < 40:
                color = BonsaiTheme.COLORS['warning']
                status_type = "warning"
            else:
                color = BonsaiTheme.COLORS['success']
                status_type = "normal"
            
            self.moisture_value.config(foreground=color)
        
        # Daily usage
        try:
            today_summary = self.data_manager.get_daily_summary()
            water_time = today_summary.get('total_water_time', 0)
            self.water_usage_value.config(text=f"{water_time:.1f}")
        except:
            self.water_usage_value.config(text="0.0")
        
        # Next watering
        if status.get('can_water'):
            self.next_watering_value.config(text="Available",
                                          foreground=BonsaiTheme.COLORS['success'])
        else:
            cooldown_remaining = self.config.system.watering_cooldown_hours * 3600
            cooldown_remaining -= self.automation.cooldown_manager.seconds_since_last()
            hours_remaining = max(0, cooldown_remaining / 3600)
            self.next_watering_value.config(text=f"{hours_remaining:.1f}h",
                                          foreground=BonsaiTheme.COLORS['warning'])
    
    def _update_charts(self):
        """Update beautiful charts"""
        # Moisture trend
        moisture_history = self.data_manager.get_moisture_history(hours=12)
        for reading in moisture_history[-5:]:  # Add recent readings
            self.moisture_chart.add_data_point(reading.moisture_percent, reading.timestamp)
        
        # Daily summaries
        for i in range(7):
            date = datetime.now() - timedelta(days=i)
            summary = self.data_manager.get_daily_summary(date)
            if summary['moisture_avg'] > 0:
                self.daily_chart.add_data_point(summary['moisture_avg'], date)
    
    def _update_activity_log(self):
        """Update beautiful activity log"""
        # Clear existing entries
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        
        try:
            # Get recent watering events
            watering_events = self.data_manager.get_watering_history(days=1)
            
            for event in watering_events[:10]:
                time_str = event.timestamp.strftime("%H:%M:%S")
                event_icon = "💧" if event.event_type == "AUTO" else "🎮" if event.event_type == "MANUAL" else "🔧"
                
                self.activity_tree.insert("", "end", values=(
                    time_str,
                    f"{event_icon} {event.event_type.title()}",
                    f"Duration: {event.duration_seconds:.1f}s • Moisture: {event.trigger_moisture or 'N/A'}%"
                ))
                
        except Exception as e:
            self.activity_tree.insert("", "end", values=(
                datetime.now().strftime("%H:%M:%S"),
                "⚠️ System",
                f"Error loading activity: {str(e)}"
            ))
    
    def on_state_changed(self, old_state, new_state):
        """Handle plant state changes"""
        pass  # Updates happen in regular cycle
    
    def on_moisture_update(self, moisture: float):
        """Handle moisture updates"""
        self.moisture_history.append((datetime.now(), moisture))
        if len(self.moisture_history) > 50:
            self.moisture_history.pop(0)