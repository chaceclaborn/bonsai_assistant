# File: hardware/sensors/soil_moisture_sensor.py

import time
import traceback
from typing import Optional, List, Dict, Any

try:
    import board
    import busio
    from adafruit_ads1x15.analog_in import AnalogIn
    from adafruit_ads1x15.ads1115 import ADS1115 as ADS
except ImportError:
    ADS = None
    AnalogIn = None

class SoilMoistureSensor:
    """
    Enhanced version of your soil moisture sensor with additional features
    This is optional - your existing sensor works fine!
    """
    
    def __init__(self, i2c_bus=None, channel=0, debug=True, 
                 dry_calibration=32000, wet_calibration=12000):
        """
        Enhanced sensor with configurable calibration values
        """
        self.debug = debug
        self.channel_index = channel
        self.available = False
        self.adc = None
        self.chan = None
        
        # Calibration values (can be configured)
        self.dry_val = dry_calibration
        self.wet_val = wet_calibration
        
        # Enhanced features
        self.reading_history = []
        self.max_history = 10
        self.last_reading_time = 0
        self.reading_interval = 1.0  # Minimum seconds between readings
        
        try:
            i2c = i2c_bus or busio.I2C(board.SCL, board.SDA)
            self.adc = ADS(i2c)
            self.chan = AnalogIn(self.adc, getattr(AnalogIn, f"P{channel}"))
            self.available = True
            if self.debug:
                print(f"✅ Enhanced ADS1x15 connected on A{channel}")
        except Exception as e:
            print(f"⚠️ Could not connect to ADS1x15: {e}")
            if self.debug:
                traceback.print_exc()

    def read_raw_adc(self) -> Optional[int]:
        """Read raw ADC value with error handling"""
        if not self.available:
            return None
        
        try:
            current_time = time.time()
            if current_time - self.last_reading_time < self.reading_interval:
                # Return cached reading if too frequent
                return self.reading_history[-1]['raw'] if self.reading_history else None
            
            raw_value = self.chan.value
            self.last_reading_time = current_time
            
            # Store in history
            self._add_to_history(raw_value)
            
            return raw_value
        except Exception as e:
            if self.debug:
                print(f"❌ Error reading raw ADC: {e}")
            return None

    def read_moisture_percent(self) -> Optional[float]:
        """
        Enhanced moisture reading with smoothing and validation
        """
        raw = self.read_raw_adc()
        if raw is None:
            return None

        # Calculate moisture percentage
        moisture = max(0, min(100, 
            round((self.dry_val - raw) / (self.dry_val - self.wet_val) * 100, 1)
        ))

        if self.debug:
            print(f"📊 A{self.channel_index}: Raw={raw}, Moisture={moisture}%")
        
        return moisture

    def get_smoothed_reading(self, samples=5) -> Optional[float]:
        """Get smoothed moisture reading over multiple samples"""
        if len(self.reading_history) < samples:
            return self.read_moisture_percent()
        
        recent_readings = [
            max(0, min(100, (self.dry_val - r['raw']) / (self.dry_val - self.wet_val) * 100))
            for r in self.reading_history[-samples:]
        ]
        
        return round(sum(recent_readings) / len(recent_readings), 1)

    def get_reading_trend(self) -> str:
        """Analyze recent trend in moisture readings"""
        if len(self.reading_history) < 3:
            return "insufficient_data"
        
        recent = self.reading_history[-3:]
        values = [
            (self.dry_val - r['raw']) / (self.dry_val - self.wet_val) * 100 
            for r in recent
        ]
        
        if values[-1] > values[0] + 2:
            return "increasing"
        elif values[-1] < values[0] - 2:
            return "decreasing"
        else:
            return "stable"

    def _add_to_history(self, raw_value: int):
        """Add reading to history buffer"""
        self.reading_history.append({
            'timestamp': time.time(),
            'raw': raw_value
        })
        
        # Keep only recent history
        if len(self.reading_history) > self.max_history:
            self.reading_history.pop(0)

    def calibrate(self, dry_reading: int, wet_reading: int):
        """Update calibration values"""
        self.dry_val = dry_reading
        self.wet_val = wet_reading
        print(f"🔧 Calibration updated: Dry={dry_reading}, Wet={wet_reading}")

    def get_diagnostics(self) -> Dict[str, Any]:
        """Get sensor diagnostic information"""
        return {
            'available': self.available,
            'channel': self.channel_index,
            'calibration': {
                'dry': self.dry_val,
                'wet': self.wet_val
            },
            'history_count': len(self.reading_history),
            'last_reading_time': self.last_reading_time,
            'trend': self.get_reading_trend() if len(self.reading_history) >= 3 else None
        }