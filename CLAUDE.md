# Bonsai Assistant — Project Bible

## What This Is

An AI-powered bonsai care companion. The physical device sits near the bonsai tree and:
- Monitors soil moisture continuously
- Automatically controls a water pump
- Displays status on an LED/RGB screen
- Answers care questions via Claude AI
- Tracks care history and health over time

A web dashboard (Next.js) provides remote monitoring and AI chat from any browser or phone.

## Hardware on Hand

| Component | Details |
|-----------|---------|
| **Computer** | Raspberry Pi (model TBD) |
| **Moisture Sensor** | Capacitive analog sensor → ADS1115 ADC chip (I2C, address default). Channel 0. Calibration: dry=32000, wet=12000 |
| **Pump** | Water pump on GPIO pin 18, controlled via `gpiozero` with `LGPIOFactory`. Safety max: 300s continuous |
| **Display** | SSD1351 RGB OLED 128×128 (SPI). Pins: SCK=SCK, MOSI=MOSI, CS=CE0, DC=D25, RST=D27 |
| **Audio** | Not wired yet — microphone + speaker planned for future voice I/O |

**Windows dev:** All hardware has mock classes in `simulation/` (MockSoilMoistureSensor, MockPumpController, MockDisplay). The app auto-detects platform and uses mocks on Windows.

## Tech Stack Decision (Final)

```
Layer          Language / Framework       Why
─────────────────────────────────────────────────────────────────
Pi backend     Python                     Adafruit libs are Python-native; 
                                           Anthropic SDK; entire AI/voice 
                                           ecosystem is Python-first
Web UI         Next.js + TypeScript       User's existing stack across all 
                                           other projects; Radix UI + Tailwind
Communication  REST + WebSocket           FastAPI on Pi exposes endpoints; 
                                           Next.js polls/subscribes for live data
Future option  C++ on ESP32               For additional sensor nodes or 
                                           low-power satellite sensors — NOT needed yet
```

**Do NOT use C++ on the Raspberry Pi.** It provides no benefit (Pi has plenty of RAM/CPU) and breaks compatibility with every library the project needs.

## Architecture

```
Raspberry Pi (Python — Tkinter UI + FastAPI server in one process)
├── hardware/
│   ├── sensors/soil_moisture_sensor.py   # ADS1115 I2C ADC, capacitive sensor
│   ├── actuators/pump_controller.py      # gpiozero pump on GPIO 18
│   └── display/rgb_display_driver.py     # SSD1351 RGB OLED (SPI)
├── core/
│   ├── automation_controller.py          # State machine + adaptive watering
│   ├── data_manager.py                   # SQLite (moisture, watering, journal)
│   └── timing.py                         # Cooldown manager
├── services/
│   ├── ai_service.py                     # Claude (claude-sonnet-4-6) wrapper
│   └── bonsai_knowledge.py               # ~3KB cached system prompt
├── api/
│   └── server.py                         # FastAPI app + WebSocket; runs in
│                                          # background thread alongside Tkinter
├── simulation/                           # Mock hardware for Windows dev
├── ui/                                   # Tkinter dashboard, theme
├── tests/                                # pytest (test_ai_service, test_api)
├── config/                               # JSON-backed app config
└── main.py                               # Entry: Tkinter UI + auto-start API

dashboard/  (Next.js, separate process)
├── package.json                          # Next 16, React 19, Tailwind 4
├── src/app/                              # App Router — mobile-first
│   ├── layout.tsx + globals.css          # Bottom nav, dark earthy theme
│   ├── page.tsx                          # Live moisture gauge + pump controls
│   ├── chat/page.tsx                     # PocketBonsai AI chat
│   └── history/page.tsx                  # Recharts moisture trend
├── src/components/                       # MoistureGauge, PumpControls, etc.
└── src/lib/api.ts                        # Typed client for the FastAPI server
```

## Three Operating Modes

| Mode | Description | Trigger |
|------|-------------|---------|
| **Steady State** | Normal daily monitoring. Poll moisture every 5 min, auto-water when below threshold, display current status | Always running |
| **Transient** | Temporary care events: repotting, seasonal shift, travel/absence, disease treatment. Different thresholds + reminders | User-triggered or seasonal calendar |
| **Alert** | Critically dry, overwatered, sensor failure, pump malfunction. Immediate notification + display warning | Threshold breach |

High-Speed Data (HSD) is **not needed** — soil moisture changes over hours, pump control is on/off.

## Current State of the Codebase

**Hardware + automation layer (from remote `ee1caa1`):**
- `main.py` — Full Tkinter app with tabbed UI, controls, simulation switching, professional theme
- `core/automation_controller.py` — State machine: HEALTHY / NEEDS_WATER / RECENTLY_WATERED / SENSOR_ERROR / CRITICAL. Adaptive threshold, scheduled watering, threading
- `core/data_manager.py` — SQLite (moisture_readings, watering_events, system_events, plant_journal)
- `core/timing.py` — Watering cooldown manager
- `config/app_config.py` + `config/settings.json` — JSON-backed config
- `hardware/display/rgb_display_driver.py` — SSD1351 OLED with PIL rendering + Windows Tkinter simulator
- `hardware/sensors/soil_moisture_sensor.py` — ADS1115 I2C with calibration, smoothing, trend
- `hardware/actuators/pump_controller.py` — gpiozero pump with safety limits, pulsing
- `simulation/` — Mock classes for Windows dev
- `ui/` — Tkinter dashboard tab, mini status widget, theme

**AI + web layer (newly built this session):**
- `services/ai_service.py` — `BonsaiAIService` using `claude-sonnet-4-6` with prompt caching. Injects live sensor context into every user message; ~3KB knowledge base cached as ephemeral system prompt
- `services/bonsai_knowledge.py` — System prompt: care fundamentals, species reference, diagnosis guide
- `api/server.py` — FastAPI app + WebSocket. Runs in background thread from `main.py._start_optional_services()`. Endpoints: `/sensors/current`, `/sensors/history`, `/pump/status`, `/pump/water`, `/watering/history`, `/summary/today`, `/journal`, `/chat`, `/chat/reset`, `/ws/live`, `/health`
- `dashboard/` — Next.js 16 + Tailwind 4 mobile-first web app. Pages: live dashboard, AI chat, history. Connects to FastAPI via `NEXT_PUBLIC_API_URL`
- `tests/` — pytest suite for ai_service (sensor context, history trim, graceful degradation) and FastAPI endpoints

**Not yet built:**
- Voice I/O — microphone + speaker
- Capacitor wrapping for native iOS/Android (web works on phone browsers as-is)
- Light sensor and species-specific configurations

## Setup & Run

### One-time setup

**Pi backend (in repo root):**
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
setx ANTHROPIC_API_KEY "sk-ant-..."   # Windows; or `export` on Linux/Mac
```

**Dashboard (in `dashboard/`):**
```bash
cd dashboard
npm install
cp .env.local.example .env.local      # edit if Pi isn't on localhost
```

### Daily use

**Recommended — one command (matches Travel Manager / AI-App pattern):**
```bash
cd dashboard
npm run dev          # spawns Python API + Next.js concurrently and auto-opens browser
```

The script (`dashboard/scripts/dev.mjs`) uses `concurrently` to run the FastAPI server (via `.venv/Scripts/python.exe ../scripts/run_api_only.py`) alongside `next dev`, watches stdout for the "Local: http://localhost:..." line, then opens the dashboard via the `open` package.

**Subcommands:**
- `npm run dev:no-open` — same as `dev` but skips the browser open
- `npm run dev:api` — Python API only
- `npm run dev:web` — Next.js only (assumes API is already running)

**Or run the full Tkinter app (which auto-starts the API in a background thread):**
```bash
python main.py
```

### View on your phone

1. Find the Pi's local IP: `hostname -I` on the Pi (e.g. `192.168.1.42`)
2. Update `dashboard/.env.local`: `NEXT_PUBLIC_API_URL=http://192.168.1.42:8000`
3. Build and serve: `cd dashboard && npm run build && npm start -- -H 0.0.0.0`
4. On your phone (same WiFi), open `http://<your-laptop-ip>:3000` — or run the dashboard on the Pi itself for a single-IP setup

For remote access (away from home WiFi): use Tailscale (zero-config) or Cloudflare Tunnel.

### Run tests

```bash
pip install pytest fastapi httpx          # if not already from requirements.txt
pytest tests/
```

## Phone Access Strategy

User wants to monitor bonsai from their phone. The Next.js dashboard is mobile-first responsive — the simplest path is the responsive web app over local WiFi.

**Phase 1 (built):** Next.js mobile-responsive dashboard accessed via Pi/laptop IP on phone browser.
**Phase 2 (future):** Wrap with Capacitor for iOS/Android native app — same pattern as `E:\Coding\travel-manager-app`.
**Phase 3 (future):** Tailscale or Cloudflare Tunnel for remote access from anywhere.

## Key Config Values

- Raspberry Pi model (TBD — affects gpiozero pin factory)
- Bonsai species (determines care thresholds; surface in `services/bonsai_knowledge.py` system prompt or in plant journal)
- `ANTHROPIC_API_KEY` — environment variable, never hardcode
- Pi's local IP address (for Next.js to connect to FastAPI; set in `dashboard/.env.local`)
- Sensor calibration `dry`/`wet` values in `config/settings.json` — re-calibrate per soil mix

## Build Priorities (Next)

1. **Voice I/O** — `SpeechRecognition` + `pyttsx3`, integrated into the existing assistant loop
2. **Light sensor** — wire a simple LDR or BH1750 lux sensor; mirror the moisture sensor pattern
3. **Species-specific profiles** — let user pick "Ficus" / "Juniper" / etc. and adjust threshold + AI system prompt accordingly
4. **Capacitor wrap** — package the Next.js app as a real iOS/Android app
5. **Tailscale or Cloudflare Tunnel** — remote access from outside home WiFi

## Code Style Rules

- Follow existing project conventions (check ESLint/tsconfig for TS, PEP8 for Python)
- No comments unless the WHY is non-obvious
- No new dependencies without asking the user first
- Keep solutions simple — don't over-engineer
- Conventional commits: `feat:`, `fix:`, `refactor:`, `chore:`

## Related Projects (for UI patterns)

- `E:\Coding\travel-manager-app` — best Next.js template (Next.js 16, Supabase, Claude API, Capacitor mobile)
- `E:\Coding\Pokemon App` — has `@anthropic-ai/sdk` integration pattern
- `E:\Coding\AI-App` — has Python FastAPI + React Vite concurrent dev pattern
- `E:\Coding\Job Shop Software` — most complete Radix UI component library
