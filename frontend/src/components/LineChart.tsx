import { buildLinePath, extent, scaleLinear, type Point, type Series } from "../features/charts/scale";

interface LineChartProps {
  series: Series[];
  labels?: string[];
  width?: number;
  height?: number;
  ariaLabel?: string;
}

const PADDING = { top: 12, right: 12, bottom: 24, left: 36 };

export function LineChart({
  series, labels = [], width = 480, height = 220, ariaLabel = "Line chart",
}: LineChartProps) {
  const all = series.flatMap((s) => s.values);
  if (all.length === 0) {
    return <p className="muted">No data to plot.</p>;
  }
  const [minY, maxY] = extent(all);
  const count = Math.max(...series.map((s) => s.values.length));
  const x = scaleLinear([0, Math.max(count - 1, 1)], [PADDING.left, width - PADDING.right]);
  const y = scaleLinear([minY, maxY], [height - PADDING.bottom, PADDING.top]);

  return (
    <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={ariaLabel} className="chart">
      {/* y-axis min/max ticks */}
      <line x1={PADDING.left} y1={PADDING.top} x2={PADDING.left} y2={height - PADDING.bottom} className="chart__axis" />
      <line x1={PADDING.left} y1={height - PADDING.bottom} x2={width - PADDING.right} y2={height - PADDING.bottom} className="chart__axis" />
      <text x={4} y={PADDING.top + 4} className="chart__tick">{Math.round(maxY)}</text>
      <text x={4} y={height - PADDING.bottom} className="chart__tick">{Math.round(minY)}</text>
      {series.map((s, si) => {
        const points: Point[] = s.values.map((v, i) => ({ x: x(i), y: y(v) }));
        return (
          <path
            key={s.label}
            d={buildLinePath(points)}
            fill="none"
            stroke={s.color ?? "var(--color-accent)"}
            strokeWidth={2}
            data-series={si}
          />
        );
      })}
      {labels.length > 0 && (
        <>
          <text x={PADDING.left} y={height - 6} className="chart__tick">{labels[0]}</text>
          <text x={width - PADDING.right} y={height - 6} textAnchor="end" className="chart__tick">
            {labels[labels.length - 1]}
          </text>
        </>
      )}
    </svg>
  );
}
