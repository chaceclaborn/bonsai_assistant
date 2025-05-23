# File: simulation/mock_sensor.py

import random
import time

class MockSoilMoistureSensor:
    """Mock soil moisture sensor for testing with live value updates"""
    
    def __init__(self, moisture_func=None):
        self.moisture_func = moisture_func or self._default_moisture
        self.available = True
        self.noise_factor = 1.5  # Add some realistic noise
        
    def _default_moisture(self):
        """Default moisture simulation with gradual decrease over time"""
        # Simulate moisture decreasing over time with some randomness
        base_time = time.time() % 86400  # Daily cycle
        daily_factor = 50 + 30 * (1 - (base_time / 86400))  # Decrease through day
        noise = random.uniform(-self.noise_factor, self.noise_factor)
        return max(0, min(100, daily_factor + noise))
    
    def read_moisture_percent(self):
        """Return simulated moisture percentage"""
        if not self.available:
            return None
        
        try:
            # Call the moisture function (which could be a lambda from settings)
            moisture = self.moisture_func()
            
            # Add some small random variation to make it realistic
            variation = random.uniform(-0.5, 0.5)
            final_moisture = max(0, min(100, moisture + variation))
            
            return round(final_moisture, 1)
        except Exception as e:
            print(f"Mock sensor error: {e}")
            return None
    
    def read_raw_adc(self):
        """Return simulated raw ADC value"""
        moisture = self.read_moisture_percent()
        if moisture is None:
            return None
        
        # Convert percentage back to simulated ADC value
        # Dry: ~32000, Wet: ~12000
        dry_val = 32000
        wet_val = 12000
        raw_value = dry_val - (moisture / 100) * (dry_val - wet_val)
        return int(raw_value + random.uniform(-300, 300))  # Add noise


# File: simulation/mock_pump.py

import time
import threading

class MockPumpController:
    """Mock pump controller for testing"""
    
    def __init__(self):
        self._start_time = None
        self._total_runtime = 0.0
        self._running = False
        self._pulsing = False
        self._pulse_thread = None
        self._lock = threading.Lock()
        print("🔧 Mock pump controller initialized")
    
    def turn_on(self):
        """Simulate turning pump on"""
        with self._lock:
            if not self._running:
                self._start_time = time.time()
                self._running = True
                print("🚿 [MOCK] Pump ON")
    
    def turn_off(self):
        """Simulate turning pump off"""
        with self._lock:
            if self._running and self._start_time:
                self._total_runtime += time.time() - self._start_time
            self._running = False
            self._start_time = None
            print("🛑 [MOCK] Pump OFF")
    
    def run_timed(self, duration_sec):
        """Simulate timed pump operation"""
        def worker():
            print(f"⏱️ [MOCK] Running pump for {duration_sec} seconds")
            self.turn_on()
            time.sleep(duration_sec)
            self.turn_off()
        
        threading.Thread(target=worker, daemon=True).start()
    
    def start_pulsing(self, pulse_on=0.3125, pulse_off=0.3125, total_duration=15):
        """Simulate pulse operation"""
        if self._pulsing:
            print("⚠️ [MOCK] Already pulsing. Ignored.")
            return
        
        def pulser():
            self._pulsing = True
            print(f"🔁 [MOCK] Starting pulse: {pulse_on}s ON, {pulse_off}s OFF for {total_duration}s")
            end_time = time.time() + total_duration
            
            while self._pulsing and time.time() < end_time:
                self.turn_on()
                time.sleep(pulse_on)
                self.turn_off()
                time.sleep(pulse_off)
            
            self._pulsing = False
            print("✅ [MOCK] Pulse sequence complete")
        
        self._pulse_thread = threading.Thread(target=pulser, daemon=True)
        self._pulse_thread.start()
    
    def stop_pulsing(self):
        """Stop pulse operation"""
        print("⛔ [MOCK] Stop pulse requested")
        self._pulsing = False
        self.turn_off()
    
    def is_running(self):
        """Check if pump is running"""
        return self._running or self._pulsing
    
    def get_status(self):
        """Get pump status"""
        return "ON" if self.is_running() else "OFF"
    
    def get_runtime_seconds(self):
        """Get total runtime"""
        if self._running and self._start_time:
            return round(self._total_runtime + (time.time() - self._start_time), 2)
        return round(self._total_runtime, 2)
    
    def close(self):
        """Close mock pump"""
        print("🔌 [MOCK] Releasing mock GPIO resources")
        self._pulsing = False
        self.turn_off()


# File: simulation/mock_display.py

from datetime import datetime

class MockDisplay:
    """Mock RGB display for testing"""
    
    def __init__(self, width=128, height=128):
        self.width = width
        self.height = height
        self.is_simulated = True
        print("📺 Mock display initialized")
    
    def clear(self):
        """Clear display"""
        print("🩹 [MOCK] Display cleared")
    
    def draw_status(self, moisture=None, pump_status="OFF", runtime_sec=0):
        """Draw status information"""
        current_time = datetime.now().strftime("%H:%M")
        moisture_str = f"{moisture:.1f}%" if moisture is not None else "---"
        
        status_info = f"""
[MOCK DISPLAY] {current_time}
Bonsai Assistant
Moisture: {moisture_str}
Pump: {pump_status} | {int(runtime_sec)}s
        """.strip()
        
        print(f"📺 {status_info}")


# File: simulation/__init__.py

"""
Simulation module for testing Bonsai Assistant without hardware
"""

from .mock_sensor import MockSoilMoistureSensor
from .mock_pump import MockPumpController  
from .mock_display import MockDisplay

__all__ = ['MockSoilMoistureSensor', 'MockPumpController', 'MockDisplay']