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
  const cardPadding = density === "compact" ? "p-4" : "p-5";
  const labelTracking = density === "compact" ? "tracking-[0.16em]" : "tracking-[0.24em]";
  const valueSize =
    density === "compact"
      ? "text-[clamp(1.5rem,1.9vw,1.85rem)] leading-tight"
      : "text-3xl";

  return (
    <div className={`min-w-0 rounded-3xl border border-white/10 bg-white/6 ${cardPadding} backdrop-blur-sm`}>
      <p className={`text-xs uppercase ${labelTracking} text-slate-400`}>{label}</p>
      <p className={`mt-3 min-w-0 whitespace-nowrap font-display ${valueSize} ${toneMap[tone]}`}>
        {value}
      </p>
    </div>
  );
}
