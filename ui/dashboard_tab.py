# File: ui/dashboard_tab.py

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from typing import Optional, List

class StatusIndicator:
    """Custom status indicator widget"""
    
    def __init__(self, parent, title: str, initial_status: str = "unknown"):
        self.frame = ttk.LabelFrame(parent, text=title, padding=10)
        
        # Status circle canvas
        self.canvas = tk.Canvas(self.frame, width=30, height=30, bg='white')
        self.canvas.pack(side="left", padx=(0, 10))
        
        # Status text
        self.status_label = ttk.Label(self.frame, text=initial_status, font=("Arial", 10, "bold"))
        self.status_label.pack(side="left")
        
        # Value label
        self.value_label = ttk.Label(self.frame, text="", font=("Arial", 9))
        self.value_label.pack(side="left", padx=(10, 0))
        
        self.current_status = initial_status
        self._draw_indicator()
    
    def update(self, status: str, value: str = "", color: str = None):
        """Update indicator status"""
        self.current_status = status
        self.status_label.config(text=status)
        self.value_label.config(text=value)
        
        if not color:
            color = self._get_status_color(status)
        
        self._draw_indicator(color)
    
    def _get_status_color(self, status: str) -> str:
        """Get color based on status"""
        status_colors = {
            "healthy": "#28a745",      # Green
            "needs_water": "#ffc107",   # Yellow
            "recently_watered": "#17a2b8",  # Blue
            "critical": "#dc3545",      # Red
            "sensor_error": "#6c757d",  # Gray
            "connected": "#28a745",
            "disconnected": "#dc3545",
            "running": "#28a745",
            "stopped": "#6c757d",
            "watering": "#007bff"
        }
        return status_colors.get(status.lower(), "#6c757d")
    
    def _draw_indicator(self, color: str = None):
        """Draw status indicator circle"""
        if not color:
            color = self._get_status_color(self.current_status)
        
        self.canvas.delete("all")
        self.canvas.create_oval(5, 5, 25, 25, fill=color, outline=color, width=2)


class MetricCard:
    """Metric display card widget"""
    
    def __init__(self, parent, title: str, value: str = "--", unit: str = "", 
                 trend: Optional[str] = None):
        self.frame = ttk.LabelFrame(parent, text=title, padding=15)
        
        # Main value
        self.value_label = ttk.Label(
            self.frame, 
            text=value, 
            font=("Arial", 18, "bold"),
            foreground="#2c3e50"
        )
        self.value_label.pack()
        
        # Unit label
        if unit:
            self.unit_label = ttk.Label(self.frame, text=unit, font=("Arial", 10))
            self.unit_label.pack()
        
        # Trend indicator
        self.trend_label = ttk.Label(self.frame, text="", font=("Arial", 9))
        self.trend_label.pack(pady=(5, 0))
        
        if trend:
            self.update_trend(trend)
    
    def update(self, value: str, trend: Optional[str] = None):
        """Update metric value and trend"""
        self.value_label.config(text=value)
        if trend:
            self.update_trend(trend)
    
    def update_trend(self, trend: str):
        """Update trend indicator"""
        if trend == "up":
            self.trend_label.config(text="↗ Increasing", foreground="#28a745")
        elif trend == "down":
            self.trend_label.config(text="↘ Decreasing", foreground="#dc3545")
        elif trend == "stable":
            self.trend_label.config(text="→ Stable", foreground="#6c757d")
        else:
            self.trend_label.config(text="")


class SimpleChart:
    """Simple ASCII-style chart widget"""
    
    def __init__(self, parent, title: str, width=400, height=150):
        self.frame = ttk.LabelFrame(parent, text=title, padding=10)
        
        # Create canvas for simple chart
        self.canvas = tk.Canvas(self.frame, width=width, height=height, bg='white')
        self.canvas.pack(fill="both", expand=True)
        
        # Data storage
        self.data_points = []
        self.max_points = 20
        self.width = width
        self.height = height
        
        # Chart margins
        self.margin_left = 40
        self.margin_right = 20
        self.margin_top = 20
        self.margin_bottom = 30
        
        self.chart_width = width - self.margin_left - self.margin_right
        self.chart_height = height - self.margin_top - self.margin_bottom
    
    def add_data_point(self, value: float, label: str = ""):
        """Add new data point"""
        self.data_points.append({'value': value, 'label': label, 'time': datetime.now()})
        
        # Keep only recent points
        if len(self.data_points) > self.max_points:
            self.data_points.pop(0)
        
        self.redraw()
    
    def redraw(self):
        """Redraw the simple chart"""
        self.canvas.delete("all")
        
        if len(self.data_points) < 2:
            # Show "No data" message
            self.canvas.create_text(
                self.width // 2, self.height // 2,
                text="No data available", 
                font=("Arial", 10),
                fill="#6c757d"
            )
            return
        
        # Get min/max values for scaling
        values = [point['value'] for point in self.data_points]
        min_val = min(values)
        max_val = max(values)
        
        if max_val == min_val:
            max_val = min_val + 1  # Avoid division by zero
        
        # Draw chart area
        chart_x = self.margin_left
        chart_y = self.margin_top
        
        # Draw border
        self.canvas.create_rectangle(
            chart_x, chart_y,
            chart_x + self.chart_width, chart_y + self.chart_height,
            outline="#e0e0e0", width=1
        )
        
        # Draw data points and lines
        points = []
        for i, point in enumerate(self.data_points):
            x = chart_x + (i / (len(self.data_points) - 1)) * self.chart_width
            y = chart_y + self.chart_height - ((point['value'] - min_val) / (max_val - min_val)) * self.chart_height
            points.append((x, y))
            
            # Draw point
            self.canvas.create_oval(x-2, y-2, x+2, y+2, fill="#007bff", outline="#007bff")
        
        # Draw lines between points
        for i in range(len(points) - 1):
            self.canvas.create_line(
                points[i][0], points[i][1],
                points[i+1][0], points[i+1][1],
                fill="#007bff", width=2
            )
        
        # Draw Y-axis labels
        for i in range(5):
            y_pos = chart_y + (i / 4) * self.chart_height
            value = max_val - (i / 4) * (max_val - min_val)
            self.canvas.create_text(
                chart_x - 10, y_pos,
                text=f"{value:.1f}",
                font=("Arial", 8),
                anchor="e"
            )
        
        # Draw latest value
        if self.data_points:
            latest = self.data_points[-1]['value']
            self.canvas.create_text(
                chart_x + self.chart_width + 10, points[-1][1],
                text=f"{latest:.1f}",
                font=("Arial", 9, "bold"),
                fill="#007bff",
                anchor="w"
            )


class DashboardTab:
    """Main dashboard tab with real-time system overview"""
    
    def __init__(self, parent, automation, data_manager, config):
        self.parent = parent
        self.automation = automation
        self.data_manager = data_manager
        self.config = config
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        self._create_dashboard()
        
        # Data for trends
        self.moisture_history = []
        self.last_update = None
    
    def _create_dashboard(self):
        """Create dashboard layout"""
        # Add import at top of file if not already there
        from ui.mini_status_widget import MiniStatusWidget
        
        # Mini status at top (but make it different since this IS the main dashboard)
        status_frame = ttk.LabelFrame(self.frame, text="Quick Status", padding=8)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        quick_status_container = ttk.Frame(status_frame)
        quick_status_container.pack(fill="x")
        
        # Current time
        self.time_label = ttk.Label(quick_status_container, text="", font=("Arial", 10, "bold"))
        self.time_label.pack(side="left")
        
        # Quick moisture display
        ttk.Separator(quick_status_container, orient="vertical").pack(side="left", fill="y", padx=10)
        
        self.quick_moisture = ttk.Label(quick_status_container, text="Moisture: ---%", font=("Arial", 10))
        self.quick_moisture.pack(side="left")
        
        # Quick automation status
        ttk.Separator(quick_status_container, orient="vertical").pack(side="left", fill="y", padx=10)
        
        self.quick_auto = ttk.Label(quick_status_container, text="Auto: Stopped", font=("Arial", 10))
        self.quick_auto.pack(side="left")
        
        # Main container with scrollable frame
        main_canvas = tk.Canvas(self.frame)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollable components
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create dashboard sections
        self._create_system_status(scrollable_frame)
        self._create_metrics_section(scrollable_frame)
        self._create_charts_section(scrollable_frame)
        self._create_recent_activity(scrollable_frame)
    
    def _create_system_status(self, parent):
        """Create system status indicators"""
        status_frame = ttk.LabelFrame(parent, text="System Status", padding=15)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        # Create status indicators
        indicators_frame = ttk.Frame(status_frame)
        indicators_frame.pack(fill="x")
        
        # Plant health indicator
        self.plant_status = StatusIndicator(indicators_frame, "Plant Health")
        self.plant_status.frame.pack(side="left", fill="x", expand=True, padx=5)
        
        # Automation status
        self.automation_status = StatusIndicator(indicators_frame, "Automation")
        self.automation_status.frame.pack(side="left", fill="x", expand=True, padx=5)
        
        # Sensor connectivity
        self.sensor_status = StatusIndicator(indicators_frame, "Sensors")
        self.sensor_status.frame.pack(side="left", fill="x", expand=True, padx=5)
        
        # Pump status
        self.pump_status = StatusIndicator(indicators_frame, "Pump")
        self.pump_status.frame.pack(side="left", fill="x", expand=True, padx=5)
    
    def _create_metrics_section(self, parent):
        """Create key metrics display"""
        metrics_frame = ttk.LabelFrame(parent, text="Key Metrics", padding=15)
        metrics_frame.pack(fill="x", padx=10, pady=5)
        
        metrics_container = ttk.Frame(metrics_frame)
        metrics_container.pack(fill="x")
        
        # Current moisture
        self.moisture_metric = MetricCard(metrics_container, "Current Moisture", "--", "%")
        self.moisture_metric.frame.pack(side="left", fill="x", expand=True, padx=5)
        
        # Daily water usage
        self.water_usage_metric = MetricCard(metrics_container, "Today's Watering", "0", "seconds")
        self.water_usage_metric.frame.pack(side="left", fill="x", expand=True, padx=5)
        
        # Next watering
        self.next_watering_metric = MetricCard(metrics_container, "Next Watering", "Available", "")
        self.next_watering_metric.frame.pack(side="left", fill="x", expand=True, padx=5)
        
        # System uptime
        self.uptime_metric = MetricCard(metrics_container, "Uptime", "Running", "")
        self.uptime_metric.frame.pack(side="left", fill="x", expand=True, padx=5)
    
    def _create_charts_section(self, parent):
        """Create simple charts section"""
        charts_frame = ttk.LabelFrame(parent, text="Real-time Data", padding=15)
        charts_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        charts_container = ttk.Frame(charts_frame)
        charts_container.pack(fill="both", expand=True)
        
        # Moisture trend chart
        self.moisture_chart = SimpleChart(charts_container, "Moisture Trend (Recent)")
        self.moisture_chart.frame.pack(side="left", fill="both", expand=True, padx=5)
        
        # Daily summary chart
        self.daily_chart = SimpleChart(charts_container, "Daily Averages")
        self.daily_chart.frame.pack(side="left", fill="both", expand=True, padx=5)
    
    def _create_recent_activity(self, parent):
        """Create recent activity log"""
        activity_frame = ttk.LabelFrame(parent, text="Recent Activity", padding=15)
        activity_frame.pack(fill="x", padx=10, pady=5)
        
        # Create treeview for activity log
        columns = ("Time", "Event", "Details")
        self.activity_tree = ttk.Treeview(activity_frame, columns=columns, show="headings", height=6)
        
        # Configure columns
        self.activity_tree.heading("Time", text="Time")
        self.activity_tree.heading("Event", text="Event")
        self.activity_tree.heading("Details", text="Details")
        
        self.activity_tree.column("Time", width=120, minwidth=80)
        self.activity_tree.column("Event", width=150, minwidth=100)
        self.activity_tree.column("Details", width=300, minwidth=200)
        
        # Add scrollbar for activity log
        activity_scroll = ttk.Scrollbar(activity_frame, orient="vertical", command=self.activity_tree.yview)
        self.activity_tree.configure(yscrollcommand=activity_scroll.set)
        
        self.activity_tree.pack(side="left", fill="both", expand=True)
        activity_scroll.pack(side="right", fill="y")
    
    def update_display(self):
        """Update all dashboard elements"""
        try:
            # Get current status
            status = self.automation.get_status()
            
            # Update quick status bar
            current_time = datetime.now().strftime("%H:%M:%S")
            self.time_label.config(text=current_time)
            
            moisture = status.get('last_moisture')
            if moisture is not None:
                self.quick_moisture.config(text=f"Moisture: {moisture:.1f}%")
                # Color coding
                if moisture < 20:
                    color = "#dc3545"
                elif moisture < 40:
                    color = "#ffc107"
                else:
                    color = "#28a745"
                self.quick_moisture.config(foreground=color)
            else:
                self.quick_moisture.config(text="Moisture: ---", foreground="#6c757d")
            
            auto_running = status.get('running', False)
            auto_active = status.get('automation_active', False)
            
            if auto_active:
                self.quick_auto.config(text="Auto: WATERING", foreground="#007bff")
            elif auto_running:
                self.quick_auto.config(text="Auto: Running", foreground="#28a745")
            else:
                self.quick_auto.config(text="Auto: Stopped", foreground="#6c757d")
            
            # Update system status indicators
            self._update_status_indicators(status)
            
            # Update metrics
            self._update_metrics(status)
            
            # Update charts
            self._update_charts()
            
            # Update activity log
            self._update_activity_log()
            
        except Exception as e:
            print(f"Error updating dashboard: {e}")
    
    def _update_status_indicators(self, status):
        """Update status indicator widgets"""
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
        pump_status = "running" if self.automation.pump.is_running() else "idle"
        runtime = f"{self.automation.pump.get_runtime_seconds():.1f}s total"
        self.pump_status.update(pump_status, runtime)
    
    def _update_metrics(self, status):
        """Update metric cards"""
        # Current moisture with trend
        moisture = status.get('last_moisture')
        if moisture is not None:
            trend = self._calculate_moisture_trend()
            self.moisture_metric.update(f"{moisture:.1f}", trend)
        
        # Daily water usage
        today_summary = self.data_manager.get_daily_summary()
        water_time = today_summary.get('total_water_time', 0)
        self.water_usage_metric.update(f"{water_time:.1f}")
        
        # Next watering availability
        if status.get('can_water'):
            self.next_watering_metric.update("Available", "stable")
        else:
            # Calculate time until next watering
            cooldown_remaining = self.config.system.watering_cooldown_hours * 3600
            cooldown_remaining -= self.automation.cooldown_manager.seconds_since_last()
            hours_remaining = max(0, cooldown_remaining / 3600)
            self.next_watering_metric.update(f"{hours_remaining:.1f}h", "down")
    
    def _update_charts(self):
        """Update simple charts with latest data"""
        # Update moisture trend chart
        moisture_history = self.data_manager.get_moisture_history(hours=6)
        if moisture_history:
            # Add recent readings to chart
            for reading in moisture_history[-10:]:  # Show last 10 points
                self.moisture_chart.add_data_point(reading.moisture_percent)
        
        # Update daily summary chart
        for i in range(7):
            date = datetime.now() - timedelta(days=i)
            summary = self.data_manager.get_daily_summary(date)
            if summary['moisture_avg'] > 0:
                self.daily_chart.add_data_point(
                    summary['moisture_avg'], 
                    date.strftime("%m/%d")
                )
    
    def _update_activity_log(self):
        """Update recent activity log"""
        # Clear existing entries
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        
        try:
            # Get recent watering events
            watering_events = self.data_manager.get_watering_history(days=1)
            recent_events = []
            
            for event in watering_events[:5]:
                recent_events.append({
                    'timestamp': event.timestamp,
                    'event': 'Watering',
                    'details': f"{event.event_type} - {event.duration_seconds:.1f}s"
                })
            
            # Sort by timestamp
            recent_events.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Add to treeview
            for event in recent_events[:10]:
                time_str = event['timestamp'].strftime("%H:%M:%S")
                self.activity_tree.insert("", "end", values=(
                    time_str,
                    event['event'],
                    event['details']
                ))
                
        except Exception as e:
            # Add error entry if something goes wrong
            self.activity_tree.insert("", "end", values=(
                datetime.now().strftime("%H:%M:%S"),
                "Error",
                f"Failed to load activity: {str(e)}"
            ))
    
    def _calculate_moisture_trend(self):
        """Calculate moisture trend over recent readings"""
        try:
            recent_readings = self.data_manager.get_moisture_history(hours=2)
            if len(recent_readings) < 5:
                return "stable"
            
            # Get values from last 5 readings
            values = [r.moisture_percent for r in recent_readings[-5:]]
            
            # Simple trend calculation
            if values[-1] > values[0] + 2:
                return "up"
            elif values[-1] < values[0] - 2:
                return "down"
            else:
                return "stable"
                
        except:
            return "stable"
    
    def on_state_changed(self, old_state, new_state):
        """Handle plant state changes from automation"""
        # Update will happen on next scheduled update
        pass
    
    def on_moisture_update(self, moisture: float):
        """Handle moisture reading updates"""
        # Store for trend calculation
        self.moisture_history.append((datetime.now(), moisture))
        
        # Keep only recent history for trend calculation
        if len(self.moisture_history) > 20:
            self.moisture_history.pop(0)