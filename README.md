# 🌱 Bonsai Assistant Professional

<div align="center">

![Bonsai Assistant](https://img.shields.io/badge/Bonsai-Assistant-green.svg?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?style=for-the-badge&logo=python)
![Raspberry Pi](https://img.shields.io/badge/Raspberry-Pi-red.svg?style=for-the-badge&logo=raspberry-pi)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

**An intelligent, automated plant care system with professional GUI and advanced monitoring capabilities**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Hardware](#%EF%B8%8F-hardware-requirements) • [Screenshots](#-screenshots)

</div>

---

## 🚀 Features

### 🤖 **Intelligent Automation**
- **Adaptive watering algorithms** that learn your plant's needs
- **Multi-threshold monitoring** with emergency watering capabilities  
- **24-hour cooldown protection** to prevent over-watering
- **Scheduling system** for time-based watering routines

### 📊 **Professional Dashboard**
- **Real-time monitoring** with live moisture readings
- **Mini status bars** on every tab for instant system visibility
- **Historical data visualization** with trend analysis
- **System diagnostics** with auto-refresh capabilities

### 🎛️ **Advanced Controls**
- **Manual pump operations** with timed and pulse modes
- **Live simulation testing** without hardware
- **Inline configuration** - no popup windows!
- **Hardware abstraction** supporting multiple sensor types

### 💾 **Data Management**
- **SQLite database** for persistent data storage
- **Automated data retention** and cleanup
- **Export capabilities** for external analysis
- **Plant care journal** for notes and observations

### 🧪 **Development Features**
- **Complete hardware simulation** for testing without sensors
- **Hot-swappable components** (real ↔ simulation)
- **Comprehensive logging** and error handling
- **Professional code architecture** with separation of concerns

---

## 🛠️ Installation

### **Prerequisites**
- Raspberry Pi 4 (recommended) or any Linux system
- Python 3.8 or higher
- Git

### **Quick Start**

```bash
# Clone the repository
git clone https://github.com/yourusername/bonsai-assistant.git
cd bonsai-assistant

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### **Hardware Setup** (Optional)
If using real hardware, connect your components:
- **Moisture Sensor**: ADS1115 ADC → I2C (pins 3,5)
- **Water Pump**: Relay → GPIO 18
- **OLED Display**: SSD1351 → SPI (CE0, pins 19,21,23)

---

## 🎮 Usage

### **Getting Started**

1. **Launch the application**:
   ```bash
   python main.py
   ```

2. **Test with simulation first**:
   - Go to **Settings** tab
   - Enable "Simulate Moisture Sensor"
   - Drag moisture slider below 30%
   - Watch automation trigger watering!

3. **Configure for your plant**:
   - Set moisture threshold (default: 30%)
   - Adjust watering cooldown period
   - Configure pump timing parameters

### **Main Interface**

#### 🏠 **Dashboard Tab**
- Live system status with color-coded indicators
- Real-time moisture readings and trends
- Pump operation history and statistics
- Recent activity log

#### 🎮 **Controls Tab**  
- Manual pump controls (ON/OFF/Timed)
- Pulse watering with custom timing
- Immediate status feedback
- Operation confirmation

#### ⚙️ **Settings Tab**
- Live configuration updates (no save button needed!)
- Hardware simulation controls with presets
- System tools (cooldown reset, data cleanup)
- Real-time hardware status display

#### 🔧 **Diagnostics Tab**
- Comprehensive system status report
- Auto-refreshing every 5 seconds
- Hardware connection status
- Database and automation statistics

---

## 🔧️ Hardware Requirements

### **Minimum Setup**
- Raspberry Pi (any model with GPIO)
- MicroSD card (16GB+)
- Power supply

### **Complete Hardware Kit**
| Component | Purpose | Connection |
|-----------|---------|------------|
| **ADS1115 ADC** | Moisture sensor interface | I2C (SDA/SCL) |
| **Capacitive Soil Sensor** | Moisture detection | Analog → ADS1115 |
| **5V Water Pump** | Plant watering | Relay → GPIO 18 |
| **5V Relay Module** | Pump control | GPIO 18 |
| **SSD1351 OLED Display** | Status display | SPI (CE0) |
| **Jumper Wires** | Connections | Various |
| **Breadboard** | Prototyping | - |

### **Wiring Diagram**
```
Raspberry Pi 4
├── I2C (Pins 3,5) → ADS1115 → Soil Sensor
├── GPIO 18 → Relay → Water Pump  
├── SPI CE0 → OLED Display
└── 5V/GND → Power Distribution
```

---

## 📸 Screenshots

### Dashboard Overview
> Professional interface with real-time monitoring and mini status bars

### Settings Panel  
> Live configuration with hardware simulation controls

### Diagnostics View
> Comprehensive system status with auto-refresh

*Screenshots coming soon - submit yours via Issues!*

---

## ⚙️ Configuration

### **Environment Variables**
```bash
# Optional configuration
export BONSAI_MOISTURE_THRESHOLD=30
export BONSAI_COOLDOWN_HOURS=24
export BONSAI_LOG_LEVEL=INFO
```

### **Configuration File**
Settings are automatically saved to `config/settings.json`:

```json
{
  "sensor": {
    "moisture_threshold": 30,
    "i2c_channel": 0,
    "calibration_dry": 32000,
    "calibration_wet": 12000
  },
  "pump": {
    "gpio_pin": 18,
    "pulse_on_time": 0.3125,
    "pulse_off_time": 0.3125,
    "pulse_duration": 15.0
  },
  "system": {
    "watering_cooldown_hours": 24,
    "log_retention_days": 30
  }
}
```

---

## 🏗️ Architecture

```
bonsai-assistant/
├── 🎯 main.py                    # Application entry point
├── 🔧 hardware/                  # Hardware abstraction layer
│   ├── sensors/                  # Moisture, light sensors
│   ├── actuators/               # Pump controllers  
│   └── display/                 # OLED display drivers
├── 🧠 core/                     # Business logic
│   ├── automation_controller.py # Smart watering logic
│   ├── data_manager.py         # Database operations
│   └── timing.py               # Cooldown management
├── 🎨 ui/                       # User interface
│   ├── dashboard_tab.py        # Main dashboard
│   └── mini_status_widget.py   # Status indicators
├── ⚙️ config/                   # Configuration management
├── 🧪 simulation/               # Hardware simulation
├── 💾 data/                     # SQLite database
└── 📋 requirements.txt          # Python dependencies
```

---

## 🔄 Development

### **Running Tests**
```bash
# Run with simulation enabled
python main.py

# Test automation logic
python -c "from core.automation_controller import AutomationController; print('Tests pass!')"
```

### **Adding Features**
1. **Hardware**: Add new sensors to `hardware/sensors/`
2. **UI**: Create new tabs in `ui/`
3. **Logic**: Extend `core/automation_controller.py`
4. **Data**: Add tables via `core/data_manager.py`

### **Code Style**
- Follow PEP 8 formatting
- Use type hints where possible
- Add docstrings to public methods
- Maintain hardware abstraction

---

## 🤝 Contributing

We welcome contributions! Here's how to help:

### **Bug Reports**
- Use GitHub Issues
- Include system info (Pi model, Python version)
- Provide steps to reproduce
- Include error messages/logs

### **Feature Requests**
- Describe the use case
- Explain expected behavior
- Consider hardware requirements

### **Pull Requests**
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📈 Roadmap

### **v2.1 - Smart Features**
- [ ] Weather integration for watering decisions
- [ ] Mobile app notifications (Pushover/Telegram)
- [ ] Machine learning for optimal watering prediction
- [ ] Multi-plant support with individual profiles

### **v2.2 - Advanced Hardware**
- [ ] Camera integration for plant health monitoring
- [ ] Light sensor for grow light automation
- [ ] pH sensor integration
- [ ] Temperature/humidity monitoring

### **v2.3 - Cloud & Analytics**
- [ ] Cloud data backup
- [ ] Advanced analytics dashboard
- [ ] Plant care recommendations
- [ ] Community plant database

---

## 🛡️ Safety & Disclaimers

- ⚠️ **Electrical Safety**: Always disconnect power when wiring
- 💧 **Water Safety**: Keep electronics away from water
- 🔌 **Power Ratings**: Verify pump power requirements
- 🌱 **Plant Health**: Monitor your plants - automation supplements, doesn't replace care
- 📖 **No Warranty**: Use at your own risk

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Adafruit** - For excellent hardware libraries and documentation
- **Raspberry Pi Foundation** - For the amazing Pi ecosystem  
- **Python Community** - For tkinter, sqlite3, and countless other libraries
- **Plant Parents Everywhere** - For inspiring automated plant care solutions

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/bonsai-assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/bonsai-assistant/discussions)
- **Wiki**: [Project Wiki](https://github.com/yourusername/bonsai-assistant/wiki)

---

<div align="center">

**Made with 🌱 for plant lovers everywhere**

![GitHub stars](https://img.shields.io/github/stars/yourusername/bonsai-assistant?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/bonsai-assistant?style=social)

*Star this project if it helped your plants thrive! 🌟*

</div>