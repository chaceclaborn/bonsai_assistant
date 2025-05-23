# File: hardware/actuators/pump_controller.py
# Optional enhancement to your existing pump

import threading
import time
from typing import Optional, Callable, Dict, Any
from gpiozero import OutputDevice
from gpiozero.pins.lgpio import LGPIOFactory

class PumpController:
    """
    Enhanced pump controller with additional safety and monitoring features
    This is optional - your existing pump controller works fine!
    """
    
    def __init__(self, gpio_pin=18, max_continuous_runtime=300, safety_enabled=True):
        """
        Enhanced pump with safety features
        
        Args:
            gpio_pin: GPIO pin number
            max_continuous_runtime: Maximum continuous run time in seconds
            safety_enabled: Enable safety checks and limits
        """
        factory = LGPIOFactory()
        self.pump = OutputDevice(gpio_pin, active_high=True, initial_value=False, pin_factory=factory)
        
        # Runtime tracking
        self._start_time = None
        self._total_runtime = 0.0
        self._session_runtime = 0.0
        self._running = False
        self._pulsing = False
        self._pulse_thread = None
        self._lock = threading.Lock()
        
        # Safety features
        self.safety_enabled = safety_enabled
        self.max_continuous_runtime = max_continuous_runtime
        self._safety_timer = None
        
        # Event callbacks
        self.on_start_callback: Optional[Callable] = None
        self.on_stop_callback: Optional[Callable] = None
        self.on_safety_stop_callback: Optional[Callable] = None
        
        # Usage statistics
        self.daily_runtime = 0.0
        self.operation_count = 0
        
        print(f"✅ Enhanced pump controller initialized on GPIO {gpio_pin}")
        if safety_enabled:
            print(f"🛡️ Safety limit: {max_continuous_runtime}s max continuous runtime")

    def turn_on(self):
        """Turn pump on with safety checks"""
        with self._lock:
            if not self.pump.value:
                if self.safety_enabled and self._session_runtime >= self.max_continuous_runtime:
                    print(f"🛡️ Safety limit reached. Cannot start pump.")
                    return False
                
                self.pump.on()
                self._start_time = time.time()
                self._running = True
                self.operation_count += 1
                
                # Start safety timer if enabled
                if self.safety_enabled:
                    self._start_safety_timer()
                
                # Trigger callback
                if self.on_start_callback:
                    try:
                        self.on_start_callback()
                    except Exception as e:
                        print(f"⚠️ Error in start callback: {e}")
                
                print("🚿 Enhanced Pump ON")
                return True
        return False

    def turn_off(self):
        """Turn pump off and update statistics"""
        with self._lock:
            if self.pump.value:
                self.pump.off()
                
                # Update runtime statistics
                if self._running and self._start_time:
                    session_time = time.time() - self._start_time
                    self._total_runtime += session_time
                    self._session_runtime += session_time
                    self.daily_runtime += session_time
                
                self._running = False
                self._start_time = None
                
                # Cancel safety timer
                if self._safety_timer:
                    self._safety_timer.cancel()
                    self._safety_timer = None
                
                # Trigger callback
                if self.on_stop_callback:
                    try:
                        self.on_stop_callback()
                    except Exception as e:
                        print(f"⚠️ Error in stop callback: {e}")
                
                print("🛑 Enhanced Pump OFF")

    def _start_safety_timer(self):
        """Start safety shutdown timer"""
        if not self.safety_enabled:
            return
            
        remaining_time = self.max_continuous_runtime - self._session_runtime
        if remaining_time > 0:
            self._safety_timer = threading.Timer(remaining_time, self._safety_shutdown)
            self._safety_timer.start()

    def _safety_shutdown(self):
        """Emergency safety shutdown"""
        print("🚨 SAFETY SHUTDOWN: Maximum runtime exceeded!")
        self.turn_off()
        
        if self.on_safety_stop_callback:
            try:
                self.on_safety_stop_callback()
            except Exception as e:
                print(f"⚠️ Error in safety callback: {e}")

    def run_timed(self, duration_sec: float):
        """Run pump for specified duration with safety checks"""
        if self.safety_enabled and duration_sec > self.max_continuous_runtime:
            print(f"🛡️ Requested duration ({duration_sec}s) exceeds safety limit")
            return False

        def worker():
            if self.turn_on():
                time.sleep(duration_sec)
                self.turn_off()
        
        threading.Thread(target=worker, daemon=True).start()
        return True

    def start_pulsing(self, pulse_on=0.3125, pulse_off=0.3125, total_duration=15):
        """Enhanced pulsing with better control"""
        if self._pulsing:
            print("⚠️ Already pulsing. Stopping current pulse first.")
            self.stop_pulsing()
            time.sleep(0.5)

        def pulser():
            self._pulsing = True
            pulse_count = 0
            print(f"🔁 Enhanced pulse: {pulse_on}s ON, {pulse_off}s OFF for {total_duration}s")
            
            end_time = time.time() + total_duration
            
            while self._pulsing and time.time() < end_time:
                if self.turn_on():
                    time.sleep(pulse_on)
                    self.turn_off()
                    pulse_count += 1
                    
                    if self._pulsing:  # Check if still pulsing before sleep
                        time.sleep(pulse_off)
                else:
                    print("⚠️ Could not start pump for pulse - safety limit reached")
                    break
            
            self._pulsing = False
            print(f"✅ Pulse complete: {pulse_count} pulses delivered")

        self._pulse_thread = threading.Thread(target=pulser, daemon=True)
        self._pulse_thread.start()

    def reset_session(self):
        """Reset session statistics (for daily reset)"""
        self._session_runtime = 0.0
        self.daily_runtime = 0.0
        print("🔄 Session statistics reset")

    def get_statistics(self) -> Dict[str, Any]:
        """Get detailed pump statistics"""
        current_runtime = 0.0
        if self._running and self._start_time:
            current_runtime = time.time() - self._start_time
            
        return {
            'total_runtime': round(self._total_runtime + current_runtime, 2),
            'session_runtime': round(self._session_runtime + current_runtime, 2),
            'daily_runtime': round(self.daily_runtime + current_runtime, 2),
            'operation_count': self.operation_count,
            'currently_running': self._running,
            'currently_pulsing': self._pulsing,
            'safety_enabled': self.safety_enabled,
            'max_continuous_runtime': self.max_continuous_runtime,
            'remaining_safe_runtime': max(0, self.max_continuous_runtime - self._session_runtime - current_runtime)
        }

    # Keep all your existing methods for compatibility
    def is_running(self):
        return self._running or self._pulsing

    def get_status(self):
        return "ON" if self.is_running() else "OFF"

    def get_runtime_seconds(self):
        current_runtime = 0.0
        if self._running and self._start_time:
            current_runtime = time.time() - self._start_time
        return round(self._total_runtime + current_runtime, 2)

    def stop_pulsing(self):
        print("⛔ Enhanced stop pulse requested")
        self._pulsing = False
        self.turn_off()

    def close(self):
        """Enhanced cleanup"""
        print("🔌 Enhanced pump cleanup")
        self._pulsing = False
        
        if self._safety_timer:
            self._safety_timer.cancel()
            
        try:
            self.turn_off()
            self.pump.close()
        except Exception as e:
            print(f"⚠️ Error during enhanced pump cleanup: {e}")