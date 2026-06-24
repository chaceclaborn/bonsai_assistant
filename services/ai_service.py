import os
from datetime import datetime
from typing import Optional

try:
    import anthropic
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

from services.bonsai_knowledge import BONSAI_SYSTEM_PROMPT


class BonsaiAIService:
    """Claude-powered chat service with live sensor context injection.

    System prompt is sent with cache_control so the ~3KB knowledge base
    is read from cache (~0.1x price) on every request after the first.
    Per-request sensor context goes in the user message — it changes
    every call and would invalidate the cache if placed in `system`.
    """

    def __init__(self, data_manager, automation_controller, model: str = "claude-sonnet-4-6"):
        self.data_manager = data_manager
        self.automation = automation_controller
        self.model = model
        self.history: list[dict] = []

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if SDK_AVAILABLE and api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
            self.available = True
        else:
            self.client = None
            self.available = False

    def _build_sensor_context(self) -> str:
        status = self.automation.get_status()

        recent_waterings = self.data_manager.get_watering_history(days=3)
        watering_lines = []
        for event in recent_waterings[:5]:
            ago = datetime.now() - event.timestamp
            hours = round(ago.total_seconds() / 3600, 1)
            watering_lines.append(
                f"  - {hours}h ago: {event.event_type}, {event.duration_seconds:.1f}s"
            )
        watering_summary = "\n".join(watering_lines) if watering_lines else "  - No watering events in the last 3 days"

        moisture = status.get("last_moisture")
        moisture_str = f"{moisture:.1f}%" if moisture is not None else "unavailable"

        return f"""<live_sensor_data timestamp="{datetime.now().isoformat(timespec="seconds")}">
Current moisture: {moisture_str}
Adaptive watering threshold: {status.get("adaptive_threshold")}%
Plant state: {status.get("current_state")}
Automation running: {status.get("running")}
Watering cooldown active: {not status.get("can_water")}
Consecutive low readings: {status.get("consecutive_low_readings")}
Recent watering events:
{watering_summary}
</live_sensor_data>"""

    def chat(self, user_message: str, plant_name: Optional[str] = None, species: Optional[str] = None) -> str:
        if not self.available:
            return self._unavailable_message()

        plant_lines = []
        if plant_name:
            plant_lines.append(f"Plant name: {plant_name}")
        if species:
            plant_lines.append(f"Species: {species}")
        plant_context = ("\n".join(plant_lines) + "\n\n") if plant_lines else ""

        contextual_message = f"{plant_context}{self._build_sensor_context()}\n\n{user_message}"

        messages = self.history + [{"role": "user", "content": contextual_message}]

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=[{
                    "type": "text",
                    "text": BONSAI_SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }],
                messages=messages,
            )
        except anthropic.APIStatusError as e:
            return f"Sorry, I couldn't reach the AI service ({e.status_code}). Try again in a moment."
        except anthropic.APIConnectionError:
            return "Sorry, I can't connect to the AI service right now. Check the Pi's internet connection."

        reply = next((b.text for b in response.content if b.type == "text"), "")

        self.history.append({"role": "user", "content": contextual_message})
        self.history.append({"role": "assistant", "content": reply})
        self._trim_history()

        return reply

    def reset(self) -> None:
        self.history = []

    def _trim_history(self, max_turns: int = 10) -> None:
        if len(self.history) > max_turns * 2:
            self.history = self.history[-(max_turns * 2):]

    def _unavailable_message(self) -> str:
        if not SDK_AVAILABLE:
            return "AI chat is unavailable: the `anthropic` package isn't installed. Run `pip install anthropic`."
        return "AI chat is unavailable: ANTHROPIC_API_KEY environment variable is not set."
