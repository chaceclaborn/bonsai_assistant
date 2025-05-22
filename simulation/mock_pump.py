class MockPumpController:
    def __init__(self):
        self._status = "OFF"
        self._runtime = 0

    def turn_on(self):
        self._status = "ON"

    def turn_off(self):
        self._status = "OFF"

    def run_timed(self, duration_sec):
        self._status = "ON"

    def start_pulsing(self, pulse_on, pulse_off, total_duration):
        self._status = "ON"

    def get_status(self):
        return self._status

    def get_runtime_seconds(self):
        return self._runtime
