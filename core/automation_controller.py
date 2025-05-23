# File: core/automation_controller.py

import time
import threading
from datetime import datetime, timedelta
from typing import Callable, Optional, Dict, Any, List
from enum import Enum
import json

class WateringTrigger(Enum):
    MOISTURE_LOW = "moisture_low"
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    EMERGENCY = "emergency"

class PlantState(Enum):
    HEALTHY = "healthy"
    NEEDS_WATER = "needs_water"
    RECENTLY_WATERED = "recently_watered"
    SENSOR_ERROR = "sensor_error"
    CRITICAL = "critical"

class AutomationController:
    def __init__(self, sensor, pump, display, cooldown_manager, data_manager, config):
        self.sensor = sensor
        self.pump = pump
        self.display = display
        self.cooldown_manager = cooldown_manager
        self.data_manager = data_manager
        self.config = config
        
        # State management
        self.running = False
        self.current_state = PlantState.HEALTHY
        self.last_moisture_reading = None
        self.last_sensor_warning = 0
        self.automation_active = False
        
        # Callbacks for UI updates
        self.state_change_callbacks: List[Callable] = []
        self.moisture_update_callbacks: List[Callable] = []
        
        # Advanced features
        self.watering_schedule = {}  # Time-based watering schedule
        self.adaptive_threshold = self.config.sensor.moisture_threshold
        self.consecutive_low_readings = 0
        
        # Thread management
        self.automation_thread = None
        self.stop_event = threading.Event()
        
    def add_state_callback(self, callback: Callable):
        """Add callback for state changes"""
        self.state_change_callbacks.append(callback)
        
    def add_moisture_callback(self, callback: Callable):
        """Add callback for moisture updates"""
        self.moisture_update_callbacks.append(callback)
    
    def start_automation(self):
        """Start the automation loop"""
        if self.running:
            return
            
        self.running = True
        self.stop_event.clear()
        self.automation_thread = threading.Thread(target=self._automation_loop, daemon=True)
        self.automation_thread.start()
        
        self.data_manager.log_system_event("AUTOMATION", "Automation started", "INFO")
    
    def stop_automation(self):
        """Stop the automation loop"""
        self.running = False
        self.stop_event.set()
        if self.automation_thread:
            self.automation_thread.join(timeout=5)
            
        self.data_manager.log_system_event("AUTOMATION", "Automation stopped", "INFO")
    
    def _automation_loop(self):
        """Main automation loop - runs in separate thread"""
        while self.running and not self.stop_event.is_set():
            try:
                self._check_and_update_state()
                self._execute_automation_logic()
                self._check_scheduled_watering()
                
                # Log moisture reading periodically
                if self.last_moisture_reading is not None:
                    self.data_manager.log_moisture_reading(
                        self.last_moisture_reading,
                        channel=0  # Could be expanded for multiple sensors
                    )
                
            except Exception as e:
                self.data_manager.log_system_event(
                    "AUTOMATION_ERROR", 
                    f"Automation loop error: {str(e)}", 
                    "ERROR"
                )
                
            self.stop_event.wait(self.config.system.refresh_interval_sec)
    
    def _check_and_update_state(self):
        """Read sensors and update plant state"""
        try:
            moisture = self.sensor.read_moisture_percent()
            
            if moisture is None:
                self._handle_sensor_error()
                return
                
            self.last_moisture_reading = moisture
            
            # Update adaptive threshold based on history
            self._update_adaptive_threshold()
            
            # Determine new state
            new_state = self._calculate_plant_state(moisture)
            
            if new_state != self.current_state:
                old_state = self.current_state
                self.current_state = new_state
                self._notify_state_change(old_state, new_state)
                
            # Notify moisture update callbacks
            for callback in self.moisture_update_callbacks:
                try:
                    callback(moisture)
                except Exception as e:
                    print(f"Error in moisture callback: {e}")
                    
        except Exception as e:
            self.data_manager.log_system_event(
                "SENSOR_ERROR", 
                f"Sensor reading failed: {str(e)}", 
                "ERROR"
            )
    
    def _calculate_plant_state(self, moisture: float) -> PlantState:
        """Calculate plant state based on moisture and other factors"""
        if moisture < self.adaptive_threshold * 0.5:  # Critical threshold
            self.consecutive_low_readings += 1
            return PlantState.CRITICAL
        elif moisture < self.adaptive_threshold:
            self.consecutive_low_readings += 1
            return PlantState.NEEDS_WATER
        else:
            self.consecutive_low_readings = 0
            
            # Check if recently watered
            if not self.cooldown_manager.can_water():
                return PlantState.RECENTLY_WATERED
            else:
                return PlantState.HEALTHY
    
    def _execute_automation_logic(self):
        """Execute watering logic based on current state"""
        if self.automation_active:
            return  # Already executing automation
            
        if self.current_state == PlantState.CRITICAL:
            # Emergency watering - longer duration
            if self.cooldown_manager.can_water():
                self._execute_watering(
                    WateringTrigger.EMERGENCY,
                    duration_multiplier=1.5,
                    emergency=True
                )
        elif self.current_state == PlantState.NEEDS_WATER:
            # Regular watering with confirmation
            if (self.cooldown_manager.can_water() and 
                self.consecutive_low_readings >= 3):  # Require multiple low readings
                self._execute_watering(WateringTrigger.MOISTURE_LOW)
    
    def _execute_watering(self, trigger: WateringTrigger, duration_multiplier: float = 1.0, 
                         emergency: bool = False):
        """Execute watering sequence"""
        if self.automation_active and not emergency:
            return
            
        try:
            self.automation_active = True
            
            # Calculate watering parameters
            initial_duration = self.config.pump.initial_run_duration * duration_multiplier
            pulse_duration = self.config.pump.pulse_duration * duration_multiplier
            
            self.data_manager.log_system_event(
                "WATERING_START", 
                f"Starting {trigger.value} watering (duration: {pulse_duration}s)", 
                "INFO"
            )
            
            # Initial pump run
            self.pump.run_timed(initial_duration)
            time.sleep(initial_duration + 0.5)
            
            # Pulse watering for better soil penetration
            self.pump.start_pulsing(
                pulse_on=self.config.pump.pulse_on_time,
                pulse_off=self.config.pump.pulse_off_time,
                total_duration=pulse_duration
            )
            
            # Log the watering event
            self.data_manager.log_watering_event(
                duration=initial_duration + pulse_duration,
                trigger_moisture=self.last_moisture_reading,
                event_type=trigger.value.upper(),
                notes=f"Consecutive low readings: {self.consecutive_low_readings}"
            )
            
            # Update cooldown
            self.cooldown_manager.mark_watered()
            
            # Wait before resuming normal operations
            self.data_manager.log_system_event(
                "WATERING_COMPLETE", 
                f"Watering complete. Waiting {self.config.pump.post_water_wait}s", 
                "INFO"
            )
            
            time.sleep(self.config.pump.post_water_wait)
            
        except Exception as e:
            self.data_manager.log_system_event(
                "WATERING_ERROR", 
                f"Watering execution failed: {str(e)}", 
                "ERROR"
            )
        finally:
            self.automation_active = False
            self.consecutive_low_readings = 0
    
    def _handle_sensor_error(self):
        """Handle sensor reading failures"""
        now = time.time()
        if now - self.last_sensor_warning >= self.config.sensor.sensor_warning_interval:
            self.data_manager.log_system_event(
                "SENSOR_WARNING", 
                "Moisture sensor not responding", 
                "WARNING"
            )
            self.last_sensor_warning = now
            
        if self.current_state != PlantState.SENSOR_ERROR:
            old_state = self.current_state
            self.current_state = PlantState.SENSOR_ERROR
            self._notify_state_change(old_state, PlantState.SENSOR_ERROR)
    
    def _update_adaptive_threshold(self):
        """Update threshold based on historical data and patterns"""
        try:
            # Get recent moisture history
            history = self.data_manager.get_moisture_history(hours=24)
            if len(history) < 10:  # Need minimum data points
                return
                
            # Calculate average moisture when NOT recently watered
            watering_events = self.data_manager.get_watering_history(days=7)
            watered_times = [event.timestamp for event in watering_events]
            
            # Find moisture readings that are at least 4 hours after watering
            stable_readings = []
            for reading in history:
                time_since_watering = min([
                    abs((reading.timestamp - watered_time).total_seconds()) 
                    for watered_time in watered_times
                ] + [float('inf')])
                
                if time_since_watering > 4 * 3600:  # 4 hours
                    stable_readings.append(reading.moisture_percent)
            
            if len(stable_readings) >= 5:
                avg_stable = sum(stable_readings) / len(stable_readings)
                # Adjust threshold to be 10% below average stable reading
                new_threshold = max(15, min(50, avg_stable * 0.9))
                
                if abs(new_threshold - self.adaptive_threshold) > 2:
                    self.adaptive_threshold = round(new_threshold, 1)
                    self.data_manager.log_system_event(
                        "THRESHOLD_UPDATE", 
                        f"Adaptive threshold updated to {self.adaptive_threshold}%", 
                        "INFO"
                    )
                    
        except Exception as e:
            print(f"Error updating adaptive threshold: {e}")
    
    def _check_scheduled_watering(self):
        """Check for scheduled watering events"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_day = now.strftime("%A").lower()
        
        # Check if there's a scheduled watering for this time
        if current_day in self.watering_schedule:
            scheduled_times = self.watering_schedule[current_day]
            if current_time in scheduled_times:
                # Check if we haven't already watered at this scheduled time today
                last_scheduled = getattr(self, '_last_scheduled_watering', None)
                if (not last_scheduled or 
                    last_scheduled.date() != now.date() or
                    last_scheduled.strftime("%H:%M") != current_time):
                    
                    self._execute_watering(WateringTrigger.SCHEDULED)
                    self._last_scheduled_watering = now
    
    def _notify_state_change(self, old_state: PlantState, new_state: PlantState):
        """Notify callbacks of state changes"""
        self.data_manager.log_system_event(
            "STATE_CHANGE", 
            f"Plant state changed from {old_state.value} to {new_state.value}", 
            "INFO"
        )
        
        for callback in self.state_change_callbacks:
            try:
                callback(old_state, new_state)
            except Exception as e:
                print(f"Error in state change callback: {e}")
    
    def manual_water(self, duration: float = None, pulse: bool = True):
        """Manually trigger watering"""
        if not duration:
            duration = self.config.pump.initial_run_duration
            
        try:
            if pulse:
                self.pump.start_pulsing(
                    pulse_on=self.config.pump.pulse_on_time,
                    pulse_off=self.config.pump.pulse_off_time,
                    total_duration=duration
                )
            else:
                self.pump.run_timed(duration)
                
            self.data_manager.log_watering_event(
                duration=duration,
                trigger_moisture=self.last_moisture_reading,
                event_type="MANUAL",
                notes="Manual watering via UI"
            )
            
        except Exception as e:
            self.data_manager.log_system_event(
                "MANUAL_WATER_ERROR", 
                f"Manual watering failed: {str(e)}", 
                "ERROR"
            )
    
    def set_schedule(self, schedule: Dict[str, List[str]]):
        """Set watering schedule (e.g., {'monday': ['08:00', '18:00']})"""
        self.watering_schedule = schedule
        self.data_manager.log_system_event(
            "SCHEDULE_UPDATE", 
            f"Watering schedule updated: {json.dumps(schedule)}", 
            "INFO"
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get current automation status"""
        return {
            'running': self.running,
            'current_state': self.current_state.value,
            'last_moisture': self.last_moisture_reading,
            'adaptive_threshold': self.adaptive_threshold,
            'consecutive_low_readings': self.consecutive_low_readings,
            'automation_active': self.automation_active,
            'can_water': self.cooldown_manager.can_water(),
            'schedule': self.watering_schedule
        }