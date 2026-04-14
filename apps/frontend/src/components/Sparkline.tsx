type SparklineProps = {
  values: number[];
  tone?: "positive" | "negative";
};

export function Sparkline({ values, tone = "positive" }: SparklineProps) {
  if (values.length === 0) {
    return <div className="h-20 rounded-2xl bg-white/5" />;
  }

  const width = 320;
  const height = 96;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;

  const points = values
    .map((value, index) => {
      const x = (index / Math.max(values.length - 1, 1)) * width;
      const y = height - ((value - min) / range) * (height - 10) - 5;
      return `${x},${y}`;
    })
    .join(" ");

  const stroke = tone === "positive" ? "#2dd4bf" : "#fb7185";

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="h-24 w-full overflow-visible">
      <defs>
        <linearGradient id={`spark-${tone}`} x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor={stroke} stopOpacity="0.2" />
          <stop offset="100%" stopColor={stroke} stopOpacity="0.9" />
        </linearGradient>
      </defs>
      <polyline
        fill="none"
        stroke={`url(#spark-${tone})`}
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
        points={points}
      />
    </svg>
  );
}
