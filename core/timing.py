# File: core/timing.py

import time

class WateringCooldownManager:
    def __init__(self, cooldown_sec=86400):
        self.cooldown_sec = cooldown_sec
        self.last_watered_time = 0

    def can_water(self):
        return time.time() - self.last_watered_time > self.cooldown_sec

    def mark_watered(self):
        self.last_watered_time = time.time()

    def seconds_since_last(self):
        return time.time() - self.last_watered_time
