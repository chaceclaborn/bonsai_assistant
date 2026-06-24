"""Run the FastAPI server without the Tkinter UI.

Useful for running headless on a Pi (or for smoke-testing on Windows).
Initializes mock hardware so the server has live data to expose.
"""

from config.app_config import ConfigManager
from core.automation_controller import AutomationController
from core.data_manager import DataManager
from core.timing import WateringCooldownManager
from simulation.mock_display import MockDisplay
from simulation.mock_pump import MockPumpController
from simulation.mock_sensor import MockSoilMoistureSensor


def main():
    config_manager = ConfigManager()
    config = config_manager.get()
    data_manager = DataManager()

    sensor = MockSoilMoistureSensor(lambda: 45.0)
    pump = MockPumpController()
    display = MockDisplay()

    cooldown = WateringCooldownManager(cooldown_sec=config.system.watering_cooldown_hours * 3600)
    automation = AutomationController(
        sensor=sensor, pump=pump, display=display,
        cooldown_manager=cooldown, data_manager=data_manager, config=config,
    )
    automation.start_automation()

    try:
        from services.ai_service import BonsaiAIService
        ai_service = BonsaiAIService(data_manager, automation)
    except Exception:
        ai_service = None

    from api.server import create_app
    import uvicorn

    app = create_app(automation, data_manager, pump, sensor, ai_service, config)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()
