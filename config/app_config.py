# File: config/app_config.py

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, Any
from pathlib import Path

@dataclass
class SensorConfig:
    moisture_threshold: int = 30
    sensor_warning_interval: int = 60
    i2c_channel: int = 0
    calibration_dry: int = 32000
    calibration_wet: int = 12000

@dataclass
class PumpConfig:
    gpio_pin: int = 18
    initial_run_duration: float = 1.0
    pulse_on_time: float = 0.3125
    pulse_off_time: float = 0.3125
    pulse_duration: float = 15.0
    post_water_wait: int = 30

@dataclass
class DisplayConfig:
    width: int = 128
    height: int = 128
    rotation: int = 180
    update_interval: int = 1

@dataclass
class SystemConfig:
    refresh_interval_sec: int = 1
    watering_cooldown_hours: int = 24
    log_retention_days: int = 30
    data_directory: str = "data"

@dataclass
class AppConfig:
    sensor: SensorConfig = None
    pump: PumpConfig = None
    display: DisplayConfig = None
    system: SystemConfig = None
    
    def __post_init__(self):
        if self.sensor is None:
            self.sensor = SensorConfig()
        if self.pump is None:
            self.pump = PumpConfig()
        if self.display is None:
            self.display = DisplayConfig()
        if self.system is None:
            self.system = SystemConfig()

class ConfigManager:
    def __init__(self, config_file: str = "config/settings.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
        
    def load_config(self) -> AppConfig:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                return AppConfig(
                    sensor=SensorConfig(**data.get('sensor', {})),
                    pump=PumpConfig(**data.get('pump', {})),
                    display=DisplayConfig(**data.get('display', {})),
                    system=SystemConfig(**data.get('system', {}))
                )
            except Exception as e:
                print(f"⚠️ Error loading config: {e}. Using defaults.")
        
        return AppConfig()
    
    def save_config(self):
        """Save current configuration to file"""
        self.config_file.parent.mkdir(exist_ok=True)
        config_dict = {
            'sensor': asdict(self.config.sensor),
            'pump': asdict(self.config.pump),
            'display': asdict(self.config.display),
            'system': asdict(self.config.system)
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    def get(self) -> AppConfig:
        return self.config
    
    def update(self, section: str, **kwargs):
        """Update configuration values"""
        if hasattr(self.config, section):
            section_obj = getattr(self.config, section)
            for key, value in kwargs.items():
                if hasattr(section_obj, key):
                    setattr(section_obj, key, value)
            self.save_config()