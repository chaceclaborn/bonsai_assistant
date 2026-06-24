"use client";

import { useEffect, useState } from "react";
import { Leaf, Droplets, Palette, Check, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { useSettings, ACCENTS, SPECIES, type ThemeMode } from "@/lib/useSettings";

export default function SettingsPage() {
  const { settings, update } = useSettings();

  // Backend config (threshold + cooldown) lives on the Pi, so we load and save
  // it separately from the browser-only appearance/plant settings.
  const [threshold, setThreshold] = useState<number | null>(null);
  const [cooldown, setCooldown] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getConfig()
      .then((c) => {
        setThreshold(c.moisture_threshold);
        setCooldown(c.watering_cooldown_hours);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Couldn't load device config"));
  }, []);

  async function saveDeviceConfig() {
    if (threshold === null || cooldown === null) return;
    setSaving(true);
    setError(null);
    try {
      const c = await api.updateConfig({
        moisture_threshold: threshold,
        watering_cooldown_hours: cooldown,
      });
      setThreshold(c.moisture_threshold);
      setCooldown(c.watering_cooldown_hours);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="px-4 pt-8 space-y-6">
      <header>
        <p className="text-sm text-[var(--text-muted)]">Settings</p>
        <h1 className="text-2xl font-bold">Customize</h1>
      </header>

      {/* PLANT — browser-stored */}
      <section className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 space-y-4">
        <div className="flex items-center gap-2">
          <Leaf size={18} className="text-[var(--green)]" />
          <h2 className="font-semibold">Plant</h2>
        </div>

        <label className="block">
          <span className="text-sm text-[var(--text-dim)]">Name</span>
          <input
            type="text"
            value={settings.plantName}
            onChange={(e) => update({ plantName: e.target.value })}
            placeholder="My Bonsai"
            className="mt-1 w-full bg-[var(--bg)] border border-[var(--border)] rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-[var(--green)]"
          />
        </label>

        <label className="block">
          <span className="text-sm text-[var(--text-dim)]">Species</span>
          <select
            value={settings.species}
            onChange={(e) => update({ species: e.target.value })}
            className="mt-1 w-full bg-[var(--bg)] border border-[var(--border)] rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-[var(--green)]"
          >
            {SPECIES.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <span className="mt-1 block text-xs text-[var(--text-muted)]">
            Shared with the AI so its advice fits your species.
          </span>
        </label>
      </section>

      {/* WATERING — device-stored (round-trips to the Pi) */}
      <section className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 space-y-4">
        <div className="flex items-center gap-2">
          <Droplets size={18} className="text-[var(--green)]" />
          <h2 className="font-semibold">Watering</h2>
          <span className="ml-auto text-[10px] uppercase tracking-wide text-[var(--text-muted)] border border-[var(--border)] rounded-full px-2 py-0.5">
            On device
          </span>
        </div>

        {threshold === null ? (
          <p className="text-sm text-[var(--text-muted)] flex items-center gap-2">
            <Loader2 size={14} className="animate-spin" /> Loading device config…
          </p>
        ) : (
          <>
            <label className="block">
              <span className="flex justify-between text-sm text-[var(--text-dim)]">
                <span>Moisture threshold</span>
                <span className="tabular-nums font-medium text-[var(--text)]">{threshold}%</span>
              </span>
              <input
                type="range"
                min={5}
                max={80}
                value={threshold}
                onChange={(e) => setThreshold(Number(e.target.value))}
                className="mt-2 w-full accent-[var(--green)]"
              />
              <span className="text-xs text-[var(--text-muted)]">Water when soil drops below this.</span>
            </label>

            <label className="block">
              <span className="flex justify-between text-sm text-[var(--text-dim)]">
                <span>Watering cooldown</span>
                <span className="tabular-nums font-medium text-[var(--text)]">{cooldown}h</span>
              </span>
              <input
                type="range"
                min={1}
                max={72}
                value={cooldown ?? 24}
                onChange={(e) => setCooldown(Number(e.target.value))}
                className="mt-2 w-full accent-[var(--green)]"
              />
              <span className="text-xs text-[var(--text-muted)]">Minimum wait between auto-waterings.</span>
            </label>

            <button
              onClick={saveDeviceConfig}
              disabled={saving}
              className="w-full bg-[var(--green)] text-black font-semibold rounded-xl py-3 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {saving ? <Loader2 size={16} className="animate-spin" /> : saved ? <Check size={16} /> : null}
              {saved ? "Saved to Pi" : "Save to device"}
            </button>
          </>
        )}
        {error && <p className="text-sm text-[var(--red)]">{error}</p>}
      </section>

      {/* APPEARANCE — browser-stored */}
      <section className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 space-y-4">
        <div className="flex items-center gap-2">
          <Palette size={18} className="text-[var(--green)]" />
          <h2 className="font-semibold">Appearance</h2>
        </div>

        <div>
          <span className="text-sm text-[var(--text-dim)]">Accent</span>
          <div className="mt-2 flex flex-wrap gap-2">
            {ACCENTS.map((a) => (
              <button
                key={a.value}
                onClick={() => update({ accent: a.value })}
                aria-label={a.name}
                title={a.name}
                className="w-9 h-9 rounded-full flex items-center justify-center transition-transform active:scale-90"
                style={{
                  background: a.value,
                  outline: settings.accent === a.value ? "2px solid var(--text)" : "none",
                  outlineOffset: 2,
                }}
              >
                {settings.accent === a.value && <Check size={16} className="text-black" />}
              </button>
            ))}
          </div>
        </div>

        <div>
          <span className="text-sm text-[var(--text-dim)]">Theme</span>
          <div className="mt-2 grid grid-cols-2 gap-2">
            {(["dark", "light"] as ThemeMode[]).map((mode) => (
              <button
                key={mode}
                onClick={() => update({ theme: mode })}
                className={`py-2.5 rounded-xl text-sm font-medium border capitalize transition-colors ${
                  settings.theme === mode
                    ? "bg-[var(--green)] text-black border-[var(--green)]"
                    : "bg-[var(--bg)] text-[var(--text-dim)] border-[var(--border)]"
                }`}
              >
                {mode}
              </button>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
