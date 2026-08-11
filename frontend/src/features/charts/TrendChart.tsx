import { useEffect, useState } from "react";
import { getTrends } from "../../api/client";
import { Card } from "../../components/Card";
import { LineChart } from "../../components/LineChart";
import { Spinner } from "../../components/Spinner";
import { toTrendChartData, type TrendPoint } from "./trends";

type Period = "daily" | "weekly" | "monthly";
const PERIODS: Period[] = ["daily", "weekly", "monthly"];

interface TrendChartProps {
  lat: number;
  lon: number;
}

export function TrendChart({ lat, lon }: TrendChartProps) {
  const [period, setPeriod] = useState<Period>("daily");
  const [points, setPoints] = useState<TrendPoint[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setPoints(null);
    setError(null);
    getTrends(lat, lon, period)
      .then((p) => active && setPoints(p))
      .catch((e: unknown) => active && setError(String(e)));
    return () => {
      active = false;
    };
  }, [lat, lon, period]);

  const data = points ? toTrendChartData(points) : null;

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
      {error && <p className="muted">Couldn’t load trends: {error}</p>}
      {!error && !points && <Spinner />}
      {data && data.series[0].values.length === 0 && <p className="muted">No trend data yet.</p>}
      {data && data.series[0].values.length > 0 && (
        <LineChart series={data.series} labels={data.labels} ariaLabel="Temperature trend" />
      )}
    </Card>
  );
}
