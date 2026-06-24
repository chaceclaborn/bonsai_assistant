"use client";

import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";
import { Droplets } from "lucide-react";
import { api, type HistoryPoint, type WateringEvent } from "@/lib/api";

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryPoint[]>([]);
  const [waterings, setWaterings] = useState<WateringEvent[]>([]);
  const [hours, setHours] = useState(24);

  useEffect(() => {
    api.sensorHistory(hours).then(setHistory).catch(() => setHistory([]));
    api.wateringHistory(7).then(setWaterings).catch(() => setWaterings([]));
  }, [hours]);

  const chartData = history
    .slice()
    .reverse()
    .map((p) => ({
      time: new Date(p.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      moisture: p.moisture,
    }));

  return (
    <div className="px-4 pt-8 space-y-6">
      <header>
        <p className="text-sm text-[var(--text-muted)]">History</p>
        <h1 className="text-2xl font-bold">Moisture trend</h1>
      </header>

      <div className="flex gap-2">
        {[6, 24, 72].map((h) => (
          <button
            key={h}
            onClick={() => setHours(h)}
            className={`flex-1 py-2 rounded-xl text-sm font-medium border transition-colors ${
              hours === h
                ? "bg-[var(--green)] text-black border-[var(--green)]"
                : "bg-[var(--bg-card)] text-[var(--text-dim)] border-[var(--border)]"
            }`}
          >
            {h}h
          </button>
        ))}
      </div>

      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-3 h-72">
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" />
              <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={11} interval="preserveStartEnd" />
              <YAxis stroke="var(--text-muted)" fontSize={11} domain={[0, 100]} />
              <Tooltip
                contentStyle={{ background: "var(--bg)", border: "1px solid var(--border)", borderRadius: 8 }}
                labelStyle={{ color: "var(--text-dim)" }}
              />
              <ReferenceLine y={22} stroke="var(--amber)" strokeDasharray="3 3" label={{ value: "threshold", fill: "var(--amber)", fontSize: 10 }} />
              <Line type="monotone" dataKey="moisture" stroke="var(--green)" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-full flex items-center justify-center text-[var(--text-muted)] text-sm">
            No readings yet
          </div>
        )}
      </div>

      <section>
        <h2 className="text-lg font-semibold mb-3">Recent waterings</h2>
        <div className="space-y-2">
          {waterings.length === 0 && (
            <p className="text-sm text-[var(--text-muted)]">No watering events in the last 7 days.</p>
          )}
          {waterings.map((w, i) => (
            <div key={i} className="bg-[var(--bg-card)] border border-[var(--border)] rounded-xl p-3 flex items-center gap-3">
              <Droplets size={18} className="text-[var(--green)]" />
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium">{w.type}</div>
                <div className="text-xs text-[var(--text-muted)]">
                  {new Date(w.timestamp).toLocaleString()} • {w.duration.toFixed(1)}s
                </div>
              </div>
              {w.trigger_moisture !== null && (
                <span className="text-xs text-[var(--text-dim)] tabular-nums">
                  {w.trigger_moisture.toFixed(1)}%
                </span>
              )}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
