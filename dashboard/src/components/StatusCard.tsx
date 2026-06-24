import type { LucideIcon } from "lucide-react";

type Props = {
  Icon: LucideIcon;
  label: string;
  value: string;
  accent?: "green" | "amber" | "red" | "neutral";
};

const accentColor: Record<NonNullable<Props["accent"]>, string> = {
  green: "var(--green)",
  amber: "var(--amber)",
  red: "var(--red)",
  neutral: "var(--text)",
};

export default function StatusCard({ Icon, label, value, accent = "neutral" }: Props) {
  return (
    <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 flex items-center gap-3">
      <div className="w-10 h-10 rounded-xl bg-[var(--bg)] flex items-center justify-center">
        <Icon size={20} style={{ color: accentColor[accent] }} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-xs uppercase tracking-wider text-[var(--text-muted)]">{label}</div>
        <div className="font-semibold text-[var(--text)] truncate" style={{ color: accentColor[accent] }}>
          {value}
        </div>
      </div>
    </div>
  );
}
