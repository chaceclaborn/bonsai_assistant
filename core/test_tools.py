# File: core/test_tools.py

def run_test_pulse(pump, duration=5.0, on_time=0.3125, off_time=0.3125):
    """
    Trigger a test pulse pattern using the pump controller.
    """
    print(f"[TEST] Starting test pulse: duration={duration}s, on={on_time}s, off={off_time}s")
    pump.start_pulsing(pulse_on=on_time, pulse_off=off_time, total_duration=duration)
