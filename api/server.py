import asyncio
import threading
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str
    plant_name: Optional[str] = None
    species: Optional[str] = None


class ConfigUpdate(BaseModel):
    moisture_threshold: Optional[int] = Field(default=None, ge=5, le=80)
    watering_cooldown_hours: Optional[int] = Field(default=None, ge=1, le=168)


class WaterRequest(BaseModel):
    duration_seconds: float = Field(default=5.0, gt=0, le=60)
    pulse: bool = True


class JournalEntry(BaseModel):
    title: str
    content: str
    entry_type: str = "NOTE"
    tags: list[str] = Field(default_factory=list)


def create_app(automation, data_manager, pump, sensor, ai_service, config) -> FastAPI:
    app = FastAPI(title="Bonsai Assistant API", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health():
        return {"status": "ok", "automation_running": automation.running}

    @app.get("/sensors/current")
    def current_sensor():
        status = automation.get_status()
        diagnostics = sensor.get_diagnostics() if hasattr(sensor, "get_diagnostics") else {}
        is_simulated = bool(getattr(sensor, "is_simulated", False))
        sensor_available = diagnostics.get("available", True) and not is_simulated
        return {
            "moisture": None if is_simulated else status.get("last_moisture"),
            "state": status.get("current_state"),
            "threshold": status.get("adaptive_threshold"),
            "trend": diagnostics.get("trend"),
            "sensor_available": sensor_available,
            "is_simulated": is_simulated,
            "timestamp": datetime.now().isoformat(),
        }

    @app.get("/sensors/history")
    def sensor_history(hours: int = 24):
        readings = data_manager.get_moisture_history(hours=hours)
        return [
            {
                "timestamp": r.timestamp.isoformat(),
                "moisture": r.moisture_percent,
                "raw": r.raw_value,
            }
            for r in readings
        ]

    @app.get("/pump/status")
    def pump_status():
        is_simulated = bool(getattr(pump, "is_simulated", False))
        if hasattr(pump, "get_statistics"):
            stats = pump.get_statistics()
        else:
            stats = {"currently_running": pump.is_running() if hasattr(pump, "is_running") else False}
        return {**stats, "is_simulated": is_simulated}

    @app.post("/pump/water")
    def manual_water(req: WaterRequest):
        try:
            automation.manual_water(duration=req.duration_seconds, pulse=req.pulse)
            return {"status": "started", "duration": req.duration_seconds, "pulse": req.pulse}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/watering/history")
    def watering_history(days: int = 7):
        events = data_manager.get_watering_history(days=days)
        return [
            {
                "timestamp": e.timestamp.isoformat(),
                "duration": e.duration_seconds,
                "trigger_moisture": e.trigger_moisture,
                "type": e.event_type,
                "notes": e.notes,
            }
            for e in events
        ]

    @app.get("/summary/today")
    def today_summary():
        return data_manager.get_daily_summary()

    @app.get("/journal")
    def list_journal(limit: int = 50):
        return data_manager.get_journal_entries(limit=limit)

    @app.post("/journal")
    def add_journal(entry: JournalEntry):
        data_manager.add_journal_entry(
            title=entry.title,
            content=entry.content,
            entry_type=entry.entry_type,
            tags=entry.tags or None,
        )
        return {"status": "added"}

    @app.get("/config")
    def get_config():
        return {
            "moisture_threshold": config.sensor.moisture_threshold,
            "watering_cooldown_hours": config.system.watering_cooldown_hours,
        }

    @app.patch("/config")
    def update_config(req: ConfigUpdate):
        from config.app_config import ConfigManager

        manager = ConfigManager()
        if req.moisture_threshold is not None:
            manager.update("sensor", moisture_threshold=req.moisture_threshold)
            config.sensor.moisture_threshold = req.moisture_threshold
            automation.adaptive_threshold = req.moisture_threshold
        if req.watering_cooldown_hours is not None:
            manager.update("system", watering_cooldown_hours=req.watering_cooldown_hours)
            config.system.watering_cooldown_hours = req.watering_cooldown_hours
        return {
            "moisture_threshold": config.sensor.moisture_threshold,
            "watering_cooldown_hours": config.system.watering_cooldown_hours,
        }

    @app.post("/chat")
    def chat(req: ChatRequest):
        if ai_service is None:
            raise HTTPException(status_code=503, detail="AI service not initialized")
        reply = ai_service.chat(req.message, plant_name=req.plant_name, species=req.species)
        return {"reply": reply}

    @app.post("/chat/reset")
    def chat_reset():
        if ai_service is not None:
            ai_service.reset()
        return {"status": "reset"}

    @app.websocket("/ws/live")
    async def live_stream(websocket: WebSocket):
        await websocket.accept()
        sensor_simulated = bool(getattr(sensor, "is_simulated", False))
        try:
            while True:
                status = automation.get_status()
                diagnostics = sensor.get_diagnostics() if hasattr(sensor, "get_diagnostics") else {}
                sensor_available = diagnostics.get("available", True) and not sensor_simulated
                await websocket.send_json({
                    "moisture": None if sensor_simulated else status.get("last_moisture"),
                    "state": status.get("current_state"),
                    "threshold": status.get("adaptive_threshold"),
                    "trend": diagnostics.get("trend"),
                    "sensor_available": sensor_available,
                    "pump_status": pump.get_status() if hasattr(pump, "get_status") else "UNKNOWN",
                    "is_simulated": sensor_simulated,
                    "timestamp": datetime.now().isoformat(),
                })
                await asyncio.sleep(2.0)
        except WebSocketDisconnect:
            pass

    return app


def start_in_background(app: FastAPI, host: str = "0.0.0.0", port: int = 8000) -> threading.Thread:
    """Run uvicorn in a daemon thread so the Tkinter loop owns the main thread."""
    import uvicorn

    config = uvicorn.Config(app, host=host, port=port, log_level="warning")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True, name="fastapi-server")
    thread.start()
    return thread
