// Map analytics trend points into chart series (WBS 1.4.4). Pure/tested.
import { formatDateTime } from "../../lib/format";
import type { Series } from "./scale";

export interface TrendPoint {
  period_start: string;
  temp_avg: number;
  rolling_avg: number | null;
}

export interface TrendChartData {
  labels: string[];
  series: Series[];
}

export function toTrendChartData(points: TrendPoint[]): TrendChartData {
  const labels = points.map((p) => formatDateTime(p.period_start));
  const avg: Series = { label: "Avg temp", values: points.map((p) => p.temp_avg) };
  // Carry the average where rolling isn't available yet, so both lines align.
  const rolling: Series = {
    label: "Rolling avg",
    color: "var(--color-warning)",
    values: points.map((p) => p.rolling_avg ?? p.temp_avg),
  };
  return { labels, series: [avg, rolling] };
}
