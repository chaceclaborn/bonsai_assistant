class MockSoilMoistureSensor:
    def __init__(self, value_func):
        self.value_func = value_func

    def read_moisture_percent(self):
        return self.value_func()
