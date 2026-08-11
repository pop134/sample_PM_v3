import { useState } from "react";
import { getTrends } from "../../api/client";
import { useQuery } from "../../api/useQuery";
import { Card } from "../../components/Card";
import { LineChart } from "../../components/LineChart";
import { EmptyState } from "../../components/states/EmptyState";
import { ErrorState } from "../../components/states/ErrorState";
import { Skeleton } from "../../components/states/Skeleton";
import { viewStatus } from "../../components/states/status";
import { toTrendChartData, type TrendPoint } from "./trends";

type Period = "daily" | "weekly" | "monthly";
const PERIODS: Period[] = ["daily", "weekly", "monthly"];

interface TrendChartProps {
  lat: number;
  lon: number;
}

export function TrendChart({ lat, lon }: TrendChartProps) {
  const [period, setPeriod] = useState<Period>("daily");
  const query = useQuery<TrendPoint[]>(
    () => getTrends(lat, lon, period),
    [lat, lon, period],
    { cacheKey: `trends:${lat}:${lon}:${period}` },
  );
  const status = viewStatus(query, (d) => d.length === 0);
  const data = query.data ? toTrendChartData(query.data) : null;

  return (
    <Card title="Temperature trend" className="trend">
      <div className="trend__controls" role="group" aria-label="Aggregation period">
        {PERIODS.map((p) => (
          <button
            key={p}
            className={`nav__item${p === period ? " nav__item--active" : ""}`}
            aria-pressed={p === period}
            onClick={() => setPeriod(p)}
          >
            {p}
          </button>
        ))}
      </div>
      {status === "loading" && <Skeleton lines={4} />}
      {status === "error" && <ErrorState message={query.error ?? "Failed to load"} onRetry={query.refetch} />}
      {status === "empty" && <EmptyState message="No trend data yet for this location." icon="📈" />}
      {status === "ready" && data && (
        <LineChart series={data.series} labels={data.labels} ariaLabel="Temperature trend" />
      )}
    </Card>
  );
}
