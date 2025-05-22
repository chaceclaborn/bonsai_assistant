# File: utils/logging_utils.py

import time
import os

LOG_DIR = "logs"
CSV_LOG = os.path.join(LOG_DIR, "irrigation_log.csv")
SERVICE_LOG = os.path.join(LOG_DIR, "service.log")

def log_event(message):
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open(SERVICE_LOG, "a") as f:
        f.write(log_msg + "\n")

def log_to_csv(moisture, pump_status):
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(CSV_LOG, "a") as f:
        f.write(f"{timestamp},{moisture},{pump_status}\n")
