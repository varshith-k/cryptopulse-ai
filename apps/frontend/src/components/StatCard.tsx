type StatCardProps = {
  label: string;
  value: string;
  tone?: "default" | "positive" | "negative";
  density?: "default" | "compact";
};

const toneMap = {
  default: "text-slate-100",
  positive: "text-emerald-300",
  negative: "text-rose-300",
};

export function StatCard({
  label,
  value,
  tone = "default",
  density = "default",
}: StatCardProps) {
  const valueSize =
    density === "compact"
      ? "text-[clamp(1.35rem,2vw,1.85rem)] leading-tight"
      : "text-3xl";

  return (
    <div className="min-w-0 rounded-3xl border border-white/10 bg-white/6 p-5 backdrop-blur-sm">
      <p className="break-words text-xs uppercase tracking-[0.24em] text-slate-400">{label}</p>
      <p className={`mt-3 min-w-0 break-words font-display ${valueSize} ${toneMap[tone]}`}>
        {value}
      </p>
    </div>
  );
}
