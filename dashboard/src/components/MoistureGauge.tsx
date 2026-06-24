type Props = {
  moisture: number | null;
  threshold: number;
};

export default function MoistureGauge({ moisture, threshold }: Props) {
  const value = moisture ?? 0;
  const radius = 90;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;

  const color =
    moisture === null ? "var(--text-muted)"
    : moisture < threshold * 0.5 ? "var(--red)"
    : moisture < threshold ? "var(--amber)"
    : "var(--green)";

  return (
    <div className="relative flex items-center justify-center" style={{ width: 220, height: 220 }}>
      <svg width="220" height="220" className="-rotate-90">
        <circle
          cx="110" cy="110" r={radius}
          stroke="var(--border)" strokeWidth="14" fill="none"
        />
        <circle
          cx="110" cy="110" r={radius}
          stroke={color} strokeWidth="14" fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 800ms ease, stroke 400ms ease" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-5xl font-bold tabular-nums" style={{ color }}>
          {moisture === null ? "—" : `${moisture.toFixed(0)}%`}
        </span>
        <span className="text-xs uppercase tracking-wider text-[var(--text-muted)] mt-1">
          Soil moisture
        </span>
        <span className="text-xs text-[var(--text-dim)] mt-2">
          threshold {threshold}%
        </span>
      </div>
    </div>
  );
}
