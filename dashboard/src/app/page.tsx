"use client";

import { Activity, Thermometer, TrendingUp, AlertTriangle, PowerOff, Radio } from "lucide-react";
import MoistureGauge from "@/components/MoistureGauge";
import StatusCard from "@/components/StatusCard";
import PumpControls from "@/components/PumpControls";
import { useLiveSensor } from "@/lib/useLiveSensor";
import { useSettings } from "@/lib/useSettings";

const STATE_COLORS: Record<string, "green" | "amber" | "red" | "neutral"> = {
  healthy: "green",
  recently_watered: "green",
  needs_water: "amber",
  critical: "red",
  sensor_error: "red",
};

function formatState(state: string | undefined): string {
  if (!state) return "…";
  return state.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function HomePage() {
  const { reading, connected, error } = useLiveSensor();
  const { settings } = useSettings();

  if (error && !reading) {
    return (
      <div className="px-4 pt-12 flex flex-col items-center text-center gap-3">
        <AlertTriangle size={48} className="text-[var(--red)]" />
        <h1 className="text-xl font-semibold">Can&apos;t reach the Pi</h1>
        <p className="text-sm text-[var(--text-dim)]">{error}</p>
        <p className="text-xs text-[var(--text-muted)] mt-4">
          Check that the FastAPI server is running and that <code>NEXT_PUBLIC_API_URL</code> points at the Pi&apos;s IP.
        </p>
      </div>
    );
  }

  const offline = reading !== null && (reading.is_simulated || !reading.sensor_available);

  return (
    <div className="px-4 pt-8 space-y-6">
      <header className="flex items-end justify-between">
        <div>
          <p className="text-sm text-[var(--text-muted)]">{settings.plantName}</p>
          <h1 className="text-2xl font-bold">Live status</h1>
        </div>
        <span
          className="flex items-center gap-1.5 text-xs font-medium"
          style={{ color: connected ? "var(--green)" : "var(--text-muted)" }}
          title={connected ? "Streaming live over WebSocket" : "Polling (WebSocket offline)"}
        >
          <Radio size={13} className={connected ? "animate-pulse" : ""} />
          {connected ? "Live" : "Polling"}
        </span>
      </header>

      {offline ? (
        <div className="flex flex-col items-center text-center py-10 px-4 bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl gap-3">
          <PowerOff size={40} className="text-[var(--text-muted)]" />
          <h2 className="text-lg font-semibold">Sensor offline</h2>
          <p className="text-sm text-[var(--text-dim)] max-w-xs">
            {reading?.is_simulated
              ? "Backend is running in simulation mode — no real moisture sensor connected. Plug in the ADS1115 + capacitive sensor on the Pi to see live readings."
              : "The sensor is not responding. Check I2C wiring and that the ADS1115 is detected."}
          </p>
        </div>
      ) : (
        <div className="flex justify-center">
          <MoistureGauge
            moisture={reading?.moisture ?? null}
            threshold={reading?.threshold ?? 0}
          />
        </div>
      )}

      <div className="grid grid-cols-2 gap-3">
        <StatusCard
          Icon={Activity}
          label="State"
          value={offline ? "—" : formatState(reading?.state)}
          accent={offline ? "neutral" : (STATE_COLORS[reading?.state ?? ""] ?? "neutral")}
        />
        <StatusCard
          Icon={TrendingUp}
          label="Trend"
          value={offline ? "—" : (reading?.trend ?? "—")}
        />
        <StatusCard
          Icon={Thermometer}
          label="Sensor"
          value={offline ? "Offline" : "Online"}
          accent={offline ? "red" : "green"}
        />
        <StatusCard
          Icon={Activity}
          label="Threshold"
          value={`${reading?.threshold ?? "—"}%`}
        />
      </div>

      <PumpControls />
    </div>
  );
}
