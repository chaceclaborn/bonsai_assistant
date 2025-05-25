# 🌱 Bonsai Assistant Professional v2.0

An intelligent automated plant care system designed specifically for bonsai trees, featuring real-time monitoring, automated watering, and a beautiful professional GUI.

![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🌟 Features

### 🎯 Core Functionality
- **Real-time Moisture Monitoring** - Continuous soil moisture tracking with color-coded alerts
- **Intelligent Automated Watering** - Adaptive threshold-based watering with cooldown protection
- **Professional GUI** - Beautiful tkinter interface with real-time charts and status displays
- **OLED Display** - 128x128 RGB display showing moisture, pump status, and system health
- **Data Logging** - SQLite database tracking moisture readings, watering events, and system logs
- **Calibration Wizard** - Easy sensor calibration with step-by-step GUI

### 🎮 Control Features
- **Manual Pump Control** - Direct on/off control with visual feedback
- **Timed Watering** - Run pump for specific durations
- **Pulse Watering** - Advanced water delivery in controlled bursts
- **Simulation Mode** - Test without hardware using mock components

### 📊 Monitoring & Analytics
- **Real-time Dashboard** - Live moisture graphs and system status
- **Historical Data** - View trends and watering history
- **Daily Summaries** - Automated reporting of water usage and moisture levels
- **Data Export** - Export readings to CSV for analysis

## 🔧 Hardware Requirements

### Essential Components
- **Raspberry Pi** (3/4/5 recommended)
- **ADS1115 ADC** - 16-bit analog-to-digital converter
- **Capacitive Soil Moisture Sensor** - Corrosion-resistant sensor
- **Water Pump** - 5V/12V submersible pump
- **Relay Module** or **MOSFET** - For pump control
- **SSD1351 OLED Display** - 128x128 RGB display (optional)

### Wiring Diagram
```
Raspberry Pi          ADS1115
    3.3V     ------>    VDD
    GND      ------>    GND
    SCL      ------>    SCL
    SDA      ------>    SDA

ADS1115              Moisture Sensor
    A0       ------>    Signal
    3.3V     ------>    VCC
    GND      ------>    GND

Raspberry Pi          Pump (via relay/MOSFET)
    GPIO18   ------>    Control Signal
    5V       ------>    Relay VCC
    GND      ------>    Relay GND
```

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/bonsai-assistant.git
cd bonsai-assistant
```

### 2. System Setup
```bash
# Enable I2C
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable

# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-dev python3-pip python3-venv i2c-tools python3-pil python3-pil.imagetk
```

### 3. Python Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

### 4. Verify Hardware
```bash
# Check I2C devices
sudo i2cdetect -y 1
# Should show 48 for ADS1115

# Test sensor connection
python hardware/sensors/test_ads1115.py
```

## 📱 Usage

### Starting the Application
```bash
source venv/bin/activate
python main.py
```

### First-Time Setup
1. Go to **Settings** tab
2. Scroll to **Sensor Calibration**
3. Click **"Start Calibration Wizard"**
4. Follow the steps:
   - Dry calibration (sensor in air)
   - Wet calibration (sensor in water)

### Setting Moisture Threshold
- **Juniper Bonsai**: 35-40% threshold
- **Tropical Bonsai**: 45-55% threshold
- **Adjust in Settings** → System Configuration

### Tabs Overview
- **🏠 Dashboard** - Real-time monitoring and charts
- **🎮 Controls** - Manual pump control and testing
- **⚙️ Settings** - Configuration and calibration

## 📁 Project Structure
```
bonsai-assistant/
├── main.py                 # Main application entry
├── requirements.txt        # Python dependencies
├── config/
│   ├── app_config.py      # Configuration management
│   └── settings.json      # User settings (auto-created)
├── core/
│   ├── automation_controller.py
│   ├── data_manager.py
│   └── timing.py
├── hardware/
│   ├── sensors/
│   │   └── soil_moisture_sensor.py
│   ├── actuators/
│   │   └── pump_controller.py
│   └── display/
│       └── rgb_display_driver.py
├── ui/
│   ├── dashboard_tab.py
│   ├── mini_status_widget.py
│   └── professional_theme.py
├── simulation/           # Mock components for testing
│   ├── mock_sensor.py
│   ├── mock_pump.py
│   └── mock_display.py
└── data/                # Auto-created data directory
    └── bonsai_data.db   # SQLite database
```

## ⚙️ Configuration

### Default Settings (settings.json)
```json
{
  "sensor": {
    "moisture_threshold": 35,
    "calibration_dry": 32000,
    "calibration_wet": 12000
  },
  "pump": {
    "pulse_duration": 15.0,
    "pulse_on_time": 0.3125,
    "pulse_off_time": 0.3125
  },
  "system": {
    "watering_cooldown_hours": 24
  }
}
```

## 🛠️ Troubleshooting

### Sensor Reading 100% or 0%
- Run calibration wizard
- Check wiring connections
- Verify sensor placement (only probes in soil)

### Display Not Working
- Check SPI connections
- Verify display rotation in settings
- Try simulation mode first

### Pump Not Responding
- Check GPIO permissions: `sudo usermod -a -G gpio $USER`
- Verify relay/MOSFET wiring
- Test with manual control first

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Adafruit for excellent hardware libraries
- The Raspberry Pi Foundation
- The bonsai community for inspiration

## 📧 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter)

Project Link: [https://github.com/yourusername/bonsai-assistant](https://github.com/yourusername/bonsai-assistant)

---
Made with 💚 for the bonsai community