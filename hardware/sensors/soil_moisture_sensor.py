# File: hardware/sensors/soil_moisture_sensor.py

import time
import traceback
from typing import Optional, List, Dict, Any

try:
    import board
    import busio
    from adafruit_ads1x15.analog_in import AnalogIn
    import adafruit_ads1x15.ads1115 as ADS
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False
    print("⚠️ ADS1115 hardware libraries not available")

class SoilMoistureSensor:
    """
    Enhanced soil moisture sensor with better error handling
    """
    
    def __init__(self, i2c_bus=None, channel=0, debug=True, 
                 dry_calibration=32000, wet_calibration=12000):
        """
        Initialize sensor with configurable calibration values
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
        
        if not HARDWARE_AVAILABLE:
            print("⚠️ Running without ADS1115 hardware support")
            return
            
        try:
            # Initialize I2C and ADS1115
            i2c = i2c_bus or busio.I2C(board.SCL, board.SDA)
            self.adc = ADS.ADS1115(i2c)
            
            # Set gain to 1 (default) for 0-4.096V range
            self.adc.gain = 1
            
            # Create channel
            if channel == 0:
                self.chan = AnalogIn(self.adc, ADS.P0)
            elif channel == 1:
                self.chan = AnalogIn(self.adc, ADS.P1)
            elif channel == 2:
                self.chan = AnalogIn(self.adc, ADS.P2)
            elif channel == 3:
                self.chan = AnalogIn(self.adc, ADS.P3)
            else:
                raise ValueError(f"Invalid channel: {channel}")
                
            self.available = True
            if self.debug:
                print(f"✅ ADS1115 initialized on channel A{channel}")
                print(f"   Calibration: Dry={dry_calibration}, Wet={wet_calibration}")
                
        except Exception as e:
            print(f"⚠️ Could not initialize ADS1115: {e}")
            if self.debug:
                traceback.print_exc()
            self.available = False

    def read_raw_adc(self) -> Optional[int]:
        """Read raw ADC value with error handling"""
        if not self.available or not self.chan:
            return None
        
        try:
            current_time = time.time()
            
            # Don't read too frequently
            if current_time - self.last_reading_time < self.reading_interval:
                # Return last reading from history if too soon
                if self.reading_history:
                    return self.reading_history[-1]['raw']
                else:
                    # If no history, wait briefly and read
                    time.sleep(0.1)
            
            # Read value
            raw_value = self.chan.value
            self.last_reading_time = current_time
            
            # Validate reading
            if raw_value is None or raw_value < 0 or raw_value > 32767:
                if self.debug:
                    print(f"❌ Invalid raw value: {raw_value}")
                return None
            
            # Store in history
            self._add_to_history(raw_value)
            
            if self.debug:
                print(f"📊 Raw ADC reading: {raw_value}")
            
            return raw_value
            
        except Exception as e:
            if self.debug:
                print(f"❌ Error reading ADC: {e}")
            self.available = False  # Mark as unavailable on error
            return None

    def read_moisture_percent(self) -> Optional[float]:
        """
        Read moisture percentage with proper calibration
        """
        raw = self.read_raw_adc()
        if raw is None:
            return None

        # Calculate moisture percentage
        # Higher ADC value = drier (more resistance)
        # Lower ADC value = wetter (less resistance)
        if self.dry_val > self.wet_val:
            # Normal calibration (dry > wet)
            moisture = (self.dry_val - raw) / (self.dry_val - self.wet_val) * 100
        else:
            # Inverted calibration (shouldn't happen but just in case)
            moisture = (raw - self.dry_val) / (self.wet_val - self.dry_val) * 100
        
        # Clamp to 0-100 range
        moisture = max(0, min(100, moisture))
        moisture = round(moisture, 1)

        if self.debug:
            print(f"💧 Moisture: {moisture}% (Raw: {raw}, Dry: {self.dry_val}, Wet: {self.wet_val})")
        
        return moisture

    def get_smoothed_reading(self, samples=5) -> Optional[float]:
        """Get smoothed moisture reading over multiple samples"""
        readings = []
        
        # Collect samples
        for i in range(samples):
            reading = self.read_moisture_percent()
            if reading is not None:
                readings.append(reading)
                time.sleep(0.1)  # Small delay between readings
        
        if not readings:
            return None
            
        # Return average
        return round(sum(readings) / len(readings), 1)

    def get_reading_trend(self) -> str:
        """Analyze recent trend in moisture readings"""
        if len(self.reading_history) < 3:
            return "insufficient_data"
        
        recent = self.reading_history[-3:]
        
        # Calculate moisture for each
        moistures = []
        for r in recent:
            if self.dry_val > self.wet_val:
                m = (self.dry_val - r['raw']) / (self.dry_val - self.wet_val) * 100
            else:
                m = (r['raw'] - self.dry_val) / (self.wet_val - self.dry_val) * 100
            moistures.append(max(0, min(100, m)))
        
        # Determine trend
        if moistures[-1] > moistures[0] + 2:
            return "increasing"
        elif moistures[-1] < moistures[0] - 2:
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
        # Test if sensor is actually working
        test_reading = self.read_raw_adc()
        
        return {
            'available': self.available and test_reading is not None,
            'hardware_present': HARDWARE_AVAILABLE,
            'channel': self.channel_index,
            'calibration': {
                'dry': self.dry_val,
                'wet': self.wet_val
            },
            'history_count': len(self.reading_history),
            'last_reading_time': self.last_reading_time,
            'last_raw_value': test_reading,
            'trend': self.get_reading_trend() if len(self.reading_history) >= 3 else None
        }

    def is_connected(self) -> bool:
        """Check if sensor is properly connected and responding"""
        if not self.available:
            return False
            
        # Try to read a value
        test_reading = self.read_raw_adc()
        return test_reading is not None