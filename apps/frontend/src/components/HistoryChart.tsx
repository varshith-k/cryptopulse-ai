import type { MarketHistoryPoint } from "../types";

type HistoryChartProps = {
  points: MarketHistoryPoint[];
  tone?: "positive" | "negative";
};

export function HistoryChart({ points, tone = "positive" }: HistoryChartProps) {
  if (points.length === 0) {
    return <div className="h-28 rounded-2xl bg-white/5" />;
  }

  const width = 480;
  const height = 180;
  const values = points.map((point) => point.price_usd);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const stroke = tone === "positive" ? "#2dd4bf" : "#fb7185";

  const linePoints = points
    .map((point, index) => {
      const x = (index / Math.max(points.length - 1, 1)) * width;
      const y = height - ((point.price_usd - min) / range) * (height - 32) - 16;
      return `${x},${y}`;
    })
    .join(" ");

  const areaPoints = `${linePoints} ${width},${height} 0,${height}`;

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="h-44 w-full overflow-visible">
      <defs>
        <linearGradient id={`history-line-${tone}`} x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor={stroke} stopOpacity="0.45" />
          <stop offset="100%" stopColor={stroke} stopOpacity="1" />
        </linearGradient>
        <linearGradient id={`history-fill-${tone}`} x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor={stroke} stopOpacity="0.24" />
          <stop offset="100%" stopColor={stroke} stopOpacity="0.04" />
        </linearGradient>
      </defs>
      <polyline
        fill={`url(#history-fill-${tone})`}
        stroke="none"
        points={areaPoints}
      />
      <polyline
        fill="none"
        stroke={`url(#history-line-${tone})`}
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
        points={linePoints}
      />
    </svg>
  );
}
