# File: core/data_manager.py

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class MoistureReading:
    timestamp: datetime
    moisture_percent: float
    raw_value: int
    sensor_channel: int = 0

@dataclass
class WateringEvent:
    timestamp: datetime
    trigger_moisture: float
    duration_seconds: float
    event_type: str  # 'AUTO', 'MANUAL', 'TIMED', 'PULSE_TEST'
    notes: str = ""

@dataclass
class SystemEvent:
    timestamp: datetime
    event_type: str
    message: str
    severity: str = "INFO"  # INFO, WARNING, ERROR

class DataManager:
    def __init__(self, db_path: str = "data/bonsai_data.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS moisture_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    moisture_percent REAL NOT NULL,
                    raw_value INTEGER,
                    sensor_channel INTEGER DEFAULT 0
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS watering_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    trigger_moisture REAL,
                    duration_seconds REAL NOT NULL,
                    event_type TEXT NOT NULL,
                    notes TEXT DEFAULT ""
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS system_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    severity TEXT DEFAULT "INFO"
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS plant_journal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    entry_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT,
                    tags TEXT,
                    image_path TEXT
                )
            ''')
    
    def log_moisture_reading(self, moisture: float, raw_value: int = None, channel: int = 0):
        """Log a moisture sensor reading"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO moisture_readings (timestamp, moisture_percent, raw_value, sensor_channel)
                VALUES (?, ?, ?, ?)
            ''', (datetime.now().isoformat(), moisture, raw_value, channel))
    
    def log_watering_event(self, duration: float, trigger_moisture: float = None, 
                          event_type: str = "MANUAL", notes: str = ""):
        """Log a watering event"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO watering_events (timestamp, trigger_moisture, duration_seconds, event_type, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (datetime.now().isoformat(), trigger_moisture, duration, event_type, notes))
    
    def log_system_event(self, event_type: str, message: str, severity: str = "INFO"):
        """Log a system event"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO system_events (timestamp, event_type, message, severity)
                VALUES (?, ?, ?, ?)
            ''', (datetime.now().isoformat(), event_type, message, severity))
    
    def get_moisture_history(self, hours: int = 24) -> List[MoistureReading]:
        """Get moisture readings from the last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT timestamp, moisture_percent, raw_value, sensor_channel
                FROM moisture_readings
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            ''', (cutoff.isoformat(),))
            
            return [
                MoistureReading(
                    timestamp=datetime.fromisoformat(row[0]),
                    moisture_percent=row[1],
                    raw_value=row[2] or 0,
                    sensor_channel=row[3]
                )
                for row in cursor.fetchall()
            ]
    
    def get_watering_history(self, days: int = 7) -> List[WateringEvent]:
        """Get watering events from the last N days"""
        cutoff = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT timestamp, trigger_moisture, duration_seconds, event_type, notes
                FROM watering_events
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            ''', (cutoff.isoformat(),))
            
            return [
                WateringEvent(
                    timestamp=datetime.fromisoformat(row[0]),
                    trigger_moisture=row[1],
                    duration_seconds=row[2],
                    event_type=row[3],
                    notes=row[4] or ""
                )
                for row in cursor.fetchall()
            ]
    
    def get_daily_summary(self, date: datetime = None) -> Dict:
        """Get daily summary statistics"""
        if not date:
            date = datetime.now()
        
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        with sqlite3.connect(self.db_path) as conn:
            # Get moisture stats
            cursor = conn.execute('''
                SELECT AVG(moisture_percent), MIN(moisture_percent), MAX(moisture_percent), COUNT(*)
                FROM moisture_readings
                WHERE timestamp >= ? AND timestamp < ?
            ''', (start_date.isoformat(), end_date.isoformat()))
            
            moisture_stats = cursor.fetchone()
            
            # Get watering events
            cursor = conn.execute('''
                SELECT COUNT(*), SUM(duration_seconds)
                FROM watering_events
                WHERE timestamp >= ? AND timestamp < ?
            ''', (start_date.isoformat(), end_date.isoformat()))
            
            watering_stats = cursor.fetchone()
            
            return {
                'date': date.date(),
                'moisture_avg': round(moisture_stats[0] or 0, 1),
                'moisture_min': moisture_stats[1] or 0,
                'moisture_max': moisture_stats[2] or 0,
                'readings_count': moisture_stats[3] or 0,
                'watering_events': watering_stats[0] or 0,
                'total_water_time': round(watering_stats[1] or 0, 1)
            }
    
    def add_journal_entry(self, title: str, content: str, entry_type: str = "NOTE", 
                         tags: List[str] = None, image_path: str = None):
        """Add an entry to the plant care journal"""
        tags_str = json.dumps(tags) if tags else None
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO plant_journal (timestamp, entry_type, title, content, tags, image_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (datetime.now().isoformat(), entry_type, title, content, tags_str, image_path))
    
    def get_journal_entries(self, limit: int = 50) -> List[Dict]:
        """Get recent journal entries"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT timestamp, entry_type, title, content, tags, image_path
                FROM plant_journal
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            entries = []
            for row in cursor.fetchall():
                entries.append({
                    'timestamp': datetime.fromisoformat(row[0]),
                    'entry_type': row[1],
                    'title': row[2],
                    'content': row[3],
                    'tags': json.loads(row[4]) if row[4] else [],
                    'image_path': row[5]
                })
            
            return entries
    
    def cleanup_old_data(self, retention_days: int = 30):
        """Remove old data beyond retention period"""
        cutoff = datetime.now() - timedelta(days=retention_days)
        
        with sqlite3.connect(self.db_path) as conn:
            # Keep moisture readings for shorter period (maybe 7 days of detailed data)
            moisture_cutoff = datetime.now() - timedelta(days=7)
            conn.execute('DELETE FROM moisture_readings WHERE timestamp < ?', 
                        (moisture_cutoff.isoformat(),))
            
            # Keep watering events and system events longer
            conn.execute('DELETE FROM watering_events WHERE timestamp < ?', 
                        (cutoff.isoformat(),))
            conn.execute('DELETE FROM system_events WHERE timestamp < ?', 
                        (cutoff.isoformat(),))