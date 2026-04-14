type StatCardProps = {
  label: string;
  value: string;
  tone?: "default" | "positive" | "negative";
};

const toneMap = {
  default: "text-slate-100",
  positive: "text-emerald-300",
  negative: "text-rose-300",
};

export function StatCard({ label, value, tone = "default" }: StatCardProps) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/6 p-5 backdrop-blur-sm">
      <p className="text-xs uppercase tracking-[0.24em] text-slate-400">{label}</p>
      <p className={`mt-3 font-display text-3xl ${toneMap[tone]}`}>{value}</p>
    </div>
  );
}
