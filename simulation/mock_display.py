class MockDisplay:
    def draw_status(self, moisture=None, pump_status="OFF", runtime_sec=0):
        print(f"[Sim OLED] Moisture={moisture}%, Pump={pump_status}, Runtime={runtime_sec}s")
