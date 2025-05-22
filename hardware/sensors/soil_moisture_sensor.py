# File: hardware/sensors/soil_moisture_sensor.py

import time
import traceback

try:
    import board
    import busio
    from adafruit_ads1x15.analog_in import AnalogIn
    from adafruit_ads1x15.ads1115 import ADS1115 as ADS  # use ADS1015 if needed
except ImportError:
    ADS = None
    AnalogIn = None

class SoilMoistureSensor:
    def __init__(self, i2c_bus=None, channel=0, debug=True):
        """
        Uses ADS1115 or ADS1015 ADC via I2C.
        channel: 0–3 (A0 to A3)
        """
        self.debug = debug
        self.channel_index = channel
        self.available = False
        self.adc = None
        self.chan = None

        try:
            i2c = i2c_bus or busio.I2C(board.SCL, board.SDA)
            self.adc = ADS(i2c)
            self.chan = AnalogIn(self.adc, getattr(AnalogIn, f"P{channel}"))
            self.available = True
            if self.debug:
                print(f"✅ ADS1x15 connected on A{channel}")
        except Exception as e:
            print(f"⚠️ Could not connect to ADS1x15: {e}")
            traceback.print_exc()

    def read_raw_adc(self):
        if not self.available:
            return None
        try:
            return self.chan.value  # 16-bit raw value
        except Exception as e:
            if self.debug:
                print(f"❌ Error reading raw ADC: {e}")
            return None

    def read_moisture_percent(self):
        """
        Converts raw ADC to approximate moisture %.
        You may need to calibrate dry/wet values.
        """
        raw = self.read_raw_adc()
        if raw is None:
            return None

        # Typical dry: ~28,000 – 32,000
        # Typical wet: ~12,000 or lower
        DRY_VAL = 32000
        WET_VAL = 12000
        moisture = max(0, min(100, round((DRY_VAL - raw) / (DRY_VAL - WET_VAL) * 100)))

        if self.debug:
            print(f"📊 A{self.channel_index}: Raw={raw}, Moisture={moisture}%")
        return moisture

    def read_all_channels(self):
        if not self.available:
            return [None] * 4

        results = []
        for ch in range(4):
            try:
                chan = AnalogIn(self.adc, getattr(AnalogIn, f"P{ch}"))
                results.append(chan.value)
            except Exception as e:
                results.append(None)
                if self.debug:
                    print(f"⚠️ Failed reading A{ch}: {e}")
        return results


if __name__ == "__main__":
    sensor = SoilMoistureSensor(channel=0, debug=True)

    print("🌱 Moisture Sensor (ADS1x15) Test — Reading every 5 sec")
    try:
        while True:
            val = sensor.read_moisture_percent()
            print(f"🌡️ Moisture: {val}%")
            time.sleep(5)
    except KeyboardInterrupt:
        print("🛑 Exiting")
