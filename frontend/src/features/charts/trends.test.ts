import { describe, expect, it } from "vitest";
import { toTrendChartData, type TrendPoint } from "./trends";

const points: TrendPoint[] = [
  { period_start: "2026-08-01T00:00:00Z", temp_avg: 18, rolling_avg: null },
  { period_start: "2026-08-02T00:00:00Z", temp_avg: 20, rolling_avg: 19 },
];

describe("toTrendChartData", () => {
  it("produces avg + rolling series aligned to labels", () => {
    const data = toTrendChartData(points);
    expect(data.labels).toHaveLength(2);
    expect(data.series.map((s) => s.label)).toEqual(["Avg temp", "Rolling avg"]);
    expect(data.series[0].values).toEqual([18, 20]);
    // rolling carries the average where null
    expect(data.series[1].values).toEqual([18, 19]);
  });

  it("handles empty input", () => {
    const data = toTrendChartData([]);
    expect(data.series[0].values).toEqual([]);
  });
});
