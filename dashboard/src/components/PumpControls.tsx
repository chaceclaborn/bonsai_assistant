"use client";

import { useState } from "react";
import { Droplets, Loader2 } from "lucide-react";
import { api } from "@/lib/api";

export default function PumpControls({ onWatered }: { onWatered?: () => void }) {
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function water(seconds: number) {
    setBusy(true);
    setMessage(null);
    try {
      await api.water(seconds, true);
      setMessage(`Watering for ${seconds}s…`);
      onWatered?.();
    } catch (err) {
      setMessage(`Failed: ${err instanceof Error ? err.message : "unknown error"}`);
    } finally {
      setTimeout(() => setBusy(false), seconds * 1000);
    }
  }

  return (
    <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4">
      <div className="flex items-center gap-2 mb-3">
        <Droplets size={18} className="text-[var(--green)]" />
        <h2 className="font-semibold">Manual watering</h2>
      </div>
      <div className="grid grid-cols-3 gap-2">
        {[3, 5, 10].map((s) => (
          <button
            key={s}
            disabled={busy}
            onClick={() => water(s)}
            className="bg-[var(--bg)] hover:bg-[var(--bg-card-hover)] border border-[var(--border)] text-[var(--text)] font-medium py-3 rounded-xl transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-1"
          >
            {busy ? <Loader2 size={14} className="animate-spin" /> : `${s}s`}
          </button>
        ))}
      </div>
      {message && <p className="text-sm text-[var(--text-dim)] mt-3">{message}</p>}
    </div>
  );
}
